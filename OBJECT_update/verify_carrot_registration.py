"""
당근부동산 광고가 "DB는 정상(판매중/중개요청)으로 기록돼 있지만 실제로는 검증을 통과하지 못해
'판매중'이 아닌" 상태일 수 있다는 문제를 확인하기 위한 독립 검증 스크립트다
(verify_naver_registration.py와 같은 목적, 당근판).

⚠️ [동기화 경고] 로그인 확인 방식(검색창 input 존재 여부로 세션 유효성 판단)과 daangn_profile
경로는 workers/carrot_worker.py의 로그인확인_및_페이지로드_안정화()와 auto.py의
run_platform_workers()에 있는 것과 동일하다 — 당근 로그인 화면 구조가 바뀌면 그쪽도 같이
확인해야 한다. 매물번호 검색·결과건수 확인·상태 판독은 util/property_utils.py의
당근매물번호_검색창_입력()/검색결과_목록개수_확인()/당근_매물상태_확인()을 그대로 재사용한다
(carrot_worker.py의 수정방식_업데이트_실행()이 이미 동일한 조합으로 쓰고 있는 검증된 방식).

당근 로그인은 네이버와 달리 아이디/비번이 아니라 휴대폰 인증(문자/QR)이라 자동화가 불가능하다
(carrot_worker.py에도 이미 명시됨). 이 스크립트는 daangn_profile에 저장된 기존 로그인 세션을
그대로 재사용할 뿐이고, 세션이 만료된 경우 사람이 먼저 그 프로필로 크롬을 열어 인증을 완료해야
한다 — 세션 유효기간은 약 15일(사용자 확인, 2026-09-06).

⚠️ [운영 주의] daangn_profile은 실제 자동업데이트 프로그램(auto.py)이 쓰는 것과 동일한 크롬
프로필이다. auto.py가 실행 중일 때 이 스크립트를 같이 실행하면 프로필 잠금 충돌이 날 수 있으니,
auto.py가 돌고 있지 않을 때만 실행할 것.

설계 변경 이력(2026-09-06): 처음에는 "중개소 매물" 목록의 "미노출" 필터 탭을 무한스크롤로 통째로
긁어서 "판매중"과 겹치는 매물을 찾으려 했다(naver 스크립트의 "확인실패 탭 스크래핑" 방식을
그대로 옮긴 것). 그런데 실측 결과 필터 칩들이 OR로 합쳐진다는 것, 그리고 "미노출" 태그 자체가
애초에 원했던 "판매중인데 실제로 검증 미통과"인 케이스를 나타내지 않는다는 것(미노출 목록
309건 전수조사 결과 상태='판매중'인 게 0건이었고, 애초 문제 사례로 봤던 매물도 미노출 목록에
아예 없었음)이 드러났다. 사용자가 다시 명확히 한 진짜 방법은 훨씬 단순했다 — 판매중/거래완료/
미노출 필터를 전부 켜서(검색 결과가 필터에 걸려 안 보이는 일이 없도록) 매물번호로 직접 검색하고,
그 결과 행 하나의 상태값을 읽으면 그게 곧 실제 반영 상태다. 이건 carrot_worker.py가 이미
쓰고 있는 검색 방식과 동일해서, 새로 만들 것 없이 그 유틸 함수들을 그대로 재사용하면 됐다.

불일치 처리 방식(사용자 결정, 2026-09-06): 네이버(ad_del='Y'로 광고 목록에서 제외)와 다르게,
당근은 ad_end(광고종료일)만 확인한 날짜로 갱신하고 ad_del은 그대로 둔다 — 당근은 네이버처럼
등록 정보 자체가 날아가는 게 아니라서, 나중에 "재등록"이 아니라 "수정" 방식으로 다시 살리는
당근 자체 정책과 맞추기 위함.

범위(2026-09-06): naver 스크립트와 동일하게, DB 수정/로그 기록은 --apply를 명시할 때만 실행되고
기본은 dry-run(리포트만)이다. 전체 스캔 기간도 마찬가지로 cafe24 환경설정 카드의 pr_config
(config_group='auto_update', config_key='before_day') 값을 그대로 재사용한다.

사용법:
    python verify_carrot_registration.py                  # 환경설정 카드의 조회기간 내 전체 검증(dry-run, 리포트만)
    python verify_carrot_registration.py --apply           # 위와 동일 + 불일치 발견 시 실제 DB 반영
    python verify_carrot_registration.py 12345678          # 새홈 매물번호(object_code_new) 하나만 검증(dry-run)
    python verify_carrot_registration.py 12345678 --apply  # 위 + 실제 DB 반영

자동업데이트 루프 통합(2026-09-06, 사용자 결정): auto.py의 run_platform_workers()가 당근 업데이트
사이클을 끝낸 직후, 그 사이클에서 방금 처리한 당근매물번호 리스트를 `당근번호로_검증(driver, 리스트,
DB반영=True)`로 그대로 넘겨서 검증한다 — 새 브라우저를 띄우지 않고 이미 로그인된 세션을 이어 쓴다.
사람 승인 없이 자동으로 DB에 반영되며(--apply와 동일), 검증 자체가 실패해도 본 업데이트 작업을
막지 않도록 auto.py 쪽에서 통째로 try/except로 감싸고 디버그 로그를 남긴다(auto.py 주석 참고).
"""

import os
import sys
import time
import datetime
import pymysql

# 🎯 [2026-09-06 실측 발견] util/property_utils.py의 당근 관련 함수들은 실패 시
# print(f"[❌ ...]")처럼 이모지가 섞인 진단 메시지를 그대로 찍는다. 콘솔이 cp949(한국어
# Windows 기본값)면 이 print() 자체가 UnicodeEncodeError로 죽어서, 정작 진짜 원인은
# 가려지고 인코딩 에러만 보이게 된다(run_unattended.bat가 PYTHONUTF8=1로 우회하는 것과
# 동일한 문제, 2026-08-30 재현 이력). 공용 유틸 파일은 건드리지 않고, 이 스크립트의
# 표준출력만 UTF-8로 재설정해서 어떤 콘솔에서 실행하든 안전하게 만든다.
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
    sys.stderr.reconfigure(encoding='utf-8', errors='backslashreplace')
except Exception:
    pass

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from util.property_utils import 당근매물번호_검색창_입력, 검색결과_목록개수_확인, 당근_매물상태_확인

DB_CONFIG = dict(host='obangkr.cafe24.com', user='obangkr', password='Ddhqkd!1', charset='utf8', database='obangkr')

# auto.py의 run_platform_workers()와 동일한 프로필 — 당근 로그인 세션을 그대로 재사용한다.
DAANGN_PROFILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "daangn_profile")

ROW_SELECTOR = "div.flex.w-full.cursor-pointer.items-center.border-b"  # carrot_worker.py와 동일

디버그_스크린샷_경로 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "verify_carrot_debug_최근실패.png")
디버그_페이지소스_경로 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "verify_carrot_debug_최근실패.html")


def 안전출력(text):
    # naver 스크립트와 동일한 이유(콘솔 cp949 코드페이지에서 이모지 등 유니코드 출력 시 크래시)로
    # 방어한다 — 자세한 배경은 verify_naver_registration.py 주석 참고.
    try:
        print(text)
    except UnicodeEncodeError:
        try:
            print(text.encode('cp949', errors='replace').decode('cp949'))
        except UnicodeEncodeError:
            print(text.encode('ascii', errors='replace').decode('ascii'))


def _디버그_덤프(driver, 상황설명):
    try:
        driver.save_screenshot(디버그_스크린샷_경로)
    except Exception:
        pass
    try:
        with open(디버그_페이지소스_경로, "w", encoding="utf-8") as f:
            f.write(f"{상황설명}\ncurrent_url={driver.current_url}\n\n")
            f.write(driver.page_source)
    except Exception:
        pass


def db연결():
    return pymysql.connect(**DB_CONFIG)


def 환경설정_조회기간_가져오기(cursor, 기본값=1):
    """ verify_naver_registration.py와 동일 — cafe24 환경설정 카드의 before_day를 그대로 쓴다. """
    cursor.execute("SELECT config_value FROM pr_config WHERE config_group='auto_update' AND config_key='before_day'")
    row = cursor.fetchone()
    if not row:
        return 기본값
    try:
        return int(row[0])
    except (TypeError, ValueError):
        return 기본값


def 검증대상_조회(cursor, 단일_매물번호=None, 기간_일수=None):
    """
    pr_externalad에서 '정상등록'(ad_del='N')으로 기록된 당근 광고를 가져온다.
    - 단일_매물번호(새홈 object_code_new)를 주면 그 매물 하나만 대상으로 삼는다.
    - 기간_일수를 주면 최근 그 일수 이내에 등록/연장(ad_udate)된 것만 대상으로 삼는다.
    """
    query = "SELECT ad_code, object_code_new FROM pr_externalad WHERE ad_site='당근' AND ad_del='N'"
    params = []
    if 단일_매물번호:
        query += " AND object_code_new = %s"
        params.append(단일_매물번호)
    elif 기간_일수 is not None:
        query += " AND ad_udate >= (CURDATE() - INTERVAL %s DAY)"
        params.append(기간_일수)
    cursor.execute(query, tuple(params))
    return cursor.fetchall()


def 당근_로그인세션_확인(driver):
    """
    daangn_profile에 저장된 기존 로그인 세션이 살아있는지 확인한다. 당근은 휴대폰 인증이라
    자동 재로그인이 불가능하므로(carrot_worker.py와 동일한 제약), 만료돼 있으면 사람이 먼저
    그 프로필로 크롬을 열어 인증을 완료해야 한다는 것을 명확히 알리고 즉시 중단한다.
    """
    driver.get('https://realty.daangn.com/ceo/home')
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "form input[placeholder*='지번']"))
        )
    except Exception:
        _디버그_덤프(driver, "로그인 세션 확인 실패")
        raise RuntimeError(
            "당근 로그인 세션이 만료된 것으로 보입니다. daangn_profile로 크롬을 열어 "
            "휴대폰 인증으로 로그인을 완료한 뒤 다시 실행해 주세요."
        )


def _필터칩_보장(driver, 라벨_시작문자열, 켜짐):
    """
    "판매중"/"거래완료"/"미노출" 같은 필터 칩(<label class="seed-control-chip">) 하나를 찾아,
    원하는 켜짐/꺼짐 상태가 아니면 클릭해서 맞춘다. 라벨 뒤에 건수(예: "판매중 24")가 붙어있어
    시작 문자열로만 찾는다.
    """
    labels = driver.find_elements(By.XPATH, f'//label[contains(@class, "seed-control-chip")][.//span[starts-with(text(), "{라벨_시작문자열}")]]')
    if not labels:
        raise RuntimeError(f"'{라벨_시작문자열}' 필터 칩을 찾지 못했습니다 — 화면 구조가 바뀌었을 수 있습니다.")
    체크박스 = labels[0].find_element(By.CSS_SELECTOR, "input[type='checkbox']")
    현재_선택됨 = 체크박스.is_selected()
    if 현재_선택됨 != 켜짐:
        labels[0].click()
        time.sleep(1.0)


def 전체상태_필터_켜기(driver):
    """
    검색 결과가 필터 때문에 걸러져 안 보이는 일이 없도록, 판매중/거래완료/미노출 필터를
    모두 켠다(사용자 지정 방식, 2026-09-06).
    """
    _필터칩_보장(driver, "판매중", 켜짐=True)
    _필터칩_보장(driver, "거래완료", 켜짐=True)
    _필터칩_보장(driver, "미노출", 켜짐=True)


def 당근매물_실제상태_확인(driver, 당근매물번호):
    """
    carrot_worker.py의 수정방식_업데이트_실행()이 이미 쓰고 있는 것과 동일한 방식으로,
    매물번호를 검색해서 결과 행 하나의 실제 상태값('판매중'/'숨김'/'거래완료'/'미노출')을
    반환한다. 검색 결과가 정확히 1건이 아니면(0건이거나 여러 건) None을 반환한다.
    """
    당근매물번호_검색창_입력(driver, 당근매물번호)
    if 검색결과_목록개수_확인(driver) != 1:
        return None
    행 = driver.find_element(By.CSS_SELECTOR, ROW_SELECTOR)
    return 당근_매물상태_확인(행)


def 불일치_DB반영(cursor, conn, object_code_new, 실제상태):
    """
    사용자 결정(2026-09-06): 네이버(ad_del='Y')와 달리, 당근은 ad_end(광고종료일)만 오늘
    날짜로 갱신하고 ad_del은 그대로 둔다 — 당근은 등록정보가 사라지지 않아서, 나중에
    "재등록"이 아니라 "수정" 방식으로 되살리는 당근 자체 정책과 맞추기 위함.
    """
    now = datetime.datetime.now()
    cursor.execute(
        """UPDATE pr_externalad
           SET ad_end=%s, ad_memo=CONCAT(IFNULL(ad_memo,''), %s), ad_udate=%s, ad_utime=%s
           WHERE ad_site='당근' AND object_code_new=%s""",
        (
            now.date().isoformat(),
            f"[불일치감지 {now.strftime('%Y-%m-%d')}] 당근 실제상태='{실제상태}' → 종료일을 확인일로 갱신. ",
            now.date().isoformat(), now.strftime('%H:%M:%S'), object_code_new,
        )
    )
    # ⚠️ [2026-09-06 실측 발견] pr_log.log_item이 원래 varchar(20)이라, 이 값(27자)이
    # 'carrot_registration_'로 조용히 잘려 저장돼(MySQL이 에러 없이 자름) 이후 조회에서 안
    # 잡히는 문제가 있었다. 사용자가 컬럼을 varchar(50)으로 늘려서 지금은 그대로 들어간다.
    cursor.execute(
        """INSERT INTO pr_log (log_target, log_item, log_value, admin_id, log_wdate, log_wtime)
           VALUES ('system', 'carrot_registration_verify', %s, '', %s, %s)""",
        (
            f"[불일치수정] object_code_new={object_code_new}, 당근 실제상태='{실제상태}' → ad_end를 {now.date().isoformat()}로 갱신",
            now.date().isoformat(), now.strftime('%H:%M:%S'),
        )
    )
    conn.commit()


def 검증_실행(driver, 대상목록, DB반영=True):
    """
    이미 로그인·필터 설정까지 끝난 driver를 받아 대상목록([(ad_code, object_code_new), ...])을
    하나씩 검증한다. driver의 생애주기(열기/닫기)는 호출자 책임이다 — auto.py의 자동업데이트
    루프처럼 당근 워커가 이미 띄워둔 세션을 그대로 이어 쓰는 경우를 위해 분리했다
    (2026-09-06, run_platform_workers() 통합용).

    반환값은 dict — {'총건수', '불일치건수', '확인불가건수', 'DB반영여부'}.
    """
    conn = db연결()
    cursor = conn.cursor()
    불일치_건수 = 0
    확인불가_건수 = 0
    try:
        for ad_code, object_code_new in 대상목록:
            try:
                실제상태 = 당근매물_실제상태_확인(driver, ad_code)
            except Exception as e:
                _디버그_덤프(driver, f"매물 {object_code_new}(당근 {ad_code}) 상태 확인 중 오류: {e}")
                안전출력(f"  [확인 실패] 매물 {object_code_new}(당근 {ad_code}): {e}")
                확인불가_건수 += 1
                continue

            if 실제상태 is None:
                안전출력(f"  [확인 불가] 매물 {object_code_new}(당근 {ad_code}) -> 검색 결과가 1건이 아님")
                확인불가_건수 += 1
            elif 실제상태 != '판매중':
                불일치_건수 += 1
                if DB반영:
                    안전출력(f"  불일치: 매물 {object_code_new}(당근 {ad_code}) -> 실제상태='{실제상태}' (ad_end 갱신함)")
                    불일치_DB반영(cursor, conn, object_code_new, 실제상태)
                else:
                    안전출력(f"  불일치: 매물 {object_code_new}(당근 {ad_code}) -> 실제상태='{실제상태}' (dry-run: DB 미반영)")
            else:
                안전출력(f"  매물 {object_code_new}(당근 {ad_code}) -> 정상(판매중)")
    finally:
        cursor.close()
        conn.close()

    return {
        '총건수': len(대상목록),
        '불일치건수': 불일치_건수,
        '확인불가건수': 확인불가_건수,
        'DB반영여부': DB반영,
    }


def 당근번호로_검증(driver, 당근번호_리스트, DB반영=True):
    """
    auto.py의 자동업데이트 루프 전용 진입점(2026-09-06 통합). 그 사이클에서 방금 처리한
    당근매물번호 리스트를 그대로 받아, 아직 '정상등록'(ad_del='N')으로 남아있는 것만 골라
    검증한다. driver는 이미 로그인된 채로 넘어온다고 가정하지만, 로그인 세션이 그 사이 끊겼을
    가능성에 대비해 로그인 확인과 필터 설정은 이 함수가 직접 다시 보장한다.
    """
    if not 당근번호_리스트:
        return {'총건수': 0, '불일치건수': 0, '확인불가건수': 0, 'DB반영여부': DB반영}

    conn = db연결()
    cursor = conn.cursor()
    try:
        자리표시자 = ','.join(['%s'] * len(당근번호_리스트))
        cursor.execute(
            f"SELECT ad_code, object_code_new FROM pr_externalad "
            f"WHERE ad_site='당근' AND ad_del='N' AND ad_code IN ({자리표시자})",
            tuple(str(ad) for ad in 당근번호_리스트)
        )
        대상목록 = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    if not 대상목록:
        return {'총건수': 0, '불일치건수': 0, '확인불가건수': 0, 'DB반영여부': DB반영}

    당근_로그인세션_확인(driver)
    전체상태_필터_켜기(driver)
    return 검증_실행(driver, 대상목록, DB반영=DB반영)


def run(단일_매물번호=None, DB반영=False):
    conn = db연결()
    cursor = conn.cursor()

    기간_일수 = None
    if not 단일_매물번호:
        기간_일수 = 환경설정_조회기간_가져오기(cursor)
        안전출력(f"환경설정 카드의 조회 기간을 적용합니다: 최근 {기간_일수}일 이내 등록/연장된 당근 광고")
    if not DB반영:
        안전출력("dry-run 모드: 불일치가 발견돼도 DB는 수정하지 않고 리포트만 출력합니다 (--apply로 실제 반영)")

    대상목록 = 검증대상_조회(cursor, 단일_매물번호, 기간_일수)
    cursor.close()
    conn.close()
    안전출력(f"검증 대상 {len(대상목록)}건 조회됨")

    if not 대상목록:
        안전출력("완료: 검증 대상이 없습니다.")
        return

    options = Options()
    options.add_argument(f"--user-data-dir={DAANGN_PROFILE_PATH}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(options=options)
    try:
        driver.maximize_window()
        당근_로그인세션_확인(driver)
        전체상태_필터_켜기(driver)
        결과 = 검증_실행(driver, 대상목록, DB반영=DB반영)
    finally:
        driver.quit()

    반영표시 = f"{결과['불일치건수']}건 DB 반영" if DB반영 else f"{결과['불일치건수']}건 발견(dry-run, DB 미반영)"
    안전출력(f"완료: 총 {결과['총건수']}건 확인, {반영표시}, 확인불가 {결과['확인불가건수']}건")


if __name__ == "__main__":
    인자 = sys.argv[1:]
    DB반영 = "--apply" in 인자
    인자 = [a for a in 인자 if a != "--apply"]
    대상 = 인자[0] if 인자 else None
    run(단일_매물번호=대상, DB반영=DB반영)
