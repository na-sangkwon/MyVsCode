from selenium import webdriver
from selenium.webdriver import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.chrome.options import Options

import pyautogui 
import time
import os

options = Options()

options.add_argument("--disable-blink-features=AutomationControlled")

def macro(data, user):
    def 그룹별명칭변환(그룹, 대상명칭):
        # 변환 매핑
        변환사전 = {}
        if 그룹 == '건축물용도':
            변환사전 = {
                "근린생활시설": "제1종 근린생활시설",
                "제1종근린생활시설": "제1종 근린생활시설",
                "제2종근린생활시설": "제2종 근린생활시설",
                "노유자시설": "노유자(老幼者: 노인 및 어린이)시설",
                "위락시설": "위락(慰樂)시설",
                "교정군사시설": "교정(矯正) 및 군사 시설",
                "자동차관련시설": "자동차 관련 시설",
                "다세대주택": "공동주택",
                # 추가 매핑
            }
        elif 그룹 == '옵션종류':
            변환사전 = {
                "공터": "마당",
                "에어컨": "벽걸이에어컨",
                "가스렌지": "가스레인지",
                "인덕션": "인덕션레인지",
                "전자렌지": "전자레인지",
                # "에어컨": "에어컨",
                # 추가 매핑
            }
        elif 그룹 == '관리비포함내역':
            변환사전 = {
                "중로접": "큰길가",
                "대로접": "큰길가",
                # 추가 매핑
            }
        elif 그룹 == '구군':
            변환사전 = {
                "용인시 처인구": "용인처인구",
                "용인시 기흥구": "용인기흥구",
                "용인시 수지구": "용인수지구",
                # 추가 매핑
            }
        elif 그룹 == '읍면동':
            변환사전 = {
                # "남사읍": "남사면",
                "대로접": "큰길가",
                # 추가 매핑
            }
        elif 그룹 == '매물상태':
            변환사전 = {
                "사용(주인)": "직접 운영중",
                "사용(임차인)": "임대중",
                "공실": "비어있음",
            }

        # 매핑된 값 반환, 매핑되지 않았으면 원래 값을 반환
        return 변환사전.get(대상명칭, 대상명칭)
    
    def 목록_변환(그룹, 항목들):
        변환된_항목들 = []
        for 항목 in 항목들.split(','):
            변환된_항목들.append(그룹별명칭변환(그룹, 항목.strip()))
        return ','.join(변환된_항목들)        
    
    def click_item_in_group(group_text, item_text):
        # 그룹 텍스트를 가진 th 요소를 찾습니다.
        group_th = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//th[text()='{group_text}']"))
        )
        # 그룹이 포함된 테이블을 찾습니다.
        table = group_th.find_element(By.XPATH, "./ancestor::table")
        # 해당 테이블 내의 모든 td 요소를 찾습니다.
        td_elements = table.find_elements(By.TAG_NAME, "td")
        # 아이템 텍스트를 포함하는 label 요소가 있는지 확인합니다.
        item_found = False
        for td in td_elements:
            # 각 td 요소 내에서 label 요소를 찾습니다.
            labels = td.find_elements(By.TAG_NAME, "label")
            for label in labels:
                if item_text in label.text:
                    label.click()
                    item_found = True
                    break
            if item_found:
                break
        return item_found
    def selectOption(select_xpath, value):
        time.sleep(0.3)
        # 선택항목요소 = WebDriverWait(driver, 10).until(
        #     EC.element_to_be_clickable((By.XPATH, f"{select_xpath}"))
        # )
        # driver.execute_script("arguments[0].scrollIntoView();", 선택항목요소)
        # # time.sleep(0.3)
        # 선택항목요소.click()
        
        select_element = driver.find_element(By.XPATH, f'{select_xpath}')
        
        # Select 객체를 생성하고 select 엘리먼트를 래핑합니다.
        select = Select(select_element)
        try:
            select.select_by_visible_text(value) #일치하는 텍스트 선택하기
        except Exception as e:
            print("선택 오류:", str(e))
            
    def clickList(btn_selector, value):
        time.sleep(0.3)
        if value == '':
            print("값이 없습니다.")
        else:
            driver.find_element(By.CSS_SELECTOR, f'{btn_selector}').click() #드롭다운버튼 클릭

            # div_element = driver.find_element(By.XPATH, f'{div_xpath}') #li를 가진 div
            # # div_element.click()
            # # pyautogui.alert("계속 ??")
            # print("리스트 선택:", value)
            try:
                dropdown_elements = driver.find_elements(By.CSS_SELECTOR, "ul li a span:first-child")
                # dropdown_elements = driver.find_elements(By.CSS_SELECTOR, "div.con_box_wrap.static_factory_o ul li a span:first-child")
                for dropdown_element in dropdown_elements:
                    # print(dropdown_element.text)
                    if dropdown_element.text == value:
                        dropdown_element.click()
                        break        
                      
            except Exception as e:
                print("선택 오류:", str(e))
            
    def 숫자한글로금액변환(숫자금액):
        숫자금액 = 숫자금액.replace(',', '')
        # 억과 만원으로 나누기
        billion = int(숫자금액) // 10000  # 억
        million = int(숫자금액) % 10000   # 만원
        # 변환한 값을 문자열로 만들기
        변환된금액 = ''
        if billion > 0:
            변환된금액 += f"{billion}억"
        if million > 0:
            변환된금액 += f"{million}만원"
        # 값이 없는 경우 "0원"으로 설정
        if not 변환된금액:
            변환된금액 = "0원"
        return 변환된금액
    
    def 카테고리별_텍스트_찾기(DIV영역클래스명, 카테고리_이름, 입력_타입, 대상텍스트):
        print(f"카테고리별_텍스트_찾기({DIV영역클래스명}, {카테고리_이름}, {입력_타입}, {대상텍스트})")
        try:
            if DIV영역클래스명 == '':
                카테고리xpath = f"//span[text() = '{카테고리_이름}']"
            else:
                카테고리xpath = f"//div[contains(@class, '{DIV영역클래스명}')]//span[text() = '{카테고리_이름}']"
            # 대상 카테고리의 span 요소들을 찾음 (모든 요소 대기)
            카테고리_spans = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, 카테고리xpath))
                # EC.presence_of_all_elements_located((By.XPATH, f"//div/span[contains(text(), '{카테고리_이름}')]"))
            )
            
            # print(f'카테고리({카테고리_spans})의 개수'+ str(len(카테고리_spans)))
            
            # 보이는 요소만 처리
            보이는_카테고리_spans = [span for span in 카테고리_spans if span.is_displayed()]
            # print(f'보이는 카테고리({보이는_카테고리_spans})의 개수' + str(len(보이는_카테고리_spans)))
            
            # 각 카테고리 span에 대하여
            if len(보이는_카테고리_spans) == 1:
                # print(f'보이는_카테고리_spans[0] :' , 보이는_카테고리_spans[0].get_attribute('outerHTML'))
                for 카테고리_span in 보이는_카테고리_spans:
                    카테고리포함_div = 카테고리_span.find_element(By.XPATH, "./ancestor::div[1]/ancestor::div[1]")  # or use "./.."
                    # print(f'카테고리포함_div :' , 카테고리포함_div.get_attribute('outerHTML'))
                    
                    # 하위두번째_div = 카테고리포함_div.find_element(By.XPATH, f"./div[2]/div[{count}]")
                    하위두번째_div = 카테고리포함_div.find_element(By.XPATH, f"./div[2]")
                    # print(f'하위두번째_div :' , 하위두번째_div.get_attribute('outerHTML'))
                    if 입력_타입 == 'radio':
                        # 모든_입력타입별요소들 = 하위두번째_div.find_elements(By.XPATH, f".//label[input[@type='{입력_타입}']]/span")
                        모든_입력타입별요소들 = 하위두번째_div.find_elements(By.XPATH, f".//div[@data-toggle='buttons']//span")
                    elif 입력_타입 == 'checkbox':
                        # 모든_입력타입별요소들 = 하위두번째_div.find_elements(By.XPATH, f".//input[@type='{입력_타입}']/following-sibling::label")
                        모든_입력타입별요소들 = 하위두번째_div.find_elements(By.XPATH, f".//label/input[@type='{입력_타입}']/following-sibling::span")
                    elif 입력_타입 in ['text', 'number']:
                        모든_입력타입별요소들 = 하위두번째_div.find_elements(By.XPATH, f".//input[@type='{입력_타입}']")
                    # print(f'모든_입력타입별요소들 개수: {len(모든_입력타입별요소들)}')    
                    보이는_입력타입별요소들 = [입력타입별요소 for 입력타입별요소 in 모든_입력타입별요소들 if 입력타입별요소.is_displayed()]
                    # print(f'보이는 입력타입별요소들의 개수: {len(보이는_입력타입별요소들)}')
                    for 라벨 in 보이는_입력타입별요소들:
                        # print("라벨:" , 라벨.get_attribute('outerHTML'))
                        # print(라벨.text)
                        if 입력_타입 in ['text', 'number']:
                            라벨.clear()
                            라벨.send_keys(대상텍스트)
                        else:
                            대상텍스트_리스트 = 대상텍스트.split(',')
                            if 라벨.text.strip() in 대상텍스트_리스트:
                                라벨.click()
                    
                    # 결과.extend(라벨텍스트)

        except Exception as e:
            print(f"Error: {e}")
   
    def new카테고리별_텍스트_찾기(DIV영역클래스명, 카테고리_이름, 입력_타입, 대상텍스트):
        print(f"new카테고리별_텍스트_찾기({DIV영역클래스명}, {카테고리_이름}, {입력_타입}, {대상텍스트})")
        try:
            # 주어진 DIV영역클래스명으로 상위 영역을 찾음
            div_area = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, f"//div[contains(@class, '{DIV영역클래스명}')]"))
            )

            # 그 영역 안에서 카테고리_이름(예: '1차 그룹')을 찾음
            category_title = div_area.find_element(By.XPATH, f".//*[contains(text(), '{카테고리_이름}')]")
            print(f"'{카테고리_이름}' 카테고리 타이틀을 찾았습니다.")

            # 입력 타입에 따라 다른 처리를 진행함
            if 입력_타입 == 'radio':
                # 대상텍스트(예: '쓰리룸+')가 포함된 라벨을 먼저 찾음
                radio_label = div_area.find_element(By.XPATH, f".//label//span[text()='{대상텍스트}']")
                # print(f"'{대상텍스트}' 라벨을 찾았습니다.")

                # 라벨에 포함된 라디오 버튼(input[type='radio'])을 찾음
                radio_button = radio_label.find_element(By.XPATH, "./preceding-sibling::input[@type='radio']")
                
                # # 요소가 화면에 보이지 않을 경우 스크롤 이동
                # driver.execute_script("arguments[0].scrollIntoView(true);", radio_button)

                # 요소가 보이지 않으면 클릭 전에 대기
                if not radio_button.is_displayed():
                    # print(f"'{대상텍스트}' 라디오 버튼이 숨겨져 있어 스크립트로 클릭합니다.")
                    driver.execute_script("arguments[0].click();", radio_button)
                else:
                    radio_button.click()
                print(f"'{대상텍스트}' 라디오 버튼이 클릭되었습니다.")

            elif 입력_타입 == 'text':
                # 대상 텍스트를 입력할 텍스트박스를 찾고, 텍스트를 입력
                input_element = category_title.find_element(By.XPATH, f".//following-sibling::div//input[@type='text']")
                input_element.send_keys(대상텍스트)
                print(f"텍스트 '{대상텍스트}'가 입력되었습니다.")
        
            elif 입력_타입 == 'checkbox':
                # 해당 영역 내 모든 체크박스와 라벨 텍스트를 출력
                checkboxes = div_area.find_elements(By.XPATH, ".//input[@type='checkbox']")
                for checkbox in checkboxes:
                    # 각 체크박스와 연결된 라벨 텍스트를 찾음
                    label_text = checkbox.find_element(By.XPATH, "./following-sibling::label").text
                    # print(f"체크박스 ID: {checkbox.get_attribute('id')}, 라벨 텍스트: {label_text}")
                    # 대상 텍스트와 라벨 텍스트가 일치하는 경우
                    if label_text == 대상텍스트:
                        # print(f"'{대상텍스트}' 체크박스를 발견했습니다. 체크박스 ID: {checkbox.get_attribute('id')}")
                        # 체크박스가 아닌 라벨을 클릭
                        label = checkbox.find_element(By.XPATH, f"./following-sibling::label[@for='{checkbox.get_attribute('id')}']")
                        driver.execute_script("arguments[0].scrollIntoView();", label)  # 라벨이 화면에 보이게 스크롤
                        label.click()  # 라벨을 클릭해서 체크박스를 활성화
                        # print(f"'{대상텍스트}' 라벨을 클릭하여 체크박스를 활성화했습니다.")
                        return

                print(f"'{대상텍스트}' 체크박스를 찾지 못했습니다.")

            else:
                print(f"지원되지 않는 입력 타입입니다: {입력_타입}")

        except Exception as e:
            print(f"오류 발생: {str(e)}")
                            
    errarr = []
    
    # 현재 날짜 출력
    import datetime
    current_date = datetime.date.today()
    formatted_date = current_date.strftime("%Y-%m-%d")
    
    admin_name = data['adminData']['admin_name']
    basic_secret = formatted_date+" "+admin_name+Keys.ENTER
    
    ad_email = data['adminData']['ad_email']
    ad_pw = data['adminData']['ad_pw']    
    request_code = data['writeData']['request_code'] #의뢰번호
    object_code_new = data['writeData']['object_code_new'] #새홈매물번호
    
    object_type = data['writeData']['object_type']
    object_type2 = data['writeData']['object_type2']
    tr_target = data['writeData']['tr_target']
    tr_range = data['writeData']['tr_range']
    trading = data['writeData']['trading'] #매매금액    
    deposit1 = data['writeData']['deposit1'] #보증금1
    deposit2 = data['writeData']['deposit2'] #보증금2
    deposit3 = data['writeData']['deposit3'] #보증금3
    rent1 = data['writeData']['rent1'] #월세1
    rent2 = data['writeData']['rent2'] #월세2
    rent3 = data['writeData']['rent3'] #월세3
    surtax = data['writeData']['surtax'] #부가세별도여부 Y
    premium_exist = data['writeData']['premium_exist'] #권리금존재유무
    premium = data['writeData']['premium'] #권리금
    premium_content = data['writeData']['premium_content'] #권리금 내역
    ttype = data['writeData']['object_ttype'] #거래종류

    manager = data['writeData']['manager'] #관리비 별도/포함/미확인
    mmoney = data['writeData']['mmoney'] #관리비
    mlist = data['writeData']['mlist'] #관리비포함내역
    mmemo = data['writeData']['mmemo'] #관리비메모
    
    landCount = data['landCount']  # 거래대상필지수
    # #사용할 변수들
    # desired_fields = ['land_si', 'land_dong', 'land_jibun']  # 원하는 필드명들의 리스트
    # # 변수 초기화
    # landData = {field: [] for field in desired_fields}
    # for i in range(0, landCount):
    #     for field in desired_fields:
    #         field_value = data['landData'][0][i][field]  # 해당 데이터의 필드 값
    #         landData[field].append(field_value)  # 필드명에 해당하는 변수에 데이터 추가
    # # 결과 확인 예시
    # for field, values in landData.items():
    #     print(f"{field} values:", values)
    # pyautogui.alert(data['landData'][4]['land_jibun'])
    
    optionImportant = ''
    secret_1 = '' if data['writeData']['tr_memo'] == '' else data['writeData']['tr_memo'] + Keys.ENTER
    secret_2 = '' if data['landData'][0]['land_memo'] == '' else data['landData'][0]['land_memo'] + Keys.ENTER
    basic_secret = secret_1 + secret_2 #비밀메모
    
    location_do = data['landData'][0]['land_do']
    if location_do.endswith('도'):
        if '경상남도' in location_do:
            location_do = '경남'
        elif '경상북도' in location_do:
            location_do = '경북'
        elif '충청남도' in location_do:
            location_do = '충남'
        elif '충청북도' in location_do:
            location_do = '충북'
        elif '전라남도' in location_do:
            location_do = '전남'
        elif '전라북도' in location_do:
            location_do = '전북'
        elif '강원특별자치도' in location_do:
            location_do = '강원'
        else:
            location_do = location_do[:-1]    
    location_si = data['landData'][0]['land_si']
    location_dong = data['landData'][0]['land_dong']
    location_lijibun = data['landData'][0]['land_jibun'] if data['landData'][0]['land_li'] == '' else (data['landData'][0]['land_li'] + ' ' + data['landData'][0]['land_jibun'])
    # location_dongli = (data['landData'][0]['land_dong'] + data['type_path'] + data['landData'][0]['land_jibun']) if data['landData'][0]['land_li'] == '' else location_lijibun
    location_dongli = location_dong if data['landData'][0]['land_li'] == '' else (location_dong + ' ' + data['landData'][0]['land_li'])
    land_jibung = data['landData'][0]['land_jibung'] 
    location_detail = location_lijibun
    land_totarea = data['landData'][0]['land_totarea']
    land_purpose = data['landData'][0]['land_purpose']
    representing_jimok = data['landData'][0]['representing_jimok']
    representing_purpose = data['landData'][0]['representing_purpose']
    representing_use = data['landData'][0]['representing_use']
    land_roadsize = data['landData'][0]['land_roadsize']
    land_memo = data['landData'][0]['land_memo'] #토지메모
    land_option = data['landData'][0]['land_option']
    main_area = land_totarea
    main_option = land_option
    # pyautogui.alert("확인 location_lijibun: "+location_lijibun)
    

    if tr_target == '건물' or tr_target == '층호수':
        location_building = '' if data['buildingData']['building_name'] == '' else ' ' + data['buildingData']['building_name']
        building_gate1 = ' '+data['buildingData']['building_gate1'] if data['buildingData']['building_gate1']!='비밀번호' else ' 현' #건물출입1
        building_gate2 = data['buildingData']['building_gate2'] if data['buildingData']['building_gate2'] != '' else '' #건물출입2  
        building_gate = building_gate1+building_gate2 if data['buildingData']['building_gate1'] == '비밀번호' else ''
        location_detail += location_building + building_gate
        # # print("building_gate1:", building_gate1)
        # # print("building_gate2:", building_gate2)
        # building_archarea = data['buildingData']['building_archarea'] #건축면적
        building_totarea = data['buildingData']['building_totarea'] #연면적
        flr_mainpurps = data['flrData']['flr_mainpurps'] #층주용도
        basic_totflr = str(int(data['buildingData']['building_grndflr']) + int(data['buildingData']['building_ugrndflr'])) #전체층
        building_ugrndflr = data['buildingData']['building_ugrndflr'] #지하층수
        building_grndflr = data['buildingData']['building_grndflr'] #지상층수
        building_type = data['buildingData']['building_type'] #건물타입 일반/집합
        building_purpose = data['buildingData']['building_purpose'] #건물주용도 
        building_direction = data['buildingData']['building_direction'] #건물방향
        building_usedate = str(data['buildingData']['building_usedate']) #준공일
        building_pn = data['buildingData']['building_pn'] #주차
        building_loan = data['buildingData']['building_loan'].decode('utf-8') #대출
        building_loan_rate = data['buildingData']['building_loan_rate'].decode('utf-8') #대출이자
        building_important = data['buildingData']['building_important'] #건물특징
        if building_important != '':
            optionImportant += ','+building_important if optionImportant != '' else building_important
        building_option = data['buildingData']['building_option'] #건물옵션
        if building_option != '':
            optionImportant += ','+building_option if optionImportant != '' else building_option
        sum_deposit = data['buildingData']['sum_deposit'].decode('utf-8') #총보증금
        sum_rent = data['buildingData']['sum_rent'].decode('utf-8') #총월세
        sum_mmoney = data['buildingData']['sum_mmoney'].decode('utf-8') #총관리비
        building_trmemo = data['buildingData']['building_trmemo'] #건물거래메모
        building_memo = data['buildingData']['building_memo'] #건물메모
        secret_3 = '' if building_memo == '' else building_memo + Keys.ENTER
        basic_secret += Keys.ENTER + location_detail + Keys.ENTER + secret_1
        # basic_secret += Keys.ENTER + basic_secret +secret_3
        main_area = building_totarea
        main_option = building_option

        brData = data['brData']
        # for room in brData:
        #     print(room['bri_sequence'])
        # pyautogui.alert(f"확인 float(trading):{str(float(trading))} len(brData):{str(len(brData))}")
        r_count = 0
        if float(trading) > 0 and len(brData)>0:
            for room in brData:
                if room['bri_type'].decode('utf8') in ['원룸', '투룸', '쓰리룸+']:
                    r_count += 1
            # pyautogui.alert("확인:"+str(r_count))    
            
    if tr_target == '층호수':
        location_room = '' if data['roomData']['room_num'] == '' else ' ' + data['roomData']['room_num']
        room_status = data['roomData']['room_status'] if data['roomData']['room_status']!='미확인' else '상태미확인' #호실상태
        room_gate1 = ' '+data['roomData']['room_gate1'] if data['roomData']['room_gate1']!='비밀번호' else ' 방' #내부출입1
        room_gate2 = ':'+data['roomData']['room_gate2'] if data['roomData']['room_gate2'] != '' else '' #내부출입2  
        room_gate = ' '+room_status+room_gate1+room_gate2 if room_gate1 != ' 미확인' else ' 미확인'
        location_detail += location_room+room_gate
        room_area1 = data['roomData']['room_area1'] #실면적
        room_area2 = data['roomData']['room_area2'] #공급면적
        room_direction = data['roomData']['room_direction'] if data['roomData']['room_direction']!='' else '방향' #호실방향
        direction_stn = '주출입문' if data['roomData']['direction_stn']=='' and object_type=='상업용' else data['roomData']['direction_stn'] #호실방향기준
        room_rcount = data['roomData']['room_rcount'] if data['roomData']['room_rcount']!='' else '0' #방수
        room_bcount = data['roomData']['room_bcount'] if data['roomData']['room_bcount']!='' else '0' #욕실수
        room_floor = data['roomData']['room_floor'] #해당층
        room_important = data['roomData']['room_important'] #호실특징
        if room_important != '':
            optionImportant += ','+room_important if optionImportant != '' else room_important
        room_option = data['roomData']['room_option'] #호실옵션
        if room_option != '':
            optionImportant += ','+room_option if optionImportant != '' else room_option
        room_options = room_option.split(',') #호실옵션리스트
        flr_strct = data['flrData']['flr_strct'] #층주구조
        room_memo = data['roomData']['room_memo'] #호실메모
        secret_4 = '' if room_memo == '' else room_memo + Keys.ENTER
        # basic_secret += secret_4    
        main_area = room_area1
        main_option = room_option
        
    def changeToPyeong(제곱미터면적):
        return str(int(float(제곱미터면적)/3.305785)) if 제곱미터면적 != '' else ''
        
    # basic_secret = "https://obangkr.cafe24.com/web/request/request_view/view_give_request_detail.php?request_code="+request_code
    
    # ChromeDriver 경로 설정
    driver = webdriver.Chrome(options=options)
    # driver = webdriver.Chrome('/chromedriver', options=options)
    # driver = webdriver.Chrome(ChromeDriverManager().install())

    # URL 열기
    driver.maximize_window()
    driver.get('https://osan-bns.com/admin_item/insert')
    # time.sleep(0.5)
    # pyautogui.alert('로그인 시도 id:'+ad_email+' pw:'+ad_pw)
    driver.find_element(By.XPATH, '//*[@id="email"]').send_keys(ad_email) # 'nsk4392@nate.com' ad_email
    driver.find_element(By.XPATH, '//*[@id="password"]').send_keys(ad_pw)
    # pyautogui.alert('로그인 시도 id:'+ad_email+' pw:'+ad_pw)
    driver.find_element(By.XPATH, '//*[@id="admin_login"]/button').click()
    
    driver.implicitly_wait(10)   

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="admin_wrap"]/header/div[1]/div'))) #헤더버튼이 나타날때까지 대기
    
    #매물 등록할지 수정할지 결정(새홈번호 6자리=>매물등록, 5자리=>매물수정)
    if len(object_code_new) != 5:
        print("신규매물등록 시작")
        driver.get('https://osan-bns.com/admin_item/insert') #매물등록화면으로 전환
        #등록폼 선택
        if object_type == '상업용': #//*[@id="form_item"]/div[1]/div[1]/div/div[2]
            driver.find_element(By.XPATH, '//*[@id="form_item"]/div[1]/div[1]/div/div[1]').click()
        elif object_type == '주거용':
            driver.find_element(By.XPATH, '//*[@id="form_item"]/div[1]/div[1]/div/div[2]').click() 
        elif object_type == '공업용':
            driver.find_element(By.XPATH, '//*[@id="form_item"]/div[1]/div[1]/div/div[4]').click() 
        elif object_type == '토지':
            driver.find_element(By.XPATH, '//*[@id="form_item"]/div[1]/div[1]/div/div[5]').click() 
           
# #기능테스트
#         pyautogui.alert("테스트 ㄱㄱ??")
#         # clickList('#form_item > div.form_box > div.box_contents > div.form_box_wrap.toji_basic > div.form_table > table > tbody > tr > td > div > div.con_box.con_box_wrap.static_factory_o > div.con_box.direction > div:nth-child(2) > div', '남서') #방향
#         clickList('#tab1 > table > tbody > tr > td > div > div:nth-child(1) > div.con_box.b_direction.b_direction_0 > div:nth-child(2) > div > button', '서') #방향 building_direction
#         # driver.find_element(By.XPATH, '//*[@id="b_direction_desc_0"]').send_keys('주출입문') #방향기준 
            
#         # clickList('#form_item > div.form_box > div.box_contents > div.form_box_wrap.toji_basic > div.form_table > table > tbody > tr > td > div > div.con_box.con_box_wrap.static_factory_o > div.con_box.direction > div:nth-child(2) > div', '서')
#         pyautogui.alert("계속진행??")
            
#위치정보
        if location_do != '경기도':
            driver.find_element(By.XPATH, '//*[@id="sido_id"]').click() 
            do_elements = driver.find_elements(By.XPATH, '//*[@id="sido_id"]/option')
            for do in do_elements:
                # print(do.text)
                if location_do == do.text :
                    do.click()
                    break
            
        if location_si != '오산시':
            driver.find_element(By.XPATH, '//*[@id="gugun_id"]').click() 
            si_elements = driver.find_elements(By.XPATH, '//*[@id="gugun_id"]/option')
            for si in si_elements:
                # print(si.text)
                if 그룹별명칭변환('구군', location_si) == si.text :
                    si.click()
                    break
        if location_dong != '궐동':
            driver.find_element(By.XPATH, '//*[@id="dong_id"]').click() 
            dong_elements = driver.find_elements(By.XPATH, '//*[@id="dong_id"]/option')
            for dong in dong_elements:
                # print(location_dong)
                # print(dong.text)
                if 그룹별명칭변환('읍면동', location_dong) == dong.text :
                    # print(location_dong)
                    dong.click()
                    break
        # time.sleep(0.5)
        driver.find_element(By.XPATH, '//*[@id="address_detail"]').send_keys(location_lijibun) #상세주소 입력
        # time.sleep(3)
        driver.find_element(By.XPATH, '//*[@id="address_detail"]').send_keys(Keys.ENTER) #지도위치이동
        # time.sleep(1)
        # driver.find_element(By.XPATH, '//*[@id="form_item"]/div[2]/div[1]/div[1]/div[2]/table/tbody/tr/td[1]/div/div[1]/div[3]/span').click() #위치이동
        
        # pyautogui.alert("준비?? object_type:"+object_type)
        # new카테고리별_텍스트_찾기('form_table_box_wrap category_op_box', '매물 공개 여부', 'checkbox', '공실')
        # new카테고리별_텍스트_찾기('item_type_box_wrap first_category_box', '1차 그룹', 'radio', '쓰리룸+')
        # 카테고리별_텍스트_찾기('보증금', 'text', '4392')
        # 카테고리별_텍스트_찾기('input_month_rent', '월세', 'text', rent1)
        # 카테고리별_텍스트_찾기('roombath1', '방', 'number', room_rcount)
        # 카테고리별_텍스트_찾기('price_box', '''
		# 												거래형태													''', 'radio', '월세')
        # 비밀메모요소들 = WebDriverWait(driver, 10).until(
        #     EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "textarea_content")]/textarea'))
        # )
        # 보이는_비밀메모요소들 = [비밀메모요소 for 비밀메모요소 in 비밀메모요소들 if 비밀메모요소.is_displayed()]
        # print(f'카테고리({보이는_비밀메모요소들})의 개수' + str(len(보이는_비밀메모요소들)))
        # print("비밀메모요소들 개수:"+str(len(보이는_비밀메모요소들)))
        # if len(보이는_비밀메모요소들) == 1:
        #     보이는_비밀메모요소들[0].send_keys(basic_secret)
        # driver.find_element(By.CSS_SELECTOR, '#floor_current').send_keys(room_floor)
        # 카테고리별_텍스트_찾기('detail_title', '''
		# 				                                옵션 종류
		# 				                            ''', 'checkbox', '가스렌지,식탁')          
        # 카테고리별_텍스트_찾기('form_table_box_manage', '''
		# 												관리비
		# 												''', 'radio', '없음')    
        # 카테고리별_텍스트_찾기('no_toji', '거래범위', 'radio', '건물 전체')
        # 카테고리별_텍스트_찾기('input_span_box_all', '지상층', 'number', building_grndflr)
        
        
        
        if object_type != '토지':
            pyautogui.alert(f"{location_detail}\n\n건물 선택후 확인버튼을 눌러주세요")
        else:
            driver.find_element(By.XPATH, '//*[@id="form_location_info"]/div[2]/div/div[1]/div[4]/div/div[2]/div[1]/label[3]').click()  #상세주소 표시방법으로 위치숨기기 선택
        
#매물정보
        # pyautogui.alert('등록폼선택 시도'+' tr_target:'+tr_target+' object_type:'+object_type)
        if tr_target == '층호수' and room_status == '공실' :
            new카테고리별_텍스트_찾기('form_table_box_wrap category_op_box', '매물 공개 여부', 'checkbox', '공실')
        elif tr_target == '건물':
            if object_type == '공업용':
                매물종류1차값 = '공장창고'
            else:
                매물종류1차값 = '통건물'
            카테고리별_텍스트_찾기('detail_title', '''
													매물 종류													''', 'radio', 매물종류1차값) #1차그룹 통건물 클릭
            카테고리별_텍스트_찾기('detail_title', '''
													매물 종류													''', 'radio', object_type2) #2차그룹
        #매물종류
        if tr_target == '토지':
            # click_item_in_group('1차 그룹', '토지')
            # click_item_in_group('2차 그룹', '대지') if representing_jimok=='대' else click_item_in_group('2차 그룹', '농지임야')
            그룹1선택값 = '토지'
            # pyautogui.alert(representing_jimok) 
            if representing_jimok:
                if representing_jimok=='대':
                    그룹2선택값 = '대지'
                else:
                    그룹2선택값 = '농지임야'
        else:
            #1차그룹
            if float(room_rcount) >= 3:
                그룹1선택값 = '쓰리룸+'
                if float(room_rcount) == 3:
                    그룹2선택값 = '쓰리룸'
                elif float(room_rcount) == 4:
                    그룹2선택값 = '포룸'
            else:
                그룹1선택값 = '원투룸'
                if float(room_rcount) >= 2:
                    그룹2선택값 = '투룸'
                elif float(room_rcount) > 1 and float(room_rcount) < 2:
                    그룹2선택값 = '1.5룸'
                elif float(room_rcount) == 1:
                    그룹2선택값 = '원룸'
            #2차그룹    
        
        new카테고리별_텍스트_찾기('item_type_box_wrap first_category_box', '1차 그룹', 'radio', 그룹1선택값)
        new카테고리별_텍스트_찾기('item_type_box_wrap second_category_box', '2차 그룹', 'radio', 그룹2선택값)
            
        #옵션종류
        if tr_target == '층호수':
            카테고리별_텍스트_찾기('detail_title', '''
						                                옵션 종류
						                            ''', 'checkbox', 목록_변환('옵션종류', optionImportant))

#금액정보
        if tr_target != '층호수' and tr_target != '토지' : 카테고리별_텍스트_찾기('no_toji', '거래범위', 'radio', '건물 전체') #거래범위 전체선택
        # pyautogui.alert(tr_target) 
        #거래유형
        if trading != '' and trading != '0' :
            카테고리별_텍스트_찾기('price_box', '''
														거래형태													''', 'radio', '매매') #매매버튼
            카테고리별_텍스트_찾기('input_sell building_shows', '매매가', 'text', trading) #매매가
            # pyautogui.alert("272 go?")
            if tr_target == '건물': 
                if building_loan:
                    if int(building_loan) > 0: 카테고리별_텍스트_찾기('input_loan building_shows', '융자금', 'radio', '있음')
                    카테고리별_텍스트_찾기('input_loan building_shows', '융자금', 'text', str(building_loan)) #융자금
                # pyautogui.alert("528 go?")
                if sum_deposit != '':
                    카테고리별_텍스트_찾기('input_deposit_hold building_hides', '기보증금', 'text', str(sum_deposit)) #총보증금
                    # driver.find_element(By.CSS_SELECTOR, '#form_item > div.form_box > div.box_contents > div:nth-child(3) > div.form_table > table > tbody > tr > td > div > div.con_box.con_box_wrap.no_villa_box.price_box > table > tbody > tr > th:nth-child(2) > div > div.contents_g_contents > div.input-group.m-b-xs.input_deposit_hold > input').send_keys(str(sum_deposit)) #총보증금
                    # pyautogui.alert("349?")     
                    카테고리별_텍스트_찾기('input_month_rent_total', '총월세', 'text', str(sum_rent)) #총월세  
                    카테고리별_텍스트_찾기('form_table_box input_rent_hold building_hides', '기월세', 'text', str(sum_rent)) #기월세                           
                    # driver.find_element(By.CSS_SELECTOR, '#form_item > div.form_box > div.box_contents > div:nth-child(3) > div.form_table > table > tbody > tr > td > div > div.con_box.con_box_wrap.no_villa_box.price_box > table > tbody > tr > th:nth-child(2) > div > div.contents_g_contents > div.input-group.m-b-xs.input_rent_hold > input').send_keys(str(sum_rent)) #총월세
        else :
            if deposit1 != '' and deposit1 != '0' :
                if rent1 != '' and rent1 != '0':
                    카테고리별_텍스트_찾기('price_box', '''
														거래형태													''', 'radio', '월세')
                    # driver.find_element(By.CSS_SELECTOR, '#form_item > div.form_box > div.box_contents > div:nth-child(3) > div.form_table > table > tbody > tr > td > div > div.con_box.con_box_wrap.no_villa_box.price_box > table > tbody > tr > th.price_types > div > div:nth-child(2) > div > label.btn.btn-default.btn_type.btn_month_rent.active').click() #월세버튼
                    # pyautogui.alert("ㄱㄱ?")
                    카테고리별_텍스트_찾기('input_month_deposit', '보증금', 'text', deposit1) #월세보증금
                    카테고리별_텍스트_찾기('input_month_rent', '월세', 'text', rent1) #월세
                    if object_type == '상업용': #부가세 포함/별도
                        if surtax == 'N':
                            driver.find_element(By.XPATH, '//*[@id="form_item"]/div[2]/div[1]/div[3]/div[2]/table/tbody/tr/td/div/div[2]/table/tbody/tr/th[2]/div/div[1]/div/div/label[1]').click()
                        else :
                            driver.find_element(By.XPATH, '//*[@id="form_item"]/div[2]/div[1]/div[3]/div[2]/table/tbody/tr/td/div/div[2]/table/tbody/tr/th[2]/div/div[1]/div/div/label[2]').click()
                else :
                    driver.find_element(By.XPATH, '//*[@id="form_item"]/div[2]/div[1]/div[3]/div[2]/table/tbody/tr/td/div/div[2]/table/tbody/tr/th[1]/div/div[2]/div/label[2]').click() #전세버튼
                    driver.find_element(By.XPATH, '//*[@id="form_item"]/div[2]/div[1]/div[3]/div[2]/table/tbody/tr/td/div/div[2]/table/tbody/tr/th[2]/div/div[2]/div[9]/input').send_keys(deposit1) #전세보증금
        
        if premium_exist == '있음': 
            driver.find_element(By.XPATH, '//*[@id="form_item"]/div[2]/div[1]/div[3]/div[2]/table/tbody/tr/td/div/div[4]/div[1]/div[2]/div[1]/label[1]').click() #권리금버튼
            driver.find_element(By.XPATH, '//*[@id="form_item"]/div[2]/div[1]/div[3]/div[2]/table/tbody/tr/td/div/div[4]/div[1]/div[2]/div[2]/input').send_keys(premium) #권리금
            driver.find_element(By.XPATH, '//*[@id="form_item"]/div[2]/div[1]/div[3]/div[2]/table/tbody/tr/td/div/div[4]/div[1]/div[2]/div[4]/input').send_keys(premium_content) #권리금 내역
        if manager == '별도' and tr_target == '층호수': 
            # driver.find_element(By.XPATH, '//*[@id="form_item"]/div[2]/div[1]/div[3]/div[2]/table/tbody/tr/td/div/div[4]/div[2]/div[2]/div[1]/label[1]').click() #관리비버튼
            카테고리별_텍스트_찾기('form_table_box_manage', '''
														관리비
														''', 'radio', '있음')   
            # driver.find_element(By.XPATH, '//*[@id="form_item"]/div[2]/div[1]/div[3]/div[2]/table/tbody/tr/td/div/div[4]/div[2]/div[2]/div[2]/div/input').send_keys(mmoney) #관리비
            카테고리별_텍스트_찾기('form_table_box_manage', '''
														관리비
														''', 'text', mmoney)   
            # driver.find_element(By.XPATH, '//*[@id="form_item"]/div[2]/div[1]/div[3]/div[2]/table/tbody/tr/td/div/div[4]/div[2]/div[2]/div[3]/input').send_keys(mmemo) #관리비메모
            # 카테고리별_텍스트_찾기('form_table_box_manage', '''
			# 											관리비
			# 											''', 'text', mmemo)   
   
            # mItem_elements = driver.find_elements(By.XPATH, '//*[@id="form_item"]/div[2]/div[1]/div[3]/div[2]/table/tbody/tr/td/div/div[4]/div[3]/div[2]/div')
            # for mItem in mItem_elements:
            #     label_tag = mItem.find_element(By.TAG_NAME, 'label')
            #     mlist_items = mlist.split(',')
            #     for item in mlist_items:
            #         if item == 'E/V관리': item = '엘리베이터' #연관 항목명으로 변경
            #         if item == label_tag.text: label_tag.click() #관리비에 포함된 항목 체크
            카테고리별_텍스트_찾기('management_price', '관리비 포함내역', 'checkbox', 목록_변환('관리비포함내역', mlist))
        else:
            카테고리별_텍스트_찾기('form_table_box_manage', '''
														관리비
														''', 'radio', '없음')            
        # pyautogui.alert('315 gogo?')            
#기본정보
        #매물상태
        if object_type == '상업용':
            if tr_target == '층호수':
                print('room_status:'+room_status)
                카테고리별_텍스트_찾기('static_status_wrap', '매물상태', 'radio', 그룹별명칭변환('매물상태', room_status))
                # if room_status == '공실':
                #     # print('공실진입 성공')
                #     driver.find_element(By.XPATH, '//*[@id="form_item"]/div[2]/div[1]/div[5]/div[2]/table/tbody/tr/td/div/div[2]/div[1]/div[2]/div/label[3]').click() #비어있음 클릭
                # elif room_status == '사용(임차인)':
                #     driver.find_element(By.XPATH, '//*[@id="form_item"]/div[2]/div[1]/div[5]/div[2]/table/tbody/tr/td/div/div[2]/div[1]/div[2]/div/label[2]').click() #임대중 클릭
                # elif room_status == '사용(주인)':
                #     driver.find_element(By.XPATH, '//*[@id="form_item"]/div[2]/div[1]/div[5]/div[2]/table/tbody/tr/td/div/div[2]/div[1]/div[2]/div/label[1]').click() #직접 운영중 클릭
        # pyautogui.alert('gogo?')
        #방수와 욕실수
        if tr_target == '층호수':
            카테고리별_텍스트_찾기('roombath1', '방', 'number', room_rcount) 
            카테고리별_텍스트_찾기('roombath2', '욕실', 'number', room_bcount)
            clickList('#form_basic_info > div.form_table > div:nth-child(3) > div.form_table_box.direction.hide_auctions > div.form_table_box_cnt > div.select_boxs.select_box_direction > div > button', room_direction) #방향
            # print('direction_stn:'+direction_stn)
            # 카테고리별_텍스트_찾기('방수', 'text', direction_stn) #방향기준 
            
            # #난방
            # clickList('#form_basic_info > div.form_table > div:nth-child(7) > div.form_table_box.heat > div.form_table_box_cnt > div.select_boxs.select_box_item_heat > div > button', '개별') #난방종류
            # pyautogui.alert('gogo?')
            #입주가능일
            if room_status == '공실':
                selectOption('//*[@id="date_select_type"]', '즉시입주가능')
            elif room_status == '사용(임차인)':
                selectOption('//*[@id="date_select_type"]', '가까운 시일내 협의')
            else:
                selectOption('//*[@id="date_select_type"]', '즉시입주가능')
            
            #면적
            if room_area2 != '' :
                driver.find_element(By.CSS_SELECTOR, '#area_law').send_keys(room_area2) #공급면적
            if room_area1 != '' :    
                driver.find_element(By.CSS_SELECTOR, '#area_real').send_keys(room_area1) #전용면적
            
            #층정보
            print('basic_totflr:'+basic_totflr,'room_floor:'+room_floor)
            
            if object_type == '주거용':
                #방/거실 형태
                방형태값 = '분리형'
                if '복층형' in optionImportant:
                    방형태값 = '복층'
                elif '오픈형' in optionImportant:
                    방형태값 = '오픈형'
                # 카테고리별_텍스트_찾기('room_type', '방/거실 형태', 'radio', 방형태값)   
                clickList('#form_basic_info > div.form_table > div:nth-child(3) > div.form_table_box.room_type.hide_auctions > div.form_table_box_cnt > div > div > button', 방형태값) 
            
            #복층여부
            복층여부값 = '단층'
            if '복층형' in optionImportant: 복층여부값 = '복층'
            카테고리별_텍스트_찾기('', '복층여부', 'radio', 복층여부값)
            
            #인테리어
            if '인테리어' in optionImportant or object_type=='주거용': 카테고리별_텍스트_찾기('', '인테리어', 'radio', '있음')
            
            #빌트인
            if '붙박이장' in optionImportant: 카테고리별_텍스트_찾기('', '빌트인', 'radio', '있음')
            
            #베란다/발코니
            if '인테리어' in optionImportant or object_type=='주거용': 카테고리별_텍스트_찾기('interior', '인테리어', 'radio', '있음')
        # pyautogui.alert('gogo?')
        if tr_target != '토지' :
            if building_type != '집합':
                if tr_target == '건물' :
                    # driver.find_element(By.CSS_SELECTOR, '#floor_current').send_keys(building_ugrndflr) #지하층
                    카테고리별_텍스트_찾기('floor_box1', '지하층', 'number', building_ugrndflr) #지하층
                    카테고리별_텍스트_찾기('input_span_box_all', '지상층', 'number', building_grndflr) #지상층
                    if object_type in ['주거용', '상업용']:
                        카테고리별_텍스트_찾기('roombath1', '방', 'number', r_count) #방
                    elif object_type == '공업용':
                        카테고리별_텍스트_찾기('roombath1', '사무실', 'number', 0) #사무실
                    if object_type == '주거용':
                        카테고리별_텍스트_찾기('roombath2', '욕실', 'number', 0) #욕실
                    elif object_type in ['상업용', '공업용']:
                        카테고리별_텍스트_찾기('roombath2', '화장실', 'number', 0) #화장실
                    clickList('#form_basic_info > div.form_table > div:nth-child(3) > div.form_table_box.direction.hide_auctions > div.form_table_box_cnt > div.select_boxs.select_box_direction', building_direction) #방향
                    clickList('#form_basic_info > div.form_table > div:nth-child(3) > div.form_table_box.direction.hide_auctions > div.form_table_box_cnt > div.select_boxs.select_box_direction_type', '주된 출입구') #방향기준
                    # pyautogui.alert("ㄱㄱ?")
                    
                    selectOption('//*[@id="date_select_type"]', '가까운 시일내 협의') #입주가능일
                    카테고리별_텍스트_찾기('main_yongdo', '주용도', 'text', building_purpose) #주용도
                if tr_target == '층호수' : 
                    floor_type = '지상'
                    if int(room_floor) < 0 :
                        floor_type = '반지하' if object_type == '주거용' else floor_type == '지하'
                    selectOption('//*[@id="floor_type"]', floor_type)
                    driver.find_element(By.CSS_SELECTOR, '#floor_current').send_keys(room_floor) #해당층
                    # driver.find_element(By.CSS_SELECTOR, '#form_item > div.form_box > div.box_contents > div.form_box_wrap.toji_basic > div.form_table > table > tbody > tr > td > div > div:nth-child(5) > div.con_box.floor > div:nth-child(3) > div:nth-child(4) > input').send_keys(basic_totflr) #총층수
                    카테고리별_텍스트_찾기('input_span_box_all', '총층', 'number', basic_totflr)
                    # pyautogui.alert('gogo?')
        
        if tr_target == '건물' :
            #주용도
            print('flr_mainpurps:',flr_mainpurps)
            # pyautogui.alert('gogo?')
            driver.find_element(By.CSS_SELECTOR, '#main_yongdo').send_keys(flr_mainpurps)
            
            #주차
            카테고리별_텍스트_찾기('form_park2', '주차 대수', 'number', building_pn)
            # driver.find_element(By.CSS_SELECTOR, '#form_item > div.form_box > div.box_contents > div.form_box_wrap.toji_basic > div.form_table > table > tbody > tr > td > div > div:nth-child(5) > div:nth-child(6) > div:nth-child(2) > div > input').send_keys(building_pn)
        
        if tr_target == '층호수':
            #옵션종류
            opt_elements = driver.find_elements(By.XPATH, '//*[@id="form_item"]/div[2]/div[1]/div[5]/div[2]/table/tbody/tr/td/div/div[6]/div[2]/div')
            for opt_elem in opt_elements:
                option = opt_elem.find_element(By.XPATH, './/label')
                for r_opt in room_options:
                    if option.text == r_opt : 
                        option.click()
                        # print(r_opt)
                        break  
         
        if tr_target != '토지':       
#건물정보
            
            #건물방향
            print('building_direction:',building_direction)
            # span_element = driver.find_element(By.XPATH, '//*[@id="form_item"]/div[2]/div[1]/div[6]/div[1]/span[2]')
            # if 'arch_open_btn on' in span_element.get_attribute('class'):
            #     print("현재 'arch_open_btn on' 상태입니다.")
            #     # pyautogui.alert('체크 ㄱㄱ')
            #     if building_direction != '':
            #         clickList('#tab1 > table > tbody > tr > td > div > div:nth-child(1) > div.con_box.b_direction.b_direction_0 > div:nth-child(2) > div', building_direction) #방향 
            #         driver.find_element(By.XPATH, '//*[@id="b_direction_desc_0"]').send_keys('주출입문') #방향기준 
        
#토지정보        
        if tr_target == '토지':
            # 쉼표로 문자열을 분리하고 공백을 제거
            jibun_list = [jibun.strip() for jibun in land_jibung.split(',')]   
            jibun_num = len(jibun_list)
            if jibun_num > 1 :
                for _ in range(jibun_num-1):
                    driver.find_element(By.XPATH, '//*[@id="form_toji_info"]/div[1]/div[1]/div/span[1]/span').click()
                extend_search_btns = driver.find_elements(By.XPATH, '//*[@id="form_toji_info"]/div[2]/div[1]/span')
                print("확장된 토지정보의 검색버튼의 개수:", len(extend_search_btns))
            land_count = 0
            for i in range(len(jibun_list)):
                if jibun_list[i] != location_lijibun :
                    jibun = jibun_list[i]
                    #거래대상필지 별로 정보입력
                    donglijibun = location_dongli+' '+jibun
                    print("동+지번:", donglijibun)
                    driver.find_element(By.XPATH, f'//*[@id="field_address_{land_count}"]').send_keys(donglijibun) #동+지번 입력
                    extend_search_btns[land_count].click()
                    # pyautogui.alert(f'//*[@id="field_address_{i}"]')
                    land_count += 1
            
            # pyautogui.alert("check!!") 
            # print("토지면적:", land_totarea)  
            # driver.find_element(By.CSS_SELECTOR, '#field_area_toji_0').send_keys(land_totarea)
            
            # print("대표지목:", representing_jimok)  
            # pyautogui.alert("대표지목check!!")
            # clickList('#toji_tbody_0 > tr > td > div > div:nth-child(1) > div.con_box.con_toji_select_box > div.field_land_aim_0 > div > button', representing_jimok)
            
            # print("대표용도:", representing_purpose) 
            # # pyautogui.alert("대표용도check!!")
            # clickList('#toji_tbody_0 > tr > td > div > div:nth-child(1) > div:nth-child(7) > div.field_land_use_0 > div > button', representing_purpose)
            
            # print("사용처:", representing_use) 
            # # pyautogui.alert("check!!")
            # driver.find_element(By.CSS_SELECTOR, '#toji_tbody_0 > tr > td > div > div:nth-child(1) > div.con_box.store_item > div:nth-child(2) > div > input[type=text]').send_keys(trading)
            # print("진입로:", land_roadsize) 
        
        #중개유형    
      
        # if 'brData' in data:
        #     brData = data['brData']
        #     for room_info in brData:
        #         # 여기서 decode는 필요에 따라 사용
        #         room_number = room_info['bri_num'].decode('utf-8') if isinstance(room_info['bri_num'], bytes) else room_info['bri_num']
        #         print(room_number)
        #     pyautogui.alert('확인' + str(len(brData)))
        # else:
        #     print("brData 키가 데이터에 없습니다.")
        #     pyautogui.alert("brData 키가 데이터에 없습니다.")              
#수익률정보
        if trading != '':
            if tr_target == '건물' and len(brData)>0:
                print("건물수익률 선택")
                structure_label = driver.find_element(By.CSS_SELECTOR,'label[data-type="structure"]')
                structure_label.click()
                if trading : driver.find_element(By.CSS_SELECTOR,'#p_sell_price').send_keys(str(trading)) #매매가 
                if building_loan : driver.find_element(By.CSS_SELECTOR,'#p_lease_price').send_keys(str(building_loan)) #융자금
                if building_loan_rate : driver.find_element(By.NAME, "p_lease_rate").send_keys(building_loan_rate) #대출금리
                if sum_deposit : driver.find_element(By.CSS_SELECTOR,'#p_gi_deposit').send_keys( str(sum_deposit)) #기보증금
                if sum_rent : driver.find_element(By.CSS_SELECTOR,'#p_total_rent_price').send_keys(str(sum_rent)) #총월세
                if sum_mmoney : driver.find_element(By.CSS_SELECTOR,'#p_total_mgr_price').send_keys(str(sum_mmoney)) #총관리비

                # class가 'rental_status_table rental_status_table_floor'인 table 내의 모든 tr 요소 찾기
                tr_rows = driver.find_elements(By.CSS_SELECTOR, ".rental_status_table.rental_status_table_floor tbody tr:has(td)")
                current_rows_length = len(tr_rows)
                print(f"현재행개수:{len(tr_rows)}")     
                sequence_index = 0        
                for room in brData:
                    bri_sequence = room['bri_sequence'] #순번
                    r_floor = room['bri_num'].decode('utf-8') #호수
                    r_area = room['bri_area'].decode('utf-8') #면적
                    r_sangho = room['bri_nmemo'].decode('utf-8') #상호
                    r_price_deposit = room['bri_deposit'].decode('utf-8') #보증금
                    r_price_month_rent = room['bri_rent'].decode('utf-8') #월세
                    r_price_manage = room['bri_mmoney'].decode('utf-8') #관리비
                    r_etc = room['bri_etc'].decode('utf-8') #비고
                    print(f"1 bri_sequence:{room['bri_sequence']}, len(tr_rows):{str(len(tr_rows))}")
                    print("bri_num:",room['bri_num'].decode('utf-8'))
                    
                    
                    if bri_sequence > len(tr_rows):
                    # if not 입력행:
                        print(f"{bri_sequence}번째 행추가")
                        # pyautogui.alert(f'{bri_sequence}번째 행추가 버튼위치index:{sequence_index}')
                        행추가버튼 = driver.find_element(By.CSS_SELECTOR, f".rental_status_table.rental_status_table_floor tbody tr td span[class='btn btn_plus']")
                        행추가버튼.click()
                        # # 새로운 행이 추가될 때까지 기다림
                        # WebDriverWait(driver, 10).until(
                        #     lambda driver: len(driver.find_elements(By.CSS_SELECTOR, ".rental_status_table.rental_status_table_floor tbody tr")) == len(tr_rows) + 2
                        # )
                        # time.sleep(1)
                        # 최신 tr_rows를 다시 가져옴
                        tr_rows = driver.find_elements(By.CSS_SELECTOR, ".rental_status_table.rental_status_table_floor tbody tr:has(td)")
                        print(f"2 bri_sequence:{room['bri_sequence']}, len(tr_rows):{str(len(tr_rows))}")                     
                    # else:
                    #     # pyautogui.alert(f'{bri_sequence}번째 입력행이 존재합니다.')
                    #     입력행 = tr_rows[bri_sequence-1]
                        

                    
                    # # 현재 행에 데이터 입력
                    # if bri_sequence > current_rows_length:
                    #     input_index = int((current_rows_length+(len(tr_rows)-current_rows_length)/2) - 1)
                    # else:
                    #     input_index = bri_sequence - 1
                    input_index = bri_sequence - 1    
                    print(f"bri_sequence:{bri_sequence} 입력행의 input_index:{input_index}")
                    입력행 = tr_rows[input_index]
                    # 데이터 입력 매핑
                    data_mapping = {
                        "r_floor[]": r_floor,
                        "r_area[]": r_area,
                        "r_sangho[]": r_sangho,
                        "r_price_deposit[]": r_price_deposit,
                        "r_price_month_rent[]": r_price_month_rent,
                        "r_price_manage[]": r_price_manage,
                        "r_etc[]": r_etc
                    }  
                    
                    print(f"sequence_index:{sequence_index} bri_sequence:{bri_sequence} data_mapping:",data_mapping) 
                    for key, value in data_mapping.items():
                        try:
                            input_element = 입력행.find_element(By.CSS_SELECTOR, f"td input[name='{key}']")
                            input_element.clear()
                            input_element.send_keys(value)
                            print(f"{bri_sequence}번째 Data for {key} ({value}) successfully entered.")
                        except Exception as e:
                            print(f"Input field for {key} not found in sequence {bri_sequence}.")   
                    마지막입력행 = 입력행
                    sequence_index += 1               
                    # pyautogui.alert(f'{bri_sequence}번째행 입력완료 sequence_index:{sequence_index} len(tr_rows):{str(len(tr_rows))}')
                # pyautogui.alert(f'{sequence_index}개 호실정보 입력완료')
#상세정보
        object_detail = '[ 매 물 기 본 정 보 ]'
        if trading != '':
            object_detail += '<p>' + f'● 매매금액: {숫자한글로금액변환(trading)}'  + '</p>'
            if tr_target == '건물':
                object_detail += '<p>' + f'● 건물 주용도: {building_purpose}'  + '</p>'
                object_detail += '<p>' + f'● 건물 준공일: {building_usedate}'  + '</p>'
                if sum_deposit == '':
                    print("보증금이 공백입니다.")
                else:
                    print("보증금이 존재합니다.")
                object_detail += ('<p>' + f'● 총보증금: {숫자한글로금액변환(sum_deposit)}' + '</p>') if str(sum_deposit) != '' else '' 
                if sum_rent != '':
                    object_detail += ('<p>' + f'● 총월세: {숫자한글로금액변환(sum_rent)}' + '</p>') if str(sum_rent) != '' else ''     
            object_detail += '<p>' + f'● 용도지역: {representing_purpose}'  + '</p>'        
            if main_area : object_detail += ('<p>' + f'● 대지면적: {land_totarea}㎡ (약{changeToPyeong(land_totarea)}평)' + '</p>') if float(main_area) > 0 else ''
            object_detail += ('<p>' + f'● 대표지목: {representing_jimok}' + '</p>') if representing_jimok != '' else ''
                
        elif deposit1 != '':
            object_detail += '<p>' + f'● 보증금: {deposit1}만원' + '</p>'
            if rent1 != '':
                object_detail += '<p>' + f'● 월세: {rent1}만원' + '</p>'
            if manager == '별도' and float(mmoney) > 0:
                object_detail += '<p>' + f'● 관리비: {mmoney}만원' + '</p>'
            # if premium_exist == '있음' & premium > 0:
            #     object_detail += f'● 권리금: {premium}만원'
        if object_type == '주거용' and tr_target == '층호수':
            object_detail += (('<p>' + f'● 방: {int(float(room_rcount))}개')+(f' / 욕실:{room_bcount}개' if float(room_rcount) > 0 else '') + '</p>') if float(room_rcount) > 0 else ''
        else:
            if tr_target == '건물':
                object_detail += ('<p>' + f'● 총층: {str(building_grndflr-building_ugrndflr)}층 (지상{str(building_grndflr)}층 / 지하{str(building_ugrndflr)}층)' + '</p>') if int(building_grndflr-building_ugrndflr) > 0 else ''
            elif tr_target == '층호수':
                object_detail += ('<p>' + f'● 면적: {main_area}㎡ (약{changeToPyeong(main_area)}평)' + '</p>') if float(main_area) > 0 else ''
            elif tr_target == '토지':
                object_detail += ('<p>' + f'● 대지면적: {land_totarea}㎡ (약{changeToPyeong(land_totarea)}평)' + '</p>') if float(land_totarea) > 0 else ''
                # pyautogui.alert(representing_jimok)
                object_detail += ('<p>' + f'● 대표지목: {representing_jimok}' + '</p>') if representing_jimok != '' else ''
                # pyautogui.alert(representing_purpose)
                object_detail += ('<p>' + f'● 용도지역: {representing_purpose}' + '</p>') if representing_purpose != '' else ''
                # pyautogui.alert(object_detail)
        
        object_detail += ('<p>' + f'● 옵션: {main_option}' + '</p>') if main_option != '' else ''
        object_detail += '<p>' + f'● 위치: ' + '</p>'
        
        object_detail += '<p>&nbsp</p>' + '<p>' + '[ 매 물 주 요 특 징 ]' + '</p>'
        
        def nl2br(text):
            return text.replace('\n', '<br>') if text else ''
        object_detail += ('<p>' + f'ㅇ {nl2br(land_memo)}' + '</p>') if land_memo else ''
        if tr_target != '토지':
            object_detail += ('<p>' + f'ㅇ {nl2br(building_trmemo)}' + '</p>') if building_trmemo else ''
            object_detail += ('<p>' + f'ㅇ {nl2br(building_memo)}' + '</p>') if building_memo else ''
        if tr_target == '층호수':
            object_detail += ('<p>' + f'ㅇ {nl2br(room_memo)}' + '</p>') if room_memo else ''


        object_detail += '<p>' + 'ㅇ&nbsp;' + '</p>'
        object_detail += '<p>' + 'ㅇ&nbsp;' + '</p>'
        
        print("object_detail: " + object_detail)
        # 상세정보 문자열을 HTML 포맷으로 조작
        detail = '<p></p>'  # 시작을 위한 빈 <p> 태그
        # 여기서 object_detail은 앞에서 선언된 변수로, 실제 내용이 들어가는 부분입니다.
        detail += '<p>&nbsp</p>' + '<p>' + object_detail + '</p>'
        detail += '<p>----------------------------------------------------------------------------------------------</p>'
        detail += '<p>◈아직 등록되지 않은 매물도 다수 보유중이니 더 많은 매물을 안내받길 원하신다면 문의주시기 바랍니다.</p>'
        detail += '<p>◈실시간 거래로 인하여 해당물건이 없을 수 있으니 반드시 문의바랍니다.</p>'
        detail += '<p>※렌트프리, 옵션, 협의사항 등 끝까지 도와드리겠습니다.</p>'
        detail += '<p>----------------------------------------------------------------------------------------------</p>'

        # iframe으로 스위치
        iframe = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//div/iframe"))
        )
        driver.switch_to.frame(iframe)   
                 
        # 텍스트 영역 찾기 및 텍스트 입력
        # text_area = driver.find_element(By.XPATH, '//body/p')
        text_area = driver.find_element(By.XPATH, '//body')
        # text_area.send_keys(detail)  
        상세정보script = """
        var textarea = arguments[0];
        var value = arguments[1];
        textarea.innerHTML  = value;
        var event = new Event('input', { bubbles: true });
        textarea.dispatchEvent(event);
        """
        driver.execute_script(상세정보script, text_area, detail)          
         
        # iframe에서 스위치 되돌리기
        driver.switch_to.default_content()      
        
        #비밀메모
        print("비밀메모:", basic_secret)    
        # driver.find_element(By.XPATH, '//*[@id="form_item"]/div[2]/div[1]/div[12]/div[1]/div[2]/table/tbody/tr/td/div/div[3]/div[2]/textarea').send_keys(basic_secret)
        비밀메모요소들 = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "textarea_content")]/textarea'))
        )
        보이는_비밀메모요소들 = [비밀메모요소 for 비밀메모요소 in 비밀메모요소들 if 비밀메모요소.is_displayed()]
        print(f'카테고리({보이는_비밀메모요소들})의 개수' + str(len(보이는_비밀메모요소들)))
        # print("비밀메모요소들 개수:"+str(len(보이는_비밀메모요소들)))
        if len(보이는_비밀메모요소들) == 1:
            보이는_비밀메모요소들[0].send_keys(basic_secret)

        #물건사진 폴더열기
        main_dir = 'Z:\\업무자료\\4사진자료&이미지자료(외부유출금지)\\1주거용물건, 상업용물건\\'
        path_dir = main_dir + data['folderPath'] #'경기도\\오산시\\궐동\\654-9\\썬플라워\\1층\\1층'
        print(path_dir)
        try:
            os.startfile(path_dir)
        except:
            print('폴더열기 에러')        
        
        
    else:
        print(f"오부사{object_code_new} 매물수정 시작")
        driver.get(f'https://osan-bns.com/admin_item/edit/{object_code_new}?page=1') #매물등록화면으로 전환
        
        # 수익률정보
        #건물수익률이 선택된 상태(active존재유무)인지 확인하기
        structure_label = driver.find_element_by_css_selector('label[data-type="structure"]')
        # 'active' 클래스가 있는지 확인
        is_active = 'active' in structure_label.get_attribute('class').split()
        print("Is 'active' class present:", is_active)    
    
    
    

    
    
    
    
    
        
    pyautogui.alert('작업종료 할래?')
    driver.quit()     