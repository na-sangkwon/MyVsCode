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
    location_si = data['landData']['land_si']
    location_dong = data['landData']['land_dong']

    location_lijibun = (data['landData']['land_type'] + data['landData']['land_jibun']) if data['landData']['land_li'] == '' else (data['landData']['land_li'] + data['landData']['land_type'] + data['landData']['land_jibun'])
    location_dongli = (data['landData']['land_dong'] + data['landData']['land_type'] + data['landData']['land_jibun']) if data['landData']['land_li'] == '' else location_lijibun
    location_building = '' if data['buildingData']['building_name'] == '' else ' ' + data['buildingData']['building_name']
    location_room = '' if data['roomData']['room_num'] == '' else ' ' + data['roomData']['room_num']
    location_detail = location_dongli + location_building + location_room

    obang_code = data['writeData']['obang_code'] #오방매물번호
    obinfo_type = ''
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
    if obinfo_type2 == '아파트':
        obinfo_type = '아파트'
    elif obinfo_type2 == '다가구':
        obinfo_type = '다가구'
    elif obinfo_type2 == '다세대':
        obinfo_type = '다세대'
    elif obinfo_type2 == '상가주택':
        obinfo_type = '상가주택'
    elif obinfo_type2 == '상가점포':
        obinfo_type = '상가점포'
    elif obinfo_type2 == '사무실':
        obinfo_type = '사무실'
    elif obinfo_type2 == '단독':
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
    print("basic_floor: ", basic_floor)
    driver.execute_script("openPopupCurrFloor()") #js코드로 openPopupCurrFloor 실행
    driver.execute_script(f"selValues({basic_floor},{basic_floor},'in_curr_floor')") #js코드로 selValues 실행

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
