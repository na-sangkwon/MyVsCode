from selenium import webdriver
from selenium.webdriver import ActionChains

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
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
    location_do = data['landData']['land_do']
    # if location_do.endswith('도'):
    #     if '경상남도' in location_do:
    #         location_do = '경남'
    #     elif '경상북도' in location_do:
    #         location_do = '경북'
    #     elif '충청남도' in location_do:
    #         location_do = '충남'
    #     elif '충청북도' in location_do:
    #         location_do = '충북'
    #     elif '전라남도' in location_do:
    #         location_do = '전남'
    #     elif '전라북도' in location_do:
    #         location_do = '전북'
    #     else:
    #         location_do = location_do[:-1]
    location_si = data['landData']['land_si']
    location_dong = data['landData']['land_dong']

    location_lijibun = (data['type_path'] + data['landData']['land_jibun']) if data['landData']['land_li'] == '' else (data['landData']['land_li'] + data['type_path'] + data['landData']['land_jibun'])
    location_dongli = (data['landData']['land_dong'] + data['type_path'] + data['landData']['land_jibun']) if data['landData']['land_li'] == '' else location_lijibun
    location_building = '' if data['buildingData']['building_name'] == '' else ' ' + data['buildingData']['building_name']
    location_room = '' if data['roomData']['room_num'] == '' else ' ' + data['roomData']['room_num']
    location_detail = location_dongli + location_building + location_room

    obang_code = data['writeData']['obang_code'] #오방매물번호
    obinfo_type = ''
    if data['writeData']['object_type'] == '주거용':
        if data['roomData']['room_rcount'] == '1':
            obinfo_type = '원룸'
        elif data['roomData']['room_rcount'] >= '2':
            obinfo_type = '투룸/쓰리룸+'
    elif data['writeData']['object_type'] == '상업용':
        obinfo_type = '상가/사무실'
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
    basic_area1 = data['roomData']['room_area1'] #실면적
    basic_area2 = data['roomData']['room_area2'] #공급면적
    basic_floor = data['roomData']['room_floor'] #해당층
    basic_totflr = str(int(data['buildingData']['building_grndflr']) + int(data['buildingData']['building_ugrndflr'])) #전체층
    secret_1 = '' if data['writeData']['tr_memo'] == '' else data['writeData']['tr_memo'] + Keys.ENTER
    secret_2 = '' if data['landData']['land_memo'] == '' else data['landData']['land_memo'] + Keys.ENTER
    secret_3 = '' if data['buildingData']['building_memo'] == '' else data['buildingData']['building_memo'] + Keys.ENTER
    secret_4 = '' if data['roomData']['room_memo'] == '' else data['roomData']['room_memo'] + Keys.ENTER
    basic_secret = secret_1 + secret_2 + secret_3 + secret_4 #비밀메모

    add_warmer = '' #data['writeData']['add_warmer'] 난방
    add_rdate = str(data['writeData']['rdate']) #입주일
    add_usedate = str(data['buildingData']['building_usedate']) #준공일
    add_pn = data['buildingData']['building_pn'] #주차
    add_options = data['roomData']['room_option'] #옵션선택

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
    print("92 ok?")



#기본정보
    #매물종류
    objectCheckTime()
    #주거용&방개수1 => 원룸, 상업용
    #거래종류
    #보증금O/월세O=>월세, 보증금O/월세X=>전세, 보증금X/월세X/매매금O=>매매

    time.sleep(20)
    print(location_do, location_si, location_dongli)
    driver.find_element(By.XPATH, '//*[@id="lcode_si"]').send_keys(location_do) # 
    time.sleep(1); print("si ok")
    driver.find_element(By.XPATH, '//*[@id="lcode_gu"]').send_keys(location_si) # 
    time.sleep(1); print("do ok")
    driver.find_element(By.XPATH, '//*[@id="lcode_dong"]').send_keys(location_dong) # 
    time.sleep(1); print("dong ok")
    if driver.find_element(By.XPATH, '//*[@id="ri"]'): driver.find_element(By.XPATH, '//*[@id="ri"]').send_keys(location_dong) # 
    time.sleep(1); print("li ok")

    time.sleep(20)
#     if obang_code == '' :
#         # 이동한 페이지 기다리기 + 불러오기 나올경우 취소
#         WebDriverWait(driver, 5)
#         try:
#             driver.find_element(By.XPATH, '//*[@id="temp_check_dialog"]/div/div[2]/div/button[2]').click()
#         except:
#             pass

        
#         print("105 pass")
        
#         # Alert 처리
#         try:
#             alert = WebDriverWait(driver, 2).until(EC.alert_is_present())
#             alert_text = alert.text
#             alert.accept()
#         except:
#             pass

#         #
#         WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/div[2]/div/div/div/h3')))

#         print("118 pass")

#         # 제일 큰 output찾기


#         # 위치정보


#         # 주소찾기로 주소선택

#         driver.find_element(By.XPATH, '//*[@id="product_form"]/div[1]/div[1]/div[2]/div/div[1]/div[1]/div[2]/button').click()

#         WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="label_text"]')))
#         time.sleep(1)

#         sidos = driver.find_elements(By.XPATH, '//*[@id="sido_section"]/ul/li/div/button')
#         for sido in sidos:
#             if sido.text == location_do:
#                 sido.click()
#                 time.sleep(0.5)
#                 guguns = driver.find_elements(By.XPATH, '//*[@id="gugun_section"]/ul/li/div/button')
#                 for gugun in guguns:
#                     if gugun.text == location_si:
#                         gugun.click()
#                         time.sleep(0.5)
#                         dongs = driver.find_elements(By.XPATH, '//*[@id="dong_section"]/ul/li/div/button')
#                         for dong in dongs:
#                             if dong.text == location_dong:
#                                 dong.click()
#                                 break

#         driver.find_element(By.XPATH, '//*[@id="address"]').send_keys(location_lijibun) # 상세주소 1
#         driver.find_element(By.XPATH, '//*[@id="address_unit"]').send_keys(location_detail) # 상세주소 2
#         driver.find_element(By.XPATH, '//*[@id="get_coord"]').click() # 위치검색 클릭

#         sele = {
#         '원룸': [11, ['오픈형', '분리형', '통1.5룸', '1.5룸', '1.8룸']],
#         '투룸/쓰리룸+': [12, ['투룸', '쓰리룸+']],
#         '상가/사무실': [16, ['상가', '사무실']],
#         '오피스텔': [13, []],
#         '아파트': [14, []],
#         '주택/고급빌라': [15, []],
#         '공장/창고': [17, []],
#         '토지': [18, []],
#         '통건물': [19, ['상업용건물','상가주택','다가구주택','다세대주택','오피스텔','단독주택','도시형생활주택','주상복합건물','지식산업센터',]],
#         }

#         WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="product_form"]/div[1]/div[2]/div[2]/div[1]/div[2]/div[2]/div')))
#         #매물정보
#         objType = data['writeData']['object_type']
#         for 매물 in driver.find_elements(By.NAME, 'category'):
#             if 매물 == objType:
#                 매물.click()
#         if obinfo_type != '':
#             driver.find_element(By.ID, f'category_{sele[obinfo_type][0]}').click() #매물 종류
#             if len(sele[obinfo_type][1]) != 0: driver.find_element(By.ID, f'category_{sele[obinfo_type][0]}').click() # 소분류
#         # driver.find_element(By.ID, f'category_{sele["원룸"][0]}').click() # 거래종류
#         driver.find_element(By.XPATH, '//*[@id="monthly_rent_deposit"]').send_keys(obinfo_deposit1) #보증금1
#         driver.find_element(By.XPATH, '//*[@id="monthly_rent_price"]').send_keys(obinfo_rent1) #월세1
#         # 관리내역
#         관리내역s = driver.find_elements(By.XPATH, '//*[@id="mgr_include_checkbox"]/input')
#         #물건의 관리비포함내역
#         관리내역ex = basic_mlist.split(',')
#         try:
#             for item in 관리내역ex:
#                 for 관리내역 in 관리내역s:
#                     if item in 관리내역.get_attribute("value"):
#                         관리내역.click()
#                         break
#         except:
#             print(관리내역ex)

#         # 거래종류
#         for a in driver.find_elements(By.XPATH, '//*[@id="product_form"]/div[1]/div[2]/div[2]/div[3]/div[2]/div/div'):
#             print(a.text)
#             if a.text == obinfo_ttype: 
#                 a.click()


#         # 비공개 선택
#         driver.find_element(By.XPATH, '//*[@id="product_form"]/div[1]/div[2]/div[2]/div[7]/div/div/label[2]').click()

#         # 기본정보
#         if data['writeData']['manager'] == '별도' and data['writeData']['mmoney'] != '':
#             driver.find_element(By.XPATH, '//*[@id="mgr_price"]').send_keys(basic_mmoney) # 관리비
#         if not driver.find_element(By.XPATH, '//*[@id="real_area"]'):driver.find_element(By.XPATH, '//*[@id="real_area"]').send_keys(basic_area1) # 실면적
#         if not driver.find_element(By.XPATH, '//*[@id="law_area"]'):driver.find_element(By.XPATH, '//*[@id="law_area"]').send_keys(basic_area2) # 공급면적
#         driver.find_element(By.XPATH, '//*[@id="current_floor"]').send_keys(basic_floor) # 해당층
#         driver.find_element(By.XPATH, '//*[@id="total_floor"]').send_keys(basic_totflr) # 전체층
#         driver.find_element(By.XPATH, '//*[@id="info_base"]/div[2]/div[13]/div[2]/textarea').send_keys(basic_secret) # 비밀메모

#         if not driver.find_element(By.XPATH, '//*[@id="heating"]'):driver.find_element(By.XPATH, '//*[@id="heating"]').send_keys("개별가스난방") # 난방
#         driver.find_element(By.XPATH, '//*[@id="enter_year"]').send_keys(add_rdate) # 입주일
#         if not driver.find_element(By.XPATH, '//*[@name="build_year"]'):driver.find_element(By.XPATH, '//*[@name="build_year"]').send_keys(add_usedate) # 준공일
        
#         #테마

#         # #옵션선택
#         # options = add_options.split(',') #옵션을 리스트로 분리
#         # given_optionbox = driver.find_element(By.XPATH, '//*[@id="option"]/div/label[1]')
#         # for option in options:
#         #     if option == given_item:


#         time.sleep(0.5)

#         # 사진
#         filePath = driver.find_element(By.XPATH, '//*[@id="product_form"]/div[1]/div[9]/div[2]/div[1]/div/div').get_attribute("outerHTML").split('<input id="')[1].split('" t')[0]
        
#         import os

#         try:
#             main_dir = 'Z:\\업무자료\\4사진자료&이미지자료(외부유출금지)\\1주거용물건, 상업용물건\\'
#             path_dir = main_dir + data['folderPath'] #'경기도\\오산시\\궐동\\654-9\\썬플라워\\1층\\1층'
#             print(path_dir)
#             # path_dir = '/Users/ksj/Desktop/python/imagea'
#             try:
#                 file_list = os.listdir(path_dir)
#                 arr = []
#                 for filename in file_list:
#                     if "output" in filename: arr.append(filename.split('output')[1])

#                 if len(arr) == 0:
#                     arr2 = []
#                     for file in file_list:
#                         if file.endswith('.jpeg') or file.endswith('.gif') or file.endswith('.png') or file.endswith('.jpg'):
#                             arr2.append(file)
#                     if len(arr2) == 0:
#                         driver.execute_script('return document.getElementById("is_speed").click()')
#                         pass


#                 path = path_dir + "/output" + max(arr)

#                 photo_list = []

#                 for file in os.listdir(path):
#                     if file.endswith('.jpeg') or file.endswith('.gif') or file.endswith('.png') or file.endswith('.jpg'):
#                         photo_list.append(file)

#                 for photo in photo_list:
#                     file_path = path + '/' + photo
#                     driver.find_element(By.ID, filePath).send_keys(file_path)
#             except: 
#                 driver.execute_script('return document.getElementById("is_speed").click()')
#                 print("사진 오류")
#                 pass
#         except:
#             print("폴더 오류", data['folderPath'])
#             driver.execute_script('return document.getElementById("is_speed").click()')
#             errarr.append("폴더 오류")
#             pass


#         time.sleep(120)
#         driver.close()
#         return errarr
    
#     else:

#         try:
#             import datetime

#             # WebDriverWait(driver, 10).until(EC.element_to_be_clickable(By.CSS_SELECTOR, "#search_id")).clear() #매물번호 입력창의 입력값 초기화
#             driver.implicitly_wait(10)
#             driver.find_element(By.CSS_SELECTOR, "#search_id").clear() 
#             print("1", obang_code)
#             driver.find_element(By.CSS_SELECTOR, "#search_id").send_keys(obang_code) #매물번호입력창에 매물번호 입력
#             print("2")
#             driver.find_element(By.CSS_SELECTOR, "#admin_member_id > option:nth-child(1)").click() #담당자를 직원별로 선택
#             print("3")
#             driver.find_element(By.CSS_SELECTOR, "#go_keyword").click() #검색버튼(돋보기) 클릭
#             print("4")
#             # WebDriverWait(driver, 10).until(EC.presence_of_element_located(By.CSS_SELECTOR, "#tr_20052 > td:nth-child(14) > div:nth-child(1)"))
#             # time.sleep(2)

#             #업데이트 실행
#             driver.find_element(By.CSS_SELECTOR, f'#tr_{obang_code} > td:nth-child(14) > div:nth-child(1)').click() #관리 클릭
#             print("5")
#             # time.sleep(1)
#             driver.find_element(By.CSS_SELECTOR, f'#tr_{obang_code} > td:nth-child(14) > div.dropdown.open > ul > li:nth-child(1)').click() #수정 클릭
#             print("6 완료")

#             #보증금1
#             if obinfo_deposit1 != '' : modify_item(driver, "#monthly_rent_deposit", obinfo_deposit1)
#             #월세1
#             if obinfo_rent1 != '' : modify_item(driver, "#monthly_rent_price", obinfo_rent1)
#             #매매
#             print("obinfo_trading: "+obinfo_trading)
#             if obinfo_trading != '' : modify_item(driver, "#sell_price", obinfo_trading)

#             #관리비
#             if basic_manager=='별도':
#                 modify_item(driver, "#mgr_price", basic_mmoney)
            
#             #실면적
#             if basic_area1 != '' : modify_item(driver, "#real_area", basic_area1)
#             #해당층
#             if basic_floor != '' : modify_item(driver, "#current_floor", basic_floor)
#             #전체층
#             modify_item(driver, "#total_floor", basic_totflr)
        
#             # print("오방 매물(" + obang_code + ")정보 수정기능 추가예정")
#             time.sleep(20)
#             driver.close()
#             return errarr




#         except Exception as e:
#             print("에러 발생:", str(e))
#             # print(obang_code,"업데이트 안됨")
#             print(f"{obang_code}업데이트 안됨")


# def modify_item(driver, selector , value=''):
#     element = driver.find_element(By.CSS_SELECTOR, selector)
#     # element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
#     if element:
#         try:
#             element.clear()
#         except Exception as e:
#             print(selector+"클리어 에러 발생:", str(e))
#             pass
#             # print(selector+" 수정안됨")

#         try:
#             element.send_keys(value)
#             print(selector+" 수정완료")
#         except Exception as e:
#             print(selector+"입력에러 발생:", str(e))
#             pass