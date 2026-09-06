"""
네이버 연장등록/등록 직후 "버튼 클릭 성공 = 정상등록"으로 DB(pr_externalad)에 기록해온 매물들이,
실제로는 네이버 심사(검증)를 통과하지 못해 게시되지 않은 상태일 수 있다는 문제를 해결하기 위한
독립 검증 스크립트다.

⚠️ [동기화 경고] 로그인 셀렉터는 naver.py의 로그인 로직과 동일하다 — 네이버가 로그인 화면 구조를
바꾸면 naver.py와 이 파일 둘 다 고쳐야 한다. (관리페이지 목록/탭 스크래핑 선택자는 naver.py에는
없는, 이 파일만의 것이다 — 아래 "설계 변경 이력" 참고.)

아직 자동업데이트(OBJECT_update/auto.py) 루프에는 연결되어 있지 않다 — 먼저 이 스크립트 하나로
독립 실행/테스트해서 신뢰할 수 있는지 확인한 뒤, 다음 단계로 자동업데이트 로직에 붙이기로 사용자와
합의했다(2026-09-06).

설계 변경 이력(2026-09-06): 처음에는 naver.py의 신규등록 흐름처럼 매물번호를 한 건씩 검색해서
상태를 읽으려 했으나, 실제로 관리페이지(ma.serve.co.kr)에 로그인해 테스트해보니 그 검색 상자는
naver.py가 등록 직후 특정 화면 상태에서만 유효했던 것으로 보이고, 이 스크립트가 독립적으로 진입한
경로에서는 검색이 실행되지 않았다(실측 확인, 스크린샷/DOM 덤프로 원인 규명). 대신 관리페이지
"등록 리스트" 화면에 이미 있는 "확인실패" 상태별 탭을 열면 심사 미통과 매물이 그대로 목록으로
뜨는 것을 발견해(실측 확인), 개별 검색 없이 이 탭 하나를 스크래핑하는 방식으로 다시 설계했다.

범위 축소(2026-09-06, 사용자 요청): 아직 실제로 확인실패가 발견된 사례로 DB반영까지 검증해보지
못한 상태라, 지금은 "검증하여 결과를 정상적으로 반환하는지"까지만 확인하고 DB 수정/로그 기록은
--apply 플래그를 명시적으로 줄 때만 실행되게 했다. 기본은 dry-run(콘솔 리포트만)이다.

전체 스캔 시 검증 대상 기간은 cafe24 환경설정 카드가 쓰는 pr_config(config_group='auto_update',
config_key='before_day')의 "데이터 조회 기간" 설정값을 그대로 재사용한다(사용자 결정) — 이 검증
스크립트만을 위한 별도 기간 설정을 새로 만들지 않고, 이미 있는 설정 하나로 통일한다.

사용법:
    python verify_naver_registration.py                  # 환경설정 카드의 조회기간 내 전체 검증(dry-run, 리포트만)
    python verify_naver_registration.py --apply           # 위와 동일 + 불일치 발견 시 실제 DB 반영
    python verify_naver_registration.py 12345678          # 새홈 매물번호(object_code_new) 하나만 검증(dry-run)
    python verify_naver_registration.py 12345678 --apply  # 위 + 실제 DB 반영
"""

import os
import re
import sys
import time
import datetime
import pymysql
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

DB_CONFIG = dict(host='obangkr.cafe24.com', user='obangkr', password='Ddhqkd!1', charset='utf8', database='obangkr')

# naver.py의 로그인 성공 확인 로직과 동일 — 헤더에 이 상호명이 뜨는지로 로그인 여부를 판단한다.
로그인확인용_상호명 = "나상권공인중개사사무소"

# 스크래핑 실패 시 실제 화면/DOM을 남겨서 원인(선택자 변경/로딩지연 등)을 확인하기 위한 경로.
디버그_스크린샷_경로 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "verify_naver_debug_최근실패.png")
디버그_페이지소스_경로 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "verify_naver_debug_최근실패.html")

최대_페이지수 = 50  # 페이지네이션 무한루프 방지용 안전장치 — 실제로 이만큼 나올 일은 없다.


def 안전출력(text):
    # Task Scheduler나 일부 콘솔은 cp949라 이모지 등 유니코드 문자를 출력하면 그대로
    # 죽는다(run_unattended.bat가 PYTHONUTF8=1로 우회한 것과 동일한 문제, 2026-08-30
    # 재현 이력). 콘솔 출력 실패가 검증/DB반영 로직 자체를 중단시키면 안 되므로 방어한다.
    # ascii로 바로 replace하면 한글까지 '?'로 뭉개지므로, 먼저 cp949로 시도해 한글은
    # 살리고 cp949도 못 담는 문자(이모지 등)만 걸러낸다.
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
    """
    cafe24 환경설정 카드("매물 자동업데이트 설정")가 쓰는 pr_config(config_group='auto_update')의
    before_day 값을 그대로 가져온다 — 이 검증 스크립트만을 위한 별도 기간 설정을 새로 만들지 않고
    이미 있는 설정 하나로 통일하기 위함(사용자 결정, 2026-09-06).
    """
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
    pr_externalad에서 '정상등록'(ad_del='N')으로 기록된 네이버 광고를 가져온다.
    - 단일_매물번호(새홈 object_code_new)를 주면 그 매물 하나만 대상으로 삼는다.
    - 기간_일수를 주면 최근 그 일수 이내에 등록/연장(ad_udate)된 것만 대상으로 삼는다
      (전체 스캔 모드에서 환경설정 카드의 조회기간을 적용하기 위함).
    """
    query = "SELECT ad_code, object_code_new, admin_id FROM pr_externalad WHERE ad_site='네이버' AND ad_del='N'"
    params = []
    if 단일_매물번호:
        query += " AND object_code_new = %s"
        params.append(단일_매물번호)
    elif 기간_일수 is not None:
        query += " AND ad_udate >= (CURDATE() - INTERVAL %s DAY)"
        params.append(기간_일수)
    cursor.execute(query, tuple(params))
    return cursor.fetchall()


def 담당자_네이버계정_조회(cursor, admin_id):
    cursor.execute("SELECT naver_id, naver_pw FROM pr_admin WHERE admin_del='N' AND admin_id=%s", (admin_id,))
    row = cursor.fetchone()
    if not row:
        raise ValueError(f"담당자({admin_id})의 pr_admin 레코드를 찾을 수 없습니다.")
    return row[0], row[1]


def 네이버_로그인(driver, naver_id, naver_pw):
    driver.get('https://www.serve.co.kr/member/login')
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="input-1"]'))
    ).send_keys(naver_id)
    driver.find_element(By.XPATH, '//*[@id="input-3"]').send_keys(naver_pw)
    driver.find_element(By.XPATH, '//*[@id="app"]/div/div/div/div/div[2]/div[4]/button').click()
    WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element(
            (By.XPATH, '//*[@id="app"]/div/div/header/div/div[2]/button[1]/span[3]/span[2]'),
            로그인확인용_상호명
        )
    )


def _현재페이지_네이버매물번호_수집(driver):
    """
    현재 화면(스크롤된 상태)에 렌더링된 행에서 네이버 매물번호를 모두 뽑는다.
    각 행의 네이버 매물번호 링크는 href="https://fin.land.naver.com/articles/<번호>" 형태다
    (2026-09-06 실측 확인, class="... t-underline-blue-link naver").
    """
    링크들 = driver.find_elements(By.XPATH, '//a[contains(@class, "t-underline-blue-link") and contains(@class, "naver")]')
    번호목록 = []
    for 링크 in 링크들:
        href = 링크.get_attribute("href") or ""
        m = re.search(r'/articles/(\d+)', href)
        if m:
            번호목록.append(m.group(1))
    return 번호목록


def 확인실패_매물목록_스크래핑(driver):
    """
    관리페이지 "등록 리스트" 화면에서 "확인실패" 탭을 열어, 그 안의 모든 매물의 네이버
    매물번호를 모아 반환한다(페이지네이션 있으면 끝까지 순회). 목록 테이블은 가상스크롤이라
    스크롤을 내려야 행이 실제로 렌더링된다(2026-09-06 실측 확인).
    """
    driver.get('https://ma.serve.co.kr/good/articleRegistList')

    확인실패_탭 = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, '//button[contains(@class, "t-text-tab")][.//span[contains(text(), "확인실패")]]')
        )
    )
    확인실패_탭.click()
    time.sleep(1.5)

    전체_매물번호 = []
    for _ in range(최대_페이지수):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.5)
        전체_매물번호.extend(_현재페이지_네이버매물번호_수집(driver))

        다음페이지_버튼들 = driver.find_elements(
            By.XPATH, '//li[@data-test="v-pagination-next"]/button'
        )
        if not 다음페이지_버튼들 or 다음페이지_버튼들[0].get_attribute("disabled") is not None:
            break
        다음페이지_버튼들[0].click()
        time.sleep(1.5)

    return set(전체_매물번호)


def 불일치_DB반영(cursor, conn, object_code_new, 사유):
    """
    사용자 결정(2026-09-06): DB만 자동으로 고치고(ad_del='Y' — 광고 목록에서 제외) 기록을 남긴다.
    실제 재등록 시도는 하지 않는다 — 재등록은 사람이 판단해서 처리한다.
    """
    now = datetime.datetime.now()
    cursor.execute(
        """UPDATE pr_externalad
           SET ad_del='Y', ad_memo=CONCAT(IFNULL(ad_memo,''), %s), ad_udate=%s, ad_utime=%s
           WHERE ad_site='네이버' AND object_code_new=%s""",
        (
            f"[불일치감지 {now.strftime('%Y-%m-%d')}] {사유} → 심사 미통과로 자동 제외. ",
            now.date().isoformat(), now.strftime('%H:%M:%S'), object_code_new,
        )
    )
    # ⚠️ [2026-09-06 실측 발견 — verify_carrot_registration.py 테스트 중 재현] pr_log.log_item이
    # 원래 varchar(20)이라 이 값(26자)이 조용히 잘려 저장되는(MySQL이 에러 없이 자름) 문제가
    # 있었다. 사용자가 컬럼을 varchar(50)으로 늘려서 지금은 그대로 들어간다.
    cursor.execute(
        """INSERT INTO pr_log (log_target, log_item, log_value, admin_id, log_wdate, log_wtime)
           VALUES ('system', 'naver_registration_verify', %s, '', %s, %s)""",
        (
            f"[불일치수정] object_code_new={object_code_new}, {사유} → ad_del='Y' 처리",
            now.date().isoformat(), now.strftime('%H:%M:%S'),
        )
    )
    conn.commit()


def run(단일_매물번호=None, DB반영=False):
    conn = db연결()
    cursor = conn.cursor()

    기간_일수 = None
    if not 단일_매물번호:
        기간_일수 = 환경설정_조회기간_가져오기(cursor)
        안전출력(f"환경설정 카드의 조회 기간을 적용합니다: 최근 {기간_일수}일 이내 등록/연장된 네이버 광고")
    if not DB반영:
        안전출력("dry-run 모드: 불일치가 발견돼도 DB는 수정하지 않고 리포트만 출력합니다 (--apply로 실제 반영)")

    대상목록 = 검증대상_조회(cursor, 단일_매물번호, 기간_일수)
    안전출력(f"검증 대상 {len(대상목록)}건 조회됨")

    담당자별_그룹 = {}
    for ad_code, object_code_new, admin_id in 대상목록:
        담당자별_그룹.setdefault(admin_id, []).append((ad_code, object_code_new))

    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")

    불일치_건수 = 0
    for admin_id, 매물들 in 담당자별_그룹.items():
        naver_id, naver_pw = 담당자_네이버계정_조회(cursor, admin_id)
        driver = webdriver.Chrome(options=options)
        try:
            driver.maximize_window()
            네이버_로그인(driver, naver_id, naver_pw)

            try:
                확인실패_번호목록 = 확인실패_매물목록_스크래핑(driver)
            except Exception as e:
                _디버그_덤프(driver, f"확인실패 탭 스크래핑 실패: {e}")
                안전출력(f"  [담당자 {admin_id}] 확인실패 탭 스크래핑 실패: {e}")
                continue

            안전출력(f"  [담당자 {admin_id}] 확인실패 탭에서 {len(확인실패_번호목록)}건 확인됨")

            for ad_code, object_code_new in 매물들:
                if ad_code in 확인실패_번호목록:
                    불일치_건수 += 1
                    if DB반영:
                        안전출력(f"  불일치: 매물 {object_code_new}(네이버 {ad_code}) -> DB는 정상등록이나 실제는 확인실패 (DB 반영함)")
                        불일치_DB반영(cursor, conn, object_code_new, f"네이버 확인실패 탭에서 발견(ad_code={ad_code})")
                    else:
                        안전출력(f"  불일치: 매물 {object_code_new}(네이버 {ad_code}) -> DB는 정상등록이나 실제는 확인실패 (dry-run: DB 미반영)")
                else:
                    안전출력(f"  매물 {object_code_new}(네이버 {ad_code}) -> 확인실패 목록에 없음(정상)")
        finally:
            driver.quit()

    cursor.close()
    conn.close()
    반영표시 = f"{불일치_건수}건 DB 반영" if DB반영 else f"{불일치_건수}건 발견(dry-run, DB 미반영)"
    안전출력(f"완료: 총 {len(대상목록)}건 확인, {반영표시}")


if __name__ == "__main__":
    인자 = sys.argv[1:]
    DB반영 = "--apply" in 인자
    인자 = [a for a in 인자 if a != "--apply"]
    대상 = 인자[0] if 인자 else None
    run(단일_매물번호=대상, DB반영=DB반영)
