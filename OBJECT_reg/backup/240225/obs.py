from selenium import webdriver
from selenium.webdriver import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

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
        driver.find_element(By.XPATH, f'{select_xpath}').click() #선택 클릭
        
        select_element = driver.find_element(By.XPATH, f'{select_xpath}')
        
        # Select 객체를 생성하고 select 엘리먼트를 래핑합니다.
        select = Select(select_element)
        try:
            select.select_by_visible_text(value) #일치하는 텍스트 선택하기
        except Exception as e:
            print("선택 오류:", str(e))
            
    def clickList(btn_selector, value):
        time.sleep(0.3)
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
        #     li_elements = div_element.find_elements(By.XPATH, './/li') # div 태그의 자식 li 태그 선택
        #     print(len(li_elements))
        #     for li_element in li_elements:
        #         span_element = li_element.find_element(By.XPATH, './/a/span[1]')
        #         print(li_element, span_element.text)
        #         if span_element.text == value:
        #             li_element.click()
        #             break            
        except Exception as e:
            print("선택 오류:", str(e))
            
    def 숫자한글로금액변환(숫자금액):
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
        building_direction = data['buildingData']['building_direction'] #건물방향
        # building_usedate = str(data['buildingData']['building_usedate']) #준공일
        building_pn = data['buildingData']['building_pn'] #주차
        building_loan = data['buildingData']['building_loan'].decode('utf-8') #대출
        building_option = data['buildingData']['building_option'] #건물옵션
        sum_deposit = data['buildingData']['sum_deposit'].decode('utf-8') #총보증금
        sum_rent = data['buildingData']['sum_rent'].decode('utf-8') #총월세
        sum_mmoney = data['buildingData']['sum_mmoney'].decode('utf-8') #총관리비
        secret_3 = '' if data['buildingData']['building_memo'] == '' else data['buildingData']['building_memo'] + Keys.ENTER
        basic_secret = location_detail + Keys.ENTER + basic_secret +secret_3
        main_area = building_totarea
        main_option = building_option
   
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
        room_option = data['roomData']['room_option'] #호실옵션
        room_options = room_option.split(',') #호실옵션리스트
        flr_strct = data['flrData']['flr_strct'] #층주구조
        secret_4 = '' if data['roomData']['room_memo'] == '' else data['roomData']['room_memo'] + Keys.ENTER
        basic_secret += secret_4    
        main_area = room_area1
        main_option = room_option
        
    main_area_pyeong = str(int(float(main_area)/3.305785)) if main_area != '' else ''
        
    # basic_secret = "https://obangkr.cafe24.com/web/request/request_view/view_give_request_detail.php?request_code="+request_code
    
    # ChromeDriver 경로 설정
    driver = webdriver.Chrome(options=options)
    # driver = webdriver.Chrome('/chromedriver', options=options)
    # driver = webdriver.Chrome(ChromeDriverManager().install())

    # URL 열기
    driver.maximize_window()
    driver.get('https://osan-bns.com/admin_item/insert')
    # time.sleep(0.5)
    driver.find_element(By.XPATH, '//*[@id="email"]').send_keys(ad_email)
    driver.find_element(By.XPATH, '//*[@id="password"]').send_keys(ad_pw)
    driver.find_element(By.XPATH, '//*[@id="admin_login"]/button').click()
    
    driver.implicitly_wait(10)   

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="admin_wrap"]/header/div[1]/div'))) #헤더버튼이 나타날때까지 대기
    
    #매물 등록할지 수정할지 결정(새홈번호 6자리=>매물등록, 5자리=>매물수정)
    if len(object_code_new) != 5:
        print("신규매물등록 시작")
        driver.get('https://osan-bns.com/admin_item/insert') #매물등록화면으로 전환
        
        #등록폼 선택
        if object_type == '상업용':
            driver.find_element(By.XPATH, '//*[@id="form_item"]/div[1]/table/tbody/tr/td/div/div[1]').click()
        elif object_type == '주거용':
            driver.find_element(By.XPATH, '//*[@id="form_item"]/div[1]/table/tbody/tr/td/div/div[2]').click() 
        elif object_type == '공업용':
            driver.find_element(By.XPATH, '//*[@id="form_item"]/div[1]/table/tbody/tr/td/div/div[4]').click() 
        elif object_type == '토지':
            driver.find_element(By.XPATH, '//*[@id="form_item"]/div[1]/table/tbody/tr/td/div/div[5]').click() 
           
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
                if location_si == si.text :
                    si.click()
                    break
        if location_dong != '궐동':
            driver.find_element(By.XPATH, '//*[@id="dong_id"]').click() 
            dong_elements = driver.find_elements(By.XPATH, '//*[@id="dong_id"]/option')
            for dong in dong_elements:
                # print(location_dong)
                # print(dong.text)
                if location_dong == dong.text :
                    # print(location_dong)
                    dong.click()
                    break
        # time.sleep(0.5)
        driver.find_element(By.XPATH, '//*[@id="address_detail"]').send_keys(location_lijibun) #상세주소 입력
        # time.sleep(3)
        driver.find_element(By.XPATH, '//*[@id="address_detail"]').send_keys(Keys.ENTER) #지도위치이동
        # time.sleep(1)
        # driver.find_element(By.XPATH, '//*[@id="form_item"]/div[2]/div[1]/div[1]/div[2]/table/tbody/tr/td[1]/div/div[1]/div[3]/span').click() #위치이동
        if object_type != '토지':
            pyautogui.alert("건물 선택후 확인버튼을 눌러주세요")
        else:
            driver.find_element(By.XPATH, '//*[@id="form_item"]/div[2]/div[1]/div[1]/div[2]/table/tbody/tr/td[1]/div/div[3]/div[2]/label[3]').click()  #상세주소 표시방법으로 위치숨기기 선택
        
        #매물정보
        if tr_target == '층호수' and room_status == '공실' :
            driver.find_element(By.XPATH, '//*[@id="form_item"]/div[2]/div[1]/div[2]/div[1]/div/div[2]/label').click() #공실 체크박스 체크
        elif tr_target == '건물' and object_type == '주거용':
            driver.find_element(By.XPATH, '//*[@id="form_item"]/div[2]/div[1]/div[2]/div[2]/table/tbody/tr/td/div/table/tbody/tr/th[1]/div/div[2]/div/table[1]/tbody/tr/td/div/label[4]').click() #1차그룹 통건물 클릭
        
        #매물종류
        if tr_target == '토지':
            click_item_in_group('1차 그룹', '토지')
            click_item_in_group('2차 그룹', '대지') if representing_jimok=='대' else click_item_in_group('2차 그룹', '농지임야')
            # pyautogui.alert(representing_jimok) 

        #금액정보
        if tr_target != '층호수' and tr_target != '토지' : driver.find_element(By.XPATH, '//*[@id="item_range"]/div[2]/label[2]/span').click() #거래범위 전체선택
        #거래유형
        if trading != '' and trading != '0' :
            driver.find_element(By.XPATH, '//*[@id="form_item"]/div[2]/div[1]/div[3]/div[2]/table/tbody/tr/td/div/div[2]/table/tbody/tr/th[1]/div/div[2]/div/label[3]').click() #매매버튼
            driver.find_element(By.XPATH, '//*[@id="form_item"]/div[2]/div[1]/div[3]/div[2]/table/tbody/tr/td/div/div[2]/table/tbody/tr/th[2]/div/div[2]/div[3]/input').send_keys(trading) #매매가
            # pyautogui.alert("272 go?")
            if tr_target == '건물': 
                driver.find_element(By.XPATH, '//*[@id="form_item"]/div[2]/div[1]/div[3]/div[2]/table/tbody/tr/td/div/div[2]/table/tbody/tr/th[2]/div/div[2]/div[6]/input').send_keys(str(building_loan)) #융자금
                if sum_deposit != '':
                    driver.find_element(By.XPATH, '//*[@id="form_item"]/div[2]/div[1]/div[3]/div[2]/table/tbody/tr/td/div/div[2]/table/tbody/tr/th[2]/div/div[2]/div[22]/input').send_keys(str(sum_deposit)) #총보증금
                    driver.find_element(By.XPATH, '//*[@id="form_item"]/div[2]/div[1]/div[3]/div[2]/table/tbody/tr/td/div/div[2]/table/tbody/tr/th[2]/div/div[2]/div[23]/input').send_keys(str(sum_rent)) #총월세
        else :
            if deposit1 != '' and deposit1 != '0' :
                if rent1 != '' and rent1 != '0':
                    driver.find_element(By.CSS_SELECTOR, '#form_item > div.form_box > div.box_contents > div:nth-child(3) > div.form_table > table > tbody > tr > td > div > div.con_box.con_box_wrap.no_villa_box.price_box > table > tbody > tr > th.price_types > div > div:nth-child(2) > div > label.btn.btn-default.btn_type.btn_month_rent.active').click() #월세버튼
                    # pyautogui.alert("ㄱㄱ?")
                    driver.find_element(By.XPATH, '//*[@id="form_item"]/div[2]/div[1]/div[3]/div[2]/table/tbody/tr/td/div/div[2]/table/tbody/tr/th[2]/div/div[2]/div[10]/input').send_keys(deposit1) #월세보증금
                    driver.find_element(By.XPATH, '//*[@id="form_item"]/div[2]/div[1]/div[3]/div[2]/table/tbody/tr/td/div/div[2]/table/tbody/tr/th[2]/div/div[2]/div[11]/input').send_keys(rent1) #월세
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
        if manager == '별도': 
            driver.find_element(By.XPATH, '//*[@id="form_item"]/div[2]/div[1]/div[3]/div[2]/table/tbody/tr/td/div/div[4]/div[2]/div[2]/div[1]/label[1]').click() #관리비버튼
            driver.find_element(By.XPATH, '//*[@id="form_item"]/div[2]/div[1]/div[3]/div[2]/table/tbody/tr/td/div/div[4]/div[2]/div[2]/div[2]/div/input').send_keys(mmoney) #관리비
            driver.find_element(By.XPATH, '//*[@id="form_item"]/div[2]/div[1]/div[3]/div[2]/table/tbody/tr/td/div/div[4]/div[2]/div[2]/div[3]/input').send_keys(mmemo) #관리비메모
            mItem_elements = driver.find_elements(By.XPATH, '//*[@id="form_item"]/div[2]/div[1]/div[3]/div[2]/table/tbody/tr/td/div/div[4]/div[3]/div[2]/div')
            for mItem in mItem_elements:
                label_tag = mItem.find_element(By.TAG_NAME, 'label')
                mlist_items = mlist.split(',')
                for item in mlist_items:
                    if item == 'E/V관리': item = '엘리베이터' #연관 항목명으로 변경
                    if item == label_tag.text: label_tag.click() #관리비에 포함된 항목 체크
        # pyautogui.alert('315 gogo?')            
        #기본정보
        if object_type == '상업용':
            if tr_target == '층호수':
                #매물상태
                print('room_status:'+room_status)
                if room_status == '공실':
                    # print('공실진입 성공')
                    driver.find_element(By.XPATH, '//*[@id="form_item"]/div[2]/div[1]/div[5]/div[2]/table/tbody/tr/td/div/div[2]/div[1]/div[2]/div/label[3]').click() #비어있음 클릭
                elif room_status == '사용(임차인)':
                    driver.find_element(By.XPATH, '//*[@id="form_item"]/div[2]/div[1]/div[5]/div[2]/table/tbody/tr/td/div/div[2]/div[1]/div[2]/div/label[2]').click() #임대중 클릭
                elif room_status == '사용(주인)':
                    driver.find_element(By.XPATH, '//*[@id="form_item"]/div[2]/div[1]/div[5]/div[2]/table/tbody/tr/td/div/div[2]/div[1]/div[2]/div/label[1]').click() #직접 운영중 클릭
        # pyautogui.alert('gogo?')
        if tr_target == '층호수':
            driver.find_element(By.CSS_SELECTOR, '#form_item > div.form_box > div.box_contents > div.form_box_wrap.toji_basic > div.form_table > table > tbody > tr > td > div > div.con_box.con_box_wrap.static_factory_o > div.con_box.roombath > div:nth-child(2) > div:nth-child(1) > input').send_keys(room_rcount) #방수
            driver.find_element(By.CSS_SELECTOR, '#form_item > div.form_box > div.box_contents > div.form_box_wrap.toji_basic > div.form_table > table > tbody > tr > td > div > div.con_box.con_box_wrap.static_factory_o > div.con_box.roombath > div:nth-child(2) > div.input-group.bath > input').send_keys(room_bcount) #욕실수
            clickList('#form_item > div.form_box > div.box_contents > div.form_box_wrap.toji_basic > div.form_table > table > tbody > tr > td > div > div.con_box.con_box_wrap.static_factory_o > div.con_box.direction > div:nth-child(2) > div', room_direction) #방향
            print('direction_stn:'+direction_stn)
            driver.find_element(By.CSS_SELECTOR, '#form_item > div.form_box > div.box_contents > div.form_box_wrap.toji_basic > div.form_table > table > tbody > tr > td > div > div.con_box.con_box_wrap.static_factory_o > div.con_box.direction > div:nth-child(2) > input').send_keys(direction_stn) #방향기준 
            clickList('#form_item > div.form_box > div.box_contents > div.form_box_wrap.toji_basic > div.form_table > table > tbody > tr > td > div > div.con_box.con_box_wrap.static_factory_o > div.con_box.heat > div:nth-child(2) > div', '개별') #난방종류
            #입주가능일
            if room_status == '공실':
                selectOption('//*[@id="enter_date_option"]', '즉시입주가능')
            elif room_status == '사용(임차인)':
                selectOption('//*[@id="enter_date_option"]', '가까운 시일내 협의')
            else:
                selectOption('//*[@id="enter_date_option"]', '즉시입주가능')
            
            #면적
            if room_area2 != '' :
                driver.find_element(By.CSS_SELECTOR, '#area_law').send_keys(room_area2) #공급면적
            if room_area1 != '' :    
                driver.find_element(By.CSS_SELECTOR, '#area_real').send_keys(room_area1) #전용면적
            
            #층정보
            print('room_floor:'+basic_totflr,'room_floor:'+room_floor)
        
        if tr_target != '토지' :
            if building_type != '집합':
                if tr_target == '건물' :
                    driver.find_element(By.CSS_SELECTOR, '#floor_current').send_keys(building_ugrndflr) #지하층
                    driver.find_element(By.CSS_SELECTOR, '#form_item > div.form_box > div.box_contents > div.form_box_wrap.toji_basic > div.form_table > table > tbody > tr > td > div > div:nth-child(5) > div.con_box.floor > div:nth-child(3) > div:nth-child(4) > input').send_keys(building_grndflr) #지상층
                if tr_target == '층호수' : 
                    driver.find_element(By.CSS_SELECTOR, '#floor_current').send_keys(room_floor) #해당층
                    driver.find_element(By.CSS_SELECTOR, '#form_item > div.form_box > div.box_contents > div.form_box_wrap.toji_basic > div.form_table > table > tbody > tr > td > div > div:nth-child(5) > div.con_box.floor > div:nth-child(3) > div:nth-child(4) > input').send_keys(basic_totflr) #총층수
        
        if tr_target == '건물' :
            #주용도
            print('flr_mainpurps:',flr_mainpurps)
            # pyautogui.alert('gogo?')
            driver.find_element(By.CSS_SELECTOR, '#main_yongdo').send_keys(flr_mainpurps)
            
            #주차
            driver.find_element(By.CSS_SELECTOR, '#form_item > div.form_box > div.box_contents > div.form_box_wrap.toji_basic > div.form_table > table > tbody > tr > td > div > div:nth-child(5) > div:nth-child(6) > div:nth-child(2) > div > input').send_keys(building_pn)
        
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
            span_element = driver.find_element(By.XPATH, '//*[@id="form_item"]/div[2]/div[1]/div[6]/div[1]/span[2]')
            if 'arch_open_btn on' in span_element.get_attribute('class'):
                print("현재 'arch_open_btn on' 상태입니다.")
                # pyautogui.alert('체크 ㄱㄱ')
                clickList('#tab1 > table > tbody > tr > td > div > div:nth-child(1) > div.con_box.b_direction.b_direction_0 > div:nth-child(2) > div', building_direction) #방향 
                driver.find_element(By.XPATH, '//*[@id="b_direction_desc_0"]').send_keys('주출입문') #방향기준 
        
        #토지정보        
        if tr_target == '토지':
            # 쉼표로 문자열을 분리하고 공백을 제거
            jibun_list = [jibun.strip() for jibun in land_jibung.split(',')]   
            jibun_num = len(jibun_list)
            if jibun_num > 1 :
                for _ in range(jibun_num-1):
                    driver.find_element(By.XPATH, '//*[@id="form_item"]/div[2]/div[1]/div[7]/div/div[1]/span[2]').click()
                extend_search_btns = driver.find_elements(By.XPATH, '//*[@id="toji_tbody"]/tr/td/div/div[1]/div[1]/div[2]/div/span')
                print("확장된 토지정보의 검색버튼의 개수:", len(extend_search_btns))
            land_count = 0
            for i in range(len(jibun_list)):
                land_count += 1
                if jibun_list[i] != location_lijibun :
                    jibun = jibun_list[i]
                    #거래대상필지 별로 정보입력
                    donglijibun = location_dongli+' '+jibun
                    print("동+지번:", donglijibun) 
                    driver.find_element(By.XPATH, f'//*[@id="field_address_{land_count}"]').send_keys(donglijibun) #동+지번 입력
                    extend_search_btns[land_count-1].click()
                    # pyautogui.alert(f'//*[@id="field_address_{i}"]')
            
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
            
        if  trading != '':
            #수익률정보
            if tr_target != '토지':
                driver.find_element(By.CSS_SELECTOR, '#form_item > div.form_box > div.box_contents > div.form_box_wrap.profit_store > div.form_title > span.profit_open_btn > span').click() #정보입력 클릭
            if tr_target == '건물':
                driver.find_element(By.CSS_SELECTOR, '#form_item > div.form_box > div.box_contents > div.form_box_wrap.profit_store > div.form_table > table > tbody > tr > td > div > div.con_box.input_profit_type > div.con_box > div > label.btn.btn-default.profit_type_building').click() #건물수익률 클릭
                driver.find_element(By.CSS_SELECTOR, '#p_sell_price').send_keys(trading) #매매가 입력 
                # driver.find_element(By.CSS_SELECTOR, '#p_lease_price').send_keys(loan) #융자금 입력
                # driver.find_element(By.CSS_SELECTOR, '#p_gi_deposit').send_keys() #기보증금 입력
                # driver.find_element(By.CSS_SELECTOR, '#p_total_rent_price').send_keys() #총월세 입력
                # driver.find_element(By.CSS_SELECTOR, '#p_sell_price').send_keys() #총관리비 입력
                # driver.find_element(By.CSS_SELECTOR, '#p_total_mgr_price').send_keys() #대출금리 입력
            elif tr_target == '층호수' and object_type != '주거용':
                driver.find_element(By.CSS_SELECTOR, '#form_item > div.form_box > div.box_contents > div.form_box_wrap.profit_store > div.form_table > table > tbody > tr > td > div > div.con_box.input_profit_type > div.con_box > div > label.btn.btn-default.profit_type_store').click() #상가수익률 클릭
        #중개유형
        
        #상세정보
        object_detail = '[ 매 물 기 본 정 보 ]'
        if trading != '':
            object_detail += Keys.ENTER + f'● 매매금액: {숫자한글로금액변환(trading)}' 
            if tr_target == '건물':
                if sum_deposit == '':
                    print("보증금이 공백입니다.")
                else:
                    print("보증금이 존재합니다.")
                object_detail += (Keys.ENTER + f'● 총보증금: {숫자한글로금액변환(sum_deposit)}') if str(sum_deposit) != '' else '' 
                if sum_rent != '':
                    object_detail += (Keys.ENTER + f'● 총월세: {숫자한글로금액변환(sum_rent)}') if str(sum_rent) != '' else ''             
                
        elif deposit1 != '':
            object_detail += Keys.ENTER + f'● 보증금: {deposit1}만원' 
            if rent1 != '':
                object_detail += Keys.ENTER + f'● 월세: {rent1}만원'
            if manager == '별도' and float(mmoney) > 0:
                object_detail += Keys.ENTER + f'● 관리비: {mmoney}만원'
            # if premium_exist == '있음' & premium > 0:
            #     object_detail += f'● 권리금: {premium}만원'
        if object_type == '주거용' and tr_target == '층호수':
            object_detail += ((Keys.ENTER + f'● 방: {int(float(room_rcount))}개')+(f' / 욕실:{room_bcount}개' if float(room_rcount) > 0 else '')) if float(room_rcount) > 0 else ''
        else:
            if tr_target == '건물':
                object_detail += (Keys.ENTER + f'● 총층: {str(building_grndflr-building_ugrndflr)}층 (지상{str(building_grndflr)}층 / 지하{str(building_ugrndflr)}층)') if int(building_grndflr-building_ugrndflr) > 0 else ''
            elif tr_target == '층호수':
                object_detail += (Keys.ENTER + f'● 면적: {main_area}㎡ (약{main_area_pyeong}평)') if float(main_area) > 0 else ''
            elif tr_target == '토지':
                object_detail += (Keys.ENTER + f'● 대지면적: {land_totarea}㎡ (약{main_area_pyeong}평)') if float(main_area) > 0 else ''
                # pyautogui.alert(representing_jimok)
                object_detail += (Keys.ENTER + f'● 대표지목: {representing_jimok}') if representing_jimok != '' else ''
                # pyautogui.alert(representing_purpose)
                object_detail += (Keys.ENTER + f'● 용도지역: {representing_purpose}') if representing_purpose != '' else ''
                # pyautogui.alert(object_detail)
        
        object_detail += (Keys.ENTER + f'● 옵션:{main_option}') if main_option != '' else ''
        object_detail += Keys.ENTER + f'● 위치: '
        
        object_detail += Keys.ENTER + Keys.ENTER + '[ 매 물 주 요 특 징 ]'
        object_detail += Keys.ENTER + 'ㅇ '
        object_detail += Keys.ENTER + 'ㅇ '
        
        print("object_detail: " + object_detail)
        detail = ''
        # detail += '빠른 상담받는 법 ☞ "오방"사이트에서 매물번호가 "' + obang_code + '"인 매물을 보고 문의주셨다고 말씀해주세요~!!' + Keys.ENTER
        # detail += Keys.ENTER + '📋상세정보'
        detail += Keys.ENTER + object_detail + Keys.ENTER
        detail += Keys.ENTER + '----------------------------------------------------------------------------------------------'
        detail += Keys.ENTER + '◈아직 등록되지 않은 매물도 다수 보유중이니 더 많은 매물을 안내받길 원하신다면 문의주시기 바랍니다.'
        detail += Keys.ENTER + '◈실시간 거래로 인하여 해당물건이 없을 수 있으니 반드시 문의바랍니다.'
        detail += Keys.ENTER + '※렌트프리, 옵션, 협의사항 등 끝까지 도와드리겠습니다.'
        # detail += Keys.ENTER + '📞010-8631-4392'
        # detail += Keys.ENTER + '📌홈페이지: osanbang.com'
        detail += Keys.ENTER + '----------------------------------------------------------------------------------------------' + Keys.ENTER
        # iframe으로 스위치
        iframe = driver.find_element(By.XPATH, '//*[@id="cke_1_contents"]/iframe')
        driver.switch_to.frame(iframe)            
        # 텍스트 영역 찾기 및 텍스트 입력
        text_area = driver.find_element(By.XPATH, '//body/p')
        text_area.send_keys(detail)    
        # iframe에서 스위치 되돌리기
        driver.switch_to.default_content()      
        
        #비밀메모
        print("비밀메모:", basic_secret)    
        driver.find_element(By.XPATH, '//*[@id="form_item"]/div[2]/div[1]/div[12]/div[1]/div[2]/table/tbody/tr/td/div/div[3]/div[2]/textarea').send_keys(basic_secret)
        
        

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
    
    
    
    

    
    
    
    
    
        
    pyautogui.alert('작업종료 할래?')
    driver.quit()     