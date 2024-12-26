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
from datetime import datetime, date
import time
import os

options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
        
def macro(data, user):
    
    def change_window(target: str):
        if target == 'parent':
            # child window close
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        elif target == 'child':
            driver.switch_to.window(driver.window_handles[1])
        else:
            print("Wrong target!")
    
    def reNaming_commalist(commalist):
        # 이름을 바꿀 매핑 딕셔너리 생성
        name_mapping = {
            '개별수도': '수도',
            '유선': 'TV',
            '전자렌지': '전자레인지',
            '전자요금': '전기세'
        }
        # 이름들을 쉼표로 분리하여 리스트로 변환
        names = commalist.split(',')    
        # 이름을 매핑된 이름으로 변경
        new_names = [name_mapping.get(name.strip(), name.strip()) for name in names]
        # 변경된 이름들을 다시 쉼표로 연결하여 문자열로 생성
        new_commalist = ','.join(new_names)
        return new_commalist              
    
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
    
    def clickLabel(div_selector, item_list): 
        print("item_list:", item_list)       
        # CSS_SELECTOR 사용하여 해당 div 태그를 찾습니다.
        div_element = driver.find_element(By.CSS_SELECTOR, f'{div_selector}')
        # div 태그 내의 모든 label 태그를 찾습니다.
        label_elements = div_element.find_elements(By.TAG_NAME, 'label')
        # 텍스트가 item 값인 label 태그를 찾아 클릭합니다.
        items = item_list.split(',')
        for item in items:
            try:
                for label in label_elements:
                    span_element = label.find_element(By.TAG_NAME, 'span')
                    # print(span_element.text, item)
                    if span_element.text == item:
                        label.click()
                        break  # 원하는 label을 찾았으므로 반복문을 종료합니다.
            except Exception as e:
                print("라벨선택 오류:", str(e))    
                

    errarr = []
    
    # 현재 날짜 출력
    current_date = date.today()
    formatted_date = current_date.strftime("%Y-%m-%d")
    
    admin_name = data['adminData']['admin_name']
    request_code = data['writeData']['request_code'] #의뢰번호
    
    location_do = data['landData'][0]['land_do']
    location_si = data['landData'][0]['land_si']
    location_dong = data['landData'][0]['land_dong']

    location_lijibun = (data['type_path'] + data['landData'][0]['land_jibun']) if data['landData'][0]['land_li'] == '' else (data['landData'][0]['land_li'] + data['type_path'] + data['landData'][0]['land_jibun'])
    location_dongli = (data['landData'][0]['land_dong'] + data['type_path'] + data['landData'][0]['land_jibun']) if data['landData'][0]['land_li'] == '' else location_lijibun
    location_detail = location_dongli
    total_location = location_do+" "+location_si+" "+location_detail
    print('주소(total_location):',total_location)
    
    building_purpose = data['buildingData']['building_purpose']
    
    # obinfo_trading = data['writeData']['trading'] #매매금액    
    obinfo_deposit1 = data['writeData']['deposit1'] #보증금1
    # obinfo_deposit2 = data['writeData']['deposit2'] #보증금2
    # obinfo_deposit3 = data['writeData']['deposit3'] #보증금3
    obinfo_rent1 = data['writeData']['rent1'] #월세1
    # obinfo_rent2 = data['writeData']['rent2'] #월세2
    # obinfo_rent3 = data['writeData']['rent3'] #월세3
    
    total_floor = str(int(data['buildingData']['building_grndflr']) + int(data['buildingData']['building_ugrndflr']))+"층" #전체층
    room_floor = "반지하" if data['roomData']['room_floor'] == '-1' else str(int(data['roomData']['room_floor']))+"층" #해당층
    request_term1 = data['writeData']['request_term1'] #계약기간하한
    request_term2 = data['writeData']['request_term2'] #계약기간상한
    room_area1 = data['roomData']['room_area1'] #실면적
    room_bcount = data['roomData']['room_bcount']+"개" if data['roomData']['room_bcount'] != '' and data['roomData']['room_bcount'] != '0' else '선택' #욕실수
    room_direction = data['roomData']['room_direction'] if data['roomData']['room_direction']!='' else '선택' #호실방향
    building_usedate = data['buildingData']['building_usedate'] #사용승인일
    building_parking = data['buildingData']['building_parking'] #주차장유무
    building_option = data['buildingData']['building_option'] #건물옵션
    mmoney = data['writeData']['mmoney'] #관리비
    manager = data['writeData']['manager'] #관리비 별도/포함/미확인
    mlist = data['writeData']['mlist'] #관리비포함내역
    mlist = mlist.replace('유선','TV')
    mlist = mlist.replace('개별수도','수도')
    room_option = data['roomData']['room_option'] #호실옵션
    room_option = room_option.replace('가스렌지','가스레인지')
    room_option = room_option.replace('벽걸이에어컨','에어컨')
    rdate = str(data['writeData']['rdate']) #입주일
    secret_memo = "https://obangkr.cafe24.com/web/request/request_view/view_give_request_detail.php?request_code="+request_code
    

    print("데이터확인:", building_purpose)
    
    
    
    # ChromeDriver 경로 설정
    driver = webdriver.Chrome(options=options)
    # driver = webdriver.Chrome('/chromedriver', options=options)
    # driver = webdriver.Chrome(ChromeDriverManager().install())

    # URL 열기
    driver.maximize_window()
    driver.get('https://ceo.zigbang.com/?was_slept=False&agree=True')

    driver.find_element(By.XPATH, '/html/body/div[1]/section/div[1]/div[2]/div[2]/div[1]/form/input[2]').send_keys("nasangkwon@outlook.kr")
    driver.find_element(By.XPATH, '/html/body/div[1]/section/div[1]/div[2]/div[2]/div[1]/form/input[3]').send_keys("dhqkd5555%")
    driver.find_element(By.XPATH, '/html/body/div[1]/section/div[1]/div[2]/div[2]/div[1]/form/div[2]/button').click()
    
    driver.implicitly_wait(10)   
    
    # 확인후 이동
    driver.get('https://ceo.zigbang.com/items/list/oneroom')
    

    # #활성화된 모든 팝업창 닫기
    # window_handles = driver.window_handles # 현재 열린 모든 창의 핸들을 가져옴
    # for handle in window_handles: # 메인 창을 제외한 모든 팝업 창을 닫음
    #     if handle != driver.current_window_handle:
    #         pyautogui.alert("popup go??")
    #         driver.switch_to.window(handle)
    #         driver.close()
    # driver.switch_to.window(driver.window_handles[0]) # 다시 메인 창으로 전환
    
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/div[2]/button'))).click()
    
    # pyautogui.alert("1go??")    
    
    # # '오늘하루보이지않음'을 기다림
    # waitbox = WebDriverWait(driver, 10).until(
    #     EC.presence_of_element_located((By.CSS_SELECTOR, "body > div.notice_layer.common_layer.on > div.item_check.has_link > label"))
    # )
    # # '오늘하루보이지않음' 체크
    # waitbox.click()
    # # '닫기버튼'을 기다림
    # closebtn = WebDriverWait(driver, 10).until(
    #     EC.presence_of_element_located((By.CSS_SELECTOR, "body > div.notice_layer.common_layer.on > div.item_check.has_link > button"))
    # )
    # # '닫기버튼' 클릭
    # closebtn.click()
    
    # pyautogui.alert("2go??")
    
    print('담당자:', admin_name)
    # selectOption('//*[@id="react-root"]/article/div[1]/div[1]/div/select', '이은선') #테스트용 담당자 선택
    selectOption('//*[@id="react-root"]/article/div[1]/div[1]/div/select', admin_name) # admin_name 담당자 선택
    
    # driver.find_element(By.XPATH, '//*[@id="react-root"]/article/div[1]/div[1]/div/select').click() #담당자 선택
    # select_element = driver.find_element(By.XPATH, '//*[@id="react-root"]/article/div[1]/div[1]/div/select')
    # # Select 객체를 생성하고 select 엘리먼트를 래핑합니다.
    # select = Select(select_element)
    # try:
    #     select.select_by_visible_text('이은선') #담당자로 본인을 선택하기
    # except Exception as e:
    #     print("담당자선택 오류:", str(e))
        
    driver.find_element(By.XPATH, '//*[@id="react-root"]/article/div[2]/div/button').click() # 배너등록하기 버튼 클릭
    
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/div[2]/button'))).click()
    # pyautogui.alert("go??")
    #건물형태
    driver.find_element(By.XPATH, '//*[@id="react-root"]/article/section/div[2]/div/div[2]/div[2]/a[1]').click() # 원룸형 선택
    
    
    
    time.sleep(0.5)  
    # '주소찾기' 버튼 클릭
    button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="item_form"]/section[1]/div/div/div[2]/div[1]/button'))
    )
    button.click()

    # # iframe으로 전환
    # iframe = WebDriverWait(driver, 10).until(
    #     EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//*[@id="__daum__viewerFrame_1"]'))
    # )
    main_page = driver.current_window_handle #팝업창 생성전의 창
    print("메인창:",driver.title, main_page)
    # #주소찾기 버튼클릭
    # driver.find_element(By.XPATH, '//*[@id="item_form"]/section[1]/div/div/div[2]/div[1]/button').click() 
    handles = driver.window_handles #팝업창을 닫기 전
    print(handles)
    driver.switch_to.window(handles[-1])
    print("현재창 활성화된 창" ,driver.title, driver.current_window_handle)
    # region_name = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="region_name"]')))
    # region_name.send_keys("나상권공인중개사사무소")
    # driver.find_element(By.XPATH, '//*[@id="region_name"]"]').send_keys("ENTER")

    # iframe 내부로 전환
    driver.switch_to.frame('__daum__viewerFrame_1')
    # iframe = WebDriverWait(driver, 10).until(
    #     EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//*[@id="__daum__viewerFrame_1"]'))
    # )
    
    # 텍스트 입력
    input_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="region_name"]')))
    input_box.send_keys(total_location)
    input_box.send_keys(Keys.ENTER)
    
    driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/ul/li/dl/dd[2]/span/button[1]/span[1]').click() #검색된 첫번째 지번주소 클릭
    driver.switch_to.window(handles[0])
    
    print("팝업창 닫히고 활성화된 창" ,driver.title, driver.current_window_handle)
    
    

    # # iframe에서 기본 상태로 전환
    # driver.switch_to.default_content()

    time.sleep(1) 
    #건물종류
    if building_purpose == '단독주택':
        driver.find_element(By.XPATH, '//*[@id="item_form"]/section[2]/div/div[1]/div[2]/div/div[1]/div/label[1]/span').click() #단독주택 클릭
    else:
        driver.find_element(By.XPATH, '//*[@id="item_form"]/section[2]/div/div[1]/div[2]/div/div[1]/div/label[2]/span').click() #그외 클릭
        # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="item_form"]/section[2]/div/div[1]/div[2]/div/div[2]/div/input')))
        driver.find_element(By.XPATH, '//*[@id="item_form"]/section[2]/div/div[1]/div[2]/div/div[2]/div/input').send_keys(building_purpose) # 건축물용도 직접입력
    
    #거래유형/가격
    if obinfo_deposit1 != '' :
        if obinfo_rent1 != '' and obinfo_rent1 != '0':
            driver.find_element(By.XPATH, '//*[@id="item_form"]/section[2]/div/div[2]/div[2]/div[1]/div[1]/div/label[2]/span').click() #월세 클릭
            driver.find_element(By.XPATH, '//*[@id="item_form"]/section[2]/div/div[2]/div[2]/div[1]/div[2]/div/div[1]/div/input').send_keys(obinfo_deposit1) #보증금 입력
            driver.find_element(By.XPATH, '//*[@id="item_form"]/section[2]/div/div[2]/div[2]/div[1]/div[3]/div/div[1]/div/input').send_keys(obinfo_rent1) #월세 입력
            if int(request_term1) < 12:
                driver.find_element(By.XPATH, '//*[@id="item_form"]/section[2]/div/div[2]/div[2]/div[3]/label/input').click() #단기매물 체크박스 클릭
                print("계약기간 "+request_term1+"개월의 단기매물입니다.")
        else:
            driver.find_element(By.XPATH, '//*[@id="item_form"]/section[2]/div/div[2]/div[2]/div[1]/div[1]/div/label[1]/span').click() #전세 클릭
            driver.find_element(By.XPATH, '//*[@id="item_form"]/section[2]/div/div[2]/div[2]/div[1]/div[2]/div/div[1]/div/input').send_keys(obinfo_deposit1) #보증금 입력
                
    #동/호
    #층/구조
    selectOption('//*[@id="item_form"]/section[2]/div/div[4]/div[1]/div[2]/div[1]/div[1]/div/div/div/select', total_floor) #전체층 선택
    selectOption('//*[@id="item_form"]/section[2]/div/div[4]/div[1]/div[2]/div[1]/div[2]/div/div/div/select', room_floor) #해당층 선택
    #전용면적
    if room_area1 != '' : driver.find_element(By.XPATH, '//*[@id="item_form"]/section[2]/div/div[5]/div[2]/div[1]/div[2]/div/div/input').send_keys(room_area1)
    #주실방향
    print("room_direction",room_direction)
    # pyautogui.alert("test ㄱㄱ")
    if room_direction != '선택' : selectOption('//*[@id="item_form"]/section[2]/div/div[6]/div[2]/div/div[1]/div/select', room_direction)
    #화장실수
    print("room_bcount",room_bcount)
    if room_bcount != '' : selectOption('//*[@id="item_form"]/section[2]/div/div[7]/div[2]/div[1]/select', room_bcount)
    #사용승인일
    driver.find_element(By.XPATH, '//*[@id="item_form"]/section[2]/div/div[8]/div[2]/div[1]/div/input').send_keys(building_usedate)
    #사진

    # class_element = driver.find_element(By.CSS_SELECTOR, '#item_form > section:nth-child(10) > div > div:nth-child(2) > div:nth-child(2)')
    # class_name = class_element.get_attribute("class") #item_form > section:nth-child(10) > div > div:nth-child(2) > div.sc-csuQGl.hdlHHX
    # pyautogui.alert('경로확인?'+f'#item_form > section:nth-child(10) > div > div:nth-child(2) > div.{class_name} > div > div:nth-child(1) > div')
    
    #주차
    if building_parking == '있음' : 
        if building_purpose == '단독주택':
            #일반건물 #item_form > section:nth-child(10) > div > div:nth-child(2) > div.sc-csuQGl.hdlHHX > div > div:nth-child(1) > div
            clickLabel('#item_form > section:nth-child(10) > div > div:nth-child(2) > div:nth-child(2) > div > div:nth-child(1) > div', '가능')
            # clickLabel(f'#item_form > section:nth-child(10) > div > div:nth-child(2) > div.{class_name} > div > div:nth-child(1) > div', '가능')
        else:  
            #집합건물
            clickLabel('#item_form > section:nth-child(10) > div > div:nth-child(1) > div:nth-child(2) > div > div:nth-child(1) > div', '가능')
    # pyautogui.alert('경로확인?')        

    #엘리베이터
    if '엘리베이터' in building_option:
        print("건물옵션에 엘리베이터 포함")
        if building_purpose == '단독주택':
            driver.find_element(By.CSS_SELECTOR, '#item_form > section:nth-child(10) > div > div:nth-child(3) > div:nth-child(2) > div').click() #있음 클릭
        else: 
            driver.find_element(By.CSS_SELECTOR, '#item_form > section:nth-child(10) > div > div:nth-child(2) > div:nth-child(2) > div').click() #있음 클릭
    # pyautogui.alert('ㄱㄱ?')
    #관리비
    if manager == '별도': 
        if building_purpose == '단독주택':
            driver.find_element(By.CSS_SELECTOR, '#item_form > section:nth-child(10) > div > div:nth-child(4) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div > div > input').send_keys(mmoney)    
        else:         
            driver.find_element(By.CSS_SELECTOR, '#item_form > section:nth-child(10) > div > div:nth-child(3) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div > div > input').send_keys(mmoney)
    else:
        print("관리비없음 체크")
        if building_purpose == '단독주택':
            driver.find_element(By.CSS_SELECTOR, '#item_form > section:nth-child(10) > div > div:nth-child(4) > div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > label > input[type=checkbox]').click()
        else: 
            driver.find_element(By.CSS_SELECTOR, '#item_form > section:nth-child(10) > div > div:nth-child(3) > div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > label > input[type=checkbox]').click()
        
    #관리비 포함 항목
    if building_purpose == '단독주택':
        clickLabel('#item_form > section:nth-child(10) > div > div:nth-child(5) > div:nth-child(2) > div', reNaming_commalist(mlist))
    else:     
        clickLabel('#item_form > section:nth-child(10) > div > div:nth-child(4) > div:nth-child(2) > div', reNaming_commalist(mlist))
    
    print("room_option:", room_option)
    print(reNaming_commalist(room_option))
    #옵션
    if building_purpose == '단독주택':
        clickLabel('#item_form > section:nth-child(10) > div > div:nth-child(6) > div:nth-child(2) > div', reNaming_commalist(room_option))
    else:     
        clickLabel('#item_form > section:nth-child(10) > div > div:nth-child(5) > div:nth-child(2) > div', reNaming_commalist(room_option))
    
    
    today = date.today() # 현재 날짜 얻기
    rdate_day = datetime.strptime(rdate, "%Y-%m-%d").date()
    # pyautogui.alert(rdate)
    
    #입주가능일
    if building_purpose == '단독주택':
        if  manager == '별도': #월세일 경우
            # rdate와 오늘 날짜 비교
            if rdate_day > today:
                print("rdate는 오늘 이후의 날짜입니다.")
                # driver.find_element(By.CSS_SELECTOR, '#item_form > section:nth-child(10) > div > div:nth-child(7) > div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > div > div > div > label > span').click() #날짜선택클릭
                # # 변수 rdate_day의 값을 가져와서 input 태그의 value 속성으로 설정
                # change_day = "2023. 06. 06 이후"  # 임의의 날짜 값
                # input_element = driver.find_element(By.CSS_SELECTOR, '#item_form > section:nth-child(10) > div > div:nth-child(7) > div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > div.react-datepicker-wrapper > div > div > label > input[type=radio]')
                # driver.execute_script("arguments[0].value = arguments[1];", input_element, change_day)        
            else:
                print("rdate는 오늘 이전의 날짜입니다.")   
                driver.find_element(By.CSS_SELECTOR, '#item_form > section:nth-child(10) > div > div:nth-child(7) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div > label > span').click() #즉시입주 클릭
        else:   
            if rdate_day > today:
                print("rdate는 오늘 이후의 날짜입니다.")    
            else:
                print("rdate는 오늘 이전의 날짜입니다.")   
                driver.find_element(By.CSS_SELECTOR, '#item_form > section:nth-child(10) > div > div:nth-child(6) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div > label > span').click() #즉시입주 클릭
            
            
    else:   
        if  manager == '별도':
            if rdate_day > today:
                print("rdate는 오늘 이후의 날짜입니다.")    
            else:
                print("rdate는 오늘 이전의 날짜입니다.")
                #JavaScript를 사용한 클릭
                element = driver.find_element(By.CSS_SELECTOR, 'div:nth-child(2) label input[value="즉시 입주"]')
                driver.execute_script("arguments[0].click();", element)
        else:
            if rdate_day > today:
                print("rdate는 오늘 이후의 날짜입니다.")    
            else:
                print("관리비별도 아닐때 rdate는 오늘 이전의 날짜입니다.")
                #JavaScript를 사용한 클릭
                element = driver.find_element(By.CSS_SELECTOR, 'div:nth-child(2) label input[value="즉시 입주"]')
                driver.execute_script("arguments[0].click();", element)
              
        
    
    
    
    #설명
    #비밀메모
    driver.find_element(By.XPATH, '//*[@id="item_form"]/section[5]/div/div[3]/div[2]/div/textarea').send_keys(secret_memo)
    
    #중개의뢰를 받은 방법
    driver.find_element(By.XPATH, '//*[@id="item_form"]/section[6]/div[2]/div[1]/div[1]/div[1]/div/label[1]/span').click()
    
    #동의체크
    driver.find_element(By.XPATH, '//*[@id="item_form"]/section[6]/div[3]/label/input').click()
    
    
    #물건사진 폴더열기
    main_dir = 'Z:\\업무자료\\4사진자료&이미지자료(외부유출금지)\\1주거용물건, 상업용물건\\'
    path_dir = main_dir + data['folderPath'] #'경기도\\오산시\\궐동\\654-9\\썬플라워\\1층\\1층'
    print(path_dir)
    try:
        os.startfile(path_dir)
    except Exception as e:
        print('폴더열기 에러', str(e))
  
    pyautogui.alert('직방 매물등록을 마치셨습니까?')
    driver.quit()