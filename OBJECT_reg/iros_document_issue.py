# repos_python/OBJECT_reg/iros_document_issue.py
# (2026-09-06 iros_address_lookup.py로 시작 → 2026-09-07 등기부등본 "발급"까지 확장하며 이 이름으로
#  변경 — 처음엔 "주소만 조회"하는 좁은 범위였지만, 지금은 결제·열람·다운로드까지 다루므로 파일명도
#  실제 범위(등기부등본 "발급")에 맞춰 넓혔다. 함수는 새로 창작하지 않고 전부 크롬확장
#  (chrome_extension/iros_autofill/content_iros.js)의 같은 이름 로직을 셀레니움으로 옮긴 것이다
#  (그 파일 자체가 "화면 구성이 다양하니 범용판별 우선" 원칙으로 이미 여러 차례 실사용 검증을 거쳤다
#  — 원본 deunggi.py보다 그쪽을 정본으로 삼는다).
#
# [이 파일의 진입점]
#   issue_real_estate_register(payload, credentials, options) — 로그인부터 결제·열람·다운로드까지 전체 발급.
#     options.lookup_only=True로 부르면 verify_register_target()까지만 하고 결제 없이 등기상
#     주소·고유번호만 조회한다 — 예전엔 이 용도로 find_register_address(payload)라는 별도
#     진입점(계정정보를 아예 안 받는, "조회는 로그인이 필요 없다"는 낡은 전제로 만든 경량 경로)이
#     따로 있었는데, 등기소가 조회 단계에도 캡차/로그인을 요구하기 시작하면서 그 전제가 깨졌다
#     (verify_register_target()의 _is_captcha_required() 관련 주석 참고). 두 경로가 결국 같은
#     verify_register_target()을 공유하면서도 한쪽만 계정정보를 받다 보니 "캡차 화면에서 아이디/
#     비번이 자동입력 안 됨" 같은 사고가 났었다(2026-09-19, 사용자 리포트) — find_register_address()를
#     걷어내고 lookup_only 옵션 하나로 합쳤다(local_helper/main.py::run_iros_address_lookup_headless()/
#     handle_iros_address_lookup(), web/_shared/external_ad_popup.js::exAdRequestRegisterAddressLookup(),
#     chrome_extension의 OBANG_IROS_ADDRESS_LOOKUP 중계도 함께 제거).
# 조회·발급 모두 verify_register_target(driver, payload, credentials) 하나를 공유한다 — "등기상주소·
# 소유주를 확인하는 과정"은 이 함수 하나뿐이고, 다른 곳에서 필요해지면 이 함수를 그대로 재사용하면
# 된다(사용자 요청, 2026-09-07 — 검증 로직을 두 곳에 따로 두면 한쪽만 고치는 사고로 이어지기 쉽다).
#
# 결제(700원 열람)는 크롬확장의 실사용 기본값과 동일하게 사람 확인 없이 자동으로 진행한다(사용자
# 확정, 2026-09-07) — 다만 auto_confirm=False로 부르면(예: 담당자가 "몰래작동"을 끄고 직접 지켜보는
# 테스트페이지 옵션) 결제 버튼을 직접 누르지 않고 **화면이 실제로 보이는 상태에서 사람이 누르길
# 기다렸다가** 그 이후(열람·다운로드)는 자동으로 이어간다 — content_iros.js의 "신청확인 자동 진행"
# 체크 여부와 동일한 설계다.
#
# [헤드리스 여부] "몰래(창 안 띄우고) 작동"이 켜지면 헤드리스로 돌리고, 이때는 auto_confirm/
# close_when_done도 항상 켜진 것으로 강제한다 — 창이 안 보이는데 사람이 누를 버튼이나 열어둘 창을
# 기다리는 건 앞뒤가 안 맞기 때문이다(document_issue_test.php의 "몰래 작동" 체크박스가 켜지면 나머지
# 두 옵션 줄을 통째로 숨기는 것과 같은 원칙 — 호출부인 local_helper/main.py에서 강제한다).
#
# [NAS 저장은 이 파일의 책임이 아니다] 다운로드는 이 스크립트가 관리하는 로컬 임시폴더로만 받는다.
# NAS로 옮기는 "쓰고 다시 읽어 검증"하는 로직은 이미 local_helper/main.py::handle_move_file()에
# 있으므로(정부 공적서류라 검증이 필요하다는 이유까지 이미 거기 문서화돼 있음) 여기서 새로 만들지
# 않는다 — 이 스크립트는 로컬 임시파일 경로만 돌려주고, 호출부(local_helper)가 그 함수로 옮긴다.
#
# ─────────────────────────────────────────────────────────────────────────────
# [deunggi.py와의 대응 — 2026-09-08, 사용자 요청 "내가 아는 deunggi.py 흐름으로 읽히게"]
# test.py의 '등기부등본' 버튼이 돌리는 deunggi.py::macro()와 같은 사이트·같은 화면을 다루므로 단계는
# 거의 1:1로 대응한다. 다른 점은 딱 하나 — deunggi.py는 갈림길마다 사람이 보고 눌러주고(pyautogui.alert/
# messagebox), 이 파일은 그 판단을 코드가 대신한다(숨김모드로 사람 없이 돌아야 하므로).
#
#   단계                       deunggi.py (행)                     이 파일
#   ① 홈 접속                  driver.get(index.jsp) (105)         _navigate_home() — 보안프로그램 설치페이지로 튕기면 재접속
#   ② 로그인                   접속 직후 헤더 로그인 드롭다운 (112)   결제 직전 로그인 팝업에서 _fill_login_popup_if_present()
#                                                                   (조회 단계는 로그인 없이 되므로 lookup_only가 가능해짐)
#   ③ 검색주소 만들기           검색주소값 조립 (30~67)              하지 않음 — 서버(getIrosIssuePayload)가 계산한 payload를 그대로 씀
#   ④ 부동산구분/시·도/동리·지번  테마별라디오선택() (72~96)           _verify_register_target_body() 앞부분 — 2분류(토지+건물)도 처리,
#                                                                   시/도는 WebSquare setValue, 글자칸은 _type_into_field()(진짜 타이핑+Tab)
#   ⑤ 검색결과에서 대상 고르기    사람이 확인 (299~306)               _visible_result_rows() + 부동산구분·시군구로 자동 특정
#   ⑥ [다음] 반복·화면 판별      h4 텍스트로 단계 판별 (348~411)      _visible_section_titles() + PASS_THROUGH_TITLES/PAYMENT_TITLES
#   ⑦ 결제대상 확인             사람이 체크 확인 alert (436, 452)     verify_register_target() — 등기상 주소·고유번호·소유자(마스킹) 자동 대조
#   ⑧ 중복결제 확인             중복결제확인 (444)                  _handle_duplicate_payment_screen()
#   ⑨ 선불전자지급수단 입력       하드코딩 번호 입력 (486~489)         credentials(서버 getirosservicecredentials)로 _type_into_field()
#   ⑩ 결제 → 확인 팝업          사람 askyesno (551)                 auto_confirm이면 자동, _finish_after_payment_confirm()
#   ⑪ 열람·저장                열람 후 최종 alert (623)             _view_and_save() → 임시폴더, NAS 이동은 main.py 책임
#   (추가) 보안프로그램 alert     사람이 닫음                          _dismiss_alert_if_present() — 클릭·폴링마다 흡수
#   (추가) 미결제 건 안내 팝업     -                                  _dismiss_cart_payment_reminder_popup_if_present() — run_search_once()
#                                                                   진입 직후 흡수(이전 실행이 결제 전에 멈춰 장바구니에 남긴 건)
#   (추가) 진행 로그             print                              print('[진행] …') → main.py가 파일로 받아 화면(테스트페이지)까지 전달
# ─────────────────────────────────────────────────────────────────────────────

import re
import time
import os
import tempfile
import uuid
import pyautogui

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (
    NoSuchElementException, UnexpectedAlertPresentException, WebDriverException,
    NoSuchWindowException, InvalidSessionIdException,
)

# [2026-09-12 추가 — 사용자 요청 "셀레니움 경로도 크롬확장처럼 사용자가 창을 닫은 경우를 구분해달라"]
# chrome_extension/background.js가 EAIS_TAB_ID_KEY용 chrome.tabs.onRemoved에서 쓰는 것과 동일한
# 문구 — 두 파이프라인의 사용자 화면 메시지·pr_log 기록을 일치시키기 위해 문구를 그대로 맞춘다.
USER_CLOSED_WINDOW_MESSAGE = '자동화 창을 완료 전에 직접 닫음'

# [2026-09-08 임시 진단 — 사용자 요청 "진짜 헤드리스로 다시 재현되는지 새 진행로그로 확인해보자"]
# 기본(False)은 화면 밖 창 방식(아래 issue_real_estate_register의 headless 분기 참고) — 실사용
# 동작은 이 값을 건드리지 않는 한 그대로다. True로 바꾸면 그 자리에 --headless=new를 대신 추가해서
# 진짜 헤드리스로 돌린다. 확인 끝나면 반드시 False로 되돌릴 것 — 진짜 헤드리스는 결제대상 확인
# 화면에서 등기소 보안프로그램에 막히는 게 이미 실측 확인돼 있다(위 커밋 사유 참고).
IROS_TRUE_HEADLESS_FOR_TEST = False

# [2026-09-07 추가 — "몰래 작동" 파이프라인이 불규칙하게 무응답으로 사라지는 문제 대응]
# 실측으로 확인된 핵심 차이: local_helper.exe를 콘솔이 있는 상태(사람이 터미널에서 직접 실행)로
# 돌리면 항상 끝까지 완료·보고되는데, local_helper/main.py::handle_iros_issue()가 발급용 자식
# 프로세스를 DETACHED_PROCESS(콘솔 자체가 없는 상태)로 띄우면 chromedriver가 응답 없이 사라진다.
# 셀레니움의 Service._start_process()는 chromedriver에 새 콘솔을 만들어줄 생각으로 STARTUPINFO에
# CREATE_NEW_CONSOLE을 넣는데, 그건 STARTUPINFO.dwFlags가 아니라 Popen의 creationflags로 넘겨야
# 실제로 적용되는 값이다(셀레니움 쪽 코드 자체의 실수로 보임 — 콘솔이 있는 프로세스에서는 그냥
# 부모 콘솔을 물려받아 우연히 정상 동작하고, 콘솔이 아예 없는 DETACHED_PROCESS에서는 물려받을
# 콘솔도 없어서 조용히 실패하는 것으로 추정). 그래서 여기서 creationflags에 CREATE_NEW_CONSOLE을
# 직접 얹어 chromedriver가 항상 자기만의 콘솔을 새로 받게 한다 — STARTUPINFO의 SW_HIDE 설정이
# 이미 그 새 콘솔창을 숨겨주므로 화면에 아무것도 안 뜬다. CREATE_BREAKAWAY_FROM_JOB은 별개로,
# chromedriver/chrome이 크롬의 프로세스 트리 정리에 함께 끌려가지 않도록 추가로 분리한다(이 가설
# 하나로 전부 설명되진 않았지만 확인된 구조적 약점이라 남겨둔다). main.py의 같은 상수와 값이
# 반드시 같아야 한다.
CREATE_NEW_CONSOLE = 0x00000010
CREATE_NEW_PROCESS_GROUP = 0x00000200
CREATE_BREAKAWAY_FROM_JOB = 0x01000000

BASE = 'mf_wfm_potal_main_wfm_content'
# [2026-09-08 추가 — 실측으로 확인] "부동산 소재지번 선택" — 등기기록유형 선택 이후 화면 구성이
# 매번 똑같지 않고 이 확인 화면이 추가로 끼는 경우가 있다("외부사이트 화면 다양성" 원칙 — 특정
# 화면 순서를 고정으로 가정하지 않는다).
PASS_THROUGH_TITLES = ['용도 및 추가사항 선택', '등기기록유형 선택', '(주민)등록번호 공개여부 확인',
                       '등기신청사건 처리여부 확인', '부동산 소재지번 선택',
                       # [2026-09-19 추가 — 실사용 재현으로 확인, 매물 10385] 조회 대상이 이미 "결제대상"
                       # 으로 등록돼 있으면(반복 테스트 등으로) 등기기록유형 선택 직후 이 확인 화면이
                       # 끼어든다 — 화면 안내문 그대로("중복하여 열람·발급 하려면 '다음' 버튼을 선택")
                       # [다음]으로 통과시킨다. 결제 버튼을 누른 뒤에만 뜨는 것으로 알고 있던 같은 화면이
                       # 조회(verify_register_target) 도중에도 뜰 수 있다는 뜻 — 그쪽 화면(결제 이후)에서
                       # 쓰는 _handle_duplicate_payment_screen()의 "이동"(기존 결제건으로 갈아타기)은
                       # 여기서는 쓰지 않는다 — 지금 조회 중인 매물의 등기상주소·소유주를 못 읽게 될 수
                       # 있기 때문이다(이 함수는 결제 버튼 자체를 안 누르므로 "다음"으로 넘겨도 안전하다).
                       '중복결제 확인',
                       # [2026-09-20 추가 — 실사용 재현으로 확인, 매물 854687/909667] "이용하시기전
                       # 확인하세요" — 등기소가 보여주는 이용안내 화면으로, 나타나는 지점이 고정돼있지
                       # 않다(캡차 로그인 직후에도, 등록번호 공개여부 확인 이후에도 각각 관찰됨 —
                       # "외부사이트 화면 다양성" 원칙대로 특정 지점 하나로 가정하지 않는다). 처음
                       # 발견됐을 때(854687)는 이 목록에 없어 "예상하지 못한 화면"으로 실패했었다.
                       '이용하시기전 확인하세요']
PAYMENT_TITLES = ['결제대상 확인']

# [2026-09-07 신규] 결제 버튼을 누른 뒤 사람이 직접 누를 때까지 기다리는 최대 시간(초) —
# auto_confirm=False + 창이 보이는 상태에서만 쓰인다. 담당자가 자리를 비울 수도 있어 넉넉히 잡는다.
HUMAN_CONFIRM_TIMEOUT_SEC = 600


def _launch_chrome(chrome_options):
    """issue_real_estate_register() 공용 — Chrome을 띄우는 지점을 하나로
    모아, chromedriver에 새 콘솔을 명시적으로 준다(위 파일 상단 CREATE_NEW_CONSOLE 주석 참고 —
    콘솔 없는 DETACHED_PROCESS에서 chromedriver가 응답 없이 사라지던 문제의 핵심 원인으로 실측
    확인됨). Job 분리(CREATE_BREAKAWAY_FROM_JOB)가 거부되는 환경(handle_iros_issue()의 자기 자신
    breakaway와 같은 이유로 실패할 수 있다)이면 그 플래그 없이 한 번 더 시도한다."""
    try:
        service = Service(popen_kw={'creation_flags': CREATE_NEW_CONSOLE | CREATE_NEW_PROCESS_GROUP | CREATE_BREAKAWAY_FROM_JOB})
        return webdriver.Chrome(service=service, options=chrome_options)
    except (OSError, WebDriverException):
        try:
            service = Service(popen_kw={'creation_flags': CREATE_NEW_CONSOLE})
            return webdriver.Chrome(service=service, options=chrome_options)
        except (OSError, WebDriverException):
            return webdriver.Chrome(options=chrome_options)


def _click_with_fallback(driver, el):
    """클릭 공용 헬퍼. 먼저 Selenium 표준 클릭과 ActionChains 클릭을 시도하고,
    커스텀 위젯/가림 요소 때문에 실패할 때만 마지막 수단으로 DOM click을 사용한다.

    [2026-09-07 추가 — 본섭 데이터(999071)로 재현] "보안프로그램 설치" alert는 접속 초기뿐 아니라
    흐름 중 아무 클릭 뒤에나 뜰 수 있다는 게 실측으로 확인됐다 — 클릭마다 즉시 흡수해야 어디서
    뜨든 다음 동작이 막히지 않는다(페이지 자체가 설치 안내로 넘어간 경우는 여기서 못 잡고 그
    클릭의 호출부가 반환값/다음 화면 판정으로 알아채게 된다).

    [2026-09-19 추가 — 실사용 재현으로 확인] "결제할 등기사항증명서가 존재합니다" 안내창(장바구니에
    남은 미결제 건)도 화면 진입 시 한 번만이 아니라 탭 전환 등 흐름 중 아무 때나 다시 뜰 수 있는
    게 확인됐다 — 클릭을 시도하기 **전에** 이 안내창부터 치운다(이미 화면을 가리고 있는 요소라
    alert처럼 클릭 후 처리로는 늦다 — 클릭 자체가 가로막힌다)."""
    _dismiss_cart_payment_reminder_popup_if_present(driver)
    try:
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
    except Exception:
        pass

    for clicker in (
        lambda: el.click(),
        lambda: ActionChains(driver).move_to_element(el).pause(0.1).click().perform(),
    ):
        try:
            clicker()
            _dismiss_alert_if_present(driver)
            return
        except UnexpectedAlertPresentException:
            _dismiss_alert_if_present(driver)
            return
        except Exception:
            pass

    driver.execute_script('arguments[0].click();', el)
    _dismiss_alert_if_present(driver)


def _type_into_field(driver, el, value):
    """[2026-09-08 추가 — 실측으로 새 원인 확인] 지금까지 결제수단 번호·비밀번호칸은 자바스크립트로
    값을 직접 꽂아넣었는데(_set_ws_value/execute_script), 실제 발급 시도에서 그 직후 등기소 사이트
    자체가 "선불전자지급수단 번호를 입력해 주십시오" 경고를 띄우는 게 확인됐다(2026-09-08 — 값은
    분명히 채워 넣었는데도 사이트가 "안 채워졌다"고 판단한 것). 인터넷등기소 같은 금융/공공기관
    사이트에서 흔히 쓰는 "키보드보안" 프로그램(AhnLab Safe Transaction, nProtect 등 — 이 PC에도
    설치·실행 중인 것 확인됨)은 정확히 이런 방식(진짜 키 입력이 아닌 값 주입)으로 채워진 입력을
    무효로 처리하도록 설계된 프로그램이라 이 증상과 정확히 들어맞는다. 그래서 결제 관련 입력칸은
    자바스크립트 주입 대신 실제 키 입력 이벤트가 문자마다 발생하도록 한 글자씩 타이핑한다.

    [2026-09-19 추가 — 실사용 재현으로 확인] 이 함수는 _click_with_fallback()과 달리 el.click()을
    직접 호출해서, "결제할 등기사항증명서가 존재합니다" 안내창이 입력칸을 가리고 있으면 위
    _click_with_fallback() 주석과 같은 이유로 ElementClickInterceptedException이 난다 — 클릭
    전에 먼저 안내창부터 치운다."""
    _dismiss_cart_payment_reminder_popup_if_present(driver)
    el.click()
    el.send_keys(Keys.CONTROL, 'a')
    el.send_keys(Keys.DELETE)
    for ch in str(value):
        el.send_keys(ch)
    # [2026-09-08 추가 — 사용자 지적으로 재검토] 타이핑만 하고 포커스를 그대로 두면, 값 확정을
    # blur(포커스 이탈) 이벤트로 판단하는 사이트는 여전히 "미입력"으로 볼 수 있다 — Tab으로 포커스를
    # 옮겨서 blur를 명시적으로 발생시킨다.
    el.send_keys(Keys.TAB)


def _navigate_home(driver, attempts=3):
    """[2026-09-07 추가 — 라이브 재현, 본섭 데이터(998041)로 확인] "보안프로그램 설치" alert를
    dismiss()해도 그것만으로는 부족하다 — 페이지 자체가 이미 TouchEn nx 보안프로그램 설치 안내
    페이지(install_nxkey.html)로 넘어가 있는 경우가 실제로 있다(진단 스냅샷의 title="TouchEn nx
    제품 설치"로 확인). 이 페이지에 머문 채로는 이후 어떤 셀렉터도 못 찾으므로, alert를 닫은 뒤
    "설치 안내 페이지로 튕겼는지"까지 확인해서, 튕겼으면 홈 접속을 다시 시도한다(최대 attempts회).
    @return bool 최종적으로 정상 홈(설치 안내 페이지가 아님)에 도달했으면 True
    """
    for _ in range(attempts):
        try:
            driver.get('https://www.iros.go.kr/index.jsp')
        except Exception:
            if not _dismiss_alert_if_present(driver):
                raise
            continue
        _dismiss_alert_if_present(driver)
        try:
            stuck = 'install_nxkey' in (driver.current_url or '') or 'TouchEn' in (driver.title or '')
        except Exception:
            stuck = False
        if not stuck:
            return True
        time.sleep(0.5)
    return False


def _dismiss_alert_if_present(driver):
    """[2026-09-07 추가 — 라이브 테스트에서 실제로 재현] 인터넷등기소는 결제와 무관한 조회 단계에서도
    "고객님의 안전한 결제 위하여 보안프로그램 설치가 필요합니다" 같은 네이티브 alert()를 이따금 띄운다.
    이 alert가 떠 있으면 이후 모든 셀레니움 동작이 UnexpectedAlertPresentException으로 막힌다.
    [확인]을 누르면 설치 페이지로 이동하는데, 사람이 모르는 프로그램을 자동으로 설치 승인하면 안 되므로
    accept() 대신 dismiss()(취소/닫기)로 무시하고 원래 흐름을 계속 진행한다.
    @return bool alert가 있어서 닫았으면 True, 애초에 없었으면 False
    """
    try:
        driver.switch_to.alert.dismiss()
        return True
    except Exception:
        return False


def _dismiss_cart_payment_reminder_popup_if_present(driver):
    """[2026-09-18 추가 — 실사용 재현으로 원인 확인] 이전 실행이 결제 전에 멈춘 채로 끝나면(예:
    "결제 전에 멈춤" 옵션으로 테스트) 인터넷등기소 장바구니에 미결제 등기사항증명서가 남는다. 이
    상태에서 "부동산 열람·발급" 화면에 들어가면 사이트가 "결제할 등기사항증명서가 존재합니다 —
    결제하려면 확인, 추가하려면 취소" 안내창을 화면 진입 직후 자동으로 띄운다. 네이티브 alert()가
    아니라 사이트 내부 HTML 팝업이라 위 _dismiss_alert_if_present()로는 못 닫고, 이 안내창에 가려
    주소 입력칸 클릭이 ElementClickInterceptedException으로 막히는 게 실사용 로그로 확인됐다.

    [동작 결정 — 사용자 확인, 2026-09-18] 이 자동화는 매 실행마다 요청받은 매물 하나만 조회·발급하는
    게 목적이라, 장바구니에 남은 예전 미결제 건을 지금 대신 결제하면 안 된다 — "취소"(추가) 버튼을
    눌러 그 미결제 건은 장바구니에 그대로 둔 채 지금 요청받은 조회를 계속 진행한다.
    @return bool 안내창이 있어서 닫았으면 True, 애초에 없었으면 False
    """
    popup_text = '결제할 등기사항증명서가 존재합니다'
    if not any(el.is_displayed() for el in driver.find_elements(By.XPATH, f'//*[contains(text(), "{popup_text}")]')):
        return False
    print('[진행] "결제할 등기사항증명서 존재" 안내창 발견 — 취소(추가) 클릭 후 계속 진행', flush=True)

    # [2026-09-19 수정 — 실사용 재현으로 원인 확인] 처음엔 안내창 텍스트의 조상 요소에서 "취소"라는
    # 정확한 텍스트를 가진 버튼을 찾았는데, 실사용에서 매번 "취소 버튼을 찾지 못함"으로 실패했다 —
    # 조상 탐색이 실제 팝업 컨테이너를 못 찾거나(WebSquare가 조상 id에 "message_popup"을 안 붙이는
    # 구조일 수 있음), 버튼의 렌더링 텍스트가 예상과 다를 가능성이 있다(직접 확인은 못 함 — 사이트
    # DOM을 코드에서 직접 들여다볼 수 없어 실패 로그로만 추정). 그래서 ①실패 시 클릭 전 예외로 뜬
    # 실제 버튼 id 패턴(message_popup<숫자>_wframe_btn_cancel2)을 우선 매칭하고, ②그래도 못 찾으면
    # 화면 전체에서 "취소"가 "포함된"(완전일치가 아니라) 보이는 버튼으로 폭을 넓히고, ③팝업이 막 뜬
    # 직후엔 버튼이 아직 안 붙어있을 수 있어 최대 2초 폴링한다.
    cancel_btn = None
    for _ in range(10):
        cancel_btn = _find_first_visible(driver, [
            'a[id*="message_popup"][id*="btn_cancel"]',
            'button[id*="message_popup"][id*="btn_cancel"]',
            'input[id*="message_popup"][id*="btn_cancel"]',
        ])
        if not cancel_btn:
            for el in driver.find_elements(By.CSS_SELECTOR, 'a, button, input'):
                if el.is_displayed() and '취소' in (el.text or el.get_attribute('value') or ''):
                    cancel_btn = el
                    break
        if cancel_btn:
            break
        time.sleep(0.2)

    if not cancel_btn:
        print('[진행] 안내창의 취소 버튼을 찾지 못해 그대로 진행', flush=True)
        return False

    # 여기서 _click_with_fallback()을 쓰지 않는다 — 그 함수 자체가 클릭 전에 이 함수를 먼저 부르도록
    # 아래에서 엮여 있어(재귀 방지), 이 함수 안에서는 최소한의 클릭만 직접 시도한다.
    try:
        cancel_btn.click()
    except Exception:
        try:
            driver.execute_script('arguments[0].click();', cancel_btn)
        except Exception:
            print('[진행] 안내창의 취소 버튼 클릭에 실패해 그대로 진행', flush=True)
            return False
    time.sleep(0.5)
    return True


def _is_selection_required_popup_visible(driver):
    """"열람발급할 부동산을 선택하시기 바랍니다" 안내창이 떠 있는지 확인한다. [2026-09-19 추가 —
    실사용 재현으로 원인 확인] "부동산 소재지번 선택" 화면의 체크박스가 실제로 선택됐는지는 DOM
    선택자로 알아내려다 계속 어긋났다(td[data-col_id="rad_sel"] 안에서 input을 못 찾아 매번
    "선택 안 됨"으로 잘못 판단 → 이미 사이트가 자동 선택해둔 체크박스를 다시 눌러 꺼버리는 사고로
    이어짐, 매물 10385로 재현). DOM 구조를 더 정밀하게 추측하는 대신, [다음]을 누른 뒤 **사이트가
    스스로 이 안내창을 띄우는지**로 "정말 선택이 안 됐는지"를 판단한다 — 이게 선택 여부를 가장
    확실하게 알려주는 신호다(사이트 자신의 유효성 검사이므로).
    @return bool 안내창이 보이면 True
    """
    return any(el.is_displayed() for el in
               driver.find_elements(By.XPATH, '//*[contains(text(), "열람발급할 부동산을 선택하시기 바랍니다")]'))


def _dismiss_selection_required_popup(driver):
    """위 _is_selection_required_popup_visible()이 True일 때만 부른다 — "확인" 버튼 하나뿐인
    안내창을 닫는다(위 _dismiss_cart_payment_reminder_popup_if_present()와 같은 방식, 이쪽은
    버튼이 "취소"가 아니라 "확인" 하나뿐이라는 점만 다르다)."""
    for el in driver.find_elements(By.CSS_SELECTOR, 'a, button, input'):
        if el.is_displayed() and '확인' in (el.text or el.get_attribute('value') or ''):
            try:
                el.click()
            except Exception:
                try:
                    driver.execute_script('arguments[0].click();', el)
                except Exception:
                    return False
            time.sleep(0.3)
            return True
    return False


def _diag_snapshot(driver):
    """[2026-09-07 추가 — 사용자 요청 "진단 로그 강화"] 실패 시점의 화면 상태를 실패 메시지에 함께
    남긴다. 헤드리스(숨김모드)에서는 사람이 화면을 직접 볼 수 없어, 실패 메시지 텍스트 하나만으로도
    재현 없이 원인을 짐작할 수 있어야 한다(이 메시지는 그대로 pr_log/pr_object_document에 남는다) —
    URL·페이지제목·화면에 보이는 텍스트 앞부분을 남긴다. 각 항목은 서로 독립적으로 실패해도(예:
    alert가 떠 있어 본문을 못 읽음) 나머지 항목은 정상적으로 남도록 개별 try/except로 감싼다."""
    parts = []
    try:
        parts.append('url=' + driver.current_url)
    except Exception as e:
        parts.append(f'url=(확인불가:{e})')
    try:
        parts.append('title=' + driver.title)
    except Exception as e:
        parts.append(f'title=(확인불가:{e})')
    try:
        _dismiss_alert_if_present(driver)  # 본문을 읽기 전에 혹시 남아있는 alert부터 치운다
        body = driver.execute_script("return document.body ? document.body.innerText : '';") or ''
        parts.append('본문앞부분=' + body.strip()[:400].replace('\n', ' '))
    except Exception as e:
        parts.append(f'본문=(확인불가:{e})')
    return ' / '.join(parts)


def _find_first_visible(driver, css_selectors):
    for sel in css_selectors:
        try:
            el = driver.find_element(By.CSS_SELECTOR, sel)
            if el.is_displayed():
                return el
        except NoSuchElementException:
            continue
    return None


def _visible_section_titles(driver):
    # 이 함수는 흐름 곳곳의 폴링 루프에서 반복 호출된다 — 여기서 alert 방어를 해두면 자동화 도중
    # 언제 alert가 떠도(위 _dismiss_alert_if_present() 주석 참고) 다음 폴링에서 자연히 걷힌다.
    _dismiss_alert_if_present(driver)
    titles = []
    for s in driver.find_elements(By.CSS_SELECTOR, f'#{BASE} section'):
        if not s.is_displayed():
            continue
        for h4 in s.find_elements(By.TAG_NAME, 'h4'):
            t = h4.text.strip()
            if t:
                titles.append(t)
    return titles


def _home_entry_button(driver):
    _dismiss_alert_if_present(driver)  # 접속 직후에도 alert가 뜬 사례가 실측됨(2026-09-07)
    for e in driver.find_elements(By.CSS_SELECTOR, 'a, button'):
        try:
            if e.is_displayed() and re.search(r'부동산\s*열람.?발급', e.text.strip()):
                return e
        except Exception:
            continue
    return None


def _next_button(driver):
    _dismiss_alert_if_present(driver)
    try:
        el = driver.find_element(By.ID, f'{BASE}_btn_next')
        return el if el.is_displayed() else None
    except NoSuchElementException:
        return None


def _visible_result_rows(driver):
    tbody = None
    for cid in (f'{BASE}_grd_loc_srch_rslt_body_tbody', f'{BASE}_grd_smpl_srch_rslt_body_tbody'):
        try:
            el = driver.find_element(By.ID, cid)
        except NoSuchElementException:
            continue
        if el.is_displayed():
            tbody = el
            break
        if tbody is None:
            tbody = el
    if tbody is None:
        return []
    rows = []
    for tr in tbody.find_elements(By.TAG_NAME, 'tr'):
        style = tr.get_attribute('style') or ''
        if 'display: none' in style or 'display:none' in style:
            continue
        if tr.text.strip() == '':
            continue
        rows.append(tr)
    return rows


def _row_category_text(tr):
    for col in ('real_cls_name', 'real_cls_cd'):
        try:
            return tr.find_element(By.CSS_SELECTOR, f'td[data-col_id="{col}"]').text.strip()
        except NoSuchElementException:
            continue
    return ''


def _find_row_addr_cell(tr):
    """[2026-09-18 추가 — 실사용 재현으로 확인] 검색결과 줄에서 주소가 적힌 칸을 찾는다. 소재지번검색
    결과는 data-col_id="real_addr_prt"인데, 간편검색 결과는 같은 자리가 "rd_addr_prt"로 이름이
    다르다(직접 DOM으로 확인, 2026-09-18) — 매물 400603(간편검색 경로)에서 시/군/구·지번 좁히기가
    조용히 아무것도 못 찾아 그냥 통과되던 원인이었다. _row_category_text()가 이미 쓰던 것과 같은
    방식(여러 후보 이름을 순서대로 시도)으로 두 검색 방식 모두 지원한다."""
    for col in ('real_addr_prt', 'rd_addr_prt'):
        try:
            return tr.find_element(By.CSS_SELECTOR, f'td[data-col_id="{col}"]')
        except NoSuchElementException:
            continue
    return None


def _squash(s):
    return re.sub(r'\s', '', s or '')


# [2026-09-13 추가 — 사용자 발견 "검색어로 숫자와 한글만 사용 가능하다는 게 핵심"] 인터넷등기소
# 간편검색은 주소에 영문자가 섞이면 검색결과 0건을 낸다(매물 490302로 재현 — "F2418A호" 그대로
# 넣으면 0건, 발음 그대로 한글로 바꾼 "에프2418에이호"로 넣으면 1건 정확히 매칭). core/lib/
# lib_request.php::convert_alphabet_to_korean()이 이미 같은 변환표(건물명 매칭용)를 갖고 있어서
# 그대로 옮겼다 — 용도는 다르지만(건물명 유사판단 vs 등기소 검색어), 매핑 자체는 동일해야 하므로
# ⚠️ [동기화 경고] 저 PHP 함수의 매핑을 고칠 일이 있으면 이 함수도 반드시 같이 맞출 것.
_ALPHABET_TO_KOREAN = {
    'A': '에이', 'B': '비', 'C': '씨', 'D': '디', 'E': '이', 'F': '에프', 'G': '지', 'H': '에이치',
    'I': '아이', 'J': '제이', 'K': '케이', 'L': '엘', 'M': '엠', 'N': '엔', 'O': '오', 'P': '피',
    'Q': '큐', 'R': '알', 'S': '에스', 'T': '티', 'U': '유', 'V': '브이', 'W': '더블유', 'X': '엑스',
    'Y': '와이', 'Z': '제트',
}


def _convert_alphabet_to_korean_for_search(text):
    return ''.join(_ALPHABET_TO_KOREAN.get(ch, ch) for ch in (text or '').upper())


def _row_matches_target(addr_text, payload):
    """content_iros.js::rowMatchesTarget()과 동일한 판정 — 결제 이후 화면(미열람/재열람 목록)에서
    이번 물건에 해당하는 줄을 고를 때도 재사용한다."""
    addr = _squash(addr_text)
    loc = payload.get('location_search') or {}
    dong_jibun = _squash(loc.get('dong_or_li')) + _squash(loc.get('jibun'))

    if dong_jibun == '':
        base = _squash(re.sub(r'\S*호\s*$', '', str(payload.get('search_address') or '')))
        if base == '' or base not in addr:
            return False
    else:
        sigungu = _squash(loc.get('sigungu'))
        if sigungu != '' and sigungu not in addr:
            return False
        if dong_jibun not in addr:
            return False

    room_digits = _squash(loc.get('room_no'))
    if room_digits == '':
        return True
    return ('제' + room_digits + '호') in addr or (room_digits + '호') in addr


def _is_stuck_on_security_page(driver):
    """_navigate_home()의 판별 로직과 동일 — 지금 화면이 TouchEn nx 설치 안내 페이지인지 확인한다."""
    try:
        return 'install_nxkey' in (driver.current_url or '') or 'TouchEn' in (driver.title or '')
    except Exception:
        return False


class _StuckOnSecurityPage(Exception):
    """[2026-09-07 추가 — 실측으로 원인 확인] alert 없이 페이지 자체가 설치 안내로 넘어간 경우, 이후
    코드가 있지도 않은 셀렉터를 계속 찾다가 WebDriverWait(20초)·8회 폴링(2.5초씩) 같은 긴 대기를 전부
    소진한 뒤에야 실패를 반환한다 — 그 사이 로컬도우미 자식 프로세스가 응답 없이 오래 도는 게, 이
    프로세스가 통째로 사라지고 아무 결과도 안 남는 문제로 이어질 수 있다는 게 실측으로 확인됐다(999071로
    재현 중, breakaway 자식 스폰이 실패해 크롬 프로세스 트리에 자식이 묶인 이 PC 환경에서 — 짧게 끝나는
    실행은 항상 정상 완료됐지만, 길게 도는 실행은 pr_log에 아무 기록도 안 남긴 채 사라졌다. 정확한
    강제종료 메커니즘은 직접 확인 못 했고 정황상 추정이지만, "가능한 한 빨리 실패를 확정한다"가 유일한
    안전한 대응이라 판단함 — 전체 흐름을 다시 시도하는 방식은 오히려 실행시간을 몇 배로 늘려 문제를
    악화시켰다(2026-09-07 실측, 재시도 도입 버전에서 2회 연속 무응답으로 사라짐 확인 후 되돌림)).
    그래서 긴 대기에 들어가기 전마다 "설치 안내 페이지에 이미 와 있는지"를 먼저 빠르게 확인해서, 맞다면
    그 대기를 다 소진하지 않고 즉시 실패로 확정한다 — 재시도는 하지 않는다(사용자는 화면에서 다시
    누르면 되고, 매번 새 프로세스로 시작하므로 이전 실행의 지연을 물려받지 않는다)."""
    pass


def _guard_not_stuck_on_security_page(driver):
    if _is_stuck_on_security_page(driver):
        raise _StuckOnSecurityPage()


def verify_register_target(driver, payload, credentials=None):
    """
    [재사용 가능한 핵심 함수 — 사용자 요청, 2026-09-07] 로그인이 필요 없는 단계까지만 진행해서
    등기상주소·소유주(마스킹)·고유번호를 확인한다. 결제 버튼은 절대 누르지 않는다.

    driver는 호출부가 만들어서 넘긴다(생성·quit 여부는 호출부 책임) — issue_real_estate_register()가
    lookup_only=True(주소만 필요한 호출)든 결제까지 이어가든 이 함수 하나를 공유한다.

    payload: {
        'property_category': '토지'|'건물'|'집합건물',
        'location_search': {sido, sigungu, dong_or_li, jibun, building_dong_no, room_no},
        'register_record_type': '현재유효사항'|'말소사항포함',
    }
    (core/lib/lib_document_issue.php::getIrosIssuePayload()가 실제로 계산해 내려주는 값 그대로 —
    주소 파싱 로직을 여기서 새로 만들지 않는다.)

    [2026-09-07] "보안프로그램 설치" alert/리다이렉트로 중간에 막히면 재시도하지 않고 즉시 실패로
    확정한다 — 위 _StuckOnSecurityPage 주석 참고(전체 흐름 재시도는 실행시간을 늘려 로컬도우미 자식
    프로세스가 응답 없이 사라지는 더 나쁜 결과로 이어졌다). 대신 alert/리다이렉트를 최대한 빨리
    감지해서 불필요한 긴 대기를 건너뛴다.

    credentials: [2026-09-18 신규, 선택값] 검색이 로그인화면(캡차 포함)으로 튕겼을 때 아이디/비번을
        미리 채워주는 용도로만 쓴다({'iros_id','iros_pw'}) — 안 넘기면 캡차가 떠도 자동채움 없이
        기존처럼 담당자가 전부 입력한다.

    @return {'ok': bool, 'address': str, 'unique_no': str, 'owner_masked': str, 'message': str}
    """
    property_category = payload.get('property_category') or ''
    loc = payload.get('location_search') or {}
    if not loc.get('dong_or_li') or not loc.get('jibun'):
        return {'ok': False, 'address': '', 'unique_no': '', 'owner_masked': '', 'message': '동·리 또는 지번 정보가 없습니다.'}

    # [2026-09-07 추가] 이 함수 안의 모든 실패 반환이 공유하는 진단 스냅샷 첨부 — _diag_snapshot() 참고.
    def _fail(message, owner_masked=''):
        return {'ok': False, 'address': '', 'unique_no': '', 'owner_masked': owner_masked,
                'message': f'{message} | {_diag_snapshot(driver)}'}

    print(f'[진행] verify_register_target 시작 — 부동산구분={property_category}, 동/리={loc.get("dong_or_li")}, 지번={loc.get("jibun")}', flush=True)
    try:
        result = _verify_register_target_body(driver, payload, property_category, loc, _fail, credentials)
        print(f'[진행] verify_register_target 종료 — ok={result.get("ok")}, message={result.get("message")}', flush=True)
        return result
    except UnexpectedAlertPresentException as e:
        print(f'[오류] "보안프로그램 설치" alert 발생: {e}', flush=True)
        _dismiss_alert_if_present(driver)
        return _fail('"보안프로그램 설치" 알림이 떠서 조회를 중단했습니다.')
    except _StuckOnSecurityPage:
        print('[오류] "보안프로그램 설치" 페이지로 전환됨', flush=True)
        return _fail('"보안프로그램 설치" 페이지로 전환돼 조회를 중단했습니다.')


def _pick_kind_cls_radio(driver, radio_id_fragment, property_category, _fail):
    """부동산구분 라디오(집합건물/토지/건물)를 라벨 텍스트로 찾아 클릭한다 — 소재지번검색
    (rad_loc_kind_cls)과 간편검색(rad_smpl_kind_cls)이 각자 부르는 공용 로직(2026-09-14 정리,
    로직은 기존과 동일 — 두 검색 방식으로 갈라지면서 중복될 뻔한 걸 공용 함수로 뺐다).

    [2026-09-20 재설계 — 사용자 실측 재현으로 확인, 매물 909667] 예전엔 라디오를 DOM 순서대로 하나씩
    보면서 "정확히 일치"와 "토지+건물 통합 폴백"을 같은 우선순위로 검사해, 화면에 "토지"가 정확히
    있는데도 그보다 먼저 나온 "토지+건물"을 먼저 찾으면 그대로 선택하고 멈췄다(라이브 화면 캡처로
    확인 — 실제로는 토지+건물/집합건물/토지/건물 4개가 다 있었는데 첫 번째 것을 집어버림). 화면에
    있는 라디오를 전부 먼저 모아본 뒤, ①정확히 일치하는 라벨을 최우선으로 찾고, ②그런 라벨이 화면에
    아예 없을 때만(2026-09-08에 실측된, 토지/건물이 "토지+건물"로 합쳐져 나오는 화면) 통합 라벨로
    폴백하는 2단계로 바꾼다."""
    _dismiss_alert_if_present(driver)
    candidates = []  # [(radio_element, label_element, label_text), ...]
    for r in driver.find_elements(By.CSS_SELECTOR, f'#{BASE} input[type="radio"]'):
        rid = r.get_attribute('id') or ''
        if radio_id_fragment not in rid:
            continue
        try:
            label = driver.find_element(By.CSS_SELECTOR, f'label[for="{rid}"]')
        except NoSuchElementException:
            continue
        candidates.append((r, label, label.text.strip()))
    seen_labels = [c[2] for c in candidates]

    target = None
    for r, label, label_text in candidates:
        if label_text == property_category:
            target = (r, label, label_text)
            break
    if target is None and property_category in ('토지', '건물'):
        for r, label, label_text in candidates:
            if label_text == '토지+건물':
                target = (r, label, label_text)
                break
    if target is None:
        return _fail(f'부동산구분 "{property_category}" 항목을 찾지 못했습니다 — 실제 화면에 있던 항목: {seen_labels}')

    r, label, label_text = target
    # [2026-09-19 추가 — 실사용 재현으로 확인] 아래 클릭이 예외 없이 끝나도 실제로 라디오가 선택됐는지
    # 확인 안 하고 넘어갔다 — 부동산 선택 체크박스(rad_sel)에서 같은 유형의 문제가 실측으로 확인된
    # 적이 있어(주석 참고, 클릭은 "성공한 것처럼" 끝나도 그리드 내부 선택 상태가 안 바뀔 때가 있음)
    # 여기도 클릭 후 확인·재시도를 추가한다. 새 클릭 방식을 따로 만들지 않고 _click_with_fallback()을
    # 그대로 다시 쓴다 — 그 함수는 항상 진짜 마우스 이벤트(표준 click → ActionChains)를 먼저 쓰고
    # execute_script는 최후의 수단으로만 써서, 반복 호출해도 기계적인 강제 클릭이 새로 늘어나지 않는다.
    for _ in range(2):
        _click_with_fallback(driver, label)
        time.sleep(0.3)
        if r.is_selected():
            break
    if not r.is_selected():
        return _fail(f'부동산구분 "{property_category}" 라디오를 클릭했지만 선택 상태가 되지 않았습니다.')
    print(f'[진행] 부동산구분 "{property_category}" 선택 완료 (화면 항목: {seen_labels}, 실제 선택: {label_text})', flush=True)
    time.sleep(0.2)
    return None


def _select_sido_via_websquare(driver, sel_id, sido_text, _fail):
    """시/도 드롭다운을 WebSquare setValue()로 선택한다 — 소재지번검색·간편검색 공용(2026-09-14
    정리). [2026-09-08 실측으로 원인 확인] 네이티브 <select> 조작(Select(), 옵션 클릭)은 화면에
    "선택해주세요"로 그대로 남고 "시/도를 선택하시기 바랍니다" 팝업까지 뜬다 — 즉 실제로는
    WebSquare가 자기 내부 상태로 다시 감싸고 있어서, 그 프레임워크의 setValue() API를 거쳐야 실제로
    반영된다(드롭다운 "선택"이라 키보드보안 프로그램 검사 대상이 아니라 이 방식이 안전하다)."""
    _dismiss_alert_if_present(driver)
    sido_el = driver.find_element(By.ID, sel_id)
    sido_value = None
    for opt in sido_el.find_elements(By.TAG_NAME, 'option'):
        if opt.text.strip() == sido_text:
            sido_value = opt.get_attribute('value')
            break
    if sido_value is None:
        return _fail(f'시/도 "{sido_text}" 옵션을 찾지 못했습니다.')
    comp_id = re.sub(r'___input$', '', sel_id)
    ok = driver.execute_script(
        """
        var comp = window.$p && window.$p.getComponentById(arguments[0]);
        if (comp && typeof comp.setValue === 'function') { comp.setValue(arguments[1]); return true; }
        return false;
        """,
        comp_id, sido_value,
    )
    print(f'[진행] 시/도 "{sido_text}" 선택 완료 (setValue 성공={ok})', flush=True)
    time.sleep(0.6)
    return None


def _click_search_button(driver, _fail):
    """검색 버튼을 찾아 클릭한다 — 소재지번검색·간편검색 공용(2026-09-14 정리)."""
    search_btn = None
    for e in driver.find_elements(By.CSS_SELECTOR, f'#{BASE} input, #{BASE} button, #{BASE} a'):
        if not e.is_displayed():
            continue
        text = (e.get_attribute('value') or e.text or '').strip()
        if text == '검색':
            search_btn = e
            break
    if not search_btn:
        return _fail('검색 버튼을 찾지 못했습니다.')
    print('[진행] 검색 버튼 클릭', flush=True)
    _click_with_fallback(driver, search_btn)
    time.sleep(0.5)
    return None


def _search_via_simple_search(driver, wait, payload, property_category, loc, _fail):
    """[2026-09-13 추가 — 사용자 발견, 실사용 재현으로 확인] "간편검색"으로 주소 한 줄을 통째로
    검색한다. 집합건물 중 건물동(동) 정보가 없는 매물(건축물대장 데이터 부재)은 소재지번검색(동/리+
    지번+동/호를 각 칸에 나눠 입력)으로는 지번만으로 검색결과가 여러 건으로 갈려 자동으로 못 골랐다
    (매물 490302로 재현). 간편검색은 주소 한 줄을 등기소 자체 DB(도로명주소·건물명 연계)로 해석해
    좁혀주므로, 동 정보가 없어도 대부분 유일하게 특정된다.

    [2026-09-14 추가 — 사용자 발견, 재현 확인] 집합건물이 아닌 경우(토지/일반건물)에는 반대로
    문제가 된다 — 지번에 부번이 없으면 같은 본번 지번 위의 여러 건물을 한꺼번에 찾아버린다. 그래서
    이 함수는 property_category가 '집합건물'일 때만 호출한다(호출부인 _verify_register_target_body
    참고) — 토지/건물은 기존 소재지번검색(_search_via_location_search)을 그대로 쓴다."""
    def _find_smpl_srch_tab(d):
        _dismiss_alert_if_present(d)
        return d.find_element(By.ID, f'{BASE}_tac_rlrg_appl_tab_tab_smpl_srch_tabHTML')
    tab = wait.until(_find_smpl_srch_tab)
    print('[진행] 간편검색 탭 찾음, 클릭', flush=True)
    _click_with_fallback(driver, tab)
    time.sleep(0.5)
    _guard_not_stuck_on_security_page(driver)
    print('[진행] 간편검색 탭 진입 확인', flush=True)

    # search_address(원본 주소 문자열)는 core/lib/lib_document_issue.php::getIrosIssuePayload()와
    # 직접입력(buildManualIrosPayload()) 양쪽 다 이미 payload에 담아 보낸다 — 여기서 새로 조립하지
    # 않는다. 혹시라도 없는 예외적인 경우에만 있는 조각으로 최소한이라도 구성해본다(방어적 fallback).
    search_address = (payload.get('search_address') or '').strip()
    if not search_address:
        parts = [loc.get('sido', ''), loc.get('dong_or_li', ''), loc.get('jibun', '')]
        if loc.get('building_dong_no'):
            parts.append(f"{loc['building_dong_no']}동")
        if loc.get('room_no'):
            parts.append(f"{loc['room_no']}호")
        search_address = ' '.join(p for p in parts if p)

    # [2026-09-13 추가 — 실사용 재현으로 확인] search_address는 "F2418A호"처럼 원본 영문 표기를
    # 그대로 갖고 있는데, 간편검색은 영문이 섞이면 0건을 낸다(위 _convert_alphabet_to_korean_for_search
    # 주석 참고) — 등기소에 넣기 직전에만 변환하고, payload 자체나 반환값(address)에는 원본을 그대로
    # 쓴다(변환은 검색용 임시값일 뿐, 실제 등기부상 주소로 오인되면 안 되므로).
    search_address_for_search = _convert_alphabet_to_korean_for_search(search_address)

    addr_el = _find_first_visible(driver, [f'#{BASE}_sbx_smpl_swrd___input'])
    if not addr_el:
        return _fail('간편검색 주소 입력칸을 찾지 못했습니다.')
    _type_into_field(driver, addr_el, search_address_for_search)
    print(f'[진행] 간편검색 주소 입력 완료 — {search_address_for_search}', flush=True)
    time.sleep(0.3)

    fail = _pick_kind_cls_radio(driver, 'rad_smpl_kind_cls', property_category, _fail)
    if fail is not None:
        return fail

    fail = _select_sido_via_websquare(driver, f'{BASE}_sel_smpl_admin_regn1', loc.get('sido', ''), _fail)
    if fail is not None:
        return fail

    return _click_search_button(driver, _fail)


def _search_via_location_search(driver, wait, payload, property_category, loc, _fail):
    """[기존 방식 — 2026-09-14부터 토지/건물 전용] "소재지번검색" 탭에서 시/도+동/리+지번(+집합건물이면
    동/호)을 각 칸에 정확히 대조해 검색한다. 집합건물의 "동 정보 공백" 문제(_search_via_simple_search
    주석 참고)는 없었던 원래 방식 — 토지/일반건물은 지번 자체가 곧 유일 식별자라 간편검색으로
    바꿀 이유가 없었고, 오히려 부번 없는 지번에서 간편검색이 여러 건을 한꺼번에 찾아버리는 문제가
    새로 생겨서(2026-09-14 재현) 이 방식으로 되돌렸다."""
    def _find_loc_srch_tab(d):
        _dismiss_alert_if_present(d)
        return d.find_element(By.ID, f'{BASE}_tac_rlrg_appl_tab_tab_loc_srch_tabHTML')
    tab = wait.until(_find_loc_srch_tab)
    print('[진행] 소재지번검색 탭 찾음, 클릭', flush=True)
    _click_with_fallback(driver, tab)
    time.sleep(0.5)
    _guard_not_stuck_on_security_page(driver)
    print('[진행] 소재지번검색 탭 진입 확인', flush=True)

    fail = _pick_kind_cls_radio(driver, 'rad_loc_kind_cls', property_category, _fail)
    if fail is not None:
        return fail

    fail = _select_sido_via_websquare(driver, f'{BASE}_sel_loc_admin_regn1', loc.get('sido', ''), _fail)
    if fail is not None:
        return fail

    jibun_el = _find_first_visible(driver, [
        f'#{BASE}_sbx_agrg_buld_loc_no___input',
        f'#{BASE}_sbx_loc_no___input',
    ])
    dongli_el = driver.find_element(By.ID, f'{BASE}_sbx_loc_admin_regn3___input')
    if not jibun_el:
        return _fail('지번 입력칸을 찾지 못했습니다.')

    _type_into_field(driver, dongli_el, loc['dong_or_li'])
    time.sleep(0.3)
    _type_into_field(driver, jibun_el, loc['jibun'])
    time.sleep(0.3)
    print(f'[진행] 동/리·지번 입력 완료 — {loc["dong_or_li"]} {loc["jibun"]}', flush=True)

    if property_category == '집합건물' and (loc.get('building_dong_no') or loc.get('room_no')):
        mode_index = 0 if (loc.get('building_dong_no') and loc.get('room_no')) else (1 if loc.get('building_dong_no') else 2)
        # [2026-09-07 추가 — 본섭 데이터(999071)로 재현] 이 지점 직전에 "보안프로그램 설치" alert가
        # 뜨어있으면 바로 다음 줄의 find_element()가 UnexpectedAlertPresentException으로 죽는다 —
        # 클릭 뒤(_click_with_fallback 안)만이 아니라 클릭 **전** DOM 조회 시점에도 alert가 열려있을 수 있다.
        _dismiss_alert_if_present(driver)
        radio_id = f'{BASE}_rad_loc_dong_room_sel_input_{mode_index}'
        try:
            mode_label = driver.find_element(By.CSS_SELECTOR, f'label[for="{radio_id}"]')
            mode_radio = driver.find_element(By.ID, radio_id)
        except NoSuchElementException:
            mode_label = None
            mode_radio = None
        if mode_label is not None and mode_radio is not None:
            # [2026-09-19 추가 — 위 _pick_kind_cls_radio()와 같은 이유] 클릭 후 실제로 선택됐는지
            # 확인 안 하고 넘어갔다 — 확인·재시도를 추가하되, 이 라디오는 부동산구분과 달리 "정확히
            # 좁히기 위한" 보조 입력이라(못 찾으면 원래도 그냥 넘어가던 곳) 그래도 안 되면 경고만
            # 남기고 계속 진행한다(검색결과가 여러 건으로 남으면 뒤에서 이미 "자동으로 고르지 않음"
            # 으로 걸러진다).
            for _ in range(2):
                _click_with_fallback(driver, mode_label)
                time.sleep(0.5)
                if mode_radio.is_selected():
                    break
            if not mode_radio.is_selected():
                print('[진행] 동/호수 입력모드 라디오를 클릭했지만 선택 상태를 확인하지 못함 — 그대로 진행', flush=True)
        if loc.get('building_dong_no'):
            dong_el = _find_first_visible(driver, [f'#{BASE}_sbx_loc_buld_no_buld___input'])
            if dong_el:
                _type_into_field(driver, dong_el, loc['building_dong_no'])
        if loc.get('room_no'):
            room_el = _find_first_visible(driver, [f'#{BASE}_sbx_loc_buld_no_room___input'])
            if room_el:
                _type_into_field(driver, room_el, loc['room_no'])
        time.sleep(0.6)
        print(f'[진행] 동/호수 입력 완료 — 동={loc.get("building_dong_no")}, 호={loc.get("room_no")}', flush=True)

    return _click_search_button(driver, _fail)


def _wait_for_human_to_pick_property(driver, candidate_count, timeout_seconds=300):
    """검색결과가 여러 건이라 좁히기(시군구·지번·동 표시)로도 하나로 못 골랐을 때, 사람이 브라우저
    창에서 직접 체크박스를 선택하고 [다음]을 눌러 다음 화면(등기기록유형 선택)으로 넘어가길 기다린다.

    [2026-09-19 신규 — 사용자 지적 "여러 건이면 조용히 실패하고 끝나는 게 문제"] 그동안은 이 경우
    바로 실패 처리하고 끝났다 — 캡차·결제확인처럼 사람 판단이 필요한 상황인데도 사람에게 알리지
    않고 조용히 죽는 셈이었다. 실제로 겪은 사례(매물 278720)에서 확인했듯, 어느 물건이 맞는지는
    저장된 정보(소유자 등)만으로 구분이 안 될 수 있어(건축물대장이 이름미확인이거나, 두 후보의
    차이가 저장 안 해둔 정보일 때) 사람이 직접 판단해야 한다 — 자동으로 아무거나 고르면 안 된다.

    화면 전환 감지는 등기기록유형 선택 화면 대기 로직(_verify_register_target_body() 안의
    record_select_el 폴링)과 같은 신호를 쓴다 — 사람이 직접 체크+[다음]까지 마치면 그 신호가
    똑같이 나타나므로, 호출부는 이 함수가 True를 반환하면 곧장 그 폴링 루프로 이어가면 된다
    (선택 과정 자체를 다시 자동화하지 않는다)."""
    print(f'[진행] 검색결과 {candidate_count}건 — 담당자 직접 선택 대기', flush=True)
    try:
        import pyautogui
        pyautogui.alert(
            f'검색결과가 {candidate_count}건이라 자동으로 고르지 못했습니다.\n\n'
            '이 창을 닫고, 열려있는 등기소 창에서 정확한 부동산을 직접 선택(체크)한 뒤 [다음]을 눌러주세요.\n'
            '다음 화면으로 넘어가면 자동으로 이어서 진행됩니다.',
            '[인터넷등기소] 부동산 선택 필요',
        )
    except Exception:
        pass
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            driver.find_element(By.ID, f'{BASE}_sel_cpab_kncd_input_0')
            print('[진행] 담당자가 부동산을 선택하고 다음 화면으로 넘어감 — 이어서 진행', flush=True)
            return True
        except NoSuchElementException:
            pass
        time.sleep(1)
    print('[진행] 부동산 선택 대기시간을 초과함', flush=True)
    return False


def _verify_register_target_body(driver, payload, property_category, loc, _fail, credentials=None):
    """verify_register_target()의 실제 로직 — 위 함수가 alert/설치페이지 예외를 잡아 즉시 실패로
    확정할 수 있도록 try 블록으로 감쌀 본체만 분리했다(로직 자체는 기존과 동일).
    credentials는 캡차화면에서 아이디/비번을 미리 채우는 용도로만 쓴다(2026-09-18 신규) — 안
    넘기면(예: 계정정보 조회 자체가 실패한 경우) 자동채움 없이 기존처럼 사람이 전부 입력한다."""
    wait = WebDriverWait(driver, 20)

    # [2026-09-18 추가 — 사용자 발견, 실사용 재현으로 확인] 등기소가 반복된 자동화 접속을 감지해
    # 검색 버튼을 누르면 결과 대신 로그인화면(캡차 포함)으로 튕기기 시작했다(원래 조회 단계는 로그인이
    # 필요 없었다 — 위 함수 안내 주석 ② 참고). 홈 접속부터 검색 제출까지를 한 덩어리로 묶어, 캡차를
    # 만나면 사람이 로그인을 마친 뒤 처음부터 한 번 더 시도할 수 있게 한다(로그인 화면으로 튕기면
    # 입력해둔 검색 폼 상태가 사라지므로, 중간부터 이어갈 방법이 없다).
    def run_search_once():
        print('[진행] 등기소 홈 접속 시도', flush=True)
        if not _navigate_home(driver):
            return _fail('"보안프로그램 설치" 안내 페이지에서 벗어나지 못했습니다(3회 재시도).')
        print(f'[진행] 홈 접속 완료 — url={driver.current_url}', flush=True)
        btn = wait.until(lambda d: _home_entry_button(d))
        print('[진행] "부동산 열람·발급" 버튼 찾음, 클릭', flush=True)
        _click_with_fallback(driver, btn)
        time.sleep(0.5)
        _guard_not_stuck_on_security_page(driver)  # [2026-09-07] 홈 진입 클릭 뒤에도 튕길 수 있다 — 다음 20초 대기 전에 먼저 확인
        print(f'[진행] 부동산 열람·발급 화면 진입 확인 — url={driver.current_url}', flush=True)
        _dismiss_cart_payment_reminder_popup_if_present(driver)
        if _is_captcha_required(driver):
            _prefill_login_page_credentials(driver, credentials)
            if not _wait_for_human_to_clear_captcha(driver):
                return _fail('로그인화면 캡차 입력 대기시간을 초과했습니다.')
            # [2026-09-20 추가 — 사용자 지적] "로그인 후엔 빈 화면만 남는다"는 게 확인 안 된 추측이었다
            # — 실제로 어떤 화면인지 남겨서, 나중에 "처음부터 다시" 대신 이 화면에서 바로 이어갈 수
            # 있는지 판단할 근거로 쓴다(지금 당장은 판단만 하고 동작은 안 바꾼다).
            print(f'[진행] 캡차 해소 직후 화면 제목={_visible_section_titles(driver)}, url={driver.current_url}', flush=True)
            print('[진행] 로그인 완료 확인 — 검색을 처음부터 다시 시도', flush=True)
            fail = run_search_once()
            if fail is not None:
                return fail
        # [2026-09-14 변경 — 사용자 발견, 실사용 재현으로 확인] 간편검색은 집합건물의 "동 정보 공백"
        # 문제는 풀어주지만, 토지·일반건물에서는 부번 없는 지번일 때 오히려 여러 건물을 한꺼번에 찾아버려
        # 새 문제가 됐다 — "간편검색이 항상 더 낫다"가 아니라 "집합건물만 간편검색이 필요"했던 것.
        # 부동산구분에 따라 검색 방식 자체를 가른다.
        if property_category == '집합건물':
            return _search_via_simple_search(driver, wait, payload, property_category, loc, _fail)
        return _search_via_location_search(driver, wait, payload, property_category, loc, _fail)

    fail = run_search_once()
    if fail is not None:
        return fail

    rows = _visible_result_rows(driver)
    if not rows:
        # 검색 직후 5초 대기로 결과가 아직 안 그려졌을 가능성에 대비해 한 번만 더 기다렸다가 재확인한다.
        # (2026-09-08에 겪은 "0건"의 실제 원인은 시/도 미선택이었지만, 대기 한 번 더는 비용이 없어 남겨둔다.)
        print('[진행] 검색결과 0건 — 3초 더 기다린 뒤 재확인', flush=True)
        time.sleep(3)
        rows = _visible_result_rows(driver)
    print(f'[진행] 검색결과 {len(rows)}건 확인', flush=True)
    matched = [tr for tr in rows if _row_category_text(tr) == property_category]

    if len(matched) > 1 and loc.get('sigungu'):
        narrowed = []
        for tr in matched:
            addr_td = _find_row_addr_cell(tr)
            if addr_td is None:
                continue
            if loc['sigungu'] in addr_td.text:
                narrowed.append(tr)
        if 0 < len(narrowed) < len(matched):
            matched = narrowed

    # [2026-09-18 추가 — 사용자 발견, 실사용 재현으로 확인] 간편검색은 지번을 느슨하게 매칭한다 —
    # "수청동 620-1"로 검색했는데 바로 옆 필지(620-3/620-4/620-5)의 건물까지 결과에 섞여 나온 사례
    # (매물 400603, 4건 중 3건이 다른 지번)로 재현·확인했다. 검색결과 주소란에는 실제 지번이 그대로
    # 찍혀 있으므로("[ 수청동 620-1 ]" 형식), 동/리+지번을 붙인 문자열이 그대로 포함된 줄로 좁힌다 —
    # 854687(동일 지번, 동만 다른 경우)과는 반대 상황이라 이 좁히기로는 안 줄어들 수 있는데, 그때는
    # 그대로 두고 아래 동 표시 좁히기가 마저 처리한다(순서상 서로 방해되지 않음). "620"이 "620-1"의
    # 앞부분으로 잘못 걸리지 않도록(둘 다 우리 지번보다 긴 지번의 일부일 수 있음) 뒤에 "-숫자" 또는
    # 숫자가 더 이어지지 않는지 확인한다(위 동 표시 좁히기와 같은 이유의 경계 확인).
    if len(matched) > 1 and loc.get('dong_or_li') and loc.get('jibun'):
        dongJibun = _squash(loc['dong_or_li'] + loc['jibun'])
        dongJibunPattern = re.compile(r'(?<!\d)' + re.escape(dongJibun) + r'(?!-?\d)')
        narrowed = []
        for tr in matched:
            addr_td = _find_row_addr_cell(tr)
            if addr_td is None:
                continue
            if dongJibunPattern.search(_squash(addr_td.text)):
                narrowed.append(tr)
        if 0 < len(narrowed) < len(matched):
            print(f'[진행] 검색결과 {len(matched)}건 — 지번("{loc["jibun"]}")으로 {len(narrowed)}건으로 좁힘', flush=True)
            matched = narrowed

    # [2026-09-17 추가 — 사용자 발견, 실사용 재현·웹 조사로 확인] 한 지번 위에 일반건물이 2동 이상이면
    # 「건축물대장의 기재 및 관리 등에 관한 규칙」 제5조에 따라 총괄표제부에 "제1동"/"제2동"처럼 동
    # 단위로 구분 표기하는 게 법정 표준이다(매물 854687로 재현: 소재지번검색·도로명주소검색 둘 다
    # "...외 1필지 1동"/"...외 1필지 2동" 2건으로 갈렸고, 소유자도 마스킹돼 같아서 구분 불가였다 —
    # 도로명주소도 두 건물이 완전히 동일해서 소용없었음, 이 함수 docstring/커밋이력 참고). 이 동
    # 번호는 매물번호 기반 payload는 'brtit_dong_name'("제1동" 형식, getIrosIssuePayload()가 채움)에,
    # 직접입력 payload는 location_search.building_dong_no(숫자만, buildManualIrosPayload() 참고)에
    # 있다 — 둘 다 값의 출처만 다를 뿐 검색결과 주소란 텍스트와 대조하는 용도는 같으므로 나란히
    # 확인한다. "1동"이 "21동"의 부분 문자열로 잘못 걸리지 않도록 숫자 경계를 확인한다(정규식 음성
    # 전방탐색).
    if len(matched) > 1:
        dongName = re.sub(r'^제\s*', '', str(payload.get('brtit_dong_name') or '').strip())
        if not dongName:
            buildingDongNo = str(loc.get('building_dong_no') or '').strip()
            if buildingDongNo:
                dongName = buildingDongNo + '동'
        if dongName and re.match(r'^\d+동$', dongName):
            dongPattern = re.compile(r'(?<!\d)' + re.escape(dongName))
            narrowed = []
            for tr in matched:
                addr_td = _find_row_addr_cell(tr)
                if addr_td is None:
                    continue
                if dongPattern.search(_squash(addr_td.text)):
                    narrowed.append(tr)
            if 0 < len(narrowed) < len(matched):
                print(f'[진행] 검색결과 {len(matched)}건 — 동 표시("{dongName}")로 {len(narrowed)}건으로 좁힘', flush=True)
                matched = narrowed

    if len(matched) == 0:
        return _fail('검색결과에서 일치하는 부동산을 찾지 못했습니다.')

    owner_masked = ''
    if len(matched) > 1:
        # [2026-09-19 재설계 — 사용자 지적 "여러 건이면 조용히 실패하고 끝나는 게 문제"] 예전엔 여기서
        # 바로 실패 처리했다 — 캡차·결제확인처럼 사람 판단이 필요한 상황인데 사람에게 알리지도 않고
        # 조용히 죽는 셈이었다(매물 278720 실사용 재현 — 저장된 정보만으로는 두 후보를 구분할 수
        # 없었다). 대신 사람에게 알리고, 브라우저 창에서 직접 체크+[다음]까지 마치고 넘어가길 기다린다
        # (_wait_for_human_to_pick_property() 참고) — 성공하면 아래 등기기록유형 선택 대기 루프로
        # 곧장 이어간다(사람이 이미 선택·[다음]까지 마쳤으므로 자동 선택 코드는 건너뛴다).
        if not _wait_for_human_to_pick_property(driver, len(matched)):
            return _fail(f'검색결과가 {len(matched)}건이라 자동으로 고르지 못했고, 담당자 선택도 시간 내에 끝나지 않았습니다.')
    else:
        row = matched[0]
        # [2026-09-07 추가 — 사용자 요청] 소유자 대조 — 등기소는 소유자를 "지**"처럼 가려서 보여준다
        # (content_iros.js에서 라이브로 확인된 사실, 2026-08-23). 완전일치 검사는 애초에 불가능하므로,
        # 담당자가 눈으로 대조할 수 있게 값만 그대로 돌려준다(자동 판정/중단에는 쓰지 않는다).
        try:
            owner_masked = row.find_element(By.CSS_SELECTOR, 'td[data-col_id="nomprs_name"]').text.strip()
        except NoSuchElementException:
            owner_masked = ''
        print(f'[진행] 대상 부동산 1건 특정 — 소유자(마스킹)={owner_masked}', flush=True)

        # [2026-09-19 수정 — 실사용 재현으로 원인 확인, 매물 10385] 예전엔 이 줄 선택 칸(WebSquare 그리드)
        # 안에서 <input>을 찾아 "이미 체크됐는지" 확인한 뒤에만 클릭했는데, 그 선택자가 실제로는 input을
        # 못 찾아(NoSuchElementException) 매번 "체크 안 됨"으로 잘못 판단했다 — 그 결과 검색결과가 1건이라
        # 사이트가 이미 자동으로 체크해둔 행을(위쪽 "검색결과 0건" 처리 부분 참고, 매물 490302/861597로
        # 이미 확인된 사이트 동작) 다시 눌러서 꺼버리는 사고로 이어졌다(담당자가 화면에서 체크 해제되는
        # 걸 직접 목격 — 예전에 고쳤다고 여겼던 매물 400603과 같은 유형의 사고가 감지 실패로 재발).
        #
        # DOM 선택자를 더 정밀하게 맞추려고 또 추측하는 대신, 이미 확실히 알고 있는 사실 두 가지로
        # 접근을 바꾼다: ①원본 검색결과(len(rows), 위에서 이미 구함)가 1건이면 사이트가 자동 선택하므로
        # 아예 클릭하지 않는다 — 여러 건 중 우리가 동/지번으로 좁혀 1건만 골랐을 때(len(rows) > 1)만
        # 사이트가 선택을 안 해주므로 그때만 클릭한다. ②"진짜 선택됐는지"는 DOM 상태를 우리가 추측하지
        # 않고, [다음]을 누른 뒤 사이트 자신이 "열람발급할 부동산을 선택하시기 바랍니다" 안내창을
        # 띄우는지로 판단한다 — 이게 선택 여부를 가장 확실하게 알려주는 신호다.
        sel_cell = row.find_element(By.CSS_SELECTOR, 'td[data-col_id="rad_sel"]')

        def _click_selection_cell():
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", sel_cell)
            try:
                ActionChains(driver).move_to_element(sel_cell).click().perform()
            except Exception as e:
                print(f'[진행] 부동산 선택 클릭 실패({type(e).__name__}) — execute_script 방식으로 재시도', flush=True)
                _click_with_fallback(driver, sel_cell)
            time.sleep(0.5)

        if len(rows) == 1:
            print('[진행] 부동산 선택 — 검색결과 원본이 1건이라 사이트가 이미 선택한 상태로 보고 클릭하지 않음', flush=True)
        else:
            print(f'[진행] 부동산 선택 — 원본 검색결과 {len(rows)}건 중 조건에 맞는 1건을 좁혔으므로 직접 클릭', flush=True)
            _click_selection_cell()

        nb = _next_button(driver)
        if not nb:
            return _fail('[다음] 버튼을 찾지 못했습니다(부동산 선택 후).', owner_masked)
        _click_with_fallback(driver, nb)
        time.sleep(0.6)

        if _is_selection_required_popup_visible(driver):
            # 예상과 반대로 선택이 안 돼 있었던 경우(또는 반대로 이미 선택된 걸 눌러 꺼버린 경우) —
            # 사이트가 직접 알려준 신호이므로 추측 없이 그대로 따른다: 안내창을 닫고 체크박스를 눌러
            # 다시 선택한 뒤 [다음]을 한 번 더 시도한다.
            print('[진행] "열람발급할 부동산을 선택하시기 바랍니다" 안내창 발견 — 다시 선택 후 재시도', flush=True)
            _dismiss_selection_required_popup(driver)
            _click_selection_cell()
            nb2 = _next_button(driver)
            if not nb2:
                return _fail('[다음] 버튼을 찾지 못했습니다(부동산 재선택 후).', owner_masked)
            _click_with_fallback(driver, nb2)
            time.sleep(0.6)
            if _is_selection_required_popup_visible(driver):
                return _fail('부동산을 선택했지만 "열람발급할 부동산을 선택하시기 바랍니다" 안내창이 계속 뜹니다.', owner_masked)

        print('[진행] 부동산 선택 완료, 다음 화면으로 이동', flush=True)

    record_select_el = None
    for _ in range(20):
        try:
            record_select_el = driver.find_element(By.ID, f'{BASE}_sel_cpab_kncd_input_0')
            break
        except NoSuchElementException:
            # [2026-09-07] 이 루프는 최악의 경우 20초를 통째로 소진한다 — 설치 안내 페이지로
            # 튕긴 상태라면 그 20초를 다 기다릴 필요 없이 바로 포기하고 재시도로 넘어간다.
            _guard_not_stuck_on_security_page(driver)
            titles = _visible_section_titles(driver)
            if any('소재지번 선택' in t for t in titles):
                nb2 = _next_button(driver)
                if nb2:
                    _click_with_fallback(driver, nb2)
            time.sleep(0.5)
    if record_select_el is None:
        return _fail('등기기록유형 선택 화면에 도달하지 못했습니다.', owner_masked)
    print('[진행] 등기기록유형 선택 화면 도달', flush=True)

    wanted = payload.get('register_record_type') or '현재유효사항'
    try:
        Select(record_select_el).select_by_visible_text(wanted)
        print(f'[진행] 등기기록유형 "{wanted}" 선택 완료', flush=True)
    except Exception:
        pass  # 기본값 그대로 진행 — 조회에는 영향 없다
    time.sleep(0.6)

    reached = None
    last_titles = []
    # 12회×2.5초(최악 30초) — 이 한도 안에서 "로딩 중 대기"와 "[다음] 화면 넘김"을 함께 소화한다.
    # 보안프로그램 설치페이지로 튕긴 경우는 _guard_not_stuck_on_security_page()가 먼저 끊으므로
    # 이 한도를 다 쓰는 일은 정말로 화면이 안 바뀔 때뿐이다.
    for _ in range(12):
        _guard_not_stuck_on_security_page(driver)
        titles = _visible_section_titles(driver)
        print(f'[진행] 현재 화면 제목={titles}', flush=True)
        # [2026-09-08 변경 — 실측으로 원인 확인] 제목이 하나도 안 잡히는 건 "모르는 화면"이 아니라 대개
        # 아직 로딩 중인 상태다(WebSquare가 화면 내용을 갈아끼우는 사이 h4가 없거나 "처리 중입니다"
        # 레이어). 예전엔 1.5초 한 번 더 보고 곧바로 "예상하지 못한 화면"으로 실패시켰는데, 같은 매물이
        # 다른 시각엔 같은 지점을 통과했으므로 등기소 응답이 느린 순간을 실패로 오판한 것(994214,
        # 2026-09-08 17:18 진행로그) — 비어 있으면 [다음]을 누르지 않고 이 루프 안에서 다시 기다린다.
        if not titles:
            time.sleep(1.5)
            continue
        last_titles = titles
        if any(k in t for t in titles for k in PAYMENT_TITLES):
            reached = 'payment'
            break
        if not any(k in t for t in titles for k in PASS_THROUGH_TITLES):
            return _fail(f'예상하지 못한 화면입니다 — {titles}', owner_masked)
        nb3 = _next_button(driver)
        if not nb3:
            return _fail(f'[다음] 버튼을 찾지 못했습니다 — {titles}', owner_masked)
        _click_with_fallback(driver, nb3)
        time.sleep(1.5)

    if reached != 'payment':
        return _fail(f'결제대상 확인 화면에 도달하지 못했습니다(마지막으로 본 화면 제목={last_titles}).', owner_masked)
    print('[진행] 결제대상 확인 화면 도달', flush=True)
    time.sleep(0.5)

    pay_tbody = driver.find_element(By.ID, f'{BASE}_grd_bpay_obj_list_body_tbody')
    pay_rows = [tr for tr in pay_tbody.find_elements(By.TAG_NAME, 'tr')
                if 'display: none' not in (tr.get_attribute('style') or '')]

    dong_jibun = _squash(loc['dong_or_li']) + _squash(loc['jibun'])
    for tr in pay_rows:
        addr_td = _find_row_addr_cell(tr)
        if addr_td is None:
            continue
        addr_text = addr_td.text.strip()
        if loc.get('sigungu') and _squash(loc['sigungu']) not in _squash(addr_text):
            continue
        if dong_jibun not in _squash(addr_text):
            continue
        try:
            checkbox = tr.find_element(By.CSS_SELECTOR, 'td[data-col_id="chk_sel"] input[type="checkbox"]')
            if not checkbox.is_selected():
                _click_with_fallback(driver, tr.find_element(By.CSS_SELECTOR, 'td[data-col_id="chk_sel"] label'))
                time.sleep(0.8)
        except NoSuchElementException:
            pass
        unique_no = ''
        m = re.search(r'\d{4}-\d{4}-\d{6}', tr.text)
        if m:
            unique_no = m.group(0)
        print(f'[진행] 등기상 주소·고유번호 확인 완료 — 주소={addr_text}, 고유번호={unique_no}', flush=True)
        # 여기서 반드시 멈춘다 — [결제] 버튼은 절대 누르지 않는다(원본 크롬확장의 확고한 원칙).
        return {'ok': True, 'address': addr_text, 'unique_no': unique_no, 'owner_masked': owner_masked, 'message': ''}

    return _fail('결제대상 표에서 일치하는 줄을 찾지 못했습니다.', owner_masked)


# ────────────────────────────────────────────────────────────────────────
# [2026-09-07 신규] 등기부등본 전체 발급(로그인 → 결제 → 열람 → 다운로드) — 크롬확장
# content_iros.js의 같은 이름 함수들을 그대로 옮겼다(proceedToPaymentScreen/routeAfterPaymentClick/
# fillLoginPopupIfPresent/handleDuplicatePaymentScreen/preparePaymentScreen/finishAfterPaymentConfirm/
# viewAndSaveFromListRows).
# ────────────────────────────────────────────────────────────────────────

def _is_duplicate_payment_popup_visible(driver):
    """content_iros.js::isDuplicatePaymentPopupVisible() 이식 — "중복결제 확인"은 본문 섹션 h4로
    뜰 때도, body 바로 밑 별도 팝업창(id 중간에 열 때마다 바뀌는 숫자가 낌)으로 뜰 때도 있다."""
    if any('중복결제 확인' in t for t in _visible_section_titles(driver)):
        return True
    for el in driver.find_elements(By.CSS_SELECTOR, '[id$="_header_title"]'):
        if el.is_displayed() and '중복결제 확인' in el.text:
            return True
    return False


def _handle_duplicate_payment_screen(driver):
    """이미 결제된 건이 있으면 [이동]으로 그 건을 쓴다(중복 결제 방지) — 여러 건이면 첫 줄."""
    try:
        tbody = driver.find_element(
            By.CSS_SELECTOR, '[id^="mf_wfm_potal_main_wfm_content"][id$="grd_dup_bpay_list_body_tbody"]')
    except NoSuchElementException:
        return False
    rows = [tr for tr in tbody.find_elements(By.TAG_NAME, 'tr') if 'display: none' not in (tr.get_attribute('style') or '')]
    if not rows:
        return False
    move_btn = None
    for e in rows[0].find_elements(By.CSS_SELECTOR, 'a, button, input'):
        text = (e.text or e.get_attribute('value') or '').strip()
        if '이동' in text:
            move_btn = e
            break
    if not move_btn:
        return False
    _click_with_fallback(driver, move_btn)
    time.sleep(1)
    return True


def _is_captcha_required(driver):
    """로그인화면에 캡차(자동입력 방지문자)가 나타났는지 확인한다. [2026-09-18 신규 — 실사용 중
    발견] 등기소가 반복된 자동화 접속을 감지해 로그인에 캡차를 요구하기 시작했다(매물 400603/854687
    반복 테스트 중 재현). 캡차는 사람이 직접 읽고 입력해야 하는 값이라 자동으로 풀 수 없다(정책상
    시도하지 않음) — 이 함수는 캡차가 나타났는지만 판별해서 사람에게 알리고 기다리는 용도로만 쓴다.
    선택자는 실제 로그인화면 HTML로 확인한 값(2026-09-18, 사용자 제공)."""
    try:
        answer_input = driver.find_element(By.CSS_SELECTOR, 'input[id$="_answer___input"]')
    except NoSuchElementException:
        return False
    return answer_input.is_displayed()


def _prefill_login_page_credentials(driver, credentials):
    """검색이 로그인화면(독립 페이지, 결제 팝업과는 다른 화면)으로 튕겼을 때 아이디/비번칸을
    미리 채운다 — 담당자는 캡차만 입력하면 된다. [2026-09-18 신규 — 사용자 요청] 로그인 버튼은
    누르지 않는다(_fill_login_popup_if_present()와 다른 점) — 캡차를 아직 안 입력한 상태라 눌러도
    실패하므로, 로그인 자체는 사람이 캡차 입력 후 직접 완료한다. 선택자는 실제 로그인화면 HTML로
    확인한 값(2026-09-18, 사용자 제공) — 결제 팝업의 popup_user_id_g/popup_mbr_pw_g와는 다른
    네임스페이스(sbx_user_id_g/sct_mbr_pw_g)를 쓰는 별개의 화면이다."""
    iros_id = (credentials or {}).get('iros_id') or ''
    iros_pw = (credentials or {}).get('iros_pw') or ''
    if not iros_id or not iros_pw:
        return
    try:
        id_input = driver.find_element(By.CSS_SELECTOR, 'input[id$="sbx_user_id_g___input"]')
        if id_input.is_displayed() and not id_input.get_attribute('value'):
            _type_into_field(driver, id_input, iros_id)
    except NoSuchElementException:
        pass
    try:
        pw_input = driver.find_element(By.CSS_SELECTOR, 'input[id$="sct_mbr_pw_g"]')
        if pw_input.is_displayed() and not pw_input.get_attribute('value'):
            _type_into_field(driver, pw_input, iros_pw)
    except NoSuchElementException:
        pass


def _wait_for_human_to_clear_captcha(driver, timeout_seconds=300):
    """캡차가 화면에서 사라질 때까지(=사람이 캡차를 직접 입력하고 로그인을 완료할 때까지) 기다린다.
    [2026-09-18 신규 — 사용자 요청] 알림창은 발견 시 한 번만 띄운다 — 담당자가 그 창을 닫기 전에
    이미 캡차를 입력해뒀을 수도 있으므로, 창을 띄우자마자 폴링을 시작해 그런 경우 곧바로 이어간다."""
    print('[진행] 로그인화면에 캡차(자동입력 방지문자) 발견 — 담당자 입력 대기', flush=True)
    try:
        import pyautogui
        pyautogui.alert(
            '인터넷등기소 로그인에 자동입력 방지문자(캡차)가 나타났습니다.\n\n'
            '아이디/비밀번호는 이미 입력해뒀습니다 — 캡차만 입력하고 로그인해주세요.\n'
            '로그인이 완료되면 자동으로 이어서 진행됩니다.',
            '[인터넷등기소] 캡차 입력 필요',
        )
    except Exception:
        pass
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        if not _is_captcha_required(driver):
            print('[진행] 캡차 화면이 사라짐 — 로그인 완료로 보고 이어서 진행', flush=True)
            return True
        time.sleep(1)
    print('[진행] 캡차 입력 대기시간을 초과함', flush=True)
    return False


def _fill_login_popup_if_present(driver, credentials):
    """content_iros.js::fillLoginPopupIfPresent() 이식. 팝업 id에 열 때마다 바뀌는 숫자가 껴서
    끝부분으로만 찾는다."""
    try:
        id_input = driver.find_element(By.CSS_SELECTOR, 'input[id$="popup_user_id_g___input"]')
    except NoSuchElementException:
        return {'shown': False}
    if not id_input.is_displayed():
        return {'shown': False}

    iros_id = credentials.get('iros_id') or ''
    iros_pw = credentials.get('iros_pw') or ''
    if not iros_id or not iros_pw:
        return {'shown': True, 'ok': False, 'message': '등기소 로그인 정보가 없습니다.'}

    # [2026-09-18 수정 — 사용자 요청 "캡차 떠도 아이디/비번은 자동으로 채워주자"] 캡차가 있든
    # 없든 아이디/비번은 먼저 채운다 — 이 둘은 캡차와 무관하게 항상 채울 수 있는 값이라, 담당자가
    # 캡차만 입력하면 되게 한다.
    _type_into_field(driver, id_input, iros_id)
    try:
        pw_input = driver.find_element(By.CSS_SELECTOR, 'input[id$="popup_mbr_pw_g"]')
    except NoSuchElementException:
        return {'shown': True, 'ok': False, 'message': '비밀번호 입력칸을 찾지 못했습니다.'}
    _type_into_field(driver, pw_input, iros_pw)

    # 캡차가 떠 있으면 로그인 버튼은 누르지 않는다 — 캡차 없이 제출하면 실패한다. 담당자가 캡차만
    # 입력하고 직접 로그인 버튼을 누르면 된다.
    if _is_captcha_required(driver):
        if _wait_for_human_to_clear_captcha(driver):
            return {'shown': True, 'ok': True}
        return {'shown': True, 'ok': False, 'message': '캡차 입력 대기시간을 초과했습니다.'}

    try:
        login_btn = driver.find_element(By.CSS_SELECTOR, 'input[id$="btn_popup_login_g"]')
    except NoSuchElementException:
        return {'shown': True, 'ok': False, 'message': '로그인 버튼을 찾지 못했습니다.'}
    _click_with_fallback(driver, login_btn)
    deadline = time.time() + 2
    while time.time() < deadline:
        _dismiss_alert_if_present(driver)
        try:
            if not id_input.is_displayed():
                break
        except Exception:
            break
        try:
            pay_tab = driver.find_element(By.ID, f'{BASE}_tac_bpay_mthd_tab_tab_pp_tabHTML')
            if pay_tab.is_displayed():
                break
        except NoSuchElementException:
            pass
        time.sleep(0.2)
    return {'shown': True, 'ok': True}


def _route_after_payment_click(driver, credentials, wait_seconds=15):
    """content_iros.js::routeAfterPaymentClick() 이식 — [결제] 클릭 후 나타나는 화면을 판별해
    분기한다. 로그인 팝업 → 결제 준비 화면 순으로 이어질 수 있어 재귀적으로 부른다.
    @return 'payment-prep' | 'duplicate-handled' | None(예상 못한 화면)
    """
    deadline = time.time() + wait_seconds
    screen = None
    while time.time() < deadline:
        if _is_duplicate_payment_popup_visible(driver):
            screen = 'duplicate'
            break
        try:
            pay_tab = driver.find_element(By.ID, f'{BASE}_tac_bpay_mthd_tab_tab_pp_tabHTML')
            if pay_tab.is_displayed():
                screen = 'payment-prep'
                break
        except NoSuchElementException:
            pass
        try:
            login_popup = driver.find_element(By.CSS_SELECTOR, 'input[id$="popup_user_id_g___input"]')
            if login_popup.is_displayed():
                screen = 'login'
                break
        except NoSuchElementException:
            pass
        time.sleep(0.5)

    if screen == 'login':
        login_result = _fill_login_popup_if_present(driver, credentials)
        if not login_result.get('ok'):
            return None
        return _route_after_payment_click(driver, credentials, wait_seconds=15)
    if screen == 'duplicate':
        if _handle_duplicate_payment_screen(driver):
            return 'duplicate-handled'
        return None
    if screen == 'payment-prep':
        return 'payment-prep'
    return None


def _prepare_payment_screen(driver, credentials):
    """content_iros.js::preparePaymentScreen()의 준비 단계(①~③)만 이식 — 결제수단 탭 선택,
    이용동의 체크, 선불전자지급수단 번호·비밀번호 입력까지. 실제 [결제] 클릭은 호출부(auto_confirm
    여부)가 판단하므로 여기서 하지 않는다.
    @return {'ready': bool, 'message': str}
    """
    try:
        tab = driver.find_element(By.ID, f'{BASE}_tac_bpay_mthd_tab_tab_pp_tabHTML')
        if tab.is_displayed():
            _click_with_fallback(driver, tab)
            time.sleep(0.2)
    except NoSuchElementException:
        return {'ready': False, 'message': '결제수단(선불전자지급수단) 탭을 찾지 못했습니다.'}

    try:
        agree_label = driver.find_element(By.CSS_SELECTOR, f'#{BASE}_chk_whl_agree li label')
        agree_input = driver.find_element(By.CSS_SELECTOR, f'#{BASE}_chk_whl_agree input[type="checkbox"]')
        if not agree_input.is_selected():
            _click_with_fallback(driver, agree_label)
            time.sleep(0.6)
    except NoSuchElementException:
        return {'ready': False, 'message': '이용동의 항목을 찾지 못했습니다.'}

    emoney_no = str(credentials.get('iros_emoney_no') or '').replace(' ', '')
    emoney_pw = str(credentials.get('iros_emoney_pw') or '')
    if not emoney_no or not emoney_pw:
        return {'ready': False, 'message': '선불전자지급수단 정보가 없습니다.'}
    if len(emoney_no) < 12:
        return {'ready': False, 'message': f'선불전자지급수단 번호가 12자리가 아닙니다({len(emoney_no)}자).'}

    try:
        no1_el = driver.find_element(By.ID, f'{BASE}_sbx_emoney_code1___input')
        no2_el = driver.find_element(By.ID, f'{BASE}_sbx_emoney_code2___input')
        pw_el = driver.find_element(By.ID, f'{BASE}_sct_emoney_pwd')
    except NoSuchElementException:
        return {'ready': False, 'message': '선불전자지급수단 입력칸을 찾지 못했습니다.'}

    # [2026-09-08 변경] 자바스크립트 값 주입 대신 진짜 타이핑으로 — 위 _type_into_field() 주석 참고.
    _type_into_field(driver, no1_el, emoney_no[:8])
    _type_into_field(driver, no2_el, emoney_no[-4:])
    _type_into_field(driver, pw_el, emoney_pw)
    time.sleep(0.4)
    return {'ready': True, 'message': ''}


def _finish_after_payment_confirm(driver):
    """content_iros.js::finishAfterPaymentConfirm() 이식 — 결제요청 확인 팝업 [확인] → 결제결과
    확인(있으면) 까지."""
    deadline = time.time() + 15
    confirm_btn = None
    while time.time() < deadline:
        _dismiss_alert_if_present(driver)  # 다른 폴링 루프와 같은 이유 — 대기 중 alert가 떠도 다음 바퀴에서 걷힌다
        try:
            el = driver.find_element(By.CSS_SELECTOR, 'a[id$="_wframe_btn_confirm2"]')
            if el.is_displayed():
                confirm_btn = el
                break
        except NoSuchElementException:
            pass
        time.sleep(0.5)
    if not confirm_btn:
        return {'ok': False, 'message': f'결제요청 확인 팝업의 [확인] 버튼을 찾지 못했습니다. | {_diag_snapshot(driver)}'}
    _click_with_fallback(driver, confirm_btn)
    time.sleep(1.5)

    try:
        result_btn = driver.find_element(By.CSS_SELECTOR, 'input[id$="_btn_cfrm"]')
        if result_btn.is_displayed():
            _click_with_fallback(driver, result_btn)
            time.sleep(1)
    except NoSuchElementException:
        pass
    return {'ok': True, 'message': ''}


def _wait_for_target_list_rows(driver, timeout=15):
    """content_iros.js::advanceToPaymentScreen()의 목록 대기 부분 이식 — "미열람"/"재열람" 목록은
    h4 제목이 없어 제목 판별이 아니라 행 유무로만 알아본다."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        for tbody_id in (f'{BASE}_grd_nview_nissue_list_body_tbody', f'{BASE}_grd_rview_list_body_tbody'):
            try:
                tbody = driver.find_element(By.ID, tbody_id)
            except NoSuchElementException:
                continue
            if not tbody.is_displayed():
                continue
            rows = [tr for tr in tbody.find_elements(By.TAG_NAME, 'tr')
                    if 'display: none' not in (tr.get_attribute('style') or '') and tr.text.strip() != '']
            if rows:
                return rows
        time.sleep(1)
    return []


def _view_and_save(driver, payload, download_dir):
    """content_iros.js::viewAndSaveFromListRows() 이식 — 목록에서 이번 물건 줄을 대조해 찾은 뒤
    [열람] → [저장]까지. 첫 줄을 무조건 열람하지 않는다(열람은 되돌릴 수 없다 — 결제취소 불가)."""
    rows = _wait_for_target_list_rows(driver)
    if not rows:
        return {'ok': False, 'message': f'열람 목록을 찾지 못했습니다. | {_diag_snapshot(driver)}'}

    target_row = None
    for tr in rows:
        try:
            td = tr.find_element(By.CSS_SELECTOR, 'td[data-col_id="real_indi_cont"]')
        except NoSuchElementException:
            continue
        if _row_matches_target(td.text, payload):
            target_row = tr
            break
    if target_row is None:
        return {'ok': False, 'message': f'열람 목록에서 이번 물건을 찾지 못했습니다 — 엉뚱한 문서를 열람하지 않도록 멈춥니다. | {_diag_snapshot(driver)}'}

    view_btn = None
    try:
        view_btn = target_row.find_element(By.ID, 'btn_issue')
    except NoSuchElementException:
        for e in target_row.find_elements(By.CSS_SELECTOR, 'a, button, input'):
            text = (e.text or e.get_attribute('value') or e.get_attribute('title') or '')
            if '열람' in text:
                view_btn = e
                break
    if not view_btn:
        return {'ok': False, 'message': f'목록에서 [열람] 버튼을 찾지 못했습니다. | {_diag_snapshot(driver)}'}
    _click_with_fallback(driver, view_btn)
    time.sleep(1)

    try:
        save_btn = driver.find_element(By.CSS_SELECTOR, 'input[id$="_btn_download"]')
    except NoSuchElementException:
        return {'ok': False, 'message': f'저장 버튼을 찾지 못했습니다 — 열람까지는 진행됐습니다(결제취소 불가 상태). | {_diag_snapshot(driver)}'}
    _click_with_fallback(driver, save_btn)

    downloaded = _wait_for_download(download_dir, timeout=60)
    if not downloaded:
        return {'ok': False, 'message': f'다운로드가 완료되지 않았습니다(60초 대기) — 열람까지는 진행됐습니다. | {_diag_snapshot(driver)}'}
    return {'ok': True, 'file_path': downloaded, 'message': ''}


def _wait_for_download(download_dir, timeout=60):
    """download_dir에 새 파일이 완전히 받아질 때까지 기다린다. 크롬은 받는 동안 .crdownload
    확장자를 붙이므로 그게 사라지고 크기가 두 번 연속 같을 때 완료로 본다."""
    deadline = time.time() + timeout
    last_size = {}
    while time.time() < deadline:
        names = [n for n in os.listdir(download_dir) if not n.endswith('.crdownload') and not n.startswith('.')]
        if names:
            path = os.path.join(download_dir, names[0])
            size = os.path.getsize(path)
            if last_size.get(names[0]) == size and size > 0:
                return path
            last_size[names[0]] = size
        time.sleep(1)
    return None


def _alert_stop_before_view(driver, reason):
    """[2026-09-08 추가 — 사용자 요청] stop_before_view로 멈출 때, 결과값만 조용히 반환하는 대신
    화면에 실제로 보이는 알림창을 띄운다 — 담당자가 지켜보다가 "여기서 멈췄다"를 놓치지 않게 하기
    위함(테스트용 안전장치이므로 close_when_done=False와 함께 쓰는 걸 전제로 한다 — 창을 닫아버리면
    이 알림도 같이 사라진다)."""
    try:
        driver.execute_script("alert(arguments[0]);", f'[테스트] {reason} — 열람(인쇄)은 하지 않고 여기서 멈췄습니다.')
    except Exception:
        pass


def _alert_failure_and_keep_window_open(driver, message):
    """[2026-09-13 추가 — 사용자 요청 "오류가 발생하면 조용히 죽는데, 숨김모드가 아니면 알림창을
    띄워서 왜 멈췄는지 알 수 있게 하고 싶다"] 지금까지는 실패 사유가 진행로그 파일에만 남아서,
    창이 보이는 상태로 지켜보고 있어도 창이 그냥 닫혀버리면 왜 멈췄는지 그 자리에서 알 방법이
    없었다. _alert_stop_before_view()와 같은 방식(alert 대화상자)을 실패 상황에도 적용한다.

    driver.execute_script("alert(...)")는 대화상자가 뜨는 즉시 반환된다(모달이 막는 건 페이지의
    JS 실행이지, 이 커맨드 자체가 아니다) — 그래서 알림을 띄운 직후 창을 닫아버리면 사람이 읽기도
    전에 알림이 창과 함께 사라진다. issue_real_estate_register()의 finally에서 이 함수를 부른
    직후 close_when_done을 강제로 꺼서, "완료 후 창 모두 닫기"가 켜져 있었어도(숨김모드가 아닌 한)
    이번 실패 건만은 창이 남아 담당자가 알림을 직접 확인·해제할 수 있게 한다."""
    try:
        driver.execute_script("alert(arguments[0]);", f'[오류] {message}\n\n이 창은 자동으로 닫히지 않습니다 — 확인 후 직접 닫아주세요.')
    except Exception:
        pass


def issue_real_estate_register(payload, credentials, options=None):
    """
    [2026-09-07 신규] 등기부등본을 로그인부터 결제·열람·다운로드까지 전체 발급한다.

    payload: getIrosIssuePayload()가 계산한 값 + save.filename(저장할 파일명, 확장자 포함).
    credentials: {'iros_id','iros_pw','iros_emoney_no','iros_emoney_pw'} — api/get_api_lib.php의
        fn=getirosservicecredentials 로 받아온 값을 그대로 넘기면 된다.
    options: {
        'headless': bool = True,        # "몰래(창 안 띄우고) 작동"
        'auto_confirm': bool = True,    # "신청확인 자동 진행" — 꺼지면 결제 버튼을 사람이 누르길 기다림
        'close_when_done': bool = True, # "완료 후 사용된 창 모두 닫기"
        'lookup_only': bool = False,    # [2026-09-07 추가 — 사용자 요청] "조회만 진행(결제 안 함)".
            # 켜면 verify_register_target()까지만 하고 반환한다 — 결제 버튼 자체를 누르지 않는다.
            # 숨김모드(headless=True)는 원래 auto_confirm을 강제로 켜서 결제까지 자동으로 나가는데,
            # 이 옵션으로 숨김모드에서도 결제 없이 조회만 하는 선택지를 남긴다 — 조회 전용
            # 진입점이었던 옛 find_register_address()가 하던 일을 이 옵션 하나로 대체했다
            # (2026-09-19, 위 파일 상단 주석 참고). 화면 표시 여부·창 닫기 여부는 이 함수의 다른
            # 옵션을 그대로 따른다.
        'stop_before_view': bool = False,  # [2026-09-08 추가 — 사용자 요청, 실결제 검증용 안전장치]
            # 결제(700원)는 실제로 진행하되, [열람] 버튼은 누르지 않고 멈춘다 — 등기소는 열람 전까지는
            # 결제취소가 가능하므로, 결제 자체가 정상적으로 되는지만 안전하게 확인하고 싶을 때 쓴다.
    }
    headless=True면 auto_confirm/close_when_done은 항상 True로 강제한다(호출부 문서 참고). lookup_only는
    이 강제와 무관하게 항상 우선한다 — 결제 자체를 안 하므로 "결제를 자동으로 할지"는 애초에 의미가 없다.

    @return {'ok': bool, 'file_path': str(로컬 임시경로, NAS 저장은 호출부 책임 — lookup_only면 항상 빈 값),
             'address': str, 'unique_no': str, 'owner_masked': str, 'message': str,
             'user_cancelled': bool(담당자가 자동화 창을 완료 전에 직접 닫은 경우에만 True —
                 2026-09-12 추가, local_helper/main.py가 이 값을 보고 오류로그 대신 취소로 기록한다)}
    """
    options = dict(options or {})
    headless = bool(options.get('headless', True))
    lookup_only = bool(options.get('lookup_only', False))
    stop_before_view = bool(options.get('stop_before_view', False))
    auto_confirm = bool(options.get('auto_confirm', True))
    close_when_done = bool(options.get('close_when_done', True))
    if headless:
        auto_confirm = True
        close_when_done = True
    if lookup_only:
        close_when_done = True  # 조회만 하고 끝나므로 창을 열어둘 이유가 없다

    download_dir = os.path.join(tempfile.gettempdir(), f'obang_iros_issue_{uuid.uuid4().hex}')
    os.makedirs(download_dir, exist_ok=True)

    chrome_options = Options()
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    # [2026-09-08 변경 — 실측으로 원인 확인] 진짜 헤드리스(--headless=new)로 돌리면, 검색 단계는
    # 전부 통과하고도 "결제대상 확인" 화면에 들어가는 바로 그 순간 등기소가 "보안프로그램 설치가
    # 필요합니다" alert를 띄우며 막힌다(오늘 새로 추가한 진행로그로 직접 확인 — 보임모드로는 같은
    # 매물이 결제까지 성공했었다). 결제 단계에서만 이 alert가 뜨는 패턴으로 보아, 등기소(TouchEn
    # 보안프로그램)가 결제 진입 시점에 "진짜 렌더링 창이 있는지"를 확인하는 것으로 보인다 — 그래서
    # 창 자체는 진짜로 띄우되(headless 아님), 화면 밖 좌표로 옮겨 직원 모니터에는 보이지 않게 한다.
    # "몰래(창 안 띄우고) 작동" 옵션이 실사용자에게 약속하는 것(창이 안 보임)은 이 방식으로도 그대로
    # 지켜진다. [2026-09-19] 조회 전용으로 이 화면을 따로 거치던 find_register_address()는 제거되고
    # lookup_only 옵션으로 이 함수에 합쳐졌다 — 창 숨김 방식을 두 곳에서 따로 맞춰야 했던 동기화
    # 부담도 함께 없어졌다.
    if headless and IROS_TRUE_HEADLESS_FOR_TEST:
        chrome_options.add_argument('--headless=new')
        # [2026-09-08 임시 진단 — 실측으로 시도했으나 원인이 아닌 것으로 확인됨] 화면밖-창(보임)과
        # 진짜 헤드리스를 로컬에서 직접 비교했을 때 눈에 띄게 다른 값이 두 가지였다: User-Agent에
        # "HeadlessChrome"이 그대로 노출되는 것, screen.width/height가 가짜 800x600인 것
        # (webdriver/플러그인개수/WebGL은 이미 동일했음). 이 둘을 아래 CDP 설정과 함께 보임모드
        # 값으로 위장해서 재현했지만 **결제대상 확인 화면에서 여전히 똑같이 막혔다** — 즉 등기소
        # (TouchEn)의 판별 근거는 User-Agent나 화면크기 같은 JS로 조작 가능한 값이 아니다(반증
        # 완료). 다음에 이 값들을 다시 건드려볼 필요는 없다 — 남은 후보는 JS로 흉내 낼 수 없는
        # 더 근본적인 신호(예: 실제 GPU 합성 여부, CDP 프로토콜 자체 감지 등)로 보인다(추정).
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 Safari/537.36')
    chrome_options.add_experimental_option('prefs', {
        'download.default_directory': download_dir,
        'download.prompt_for_download': False,
        'download.directory_upgrade': True,
        'plugins.always_open_pdf_externally': True,  # PDF 뷰어로 열지 않고 그대로 다운로드
    })
    driver = _launch_chrome(chrome_options)
    # [2026-09-13 추가 — 사용자 리포트로 발견된 버그 수정] stop_before_view=True로 멈춘 경우
    # ok=True인데도 file_path가 항상 빈 값이다(원래 설계 — 결제만 하고 열람·다운로드는 일부러
    # 안 함). 그런데 호출부(local_helper/main.py)가 이 둘을 구분하지 않고 ok=True면 무조건 파일을
    # NAS로 옮기려 시도해서, "옮길 파일 경로가 없습니다"라는 엉뚱한 이유로 "발급 실패"가 오류로그에
    # 잘못 남았다(실사용 재현, object_code_new=490302). 호출부가 "파일이 없는 게 정상인 멈춤"과
    # "진짜 실패"를 구분할 수 있도록 플래그를 추가한다.
    result = {'ok': False, 'file_path': '', 'address': '', 'unique_no': '', 'owner_masked': '', 'message': '',
              'user_cancelled': False, 'stopped_before_view': False}
    try:
        print(f'[진행] issue_real_estate_register 시작 — headless={headless}, true_headless_test={IROS_TRUE_HEADLESS_FOR_TEST}, lookup_only={lookup_only}, auto_confirm={auto_confirm}, stop_before_view={stop_before_view}', flush=True)
        driver.set_window_size(1280, 1000)
        if headless and not IROS_TRUE_HEADLESS_FOR_TEST:
            driver.set_window_position(80, 40)  # 사용자 확인이 가능하도록 보이는 위치에서 실행
        if headless and IROS_TRUE_HEADLESS_FOR_TEST:
            # --window-size 플래그로는 안 바뀌던 screen.width/height(가짜 800x600)를 CDP로 직접
            # 덮어쓴다 — 보임모드 실측값(1920x1080)에 맞춘다.
            driver.execute_cdp_cmd('Emulation.setDeviceMetricsOverride', {
                'width': 1280, 'height': 1000, 'deviceScaleFactor': 1, 'mobile': False,
                'screenWidth': 1920, 'screenHeight': 1080,
            })

        target = verify_register_target(driver, payload, credentials)
        result['address'] = target.get('address', '')
        result['unique_no'] = target.get('unique_no', '')
        result['owner_masked'] = target.get('owner_masked', '')
        if not target.get('ok'):
            result['message'] = target.get('message', '')
            return result
        if lookup_only:
            # 여기서 반드시 멈춘다 — [결제] 버튼은 절대 누르지 않는다(옛 find_register_address()가
            # 지키던 원칙 그대로).
            print('[진행] lookup_only — 조회만 하고 종료', flush=True)
            result['ok'] = True
            return result

        # [결제대상 확인] 화면의 [결제] — 아직 청구되지 않는다(로그인 팝업/결제 준비 화면으로 이어질
        # 뿐인 버튼, content_iros.js::proceedToPaymentScreen() 주석 참고).
        print('[진행] [결제] 버튼(첫 번째) 클릭 — 아직 청구되지 않음', flush=True)
        pay_btn = driver.find_element(By.ID, f'{BASE}_btn_bpay')
        _click_with_fallback(driver, pay_btn)
        time.sleep(1)

        routed = _route_after_payment_click(driver, credentials)
        print(f'[진행] 결제 클릭 후 라우팅 결과 = {routed}', flush=True)
        if routed == 'duplicate-handled':
            if stop_before_view:
                result['ok'] = True
                result['stopped_before_view'] = True
                result['message'] = '(stop_before_view) 이미 결제된 건으로 연결됨 — 열람 전에 멈췄습니다.'
                _alert_stop_before_view(driver, '이미 결제된 건으로 연결됨')
                return result
            save_result = _view_and_save(driver, payload, download_dir)
            result.update({'ok': save_result.get('ok', False), 'file_path': save_result.get('file_path', ''),
                            'message': save_result.get('message', '')})
            return result
        if routed != 'payment-prep':
            result['message'] = f'결제 화면 진입 중 예상하지 못한 화면이 나타났습니다. | {_diag_snapshot(driver)}'
            return result

        prep = _prepare_payment_screen(driver, credentials)
        if not prep.get('ready'):
            result['message'] = f'{prep.get("message", "결제 준비를 마치지 못했습니다.")} | {_diag_snapshot(driver)}'
            return result
        print('[진행] 결제수단(선불전자지급수단) 정보 입력 완료', flush=True)

        if auto_confirm:
            print('[진행] [결제] 버튼(두 번째, 실제 결제) 클릭 — 진짜 마우스 클릭 시도', flush=True)
            pay_btn2 = driver.find_element(By.ID, f'{BASE}_btn_bpay')
            # [2026-09-08 변경 — 실측으로 원인 확인] 다른 버튼들은 execute_script로 클릭해야
            # ElementNotInteractable 문제를 피할 수 있었지만(다른 요소에 가려지는 경우 등), 이
            # "실제 결제" 버튼을 누르는 바로 그 순간에만 셀레니움 연결(DevTools) 자체가 끊기는 게
            # 실측 확인됐다 — 자바스크립트로 흉내낸 클릭이 아니라 진짜 마우스 이벤트인지까지 이 PC의
            # 보안프로그램(AhnLab Safe Transaction 등, 실거래 감지가 목적인 프로그램)이 검사하고
            # 있을 가능성이 있어, 이 클릭만큼은 셀레니움 표준 click()(진짜 마우스 이벤트)으로
            # 시도한다. 다른 버튼과 달리 이 버튼은 화면에 가려질 일이 없어 표준 click()으로도
            # 문제없이 눌릴 것으로 본다 — 혹시 실패하면(가려짐 등) 기존 방식으로 한 번 더 시도한다.
            try:
                pay_btn2.click()
            except Exception as e:
                print(f'[진행] 표준 click() 실패({type(e).__name__}) — execute_script 방식으로 재시도', flush=True)
                _click_with_fallback(driver, pay_btn2)
        else:
            # [2026-09-07 신규 — 사용자 요청] "신청확인 자동 진행"이 꺼져 있으면(창이 실제로 보이는
            # 상태다 — headless일 땐 위에서 이미 auto_confirm을 강제로 켰다) 결제 버튼을 직접 누르지
            # 않는다. 화면이 진짜로 사람 눈앞에 떠 있으므로, 담당자가 자기 마우스로 직접 눌러도 된다
            # — 그동안 이 스크립트는 결제요청 확인 팝업이 뜨는지만 기다린다(content_iros.js가
            # auto_pay_registry_fee===false일 때 버튼만 남겨두고 사람 클릭을 기다리는 것과 같은 방식).
            # [2026-09-18 추가 — 사용자 요청] 캡차 대기(_wait_for_human_to_clear_captcha)와 같은 방식으로
            # 알림창을 띄운다 — 화면이 보임모드라도 담당자가 다른 일을 하다 놓칠 수 있으므로, [결제]를
            # 직접 눌러야 한다는 것과 최대 대기시간을 명시적으로 알려준다.
            print(f'[진행] 사람이 직접 [결제] 누르길 최대 {HUMAN_CONFIRM_TIMEOUT_SEC}초 대기 중...', flush=True)
            try:
                import pyautogui
                pyautogui.alert(
                    '인터넷등기소 화면에서 [결제] 버튼을 직접 눌러주세요.\n\n'
                    f'확인 후 최대 {HUMAN_CONFIRM_TIMEOUT_SEC}초({HUMAN_CONFIRM_TIMEOUT_SEC // 60}분) 동안 기다립니다.',
                    '[인터넷등기소] 결제 버튼 확인 필요',
                )
            except Exception:
                pass
            confirm_appears = False
            deadline = time.time() + HUMAN_CONFIRM_TIMEOUT_SEC
            while time.time() < deadline:
                try:
                    el = driver.find_element(By.CSS_SELECTOR, 'a[id$="_wframe_btn_confirm2"]')
                    if el.is_displayed():
                        confirm_appears = True
                        break
                except NoSuchElementException:
                    pass
                time.sleep(1)
            if not confirm_appears:
                result['message'] = (f'{HUMAN_CONFIRM_TIMEOUT_SEC}초 동안 결제 확인을 기다렸지만 진행되지 않았습니다 '
                                      f'— 화면에서 직접 진행해주세요. | {_diag_snapshot(driver)}')
                return result
            print('[진행] 결제요청 확인 팝업 감지됨', flush=True)

        finish = _finish_after_payment_confirm(driver)
        if not finish.get('ok'):
            result['message'] = f'{finish.get("message", "")} | {_diag_snapshot(driver)}'
            return result
        print('[진행] 결제 확정 완료', flush=True)

        if stop_before_view:
            # 여기서 멈춘다 — 결제는 이미 완료됐지만 [열람]은 아직 안 눌렀으므로 결제취소가 가능하다.
            print('[진행] stop_before_view — 열람 전에 멈춤', flush=True)
            result['ok'] = True
            result['stopped_before_view'] = True
            result['message'] = '(stop_before_view) 결제까지 완료, 열람 전에 멈췄습니다.'
            _alert_stop_before_view(driver, '결제까지 완료')
            return result

        print('[진행] 열람·다운로드 시작', flush=True)
        save_result = _view_and_save(driver, payload, download_dir)
        print(f'[진행] 열람·다운로드 결과 — ok={save_result.get("ok")}, file_path={save_result.get("file_path")}', flush=True)
        result.update({'ok': save_result.get('ok', False), 'file_path': save_result.get('file_path', ''),
                        'message': save_result.get('message', '')})
        return result

    except (NoSuchWindowException, InvalidSessionIdException):
        # [2026-09-12 추가 — 사용자 요청] 담당자가 자동화 창을 완료 전에 직접 닫은 경우다. 아래 일반
        # except의 "자동화 중 오류(...)" 문구는 시스템 버그로 오인되고 오류로그(pr_error_log)에도
        # 남는데, 이건 사람이 스스로 취소한 정상 동작이라 chrome_extension/background.js의
        # chrome.tabs.onRemoved 처리와 같은 기준으로 구분한다 — local_helper/main.py가
        # user_cancelled를 보고 오류로그를 건너뛴다(_report_document_issue_status 참고).
        print('[진행] 사용자가 자동화 창을 직접 닫음 — 정상 취소로 처리', flush=True)
        result['message'] = USER_CLOSED_WINDOW_MESSAGE
        result['user_cancelled'] = True
        return result
    except Exception as e:
        print(f'[오류] issue_real_estate_register 중 예외 발생: {type(e).__name__}: {e}', flush=True)
        result['message'] = f'자동화 중 오류({type(e).__name__}): {e} | {_diag_snapshot(driver)}'
        return result
    finally:
        # [2026-09-13 추가 — 사용자 요청] 실패(result['ok']=False)했는데 사람이 스스로 창을 닫은
        # 경우(user_cancelled)가 아니고 몰래 작동도 아니면, 사유를 알림창으로 띄우고 이번 실패
        # 건만은 close_when_done 설정과 무관하게 창을 열어둔다 — 담당자가 왜 멈췄는지 그 자리에서
        # 바로 읽을 수 있게 하기 위함(_alert_failure_and_keep_window_open() 참고).
        if not result['ok'] and not result.get('user_cancelled') and not headless:
            _alert_failure_and_keep_window_open(driver, result['message'])
            close_when_done = False
        if close_when_done:
            # [2026-09-12 추가] 사용자가 이미 창을 닫은 상태면 quit()도 예외를 낼 수 있다 — 위에서
            # 막 만든 result가 이 예외로 덮여 함수 자체가 크래시하지 않도록 보호한다.
            try:
                driver.quit()
            except Exception:
                pass
        # close_when_done=False면 창을 열어둔다 — 담당자가 화면을 보고 남은 절차를 직접 마칠 수 있게.
