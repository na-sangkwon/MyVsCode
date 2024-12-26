from selenium import webdriver
from selenium.webdriver import ActionChains

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait

import pyautogui 
import time


# # ChromeDriver 경로 설정
# driver = webdriver.Chrome('/chromedriver')
def objectCheckTime():
    import sys
    from PyQt5.QtWidgets import QApplication, QMessageBox
    app = QApplication(sys.argv)

    # 메시지 창 생성
    msgBox = QMessageBox()
    msgBox.setText("매물종류를 선택해주세요~5초후 작업이 시작됩니다.")
    msgBox.setStandardButtons(QMessageBox.Ok)
    msgBox.setWindowModality(2)  # 모달 창으로 설정 (다른 작업을 막음)
    msgBox.show()

    sys.exit(app.exec_())

def macro(data, user):
    
    errarr = []
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
    basic_mmoney = data['writeData']['mmoney'] #관리비
    basic_mlist = data['writeData']['mlist'] #관리비포함내역
    basic_mmemo = data['writeData']['mmemo'] #관리비메모
    add_warmer = '' #data['writeData']['add_warmer'] 난방
    add_rdate = str(data['writeData']['rdate']) #입주일
    secret_1 = '' if data['writeData']['tr_memo'] == '' else data['writeData']['tr_memo'] + Keys.ENTER
    secret_2 = '' if data['landData']['land_memo'] == '' else data['landData']['land_memo'] + Keys.ENTER
    basic_secret = secret_1 + secret_2 #비밀메모
    land_option = data['landData']['land_option']#토지옵션

    if tr_target == '토지' or tr_target == '건물':
        land_totarea = data['landData']['land_totarea'] #대지면적

    if tr_target == '건물' or tr_target == '층호수':
        location_building = '' if data['buildingData']['building_name'] == '' else ' ' + data['buildingData']['building_name']
        location_detail += location_building
        building_archarea = data['buildingData']['building_archarea'] #건축면적
        building_totarea = data['buildingData']['building_totarea'] #연면적
        building_direction = data['buildingData']['building_direction'] #방향
        building_purpose = data['buildingData']['building_purpose'] #주용도
        building_usedate = str(data['buildingData']['building_usedate']) #사용승인일
        basic_totflr = str(int(data['buildingData']['building_grndflr']) + int(data['buildingData']['building_ugrndflr'])) #전체층
        building_ugrndflr = data['buildingData']['building_ugrndflr'] #지하층수
        building_grndflr = data['buildingData']['building_grndflr'] #지상층수
        add_usedate = str(data['buildingData']['building_usedate']) #준공일
        building_pn = int(data['buildingData']['building_pn']) if data['buildingData']['building_pn'] != '' else 0 #주차대수
        secret_3 = '' if data['buildingData']['building_memo'] == '' else data['buildingData']['building_memo'] + Keys.ENTER
        basic_secret += secret_3

    if tr_target == '층호수':
        location_room = '' if data['roomData']['room_num'] == '' else ' ' + data['roomData']['room_num']
        room_status = ' '+data['roomData']['room_status'] if data['roomData']['room_status']!='미확인' else ' 상태미확인' #호실상태
        room_gate1 = ' '+data['roomData']['room_gate1'] #내부출입1
        room_gate2 = ':'+data['roomData']['room_gate2'] if data['roomData']['room_gate2'] != '' else '' #내부출입2  
        room_gate = room_status+room_gate1+room_gate2 if room_gate1 != ' 미확인' else ' 미확인'
        location_detail += location_room+room_gate
        basic_area1 = data['roomData']['room_area1'] #실면적
        basic_area2 = data['roomData']['room_area2'] #공급면적
        basic_rcount = data['roomData']['room_rcount'] #방수
        basic_bcount = data['roomData']['room_bcount'] #욕실수
        basic_floor = data['roomData']['room_floor'] #해당층
        add_options = data['roomData']['room_option'] #옵션선택
        room_direction = data['roomData']['room_direction'] #방향
        secret_4 = '' if data['roomData']['room_memo'] == '' else data['roomData']['room_memo'] + Keys.ENTER
        basic_secret += secret_4
    
    basic_secret = "https://obangkr.cafe24.com/web/request/request_view/view_give_request_detail.php?request_code="+request_code

    # ChromeDriver 경로 설정
    driver = webdriver.Chrome('/chromedriver')

    # URL 열기
    driver.maximize_window()
    driver.get('https://member.serve.co.kr/login/login.asp?TargetPage=http://www.serve.co.kr/agency/maemul/nmaemul_reg.asp')

    driver.find_element(By.XPATH, '//*[@id="txtUserID"]').send_keys("osanbang6666")
    driver.find_element(By.XPATH, '//*[@id="pwdPassWord"]').send_keys("dhqkd5555%")
    driver.find_element(By.XPATH, '//*[@id="loginWrap"]/div/div[1]/button').click()

    # 로그인확인겸 첫 파란등록버튼 기다리기(관리자로 로그인시)
    driver.implicitly_wait(10)
    # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/div[1]/div/ul/li[3]/a'))).click()
    # driver.find_element(By.XPATH, '//*[@id="menu-product-1"]/a').click()

    # 확인후 이동
    driver.get('http://serve.co.kr/agency/maemul/nmaemul_reg.asp')



#기본정보
    #매물분류

    #주거용&방개수1 => 원룸, 상업용
    print("매물분류1차:", obinfo_type1, "매물분류2차:", obinfo_type2)
    if obinfo_type1 == '':
        objectCheckTime()
    else:
        driver.find_element(By.XPATH, '//*[@id="category1"]').send_keys(obinfo_type1)
        driver.find_element(By.XPATH, '//*[@id="category2"]').send_keys(obinfo_type2)
    #거래종류 obinfo_ttype
    print("거래종류:", obinfo_ttype)
    ttype_td = driver.find_elements(By.XPATH, '//*[@id="div_disabled_01"]/fieldset/table/tbody/tr[2]/td/label')
    for item in ttype_td:
        # print("거래종류:", item.text)
        if item.text == obinfo_ttype:
            item.click()
            break
    # driver.find_element(By.XPATH, '//*[@id="lcode_si"]').click() #보증금O/월세O=>월세, 보증금O/월세X=>전세, 보증금X/월세X/매매금O=>매매

    print(location_do, location_si, location_dongli)
    driver.find_element(By.XPATH, '//*[@id="lcode_si"]').send_keys(location_do) # 
    time.sleep(0.5); print("si ok:", location_do)
    driver.find_element(By.XPATH, '//*[@id="lcode_gu"]').send_keys(location_si) # 
    time.sleep(0.5); print("do ok:", location_si)
    driver.find_element(By.XPATH, '//*[@id="lcode_dong"]').send_keys(location_dong) # 
    time.sleep(0.5); print("dong ok:", location_dong)
    if data['landData']['land_li']!='': 
        driver.find_element(By.XPATH, '//*[@id="ri"]').send_keys(data['landData']['land_li']) # 
        time.sleep(0.5); print("li ok:", data['landData']['land_li'])
    time.sleep(0.5); print("type_path ok:", data['type_path'])
    if data['type_path']=='산':
        driver.find_element(By.XPATH, '//*[@id="ismount2"]').click()
    time.sleep(0.5); print("jibun ok:", data['landData']['land_jibun'])
    driver.find_element(By.XPATH, '//*[@id="address2"]').send_keys(data['landData']['land_jibun']) # 
    driver.find_element(By.XPATH, '//*[@id="latlng_btn"]/a').click()


#가격정보
    if obinfo_ttype=='매매':
        print("매매가: ",obinfo_trading)
        driver.find_element(By.XPATH, '//*[@id="price1"]').send_keys(obinfo_trading) #매매가
        # driver.find_element(By.XPATH, '//*[@id="aprice1"]').send_keys() #현 보증금
        # driver.find_element(By.XPATH, '//*[@id="aprice2"]').send_keys() #현 월세
        driver.find_element(By.XPATH, '//*[@id="loanCode"]').send_keys("시세대비 30% 이상") #융자여부 시세대비 30%이상 선택
        # driver.find_element(By.XPATH, '//*[@id="loan"]').send_keys() #융자금

    if obinfo_ttype=='전세' or obinfo_ttype=='월세':
        print("보증금: ",obinfo_deposit1)
        driver.find_element(By.XPATH, '//*[@id="price1"]').send_keys(obinfo_deposit1) #보증금
        # driver.find_element(By.XPATH, '//*[@id="aprice2"]').send_keys() #현 월세
        driver.find_element(By.XPATH, '//*[@id="loanCode"]').send_keys("시세대비 30% 이상") #융자여부 시세대비 30%이상 선택
        # driver.find_element(By.XPATH, '//*[@id="loan"]').send_keys() #융자금   
        if basic_manager == '별도':
            driver.find_element(By.XPATH, '//*[@id="mnexYn1"]').click()
            driver.find_element(By.XPATH, '//*[@id="mnex"]').send_keys(basic_mmoney) #월관리비

    if obinfo_ttype=='월세':
        print("월세: ",obinfo_rent1)
        driver.find_element(By.XPATH, '//*[@id="price2"]').send_keys(obinfo_rent1) #월세
        # driver.find_element(By.XPATH, '//*[@id="aprice1"]').send_keys() #권리금


#매물정보
    if tr_target in ['토지']:
        driver.find_element(By.XPATH, '//*[@id="spc1"]').send_keys(land_totarea) #대지면적
    driver.find_element(By.XPATH, '//*[@id="spc1"]').send_keys(basic_area2) #계약면적
    


    if obinfo_type1 in ['주택']:
        #건물유형
        driver.find_element(By.XPATH, '//*[@id="spc2"]').send_keys(basic_area1) #전용면적
        driver.find_element(By.XPATH, '//*[@id="floor1"]').send_keys(basic_floor) #해당층
        driver.find_element(By.XPATH, '//*[@id="floor2"]').send_keys(basic_totflr) #총층수
        #층노출동의여부
        #방수
        #욕실수
        print("방향기준: ",room_direction); driver.find_element(By.XPATH, '//*[@id="direction"]').send_keys(room_direction) #방향기준
        #호실방향
        #복층여부
        if building_pn > 0 : driver.find_element(By.XPATH, '//*[@id="parkingpsbl"]').send_keys('가능') #주차가능여부
        print("총주차대수: ",building_pn); driver.find_element(By.XPATH, '//*[@id="parking"]').send_keys(building_pn) #총주차대수
        print("건축물용도: ",building_purpose); driver.find_element(By.XPATH, '//*[@id="lawUsageCode"]').send_keys(building_purpose) #건축물용도
        usedate = building_usedate.split("-")
        driver.find_element(By.XPATH, '//*[@id="cdate_yy"]').send_keys(usedate[0]) #건축물일자 년
        driver.find_element(By.XPATH, '//*[@id="cdate_mm"]').send_keys(usedate[1]) #건축물일자 월
        driver.find_element(By.XPATH, '//*[@id="cdate_dd"]').send_keys(usedate[2]) #건축물일자 일   

#중개업소정보
    time.sleep(0.5)
    print("관리자메모: ", basic_secret)
    driver.find_element(By.XPATH, '//*[@id="admin_memo"]').send_keys(basic_secret) #관리자메모

    time.sleep(60)
    pyautogui.alert("작업을 종료하시겠습니까?")
    driver.close()
    return errarr