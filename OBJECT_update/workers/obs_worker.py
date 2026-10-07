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

    def __init__(self, driver, mode, progress_callback=None, unattended=False, 강제_새홈번호_목록=None, 갱신_기준일수=1):
        self.driver = driver
        self.mode = mode
        # 오방과 같은 기준(auto.py의 before_day)으로 "최근 N일 안에 의뢰확인일이 갱신된 매물"만 갱신한다.
        # 2026-10-06 사용자 결정: 처음엔 활성 매물 전체를 매일 갱신했으나(하루 약 180건) 요청이 있었던
        # 매물만 올리는 오방 방식(B안)으로 바꿨다 — 갱신_대상_여부() 참고.
        self.갱신_기준일수 = 갱신_기준일수
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
        self.auto_fix_ok = 0      # 저장 거부 사유(필수항목)를 자동으로 채우거나 거래유형을 DB에 맞춰 저장한 매물 수 — 이것도 부가 지표
        self._이번_매물_해결문구 = []  # 한 매물을 저장하는 동안 자동으로 해결한 필수항목 문구(보정 건수 집계용)

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
            # request_*/관심여부는 갱신_대상_여부()가 오방과 같은 기준(최근 의뢰확인 또는 관심 매물)으로
            # 갱신 대상을 고르기 위한 값이다. LEFT JOIN이라 의뢰가 없는 매물도 행은 그대로 나온다.
            cur.execute("SELECT o.object_code_new, o.object_status, o.object_del, o.obs_open_yn, o.object_address, "
                        "o.object_ttype, o.object_tmoney1, o.object_tmoney2, o.object_udate, "
                        "p.request_status, p.request_date, p.request_del, "
                        "EXISTS(SELECT 1 FROM pr_request_fix f WHERE f.request_code=o.request_code AND f.fix_del='N') AS 관심여부 "
                        "FROM pr_object o LEFT JOIN pr_request p ON p.request_code=o.request_code "
                        "WHERE CHAR_LENGTH(o.object_code_new)=5")
            return {str(r['object_code_new']): r for r in cur.fetchall()}
        finally:
            conn.close()

    @staticmethod
    def 활성매물_여부(db행):
        return db행['object_status'] == '중개요청' and db행['object_del'] == 'N'

    def 갱신_대상_여부(self, db행, 오늘):
        """
        오방(auto.py::obang_data)의 갱신 대상 기준을 그대로 따른다: 의뢰가 접수/진행 상태이면서
        (의뢰확인일이 최근 N일 안이거나 관심 매물). 오방은 여기에 보증금/월세 입력 여부도 보지만, 오부사는
        전세·매매도 다루므로 그 조건은 따르지 않는다. request_date를 의뢰확인일로 본 것은 구버전 오방
        쿼리(autp_260530.py)의 주석("의뢰확인일 기준 request_date")을 따른 것이다.
        테스트 모드(강제_새홈번호_목록)는 지정한 번호를 무조건 대상으로 삼는다.
        """
        if self.강제_새홈번호_목록 is not None:
            return True
        if db행.get('request_status') not in ('접수', '진행') or db행.get('request_del') == 'Y':
            return False
        if db행.get('관심여부'):
            return True
        기준일 = db행.get('request_date')
        if isinstance(기준일, str):
            # 날짜 칸이 비어있거나 '0000-00-00' 같은 값이 문자열로 오는 행이 있다(실측) — 못 읽으면 대상이 아니다.
            try:
                기준일 = datetime.datetime.strptime(기준일[:10], '%Y-%m-%d').date()
            except ValueError:
                return False
        return bool(기준일 and 오늘 - datetime.timedelta(days=self.갱신_기준일수) <= 기준일 <= 오늘)

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

    # 저장 거부(법정 필수항목 미입력) 문구 → 해결 방법. 2026-10-07 빈 등록 화면에서 물건종류 8가지 × 건물 일부/전체 ×
    # 거래유형 조합 38개를 "저장 → 거부 문구 → 채움"으로 끝까지 돌려 얻은 목록이다(경매용은 오부사 DB에 없는 유형이라
    # 제외). 이 사이트 검사는 첫 위반에서 멈추고 문구와 대상 칸을 알려주므로, 문구를 키로 쓴다.
    #  - '체크': 값이 아니라 표시 선택일 뿐인 칸 → 켠다(데이터 추정 없음).
    #  - 'DB값': DB에서 출처가 확인된 값을 입력한다. DB에 값이 없으면 추측하지 않고 해결 불가로 두어 사람이 채우게 한다
    #    (예: 10039 화장실, 10415 연면적은 DB에도 비어 있음).
    #  - 'DB선택': 드롭다운에서 DB 값과 이름이 같은 항목을 고른다.
    # 여기 없는 문구(입주가능일·관리비·상세주소 공개·고객정보·건물매매용 지상층 등)는 출처/영향이 확인되지 않아
    # 자동으로 채우지 않는다 — 해결 불가로 보고 기존처럼 사유를 남기고 실패로 둔다.
    # 화장실/욕실, 방 등은 DB(pr_room)에만 있고 면적은 단위가 평/㎡ 섞여 있어 DB_보정값_조회에서 ㎡로 맞춘다.
    _저장거부_해결규칙 = {
        '해당층 노출': ('체크', 'floor_display_use_1', None),
        '리주소 공개': ('체크', 'address_detail_ri_state', None),
        '대지면적': ('DB값', 'area_land', '대지면적'),
        '연면적': ('DB값', 'area_const_sum', '연면적'),
        '건물면적': ('DB값', 'area_const', '건물면적'),
        '전용면적': ('DB값', 'area_real', '전용면적'),
        '화장실': ('DB값', 'bath', '화장실수'),
        '욕실': ('DB값', 'bath', '화장실수'),
        '방': ('DB값', 'room', '방수'),
        '주용도': ('DB값', 'main_yongdo', '주용도'),
        '사용승인일': ('DB값', 'build_date', '사용승인일'),
        '방향': ('DB선택', 'direction', '방향'),
        '방향 기준': ('DB선택', 'direction_type', '방향기준'),
    }
    # '층'은 같은 문구가 두 칸(해당층/총층)에 쓰여 입력칸 이름으로 구분한다.
    _층_입력칸_DB값 = {'floor_current': '해당층', 'floor_total': '총층'}
    _저장거부_최대해결횟수 = 12  # 38개 조합 시험에서 가장 긴 연쇄가 16단계였지만 기존 매물은 대부분 채워져 있어 이보다 훨씬 짧다

    # 저장 거부 때 사이트가 보여주는 안내창의 (문구, 대상 칸)을 읽으려고 폼 열 때 붙이는 훅 — 안내창 본문만으로는
    # '층'처럼 같은 문구의 어느 칸인지 알 수 없다.
    _거부항목_훅_JS = (
        "if(!window.__obsRejectHooked){window.__obsRejectHooked=1;window.__obsRejects=[];"
        "var o=window.open_alert_modal;window.open_alert_modal=function(a,b,c,id){window.__obsRejects.push([b,id||'']);return o.apply(this,arguments);};}"
    )

    def DB_보정값_조회(self, 코드):
        """
        저장 거부 사유를 채울 때 쓸 DB 값 묶음. 값이 비었거나 0인 항목은 아예 넣지 않는다(= 출처 없음으로 취급).
        토지·건물·호실을 고르는 조인은 auto.py::obang_data의 o_query와 같은 규칙이다 — 하나를 고치면 다른 쪽도 맞출 것.
        """
        conn = self._DB연결()
        try:
            cur = conn.cursor(pymysql.cursors.DictCursor)
            cur.execute("""SELECT l.land_totarea, b.building_purpose, b.building_grndflr, b.building_archarea, b.building_totarea,
                    b.building_usedate, b.building_direction, r.room_floor, r.room_rcount, r.room_bcount, r.room_direction,
                    r.r_direction, r.room_area1, r.room_areatype1
                FROM pr_object o
                LEFT JOIN pr_land AS l ON l.land_code = COALESCE(
                    (SELECT li.land_code FROM pr_land_group_item li INNER JOIN pr_land il ON il.land_code = li.land_code AND il.land_del = 'N'
                     WHERE li.land_group_code = o.land_group_code
                       AND il.land_jibun = (SELECT lgr.representing_jibun FROM pr_land_group lgr WHERE lgr.land_group_code = o.land_group_code) LIMIT 1),
                    (SELECT li2.land_code FROM pr_land_group_item li2 WHERE li2.land_group_code = o.land_group_code ORDER BY li2.item_idx ASC LIMIT 1)
                ) AND l.land_del = 'N'
                LEFT JOIN pr_building AS b ON b.building_code = (SELECT bi.building_code FROM pr_building_group_item bi WHERE bi.building_group_code = o.building_group_code LIMIT 1) AND b.building_del = 'N'
                LEFT JOIN pr_room AS r ON r.room_code = (SELECT ri.room_code FROM pr_room_group_item ri WHERE ri.room_group_code = o.room_group_code LIMIT 1) AND r.room_del = 'N'
                WHERE o.object_code_new = %s LIMIT 1""", (코드,))
            행 = cur.fetchone() or {}
        finally:
            conn.close()

        def 숫자문구(값):
            try:
                수 = float(str(값).replace(',', '').strip())
            except ValueError:
                return None
            return None if 수 <= 0 else (str(int(수)) if 수 == int(수) else f"{수:.2f}".rstrip('0').rstrip('.'))

        보정값 = {}
        for 이름, 컬럼 in (('대지면적', 'land_totarea'), ('연면적', 'building_totarea'), ('건물면적', 'building_archarea'),
                           ('화장실수', 'room_bcount'), ('방수', 'room_rcount'), ('총층', 'building_grndflr')):
            값 = 숫자문구(행.get(컬럼))
            if 값:
                보정값[이름] = 값
        # 전용면적: 사이트 칸은 ㎡라 DB가 '평'으로 저장한 건은 변환한다(1평 = 3.305785㎡).
        전용 = 숫자문구(행.get('room_area1'))
        if 전용:
            보정값['전용면적'] = 숫자문구(float(전용) * 3.305785) if (행.get('room_areatype1') or '').strip() == '평' else 전용
        # 해당층: '3', '지하1' 같은 문구는 숫자만 있는 경우에만 쓴다(추정하지 않음).
        해당층 = str(행.get('room_floor') or '').strip()
        if 해당층.isdigit() and int(해당층) > 0:
            보정값['해당층'] = 해당층
        if (행.get('building_purpose') or '').strip():
            보정값['주용도'] = 행['building_purpose'].strip()
        승인일 = 행.get('building_usedate')
        if isinstance(승인일, datetime.date) and 승인일.year > 1900:
            보정값['사용승인일'] = 승인일.strftime('%Y%m%d')
        방향 = (행.get('room_direction') or 행.get('building_direction') or '').strip()
        if 방향:
            보정값['방향'] = 방향
        if (행.get('r_direction') or '').strip():
            보정값['방향기준'] = 행['r_direction'].strip()
        return 보정값

    def _거부항목_해결(self, 문구, 입력칸, 보정값):
        """
        저장이 거부된 항목 하나를 규칙표대로 채운다. :return: 채웠으면 True, 규칙이 없거나 DB에 값이 없으면 False.
        """
        규칙 = self._저장거부_해결규칙.get(문구)
        if 문구 == '층':
            규칙 = ('DB값', 입력칸, self._층_입력칸_DB값.get(입력칸)) if 입력칸 in self._층_입력칸_DB값 else None
        if not 규칙:
            return False
        방식, 칸이름, 값이름 = 규칙
        if 방식 == '체크':
            return bool(self.driver.execute_script(
                "var e=document.getElementById(arguments[0]); if(!e) return false; if(!e.checked) e.click(); return e.checked;", 칸이름))
        값 = 보정값.get(값이름)
        if not 값:
            return False
        칸 = self.driver.find_element(By.NAME, 칸이름)
        if 방식 == 'DB값':
            self._입력칸_값_넣기(칸, 값)
            return True
        if 방식 == 'DB선택':
            return bool(self.driver.execute_script(
                "var s=arguments[0], t=arguments[1]; var o=[].slice.call(s.options).filter(function(x){return x.text.trim()===t;})[0];"
                "if(!o) return false; s.value=o.value; $(s).trigger('change'); return true;", 칸, 값))
        return False

    def _저장하고_거부사유_해결하기(self, 코드):
        """
        수정 폼의 [매물 저장]을 누르고, 필수항목 때문에 거부되면 규칙표대로 채워 다시 저장한다(통과할 때까지 반복).
        거부 사유를 하나라도 못 채우면 그 자리에서 멈춘다 — 저장은 거부된 채라 사이트에는 아무것도 반영되지 않는다
        (일부만 채워 저장되는 일이 없다). :return: (결과, 해결한 문구 목록) — 결과는 '이동함'(저장됨) 또는 거부 사유 문구.
        """
        # 사이트의 저장 검사는 '위치정보 소재지'(#dong_id)가 비어 있으면 "소재지를 입력해주세요"로 막는데, 이 칸은
        # 페이지가 열린 뒤 시/도→구/군→동 선택 목록을 불러오며 나중에 채워진다. 폼이 열리자마자 저장하면 아직
        # 비어 있는 시점에 걸려(2026-10-04 매매 11건이 전부 이 사유로 거부됨) 데이터가 멀쩡한데도 저장이 막힌다.
        # 채워질 때까지 기다린다 — 끝까지 비어 있으면(진짜 미입력) 기다림을 포기하고 사이트의 거부 사유를 그대로 받는다.
        try:
            WebDriverWait(self.driver, 15).until(lambda d: d.execute_script("return !!$('#dong_id').val();"))
        except TimeoutException:
            pass
        해결한 = []
        보정값 = None
        시도한_항목 = set()
        for _ in range(self._저장거부_최대해결횟수 + 1):
            self.driver.execute_script("window.__obsRejects = [];")
            저장버튼 = next(b for b in self.driver.find_elements(By.CSS_SELECTOR, '.save_btn') if b.is_displayed())
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", 저장버튼)
            저장버튼.click()
            self._저장후_알림_처리()
            # 저장이 통과하면 목록으로 이동하고, 막히면 같은 화면에 필수항목 안내창이 뜬다. 오부사는 중개대상물
            # 표시·광고법상 필수항목(예: 화장실)이 비어 있는 옛 매물은 가격만 고쳐도 저장을 거부한다.
            결과 = WebDriverWait(self.driver, 20).until(self._저장_결과_판정)
            if 결과 == '이동함':
                return 결과, 해결한
            거부 = self.driver.execute_script("var r=window.__obsRejects||[]; return r.length? r[r.length-1] : null;")
            if not 거부 or len(해결한) >= self._저장거부_최대해결횟수 or tuple(거부) in 시도한_항목:
                return 결과, 해결한   # 어느 항목인지 모르거나, 같은 항목이 되풀이되거나, 너무 길어지면 사람에게 넘긴다
            시도한_항목.add(tuple(거부))
            if 보정값 is None:
                보정값 = self.DB_보정값_조회(코드)
            if not self._거부항목_해결(거부[0], 거부[1], 보정값):
                return 결과, 해결한
            print(f"   [🛠️ 필수항목 자동 입력 - 오부사 {코드}] {거부[0]}({거부[1]}) ← DB/체크")
            해결한.append(거부[0])
            self.driver.execute_script("$('#modal-item_form_checks').modal('hide');")
            time.sleep(0.4)
        return 결과, 해결한

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
            # 필수항목 때문에 거부되면 규칙표대로 자동으로 채워 다시 저장한다. DB에도 값이 없어 못 채우는 항목(예:
            # 10039 화장실)은 사유를 그대로 로그에 남기고 실패로 둔다 — 임의로 채우지 않는다.
            결과, 해결한 = self._저장하고_거부사유_해결하기(코드)
            if 결과 != '이동함':
                print(f"   [❌ 가격 저장 거부 - 사람이 채워야 함 - 오부사 {코드}] {결과}")
                return '실패'
            self._이번_매물_해결문구.extend(해결한)
            확인 = self._수정폼_가격읽기(코드, list(목표))
            if 확인 == 목표:
                return '수정함'
            print(f"   [❌ 가격 수정 미반영 - 오부사 {코드}] 저장 후 다시 열어보니 {확인} (목표 {목표})")
            return '실패'
        except Exception as e:
            print(f"   [❌ 가격 수정 실패 - 오부사 {코드}] {type(e).__name__}: {str(e)[:200]}")
            self._알림창_정리()
            return '실패'

    # 거래유형 불일치를 DB 기준으로 자동 수정해도 되는 조건(2026-10-07 사용자 결정: "조건부 자동"). 가격과 달리
    # 거래유형은 매물의 성격 자체를 바꾸므로 DB가 최신이라는 근거가 있을 때만 한다 — 사이트의 '수정일'은 갱신이
    # 덮어써서 어느 쪽이 최신인지 사이트로는 알 수 없고(가격 때와 같은 문제), DB 수정일이 최근인 경우만 믿는다.
    _거래유형_자동수정_DB수정_허용일수 = 30
    _폼_거래유형값 = {'월세': 'month_rent', '전세': 'full_rent', '매매': 'sell'}

    def 거래유형_자동수정_허용(self, db행, 사이트행, 오늘):
        """ :return: (허용 여부, 허용 안 할 때의 사유) """
        if db행.get('object_ttype') not in self._폼_거래유형값:
            return False, f"DB 거래종류 '{db행.get('object_ttype')}'은(는) 월세/전세/매매가 아니라 자동 수정 대상이 아님"
        if 사이트행.get('deal') not in self._폼_거래유형값:
            # 전월세처럼 복수 유형을 함께 등록한 매물은 DB(단일 유형)로 덮으면 사이트에만 있는 가격 정보가 사라진다.
            return False, f"사이트 거래유형 '{사이트행.get('deal')}'은(는) 복수 유형일 수 있어 DB 값으로 덮으면 정보가 사라질 수 있음"
        수정일 = db행.get('object_udate')
        if isinstance(수정일, datetime.datetime):
            수정일 = 수정일.date()
        if not isinstance(수정일, datetime.date) or (오늘 - 수정일).days > self._거래유형_자동수정_DB수정_허용일수:
            return False, f"DB 수정일({수정일})이 {self._거래유형_자동수정_DB수정_허용일수}일 이내가 아니어서 DB가 최신이라는 근거가 없음"
        return True, ''

    def 거래유형_맞추기(self, 코드, db행):
        """
        수정 폼에서 거래유형 버튼을 DB 거래종류로 바꾸고 그 유형의 가격 칸을 DB 값으로 채워 저장한다(필수항목 거부는
        수정폼에서_가격_맞추기와 같은 자동 해결 루프를 탄다). 저장 후 폼을 다시 열어 유형과 가격이 반영됐는지 확인한다.
        :return: '이미같음' | '수정함' | '실패'
        """
        목표형 = self._폼_거래유형값[db행['object_ttype']]
        _, 입력칸규칙, _, _ = self._가격_동기화_규칙[db행['object_ttype']]
        목표 = {이름: int(db행[컬럼] or 0) for 이름, 컬럼 in 입력칸규칙.items()}
        현재형_JS = "return $('input[name=type]:checked').val();"
        try:
            self._수정폼_가격읽기(코드, list(목표))   # 폼을 열고 거부항목 훅을 붙인다(읽은 값은 여기선 안 쓴다)
            현재형 = self.driver.execute_script(현재형_JS)
            if 현재형 == 목표형:
                return '이미같음'
            print(f"   [🔁 거래유형 수정 - 오부사 {코드}] 사이트:{현재형} → DB:{목표형} {목표}")
            self.driver.execute_script("$('.btn_type.btn_' + arguments[0]).click();", 목표형)
            time.sleep(0.8)
            if self.driver.execute_script(현재형_JS) != 목표형:
                print(f"   [❌ 거래유형 수정 실패 - 오부사 {코드}] 거래유형 버튼을 눌러도 {목표형}로 바뀌지 않았습니다")
                return '실패'
            for 이름, 값 in 목표.items():
                self._입력칸_값_넣기(self.driver.find_element(By.NAME, 이름), 값)
            결과, 해결한 = self._저장하고_거부사유_해결하기(코드)
            if 결과 != '이동함':
                print(f"   [❌ 거래유형 저장 거부 - 사람이 채워야 함 - 오부사 {코드}] {결과}")
                return '실패'
            self._이번_매물_해결문구.extend(해결한)
            확인 = self._수정폼_가격읽기(코드, list(목표))
            확인형 = self.driver.execute_script(현재형_JS)
            if 확인 == 목표 and 확인형 == 목표형:
                return '수정함'
            print(f"   [❌ 거래유형 수정 미반영 - 오부사 {코드}] 저장 후 다시 열어보니 유형 {확인형}, 가격 {확인} (목표 {목표형}, {목표})")
            return '실패'
        except Exception as e:
            print(f"   [❌ 거래유형 수정 실패 - 오부사 {코드}] {type(e).__name__}: {str(e)[:200]}")
            self._알림창_정리()
            return '실패'

    def _수정폼_가격읽기(self, 코드, 입력칸이름들):
        self.driver.get(f'https://osan-bns.com/admin_item/edit/{코드}?page=1')
        WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.NAME, 입력칸이름들[0])))
        self.driver.execute_script(self._거부항목_훅_JS)
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
        """ :return: (성공, 비공개, 건너뜀, 실패, 미등록, 가격수정, 자동보정) — 총건수는 앞의 다섯의 합과 같고, 가격수정·자동보정은 부가 지표다. """
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
                self._이번_매물_해결문구 = []
                유형맞춤함 = False
                if 가격판정 == '확인필요':
                    가격결과 = self.수정폼에서_가격_맞추기(코드, db행)
                    if 가격결과 == '수정함':
                        self.price_fix_ok += 1
                    elif 가격결과 == '실패':
                        self.error_count += 1
                        continue
                elif 가격판정 == '대상아님' and '거래유형 불일치' in 가격사유:
                    허용, 불허사유 = self.거래유형_자동수정_허용(db행, 행, 오늘)
                    if not 허용:
                        print(f"   [⚠️ 거래유형 불일치 - 사람 확인 필요 - 오부사 {코드}] {가격사유} — {불허사유}")
                    else:
                        유형결과 = self.거래유형_맞추기(코드, db행)
                        if 유형결과 == '수정함':
                            유형맞춤함 = True
                        elif 유형결과 == '실패':
                            self.error_count += 1
                            continue
                # 필수항목 자동 입력이나 거래유형 맞춤이 한 번이라도 있었으면 보정 1건으로 센다(가격수정처럼 부가 지표).
                if 유형맞춤함 or self._이번_매물_해결문구:
                    self.auto_fix_ok += 1
                # 가격 맞추기는 요청 여부와 무관하게 모든 활성 매물에 하되(가격이 틀린 채 노출되면 안 됨),
                # 목록 상단 재노출(갱신)은 요청이 있었던 매물에만 한다.
                if not self.갱신_대상_여부(db행, 오늘):
                    self.skip_count += 1
                    continue
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
        return self.complete_count, self.end_ok, self.skip_count, self.error_count, self.not_found_count, self.price_fix_ok, self.auto_fix_ok

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
