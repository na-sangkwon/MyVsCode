# repos_python/OBJECT_reg/iros_document_issue.py
# (2026-09-06 iros_address_lookup.py로 시작 → 2026-09-07 등기부등본 "발급"까지 확장하며 이 이름으로
#  변경 — 처음엔 "주소만 조회"하는 좁은 범위였지만, 지금은 결제·열람·다운로드까지 다루므로 파일명도
#  실제 범위(등기부등본 "발급")에 맞춰 넓혔다. 함수는 새로 창작하지 않고 전부 크롬확장
#  (chrome_extension/iros_autofill/content_iros.js)의 같은 이름 로직을 셀레니움으로 옮긴 것이다
#  (그 파일 자체가 "화면 구성이 다양하니 범용판별 우선" 원칙으로 이미 여러 차례 실사용 검증을 거쳤다
#  — 원본 deunggi.py보다 그쪽을 정본으로 삼는다).
#
# [이 파일의 두 진입점]
#   find_register_address(payload)            — 결제 없이 등기상 주소·고유번호만 조회 (기존, 그대로 유지)
#   issue_real_estate_register(payload, credentials, options) — 로그인부터 결제·열람·다운로드까지 전체 발급 (신규)
# 두 진입점 모두 verify_register_target(driver, payload) 하나를 공유한다 — "등기상주소·소유주를
# 확인하는 과정"은 이 함수 하나뿐이고, 다른 곳에서 필요해지면 이 함수를 그대로 재사용하면 된다
# (사용자 요청, 2026-09-07 — 검증 로직을 두 곳에 따로 두면 한쪽만 고치는 사고로 이어지기 쉽다).
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
#   (추가) 진행 로그             print                              print('[진행] …') → main.py가 파일로 받아 화면(테스트페이지)까지 전달
# ─────────────────────────────────────────────────────────────────────────────

import re
import time
import os
import tempfile
import uuid

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, UnexpectedAlertPresentException, WebDriverException

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
                       '등기신청사건 처리여부 확인', '부동산 소재지번 선택']
PAYMENT_TITLES = ['결제대상 확인']

# [2026-09-07 신규] 결제 버튼을 누른 뒤 사람이 직접 누를 때까지 기다리는 최대 시간(초) —
# auto_confirm=False + 창이 보이는 상태에서만 쓰인다. 담당자가 자리를 비울 수도 있어 넉넉히 잡는다.
HUMAN_CONFIRM_TIMEOUT_SEC = 600


def _launch_chrome(chrome_options):
    """find_register_address()/issue_real_estate_register() 공용 — Chrome을 띄우는 지점을 하나로
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


def _js_click(driver, el):
    """WebDriver의 좌표 기반 click()이 커스텀 위젯(라디오/체크박스 td)에서 종종
    ElementNotInteractableException/ElementClickInterceptedException을 낸다(실측 확인, 2026-09-06 —
    검색결과 행의 rad_sel 셀, 결제대상 표의 체크박스, 플로팅 "맨 위로" 버튼에 가려진 [다음] 버튼).
    execute_script로 DOM에 직접 click 이벤트를 보내면 좌표·가시성 판정을 건너뛰어 더 안정적이다
    (content_iros.js의 .click()과 동일한 효과).

    [2026-09-07 추가 — 본섭 데이터(999071)로 재현] "보안프로그램 설치" alert는 접속 초기뿐 아니라
    흐름 중 아무 클릭 뒤에나 뜰 수 있다는 게 실측으로 확인됐다 — 클릭마다 즉시 흡수해야 어디서
    뜨든 다음 동작이 막히지 않는다(페이지 자체가 설치 안내로 넘어간 경우는 여기서 못 잡고 그
    클릭의 호출부가 반환값/다음 화면 판정으로 알아채게 된다)."""
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
    자바스크립트 주입 대신 진짜 키 입력처럼 한 글자씩 타이핑한다."""
    el.click()
    el.send_keys(Keys.CONTROL, 'a')
    el.send_keys(Keys.DELETE)
    el.send_keys(value)
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
        time.sleep(1.5)
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


def _squash(s):
    return re.sub(r'\s', '', s or '')


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


def verify_register_target(driver, payload):
    """
    [재사용 가능한 핵심 함수 — 사용자 요청, 2026-09-07] 로그인이 필요 없는 단계까지만 진행해서
    등기상주소·소유주(마스킹)·고유번호를 확인한다. 결제 버튼은 절대 누르지 않는다.

    driver는 호출부가 만들어서 넘긴다(생성·quit 여부는 호출부 책임) — find_register_address()
    (주소만 필요한 호출부)와 issue_real_estate_register()(이 결과를 이어받아 결제까지 진행)가
    이 함수 하나를 공유한다.

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
        result = _verify_register_target_body(driver, payload, property_category, loc, _fail)
        print(f'[진행] verify_register_target 종료 — ok={result.get("ok")}, message={result.get("message")}', flush=True)
        return result
    except UnexpectedAlertPresentException as e:
        print(f'[오류] "보안프로그램 설치" alert 발생: {e}', flush=True)
        _dismiss_alert_if_present(driver)
        return _fail('"보안프로그램 설치" 알림이 떠서 조회를 중단했습니다.')
    except _StuckOnSecurityPage:
        print('[오류] "보안프로그램 설치" 페이지로 전환됨', flush=True)
        return _fail('"보안프로그램 설치" 페이지로 전환돼 조회를 중단했습니다.')


def _verify_register_target_body(driver, payload, property_category, loc, _fail):
    """verify_register_target()의 실제 로직 — 위 함수가 alert/설치페이지 예외를 잡아 즉시 실패로
    확정할 수 있도록 try 블록으로 감쌀 본체만 분리했다(로직 자체는 기존과 동일)."""
    wait = WebDriverWait(driver, 20)

    print('[진행] 등기소 홈 접속 시도', flush=True)
    if not _navigate_home(driver):
        return _fail('"보안프로그램 설치" 안내 페이지에서 벗어나지 못했습니다(3회 재시도).')
    print(f'[진행] 홈 접속 완료 — url={driver.current_url}', flush=True)
    btn = wait.until(lambda d: _home_entry_button(d))
    print('[진행] "부동산 열람·발급" 버튼 찾음, 클릭', flush=True)
    _js_click(driver, btn)
    time.sleep(2)
    _guard_not_stuck_on_security_page(driver)  # [2026-09-07] 홈 진입 클릭 뒤에도 튕길 수 있다 — 다음 20초 대기 전에 먼저 확인
    print(f'[진행] 부동산 열람·발급 화면 진입 확인 — url={driver.current_url}', flush=True)

    def _find_loc_srch_tab(d):
        _dismiss_alert_if_present(d)
        return d.find_element(By.ID, f'{BASE}_tac_rlrg_appl_tab_tab_loc_srch_tabHTML')
    tab = wait.until(_find_loc_srch_tab)
    print('[진행] 소재지번검색 탭 찾음, 클릭', flush=True)
    _js_click(driver, tab)
    time.sleep(1.5)
    _guard_not_stuck_on_security_page(driver)
    print('[진행] 소재지번검색 탭 진입 확인', flush=True)

    picked = False
    seen_labels = []
    _dismiss_alert_if_present(driver)
    for r in driver.find_elements(By.CSS_SELECTOR, f'#{BASE} input[type="radio"]'):
        rid = r.get_attribute('id') or ''
        if 'rad_loc_kind_cls' not in rid:
            continue
        try:
            label = driver.find_element(By.CSS_SELECTOR, f'label[for="{rid}"]')
        except NoSuchElementException:
            continue
        label_text = label.text.strip()
        seen_labels.append(label_text)
        # [2026-09-08 변경 — 실측으로 확인] 이 라디오 항목이 항상 "토지"/"건물"/"집합건물" 3개로
        # 나오는 게 아니라, 어떤 때는 "토지+건물"(둘을 합친 하나) / "집합건물" 2개로만 나온다(실측
        # 화면캡처로 확인, 2026-09-08) — "외부사이트 화면 다양성" 원칙대로 라벨이 고정돼있다고
        # 가정하지 않고, 대상이 토지/건물이면 "토지+건물"도 같이 인정한다.
        is_match = (
            label_text == property_category
            or (property_category in ('토지', '건물') and label_text == '토지+건물')
        )
        if is_match:
            _js_click(driver, label)
            picked = True
            break
    if not picked:
        return _fail(f'부동산구분 "{property_category}" 항목을 찾지 못했습니다 — 실제 화면에 있던 항목: {seen_labels}')
    print(f'[진행] 부동산구분 "{property_category}" 선택 완료 (화면 항목: {seen_labels})', flush=True)
    time.sleep(1.2)

    sido_id = f'{BASE}_sel_loc_admin_regn1'
    _dismiss_alert_if_present(driver)
    sido_el = driver.find_element(By.ID, sido_id)
    sido_value = None
    for opt in sido_el.find_elements(By.TAG_NAME, 'option'):
        if opt.text.strip() == loc.get('sido', ''):
            sido_value = opt.get_attribute('value')
            break
    if sido_value is None:
        return _fail(f'시/도 "{loc.get("sido", "")}" 옵션을 찾지 못했습니다.')
    # [2026-09-08 재변경 — 실측으로 원인 확인] Select()로 바꿨다가(select_by_value도, 옵션 직접
    # 클릭도) 실제 화면에서 "선택해주세요"로 그대로 남고 "시/도를 선택하시기 바랍니다" 팝업까지
    # 뜨는 게 실측으로 확인됨 — 즉 네이티브 <select> 조작처럼 보여도 실제로는 WebSquare가 자기
    # 내부 상태로 다시 감싸고 있어서, 그 프레임워크의 setValue() API를 거쳐야 실제로 반영된다.
    # (텍스트 입력칸의 진짜 타이핑 원칙과는 별개다 — 이건 키보드 입력이 아니라 드롭다운 "선택"이라
    # 키보드보안 프로그램이 검사할 대상 자체가 아니다.)
    comp_id = re.sub(r'___input$', '', sido_id)
    ok = driver.execute_script(
        """
        var comp = window.$p && window.$p.getComponentById(arguments[0]);
        if (comp && typeof comp.setValue === 'function') { comp.setValue(arguments[1]); return true; }
        return false;
        """,
        comp_id, sido_value,
    )
    print(f'[진행] 시/도 "{loc.get("sido", "")}" 선택 완료 (setValue 성공={ok})', flush=True)
    time.sleep(0.6)

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
    time.sleep(0.6)
    print(f'[진행] 동/리·지번 입력 완료 — {loc["dong_or_li"]} {loc["jibun"]}', flush=True)

    if property_category == '집합건물' and (loc.get('building_dong_no') or loc.get('room_no')):
        mode_index = 0 if (loc.get('building_dong_no') and loc.get('room_no')) else (1 if loc.get('building_dong_no') else 2)
        # [2026-09-07 추가 — 본섭 데이터(999071)로 재현] 이 지점 직전에 "보안프로그램 설치" alert가
        # 뜨어있으면 바로 다음 줄의 find_element()가 UnexpectedAlertPresentException으로 죽는다 —
        # 클릭 뒤(_js_click 안)만이 아니라 클릭 **전** DOM 조회 시점에도 alert가 열려있을 수 있다.
        _dismiss_alert_if_present(driver)
        try:
            _js_click(driver, driver.find_element(By.CSS_SELECTOR, f'label[for="{BASE}_rad_loc_dong_room_sel_input_{mode_index}"]'))
            time.sleep(1)
        except NoSuchElementException:
            pass
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
    _js_click(driver, search_btn)
    time.sleep(5)

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
            try:
                addr_td = tr.find_element(By.CSS_SELECTOR, 'td[data-col_id="real_addr_prt"]')
            except NoSuchElementException:
                continue
            if loc['sigungu'] in addr_td.text:
                narrowed.append(tr)
        if 0 < len(narrowed) < len(matched):
            matched = narrowed

    if len(matched) == 0:
        return _fail('검색결과에서 일치하는 부동산을 찾지 못했습니다.')
    if len(matched) > 1:
        return _fail(f'검색결과가 {len(matched)}건이라 자동으로 고르지 않았습니다 — 매물의 저장된 동/호 정보가 부족할 수 있습니다.')

    row = matched[0]
    # [2026-09-07 추가 — 사용자 요청] 소유자 대조 — 등기소는 소유자를 "지**"처럼 가려서 보여준다
    # (content_iros.js에서 라이브로 확인된 사실, 2026-08-23). 완전일치 검사는 애초에 불가능하므로,
    # 담당자가 눈으로 대조할 수 있게 값만 그대로 돌려준다(자동 판정/중단에는 쓰지 않는다).
    try:
        owner_masked = row.find_element(By.CSS_SELECTOR, 'td[data-col_id="nomprs_name"]').text.strip()
    except NoSuchElementException:
        owner_masked = ''
    print(f'[진행] 대상 부동산 1건 특정 — 소유자(마스킹)={owner_masked}', flush=True)

    _js_click(driver, row.find_element(By.CSS_SELECTOR, 'td[data-col_id="rad_sel"]'))
    time.sleep(0.6)

    nb = _next_button(driver)
    if not nb:
        return _fail('[다음] 버튼을 찾지 못했습니다(부동산 선택 후).', owner_masked)
    _js_click(driver, nb)
    time.sleep(1.5)
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
                    _js_click(driver, nb2)
            time.sleep(1)
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
            time.sleep(2.5)
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
        _js_click(driver, nb3)
        time.sleep(2.5)

    if reached != 'payment':
        return _fail(f'결제대상 확인 화면에 도달하지 못했습니다(마지막으로 본 화면 제목={last_titles}).', owner_masked)
    print('[진행] 결제대상 확인 화면 도달', flush=True)
    time.sleep(1)

    pay_tbody = driver.find_element(By.ID, f'{BASE}_grd_bpay_obj_list_body_tbody')
    pay_rows = [tr for tr in pay_tbody.find_elements(By.TAG_NAME, 'tr')
                if 'display: none' not in (tr.get_attribute('style') or '')]

    dong_jibun = _squash(loc['dong_or_li']) + _squash(loc['jibun'])
    for tr in pay_rows:
        try:
            addr_td = tr.find_element(By.CSS_SELECTOR, 'td[data-col_id="real_addr_prt"]')
        except NoSuchElementException:
            continue
        addr_text = addr_td.text.strip()
        if loc.get('sigungu') and _squash(loc['sigungu']) not in _squash(addr_text):
            continue
        if dong_jibun not in _squash(addr_text):
            continue
        try:
            checkbox = tr.find_element(By.CSS_SELECTOR, 'td[data-col_id="chk_sel"] input[type="checkbox"]')
            if not checkbox.is_selected():
                _js_click(driver, tr.find_element(By.CSS_SELECTOR, 'td[data-col_id="chk_sel"] label'))
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


def find_register_address(payload):
    """[기존 시그니처·동작 그대로 유지] 결제 없이 등기상 주소·고유번호만 조회한다.
    local_helper/main.py의 --iros-address-lookup 호출부가 이 함수를 그대로 부르므로 시그니처를
    바꾸지 않는다. 항상 헤드리스로 돈다(사람 눈에 보이면 안 되는 "몰래" 조회 용도 — iros_address_lookup.py
    시절부터의 설계, 2026-09-06/07 확정 사유는 이 파일 상단 주석 참고).

    @return {'ok': bool, 'address': str, 'unique_no': str, 'owner_masked': str, 'message': str}
    """
    options = Options()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--headless=new')
    driver = _launch_chrome(options)
    try:
        driver.set_window_size(1280, 1000)
        result = verify_register_target(driver, payload)
        return {'ok': result['ok'], 'address': result['address'], 'unique_no': result['unique_no'],
                'owner_masked': result.get('owner_masked', ''), 'message': result['message']}
    except Exception as e:
        # [2026-09-07 추가 — 라이브 재현] TimeoutException 등 일부 셀레니움 예외는 str(e)가 빈
        # 문자열이라(예: "Message: \n") 무슨 예외인지조차 알 수 없었다 — 클래스명을 함께 남긴다.
        return {'ok': False, 'address': '', 'unique_no': '', 'owner_masked': '',
                'message': f'자동화 중 오류({type(e).__name__}): {e} | {_diag_snapshot(driver)}'}
    finally:
        driver.quit()


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
    _js_click(driver, move_btn)
    time.sleep(3)
    return True


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

    driver.execute_script("arguments[0].value = arguments[1];", id_input, iros_id)
    try:
        pw_input = driver.find_element(By.CSS_SELECTOR, 'input[id$="popup_mbr_pw_g"]')
        driver.execute_script("arguments[0].value = arguments[1];", pw_input, iros_pw)
    except NoSuchElementException:
        pass
    try:
        login_btn = driver.find_element(By.CSS_SELECTOR, 'input[id$="btn_popup_login_g"]')
    except NoSuchElementException:
        return {'shown': True, 'ok': False, 'message': '로그인 버튼을 찾지 못했습니다.'}
    _js_click(driver, login_btn)
    time.sleep(5)
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
            _js_click(driver, tab)
            time.sleep(1.2)
    except NoSuchElementException:
        return {'ready': False, 'message': '결제수단(선불전자지급수단) 탭을 찾지 못했습니다.'}

    try:
        agree_label = driver.find_element(By.CSS_SELECTOR, f'#{BASE}_chk_whl_agree li label')
        agree_input = driver.find_element(By.CSS_SELECTOR, f'#{BASE}_chk_whl_agree input[type="checkbox"]')
        if not agree_input.is_selected():
            _js_click(driver, agree_label)
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
    _js_click(driver, confirm_btn)
    time.sleep(3.5)

    try:
        result_btn = driver.find_element(By.CSS_SELECTOR, 'input[id$="_btn_cfrm"]')
        if result_btn.is_displayed():
            _js_click(driver, result_btn)
            time.sleep(3)
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
    _js_click(driver, view_btn)
    time.sleep(6)

    try:
        save_btn = driver.find_element(By.CSS_SELECTOR, 'input[id$="_btn_download"]')
    except NoSuchElementException:
        return {'ok': False, 'message': f'저장 버튼을 찾지 못했습니다 — 열람까지는 진행됐습니다(결제취소 불가 상태). | {_diag_snapshot(driver)}'}
    _js_click(driver, save_btn)

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
            # 이 옵션으로 숨김모드에서도 결제 없이 조회만 하는 선택지를 남긴다(find_register_address()가
            # 하던 일과 같은 지점에서 멈추되, 화면 표시 여부·창 닫기 여부는 이 함수의 다른 옵션을 그대로 따른다).
        'stop_before_view': bool = False,  # [2026-09-08 추가 — 사용자 요청, 실결제 검증용 안전장치]
            # 결제(700원)는 실제로 진행하되, [열람] 버튼은 누르지 않고 멈춘다 — 등기소는 열람 전까지는
            # 결제취소가 가능하므로, 결제 자체가 정상적으로 되는지만 안전하게 확인하고 싶을 때 쓴다.
    }
    headless=True면 auto_confirm/close_when_done은 항상 True로 강제한다(호출부 문서 참고). lookup_only는
    이 강제와 무관하게 항상 우선한다 — 결제 자체를 안 하므로 "결제를 자동으로 할지"는 애초에 의미가 없다.

    @return {'ok': bool, 'file_path': str(로컬 임시경로, NAS 저장은 호출부 책임 — lookup_only면 항상 빈 값),
             'address': str, 'unique_no': str, 'owner_masked': str, 'message': str}
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
    # 지켜진다.
    chrome_options.add_experimental_option('prefs', {
        'download.default_directory': download_dir,
        'download.prompt_for_download': False,
        'download.directory_upgrade': True,
        'plugins.always_open_pdf_externally': True,  # PDF 뷰어로 열지 않고 그대로 다운로드
    })
    driver = _launch_chrome(chrome_options)
    result = {'ok': False, 'file_path': '', 'address': '', 'unique_no': '', 'owner_masked': '', 'message': ''}
    try:
        print(f'[진행] issue_real_estate_register 시작 — headless={headless}, lookup_only={lookup_only}, auto_confirm={auto_confirm}, stop_before_view={stop_before_view}', flush=True)
        driver.set_window_size(1280, 1000)
        if headless:
            driver.set_window_position(-32000, -32000)  # 화면 밖으로 이동 — 진짜 창이지만 안 보이게

        target = verify_register_target(driver, payload)
        result['address'] = target.get('address', '')
        result['unique_no'] = target.get('unique_no', '')
        result['owner_masked'] = target.get('owner_masked', '')
        if not target.get('ok'):
            result['message'] = target.get('message', '')
            return result
        if lookup_only:
            # 여기서 반드시 멈춘다 — [결제] 버튼은 절대 누르지 않는다(find_register_address()와 동일 원칙).
            print('[진행] lookup_only — 조회만 하고 종료', flush=True)
            result['ok'] = True
            return result

        # [결제대상 확인] 화면의 [결제] — 아직 청구되지 않는다(로그인 팝업/결제 준비 화면으로 이어질
        # 뿐인 버튼, content_iros.js::proceedToPaymentScreen() 주석 참고).
        print('[진행] [결제] 버튼(첫 번째) 클릭 — 아직 청구되지 않음', flush=True)
        pay_btn = driver.find_element(By.ID, f'{BASE}_btn_bpay')
        _js_click(driver, pay_btn)
        time.sleep(4)

        routed = _route_after_payment_click(driver, credentials)
        print(f'[진행] 결제 클릭 후 라우팅 결과 = {routed}', flush=True)
        if routed == 'duplicate-handled':
            if stop_before_view:
                result['ok'] = True
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
                _js_click(driver, pay_btn2)
        else:
            # [2026-09-07 신규 — 사용자 요청] "신청확인 자동 진행"이 꺼져 있으면(창이 실제로 보이는
            # 상태다 — headless일 땐 위에서 이미 auto_confirm을 강제로 켰다) 결제 버튼을 직접 누르지
            # 않는다. 화면이 진짜로 사람 눈앞에 떠 있으므로, 담당자가 자기 마우스로 직접 눌러도 된다
            # — 그동안 이 스크립트는 결제요청 확인 팝업이 뜨는지만 기다린다(content_iros.js가
            # auto_pay_registry_fee===false일 때 버튼만 남겨두고 사람 클릭을 기다리는 것과 같은 방식).
            print(f'[진행] 사람이 직접 [결제] 누르길 최대 {HUMAN_CONFIRM_TIMEOUT_SEC}초 대기 중...', flush=True)
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
            result['message'] = '(stop_before_view) 결제까지 완료, 열람 전에 멈췄습니다.'
            _alert_stop_before_view(driver, '결제까지 완료')
            return result

        print('[진행] 열람·다운로드 시작', flush=True)
        save_result = _view_and_save(driver, payload, download_dir)
        print(f'[진행] 열람·다운로드 결과 — ok={save_result.get("ok")}, file_path={save_result.get("file_path")}', flush=True)
        result.update({'ok': save_result.get('ok', False), 'file_path': save_result.get('file_path', ''),
                        'message': save_result.get('message', '')})
        return result

    except Exception as e:
        print(f'[오류] issue_real_estate_register 중 예외 발생: {type(e).__name__}: {e}', flush=True)
        result['message'] = f'자동화 중 오류({type(e).__name__}): {e} | {_diag_snapshot(driver)}'
        return result
    finally:
        if close_when_done:
            driver.quit()
        # close_when_done=False면 창을 열어둔다 — 담당자가 화면을 보고 남은 절차를 직접 마칠 수 있게.
