from selenium import webdriver
from selenium.webdriver import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.chrome.options import Options

import pyautogui 
import time

# # ChromeDriver 경로 설정
# driver = webdriver.Chrome('/chromedriver')


def macro(data, user):
    errarr = []
    
    # options = None
    options = Options()
    options.add_experimental_option("detach", True) # 창이 자동으로 닫히지 않게 해줌
    options.add_experimental_option("excludeSwitches", ["enable-automation"]) #브라우저에 나타나는 자동화라는 메세지 제거
    options.add_argument("--disable-blink-features=AutomationControlled") #봇으로 인식안하게 하는 옵션
    
    # 현재 날짜 출력
    import datetime
    current_date = datetime.date.today()
    formatted_date = current_date.strftime("%Y-%m-%d")
    
    admin_name = data['adminData']['admin_name']
    
    tr_target = data['writeData']['tr_target']
    location_do = data['landData']['land_do']
    location_si = data['landData']['land_si']
    location_dong = data['landData']['land_dong']

    location_lijibun = (data['type_path'] + data['landData']['land_jibun']) if data['landData']['land_li'] == '' else (data['landData']['land_li'] + data['type_path'] + data['landData']['land_jibun'])
    location_dongli = (data['landData']['land_dong'] + data['type_path'] + data['landData']['land_jibun']) if data['landData']['land_li'] == '' else location_lijibun
    location_detail = location_dongli

    request_code = data['writeData']['request_code'] #의뢰번호
    obang_code = data['writeData']['obang_code'] #오방매물번호
    obinfo_type = ''
    obinfo_type1 = data['writeData']['object_type1']
    obinfo_type2 = data['writeData']['object_type2']
    # if data['writeData']['object_type'] == '주거용' and tr_target == '층호수':
    #     if data['roomData']['room_rcount'] == '1':
    #         obinfo_type = '원룸'
    #     elif data['roomData']['room_rcount'] >= '2':
    #         obinfo_type = '투룸/쓰리룸+'
    # elif data['writeData']['object_type'] == '상업용':
    #     obinfo_type = '상가/사무실'
    obinfo_trading = data['writeData']['trading'] #매매금액    
    obinfo_deposit1 = data['writeData']['deposit1'] #보증금1
    obinfo_deposit2 = data['writeData']['deposit2'] #보증금2
    obinfo_deposit3 = data['writeData']['deposit3'] #보증금3
    obinfo_rent1 = data['writeData']['rent1'] #월세1
    obinfo_rent2 = data['writeData']['rent2'] #월세2
    obinfo_rent3 = data['writeData']['rent3'] #월세3
    obinfo_ttype = data['writeData']['object_ttype'] #거래종류

    basic_manager = data['writeData']['manager'] #관리비 별도/포함/미확인
    basic_mmoney = int(data['writeData']['mmoney'])*10000 if data['writeData']['mmoney'] != '' else '' #관리비
    basic_mlist = data['writeData']['mlist'] #관리비포함내역
    basic_mmemo = data['writeData']['mmemo'] #관리비메모
    add_warmer = '' #data['writeData']['add_warmer'] 난방
    add_rdate = str(data['writeData']['rdate']) #입주일
    secret_1 = '' if data['writeData']['tr_memo'] == '' else data['writeData']['tr_memo'] + Keys.ENTER
    secret_2 = '' if data['landData']['land_memo'] == '' else data['landData']['land_memo'] + Keys.ENTER
    basic_secret = secret_1 + secret_2 #비밀메모
    land_totarea = data['landData']['land_totarea']#대지면적
    land_option = data['landData']['land_option']#토지옵션

    if tr_target == '건물' or tr_target == '층호수':
        location_building = '' if data['buildingData']['building_name'] == '' else ' ' + data['buildingData']['building_name']
        location_detail += location_building
        basic_totflr = str(int(data['buildingData']['building_grndflr']) + int(data['buildingData']['building_ugrndflr'])) #전체층
        building_usedate = str(data['buildingData']['building_usedate']) #준공일
        building_pn = data['buildingData']['building_pn'] #주차
        secret_3 = '' if data['buildingData']['building_memo'] == '' else data['buildingData']['building_memo'] + Keys.ENTER
        basic_secret += secret_3
        building_archarea = data['buildingData']['building_archarea'] #건축면적
        building_totarea = data['buildingData']['building_totarea'] #연면적
        building_direction = data['buildingData']['building_direction'] #방향
        building_purpose = data['buildingData']['building_purpose'] #주용도
        building_elvcount = data['buildingData']['building_elvcount'] #승강기수
        building_option = data['buildingData']['building_option']#건물옵션
        tot_options = ",".join([land_option, building_option])

    if tr_target == '층호수':
        location_room = '' if data['roomData']['room_num'] == '' else ' ' + data['roomData']['room_num']
        location_detail += location_room
        basic_area1 = data['roomData']['room_area1'] #실면적
        basic_area2 = data['roomData']['room_area2'] #공급면적
        basic_rcount = data['roomData']['room_rcount'] #방수
        basic_bcount = data['roomData']['room_bcount'] #욕실수
        basic_floor = data['roomData']['room_floor'] #해당층
        add_options = data['roomData']['room_option'] #옵션선택
        room_direction = data['roomData']['room_direction'] #방향
        secret_4 = '' if data['roomData']['room_memo'] == '' else data['roomData']['room_memo'] + Keys.ENTER
        basic_secret += secret_4
        room_option = data['roomData']['room_option']#호실옵션
        tot_options = ",".join([building_option, room_option])

    
    # ChromeDriver 경로 설정
    driver = webdriver.Chrome('/chromedriver', options=options)
    # driver = webdriver.Chrome(ChromeDriverManager().install())

    # URL 열기
    # driver.maximize_window()
    
    driver.get('https://mobile.karhanbang.com/kren/mamul/list')

    # driver.get('https://mobile.karhanbang.com/snsLogin/login')
    driver.execute_script('return document.getElementById("realtorYn").click()') #개업공인중개사여부 체크
    driver.find_element(By.XPATH, '//*[@id="userId"]').send_keys('bsleemanse')
    driver.find_element(By.XPATH, '//*[@id="userPw"]').send_keys('tkdrnjs1001')
    driver.find_element(By.XPATH, '//*[@id="loginBtn"]/a/span').click()

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="in_search_so"]'))).click()
    한방번호 = ''
    options = driver.find_elements(By.XPATH, '//*[@id="in_search_so"]/option')
    if 한방번호 != '':
        print('한방번호가 존재할때')
        choice = '한방매물번호'
        value = ''
    else:
        print('한방번호가 존재하지 않을 때')
        choice = '본번-부번'
        value = data['landData']['land_jibun']
    for opt in options:
        print(opt.text)
        if opt.text == choice: 
            opt.click()
            driver.find_element(By.XPATH, '//*[@id="in_keyword"]').send_keys(value)
            driver.find_element(By.XPATH, '//*[@id="mainSearchBtn"]').click()
            break

    result = pyautogui.confirm('\n\n 매물등록을 진행하시겠습니까?', buttons=['예', '아니오'])    
    if result == '예':
        driver.get('https://mobile.karhanbang.com/kren/mamul/regist')
        # print("93")
        # # 로딩 완료를 기다리기 위한 암묵적 대기 설정
        # driver.implicitly_wait(10)
        print("95")
        if obinfo_type2 == '아파트':
            obinfo_type = '아파트'
        elif obinfo_type2 == '다가구':
            obinfo_type = '다가구'
        elif obinfo_type2 == '다세대':
            obinfo_type = '다세대'
        elif obinfo_type2 == '빌라':
            obinfo_type = '빌라'
        elif obinfo_type2 == '상가주택':
            obinfo_type = '상가주택'
        elif obinfo_type1 == '상가점포':
            obinfo_type = '상가점포'
        elif obinfo_type2 == '사무실':
            obinfo_type = '사무실'
        elif obinfo_type2 == '단독주택':
            obinfo_type = '단독'
        elif obinfo_type2 == '창고':
            obinfo_type = '창고'
        elif obinfo_type2 == '공장':
            obinfo_type = '공장'
        elif obinfo_type2 == '오피스텔':
            obinfo_type = '오피스텔'
        elif obinfo_type1 == '토지':
            obinfo_type = '토지'

        # 매물종류 변경버튼 클릭
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#formAddress > div.top_basic_box > div.base_info_option > ul > li.bx.view.pt5 > div > a'))).click()
        print("obinfo_type: "+obinfo_type)
        
        if obinfo_type == '':
            pyautogui.alert("매물분류를 선택하셨습니까? 계속하려면 '확인'을 누르세요")   
        else:
            time.sleep(0.2)
            s_li_tags = driver.find_element(By.CLASS_NAME, 's_box_list').find_elements(By.TAG_NAME,"li") #각 element속에 li 태그들을 모두 찾기
            s_box_list_text(s_li_tags, obinfo_type)
        # li_tags = driver.find_element(By.CLASS_NAME, 's_box_list').find_elements(By.TAG_NAME,"li") #각 element속에 li 태그들을 모두 찾기
        # for li in li_tags:
        #     print(li.text)
        #     if li.text == '아파트':
        #         li.click()
        #         break
        # option = driver.find_element(By.XPATH, "//*[@id='in_gure_cd_name2'][text()='전세']")
        # driver.execute_script("arguments[0].scrollIntoView();", option) #현재 상태에서 스크롤을 진행하되, option값이 나올때 까지 스크롤을 하는 함수
        # option.click()



        #거래구분
        print("obinfo_ttype: "+obinfo_ttype)
        driver.find_element(By.XPATH, '//*[@id="formAddress"]/div[2]/div[2]/ul/li[2]/div/ul/li[1]/div/div/div').click()
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 's_box_list'))) #매물종류 레이어팝업창이 뜰때까지 대기
        # print(driver.find_element(By.CLASS_NAME, 's_box_list').is_displayed())
        s_li_tags = driver.find_element(By.CLASS_NAME, 's_box_list').find_elements(By.TAG_NAME,"li") #각 element속에 li 태그들을 모두 찾기
        s_box_list_text(s_li_tags, obinfo_ttype)

        #입주가능일
        driver.execute_script("selValues('Y','즉시입주','in_soon_move_yn')") #js코드로 selValues함수 실행
        # s_li_tags = driver.find_element(By.CLASS_NAME, 's_box_list').find_elements(By.TAG_NAME,"li") #각 element속에 li 태그들을 모두 찾기
        # s_box_list_text(s_li_tags, '즉시입주')

        #시도
        driver.find_element(By.XPATH, '//*[@id="in_sido_name"]').click()
        s_li_tags = driver.find_element(By.CLASS_NAME, 's_box_list').find_elements(By.TAG_NAME,"li") #각 element속에 li 태그들을 모두 찾기
        s_box_list_text(s_li_tags, location_do)
        #시군구
        driver.find_element(By.XPATH, '//*[@id="in_gugun_name"]').click()
        s_li_tags = driver.find_element(By.CLASS_NAME, 's_box_list').find_elements(By.TAG_NAME,"li") #각 element속에 li 태그들을 모두 찾기
        s_box_list_text(s_li_tags, location_si)
        #읍면동
        driver.find_element(By.XPATH, '//*[@id="in_dong_name"]').click()
        s_li_tags = driver.find_element(By.CLASS_NAME, 's_box_list').find_elements(By.TAG_NAME,"li") #각 element속에 li 태그들을 모두 찾기
        # print("s_li_tags: " , s_li_tags)
        s_box_list_text(s_li_tags, location_dong)
        #일반/산
        driver.find_element(By.XPATH, '//*[@id="in_san_cd_name"]').click()
        s_li_tags = driver.find_element(By.CLASS_NAME, 's_box_list').find_elements(By.TAG_NAME,"li") #각 element속에 li 태그들을 모두 찾기
        s_box_list_text(s_li_tags, data['landData']['land_type'])
        #본번
        jibun_main = data['landData']['land_jibun'].split('-')[0]
        driver.find_element(By.XPATH, '//*[@id="in_old_bon_no"]').send_keys(jibun_main)

        #부번
        if '-' in data['landData']['land_jibun']:
            jibun_sub = data['landData']['land_jibun'].split('-')[-1]
            driver.find_element(By.XPATH, '//*[@id="in_old_bu_no"]').send_keys(jibun_sub)

        if tr_target == '건물' and tr_target == '층호수' :
            # 건물명
            driver.find_element(By.XPATH, '//*[@id="in_bd_nm"]').send_keys(data['buildingData']['building_name'])
            #호
            driver.find_element(By.XPATH, '//*[@id="in_ho_nm"]').send_keys(data['roomData']['room_num'])
            #회사명
            #건물위치
        #층
        if tr_target == '층호수':
            print(f"selValues('{basic_floor}','{basic_floor}','in_curr_floor')")
            driver.execute_script("openPopupCurrFloor()") #js코드로 openPopupCurrFloor 실행
            driver.execute_script(f"selValues('{basic_floor}','{basic_floor}','in_curr_floor')") #js코드로 selValues 실행

            # driver.find_element(By.XPATH, '//*[@id="in_curr_floor_name"]').click()
            # s_li_tags = driver.find_element(By.CLASS_NAME, 's_box_list').find_element(By.TAG_NAME, "in_curr_floor") #각 element속에 li 태그들을 모두 찾기
            # for li in s_li_tags:
            #     print(li)

            # s_box_list_value(s_li_tags, basic_floor)
            #총층
            driver.execute_script("openPopupTotalFloor()") #js코드로 openPopupTotalFloor 실행
            driver.execute_script(f"selValues({basic_totflr},{basic_totflr},'in_total_floor')") #js코드로 selValues 실행
            # driver.find_element(By.XPATH, '//*[@id="in_total_floor_name"]').click()
            # s_li_tags = driver.find_element(By.CLASS_NAME, 's_box_list').find_elements(By.TAG_NAME,"li") #각 element속에 li 태그들을 모두 찾기
            # s_box_list_value(s_li_tags, basic_totflr)

    #가격정보
        #매매가
        print("obinfo_trading: "+obinfo_trading ,"obinfo_rent1: "+obinfo_rent1 ,"obinfo_deposit1: "+obinfo_deposit1)

        if obinfo_ttype == '매매':
            driver.find_element(By.XPATH, '//*[@id="in_amt_sell"]').send_keys(obinfo_trading)
        # if driver.find_element(By.XPATH, '//*[@id="in_amt_sell"]').is_displayed() and obinfo_trading !='' : driver.find_element(By.XPATH, '//*[@id="in_amt_sell"]').send_keys(obinfo_trading) 
        if obinfo_ttype == '월세':
            #현월세금
            if driver.find_element(By.XPATH, '//*[@id="in_amt_month"]').is_displayed() and obinfo_rent1 !='' : driver.find_element(By.XPATH, '//*[@id="in_amt_month"]').send_keys(obinfo_rent1) 
        if obinfo_ttype == '월세' or obinfo_ttype == '전세':
            #현보증금
            if driver.find_element(By.XPATH, '//*[@id="in_amt_guar"]').is_displayed() and obinfo_deposit1 !='' : driver.find_element(By.XPATH, '//*[@id="in_amt_guar"]').send_keys(obinfo_deposit1) 
        #융자금
        driver.execute_script("openPopupLoanCode()")
        # driver.find_element(By.XPATH, '//*[@id="dialog_1683013148826"]/div/div/ul/li/div/ul/li[3]').click()
        driver.execute_script("selValues('2','30%이상(시세대비)','in_loanCode')")
        
    #면적정보
        print("면적정보")
        if tr_target == '층호수':
            #공급면적
            if driver.find_element(By.XPATH, '//*[@id="in_gong_meter"]').is_displayed() and basic_area2 !='' : driver.find_element(By.XPATH, '//*[@id="in_gong_meter"]').send_keys(basic_area2) 
            #전용면적
            if driver.find_element(By.XPATH, '//*[@id="in_jun_meter"]').is_displayed() and basic_area1 !='' : driver.find_element(By.XPATH, '//*[@id="in_jun_meter"]').send_keys(basic_area1) 
        if tr_target == '건물':
            #건축면적
            driver.find_element(By.XPATH, '//*[@id="in_gun_meter"]').send_keys(building_archarea)
            #연면적
            driver.find_element(By.XPATH, '//*[@id="in_yun_meter"]').send_keys(building_totarea)
        if tr_target == '토지' or tr_target == '건물':
            #대지면적
            driver.find_element(By.XPATH, '//*[@id="in_toji_meter"]').send_keys(land_totarea)

    #기타정보
        if tr_target != '토지':
            print("기타정보")
            #룸수
            #욕실수
            #승강기
            if int(building_elvcount) > 0:
                driver.execute_script("selValues('Y','유','in_elevator_yn')")
            elif int(building_elvcount) == 0:
                driver.execute_script("selValues('N','무','in_elevator_yn')")
            
        
            #주차
            if building_pn != '' : driver.find_element(By.XPATH, '//*[@id="in_total_park_cnt"]').send_keys(building_pn)
            #가구당 주차
            if building_pn != '' : driver.find_element(By.XPATH, '//*[@id="in_total_park_cnt"]').send_keys(building_pn)
            #방향기준
            if obinfo_type in ['상가점포']: #직접입력방식이 적용되는 물건
                driver.find_element(By.XPATH, '//*[@id="in_direction_info"]').send_keys("주출입문")
            #방향
            time.sleep(0.5)
            if tr_target == '건물' and building_direction != '': 
                print("건물방향: " + building_direction)
                driver.execute_script("openPopupDirectionCd()") #js코드로 openPopupDirectionCd 실행
                # driver.find_element(By.XPATH, f"//span[text()='{building_direction}']").click()  
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 's_box_list'))) 
                s_li_tags = driver.find_element(By.CLASS_NAME, 's_box_list').find_elements(By.TAG_NAME,"li") #각 element속에 li 태그들을 모두 찾기
                # print("s_li_tags: " , s_li_tags)
                s_box_list_text(s_li_tags, building_direction)
            elif tr_target == '층호수' and room_direction != '':
                print("호실방향: " + room_direction)
                driver.execute_script("openPopupDirectionCd()") #js코드로 openPopupDirectionCd 실행
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 's_box_list'))) 
                s_li_tags = driver.find_element(By.CLASS_NAME, 's_box_list').find_elements(By.TAG_NAME,"li") #각 element속에 li 태그들을 모두 찾기
                # print("s_li_tags: " , s_li_tags)
                s_box_list_text(s_li_tags, room_direction)
            #난방방식(초기값: 개별난방)
            #난방연료(초기값: 개별난방)
            #건축물용도
            print("건축물용도: ", building_purpose)
            if building_purpose != '':
                driver.execute_script("openPopUpBuildCd()") #js코드로 openPopUpBuildCd 실행
                if building_purpose == '제1종근린생활시설': building_purpose = '제1종 근린생활시설'
                if building_purpose == '제2종근린생활시설': building_purpose = '제2종 근린생활시설'
                if building_purpose == '자동차관련시설': building_purpose = '자동차 관련 시설'
                if building_purpose == '자동차관련시설': building_purpose = '동물 및 식물 관련 시설'
                if building_purpose == '자동차관련시설': building_purpose = '자원순환 관련 시설'
                if building_purpose == '자동차관련시설': building_purpose = '교정(교정) 및 군사 시설'
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 's_box_list')))
                s_li_tags = driver.find_element(By.CLASS_NAME, 's_box_list').find_elements(By.TAG_NAME,"li")
                s_box_list_text(s_li_tags, building_purpose)

            #사용승인일 building_usedate 
            driver.execute_script("checkApprovalDayManual()") #js코드로 checkApprovalDayManual 실행
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="manual_approval_year"]')))
            usedate = building_usedate.split("-")

            # pyautogui.alert("사용승인일 차례")
            
            driver.find_element(By.XPATH, '//*[@id="manual_approval_year"]').send_keys(usedate[0])
            driver.find_element(By.XPATH, '//*[@id="manual_approval_month"]').send_keys(usedate[1])
            driver.find_element(By.XPATH, '//*[@id="manual_approval_day"]').send_keys(usedate[2])
            # WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="basic"]/div[11]/ul/li[12]/div/ul/li/div/div/div/div[1]/div/div/label[3]/span/span'))).click() 

            if basic_manager == '별도':
                # 관리비
                driver.find_element(By.XPATH, '//*[@id="in_managefee_info"]').send_keys(basic_mmoney)
                #관리비항목
                driver.execute_script("openPopupmnexItem()") #js코드로 openPopupmnexItem 실행
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'option_list')))
                o_li_tags = driver.find_element(By.CLASS_NAME, 'option_list').find_elements(By.TAG_NAME,"li")
                for li in o_li_tags:
                    # print("li.text: ", li.text)
                    mlist =  basic_mlist.split(",")
                    for item in mlist:
                        if item == '개별수도': item = '수도'
                        if item == '유선': item = 'TV'
                        # print("item: ",item)
                        if item == li.text:
                            li.click()
                driver.execute_script("confirmMnixItem()") #선택완료버튼 클릭
                #비목
                driver.find_element(By.XPATH, '//*[@id="in_expenses_item_info"]').send_keys(basic_mmemo) 
            #옵션내역
            if obinfo_type not in ['아파트']: #옵션항목이 없는 리스트 설정
                driver.execute_script("openPopupOption()") #옵션선택 팝업창열기
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'option_list')))
                o_li_tags = driver.find_element(By.CLASS_NAME, 'option_list').find_elements(By.TAG_NAME,"li")
                for li in o_li_tags:
                    # print("li.text: ", li.text)
                    options =  tot_options.split(",")
                    for item in options:
                        # if item == '개별수도': item = '수도'
                        # if item == '유선': item = 'TV'
                        # print("item: ",item)
                        if item == li.text:
                            li.click()
                driver.execute_script("confirmOption()") #선택완료버튼 클릭 
        if tr_target == '토지':
            #지목 representing_jimok   
            jimok = f"({data['landData']['representing_jimok'][0]}){data['landData']['representing_jimok']}" 
            driver.find_element(By.XPATH, '//*[@id="in_jimok_cd_name"]').click()
            s_li_tags = driver.find_element(By.CLASS_NAME, 's_box_list').find_elements(By.TAG_NAME,"li") #각 element속에 li 태그들을 모두 찾기
            s_box_list_text(s_li_tags, jimok)   
            #용도지역  
            representing_purpose = data['landData']['representing_purpose']
            if '주거' in representing_purpose or '상업' in representing_purpose or '공업' in representing_purpose or '녹지' in representing_purpose:
                purpose1 = '도시지역'
            elif '관리' in representing_purpose:
                purpose1 = '관리지역'
            elif '농림' in representing_purpose or '농업' in representing_purpose:
                purpose1 = '농림지역'
            elif '보전' in representing_purpose:
                purpose1 = '자연환경보전지역'
            
            driver.find_element(By.XPATH, '//*[@id="in_yong_jiyuk1_cd_name"]').click()
            s_li_tags = driver.find_element(By.CLASS_NAME, 's_box_list').find_elements(By.TAG_NAME,"li") #각 element속에 li 태그들을 모두 찾기
            s_box_list_text(s_li_tags, purpose1)  
            #용도지역2
            driver.find_element(By.XPATH, '//*[@id="in_yong_jiyuk2_cd_name"]').click()
            pyautogui.alert(f"용도지역: {data['landData']['representing_purpose']} \n용도지역2 선택후 확인!!")
            # time.sleep(0.5)
            # #접한도로 //*[@id="in_road_meter_name"]
            # driver.find_element(By.XPATH, '//*[@id="in_road_meter_name"]').click()
            # pyautogui.alert(f"{data['landData']['land_road']} 토지입니다. \n선택후 확인!!")
                   
        #매물특징
        driver.find_element(By.XPATH, '//*[@id="in_feature"]').send_keys()
        #매물설명
        driver.find_element(By.XPATH, '//*[@id="in_memo"]').send_keys(basic_secret)
        #비공개메모
        basic_secret = formatted_date+" "+admin_name+" https://obangkr.cafe24.com/web/request/request_view/view_give_request_detail.php?request_code="+request_code
        driver.find_element(By.XPATH, '//*[@id="in_secret_memo"]').send_keys(basic_secret)
        # #사진 (미적용: 고난이도 작업ㅠ)
        # filePath = driver.find_element(By.XPATH, '//*[@id="product_form"]/div[1]/div[9]/div[2]/div[1]/div/div').get_attribute("outerHTML").split('<input id="')[1].split('" t')[0]
        
        # import os

        # try:
        #     main_dir = 'Z:\\업무자료\\4사진자료&이미지자료(외부유출금지)\\1주거용물건, 상업용물건\\'
        #     # path_dir = main_dir + data['folderPath'] #'경기도\\오산시\\궐동\\654-9\\썬플라워\\1층\\1층'
        #     # print(path_dir)
        #     path_dir = 'Z:\\업무자료\\4사진자료&이미지자료(외부유출금지)\\1주거용물건, 상업용물건\\경기도\\오산시\\궐동\\672-1\\신도빌딩\\3층\\301호 세븐당구클럽'
        #     try:
        #         file_list = os.listdir(path_dir)
        #         arr = []
        #         for filename in file_list:
        #             if "output" in filename: arr.append(filename.split('output')[1]) #output폴더들의 생성일을 arr에 담기

        #         if len(arr) == 0: #output폴더가 없다면
        #             arr2 = []
        #             for file in file_list: #원본사진을 arr2에 담기(원본사진은 있는지 확인)
        #                 if file.endswith('.jpeg') or file.endswith('.gif') or file.endswith('.png') or file.endswith('.jpg'):
        #                     arr2.append(file)
        #             if len(arr2) == 0: #원본사진도 없다면?
        #                 # driver.execute_script('return document.getElementById("is_speed").click()') #급매 체크
        #                 pass


        #         path = path_dir + "/output" + max(arr) #최근에 변환된 사진이 있는 폴더경로 설정

        #         photo_list = []

        #         for file in os.listdir(path):
        #             if file.endswith('.jpeg') or file.endswith('.gif') or file.endswith('.png') or file.endswith('.jpg'):
        #                 photo_list.append(file) #사진파일들만 photo_list에 추가

        #         for photo in photo_list:
        #             file_path = path + '/' + photo #사진파일의 전체경로 설정
        #             driver.find_element(By.ID, '#apdPicSwiper').send_keys(file_path)
        #             driver.execute_script("confirmOption()")
        #     except: 
        #         # driver.execute_script('return document.getElementById("is_speed").click()')
        #         print("사진 오류")
        #         pass
        # except:
        #     print("폴더 오류", data['folderPath'])
        #     # driver.execute_script('return document.getElementById("is_speed").click()')
        #     errarr.append("폴더 오류")
        #     pass

        #개인정보수집이용동의
        driver.execute_script('document.getElementById("checkAgree").checked = true') #동의 체크하기

        # time.sleep(120)
        pyautogui.alert("확인을 누르면 프로그램이 종료됩니다.") 

        driver.close()
        return errarr

        #등록하기


        # try:
        #     driver.execute_script("checkApprovalDayManual()") #js코드로 checkApprovalDayManual 실행
        #     # time.sleep(5)
        #     # print(driver.find_element(By.XPATH, '//*[@id="basic"]/div[13]/ul/li[11]/div/ul/li/div/div/div/div[1]/div/div/label[3]'))
        #     # driver.find_element(By.XPATH, '//*[@id="basic"]/div[13]/ul/li[11]/div/ul/li/div/div/div/div[1]/div/div/label[3]').click()
        # except Exception as e:
        #     print("에러 발생:", str(e))
    elif result == '아니오':
        driver.close()
        return errarr

def s_box_list_text(li_tags, text): 
    for li in li_tags:
        # print(li.text)
        if li.text == text:
            li.click()
            break

def s_box_list_value(li_tags, val): 
    for li in li_tags:
        # print(li.get_attribute('value'))
        if li.get_attribute('value') == val:
            li.click()
            break
