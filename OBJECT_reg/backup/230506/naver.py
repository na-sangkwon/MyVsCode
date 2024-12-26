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
    tr_range = data['writeData']['tr_range']
    location_do = data['landData']['land_do']
    location_si = data['landData']['land_si']
    location_dong = data['landData']['land_dong']

    location_lijibun = (data['type_path'] + data['landData']['land_jibun']) if data['landData']['land_li'] == '' else (data['landData']['land_li'] + data['type_path'] + data['landData']['land_jibun'])
    location_dongli = (data['landData']['land_dong'] + data['type_path'] + data['landData']['land_jibun']) if data['landData']['land_li'] == '' else location_lijibun
    location_detail = ''

    request_code = data['writeData']['request_code'] #의뢰번호
    obang_code = data['writeData']['obang_code'] #오방매물번호
    options = ''
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
        building_name = data['buildingData']['building_name'] #건물명
        building_archarea = data['buildingData']['building_archarea'] #건축면적
        building_totarea = data['buildingData']['building_totarea'] #연면적
        building_direction = data['buildingData']['building_direction'] #방향
        building_purpose = data['buildingData']['building_purpose'] #주용도
        building_usedate = str(data['buildingData']['building_usedate']) #사용승인일
        basic_totflr = str(int(data['buildingData']['building_grndflr']) + int(data['buildingData']['building_ugrndflr'])) #전체층
        building_ugrndflr = str(data['buildingData']['building_ugrndflr']) if data['buildingData']['building_ugrndflr']!='' else 0 #지하총층
        building_grndflr = str(data['buildingData']['building_grndflr']) #지상총층
        building_important = data['buildingData']['building_important'] #건물특징
        if building_important != '':
            options += ','+building_important if options != '' else building_important
        # if building_important != '': options = building_important
        print("building_important: ", options)
        building_option = data['buildingData']['building_option'] #건물옵션
        if building_option != '':
            options += ','+building_option if options != '' else building_option
        # if building_option != '': options = options+','+building_option
        print("building_option: ", options)
        building_pn = int(data['buildingData']['building_pn']) if data['buildingData']['building_pn'] != '' else 0 #주차대수
        secret_3 = '' if data['buildingData']['building_memo'] == '' else data['buildingData']['building_memo'] + Keys.ENTER
        basic_secret += secret_3

    basic_floor = ''
    basic_rcount=''
    basic_bcount=''
    r_direction=''
    room_direction=''
    if tr_target == '층호수':
        location_room = '' if data['roomData']['room_num'] == '' else ' ' + data['roomData']['room_num']
        room_status = ' '+data['roomData']['room_status'] if data['roomData']['room_status']!='미확인' else ' 상태미확인' #호실상태
        room_gate1 = ' '+data['roomData']['room_gate1'] #내부출입1
        room_gate2 = ':'+data['roomData']['room_gate2'] if data['roomData']['room_gate2'] != '' else '' #내부출입2  
        room_gate = room_status+room_gate1+room_gate2 if room_gate1 != ' 미확인' else ' 미확인'
        location_detail += location_room
        basic_area1 = data['roomData']['room_area1'] #전용면적(호실)
        basic_area2 = data['roomData']['room_area2'] #공급면적
        basic_rcount = data['roomData']['room_rcount'] #방수
        basic_bcount = data['roomData']['room_bcount'] #욕실수
        basic_floor = data['roomData']['room_floor'] #해당층
        room_important = data['roomData']['room_important'] #호실특징
        if room_important != '':
            options += ','+room_important if options != '' else room_important
        print("room_important: ", options)
        room_option = data['roomData']['room_option'] #호실옵션
        if room_option != '':
            options += ','+room_option if options != '' else room_option
        print("room_option: ", options)
        r_direction = data['roomData']['direction_stn'] #방향기준
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

    def find_Maintag(th_xpath, tag_type, target_text, exe_xpath, exe_type, content):
        # # 스크롤을 내리는 JavaScript 코드 실행
        # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        try:
            alert = WebDriverWait(driver, 0.2).until(EC.alert_is_present())
            alert.accept()
        except Exception as e:
            print("alert오류", str(e))
            pass  # alert 창이 없는 경우, 그냥 넘어갑니다.

        # 특정 텍스트와 일치하는 span 태그를 찾습니다.
        print("항목명 xpath:", f'{th_xpath}//{tag_type}'," ,값:", content)

        # pyautogui.alert(f"항목명({target_text}:{content}) 찾기 실행 ㄱㄱ?")

        elements = driver.find_elements(By.XPATH, f'{th_xpath}//{tag_type}')
        # elements = driver.find_elements(By.XPATH, f"//{tag_type}[contains(text(), '{target_text}')]") #문자열포함
        print("elements개수:", len(elements))
        # 일치하는 태그가 있는지 확인합니다. //*[@id="div_disabled_04"]/fieldset/table/tbody/tr[2]/th/label
        if len(elements) > 0:
            for element in elements:
                print("element.text:",element.text)
                if target_text in element.text :
                    print(f"'{target_text}'와 일치하는 '{tag_type}'태그(main)가 있습니다.")
                    exe_ele = driver.find_element(By.XPATH, f'{exe_xpath}')
                    if exe_type == 'input':
                        exe_ele.send_keys(content)
                    elif exe_type == 'click':
                        exe_ele.click()
                    elif exe_type == 'select':
                        exe_ele.select_by_value(content)
                    break
                else:
                    print(f"'{tag_type}'태그(main)에 '{target_text}' 텍스트가 없습니다.")
                    # return "exist"
        else:
            print(f"'{target_text}'와 일치하는 '{tag_type}'태그(main)가 없습니다.")
            # return "nothing"



    def find_Subtag(tag_type, target_text, xpath, content):
        # # 스크롤을 내리는 JavaScript 코드 실행
        # driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        # 특정 텍스트와 일치하는 span 태그를 찾습니다.
        elements = driver.find_elements(By.XPATH, f"//{tag_type}[text()='{target_text}']")

        # 일치하는 태그가 있는지 확인합니다.
        if len(elements) > 0:
            print(f"'{target_text}'와 일치하는 '{tag_type}'태그(sub)가 있습니다.")
            input_ele = driver.find_element(By.XPATH, xpath)
            input_ele.send_keys(content)
            # return "exist"
        else:
            print(f"'{target_text}'와 일치하는 '{tag_type}'태그(sub)가 없습니다.")
            # return "nothing"
        
    # pyautogui.alert("계속 하시겠습니까?")

#기본정보
    #매물분류

    #주거용&방개수1 => 원룸, 상업용
    print("매물분류1차:", obinfo_type1, "매물분류2차:", obinfo_type2)
    if obinfo_type1 == '':
        # objectCheckTime()
        pyautogui.alert("매물분류 선택후 확인을 눌러주세요!!")
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
    driver.find_element(By.XPATH, '//*[@id="address3"]').send_keys(location_detail)

    # find_Subtag("em", "건물명", '//*[@id="buildnm"]',building_name)

#가격정보
    if obinfo_ttype=='매매':
        print("매매가: ",obinfo_trading)
        driver.find_element(By.XPATH, '//*[@id="price1"]').send_keys(obinfo_trading) #매매가
        # driver.find_element(By.XPATH, '//*[@id="aprice2"]').send_keys() #현 월세

    if obinfo_ttype=='전세' or obinfo_ttype=='월세':
        print("보증금: ",obinfo_deposit1)
        driver.find_element(By.XPATH, '//*[@id="price1"]').send_keys(obinfo_deposit1) #보증금
        if obinfo_ttype=='월세':
            print("월세: ",obinfo_rent1)
            driver.find_element(By.XPATH, '//*[@id="price2"]').send_keys(obinfo_rent1) #월세
            # if obinfo_type1 in ['상가점포']:
            #     driver.find_element(By.XPATH, '//*[@id="aprice1"]').send_keys() #권리금
        
        driver.find_element(By.XPATH, '//*[@id="loanCode"]').send_keys("시세대비 30% 이상") #융자여부 시세대비 30%이상 선택
        # driver.find_element(By.XPATH, '//*[@id="loan"]').send_keys() #융자금   

    if basic_manager == '별도' and obinfo_type1 != '토지':
        driver.find_element(By.XPATH, '//*[@id="mnexYn1"]').click()
        driver.find_element(By.XPATH, '//*[@id="mnex"]').send_keys(basic_mmoney) #월관리비



#매물정보
    if obinfo_type1 in ['주택']:
        #건물유형 (건물일부/건물전체)
        find_Maintag('//*[@id="div_disabled_04"]/fieldset/table/tbody/tr[2]/th','label', '건물유형', '//*[@id="div_disabled_04"]/fieldset/table/tbody/tr[2]/td/label[2]', 'click', '건물 전체')
        # print("건물유형 th태그내 label:", driver.find_element(By.XPATH, '//*[@id="div_disabled_04"]/fieldset/table/tbody/tr[2]/th//label').text)

        if tr_target=='건물':
            if tr_range=='전체':
                # print("연면적 th태그내 span개수:", len(driver.find_elements(By.XPATH, '//*[@id="spc1_mark"]//span')))
                if obinfo_type2 in ['다가구','단독']:
                    find_Maintag('//*[@id="spc1_mark"]','span', '연면적', '//*[@id="spc1"]', 'input', building_totarea) #연면적
                    find_Maintag('//*[@id="spc2_mark"]','span','대지면적','//*[@id="spc2"]','input',land_totarea) #대지면적
                    find_Maintag('//*[@id="spc3_mark"]','span','건축면적','//*[@id="spc3"]','input',building_archarea) #건축면적
                    # find_Maintag('//*[@id="spc4_mark"]','span','전용면적','//*[@id="spc4"]','input','0') #건물 전용면적
                    find_Maintag('//*[@id="floor1_mark"]','span','지상총층수','//*[@id="floor1"]','input', building_grndflr) #지상총층
                    find_Maintag('//*[@id="floor2_mark"]','span','지하총층수','//*[@id="floor2"]','input', building_ugrndflr) #지하총층
                #[지하총층수]는 필수항목입니다. 경고창 닫기
                # time.sleep(5) #알람창이 뜨는지 확인하기 위한 딜레이타임
                try:
                    WebDriverWait(driver, 0.5).until(EC.alert_is_present())
                    alert = driver.switch_to.alert
                    
                    # # 취소하기(닫기)
                    # alert.dismiss()
                    
                    # 확인하기
                    alert.accept()
                except:
                    print("no alert")  
            #방수(건물)
            #욕실수(건물)
        if tr_target=='층호수':
            # driver.find_element(By.XPATH, '//*[@id="room"]').send_keys(basic_rcount) #방수(호실)
            find_Maintag('//*[@id="div_disabled_04"]/fieldset/table/tbody/tr[10]/th[1]','label','방수','//*[@id="room"]','input', basic_rcount) #방수(호실)
            # driver.find_element(By.XPATH, '//*[@id="restroom"]').send_keys(basic_bcount) #욕실수(호실)
            find_Maintag('//*[@id="div_disabled_04"]/fieldset/table/tbody/tr[10]/th[2]','label','욕실수','//*[@id="restroom"]','input', basic_bcount) #욕실수(호실)
            find_Maintag('//*[@id="floor1"]','span','해당층','//*[@id="spc4"]','input', basic_floor) #해당층
            find_Maintag('//*[@id="floor2"]','span','총층수','//*[@id="spc4"]','input', basic_totflr) #총층수
            #층노출동의여부

    if obinfo_type1 in ['상가점포','사무실']:
        if tr_target=='층호수':
            if basic_area2 == '': basic_area2 = basic_area1
            find_Maintag('//*[@id="spc1_mark"]','span','임대(계약)면적','//*[@id="spc1"]','input', basic_area2) #호실 공급면적
            find_Maintag('//*[@id="spc2_mark"]','span','전용면적','//*[@id="spc2"]','input', basic_area1) #호실 전용면적
            find_Maintag('//*[@id="floor1_mark"]','span','해당층','//*[@id="floor1"]','input', basic_floor) #해당층
            find_Maintag('//*[@id="floor2_mark"]','span','총층','//*[@id="floor2"]','input', basic_totflr) #총층수
       
    if obinfo_type1 != '토지':
        #방향기준/방향
        if tr_target == '층호수':
            print("방향기준(호실): ", r_direction); 
            if r_direction == '안방': driver.find_element(By.XPATH, '//*[@id="direction"]').send_keys('안방') #방향기준
            driver.find_element(By.XPATH, '//*[@id="direction"]').send_keys(room_direction) #호실방향(방향)
        # if tr_target == '건물':
        #     print("방향기준(건물): ", b_direction); 
        #     if b_direction == '안방': driver.find_element(By.XPATH, '//*[@id="direction"]').send_keys('안방') #방향기준
        #     driver.find_element(By.XPATH, '//*[@id="direction"]').send_keys(building_direction) #건물방향(방향)

        if building_pn > 0 : driver.find_element(By.XPATH, '//*[@id="parkingpsbl"]').send_keys('가능') #주차가능여부
        print("총주차대수: ",building_pn); driver.find_element(By.XPATH, '//*[@id="parking"]').send_keys(building_pn) #총주차대수
        # find_Maintag('//*[@id="div_disabled_04"]/fieldset/table/tbody/tr[18]/th','label','건축물용도','//*[@id="lawUsageCode"]','option',building_purpose) #건축물용도
        driver.find_element(By.XPATH, '//*[@id="lawUsageCode"]').send_keys(building_purpose) #건축물용도
        usedate = building_usedate.split("-")
        driver.find_element(By.XPATH, '//*[@id="cdate_yy"]').send_keys(usedate[0]) #건축물일자 년
        driver.find_element(By.XPATH, '//*[@id="cdate_mm"]').send_keys(usedate[1]) #건축물일자 월
        driver.find_element(By.XPATH, '//*[@id="cdate_dd"]').send_keys(usedate[2]) #건축물일자 일 
#시설정보
        #난방정보(개별난방 임의선택)
        driver.find_element(By.XPATH, '//*[@id="heat"]').send_keys('개별난방')
        #난방연료(도시가스 임의선택)
        driver.find_element(By.XPATH, '//*[@id="fuel"]').send_keys('도시가스')
        #시설옵션선택
        option_lis = driver.find_elements(By.XPATH, '//*[@id="div_disabled_06"]//li/label')
        print("Options: ", options)
        # options = "스탠드에어컨,인터폰,사설경비,베란다,엘리베이터"
        object_opts = options.split(',')

        for opt in object_opts:
            for li in option_lis:
                if li.text == opt:
                    print(li.text, opt)
                    WebDriverWait(driver, 5).until(EC.element_to_be_clickable(li)).click()
                    # print("--------------------") 
    else:
        print("토지 대지면적:", land_totarea)
        find_Maintag('//*[@id="spc1_mark"]','span','대지면적','//*[@id="spc1"]','input',land_totarea) #대지면적


    # pyautogui.alert("계속 하시겠습니까?")        
        
    # if obinfo_type1 in ['토지']:
    #     driver.find_element(By.XPATH, '//*[@id="spc1"]').send_keys(land_totarea) #대지면적

    # find_Maintag('//*[@id="spc1"]','span','계약면적','//*[@id="spc4"]','input', basic_area2) #계약면적

    # if r_direction == '안방': driver.find_element(By.XPATH, '//*[@id="direction"]').send_keys('안방') #방향기준
    # driver.find_element(By.XPATH, '//*[@id="direction"]').send_keys(room_direction) #호실방향(방향)
    # if building_pn > 0 : driver.find_element(By.XPATH, '//*[@id="parkingpsbl"]').send_keys('가능') #주차가능여부
    # print("총주차대수: ",building_pn); driver.find_element(By.XPATH, '//*[@id="parking"]').send_keys(building_pn) #총주차대수
    # find_Maintag('//*[@id="div_disabled_04"]/fieldset/table/tbody/tr[18]/th','label','건축물용도','//*[@id="lawUsageCode"]/option','option',building_purpose) #건축물용도
    # usedate = building_usedate.split("-")
    # driver.find_element(By.XPATH, '//*[@id="cdate_yy"]').send_keys(usedate[0]) #건축물일자 년
    # driver.find_element(By.XPATH, '//*[@id="cdate_mm"]').send_keys(usedate[1]) #건축물일자 월
    # driver.find_element(By.XPATH, '//*[@id="cdate_dd"]').send_keys(usedate[2]) #건축물일자 일  

    # if tr_range == '전체': 
    #     find_Maintag('//*[@id="spc1_mark"]','span', '연면적', '//*[@id="spc1"]', 'input', building_totarea)   #연면적
    #     find_Maintag('//*[@id="spc2_mark"]','span','대지면적','//*[@id="spc2"]','input',land_totarea) #대지면적
    #     find_Maintag('//*[@id="spc3_mark"]','span','건축면적','//*[@id="spc3"]','input',building_archarea) #건축면적
    #     find_Maintag('//*[@id="floor1_mark"]','span','지상총층수','//*[@id="floor1"]','input', building_grndflr) #지상총층
    #     find_Maintag('//*[@id="floor2_mark"]','span','지하총층수','//*[@id="floor2"]','input', building_ugrndflr) #지하총층


    # if tr_target == '층호수':
    #     find_Maintag('//*[@id="floor1"]','span','해당층','//*[@id="spc4"]','input', basic_floor) #해당층
    #     find_Maintag('//*[@id="floor2"]','span','총층수','//*[@id="spc4"]','input', basic_totflr) #총층수
    #     #층노출동의여부
    #     find_Maintag('//*[@id="room"]','span','방수','//*[@id="spc4"]','input', basic_rcount) #방수(호실)
    #     find_Maintag('//*[@id="restroom"]','span','욕실수','//*[@id="spc4"]','input', basic_bcount) #욕실수(호실)

    # if obinfo_type1 in ['주택']:
    #     if tr_range == '전체': 
        
    #         driver.find_element(By.XPATH, '//*[@id="maemul_type2"]').click()
    #         driver.find_element(By.XPATH, '//*[@id="floor1"]').send_keys(building_grndflr) #지상총층
    #         driver.find_element(By.XPATH, '//*[@id="floor2"]').send_keys(building_ugrndflr) #지하총층
    #         #[지하총층수]는 필수항목입니다. 경고창 닫기
    #         # time.sleep(5) #알람창이 뜨는지 확인하기 위한 딜레이타임
    #         try:
    #             WebDriverWait(driver, 3).until(EC.alert_is_present())
    #             alert = driver.switch_to.alert
                
    #             # # 취소하기(닫기)
    #             # alert.dismiss()
                
    #             # 확인하기
    #             alert.accept()
    #         except:
    #             print("no alert")


    #     elif tr_range == '일부':
    #         driver.find_element(By.XPATH, '//*[@id="floor1"]').send_keys(basic_floor) #해당층
    #         driver.find_element(By.XPATH, '//*[@id="floor2"]').send_keys(basic_totflr) #총층수
    #     #공급면적

    #     if obinfo_ttype == '전세' or obinfo_ttype == '월세':
    #         driver.find_element(By.XPATH, '//*[@id="spc1"]').send_keys(basic_area2) #계약면적
    #     time.sleep(0.5)
    #     # driver.find_element(By.XPATH, '//*[@id="spc2"]').send_keys() #전용면적
    #     #대지지분

    #     #층노출동의여부
    #     if tr_target == '층호수':
    #         driver.find_element(By.XPATH, '//*[@id="room"]').send_keys(basic_rcount) #방수(호실)
    #         driver.find_element(By.XPATH, '//*[@id="restroom"]').send_keys(basic_bcount) #욕실수(호실)
    #         print("방향기준(호실): ", r_direction); 
    #         if r_direction == '안방': driver.find_element(By.XPATH, '//*[@id="direction"]').send_keys('안방') #방향기준
    #         driver.find_element(By.XPATH, '//*[@id="direction"]').send_keys(room_direction) #호실방향(방향)

    #     # print("방향기준(건물): ", b_dibection); 
    #     # if b_direction == '안방': driver.find_element(By.XPATH, '//*[@id="direction"]').send_keys('안방') #방향기준
    #     # driver.find_element(By.XPATH, '//*[@id="direction"]').send_keys(building_direction) #건물방향(방향)

    #     #복층여부
    #     if building_pn > 0 : driver.find_element(By.XPATH, '//*[@id="parkingpsbl"]').send_keys('가능') #주차가능여부
    #     print("총주차대수: ",building_pn); driver.find_element(By.XPATH, '//*[@id="parking"]').send_keys(building_pn) #총주차대수
    #     print("건축물용도: ",building_purpose); driver.find_element(By.XPATH, '//*[@id="lawUsageCode"]').send_keys(building_purpose) #건축물용도
    #     usedate = building_usedate.split("-")
    #     driver.find_element(By.XPATH, '//*[@id="cdate_yy"]').send_keys(usedate[0]) #건축물일자 년
    #     driver.find_element(By.XPATH, '//*[@id="cdate_mm"]').send_keys(usedate[1]) #건축물일자 월
    #     driver.find_element(By.XPATH, '//*[@id="cdate_dd"]').send_keys(usedate[2]) #건축물일자 일   





#중개업소정보
    time.sleep(0.5)
    print("관리자메모: ", basic_secret)
    driver.find_element(By.XPATH, '//*[@id="admin_memo"]').send_keys(basic_secret) #관리자메모

#의뢰인 정보
    #등기부상의 소유자명
    #소유자와의 관계

#개인정보동의
    driver.find_element(By.XPATH, '//*[@id="agreeNaver"]').click()

    # time.sleep(60)
    pyautogui.alert("작업을 종료하시겠습니까?")
    driver.close()
    return errarr