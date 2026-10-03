# fileName: OBJECT_update/observe_carrot_exposure.py
"""
당근부동산의 노출 규칙(언제 숨겨지는가 / 끌올 쿨타임이 며칠인가)을 알아내기 위한 "관측 전용" 도구.

[왜 만들었나 — 2026-10-03, 사용자 요청]
지금까지의 관측은 새벽 5시 자동업데이트(auto.py)가 "처리 대상 매물을 처리하기 직전에" 한 번 남기는
pr_log(log_item='당근끌올관측')뿐이었다. 그래서 (1) 하루 한 장짜리 스냅샷이라 숨김 시각을 24시간
단위로밖에 못 좁히고, (2) 우리가 숨김해제·끌올을 한 매물만 반복 관측돼 당근이 스스로 한 일과 우리가 한 일이
섞였다(분석 결과 상세는 obangtest 저장소 GLOSSARY.md "당근 노출 규칙" 참고). 이 도구는 하루 여러 번, 당근 목록 전체를
"보기만" 해서 기록한다.

[읽기 전용 — 이 파일이 하는 일의 전부]
- 당근 화면: 필터 칩(판매중/거래완료/미노출) 켜기와 스크롤만 한다. 매물 행의 어떤 버튼도 누르지 않는다.
- DB: pr_log에 INSERT만 한다(pr_externalad/pr_object 등은 SELECT만).

[기록 형식 — 새 테이블 없이 기존 pr_log 사용]
한 번 실행(run)마다 run_id = obs_YYYYMMDD_HHMM 하나를 정하고, 같은 run_id를 log_target으로 쓴다.
- log_item='당근노출관측'      : 청크 여러 줄. {"run","kind":"list"|"db","part","parts","rows":[...]}
    kind=list rows = [당근번호, 상태, 날짜표시(첫 줄), 끌어올리기버튼(0/1), 광고노출회수(없으면 ''), 행 맨앞 칸(관측상
                      담당자), '수정' 앞 숫자 두 칸('a/b', 의미 미확인), 날짜칸 나머지 줄(40자), 행 원문 꼬리(60자)]
    kind=db   rows = [당근번호(ad_code), 새홈번호, object_status, ad_start, ad_end]  (그 시각 우리 DB 모습)
- log_item='당근노출관측요약'  : 마지막에 한 줄. 이 줄이 있으면 청크가 전부 적재된 것이다(분석 시 이 줄이
    없는 run은 중간에 끊긴 것으로 버린다). 로그인 만료/프로필 사용중 등으로 목록을 못 읽은 run도 사유를
    이 줄에 남긴다 — 관측이 비는 시간대가 "안 돌아서"인지 "돌았는데 못 읽어서"인지 구분하기 위함.
청크로 나누는 이유: pr_log.log_value는 TEXT(약 64KB)인데 당근 300여 건의 행 원문까지 담으면 넘칠 수 있고,
넘치면 MySQL 설정에 따라 조용히 잘리거나 에러가 난다.

[운영]
- 나스 컨테이너: `run_scheduled.sh observe`(→ entrypoint.sh의 observe 분기)를 DSM 작업 스케줄러에 3시간마다
  등록한다. 새벽 5시 자동업데이트와 같은 크롬 프로필(daangn_profile)을 쓰므로 겹치면 안 된다 — 아래
  프로필_사용중인지()가 겹침을 감지하면 크롬을 띄우지 않고 '건너뜀'만 기록한다(새벽 작업을 방해하지 않기 위해).
  스케줄도 새벽 4~7시대는 비워둘 것.
- 로컬 점검: `python observe_carrot_exposure.py --dry-run` — DB에 아무것도 쓰지 않고 읽은 내용을 화면에
  요약만 출력한다(스크롤로 목록 전체가 다 읽히는지 처음 확인할 때 사용).

⚠️ [동기화 경고] 크롬 기동 옵션은 auto.py::run_platform_workers()의 것과 같은 이유(나스 컨테이너에서 크롬이
죽는 문제 대응)로 같아야 한다. 로그인 세션 확인/필터 켜기는 verify_carrot_registration.py의 함수를 그대로
쓴다 — 당근 화면 구조가 바뀌어 그쪽이 깨지면 이 도구도 같이 깨진다.

[직접 확인 필요 — 코드만으로는 확정 못 한 가정]
- 목록이 "스크롤하면 더 불러오는" 방식이라는 것(9/06 미노출 309건을 스크롤로 전수 조사한 선례가 근거).
  보이는 행만 렌더하는 가상스크롤일 가능성도 있어, 스크롤 한 칸마다 읽어 번호로 중복을 제거하며
  모으는 방식으로 두 경우 모두 대응한다.
- 필터 칩 숫자 합과 읽은 행 수가 맞는지(칩끼리 겹칠 수 있어 '참고용'으로만 기록하고 판정에는 쓰지 않는다).
"""

import os
import sys
import json
import time
import platform
import datetime
import traceback

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
    sys.stderr.reconfigure(encoding='utf-8', errors='backslashreplace')
except Exception:
    pass

import pymysql
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from util.property_utils import 로그저장
import verify_carrot_registration as 검증기모듈

ROW_SELECTOR = 검증기모듈.ROW_SELECTOR
DAANGN_PROFILE_PATH = 검증기모듈.DAANGN_PROFILE_PATH

# 한 줄(pr_log 한 행)에 담을 JSON 최대 바이트 — TEXT 한계(65,535)보다 충분히 작게 잡는다.
청크_최대_바이트 = 30000
# 스크롤 수집 상한 — 당근 화면이 바뀌어 끝이 없는 목록처럼 동작해도 무한 루프에 빠지지 않게 한다.
스크롤_최대_스텝 = 600
스크롤_최대_초 = 300
# 바닥에 닿은 뒤 새 행이 이 횟수만큼 연속으로 안 늘면 목록 끝으로 본다(느린 추가 로딩 대비).
바닥_연속_무증가_허용 = 3


def 안전문자열(값, 최대길이=None):
    """
    pr_log 컬럼은 charset=utf8(=MySQL utf8mb3)이라 이모지 같은 4바이트 문자가 들어가면 INSERT가
    실패하거나 조용히 잘린다 — 당근 행 원문에 이모지가 섞일 수 있어 BMP 밖 문자를 미리 뺀다.
    """
    문자열 = '' if 값 is None else str(값)
    문자열 = ''.join(c for c in 문자열 if ord(c) <= 0xFFFF)
    return 문자열[:최대길이] if 최대길이 else 문자열


def 프로필_사용중인지():
    """
    다른 크롬(새벽 5시 자동업데이트 등)이 이 프로필을 쓰고 있으면 True. 겹쳐서 띄우면 그 크롬이
    깨지거나 이쪽이 시작 못 하므로, 겹침을 감지하면 크롬을 아예 띄우지 않는다.
    크롬은 프로필 폴더에 잠금 파일을 만든다(리눅스 SingletonLock, 윈도우 lockfile) — 정상 종료하면 사라진다.
    """
    for 잠금파일 in ('SingletonLock', 'lockfile'):
        if os.path.lexists(os.path.join(DAANGN_PROFILE_PATH, 잠금파일)):
            return True
    return False


def 크롬_기동():
    # auto.py::run_platform_workers()의 옵션과 동일하게 유지(동기화 경고 — 파일 상단 참고).
    options = Options()
    options.add_argument(f"--user-data-dir={DAANGN_PROFILE_PATH}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    if platform.system() != 'Windows':
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1600,900")
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-backgrounding-occluded-windows")
    options.add_argument("--disable-renderer-backgrounding")
    options.add_argument("--disable-background-timer-throttling")
    options.add_experimental_option("prefs", {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "autofill.profile_enabled": False,
    })
    driver = webdriver.Chrome(options=options)
    # 이 도구는 "없으면 없는 대로" 읽는 일이 대부분이라 암묵적 대기를 끈다(켜두면 find_elements가
    # 빈 결과일 때마다 최대 대기시간을 통째로 기다린다). 필요한 대기는 직접 sleep/WebDriverWait로 준다.
    driver.implicitly_wait(0)
    if platform.system() == 'Windows':
        driver.maximize_window()
    return driver


def 안내팝업_닫기(driver):
    """
    로그인 직후 뜨는 기능 안내 팝업의 배경이 필터 칩 클릭을 가로막는다(carrot_worker.py의
    로그인확인_및_페이지로드_안정화()에서 실측으로 확인된 문제와 동일) — 있으면 닫는다.
    """
    try:
        버튼들 = driver.find_elements(By.XPATH, "//div[@role='dialog']//button[@aria-label='닫기']")
        if 버튼들:
            driver.execute_script("arguments[0].click();", 버튼들[0])
            time.sleep(0.5)
    except Exception as 오류:
        print(f"[경고] 안내 팝업 닫기 중 오류(무시하고 계속): {오류}")


def 필터칩_문구_수집(driver):
    """ '판매중 24' 같은 필터 칩의 화면 문구 그대로. 칩 숫자와 읽은 행 수를 나중에 대조하기 위한 참고값. """
    return driver.execute_script(
        "return Array.from(document.querySelectorAll('label.seed-control-chip'))"
        ".map(l => (l.innerText || '').replace(/\\s+/g, ' ').trim());"
    )


# 목록 행에서 값을 뽑는 JS — 상태/날짜/버튼 셀렉터는 util/property_utils.py의 당근_매물상태_확인()/
# 당근_날짜및_끌어올리기_가능여부_확인()과 같다(그 함수들이 검증된 방식이라 그대로 맞췄다).
# 당근번호는 행 안의 /articles/<번호> 링크에서 우선 읽고, 없으면 행 원문의 7자리 숫자로 대체한다
# (당근 매물번호가 7자리인 것은 지금까지 관측한 값 전부가 그랬다는 사실에 근거한 가정).
행_읽기_JS = r"""
const rows = Array.from(document.querySelectorAll(arguments[0]));
return rows.map(r => {
  const st = r.querySelector("div[class*='w-[82px]'] span");
  const dc = r.querySelector("div[class*='w-[100px]']");
  const a = r.querySelector("a[href*='/articles/']");
  let num = null;
  if (a) { const m = (a.getAttribute('href') || '').match(/articles\/(\d+)/); if (m) num = m[1]; }
  const text = (r.innerText || '').replace(/\s*\n\s*/g, ' | ').trim();
  if (!num) { const m = text.match(/(?<!\d)(\d{7})(?!\d)/); if (m) num = m[1]; }
  const lines = dc ? (dc.innerText || '').split('\n').map(s => s.trim()).filter(Boolean) : [];
  const bump = dc ? Array.from(dc.querySelectorAll('button')).some(b => (b.textContent || '').trim() === '끌어올리기') : false;
  // [2026-10-03 실제 화면 dry-run으로 확인한 행 구성] "담당자 | 상태 | 날짜 | 끌어올리기 | 번호 | 메모 | 건물명 |
  // 주소 | 면적 | 가격 | 0 | 0 | 수정 | 채팅 | 광고 노출: N회". 이 중 "광고 노출: N회"는 매물별 노출 횟수라
  // 시간에 따라 어디서 멈추는지 보면 노출이 끊긴 시점을 직접 알 수 있어 별도 필드로 뽑는다.
  // '수정' 바로 앞 숫자 두 칸(counts)은 의미를 아직 모른다(조회/관심/채팅 수 중 무엇인지 직접 확인 필요) —
  // 값만 그대로 남겨 나중에 대조할 수 있게 한다.
  const em = text.match(/광고 노출:\s*([\d,]+)\s*회/);
  const cm = text.match(/\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*수정/);
  let tail = text;
  if (num) { const i = text.indexOf(num); if (i >= 0) tail = text.slice(i + num.length).replace(/^\s*\|\s*/, ''); }
  return {num: num, status: st ? (st.textContent || '').trim() : '', date: lines[0] || '',
          dateExtra: lines.slice(1).join(' / '), bump: bump,
          exposure: em ? parseInt(em[1].replace(/,/g, ''), 10) : null,
          owner: (text.split(' | ')[0] || '').slice(0, 20),
          counts: cm ? cm[1] + '/' + cm[2] : '',
          text: tail.slice(0, 120)};
});
"""

스크롤_영역_찾기_JS = r"""
const row = document.querySelector(arguments[0]);
if (!row) return null;
let el = row.parentElement;
while (el && el !== document.body) {
  const oy = getComputedStyle(el).overflowY;
  if ((oy === 'auto' || oy === 'scroll') && el.scrollHeight > el.clientHeight + 10) break;
  el = el.parentElement;
}
window.__obsScrollEl = (el && el !== document.body) ? el : (document.scrollingElement || document.documentElement);
window.__obsScrollEl.scrollTop = 0;
return window.__obsScrollEl.tagName + ' ' + String(window.__obsScrollEl.className || '').slice(0, 80);
"""

스크롤_한칸_JS = r"""
const el = window.__obsScrollEl;
el.scrollTop = el.scrollTop + Math.max(300, el.clientHeight * 0.8);
return {top: el.scrollTop, max: el.scrollHeight - el.clientHeight};
"""


def 목록_전체_수집(driver):
    """
    스크롤을 한 칸씩 내리며 그때그때 보이는 행을 읽어 당근번호로 중복을 제거해 모은다.
    [왜 끝까지 내린 뒤 한 번에 읽지 않나] 목록이 보이는 행만 렌더하는 가상스크롤이면 끝까지 내린 뒤엔
    앞쪽 행이 DOM에서 사라져 있다 — 한 칸마다 읽으면 두 방식 모두 전부 모을 수 있다.
    반환: (행 목록, 메타 dict). 번호를 못 읽은 행은 원문 해시를 키로 써서 일단 보존한다(버리면 누락을
    눈치채지 못한다) — 번호 없는 행 수는 메타에 남겨 읽기 방식이 깨졌는지 알아볼 수 있게 한다.
    """
    시작 = time.time()
    영역 = driver.execute_script(스크롤_영역_찾기_JS, ROW_SELECTOR)
    if 영역 is None:
        raise RuntimeError("목록 행을 하나도 찾지 못했습니다 — 화면 구조가 바뀌었을 수 있습니다.")
    time.sleep(1.0)

    모음 = {}   # 키 -> 행 dict (처음 본 순서 유지)
    스텝 = 0
    바닥_무증가 = 0
    잘림 = False
    while True:
        스텝 += 1
        새로_늘었나 = False
        for 행 in driver.execute_script(행_읽기_JS, ROW_SELECTOR):
            키 = 행['num'] or ('text:' + 행['text'])
            if 키 not in 모음:
                모음[키] = 행
                새로_늘었나 = True
        위치 = driver.execute_script(스크롤_한칸_JS)
        바닥임 = 위치['top'] >= 위치['max'] - 5
        if 바닥임:
            바닥_무증가 = 0 if 새로_늘었나 else 바닥_무증가 + 1
            if 바닥_무증가 >= 바닥_연속_무증가_허용:
                break
            time.sleep(1.5)  # 바닥에서는 추가 로딩이 오기를 넉넉히 기다린다
        else:
            바닥_무증가 = 0
            time.sleep(0.6)
        if 스텝 >= 스크롤_최대_스텝 or time.time() - 시작 > 스크롤_최대_초:
            잘림 = True
            break

    행들 = list(모음.values())
    메타 = {
        '스크롤영역': 영역, '스크롤_스텝': 스텝, '수집_초': round(time.time() - 시작, 1),
        '총행수': len(행들), '번호없는행수': sum(1 for 행 in 행들 if not 행['num']),
        '잘림': 잘림,
        '상태별': {},
    }
    for 행 in 행들:
        메타['상태별'][행['status'] or '(빈값)'] = 메타['상태별'].get(행['status'] or '(빈값)', 0) + 1
    return 행들, 메타


def DB_스냅샷():
    """ 그 시각 우리 DB의 당근 광고 모습 — 숨김이 우리 쪽 상태 변화(거래완료 등)와 겹쳤는지 대조하기 위함. """
    연결 = pymysql.connect(**검증기모듈.DB_CONFIG)
    try:
        커서 = 연결.cursor()
        커서.execute(
            "SELECT e.ad_code, e.object_code_new, o.object_status, e.ad_start, e.ad_end "
            "FROM pr_externalad e LEFT JOIN pr_object o ON o.object_code_new = e.object_code_new "
            "WHERE e.ad_site = '당근' AND e.ad_del = 'N'"
        )
        return [[str(r[0]), str(r[1] or ''), str(r[2] or ''), str(r[3] or ''), str(r[4] or '')] for r in 커서.fetchall()]
    finally:
        연결.close()


def 청크로_나누기(행들, kind, run_id):
    """ 행 목록을 JSON 바이트가 청크_최대_바이트를 넘지 않게 나눠 [{run,kind,part,parts,rows}, ...]로 만든다. """
    덩어리들, 현재, 현재_바이트 = [], [], 0
    for 행 in 행들:
        바이트 = len(json.dumps(행, ensure_ascii=False).encode('utf-8')) + 2
        if 현재 and 현재_바이트 + 바이트 > 청크_최대_바이트:
            덩어리들.append(현재)
            현재, 현재_바이트 = [], 0
        현재.append(행)
        현재_바이트 += 바이트
    if 현재:
        덩어리들.append(현재)
    return [{'run': run_id, 'kind': kind, 'part': i + 1, 'parts': len(덩어리들), 'rows': 덩어리}
            for i, 덩어리 in enumerate(덩어리들)]


def 행을_저장형식으로(행):
    # 번호·상태·날짜·버튼·노출횟수가 분석의 핵심이다. 주소/가격/면적은 우리 DB에서 번호로 찾을 수 있어 매번
    # 반복 저장할 이유가 없다 — 거래완료·차단 행은 원문 꼬리를 아예 빼 저장 용량을 줄인다(관측은 몇 주간
    # 하루 8번 돌아 pr_log에 쌓이는 양이 크다). 원문 꼬리(60자)는 번호를 잘못 읽었는지 확인하는 용도다.
    꼬리 = 안전문자열(행['text'], 60) if 행['status'] in ('판매중', '숨김', '미노출') else ''
    return [행['num'] or '', 안전문자열(행['status']), 안전문자열(행['date']), 1 if 행['bump'] else 0,
            행['exposure'] if 행['exposure'] is not None else '', 안전문자열(행['owner'], 20),
            안전문자열(행['counts'], 12), 안전문자열(행['dateExtra'], 40), 꼬리]


def 로그_적재(run_id, 청크들, 요약, dry_run):
    """ 청크 → 요약 순서로 적재한다(요약이 마지막이어야 "요약이 있으면 전부 적재됨"이 성립). """
    실패 = 0
    if not dry_run:
        for 청크 in 청크들:
            if not 로그저장(run_id, '당근노출관측', json.dumps(청크, ensure_ascii=False), 'SYSTEM'):
                실패 += 1
    요약['적재_청크수'] = len(청크들)
    요약['적재_실패청크수'] = 실패
    if not dry_run:
        로그저장(run_id, '당근노출관측요약', json.dumps(요약, ensure_ascii=False), 'SYSTEM')
    return 실패


def main(dry_run=False):
    시작 = datetime.datetime.now()
    run_id = 시작.strftime('obs_%Y%m%d_%H%M')
    요약 = {'run': run_id, '시작': 시작.isoformat(timespec='seconds'), '결과': '', 'dry_run': dry_run}
    청크들 = []
    종료코드 = 0
    driver = None
    try:
        if 프로필_사용중인지():
            요약['결과'] = '건너뜀_프로필사용중'
            print("[건너뜀] 다른 크롬이 당근 프로필을 쓰고 있어 이번 관측은 건너뜁니다(새벽 자동업데이트와 겹친 것으로 보임).")
        else:
            driver = 크롬_기동()
            검증기모듈.당근_로그인세션_확인(driver)
            time.sleep(2.0)  # 목록이 안착할 시간(carrot_worker.py의 로그인확인_및_페이지로드_안정화와 동일)
            안내팝업_닫기(driver)
            요약['칩_켜기전'] = 필터칩_문구_수집(driver)
            검증기모듈.전체상태_필터_켜기(driver)
            time.sleep(1.5)
            요약['칩_켠후'] = 필터칩_문구_수집(driver)

            행들, 메타 = 목록_전체_수집(driver)
            요약.update(메타)
            청크들 += 청크로_나누기([행을_저장형식으로(행) for 행 in 행들], 'list', run_id)
            db행들 = DB_스냅샷()
            요약['db_당근광고수'] = len(db행들)
            청크들 += 청크로_나누기(db행들, 'db', run_id)
            요약['결과'] = '성공'
    except RuntimeError as 오류:
        # 당근_로그인세션_확인()이 던지는 "세션 만료"는 사람이 그 PC/나스에서 휴대폰 인증을 해야 풀린다.
        요약['결과'] = '로그인세션만료' if '로그인' in str(오류) else '오류'
        요약['사유'] = 안전문자열(오류, 300)
        종료코드 = 1
        print(f"[오류] {오류}")
    except Exception:
        요약['결과'] = '오류'
        요약['사유'] = 안전문자열(traceback.format_exc().strip().splitlines()[-1], 300)
        종료코드 = 1
        print(traceback.format_exc())
    finally:
        if driver is not None:
            try:
                driver.quit()
            except Exception:
                pass

    요약['종료'] = datetime.datetime.now().isoformat(timespec='seconds')
    try:
        실패 = 로그_적재(run_id, 청크들, 요약, dry_run)
        if 실패:
            종료코드 = 1
    except Exception:
        print(traceback.format_exc())
        종료코드 = 1

    print(f"[관측 요약] {json.dumps(요약, ensure_ascii=False)}")
    if dry_run and 청크들:
        # dry-run에서는 저장 대신 앞쪽 몇 행을 보여준다 — 행 읽기 방식이 맞는지 눈으로 확인하는 용도.
        미리보기 = next((c for c in 청크들 if c['kind'] == 'list'), None)
        if 미리보기:
            print("[dry-run] 목록 앞 5행 미리보기:")
            for 행 in 미리보기['rows'][:5]:
                print("   ", json.dumps(행, ensure_ascii=False))
    return 종료코드


if __name__ == "__main__":
    sys.exit(main(dry_run="--dry-run" in sys.argv[1:]))
