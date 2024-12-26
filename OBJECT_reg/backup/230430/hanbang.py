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
    location_do = data['landData']['land_do']
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
        else:
            location_do = location_do[:-1]
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
    obinfo_type1 = data['writeData']['object_type1']
    obinfo_type2 = data['writeData']['object_type2']
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
    pyautogui.alert("매물종류를 변경해주세요")
    # # 매물종류 변경버튼 클릭
    # WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#formAddress > div.top_basic_box > div.base_info_option > ul > li.bx.view.pt5 > div > a'))).click()
    
    # #거래구분
    # driver.find_element(By.XPATH, '//*[@id="formAddress"]/div[2]/div[2]/ul/li[2]/div/ul/li[1]/div/div/div').click()
    # time.sleep(0.5)
    # current_window_handle = driver.current_window_handle
    # popup_window_handle = None
    # for handle in driver.window_handles:
    #     if handle != current_window_handle:
    #         popup_window_handle = handle
    #         break
    # driver.switch_to.window(popup_window_handle)
    # tests = driver.find_elements(By.XPATH, '//*[@id="dialog_1682770268429"]/div/div/ul/li/div/ul/li')
    # print("길이: ", len(tests)) 
    # # driver.find_element(By.XPATH, '//*[@id="in_gure_cd_name"]').send_keys('전세')
    # driver.switch_to.window(current_window_handle)

    # #매물종류 선택
    
    # if obinfo_type1 == '사무실': ob_type = '사무실'
    # # iframe 전환
    # frame_element = driver.find_element(By.CLASS_NAME, '.iframe_content')
    # driver.switch_to.frame(frame_element)
    # # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, f'/html/body/div[5]')))
    # # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, f'//*[@id="dialog_1682762396676"]/div/div/ul/li/div[//span[text()="{ob_type}"]]'))).click()
    # ob_items = driver.find_elements(By.XPATH, '//*[@id="dialog_1682762396676"]/div/div/ul/li/div/ul/li')
    # print("길이: ", len(ob_items)) 
    # for ob_item in ob_items:
    #     print("ob_items: ", ob_items)
    #     if ob_item.text == ob_type:
    #         ob_item.click()
    # print(ob_type, "작업완료")


    # time.sleep(5)
    # driver.find_element(By.XPATH, '//*[@id="in_sido_name"]').click() #시/도 선택

    # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[5]/div[2]')))
    # driver.find_element(By.XPATH, f'//*[@id="dialog_1682762396676"]/div/div/ul/li/div[//span[text()="{obinfo_ttype}"]]').click()   


#     # # 로그인확인겸 첫 파란등록버튼 기다리기(준회원으로 로그인시)
#     # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/div[2]/div/div[1]/div/div/div/div/span[1]/button')))
    # if driver.find_element(By.XPATH, '//*[@id="H_header"]/div/div[1]/h1/a/img').is_displayed(): driver.get('https://mobile.karhanbang.com/kren/mamul/regist')

    time.sleep(10)
    driver.close()
    return errarr
    # input()