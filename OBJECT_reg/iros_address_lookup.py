# repos_python/OBJECT_reg/iros_address_lookup.py
# [2026-09-06 신규 — 사용자 요청] "연장등록" 확인창에서 등기부상 주소/부동산고유번호가 없을 때,
# 인터넷등기소에서 결제 없이(주소만) 조회해 채워주는 자동화. 크롬확장(chrome_extension/iros_autofill/
# content_iros.js)의 같은 이름 로직을 셀레니움으로 옮긴 것이다 — 새 로직을 창작하지 않았다.
#
# [왜 크롬확장을 안 쓰고 이걸 새로 만들었나]
# 크롬확장의 발급 자동화는 chrome.windows.create()로 직접 여는 창에서 동작하는데, 이 창은 "로그인
# 세션 유지"와 "완전히 숨김" 두 조건을 동시에 만족시키지 못한다(background.js의 openDocumentIssueSite()
# 주석 참고 — 실사용 반복검증 끝에 "로그인 순간만 잠깐 보임"으로 절충했다). 그런데 "연장등록"에는
# 이미 팝업을 닫고 배너로만 진행하는 "숨김 모드"가 있어서, 이 조회도 사람 눈에 전혀 안 보이게 끝나야
# 한다. 다행히 이 조회(주소만 확인)는 애초에 로그인이 필요 없는 단계까지만 가므로, 로그인 유지
# 문제 자체가 없다 — 그래서 네이버 연장등록(local_helper의 별도 셀레니움 크롬)과 같은 방식으로,
# 크롬확장이 아니라 로컬도우미가 직접 스폰하는 독립된 셀레니움 크롬에서 실행한다.
# [2026-09-07 수정 — 사용자 리포트로 발견] 처음엔 "로그인이 필요 없으니 최소화만 해도 된다"고
# 판단했지만(Phase 1 검증, 2026-09-06), 실사용 중 창이 실제로 화면에 보이는 게 재현됐다 — 최소화는
# 작업표시줄에 아이콘이 남고 창이 사라지기 전 잠깐 그려지는 순간이 있어 "화면에 아무 표시도 없어야
# 한다"는 기준을 못 채운다. naver.py가 같은 문제를 먼저 겪고 고친 방식(--headless=new, 진짜 창을
# 안 만듦) 그대로 맞췄다 — find_register_address() 안의 동기화 경고 주석 참고.
#
# 결제 버튼은 절대 누르지 않는다 — 원본 크롬확장의 확고한 원칙("등기부는 유료고 열람하면 취소가
# 어렵다")을 그대로 지킨다. 이 스크립트는 "결제대상 확인" 화면에서 주소·고유번호만 읽고 끝난다.
#
# 검색결과가 여러 건으로 좁혀지지 않으면(같은 지번에 동이 여러 개 있는데 저장된 동 정보가 없는
# 경우 등) 자동으로 아무거나 고르지 않고 실패로 보고한다 — content_iros.js와 동일한 안전 원칙
# ("잘못 짚으면 안 되니 애매하면 사람에게 넘긴다").

import re
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

BASE = 'mf_wfm_potal_main_wfm_content'
PASS_THROUGH_TITLES = ['용도 및 추가사항 선택', '등기기록유형 선택', '(주민)등록번호 공개여부 확인', '등기신청사건 처리여부 확인']
PAYMENT_TITLES = ['결제대상 확인']


def _js_click(driver, el):
    """WebDriver의 좌표 기반 click()이 커스텀 위젯(라디오/체크박스 td)에서 종종
    ElementNotInteractableException/ElementClickInterceptedException을 낸다(실측 확인, 2026-09-06 —
    검색결과 행의 rad_sel 셀, 결제대상 표의 체크박스, 플로팅 "맨 위로" 버튼에 가려진 [다음] 버튼).
    execute_script로 DOM에 직접 click 이벤트를 보내면 좌표·가시성 판정을 건너뛰어 더 안정적이다
    (content_iros.js의 .click()과 동일한 효과)."""
    driver.execute_script('arguments[0].click();', el)


def _set_ws_value(driver, el_id, value):
    """WebSquare 컴포넌트(소재지번검색 입력칸)는 .value 대입이 안 먹힌다(content_iros.js 주석 확인).
    window.$p.getComponentById(id).setValue(value)가 실제 우회로다 — 크롬확장은 격리된 실행환경이라
    이 API를 못 불러 배경스크립트를 거쳤지만(background.js::OBANG_IROS_SET_COMPONENT_VALUES),
    셀레니움은 페이지 JS 컨텍스트에서 바로 실행되므로 그 우회가 필요 없다."""
    comp_id = re.sub(r'___input$', '', el_id)
    return driver.execute_script(
        """
        var comp = window.$p && window.$p.getComponentById(arguments[0]);
        if (comp && typeof comp.setValue === 'function') { comp.setValue(arguments[1]); return true; }
        return false;
        """,
        comp_id, value,
    )


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
    for e in driver.find_elements(By.CSS_SELECTOR, 'a, button'):
        try:
            if e.is_displayed() and re.search(r'부동산\s*열람.?발급', e.text.strip()):
                return e
        except Exception:
            continue
    return None


def _next_button(driver):
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


def find_register_address(payload):
    """
    payload: {
        'property_category': '토지'|'건물'|'집합건물',
        'location_search': {sido, sigungu, dong_or_li, jibun, building_dong_no, room_no},
        'register_record_type': '현재유효사항'|'말소사항포함',
    }
    (core/lib/lib_document_issue.php::getIrosIssuePayload()가 실제로 계산해 내려주는 값 그대로 —
    주소 파싱 로직을 여기서 새로 만들지 않는다.)

    @return {'ok': bool, 'address': str, 'unique_no': str, 'message': str}
    """
    property_category = payload.get('property_category') or ''
    loc = payload.get('location_search') or {}
    if not loc.get('dong_or_li') or not loc.get('jibun'):
        return {'ok': False, 'address': '', 'unique_no': '', 'message': '동·리 또는 지번 정보가 없습니다.'}

    options = Options()
    options.add_argument('--disable-blink-features=AutomationControlled')
    # [2026-09-07 수정 — 사용자 리포트 "숨김 모드가 아닌데도 화면에 창이 열려서 진행이 안 된다"]
    # 원래 "로그인이 필요 없으니 최소화만 해도 된다"고 판단했는데(Phase 1 검증), 실사용 중 창이
    # 실제로 화면에 보이는 게 재현됐다 — 최소화는 작업표시줄에 아이콘이 남고, 창이 완전히 사라지기
    # 전에 잠깐 그려지는 순간이 있어 "화면에 아무 표시도 없어야 한다"는 기준을 못 채운다. 정확히
    # 같은 문제를 naver.py가 2026-09-06에 먼저 겪고 --headless=new로 바꿨다(naver.py의 "webdriver
    # 열기" 주석 참고) — 여기도 같은 방식으로 바꾼다.
    # ⚠️ [동기화 경고] 창 숨김 방식(최소화 대신 진짜 headless)은 naver.py와 이 파일 둘 다 같은
    # 원칙을 따라야 한다 — 한쪽만 고치면 이번처럼 사용자가 "왜 어떤 자동화는 숨겨지고 어떤 건
    # 안 숨겨지냐"고 다시 겪게 된다.
    options.add_argument('--headless=new')
    driver = webdriver.Chrome(options=options)
    try:
        driver.set_window_size(1280, 1000)
        driver.get('https://www.iros.go.kr/index.jsp')
        wait = WebDriverWait(driver, 20)

        btn = wait.until(lambda d: _home_entry_button(d))
        _js_click(driver, btn)
        time.sleep(2)

        tab = wait.until(lambda d: d.find_element(By.ID, f'{BASE}_tac_rlrg_appl_tab_tab_loc_srch_tabHTML'))
        _js_click(driver, tab)
        time.sleep(1.5)

        picked = False
        for r in driver.find_elements(By.CSS_SELECTOR, f'#{BASE} input[type="radio"]'):
            rid = r.get_attribute('id') or ''
            if 'rad_loc_kind_cls' not in rid:
                continue
            try:
                label = driver.find_element(By.CSS_SELECTOR, f'label[for="{rid}"]')
            except NoSuchElementException:
                continue
            if label.text.strip() == property_category:
                _js_click(driver, label)
                picked = True
                break
        if not picked:
            return {'ok': False, 'address': '', 'unique_no': '',
                    'message': f'부동산구분 "{property_category}" 항목을 찾지 못했습니다.'}
        time.sleep(1.2)

        sido_id = f'{BASE}_sel_loc_admin_regn1'
        sido_el = driver.find_element(By.ID, sido_id)
        sido_value = None
        for opt in sido_el.find_elements(By.TAG_NAME, 'option'):
            if opt.text.strip() == loc.get('sido', ''):
                sido_value = opt.get_attribute('value')
                break
        if sido_value is None:
            return {'ok': False, 'address': '', 'unique_no': '',
                    'message': f'시/도 "{loc.get("sido", "")}" 옵션을 찾지 못했습니다.'}
        _set_ws_value(driver, sido_id, sido_value)
        time.sleep(0.6)

        jibun_el = _find_first_visible(driver, [
            f'#{BASE}_sbx_agrg_buld_loc_no___input',
            f'#{BASE}_sbx_loc_no___input',
        ])
        dongli_el = driver.find_element(By.ID, f'{BASE}_sbx_loc_admin_regn3___input')
        if not jibun_el:
            return {'ok': False, 'address': '', 'unique_no': '', 'message': '지번 입력칸을 찾지 못했습니다.'}

        _set_ws_value(driver, dongli_el.get_attribute('id'), loc['dong_or_li'])
        time.sleep(0.3)
        _set_ws_value(driver, jibun_el.get_attribute('id'), loc['jibun'])
        time.sleep(0.6)

        if property_category == '집합건물' and (loc.get('building_dong_no') or loc.get('room_no')):
            mode_index = 0 if (loc.get('building_dong_no') and loc.get('room_no')) else (1 if loc.get('building_dong_no') else 2)
            try:
                _js_click(driver, driver.find_element(By.CSS_SELECTOR, f'label[for="{BASE}_rad_loc_dong_room_sel_input_{mode_index}"]'))
                time.sleep(1)
            except NoSuchElementException:
                pass
            if loc.get('building_dong_no'):
                dong_el = _find_first_visible(driver, [f'#{BASE}_sbx_loc_buld_no_buld___input'])
                if dong_el:
                    _set_ws_value(driver, dong_el.get_attribute('id'), loc['building_dong_no'])
            if loc.get('room_no'):
                room_el = _find_first_visible(driver, [f'#{BASE}_sbx_loc_buld_no_room___input'])
                if room_el:
                    _set_ws_value(driver, room_el.get_attribute('id'), loc['room_no'])
            time.sleep(0.6)

        search_btn = None
        for e in driver.find_elements(By.CSS_SELECTOR, f'#{BASE} input, #{BASE} button, #{BASE} a'):
            if not e.is_displayed():
                continue
            text = (e.get_attribute('value') or e.text or '').strip()
            if text == '검색':
                search_btn = e
                break
        if not search_btn:
            return {'ok': False, 'address': '', 'unique_no': '', 'message': '검색 버튼을 찾지 못했습니다.'}
        _js_click(driver, search_btn)
        time.sleep(5)

        rows = _visible_result_rows(driver)
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
            return {'ok': False, 'address': '', 'unique_no': '', 'message': '검색결과에서 일치하는 부동산을 찾지 못했습니다.'}
        if len(matched) > 1:
            return {'ok': False, 'address': '', 'unique_no': '',
                    'message': f'검색결과가 {len(matched)}건이라 자동으로 고르지 않았습니다 — 매물의 저장된 동/호 정보가 부족할 수 있습니다.'}

        row = matched[0]
        _js_click(driver, row.find_element(By.CSS_SELECTOR, 'td[data-col_id="rad_sel"]'))
        time.sleep(0.6)

        nb = _next_button(driver)
        if not nb:
            return {'ok': False, 'address': '', 'unique_no': '', 'message': '[다음] 버튼을 찾지 못했습니다(부동산 선택 후).'}
        _js_click(driver, nb)
        time.sleep(1.5)

        record_select_el = None
        for _ in range(20):
            try:
                record_select_el = driver.find_element(By.ID, f'{BASE}_sel_cpab_kncd_input_0')
                break
            except NoSuchElementException:
                titles = _visible_section_titles(driver)
                if any('소재지번 선택' in t for t in titles):
                    nb2 = _next_button(driver)
                    if nb2:
                        _js_click(driver, nb2)
                time.sleep(1)
        if record_select_el is None:
            return {'ok': False, 'address': '', 'unique_no': '', 'message': '등기기록유형 선택 화면에 도달하지 못했습니다.'}

        wanted = payload.get('register_record_type') or '현재유효사항'
        try:
            Select(record_select_el).select_by_visible_text(wanted)
        except Exception:
            pass  # 기본값 그대로 진행 — 조회에는 영향 없다
        time.sleep(0.6)

        reached = None
        for _ in range(8):
            titles = _visible_section_titles(driver)
            if not titles:
                time.sleep(1.5)
                titles = _visible_section_titles(driver)
            if any(k in t for t in titles for k in PAYMENT_TITLES):
                reached = 'payment'
                break
            if not any(k in t for t in titles for k in PASS_THROUGH_TITLES):
                return {'ok': False, 'address': '', 'unique_no': '', 'message': f'예상하지 못한 화면입니다 — {titles}'}
            nb3 = _next_button(driver)
            if not nb3:
                return {'ok': False, 'address': '', 'unique_no': '', 'message': f'[다음] 버튼을 찾지 못했습니다 — {titles}'}
            _js_click(driver, nb3)
            time.sleep(2.5)

        if reached != 'payment':
            return {'ok': False, 'address': '', 'unique_no': '', 'message': '결제대상 확인 화면에 도달하지 못했습니다.'}
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
            # 여기서 반드시 멈춘다 — [결제] 버튼은 절대 누르지 않는다(원본 크롬확장의 확고한 원칙).
            return {'ok': True, 'address': addr_text, 'unique_no': unique_no, 'message': ''}

        return {'ok': False, 'address': '', 'unique_no': '', 'message': '결제대상 표에서 일치하는 줄을 찾지 못했습니다.'}

    except Exception as e:
        return {'ok': False, 'address': '', 'unique_no': '', 'message': f'자동화 중 오류: {e}'}
    finally:
        driver.quit()
