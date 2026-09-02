import os
import time
import datetime
import random
import platform
import pyautogui
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException

class ObangAutomationWorker:
    """ 오방부동산 웹사이트 제어 및 매물 업데이트/비공개 처리를 전담하는 클래스 """
    
    sele = {
        '원룸': [11, ['오픈형', '분리형', '통1.5룸', '1.5룸', '1.8룸']],
        '투룸/쓰리룸+': [12, ['투룸', '쓰리룸+']],
        '상가/사무실': [16, ['상가', '사무실']],
        '오피스텔': [13, []],
        '아파트': [14, []],
        '주택/고급빌라': [15, []],
        '공장/창고': [17, []],
        '토지': [18, []],
        '통건물': [19, ['상업용건물','상가주택','다가구주택','다세대주택','오피스텔','단독주택','도시형생활주택','주상복합건물','지식산업센터']],
    }

    def __init__(self, driver, data, mode, progress_callback=None, unattended=False):
        self.driver = driver
        self.data = data
        self.mode = mode
        self.progress_callback = progress_callback
        # 나스 무인 실행 등 사람이 화면 앞에 없는 경우 True — pyautogui 알림창은 사람 클릭을
        # 기다리며 무한정 멈추므로, 이때는 알림창 대신 progress_callback 로그로 대체한다.
        self.unattended = unattended

        self.complete_count = 0
        self.restart_ok = 0
        self.update_ok = 0
        self.end_ok = 0
        self.skip_count = 0

    def _경고_또는_로그(self, message):
        """ 수동 모드는 기존처럼 알림창으로 사람에게 묻고, 무인 모드는 로그로만 남기고 계속 진행한다. """
        if self.unattended:
            if self.progress_callback:
                self.progress_callback(0, 0, f"⚠️ {message}", 'determinate')
        else:
            pyautogui.alert(message)

    def modify_item(self, selector, value=''):
        element = self.driver.find_element(By.CSS_SELECTOR, selector)
        if element.is_displayed():
            try:
                if element.get_attribute('value'): element.clear()
            except: pass
            try: element.send_keys(value)
            except: pass

    def 현재페이지_매물번호수집(self, timeout=5):
        WebDriverWait(self.driver, timeout).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#search-items tr.admin_column")))
        ids = []
        for row in self.driver.find_elements(By.CSS_SELECTOR, "#search-items tr.admin_column"):
            try:
                pid = row.find_element(By.CSS_SELECTOR, "td:nth-of-type(2) strong").text.strip()
                if pid: ids.append(pid)
            except: continue
        return ids

    def 비공개여부(self, 토글):
        return (toggle_state.strip() == "1") if (toggle_state := 토글.get_attribute("data-state")) else False

    def 비공개로_전환(self, 매물번호, timeout=6):
        행 = WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, f"#tr_{매물번호}")))
        토글 = WebDriverWait(행, timeout).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "td:nth-of-type(3) .btn-group[onclick^='activated_change']")))
        if self.비공개여부(토글): return "skip"
        토글.click()
        try:
            WebDriverWait(self.driver, timeout).until(lambda d: self.비공개여부(d.find_element(By.CSS_SELECTOR, f"#tr_{매물번호} td:nth-of-type(3) .btn-group[onclick^='activated_change']")))
            return "ok"
        except: return "fail"

    def 선택목록_비공개처리(self, 비공개할매물번호들_arr, timeout=6):
        성공, 스킵, 실패 = [], [], []
        for pid in 비공개할매물번호들_arr:
            try:
                결과 = self.비공개로_전환(pid, timeout=timeout)
                if 결과 == "ok": 성공.append(pid)
                elif 결과 == "skip": 스킵.append(pid)
                else: 실패.append(pid)
            except: 실패.append(pid)
        print(f"[비공개 처리] 성공:{len(성공)} / 이미 비공개:{len(스킵)} / 실패:{len(실패)}")
        return {"성공": 성공, "이미비공개": 스킵, "실패": 실패}

    def 현재페이지_비공개처리(self, DB완료_set, timeout=6):
        현재페이지_매물번호들_arr = self.현재페이지_매물번호수집()
        비공개할매물번호들_arr = [pid for pid in 현재페이지_매물번호들_arr if pid in DB완료_set]
        # if not 비공개할매물번호들_arr: return {"성공": [], "이미비공개": [], "실패": []}
        return self.선택목록_비공개처리(비공개할매물번호들_arr, timeout=timeout)

    def 다음페이지_있나(self):
        els = self.driver.find_elements(By.XPATH, "//ul[@id='paging']//a[contains(., '다음')]")
        return els[0] if els else None

    def 다음페이지로_이동(self, timeout=10):
        링크 = self.다음페이지_있나()
        if not 링크: return False
        기존_첫행 = None
        기존행들 = self.driver.find_elements(By.CSS_SELECTOR, "#search-items tr.admin_column")
        if 기존행들: 기존_첫행 = 기존행들[0]
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", 링크)
        링크.click()
        wait = WebDriverWait(self.driver, timeout)
        if 기존_첫행:
            try: wait.until(EC.staleness_of(기존_첫행))
            except: pass
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#search-items tr.admin_column")))
        return True

    def 모든페이지_비공개처리(self, 최대페이지=None, timeout=8):
        """
        첫 페이지부터 '다음'이 없을 때까지 반복 처리.
        - obangData['거래완료매물']과 현재 페이지를 교집합 후 비공개 처리
        - 최대페이지: 안전장치(정수). None이면 제한 없음.
        """
        DB완료_set = set(str(x).strip() for x in (self.data.get('거래완료매물') or []) if str(x).strip())
        총성공, 총스킵, 총실패 = [], [], []
        페이지 = 1
        
        while True:
            print(f"\n=== [{페이지}페이지] 비공개 처리 시작 ===")
            if self.progress_callback:
                self.progress_callback(페이지, 100, f"🔒 오방 완료 매물 일괄 비공개 전환 중... ({페이지}페이지 분석 중)", mode='indeterminate')

            결과 = self.현재페이지_비공개처리(DB완료_set, timeout=timeout)
            총성공 += 결과.get("성공", [])
            총스킵 += 결과.get("이미비공개", [])
            총실패 += 결과.get("실패", [])
            if 최대페이지 and 페이지 >= 최대페이지: break
            이동됨 = self.다음페이지로_이동(timeout=timeout)
            if not 이동됨: break
            페이지 += 1
        return {"성공": 총성공, "이미비공개": 총스킵, "실패": 총실패}

    def 메모에마크추가(self, 메모, 마크='-- '):
        if not 메모: return ""            
        return "<br>".join([f"{마크}{line}" for line in 메모.split("<br>") if line.strip()])       

    def 단일오방매물업데이트(self, 업데이트정보):
        if not 업데이트정보: return
        main_option, main_important, I_memo = '', '', ''
        current_date = datetime.date.today()
        formatted_date = current_date.strftime("%Y-%m-%d")

        admin_name = 업데이트정보['admin_name']
        object_code_new = 업데이트정보['object_code_new']
        request_code = 업데이트정보['request_code']
        object_type1, object_type2, land_code = 업데이트정보.get('object_type1', ''), 업데이트정보.get('object_type2', ''), 업데이트정보.get('land_code', '')
        building_code, room_code, tr_target = 업데이트정보.get('building_code', ''), 업데이트정보.get('room_code', ''), 업데이트정보.get('tr_target', '')
        object_type, object_ttype = 업데이트정보.get('object_type', ''), 업데이트정보.get('object_ttype', '')
        
        obinfo_trading = '' if 업데이트정보['request_trading'] =='' else 업데이트정보['request_trading']
        obinfo_deposit1 = '' if 업데이트정보['request_deposit1'] =='' else 업데이트정보['request_deposit1']
        
        if obinfo_deposit1 == '' :
            land_address = 업데이트정보.get('land_address', '주소 미기재')

            if self.unattended:
                # 무인 모드는 팝업으로 사람에게 물어볼 수 없으므로 자동으로 건너뛴다.
                # DB 조회 로직(obang_data)이 매번 대상 후보를 새로 뽑기 때문에, 나중에 사람이
                # 임대료를 채워 넣으면 별도 재처리 큐 없이도 다음 실행 때 자연히 다시 시도된다.
                self._경고_또는_로그(f"[자동 건너뜀-임대료누락] 새홈번호:{object_code_new} 주소:{land_address}")
                self.skip_count += 1
                self.driver.find_element(By.CSS_SELECTOR, '#menu-product-1 > a').click()
                time.sleep(0.5)
                return "skip"

            import sys
            msg = f"[새홈 매물번호: {object_code_new}]\n주소: {land_address}\n\n임대료 값이 누락되었습니다! 이 매물을 건너뛰시겠습니까?"
            ans = pyautogui.confirm(text=msg, title="⚠️ 임대료 누락 경고", buttons=['건너뛰기(예)', '프로그램 종료(아니오)'])
            if ans == '건너뛰기(예)':
                self.skip_count += 1
                self.driver.find_element(By.CSS_SELECTOR, '#menu-product-1 > a').click()
                time.sleep(0.5)
                return "skip"
            else:
                self.driver.quit(); sys.exit()
            
        obinfo_deposit2 = '' if 업데이트정보['request_deposit2'] =='' else 업데이트정보['request_deposit2']
        obinfo_deposit3 = '' if 업데이트정보['request_deposit3'] =='' else 업데이트정보['request_deposit3']
        obinfo_rent1 = '' if 업데이트정보['request_rent1'] =='' else 업데이트정보['request_rent1']
        obinfo_rent2 = '' if 업데이트정보['request_rent2'] =='' else 업데이트정보['request_rent2']
        obinfo_rent3 = '' if 업데이트정보['request_rent3'] =='' else 업데이트정보['request_rent3']    
        request_manager = '' if 업데이트정보['request_manager'] =='' else 업데이트정보['request_manager']
        request_mmoney = 업데이트정보['request_mmoney']
        request_area1 = 업데이트정보['request_area1']
        request_mlist = 업데이트정보['request_mlist']
        tr_memo = 업데이트정보['tr_memo']

        location_do = 업데이트정보['land_do']
        if location_do.endswith('도'):
            if '경상남도' in location_do: location_do = '경남'
            elif '경상북도' in location_do: location_do = '경북'
            elif '충청남도' in location_do: location_do = '충남'
            elif '충청북도' in location_do: location_do = '충북'
            elif '전라남도' in location_do: location_do = '전남'
            elif '전라북도' in location_do: location_do = '전북'
            elif '강원특별자치도' in location_do: location_do = '강원'
            else: location_do = location_do[:-1]
        elif location_do.endswith('특별시'): location_do = location_do[:-3]

        location_detail = 업데이트정보['land_dong'] + 업데이트정보['land_jibun'] if 업데이트정보['land_li'] == '' else 업데이트정보['land_li'] + ' ' + 업데이트정보['land_jibun']
        main_area, land_memo = 업데이트정보['land_totarea'], 업데이트정보['land_memo']
        land_memo_formatted = self.메모에마크추가(land_memo , '· ')
        if land_memo_formatted: I_memo += ("<br>" if I_memo else "") + land_memo_formatted
        main_important = 업데이트정보.get('land_important', '').strip()

        basic_secret = ('' if tr_memo == '' else tr_memo + Keys.ENTER) + ('' if land_memo == '' else land_memo + Keys.ENTER)
            
        if tr_target in ['건물', '층호수']:
            building_grndflr, building_ugrndflr = 업데이트정보['building_grndflr'], 업데이트정보['building_ugrndflr']
            main_area = 업데이트정보['building_totarea']
            building_memo_formatted = self.메모에마크추가(업데이트정보['building_memo'] , '· ')
            main_option += ','+업데이트정보.get('building_option', '').strip() if main_option != '' else 업데이트정보.get('building_option', '').strip()
            main_important += ','+업데이트정보.get('building_important', '').strip() if main_important != '' else 업데이트정보.get('building_important', '').strip()
            if building_memo_formatted: I_memo += ("<br>" if I_memo else "") + building_memo_formatted
            basic_secret += '' if 업데이트정보['building_memo'] == '' else 업데이트정보['building_memo'] + Keys.ENTER

        if tr_target == '층호수':
            room_status = ' '+업데이트정보['room_status'] if 업데이트정보['room_status']!='미확인' else ' 상태미확인' 
            room_gate1 = ' '+업데이트정보['room_gate1'] if 업데이트정보['room_gate1']!='비밀번호' else ' 방' 
            location_detail += ('' if 업데이트정보['room_num'] == '' else ' ' + 업데이트정보['room_num']) + (room_status+room_gate1+(':'+업데이트정보['room_gate2'] if 업데이트정보['room_gate2'] != '' else '') if room_gate1 != ' 미확인' else ' 미확인')
            main_area = 업데이트정보['room_area1']
            main_option += ','+업데이트정보.get('room_option', '').strip() if main_option != '' else 업데이트정보.get('room_option', '').strip()
            main_important += ','+업데이트정보.get('room_important', '').strip() if main_important != '' else 업데이트정보.get('room_important', '').strip()
            room_memo_formatted = self.메모에마크추가(업데이트정보['room_memo'] , '· ')
            if room_memo_formatted: I_memo += ("<br>" if I_memo else "") + room_memo_formatted
            basic_secret += '' if 업데이트정보['room_memo'] == '' else 업데이트정보['room_memo'] + Keys.ENTER
            
        basic_secret = f"[새홈{object_code_new}] 수정일:"+formatted_date+" "+admin_name + Keys.ENTER +" https://obangkr.cafe24.com/web/request/request_view/view_give_request_detail.php?request_code="+request_code
        main_area_pyeong = str(int(float(main_area)/3.305785)) if main_area != '' else ''

        if tr_target == '층호수' and object_type == '주거용' and 업데이트정보.get('room_rcount', '') != '':
            rcnt = float(업데이트정보['room_rcount'])
            if 1 <= rcnt < 2:
                object_type1 = '원룸'
                object_type2 = "오픈형" if "오픈형" in main_important else "분리형"
            elif rcnt >= 2:
                object_type1 = '투룸/쓰리룸+'
                object_type2 = '투룸' if rcnt == 2 else '쓰리룸+'
        elif tr_target == '층호수' and object_type == '상업용': object_type1 = '상가/사무실'
        elif tr_target == '층호수' and object_type == '공업용': object_type1 = '공장/창고'
        elif tr_target == '건물':
            object_type1 = '공장/창고' if object_type == '공업용' else '통건물'
            object_type2 = '다가구주택' if object_type == '주거용' else '상업용건물'
        elif tr_target == '토지': object_type1 = '토지'

        if object_type1 != '':
            self.driver.find_element(By.ID, f'category_{self.sele[object_type1][0]}').click()
            if self.sele[object_type1][1]: 
                for a in self.driver.find_elements(By.CLASS_NAME, f'main_{self.sele[object_type1][0]}'):
                    if a.text == object_type2: a.click()   

        거래종류값 = '전/월세' if ',' in object_ttype and '전세' in object_ttype and '월세' in object_ttype else object_ttype
        for group in self.driver.find_elements(By.CLASS_NAME, 'form-group'):
            try:
                if '거래종류' in group.find_element(By.CLASS_NAME, 'control-label').text:
                    for btn in group.find_elements(By.XPATH, './/div[contains(@class, "btn-group")]//div[contains(@class, "btn")]'):
                        if 거래종류값 in btn.text.strip(): btn.click(); break
                    break
            except: pass

        if 거래종류값 == '전/월세':
            first_deposit, first_rent = None, None
            for deposit, rent in [(obinfo_deposit1, obinfo_rent1), (obinfo_deposit2, obinfo_rent2), (obinfo_deposit3, obinfo_rent3)]:
                deposit_val, rent_val = int(deposit or 0), int(rent or 0)
                if deposit_val > 0 and rent_val == 0: self.modify_item("#full_rent_price", deposit_val)
                elif rent_val > 0 and first_deposit is None:
                    first_deposit, first_rent = deposit_val, rent_val
                    self.modify_item("#monthly_rent_deposit", first_deposit)  
                    self.modify_item("#monthly_rent_price", first_rent)       
        else:
            if obinfo_deposit1 != '': self.modify_item("#full_rent_price", obinfo_deposit1)  
            if obinfo_deposit1 != '': self.modify_item("#monthly_rent_deposit", obinfo_deposit1)  
            if obinfo_rent1 != '': self.modify_item("#monthly_rent_price", obinfo_rent1)  
            if obinfo_trading != '': self.modify_item("#sell_price", obinfo_trading)  

        if request_manager=='별도': self.modify_item("#mgr_price", request_mmoney)
        if tr_target == '층호수':
            관리내역ex = request_mlist.split(',') + ['일반관리']
            try:
                for item in 관리내역ex:
                    for 관리내역 in self.driver.find_elements(By.XPATH, '//*[@id="mgr_include_checkbox"]/input'):
                        if item == 관리내역.get_attribute("value") and not 관리내역.is_selected(): 관리내역.click(); break
            except: pass    
            if request_area1 != '' : self.modify_item("#real_area", request_area1)
            if 업데이트정보['room_floor'] != '' : self.modify_item("#current_floor", 업데이트정보['room_floor'])
            self.driver.find_element(By.XPATH, '//*[@id="enter_year"]').clear() 
            self.driver.find_element(By.XPATH, '//*[@id="enter_year"]').send_keys('입주협의' if '사용' in 업데이트정보['room_status'] else '즉시입주') 

        secret_box = self.driver.find_element(By.XPATH, '//*[@id="info_base"]/div[2]/div[13]/div[2]/textarea')
        secret_box.clear(); secret_box.send_keys(basic_secret) 

        if tr_target != '토지':
            main_collections = [option.strip() for option in list(set(main_option.split(',') + main_important.split(','))) if option.strip()]
            replace_options = {"가스렌지": "가스레인지", "지상주차장": "주차장", "지하주차장": "주차장", "벽걸이에어컨": "에어컨", "천정형에어컨": "에어컨", "건물CCTV": "CCTV", "전자렌지": "전자레인지", "구분공간": "내실"}    
            updated_options = [replace_options.get(opt, opt) for opt in main_collections]
            replace_importants = {"복층형": "복층형 구조", "무권리": "권리금 무", "전세대출가능": "전세대출", "천정형에어컨": "천정에어컨", "전자렌지": "전자레인지", "지상주차장": "주차장"}    
            updated_importants = [replace_importants.get(imp, imp) for imp in main_collections]
            if "엘리베이터" in updated_options: updated_importants.append("엘리베이터")  
            if "주차장" in updated_options: updated_importants.append("주차장")  
            if tr_target == '층호수' and 업데이트정보['room_floor'] == '1': updated_importants.append("1층")    
            
            for box in self.driver.find_elements(By.XPATH, '//*[@id="info_add"]/div[2]/div[17]/div[2]/div/label'):
                if box.text.strip().replace('\n', ' ') in updated_importants and not "active" in box.get_attribute("class"): box.click()
            
            # 🔥 [오타 수정] By.TAG_TAG_NAME 이었던 잘못된 부분을 By.TAG_NAME 으로 전면 수정
            for box in self.driver.find_elements(By.XPATH, '//*[@id="option"]/div/label'):
                if box.find_element(By.TAG_NAME, 'input').get_attribute('value').strip() in updated_options and not "active" in box.get_attribute("class"): box.click()

            object_detail = '[ 매 물 기 본 정 보 ]'
            if object_type == '주거용' and tr_target == '층호수' and 업데이트정보.get('room_rcount', '') != '':
                object_detail += f'<p>● 방: {int(float(업데이트정보["room_rcount"]))}개 / 욕실:{업데이트정보["room_bcount"]}개</p>'
            else:
                if tr_target == '건물' and building_grndflr: object_detail += f'<p>● 총층: {str(building_grndflr-building_ugrndflr)}층 (지상{str(building_grndflr)}층 / 지하{str(building_ugrndflr)}층)</p>'
                elif tr_target == '층호수' and main_area: object_detail += f'<p>● 면적: {main_area}㎡ (약{main_area_pyeong}평)</p>'
            
            if I_memo: object_detail += '<p><br>[ 매 물 주 요 특 징 ]</p><p>' + I_memo + '</p>'
            
            # 🔥 [원형 전수 복원] 유실되었던 3줄짜리 상세 홍보문구 레이아웃 전체 복구 완료
            detail = '<p>' + object_detail + '<br></p><p>----------------------------------------------------------------------------------------------</p>'
            detail += '<p>◈아직 등록되지 않은 매물도 다수 보유중이니 더 많은 매물을 안내받길 원하신다면 문의주시기 바랍니다.</p>'
            detail += '<p>◈편하게 연락 주시고 홈페이지도 방문해보세요!!</p><p>※렌트프리, 옵션, 협의사항 등 끝까지 도와드리겠습니다.</p>'
            detail += '<p>----------------------------------------------------------------------------------------------<br></p>'
            
            self.driver.switch_to.frame(self.driver.find_element(By.XPATH, '//*[@id="cke_1_contents"]/iframe'))            
            text_area = self.driver.find_element(By.XPATH, '//body')
            if text_area.get_attribute('innerHTML').strip() in ['', '<p><br></p>']:
                self.driver.execute_script("arguments[0].innerHTML = arguments[1];", text_area, detail)
            self.driver.switch_to.default_content()             

            try:
                # time.sleep(1)
                print("수정후 시작")
                수정후최신으로갱신버튼들 = self.driver.find_elements(By.XPATH, '//*[@id="product_form"]/div[7]/button[2]')
                if len(수정후최신으로갱신버튼들) > 0:
                    print("수정후최신으로갱신버튼들 개수:"+str(len(수정후최신으로갱신버튼들)))
                    # 수정후최신으로갱신버튼들이 존재하는 경우의 코드
                else:
                    print("수정후최신으로갱신버튼들이 페이지에 존재하지 않습니다.")       
                # pyautogui.alert("등록완료 수정 정상?")     
                # 수정후최신으로갱신버튼의 XPath를 사용하여 요소 찾기
                # time.sleep(1)
                수정후최신으로갱신버튼 = self.driver.find_element(By.XPATH, '//*[@id="product_form"]/div[7]/button[2]')
                수정후최신으로갱신버튼.click()
                try:
                    # 최대 3초 동안 수정후최신으로갱신버튼이 사라질 때까지 대기
                    WebDriverWait(self.driver, 3).until(EC.invisibility_of_element((By.XPATH, '//*[@id="product_form"]/div[7]/button[2]')))
                    print("정상적으로 최신등록일로갱신되었습니다.")
                except:
                    # 3초 내에 최신등록일로갱신 버튼이 사라지지 않으면 오류 메시지 출력
                    self._경고_또는_로그(f"[새홈번호:{object_code_new}] 정상적으로 최신등록일로갱신되지 않았습니다.")
                print("최신등록일로갱신 종료")

                # pyautogui.alert(f"{location_detail}\n\n등록완료 확인!! land_code:{land_code} building_code:{building_code} room_code:{room_code}")
            except Exception as e:
                self._경고_또는_로그(f"[새홈번호:{object_code_new}] 최신등록일로갱신시키기 에러발생: {e}")
                print("최신등록일로갱신시키기 에러발생:", str(e))
        
            # try:
            #     btn = self.driver.find_element(By.XPATH, '//*[@id="product_form"]/div[7]/button[2]')
            #     btn.click()
            #     WebDriverWait(self.driver, 3).until(EC.invisibility_of_element(btn))
            # except: pyautogui.alert("갱신 실패")            

    def process_updates(self):
        obang_update = self.data['업데이트매물']
        오방매물정보 = self.data['오방매물정보']
        total_items = len(obang_update)
        
        for idx, update_code in enumerate(obang_update, 1):
            if self.progress_callback:
                self.progress_callback(idx, total_items, f"🔄 오방 업데이트 중... ({idx}/{total_items} 완료) | 건너뜀: {self.skip_count}개")
                
            try:
                매물번호입력창 = self.driver.find_element(By.CSS_SELECTOR, "#search_id")
                매물번호입력창.clear(); 
                print(f"{update_code} 1.매물번호입력창 초기화")
                매물번호입력창.send_keys(update_code); 
                print("----- 2.매물번호입력창에 매물번호 입력")
                time.sleep(0.2); 
                매물번호입력창.send_keys(Keys.ENTER)
                print("----- 3.엔터(매물조회)")

                WebDriverWait(self.driver, 5).until(lambda d: d.find_elements(By.CSS_SELECTOR, "#search-items tr strong")[0].text.strip() == update_code)
                if len(self.driver.find_element(By.ID, "search-items").find_element(By.TAG_NAME, "tr").find_elements(By.TAG_NAME, "td")) == 1: continue

                #자료 존재유무 확인 = 첫번째목록의열개수가 1이면 자료없음을 의미
                첫번째목록의열개수 = len(self.driver.find_element(By.ID, "search-items").find_element(By.TAG_NAME, "tr").find_elements(By.TAG_NAME, "td"))
                # print(첫번째목록의열개수)
                # pyautogui.alert(f"첫번째목록의열개수 확인:{update_code}")
                if 첫번째목록의열개수 == 1:
                    print(f"자료없는 오방코드: {update_code}")
                    continue

                before_target = self.driver.find_element(By.CSS_SELECTOR, f"#tr_{update_code} > td:nth-child(15) > div").get_attribute('title').split(' ')[0]
                before_date = datetime.datetime.strptime(before_target , '%Y-%m-%d')
                today = datetime.datetime.today()
                print(f"----- before_date: ", before_date)
                # print(f"{update_code} today: ", today)
                # if before_date == today:            

                # 오늘 날짜와 비교하여 출력
                if before_target == str(datetime.date.today()):
                    print("----- 5.Today! pass")
                    continue
                elif before_date > today:
                    print("----- 5.Future Date! pass")
                    continue

                행 = WebDriverWait(self.driver, 6).until(EC.presence_of_element_located((By.CSS_SELECTOR, f"#tr_{update_code}")))
                토글 = 행.find_element(By.CSS_SELECTOR, "td:nth-of-type(3) .btn-group[onclick^='activated_change']")
                제목 = 행.find_element(By.CSS_SELECTOR, "td:nth-of-type(9) .admin_title_section").text
                print("조회수입력란 찾음")

                if self.비공개여부(토글) and not 제목 in ['상가/사무실','원룸','투룸','테스트','투룸/쓰리룸+']:
                    print(f"기본제목을 사용하지 않는 비공개매물 오방코드:{update_code}")
                    try:
                        # 1. viewbadge span 클릭해서 input 보이게 하기
                        view_span = 행.find_element(By.CSS_SELECTOR, "td:nth-of-type(18) .viewbadge"); view_span.click()
                        # 2. input 태그가 보이게 된 후 다시 찾기
                        조회수입력란 = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, f"#tr_{update_code} td:nth-of-type(18) span:nth-of-type(2) input[type='text']")))
                        조회수입력란.send_keys(Keys.CONTROL + "a")
                        조회수입력란.send_keys("0")
                        print("조회수입력란 초기화")

                        토글.click() #공개로 전환
                        print("공개전환 완료")
                        self.restart_ok += 1  
                    except Exception as e:
                        print("조회수 초기화 및 공개전환 실패")
                        self._경고_또는_로그(f"[오방코드:{update_code}] 토글버튼을 찾을 수 없습니다: {e}")

                    #수정페이지로 전환
                    행.find_element(By.CSS_SELECTOR, "td:nth-child(14) > div:nth-child(1)").click() #관리 클릭
                    self.driver.find_element(By.CSS_SELECTOR, f'#tr_{update_code} > td:nth-child(14) > div.dropdown.open > ul > li:nth-child(1)').click() #수정 클릭
                    #재등록 프로세스 시작
                    선택된매물정보 = 오방매물정보.get(update_code)
                    print("선택된매물정보:",선택된매물정보)
                    res_update = self.단일오방매물업데이트(선택된매물정보)
                    if res_update == "skip": continue

                else:
                    print("----- 이미 공개된 매물")
                    # continue
                    # pyautogui.alert(f"이미 공개된 매물 오방코드:{update_code}")
                    print("----- 5.past Date! update")
                    행.find_element(By.CSS_SELECTOR, "td:nth-child(14) > div:nth-child(1)").click() #관리 클릭
                    print("----- 5-1.관리 클릭")
                    self.driver.find_element(By.CSS_SELECTOR, f'#tr_{update_code} > td:nth-child(14) > div.dropdown.open > ul > li:nth-child(7)').click() #최신등록일로갱신 클릭
                    print("----- 5-2.최신등록일로갱신 클릭")

                #거래완료 해제
                status_span = self.driver.find_elements(By.XPATH, f'//*[@id="tr_{update_code}"]/td[10]/span')
                # print(status_span.text)
                span_texts = []    
                for span in status_span: span_texts.append(span.text)
                if "완료" in span_texts:
                    print("----- 6.완료라벨 표시중 -> 완료라벨 제거")
                    self.driver.execute_script(f"change('is_finished','{update_code}','0');")
                    try:
                        alert = WebDriverWait(self.driver, 0.2).until(EC.alert_is_present())
                        alert.accept()
                    except Exception as e:
                        print("alert오류", str(e))
                        pass  # alert 창이 없는 경우, 그냥 넘어갑니다. 
                else:
                    print("----- 6.완료라벨 없음")
                    pass

                self.update_ok += 1; self.complete_count += 1                
            except: pass

    def process_closures(self):
        # process_updates()에서 매물을 순회하며 여러 페이지를 오간 뒤라 사이드바 서브메뉴가
        # 접혀있을 수 있어 일반 click()이 "element not interactable"로 실패한다(2026-08-30
        # 나스에서 실제로 재현). 이 파일 다른 곳들처럼 자바스크립트 강제클릭으로 우회한다.
        메뉴버튼 = self.driver.find_element(By.CSS_SELECTOR, '#menu-product-1 > a')
        self.driver.execute_script("arguments[0].click();", 메뉴버튼)
        # 자바스크립트 강제클릭은 일반 click()과 달리 페이지 전환을 기다려주지 않아서,
        # 곧바로 다음 스크립트를 실행하면 #search_form이 아직 없는 상태일 수 있다
        # (2026-08-30 나스에서 실제로 재현: dispatchEvent on null). 페이지 전환이 끝나서
        # #search_form이 실제로 나타날 때까지 명시적으로 기다린 뒤 진행한다.
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "search_form")))
        self.driver.execute_script("""
            const hidden = document.querySelector('#only_public');
            if (hidden) hidden.value = 'public';
            document.querySelector('#search_form').dispatchEvent(new Event('submit', {bubbles:true}));
        """)
        Select(WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.NAME, "per_page")))).select_by_value("100")
        결과 = self.모든페이지_비공개처리()
        self.end_ok += len(결과.get("성공", []))

    def login_and_navigate(self):
        self.driver.implicitly_wait(10)
        # URL 열기
        # 나스 도커(리눅스 Xvfb)에는 창을 관리해주는 윈도우 매니저가 없어서 maximize_window()가
        # 내부적으로 쓰는 CDP 호출(Runtime.evaluate)이 깨진다(2026-08-30 실제로 재현).
        # auto.py 쪽에서 이미 --window-size로 크기를 지정해두므로 리눅스에서는 건너뛴다.
        if platform.system() == 'Windows':
            self.driver.maximize_window()
        self.driver.get('https://osanbang.com/adminlogin/index')
        try:
            아이디입력창 = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="login_form"]/div[1]/div/input'))
            )
            # 크롬 자동완성으로 필드에 값이 이미 채워져 있을 수 있어(2026-08-30 나스에서 실제로
            # 확인됨: 아이디가 중복 이어붙여져 로그인이 거부됨) 지우고 입력해야 하는데, 이 폼은
            # 자바스크립트로 값을 관리해서 .clear()가 안 먹는다(이 역시 실제로 확인됨). 이 파일
            # 다른 곳(조회수입력란)에서 이미 쓰고 있는 전체선택 방식이 이런 필드에 안전하다.
            # [2026-09-02] 이 Ctrl+A 방식만으로는 근본 해결이 안 됐다 — 크롬 자동완성이 언제
            # 끼어드는지가 실행마다 달라 Ctrl+A 이전/이후 어느 쪽으로도 경쟁(race condition)할
            # 수 있었다(진단 로그로 실제 확인함). 진짜 원인은 이 자동화가 쓰는 크롬 프로필에
            # 오방 로그인 정보가 저장돼 있던 것이라, auto.py의 드라이버 생성 옵션에서 비밀번호
            # 저장/자동완성 자체를 껐다(auto.py의 run_platform_workers, prefs 설정 참고). 이
            # Ctrl+A 방식은 그래도 안전장치로 남겨둔다.
            아이디입력창.send_keys(Keys.CONTROL + "a")
            아이디입력창.send_keys("nasangkwon@outlook.kr")
            비밀번호입력창 = self.driver.find_element(By.XPATH, '//*[@id="login_form"]/div[2]/div/input')
            비밀번호입력창.send_keys(Keys.CONTROL + "a")
            비밀번호입력창.send_keys('tkdrnjs2@')
            self.driver.find_element(By.XPATH, '//*[@id="login_form"]/div[3]/button').click()
        except TimeoutException:
            print("🔑 로그인창이 없습니다.")
            # self.driver.find_element(By.CSS_SELECTOR, '사이드바매물버튼좌표').click() #사이드바 매물 클릭
            
        사이드바매물버튼좌표 = 'body > div.page-container > div.page-sidebar-wrapper > div > ul > li:nth-child(3) > a > span.title'
        try:
            # [2026-09-02] 나스(도커) 환경이 로그인 직후 사이트 렌더링에 5초보다 오래 걸리는
            # 경우가 실제로 있었다(사람이 직접 로그인하면 문제없이 빠르게 뜨는 것과 대조적으로
            # 확인됨) — 여유를 두어 20초로 늘림. 그래도 실패하면(로그인 자체가 막혔거나 사이트
            # 구조가 바뀐 경우) 그 순간 화면을 스크린샷으로 남겨 다음에 원인을 바로 알 수 있게 한다.
            사이드바매물버튼 = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 사이드바매물버튼좌표))
            )
        except TimeoutException:
            screenshot_dir = os.path.join('logs', 'screenshots')
            os.makedirs(screenshot_dir, exist_ok=True)
            screenshot_path = os.path.join(
                screenshot_dir,
                f"obang_login_timeout_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            )
            self.driver.save_screenshot(screenshot_path)
            print(f"🔍 사이드바 매물버튼을 못 찾음 — 실패 화면을 저장했습니다: {screenshot_path}")
            raise
        사이드바매물버튼.click() #사이드바 매물 클릭
        self.driver.find_element(By.CSS_SELECTOR, '#menu-product-1 > a').click() #매물->매물관리 클릭

    def run(self):
        self.login_and_navigate() 
        if self.mode in ['all', 'update_only']: self.process_updates()
        if self.mode in ['all', 'close_only']: self.process_closures()
        return self.complete_count, self.restart_ok, self.update_ok, self.end_ok, self.skip_count