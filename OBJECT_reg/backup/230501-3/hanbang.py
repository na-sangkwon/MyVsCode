from selenium import webdriver
from selenium.webdriver import ActionChains

from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait

import pyautogui 
import time

# # ChromeDriver 경로 설정
# driver = webdriver.Chrome('/chromedriver')
options = Options()
options.add_experimental_option("detach", True) # 창이 자동으로 닫히지 않게 해줌
options.add_experimental_option("excludeSwitches", ["enable-automation"]) #브라우저에 나타나는 자동화라는 메세지 제거

def macro(data, user):
    
    errarr = []
    tr_target = data['writeData']['tr_target']
    location_do = data['landData']['land_do']
    location_si = data['landData']['land_si']
    location_dong = data['landData']['land_dong']

    location_lijibun = (data['type_path'] + data['landData']['land_jibun']) if data['landData']['land_li'] == '' else (data['landData']['land_li'] + data['type_path'] + data['landData']['land_jibun'])
    location_dongli = (data['landData']['land_dong'] + data['type_path'] + data['landData']['land_jibun']) if data['landData']['land_li'] == '' else location_lijibun
    location_detail = location_dongli

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
    basic_mmoney = data['writeData']['mmoney'] #관리비
    basic_mlist = data['writeData']['mlist'] #관리비포함내역
    basic_mmemo = data['writeData']['mmemo'] #관리비메모
    basic_totflr = str(int(data['buildingData']['building_grndflr']) + int(data['buildingData']['building_ugrndflr'])) #전체층
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
        building_usedate = str(data['buildingData']['building_usedate']) #준공일
        building_pn = data['buildingData']['building_pn'] #주차
        secret_3 = '' if data['buildingData']['building_memo'] == '' else data['buildingData']['building_memo'] + Keys.ENTER
        basic_secret += secret_3
        building_archarea = data['buildingData']['building_archarea'] #건축면적
        building_totarea = data['buildingData']['building_totarea'] #연면적
        building_direction = data['buildingData']['building_direction'] #방향
        building_purpose = data['buildingData']['building_purpose'] #주용도
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
        secret_4 = '' if data['roomData']['room_memo'] == '' else data['roomData']['room_memo'] + Keys.ENTER
        basic_secret += secret_4
        room_option = data['roomData']['room_option']#호실옵션
        tot_options = ",".join([building_option, room_option])

    
    # ChromeDriver 경로 설정
    driver = webdriver.Chrome('/chromedriver')

    # URL 열기
    # driver.maximize_window()
    
    driver.get('https://mobile.karhanbang.com/kren/mamul/regist')

    # driver.get('https://mobile.karhanbang.com/snsLogin/login')
    driver.execute_script('return document.getElementById("realtorYn").click()') #개업공인중개사여부 체크
    driver.find_element(By.XPATH, '//*[@id="userId"]').send_keys('bsleemanse')
    driver.find_element(By.XPATH, '//*[@id="userPw"]').send_keys('tkdrnjs1001')
    driver.find_element(By.XPATH, '//*[@id="loginBtn"]/a/span').click()

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
    elif obinfo_type2 == '상가점포':
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
    elif obinfo_type2 == '토지':
        obinfo_type = '토지'

    # 매물종류 변경버튼 클릭
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#formAddress > div.top_basic_box > div.base_info_option > ul > li.bx.view.pt5 > div > a'))).click()
    print("obinfo_type: "+obinfo_type)
    if obinfo_type == '':
        pyautogui.alert("매물종류를 변경해주세요")   
    else:
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
    jibun_sub = data['landData']['land_jibun'].split('-')[-1]
    driver.find_element(By.XPATH, '//*[@id="in_old_bu_no"]').send_keys(jibun_sub)

    #건물명
    # driver.find_element(By.XPATH, '//*[@id="in_bd_nm"]').send_keys(data['buildingData']['building_name'])
    #호
    # driver.find_element(By.XPATH, '//*[@id="in_ho_nm"]').send_keys(data['roomData']['room_num'])
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
    print("기타정보")
    #룸수
    #욕실수
    #주차
    if building_pn != '' : driver.find_element(By.XPATH, '//*[@id="in_total_park_cnt"]').send_keys(building_pn)
    #가구당 주차
    #방향기준
    #방향
    time.sleep(0.5)
    if building_direction != '': 
        driver.execute_script("openPopupDirectionCd()") #js코드로 openPopupDirectionCd 실행
        # driver.find_element(By.XPATH, f"//span[text()='{building_direction}']").click()  
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 's_box_list'))) 
        s_li_tags = driver.find_element(By.CLASS_NAME, 's_box_list').find_elements(By.TAG_NAME,"li") #각 element속에 li 태그들을 모두 찾기
        # print("s_li_tags: " , s_li_tags)
        s_box_list_text(s_li_tags, building_direction)

    #난방방식(초기값: 개별난방)
    #난방연료(초기값: 개별난방)
    #건축물용도
    print("건축물용도: ", building_purpose)
    if building_purpose != '':
        driver.execute_script("openPopUpBuildCd()") #js코드로 openPopUpBuildCd 실행
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 's_box_list')))
        s_li_tags = driver.find_element(By.CLASS_NAME, 's_box_list').find_elements(By.TAG_NAME,"li")
        s_box_list_text(s_li_tags, building_purpose)
    #사용승인일 building_usedate 
    driver.execute_script("checkApprovalDayManual()") #js코드로 checkApprovalDayManual 실행
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="manual_approval_year"]')))
    usedate = building_usedate.split("-")
    driver.find_element(By.XPATH, '//*[@id="manual_approval_year"]').send_keys(usedate[0])
    driver.find_element(By.XPATH, '//*[@id="manual_approval_month"]').send_keys(usedate[1])
    driver.find_element(By.XPATH, '//*[@id="manual_approval_day"]').send_keys(usedate[2])
    # WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="basic"]/div[11]/ul/li[12]/div/ul/li/div/div/div/div[1]/div/div/label[3]/span/span'))).click() 

    driver.find_element(By.XPATH, '//*[@id="in_managefee_info"]').send_keys("4444")


    if basic_manager == '별도':
        # 관리비
        driver.find_element(By.XPATH, '//*[@id="in_managefee_info"]').send_keys(basic_mmoney)
        #관리비항목
        driver.execute_script("openPopupmnexItem()") #js코드로 openPopupmnexItem 실행
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'option_list')))
        o_li_tags = driver.find_element(By.CLASS_NAME, 'option_list').find_elements(By.TAG_NAME,"li")
        for li in o_li_tags:
            print("li.text: ", li.text)
            mlist =  basic_mlist.split(",")
            for item in mlist:
                if item == '개별수도': item = '수도'
                if item == '유선': item = 'TV'
                print("item: ",item)
                if item == li.text:
                    li.click()
        driver.execute_script("confirmMnixItem()") #선택완료버튼 클릭
        #비목
        driver.find_element(By.XPATH, '//*[@id="in_expenses_item_info"]').send_keys(basic_mmemo) 

    pyautogui.alert("검토하기!!") 

    #옵션내역
    driver.execute_script("openPopupOption()") #옵션선택 팝업창열기
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'option_list')))
    o_li_tags = driver.find_element(By.CLASS_NAME, 'option_list').find_elements(By.TAG_NAME,"li")
    for li in o_li_tags:
        print("li.text: ", li.text)
        options =  tot_options.split(",")
        for item in options:
            # if item == '개별수도': item = '수도'
            # if item == '유선': item = 'TV'
            # print("item: ",item)
            if item == li.text:
                li.click()
    driver.execute_script("confirmOption()") #선택완료버튼 클릭    
    #매물특징
    #매물설명
    #비공개메모
    driver.find_element(By.XPATH, '//*[@id="in_secret_memo"]').send_keys(basic_secret)
    #사진
    #개인정보수집이용동의
    # WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="checkAgree"]'))).click()  

    #등록하기


    # try:
    #     driver.execute_script("checkApprovalDayManual()") #js코드로 checkApprovalDayManual 실행
    #     # time.sleep(5)
    #     # print(driver.find_element(By.XPATH, '//*[@id="basic"]/div[13]/ul/li[11]/div/ul/li/div/div/div/div[1]/div/div/label[3]'))
    #     # driver.find_element(By.XPATH, '//*[@id="basic"]/div[13]/ul/li[11]/div/ul/li/div/div/div/div[1]/div/div/label[3]').click()
    # except Exception as e:
    #     print("에러 발생:", str(e))

    time.sleep(10)
    pyautogui.alert("작업을 종료하시겠습니까?")
    driver.close()
    return errarr
    # input()

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
