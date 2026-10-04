import re
import json
import time
import datetime
import urllib.request
import urllib.parse
import pymysql
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException, NoAlertPresentException

# [동기화 주의] 같은 구조(공용계정 API 조회 → 로그인 → 사이트 상태 읽기 → 처리 → DB 반영)를 따르는
# 짝꿍 워커는 obang_worker.py(오방)다. 공통 흐름(모드 해석, 요약 카운트 형식)을 고칠 땐 그쪽과
# auto.py의 run_platform_workers()를 함께 확인할 것. 오부사 = 새홈 = osan-bns.com(같은 사이트의 다른 이름).

# core/config.php의 $CFG['local_helper']['service_token'], obang_worker.py의 OBANG_SERVICE_TOKEN과
# 반드시 같은 값이어야 한다(하나를 바꾸면 전부 같이 바꿀 것).
OBS_SERVICE_TOKEN = '51b5f2f355a2e3958e6d5e9a744ab00b53cd181c3a9864ac'
OBS_API_BASE = 'https://obangkr.cafe24.com'
OBS_LOGIN_URL = 'https://osan-bns.com/admin/login'
OBS_LIST_URL = 'https://osan-bns.com/admin_item/item/1/1'


def _오부사_공용계정_조회():
    """
    오부사 로그인 정보를 이 파일에 박아두지 않고 서버(core/config.php의 'obs' 공용 계정)에서 매 실행 시
    API로 받아온다 — 오방(obang_worker.py::_오방_공용계정_조회)과 같은 방식. 오방 쪽 API 이름이 "Obang"으로
    고정돼 있어 오부사를 거기 끼우지 않고, 사이트 이름이 일반화된 getofficeservicecredentials를 새로 뒀다
    (api/lib/lib_api.php::apiGetOfficeServiceCredentials 주석 참고).
    """
    body = urllib.parse.urlencode({
        'fn': 'getofficeservicecredentials',
        'service_token': OBS_SERVICE_TOKEN,
        'site_key': 'obs',
    }).encode('utf-8')
    req = urllib.request.Request(f'{OBS_API_BASE}/api/get_api_lib.php', data=body, method='POST')
    with urllib.request.urlopen(req, timeout=15) as resp:
        res = json.loads(resp.read().decode('utf-8'))
    if not res.get('ok'):
        raise RuntimeError(f'오부사 공용계정 조회 실패: {res}')
    return res['data']['id'], res['data']['pw']


# 오부사 목록 전체를 사이트 자신의 페이지 이동 요청(/admin_item/get_list/N, 화면의 페이지 번호가 쓰는 것과
# 같은 요청)으로 읽는다. 행 하나마다 검색 화면을 다시 띄우는 것보다 훨씬 빠르고(559건 기준 1분 안팎),
# 갱신 후에도 같은 방식으로 다시 읽어 실제로 반영됐는지 검증할 수 있다.
_목록_전체읽기_JS = """
const done = arguments[arguments.length - 1];
(async () => {
  const byId = {};
  for (let p = 1; p <= 300; p++) {
    const r = await fetch('/admin_item/get_list/' + p, {credentials: 'same-origin'});
    const j = await r.json();
    const t = document.createElement('template');
    t.innerHTML = '<table><tbody>' + (j.html || '') + '</tbody></table>';
    const trs = t.content.querySelectorAll('tr[data-id]');
    if (!trs.length) break;
    trs.forEach(tr => {
      const pub = tr.querySelector('.is_public');
      // catx-c-* 같은 열 이름 클래스는 사이트 스크립트가 화면에서 나중에 붙이는 것이라 이 응답에는 없다
      // (2026-10-03 실측: '.catx-c-date .reg_date_box'는 빈 값) — 응답 원본에도 있는 클래스를 쓴다.
      const dt = tr.querySelector('.date_view_box .reg_date_box');
      const ad = tr.querySelector('.item_address');
      const dl = tr.querySelector('.deal_status_box .deal');
      const pr = tr.querySelector('.price_type_box');
      byId[tr.dataset.id] = {
        id: tr.dataset.id,
        deal: ((dl || {}).textContent || '').replace(/\\s+/g, ' ').trim(),
        price: ((pr || {}).textContent || '').replace(/\\s+/g, ' ').trim(),
        pub: !!(pub && pub.checked),
        date: ((dt || {}).innerText || '').replace(/\\s+/g, ' ').trim(),
        addr: ((ad || {}).textContent || '').replace(/\\s+/g, ' ').trim(),
      };
    });
  }
  done(Object.values(byId));
})().catch(e => done({error: String(e)}));
"""

# 화면의 [갱신] 버튼(regup_item)과 [공개] 체크박스(public_flag)가 보내는 요청을 그대로 보낸다 —
# jQuery 요청과 같게 X-Requested-With를 붙인다. 응답 본문은 사이트가 거의 비워서 주므로(갱신) 성공 여부는
# 이 응답이 아니라 아래 재읽기 검증으로 판정한다.
_요청_전송_JS = """
const [url, body, done] = arguments;
fetch(url, {
  method: 'POST', credentials: 'same-origin',
  headers: {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'X-Requested-With': 'XMLHttpRequest'},
  body: body,
}).then(async r => done({status: r.status, text: (await r.text()).slice(0, 100)}))
  .catch(e => done({status: 0, text: String(e)}));
"""

_지번 = r'산?\d+(?:-\d+)?'
_주소_동지번_패턴 = re.compile(rf'([가-힣0-9]+(?:동|리|가))\s*({_지번}(?:\s*,\s*{_지번})*)')
_갱신일_패턴 = re.compile(r'(갱신|등록)\s*:\s*(\d{2})-(\d{2})-(\d{2})\s+(\d{2}):(\d{2}):(\d{2})')


def 주소에서_동지번_추출(주소):
    """
    '경기도 오산시 궐동 687-2 드라마타워 501호' → ('궐동', {'687-2'}).
    여러 필지를 한 매물로 묶은 주소('오산동 595-1,879-9,879-12 …')는 지번을 전부 담는다 — DB는 묶인 필지를
    다 적고 오부사 목록은 그중 하나만 보여주는 경우가 실제로 있다(2026-10-03 실측). 못 읽으면 None.
    """
    m = _주소_동지번_패턴.search(주소 or '')
    if not m:
        return None
    return m.group(1), {x.strip() for x in m.group(2).split(',')}


# 목록의 가격 문구('보1억월900만(부가세 별도) 관127원', '매13억6,706만', '전1억1,000만')를 만원 단위로 푼다.
# 억/만 단위가 섞여 있어 숫자만 뽑으면 틀린다(실제로 '보1억'을 1로 읽는 오류가 있었다). 여기서 못 읽거나 DB와
# 달라 보이는 매물은 수정 폼의 원값(만원 단위)으로 한 번 더 비교하므로, 이 해석은 "수정 폼을 열 대상"을
# 가려내는 1차 거름망일 뿐이다 — 틀려도 불필요하게 폼을 한 번 더 여는 것으로 끝난다.
_가격_조각_패턴 = re.compile(r'(보|월|전|매)\s*(?:([\d,]+)\s*억)?\s*(?:([\d,]+)\s*만)?')


def 목록_가격문구_해석(가격문구):
    """ '보1억월900만' → {'보': 10000, '월': 900}. 값 없이 라벨만 있는 조각은 건너뛴다. """
    결과 = {}
    for 라벨, 억, 만 in _가격_조각_패턴.findall(가격문구 or ''):
        if not 억 and not 만:
            continue
        결과[라벨] = (int(억.replace(',', '')) * 10000 if 억 else 0) + (int(만.replace(',', '')) if 만 else 0)
    return 결과


def 목록행_갱신일시_해석(날짜문구):
    """ '갱신 : 26-10-03 19:25:54' → ('갱신', datetime). 한 번도 갱신 안 한 매물은 '등록 : ...'이 보인다. """
    m = _갱신일_패턴.search(날짜문구 or '')
    if not m:
        return None, None
    라벨, yy, mo, dd, hh, mi, ss = m.groups()
    return 라벨, datetime.datetime(2000 + int(yy), int(mo), int(dd), int(hh), int(mi), int(ss))


class ObsAutomationWorker:
    """ 오부사(새홈, osan-bns.com) 매물 갱신 및 공개상태 정리를 전담하는 클래스 """

    def __init__(self, driver, mode, progress_callback=None, unattended=False, 강제_새홈번호_목록=None):
        self.driver = driver
        self.mode = mode
        self.progress_callback = progress_callback
        self.unattended = unattended
        # 새홈번호 테스트 모드(auto.py의 test_code)용 — 주어지면 그 번호들만 처리한다.
        self.강제_새홈번호_목록 = set(str(x) for x in 강제_새홈번호_목록) if 강제_새홈번호_목록 else None

        self.complete_count = 0   # 갱신 성공
        self.end_ok = 0           # 거래완료인데 공개 중이던 매물을 비공개로 내림
        self.skip_count = 0
        self.error_count = 0
        self.not_found_count = 0  # DB상 오부사 활성 매물인데 사이트 목록에 없음
        self.price_fix_ok = 0     # 사이트 가격을 DB 값으로 고친 건수 — 갱신/건너뜀 등으로 이미 집계된 매물의 부가 지표(총건수에 안 더함)

    def _알림(self, current, total, text):
        if self.progress_callback:
            self.progress_callback(current, total, text, 'determinate')

    def _DB연결(self):
        return pymysql.connect(host='obangkr.cafe24.com', user='obangkr', password='Ddhqkd!1', database='obangkr', charset='utf8')

    def 로그인(self):
        self.driver.get(OBS_LIST_URL)
        if '/admin/login' not in self.driver.current_url:
            return  # 프로필에 저장된 로그인 세션이 살아있음
        아이디, 비밀번호 = _오부사_공용계정_조회()
        self._로그인칸_입력_검증('//*[@id="email"]', 아이디)
        self._로그인칸_입력_검증('//*[@id="password"]', 비밀번호)
        self.driver.find_element(By.XPATH, '//*[@id="admin_login"]/button').click()
        WebDriverWait(self.driver, 15).until(lambda d: '/admin/login' not in d.current_url)
        self.driver.get(OBS_LIST_URL)
        if '/admin/login' in self.driver.current_url:
            raise RuntimeError('오부사 로그인 실패 — 계정 정보 또는 로그인 화면 변경 확인 필요')

    def _로그인칸_입력_검증(self, xpath, 목표값):
        # 오방 로그인에서 크롬 자동완성이 입력값을 이어붙이는 일이 실제로 있었다(obang_worker.py 참고) —
        # 같은 프로필을 쓰므로 오부사 로그인칸도 입력 직후 실제 값을 확인하고 어긋나면 한 번 다시 넣는다.
        칸 = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
        칸.clear()
        칸.send_keys(목표값)
        if 칸.get_attribute('value') != 목표값:
            칸.send_keys(Keys.CONTROL, 'a', Keys.BACKSPACE)
            칸.send_keys(목표값)

    def 목록_전체읽기(self):
        결과 = self.driver.execute_async_script(_목록_전체읽기_JS)
        if isinstance(결과, dict) and 결과.get('error'):
            raise RuntimeError(f"오부사 목록 읽기 실패: {결과['error']}")
        return {행['id']: 행 for 행 in 결과}

    def DB_오부사후보_조회(self):
        """
        새홈번호가 5자리인 매물만 오부사 번호일 가능성이 있다(lib_external_ad.php::externalAdDecideMode의
        규칙과 같다). 다만 5자리라고 해서 반드시 오부사에 있는 건 아니다(2026-10-03 실측: 오부사 최대번호
        10573 초과인 5자리 번호 234건이 DB에 있음) — 그래서 사이트 목록과 겹치는 것만, 주소까지 대조해서
        처리한다(아래 주소_일치_여부).
        """
        conn = self._DB연결()
        try:
            cur = conn.cursor(pymysql.cursors.DictCursor)
            cur.execute("SELECT object_code_new, object_status, object_del, obs_open_yn, object_address, "
                        "object_ttype, object_tmoney1, object_tmoney2, object_udate "
                        "FROM pr_object WHERE CHAR_LENGTH(object_code_new)=5")
            return {str(r['object_code_new']): r for r in cur.fetchall()}
        finally:
            conn.close()

    @staticmethod
    def 활성매물_여부(db행):
        return db행['object_status'] == '중개요청' and db행['object_del'] == 'N'

    @staticmethod
    def 종결매물_여부(db행):
        return db행['object_status'] == '거래완료' or db행['object_del'] == 'Y'

    @staticmethod
    def 주소_일치_여부(db행, 사이트행):
        # 번호만 같고 다른 매물일 위험(위 DB_오부사후보_조회 주석)을 막는다. 갱신은 되돌릴 수 있지만 비공개
        # 전환은 실제 노출에 영향을 주므로, 동+지번을 어느 한쪽이라도 못 읽으면 "일치"로 보지 않고 건너뛴다.
        # 같은 동이고 지번이 하나라도 겹치면 같은 매물로 본다(여러 필지 묶음 주소 대응).
        db = 주소에서_동지번_추출(db행.get('object_address'))
        site = 주소에서_동지번_추출(사이트행.get('addr'))
        return bool(db and site and db[0] == site[0] and (db[1] & site[1]))

    # DB 거래종류 → (사이트 목록의 거래유형 문구, {수정폼 입력칸 이름: DB 컬럼}, {목록 가격 라벨: DB 컬럼}).
    # 거래유형이 하나인 월세/전세/매매만 맞춘다 — 관리비·권리금·'전월세' 같은 복수 거래유형·단기임대는
    # 입력 구조가 달라 이 단계에서는 다루지 않는다(DB가 그 값을 어떻게 나눠 갖는지 아직 확인 못 함).
    # 네 번째 값은 "자동으로 사이트 가격을 덮어써도 되는가"다. 지금은 셋 다 True지만 값 자체는 남겨둔다 —
    # 새 거래종류를 추가할 때 근거가 확인되기 전까지 False(불일치를 로그에만 남기고 사람이 확인)로 시작할 수 있게.
    # 매매는 2026-10-03 드라이런에서 11건이 1억 단위로 어긋나 처음에 False로 뒀고(DB 수정일이 2025년인 건도 있어
    # DB가 최신이라는 근거가 없었다), 2026-10-04 사용자가 "DB 기준으로 수정"하기로 확정해 True로 바꿨다.
    _가격_동기화_규칙 = {
        '월세': ('월세', {'price_month_deposit': 'object_tmoney1', 'price_month_rent': 'object_tmoney2'}, {'보': 'object_tmoney1', '월': 'object_tmoney2'}, True),
        '전세': ('전세', {'price_full_rent': 'object_tmoney1'}, {'전': 'object_tmoney1'}, True),
        '매매': ('매매', {'price_sell': 'object_tmoney1'}, {'매': 'object_tmoney1'}, True),
    }

    def 가격_판정(self, db행, 사이트행):
        """
        :return: ('대상아님'|'같음'|'확인필요', 사유). '확인필요'는 목록 표기가 DB와 달라 보이거나 못 읽었다는 뜻이라
            수정 폼 원값으로 한 번 더 비교해야 한다 — 목록 표기만 믿고 바로 고치지 않는다.
        """
        규칙 = self._가격_동기화_규칙.get(db행.get('object_ttype'))
        if not 규칙:
            return '대상아님', f"DB 거래종류 '{db행.get('object_ttype')}'은(는) 가격 동기화 대상이 아님"
        사이트_거래유형, _, 목록라벨, _ = 규칙
        if 사이트행.get('deal') != 사이트_거래유형:
            return '대상아님', f"거래유형 불일치(DB:{db행.get('object_ttype')} / 사이트:{사이트행.get('deal')})"
        사이트가격 = 목록_가격문구_해석(사이트행.get('price'))
        for 라벨, 컬럼 in 목록라벨.items():
            if 사이트가격.get(라벨) != int(db행[컬럼] or 0):
                return '확인필요', f"{라벨} DB:{db행[컬럼]} / 목록:{사이트가격.get(라벨)}"
        return '같음', ''

    def 수정폼에서_가격_맞추기(self, 코드, db행):
        """
        오부사 수정 폼을 열어 가격 입력칸의 원값(만원 단위)을 DB와 비교하고, 다르면 DB 값으로 고쳐 저장한다.
        화면의 [매물 저장] 버튼(btn_submit)을 실제로 눌러 폼 자신의 검증과 후처리를 그대로 거친다 — 폼 데이터를
        직접 POST하면 그 처리를 건너뛰어 다른 칸이 어긋날 수 있다. 저장 후 폼을 다시 열어 반영을 확인한다.
        :return: '이미같음' | '수정함' | '수정안함' | '실패' ('수정안함'은 자동 덮어쓰기가 허용되지 않은 거래종류의 불일치)
        """
        _, 입력칸규칙, _, 자동수정 = self._가격_동기화_규칙[db행['object_ttype']]
        목표 = {이름: int(db행[컬럼] or 0) for 이름, 컬럼 in 입력칸규칙.items()}
        try:
            현재 = self._수정폼_가격읽기(코드, list(목표))
            if 현재 == 목표:
                return '이미같음'
            if not 자동수정:
                print(f"   [⚠️ 가격 불일치 - 사람 확인 필요 - 오부사 {코드}] {db행['object_ttype']} 사이트:{현재} / DB:{목표} (DB 수정일 {db행.get('object_udate')}) — 자동 수정하지 않습니다")
                return '수정안함'
            print(f"   [💲 가격 수정 - 오부사 {코드}] 사이트:{현재} → DB:{목표}")
            for 이름, 값 in 목표.items():
                self._입력칸_값_넣기(self.driver.find_element(By.NAME, 이름), 값)
            # 사이트의 저장 검사는 '위치정보 소재지'(#dong_id)가 비어 있으면 "소재지를 입력해주세요"로 막는데, 이 칸은
            # 페이지가 열린 뒤 시/도→구/군→동 선택 목록을 불러오며 나중에 채워진다. 폼이 열리자마자 저장하면 아직
            # 비어 있는 시점에 걸려(2026-10-04 매매 11건이 전부 이 사유로 거부됨) 데이터가 멀쩡한데도 저장이 막힌다.
            # 채워질 때까지 기다린다 — 끝까지 비어 있으면(진짜 미입력) 기다림을 포기하고 사이트의 거부 사유를 그대로 받는다.
            try:
                WebDriverWait(self.driver, 15).until(lambda d: d.execute_script("return !!$('#dong_id').val();"))
            except TimeoutException:
                pass
            저장버튼 = next(b for b in self.driver.find_elements(By.CSS_SELECTOR, '.save_btn') if b.is_displayed())
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", 저장버튼)
            저장버튼.click()
            self._저장후_알림_처리()
            # 저장이 통과하면 목록으로 이동하고, 막히면 같은 화면에 필수항목 안내창이 뜬다. 오부사는 중개대상물
            # 표시·광고법상 필수항목(예: 화장실)이 비어 있는 옛 매물은 가격만 고쳐도 저장을 거부한다 — 임의로
            # 채울 수 없는 값이라 사유를 그대로 로그에 남기고 실패로 둔다(2026-10-03 10039에서 실측).
            결과 = WebDriverWait(self.driver, 20).until(self._저장_결과_판정)
            if 결과 != '이동함':
                print(f"   [❌ 가격 저장 거부 - 사람이 채워야 함 - 오부사 {코드}] {결과}")
                return '실패'
            확인 = self._수정폼_가격읽기(코드, list(목표))
            if 확인 == 목표:
                return '수정함'
            print(f"   [❌ 가격 수정 미반영 - 오부사 {코드}] 저장 후 다시 열어보니 {확인} (목표 {목표})")
            return '실패'
        except Exception as e:
            print(f"   [❌ 가격 수정 실패 - 오부사 {코드}] {type(e).__name__}: {str(e)[:200]}")
            self._알림창_정리()
            return '실패'

    def _수정폼_가격읽기(self, 코드, 입력칸이름들):
        self.driver.get(f'https://osan-bns.com/admin_item/edit/{코드}?page=1')
        WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.NAME, 입력칸이름들[0])))
        값들 = {}
        for 이름 in 입력칸이름들:
            원값 = (self.driver.find_element(By.NAME, 이름).get_attribute('value') or '').replace(',', '').strip()
            값들[이름] = int(원값) if 원값.isdigit() else None
        return 값들

    def _입력칸_값_넣기(self, 칸, 값):
        # 이 칸들은 입력할 때 천단위 쉼표를 붙이는 스크립트가 달려 있다 — 실제 키 입력으로 넣어 그 처리를 거친다.
        if 칸.is_displayed():
            칸.clear()
            칸.send_keys(str(값))
        else:
            self.driver.execute_script(
                "arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input', {bubbles:true})); "
                "arguments[0].dispatchEvent(new Event('change', {bubbles:true}));", 칸, str(값))

    def _저장_결과_판정(self, driver):
        """ 저장 클릭 후 상태: 목록으로 이동했으면 '이동함', 필수항목 안내창이 떴으면 그 문구, 아직이면 False. """
        if '/admin_item/edit/' not in driver.current_url:
            return '이동함'
        안내 = driver.execute_script(
            "var m = document.querySelector('#modal-item_form_checks');"
            "return (m && m.offsetParent !== null) ? m.innerText.replace(/\\s+/g, ' ').trim().slice(0, 200) : '';")
        return 안내 or False

    def _저장후_알림_처리(self):
        try:
            WebDriverWait(self.driver, 2).until(EC.alert_is_present())
            알림 = self.driver.switch_to.alert
            print(f"   [🔎 오부사 저장 알림] {알림.text}")
            알림.accept()
        except (TimeoutException, NoAlertPresentException):
            pass

    def _알림창_정리(self):
        try:
            self.driver.switch_to.alert.accept()
        except Exception:
            pass

    def _요청(self, url, body):
        return self.driver.execute_async_script(_요청_전송_JS, url, body)

    def run(self):
        """ :return: (성공, 비공개, 건너뜀, 실패, 미등록, 가격수정) — 총건수는 앞의 다섯의 합과 같고, 가격수정은 부가 지표다. """
        시작시각 = datetime.datetime.now().replace(microsecond=0)
        오늘 = 시작시각.date()
        갱신함 = self.mode in ('all', 'update_only')
        비공개함 = self.mode in ('all', 'close_only')

        self._알림(0, 100, '🔐 오부사 로그인/목록 읽는 중...')
        self.로그인()
        사이트 = self.목록_전체읽기()
        db = self.DB_오부사후보_조회()

        갱신대기, 비공개대기 = [], []
        def 대상인가(코드):
            return self.강제_새홈번호_목록 is None or 코드 in self.강제_새홈번호_목록

        for 코드, db행 in db.items():
            if not 대상인가(코드):
                continue
            행 = 사이트.get(코드)
            if self.활성매물_여부(db행) and 갱신함:
                if 행 is None:
                    self.not_found_count += 1
                    continue
                if not self.주소_일치_여부(db행, 행):
                    print(f"   [⚠️ 주소 불일치 - 오부사 {코드}] DB:{db행.get('object_address')} / 사이트:{행.get('addr')} — 같은 번호의 다른 매물일 수 있어 건너뜁니다")
                    self.skip_count += 1
                    continue
                # 가격 동기화(DB → 사이트): 갱신 전에 먼저 맞춘다. 가격 맞추기에 실패한 매물은 갱신(= 목록 상단
                # 재노출)하지 않고 실패로 집계한다 — 가격이 틀린 채로 다시 띄우는 것보다 낫고, 한 매물이 두 번
                # 집계되지 않는다(수정 성공은 부가 지표라 총건수에 더하지 않음).
                가격판정, 가격사유 = self.가격_판정(db행, 행)
                if 가격판정 == '확인필요':
                    가격결과 = self.수정폼에서_가격_맞추기(코드, db행)
                    if 가격결과 == '수정함':
                        self.price_fix_ok += 1
                    elif 가격결과 == '실패':
                        self.error_count += 1
                        continue
                elif 가격판정 == '대상아님' and '거래유형 불일치' in 가격사유:
                    print(f"   [⚠️ 가격 동기화 건너뜀 - 오부사 {코드}] {가격사유}")
                라벨, 일시 = 목록행_갱신일시_해석(행['date'])
                if 라벨 == '갱신' and 일시 and 일시.date() == 오늘:
                    self.skip_count += 1
                    continue
                갱신대기.append(코드)
            elif self.종결매물_여부(db행) and 비공개함 and 행 is not None and 행['pub']:
                if not self.주소_일치_여부(db행, 행):
                    print(f"   [⚠️ 주소 불일치 - 오부사 {코드}] DB:{db행.get('object_address')} / 사이트:{행.get('addr')} — 같은 번호의 다른 매물일 수 있어 건너뜁니다")
                    self.skip_count += 1
                    continue
                비공개대기.append(코드)

        총 = len(갱신대기) + len(비공개대기)
        print(f"   [오부사] 사이트 {len(사이트)}건 / DB후보 {len(db)}건 → 갱신 {len(갱신대기)}건, 비공개 {len(비공개대기)}건 처리 예정")
        진행 = 0
        for 코드 in 갱신대기:
            진행 += 1
            self._알림(진행, max(총, 1), f"🔄 오부사 매물갱신 중... ({진행}/{총})")
            res = self._요청('/admin_item/regup_item', 'id=' + urllib.parse.quote(코드))
            if res.get('status') != 200:
                print(f"   [❌ 갱신 요청 실패 - 오부사 {코드}] {res}")
            time.sleep(0.2)
        for 코드 in 비공개대기:
            진행 += 1
            self._알림(진행, max(총, 1), f"🔒 오부사 거래완료 비공개 중... ({진행}/{총})")
            res = self._요청('/admin_item/public_flag', 'flag=false&id=' + urllib.parse.quote(코드))
            if res.get('status') != 200 or (res.get('text') or '').strip() == 'no':
                print(f"   [❌ 비공개 요청 실패 - 오부사 {코드}] {res}")
            time.sleep(0.2)

        # 요청이 200을 줬다고 반영된 것은 아니다 — 처리 후 목록을 다시 읽어 실제 상태로 판정한다.
        사이트 = self.목록_전체읽기() if 총 else 사이트
        for 코드 in 갱신대기:
            라벨, 일시 = 목록행_갱신일시_해석((사이트.get(코드) or {}).get('date'))
            if 라벨 == '갱신' and 일시 and 일시 >= 시작시각:
                self.complete_count += 1
            else:
                self.error_count += 1
                print(f"   [❌ 갱신 미반영 - 오부사 {코드}] 처리 후에도 갱신일시가 바뀌지 않았습니다: {(사이트.get(코드) or {}).get('date')}")
        for 코드 in 비공개대기:
            if 코드 in 사이트 and not 사이트[코드]['pub']:
                self.end_ok += 1
            else:
                self.error_count += 1
                print(f"   [❌ 비공개 미반영 - 오부사 {코드}] 처리 후에도 공개 상태입니다")

        self.공개상태_DB반영(사이트, db)
        return self.complete_count, self.end_ok, self.skip_count, self.error_count, self.not_found_count, self.price_fix_ok

    def 공개상태_DB반영(self, 사이트, db):
        """
        사이트의 실제 공개 여부를 pr_object.obs_open_yn에 기록한다(사이트 → DB 방향). 이 컬럼은 갱신이
        없어 실제와 크게 어긋나 있었다(2026-10-03 실측: 공개 중인 DB 중개요청 146건 중 117건이 'N').
        DB 값을 사이트에 강제하는 반대 방향은 위험해서(그대로 하면 공개 매물 대부분이 내려간다) 하지 않는다 —
        사이트에 내리는 건 위 '거래완료 비공개'뿐이다.
        """
        바꿀것 = []
        for 코드, db행 in db.items():
            행 = 사이트.get(코드)
            if 행 is None or (self.강제_새홈번호_목록 is not None and 코드 not in self.강제_새홈번호_목록):
                continue
            if not self.주소_일치_여부(db행, 행):
                continue
            실제 = 'Y' if 행['pub'] else 'N'
            if db행['obs_open_yn'] != 실제:
                바꿀것.append((실제, 코드))
        if not 바꿀것:
            return
        try:
            conn = self._DB연결()
            try:
                cur = conn.cursor()
                cur.executemany("UPDATE pr_object SET obs_open_yn=%s WHERE object_code_new=%s", 바꿀것)
                conn.commit()
            finally:
                conn.close()
            print(f"   [💾 DB 동기화] 오부사 공개상태(obs_open_yn) {len(바꿀것)}건 갱신")
        except Exception as e:
            print(f"   [❌ obs_open_yn 동기화 실패] {e}")
