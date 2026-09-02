from selenium import webdriver
from selenium.webdriver import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException


from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.chrome.options import Options

import pyautogui 
import time
import pyperclip
import pymysql
import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta

from selenium.webdriver.common.alert import Alert

import os
import sys
# 🚀 상위 폴더의 패키지를 인식할 수 있도록 시스템 경로(sys.path)에 추가하는 마법의 코드
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# 이제 공용 함수를 내 파일 안에 있는 것처럼 자유롭게 불러옵니다!
from util.property_utils import 건축법상건축물용도로변환

# # ChromeDriver 경로 설정
# driver = webdriver.Chrome('/chromedriver')
def 페이지완전로딩대기(driver, timeout=10):
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
    except TimeoutException:
        print("페이지 로딩 타임아웃: 지정된 시간 내에 페이지가 완전히 로드되지 않음.")

def 리스트선택(driver, li_id, li_text):
    print("리스트선택(li_id:"+li_id+" li_text:"+li_text+")")
    # pyautogui.alert("리스트선택("+li_text+") 준비")
    try:
        # select_id에 해당하는 버튼 클릭하여 드롭다운 활성화
        # 'li_id'에 해당하는 li 요소 찾기
        print("리스트선택 1단계")
        # li_element = WebDriverWait(driver, 5).until(
        #     EC.element_to_be_clickable((By.ID, li_id))
        # )
        print("리스트선택 2단계")
        # li_id에서 'li_'를 제거하고 '-button'을 붙여서 완전한 버튼 ID 생성
        button_id = li_id.replace("li_", "") + "-button"
        
        # if li_id == 'li_regDtl02gsanggaIpjiCd': #난방방식 선택
        #     pyautogui.alert("버튼클릭("+li_text+") 준비 button_id:"+button_id)
        
        # 버튼 ID를 사용하여 버튼 요소 찾기
        # dropdown_button = li_element.find_element(By.ID, button_id)
        dropdown_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, button_id))
        )
        ActionChains(driver).move_to_element(dropdown_button).perform()
        
        # if li_id == 'li_regDtl02gsanggaIpjiCd': #난방방식 선택
        #     pyautogui.alert("버튼클릭("+li_text+") 종료")
             
        print("리스트선택 3단계")
        # time.sleep(0.5)
        # if li_id=='li_regDtl02buildUseCd':pyautogui.alert("건축물용도 항목의 위치확인")
        
        # dropdown_button.click() 
        driver.execute_script("arguments[0].click();", dropdown_button)
             
        # pyautogui.alert("확인필요")
        print("드롭다운버튼 클릭", li_id, li_text)
        # 해당 텍스트를 가진 a 요소가 보일 때까지 기다림
        텍스트를포함하는a태그 = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//li[@id='{li_id}']//ul/li/a[contains(text(), '{li_text}')]"))
        )
        print("리스트선택 4단계")
        time.sleep(0.2)
        # a 요소 클릭
        텍스트를포함하는a태그.click()
              
        # pyautogui.alert("확인필요1")
        print(li_text+" 클릭")
        # print("a태그가 안보일 때까지 기다리기")
        # pyautogui.alert("리스트선택 완료확인")
    except Exception as e:
        print(f"항목 선택 중 오류 발생: {e}")


def 라벨텍스트로span입력값넣기(driver, 라벨텍스트, 넣을값):
    try:
        # 넣을값 = str(넣을값)
        # print(f"라벨텍스트로span입력값넣기({driver}, {라벨텍스트}, {넣을값})")
        # '라벨에 해당하는 span 내의 input 요소 찾기
        # pyautogui.alert("여기가 문제??")
        
        span_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//label[contains(text(), '" + 라벨텍스트 + "')]/following-sibling::span"))
        )
        # print(라벨텍스트+" span요소들:"+ str(len(span_elements)))
        if len(span_elements)==1:
            # print(라벨텍스트+" 입력요소 1개보임")
            input_element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(span_elements[0].find_element(By.XPATH, ".//input"))
            )
            ActionChains(driver).move_to_element(input_element).perform()
            input_element.send_keys(넣을값)
        else:
            # print(라벨텍스트+f" 입력요소 {str(len(span_elements))}개보임")
            for span in span_elements:
                # input_element = span.find_element(By.XPATH, ".//input")
                # print("span: ", span)
                try:
                    input_element = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable(span.find_element(By.XPATH, ".//input"))
                    )
                except Exception as e:
                    continue
                
                ActionChains(driver).move_to_element(input_element).perform()
                if input_element.is_displayed():
                    # JavaScript를 사용하여 값 설정
                    driver.execute_script("arguments[0].value = arguments[1];", input_element, 넣을값)
                    # print("입력값넣기 성공")
                    return True
                else:
                    print(라벨텍스트+" 입력요소 안보임")
    except TimeoutException as e:
        print("라벨텍스트로span입력값넣기 타임아웃 오류 발생: ", e)
        pyautogui.alert("여기가 문제맞아??")
    except Exception as e:
        print(f"라벨텍스트로span입력값넣기 오류 발생: {e}")
        pyautogui.alert("여기가 문제맞아??")
        return False


def 라벨텍스트로div입력값넣기(driver, 라벨텍스트, 넣을값):
    try:
        # 넣을값 = str(넣을값)
        print(f"라벨텍스트로div입력값넣기({driver}, {라벨텍스트}, {넣을값})")
        # '라벨에 해당하는 span 내의 input 요소 찾기
        # pyautogui.alert("여기가 문제??")
        
        div_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//label[contains(text(), '" + 라벨텍스트 + "')]/following-sibling::div"))
        )
        print(라벨텍스트+" div요소들:"+ str(len(div_elements)))
        if len(div_elements)==1:
            print(라벨텍스트+" 입력요소 1개보임")
            input_element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(div_elements[0].find_element(By.XPATH, ".//input"))
            )
            ActionChains(driver).move_to_element(input_element).perform()
            input_element.send_keys(넣을값)
        else:
            print(라벨텍스트+f" 입력요소 {str(len(div_elements))}개보임")
            for div in div_elements:
                # input_element = div.find_element(By.XPATH, ".//input")
                print("div: ", div)
                try:
                    input_element = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable(div.find_element(By.XPATH, ".//input"))
                    )
                except Exception as e:
                    continue
                
                ActionChains(driver).move_to_element(input_element).perform()
                if input_element.is_displayed():
                    # JavaScript를 사용하여 값 설정
                    driver.execute_script("arguments[0].value = arguments[1];", input_element, 넣을값)
                    print("입력값넣기 성공")
                    return True
                else:
                    print(라벨텍스트+" 입력요소 안보임")
    except TimeoutException as e:
        print("라벨텍스트로div입력값넣기 타임아웃 오류 발생: ", e)
        pyautogui.alert("여기가 문제맞아??")
    except Exception as e:
        print(f"라벨텍스트로div입력값넣기 오류 발생: {e}")
        pyautogui.alert("여기가 문제맞아??")
        return False

    # print(f"'{라벨텍스트}' 라벨을 가진 span 요소를 찾을 수 없습니다.")
    # return False

def 라벨텍스트로라디오선택(driver, li_id, 선택값):
    try:
        # 'li_id'에 해당하는 li 요소 찾기
        li_element = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.ID, li_id))
        )

        # 해당 li 내의 '선택값'에 해당하는 라디오 버튼의 label 찾기
        radio_label = li_element.find_element(By.XPATH, f".//label[text()='{선택값}']")
        radio_id = radio_label.get_attribute("for")

        # 라디오 버튼까지 스크롤하고 클릭 가능할 때까지 기다림
        radio_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, radio_id))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", radio_button)

        # JavaScript를 사용하여 라디오 버튼 클릭
        driver.execute_script("arguments[0].click();", radio_button)

    except Exception as e:
        print(f"라디오선택 오류 발생: {e}")
        return False

    return True

def 그룹별명칭변환(그룹, 대상명칭):
    # 변환 매핑
    변환사전 = {}
    if 그룹 == '건축물용도':
        변환사전 = {
            "제1종근린생활시설": "제1종 근린생활시설",
            "제2종근린생활시설": "제2종 근린생활시설",
            "노유자시설": "노유자(老幼者: 노인 및 어린이)시설",
            "위락시설": "위락(慰樂)시설",
            "교정군사시설": "교정(矯正) 및 군사 시설",
            # 추가 매핑
        }
    elif 그룹 == '주거옵션':
        변환사전 = {
            "화장실": "욕실",
            "벽걸이에어컨": "에어컨",
            # 추가 매핑
        }
    elif 그룹 == '주용도':
        변환사전 = {
            "상가점포": "상가전용",
            "사무실": "사무실전용",
            # 추가 매핑
        }

    # 매핑된 값 반환, 매핑되지 않았으면 원래 값을 반환
    return 변환사전.get(대상명칭, 대상명칭)


def 최상단알림창(message, title="알림"):
    root = tk.Tk()
    root.withdraw()  # 창 숨기기
    root.attributes("-topmost", True)  # 항상 위에 있도록 설정
    messagebox.showinfo(title, message)
    root.destroy()


def macro(data, user):
    errarr = []
    
    # options = None
    options = Options()
    options.add_experimental_option("detach", True) # 창이 자동으로 닫히지 않게 해줌
    options.add_experimental_option("excludeSwitches", ["enable-automation"]) #브라우저에 나타나는 자동화라는 메세지 제거
    options.add_argument("--disable-blink-features=AutomationControlled") #봇으로 인식안하게 하는 옵션


    # 현재 날짜와 시간 가져오기
    현재날짜시간 = datetime.now()
    현재날짜 = 현재날짜시간.date()
    # 문자형으로 변환
    current_date = 현재날짜시간.strftime("%Y-%m-%d")  # 'YYYY-MM-DD' 형식
    current_time = 현재날짜시간.strftime("%H:%M:%S")  # 'HH:MM:SS' 형식 
    
    manager_id = data['adminData']['ad_id']
    admin_name = data['adminData']['admin_name']
    print("한방:", data['adData']['한방'])
    hanbang_code = '' if len(data['adData']['한방'])==0 else data['adData']['한방'][0]['ad_code']
    
    tr_target = data['writeData']['tr_target']
    location_do = data['landData'][0]['land_do']
    location_si = data['landData'][0]['land_si']
    location_dong = data['landData'][0]['land_dong']
    location_li = data['landData'][0]['land_li']
    location_jibun = data['landData'][0]['land_jibun']

    location_lijibun = (data['type_path'] + data['landData'][0]['land_jibun']) if location_li == '' else (location_li + data['type_path'] + data['landData'][0]['land_jibun'])
    location_dongli = (data['landData'][0]['land_dong'] + data['type_path'] + data['landData'][0]['land_jibun']) if location_li == '' else location_lijibun
    location_detail = location_dongli
    dosidongli = location_do+' '+location_si+' '+location_dong+((' '+location_li) if location_li != '' else '')
    land_type = '일반' if data['landData'][0]['land_type']=='1' else '산'

    request_code = data['writeData']['request_code'] #의뢰번호
    obang_code = data['writeData']['obang_code'] #오방매물번호
    object_code_new = data['writeData']['object_code_new'] #오방매물번호
    obinfo_type = ''
    object_type = data['writeData']['object_type']
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
    if ',' in obinfo_ttype: #쉼표가 있다면 쉼표로 분리후 첫번째 항목을 값으로 지정
        obinfo_ttype = obinfo_ttype.split(',')[0]

    basic_manager = data['writeData']['manager'] #관리비 별도/포함/미확인
    basic_mmoney = int(data['writeData']['mmoney'])*10000 if data['writeData']['mmoney'] != '' else '' #관리비
    print("관리비:"+str(basic_mmoney))
    basic_mlist = data['writeData']['mlist'] #관리비포함내역
    basic_mmemo = data['writeData']['mmemo'] #관리비메모
    premium = data['writeData']['premium'] #권리금
    add_warmer = '' #data['writeData']['add_warmer'] 난방
    add_rdate = str(data['writeData']['rdate']) #입주일
    secret_1 = '' if data['writeData']['tr_memo'] == '' else data['writeData']['tr_memo'] + Keys.ENTER
    secret_2 = '' if data['landData'][0]['land_memo'] == '' else data['landData'][0]['land_memo']
    object_detail = '- ' + secret_2 if secret_2 != '' else '' #비밀메모
    representing_jimok = data['landData'][0]['representing_jimok']#토지주지목
    representing_purpose = data['landData'][0]['representing_purpose']#토지주용도
    land_totarea = data['landData'][0]['land_totarea']#대지면적
    land_option = data['landData'][0]['land_option']#토지옵션
    representing_use = data['landData'][0]['representing_use']#지목
    land_adjoiningroad = data['landData'][0]['land_adjoiningroad']#접한도로폭
    try:
        # 문자열을 'x'로 분리 후, 정수로 변환하여 큰 수 선택
        values = [int(x) for x in land_adjoiningroad.split('x')]
        접한도로폭 = max(values)
        print(f"접한도로폭: {접한도로폭}")
    except Exception as e:
        접한도로폭 = None  # 예외 발생 시 None으로 처리
        print(f"도로폭 파싱 오류: {e}")        
    # pyautogui.alert("obinfo_type:"+ obinfo_type)
    
    

    if tr_target == '건물' or tr_target == '층호수':
        building_name = data['buildingData']['building_name'] if  data['buildingData']['building_name'] not in ['무명건물'] else '' #건물명
        location_building = '' if building_name == '' else ' ' + building_name
        location_detail += location_building
        building_grndflr = int(data['buildingData']['building_grndflr'])
        building_ugrndflr = int(data['buildingData']['building_ugrndflr'])
        basic_totflr = str(building_grndflr + building_ugrndflr) #전체층
        building_usedate = str(data['buildingData']['building_usedate']) #준공일
        building_pn = data['buildingData']['building_pn'] #주차
        secret_3 = '' if data['buildingData']['building_memo'] == '' else data['buildingData']['building_memo'] + Keys.ENTER
        if secret_3 != '' : object_detail += Keys.ENTER + '- ' + secret_3
        building_archarea = data['buildingData']['building_archarea'] #건축면적
        building_totarea = data['buildingData']['building_totarea'] #연면적
        building_direction = data['buildingData']['building_direction'] #방향
        building_purpose = data['buildingData']['building_purpose'] #주용도
        building_hhld = data['buildingData']['building_hhld'] #세대수
        building_elvcount = data['buildingData']['building_elvcount'] #승강기수
        building_option = data['buildingData']['building_option']#건물옵션
        building_option_arr = building_option.split(',')
        tot_options = ",".join([land_option, building_option])
        direction_stn = '안방'
        # basic_rcount = '99'
        # basic_bcount = '99'
        # if basic_rcount == '99' and basic_bcount == '99':
        #     object_detail += Keys.ENTER + '- ' + '룸수와 욕실수 확인필요'
        basic_area1 = building_totarea

    if tr_target == '층호수':
        room_num = data['roomData']['room_num']#호실명
        location_room = '' if room_num == '' else ' ' + room_num
        location_detail += location_room
        basic_area1 = data['roomData']['room_area1'] #실면적
        if basic_area1 == '': basic_area1 = '0'
        basic_area2 = data['roomData']['room_area2'] #공급면적
        if basic_area1 != '' and basic_area2 == '': basic_area2 = basic_area1
        basic_rcount = data['roomData']['room_rcount'] #방수
        basic_bcount = data['roomData']['room_bcount'] #욕실수
        basic_floor = data['roomData']['room_floor'] #해당층
        room_important = data['roomData']['room_important'] #옵션선택
        room_option = data['roomData']['room_option'] #옵션선택
        room_option_arr = room_option.split(',')
        direction_stn = data['roomData']['direction_stn'] #방향기준
        room_direction = data['roomData']['room_direction'] #방향
        secret_4 = '' if data['roomData']['room_memo'] == '' else data['roomData']['room_memo'] + Keys.ENTER
        if secret_4 != '' : object_detail += Keys.ENTER + '- ' + secret_4
        room_option = data['roomData']['room_option']#호실옵션
        tot_options = ",".join([building_option, room_option])
        
        #필수항목체크
        if basic_area1 == '': 
            pyautogui.alert("전용면적 설정후 다시시작하세요~")
            exit()
        if tr_target == '층호수' and room_direction == '': 
            pyautogui.alert("호실방향 설정후 다시시작하세요~")
            exit()
        if tr_target == '건물' and building_direction == '': 
            pyautogui.alert("건물방향 설정후 다시시작하세요~")
            exit()
            
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
    elif obinfo_type1 == '원룸':
        obinfo_type = '원룸'
    elif obinfo_type1 == '상가점포':
        obinfo_type = '상가점포'
    elif obinfo_type1 == '사무실':
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
    else:
        obinfo_type = obinfo_type2

    print(f"obinfo_type:{obinfo_type}, obinfo_type1:{obinfo_type1}, obinfo_type2:{obinfo_type2}")

    def 최상단알림창(message, title="알림"):
        root = tk.Tk()
        root.withdraw()  # 창 숨기기
        root.attributes("-topmost", True)  # 항상 위에 있도록 설정
        messagebox.showinfo(title, message)
        root.destroy()
    
    
    # ChromeDriver 경로 설정
    driver = webdriver.Chrome(options=options)
    # driver = webdriver.Chrome('/chromedriver', options=options)
    # driver = webdriver.Chrome(ChromeDriverManager().install())

    # URL 열기
    # driver.maximize_window()
    
    #driver.get('https://mobile.karhanbang.com/kren/mamul/list')
    driver.get('https://m.karhanbang.com/mptl/main')
    
    def 기본주소정보등록():
        nonlocal basic_area1,basic_area2,direction_stn,basic_rcount
        driver.execute_script("fn_moveRegDtl('1')") #기본/주소 정보
        
        #팝업이 보이면 제거
        try:
            # popAlertBodyId 요소의 display 상태 확인
            # WebDriverWait를 사용하여 popAlertBodyId가 보일 때까지 최대 3초 대기
            pop_alert_body = WebDriverWait(driver, 3).until(
                EC.visibility_of_element_located((By.ID, "popAlertBodyId"))
            )
            # pop_alert_body = driver.find_element_by_id("popAlertBodyId")
            if pop_alert_body.value_of_css_property("display") != "none":
                # 팝업이 보이면 popAlertExecuteBtnId 버튼 클릭
                pop_alert_close_btn = driver.find_element(By.ID, "popAlertExecuteBtnId")
                pop_alert_close_btn.click()
        except Exception as e:
            print(f"팝업 닫기 시도 중 오류 발생: {e}")        
        
        # pyautogui.alert("확인필요")  
        # driver.find_element(By.XPATH, '//*[@id="regDtl01cateCd-button"]').click() #매물유형 클릭
        리스트선택(driver, 'li_regDtl01cateCd', obinfo_type) #매물유형선택
        리스트선택(driver, 'li_regDtl01gureCd', obinfo_ttype) #거래유형선택
        if obinfo_type != '토지':
            WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="div_regDtl01soonMoveYn"]/span/label'))).click() #즉시입주 클릭
        
            # pyautogui.alert("확인필요")  
            #임대 구분(전체임대 기본설정)
            # WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.ID, "regDtl01rentCd01"))).click()
            driver.execute_script("arguments[0].click();", driver.find_element(By.ID, "regDtl01rentCd01"))

        
        #매물 주소
        driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, '//*[@id="li_regDtl01address"]/span/button')) #지역검색 버튼 클릭
        print("주소 입력창에 "+dosidongli+"입력")
        # time.sleep(0.3)
        주소입력창 = WebDriverWait(driver, 3).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="asp_text"]')))
        주소입력창.send_keys(dosidongli+Keys.ENTER) #검색어 입력창에 동+리까지 입력
        # driver.find_element(By.XPATH, '//*[@id="asp_icSearch"]').click() #돋보기 클릭 
        # time.sleep(0.5)
        주소입력창.send_keys(Keys.ENTER)
        페이지완전로딩대기(driver)
        time.sleep(0.5)
        # 검색된 리스트 "asp_areaSelWrap_div"를 가진 div 내부의 모든 'li' 요소 찾기
        li_elements = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[@id='asp_areaSelWrap_div']//li"))
        ) 
        print("검색된주소 li개수:", str(len(li_elements)))
        # 원하는 요소 클릭
        if len(li_elements) == 1:
            페이지완전로딩대기(driver)
            # driver.find_element(By.XPATH, '//*[@id="asp_icSearch"]').click() #돋보기 클릭 
            # 요소가 하나만 있을 경우, 바로 해당 요소 클릭
            time.sleep(0.5)
            driver.find_element(By.XPATH, '//*[@id="asp_areaSelWrap_div"]/ul/li/label/strong').click()
            # li_elements[0].click()
            # pyautogui.alert("올바르게 클릭했는지 확인")
        else:
            for li in li_elements:
                try:
                    strong_text = li.find_element(By.TAG_NAME, "strong").text
                    print("strong_text: " + strong_text)
                    print("dosidongli: " + dosidongli)
                    if dosidongli in strong_text:
                        li.click()
                        # pyautogui.alert("올바르게 클릭했는지 확인")
                        # return  # 성공적으로 클릭 후 함수 종료
                        break
                except Exception as e:
                    print(f"주소항목 선택 중 오류 발생: {e}")
                    continue     
        print("선택완료 클릭")
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="asp_choice_btn"]'))).click() #선택완료 클릭
        # driver.find_element(By.XPATH, '//*[@id="asp_choice_btn"]').click() #선택완료 클릭
        # pyautogui.alert("선택완료 확인")
        # if land_type == '일반' : driver.find_element(By.XPATH, '//*[@id="li_regDtl01address"]/div/ul[1]/li[2]').click() #산 클릭 
        if land_type == '산' : driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, '//*[@id="regDtl01sanCd1"]')) #산 클릭 
        if '-' in location_jibun:
            land_bon, land_bu = location_jibun.split('-', 1)
        else:
            land_bon = location_jibun
            land_bu = ""  # '-'가 없을 경우, land_bu는 비어 있는 상태로 둡니다.      
        print("본번: " + land_bon, "부번: " + land_bu)
        time.sleep(0.5)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="regDtl01bonNo"]'))).send_keys(land_bon) #본번 입력
        # driver.find_element(By.XPATH, '//*[@id="regDtl01bonNo"]').send_keys(land_bon) #본번 입력
        # # JavaScript를 사용하여 본번과 부번 값을 직접 설정
        # driver.execute_script("document.getElementById('regDtl01bonNo').value = arguments[0];", land_bon)

        time.sleep(0.1)
        driver.find_element(By.XPATH, '//*[@id="regDtl01buNo"]').send_keys(land_bu) #부번 입력
        # pyautogui.alert("올바르게 지번이 입력되었는지 확인")

        if obinfo_type != '토지':
            #건물명
            if '무명건물' not in building_name: 라벨텍스트로span입력값넣기(driver, '건물명', building_name)
            #층
            # pyautogui.alert("확인필요")  
            if tr_target == '층호수':
                if int(basic_floor) < 0 : driver.execute_script("arguments[0].click();", driver.find_element(By.ID, "regDtl01currTopBottom02")) #지하 클릭
                라벨텍스트로span입력값넣기(driver, '층', basic_floor)
            if obinfo_type in ['공장','창고','상업용건물','단독']:
                print("지상/지하 층입력 "+obinfo_type)
                print("building_grndflr:"+str(building_grndflr))
                print("building_ugrndflr:"+str(building_ugrndflr))
                #지상/지하
                if building_grndflr != '':driver.find_element(By.XPATH, '//*[@id="regDtl01topFloor"]').send_keys(building_grndflr)
                if building_ugrndflr != '':driver.find_element(By.XPATH, '//*[@id="regDtl01bottomFloor"]').send_keys(building_ugrndflr)
            
            #총층
            라벨텍스트로span입력값넣기(driver, '총 층', int(basic_totflr))
            # pyautogui.alert("올바르게 층 입력되었는지 확인")
            print("object_type:",object_type)
            # pyautogui.alert("object_type확인: "+object_type)
            if obinfo_type in ['원룸']:
                #공급 면적
                라벨텍스트로span입력값넣기(driver, '공급 면적', basic_area2)
            if obinfo_type in ['상가점포']:
                #계약 면적
                라벨텍스트로span입력값넣기(driver, '계약 면적', basic_area2)
            if obinfo_type in ['공장', '창고', '상업용건물', '단독']:
                #건축 면적
                라벨텍스트로span입력값넣기(driver, '건축 면적', building_archarea)
            if obinfo_type in ['공장', '창고', '상업용건물', '단독']:
                #연 면적
                라벨텍스트로span입력값넣기(driver, '연 면적', building_totarea)
            if obinfo_type in ['공장', '창고', '상업용건물', '단독']:
                #대지 면적
                라벨텍스트로span입력값넣기(driver, '대지 면적', land_totarea)
            if obinfo_type in ['상가점포', '공장', '창고']:
                #전용 면적  
                라벨텍스트로span입력값넣기(driver, '전용 면적', basic_area1) 

            if tr_target == '건물':
                최상단알림창("룸수,욕실수 입력후 '확인'을 클릭하세요") 
            else:
                #룸 수
                if obinfo_type in ['공장', '창고']:
                    basic_rcount = '0' if str(basic_rcount) == '' else str(basic_rcount)
                    라벨텍스트로span입력값넣기(driver, '룸 수', basic_rcount)

                #욕실수
                if obinfo_type in ['단독']:
                    라벨텍스트로span입력값넣기(driver, '욕실 수', basic_bcount)
                elif obinfo_type in ['공장']:
                    라벨텍스트로span입력값넣기(driver, '욕실 또는 화장실 수', basic_bcount)

            # pyautogui.alert("올바르게 계약 입력되었는지 확인")   

            # pyautogui.alert("올바르게 전용 입력되었는지 확인")
            #방향
            if tr_target == '층호수':
                if room_direction != '':
                    print("방향 입력시작 room_direction:"+room_direction)
                    라벨텍스트로라디오선택(driver, 'li_regDtl01directionCd', room_direction)
            elif tr_target == '건물':
                if building_direction != '':
                    print("방향 입력시작 building_direction:"+building_direction)
                    라벨텍스트로라디오선택(driver, 'li_regDtl01directionCd', building_direction)
            
            #방향 기준
            print("방향기준 입력시작")
            if object_type != '주거용':
                라벨텍스트로span입력값넣기(driver, '방향 기준', '주출입문')
            else:
                if direction_stn=='': direction_stn='안방'
                라벨텍스트로라디오선택(driver, 'li_regDtl01directionInfo', direction_stn)
                if obinfo_type == '다세대':
                    라벨텍스트로span입력값넣기(driver, '총 세대', building_hhld)
                    리스트선택(driver, 'li_regDtl01stairCd', '계단식') #계단형태
            
        # pyautogui.alert("전송종료 준비")
        # 'togList' 클래스를 가진 ul 요소 아래의 모든 li 요소를 찾음
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'ul.togList')))
        매물노출리스트 = driver.find_elements(By.CSS_SELECTOR, 'ul.togList li')
        # 각 li 요소를 순회하면서 체크박스가 체크되어 있지 않은 경우 클릭
        for li in 매물노출리스트:
            # label = li.find_element(By.CSS_SELECTOR, 'label')
            label = li.find_element(By.CSS_SELECTOR, 'span.btTog.txt > label')
            print("label: "+label.text)
            if label.text == "전송종료":
                # pyautogui.alert("종료확인 클릭준비")
                # action = ActionChains(driver)
                # action.move_to_element(li).perform()
                # 요소가 화면에 나타날 때까지 스크롤
                driver.execute_script("arguments[0].scrollIntoView(true);", li)
                li.click()
                # pyautogui.alert("종료확인팝업 준비")
                #종료확인팝업에서 '예'선택
                WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="popAlertExecuteBtnId"]'))).click()
        
        # pyautogui.alert("전송종료 확인")   
        
        # #노출 채널
        # print("채널 입력시작")
        # driver.find_element(By.XPATH, '//*[@id="ul_regDtl01_07"]/li[2]/span/ul/li[3]/label').click() #한방(앱) 클릭
        
        # pyautogui.alert("기본정보등록 완료")    
        driver.execute_script("setAreaLatLngRegDtl01()")
        print("기본정보등록 완료") #완료
        
    def 금액옵션정보등록():
        nonlocal building_usedate
        # driver.execute_script("fn_moveRegDtl('2')") #금액/옵션 정보 
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="btn_atlfslRegListRegDtl02"]'))).click()
        # pyautogui.alert("금액옵션정보 확인")
        if obinfo_ttype == '매매':
            print("obinfo_ttype:"+obinfo_ttype)
            #매매가
            라벨텍스트로span입력값넣기(driver, '매매가', obinfo_trading)

        else:            
            #월세금    
            라벨텍스트로span입력값넣기(driver, '월세금', obinfo_rent1)
            #보증금    
            라벨텍스트로span입력값넣기(driver, '보증금', obinfo_deposit1)


        if obinfo_type == '토지':
            #접한도로
            if 접한도로폭:
                라벨텍스트로div입력값넣기(driver, '접한 도로', 접한도로폭)
            else:
                최상단알림창("접한도로 폭을 입력하세요~\n계속 진행하시려면 확인클릭!!")
            
            #토지면적
            라벨텍스트로span입력값넣기(driver, '토지 면적', land_totarea)
            #지목
            리스트선택(driver, 'li_regDtl02jimokCd', representing_jimok)
            #용도분류
            # driver.find_element(By.XPATH, '//*[@id="regDtl02recommendUse2_toji-button"]/span').click()
            용도분류선택 = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="regDtl02recommendUse2_toji-button"]'))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", 용도분류선택)
            용도분류선택.click()
            def 지목에따른용도(지목):
                지목 = str(지목).strip()  # 혹시 모를 공백 제거 및 문자열 처리
                if 지목 in ['전', '답']:
                    return '농지'
                elif 지목  in ['공장', '창고']:
                    return '공장창고용지'
                else:
                    return '기타'
            용도값 = 지목에따른용도(representing_use)
            리스트선택(driver, 'regDtl02recommendUse2_toji', 용도값)
            최상단알림창("용도분류를 선택하세요~\n계속 진행하시려면 확인클릭!!")       
        else:    
            # print("object_type:"+object_type, "obinfo_type:"+obinfo_type)
            if object_type != '주거용':
                if obinfo_type in ['상가', '사무실']:
                    #시설비    
                    라벨텍스트로span입력값넣기(driver, '시설비', '1')
                    #권리금
                    if isinstance(premium, int) and premium > 0:   #자연수일 경우에만 실행
                        라벨텍스트로span입력값넣기(driver, '권리금', premium)
                    else:
                        라벨텍스트로span입력값넣기(driver, '권리금', '1')
                if obinfo_type in ['공장','창고']:
                    최상단알림창("층고, 동력, 입지, 공장종류, 공장형태, 진입도로, 건축구조를 선택하세요~\n계속 진행하시려면 확인클릭!!")
                    #층고
                    #동력
                    #입지
            else:
                if obinfo_type in {'원룸'}:
                    #발코니
                    최상단알림창("베란다 정보확인")
                    if '베란다' in room_important:
                        print("베란다가 존재합니다.")
                        라벨텍스트로라디오선택(driver, 'li_regDtl02balconyCd','유')
                    else:
                        라벨텍스트로라디오선택(driver, 'li_regDtl02balconyCd','무')
                    #구조
                    if '오픈형' in room_important:
                        print("오픈형 구조입니다..")
                        라벨텍스트로라디오선택(driver, 'li_regDtl02roomCd','오픈형')
                    else:
                        라벨텍스트로라디오선택(driver, 'li_regDtl02roomCd','분리형')
                    #세탁
                    pyautogui.alert("개별세탁 정보확인")
                    print("개별세탁 선택")
                    리스트선택(driver, 'li_regDtl02setakCd', '개별세탁')
                    #주방
                    pyautogui.alert("개별주방 정보확인")
                    print("개별주방 선택")
                    리스트선택(driver, 'li_regDtl02jubangCd', '개별주방')
                    #욕실 구분
                    pyautogui.alert("개별욕실 정보확인")
                    print("개별욕실 선택")
                    라벨텍스트로라디오선택(driver, 'li_regDtl02yoksilCd','개별 욕실')
                    #옵션
                    pyautogui.alert("풀옵션 정보확인")
                    required_options = ['싱크대', '세탁기', '냉장고'] #풀옵션 요소들
                    if all(option in room_option_arr for option in required_options):
                        print("풀옵션 선택")
                        라벨텍스트로라디오선택(driver, 'li_regDtl02optionCd','풀옵션')
                    elif any(option in room_option_arr for option in required_options):
                        print("부분옵션 선택")
                        라벨텍스트로라디오선택(driver, 'li_regDtl02optionCd','부분옵션')
                    else:
                        print("비옵션 선택")
                        라벨텍스트로라디오선택(driver, 'li_regDtl02optionCd','비옵션')
                        
            #승강기
            if "엘리베이터" in building_option_arr:
                print("엘리베이터가 존재합니다.")
                라벨텍스트로라디오선택(driver, 'li_regDtl02elevatorYn', '유')
            else:
                라벨텍스트로라디오선택(driver, 'li_regDtl02elevatorYn', '무')
            # pyautogui.alert("엘리베이터 확인")
            
            #난방방식(초기값: 개별난방)
            print(object_type+"난방방식 선택")
            if object_type == '주거용':
                if obinfo_type in ['단독']:
                    라벨텍스트로라디오선택(driver, 'li_regDtl02warmCd-memu', 그룹별명칭변환('난방 방식', '개별난방'))
                else:
                    라벨텍스트로라디오선택(driver, 'li_regDtl02warmCd', 그룹별명칭변환('난방 방식', '개별난방'))
            elif object_type== '상업용':
                리스트선택(driver, 'li_regDtl02warmCd', '개별난방')
                라벨텍스트로라디오선택(driver, 'li_regDtl02coldCd', '개별냉방')
            # pyautogui.alert("난방방식 확인")
            
            if tr_target == '층호수':
                리스트선택(driver, 'li_regDtl02recommendUse2', '(선택)안함')
            
                #입지 조건 (임의 초기설정)
                print(object_type+' '+obinfo_type1+' 입지조건 선택')
                if obinfo_type1 not in ['원룸']:  
                    if object_type == '주거용':    
                        # print("입지")
                        리스트선택(driver, 'li_regDtl02sukbakIpjiCd', '주택가')
                    elif obinfo_type1 == '사무실':    
                        # print("입지")
                        리스트선택(driver, 'li_regDtl02officeIpjiCd', '주택가')
                    elif obinfo_type1 == '상가점포':    
                        # print("입지")
                        리스트선택(driver, 'li_regDtl02gsanggaIpjiCd', '주택가')
                        #상가구분
                        리스트선택(driver, 'li_regDtl02gsanggaCd', '근린상가')
                # pyautogui.alert("입지조건 확인")    
                #주 용도 (임의 초기설정)
                print("주용도:", 그룹별명칭변환('주용도', obinfo_type1))
            
                라벨텍스트로라디오선택(driver, 'li_regDtl02storeUseCd', 그룹별명칭변환('주용도', obinfo_type1))

            elif tr_target == '건물':
                최상단알림창(f"주용도 선택후 '확인'을 클릭하세요!!\n\n※참고: 건축물대장상 용도는 '{building_purpose}'입니다.")    
                # 라벨텍스트로라디오선택(driver, 'li_regDtl02officeUseCd', 그룹별명칭변환('주용도', obinfo_type1))

                # # 상가면적/사무실면적/주택면적 초기값0 적용
                # 라벨텍스트로span입력값넣기(driver, '상가 면적', '0')
                # 라벨텍스트로span입력값넣기(driver, '사무실 면적', '0')
                # 라벨텍스트로span입력값넣기(driver, '주택 면적', '0')
            
            #주차
            최상단알림창(f"총주차대수 입력후 '확인'을 클릭하세요!!\n\n※참고: 건축물대장상 총주차대수는 '{building_pn}대'입니다.")

            
            # #비목
            # print("관리비내역")
            # # driver.find_element(By.XPATH, '//*[@id="regDtl02expensesItemInfo"]').send_keys("관리비내역") #관리비내역 입력
            # try:
            #     # WebDriverWait를 사용하여 요소가 상호작용 가능할 때까지 기다립니다.
            #     expenses_item_input = WebDriverWait(driver, 10).until(
            #         EC.visibility_of_element_located((By.XPATH, '//*[@id="regDtl02expensesItemInfo"]'))
            #     )
            #     expenses_item_input.send_keys("관리비내역")
            # except Exception as e:
            #     print(f"오류 발생: {e}")

            #건축물용도 regDtl02expensesItemInfo
            # -------------------------------------------------------------------------
            # 🎯 [수정] 건축법상 건축물 용도 자동 정제 및 변환 반영
            # -------------------------------------------------------------------------
            # 1. 면적(basic_area1)과 원본 용도(building_purpose)를 공용 함수에 전달하여 1차 정제
            정제된용도 = 건축법상건축물용도로변환(building_purpose, basic_area1)
            # 2. 공용 함수에서 매칭되지 않았을 경우(None), 기존 그룹별명칭변환 사전을 차선책으로 활용
            if not 정제된용도:
                최종용도 = 그룹별명칭변환('건축물용도', building_purpose)
            else:
                # 공용 함수가 반환한 값("노유자시설" 등)을 한방 플랫폼의 최종 특수 명칭으로 보정
                최종용도 = 그룹별명칭변환('건축물용도', 정제된용도)
            print(f"▶ 건축물용도 매핑완료: 원본({building_purpose}) / 면적({basic_area1}㎡) -> 최종 선택값({최종용도})")
            # 한방 드롭다운 선택 실행
            리스트선택(driver, "li_regDtl02buildUseCd", 최종용도)
            # pyautogui.alert("올바르게 건축물용도 선택되었는지 확인")
            
            #사용승인일
            if building_usedate == '' or building_usedate == '0000-00-00':
                pyautogui.alert("확인불가 클릭되는지 확인")
                # driver.find_element(By.XPATH, '//*[@id="regDtl02dayCheck"]').click() #준공일확인불가 클릭
                준공일확인불가 = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="regDtl02dayCheck"]'))
                )
                # 요소가 화면에 보이도록 스크롤
                driver.execute_script("arguments[0].scrollIntoView(true);", 준공일확인불가)
                # JavaScript를 이용해 요소 클릭 시도
                driver.execute_script("arguments[0].click();", 준공일확인불가)           
            else:
                # building_usedate = building_usedate.replace('-', '')
                print("building_usedate",building_usedate)
                # driver.find_element(By.XPATH, '//*[@id="regDtl02useApprovalDay"]').send_keys(building_usedate)
                driver.execute_script("document.getElementById('regDtl02useApprovalDay').value = arguments[0];", building_usedate)
        driver.execute_script("saveCmptnRegDtl02()") #완료
        
        # driver.execute_script("saveTempRegDtl02()") #임시저장
        # WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="popAlertExecuteBtnId"]'))).click() #임시저장 확인팝업 예 클릭
        print("금액옵션정보등록 완료")
    
    def 관리비정보등록():
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="btn_atlfslRegListRegDtl07"]'))).click() #관리비 정보 
        #관리비부과방식 클릭
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="regDtl07chargeCodeType-button"]/span'))).click()
        
        # "확인불가" 텍스트를 가진 요소가 클릭 가능할 때까지 기다린 후 클릭
        try:
            확인불가_버튼 = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//a[text()='확인불가']"))
            )
            확인불가_버튼.click()
        except Exception as e:
            print(f"‘확인불가’ 버튼 클릭 시도 중 오류 발생: {e}")  
              
        #확인불가사유 클릭
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="regDtl07detailCodeType3-button"]/span'))).click()
        try:
            미고지_버튼 = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//a[text()='임대인이 관리비를 미고지 하는 경우']"))
            )
            미고지_버튼.click()
        except Exception as e:
            print(f"‘미고지’ 버튼 클릭 시도 중 오류 발생: {e}")  
        driver.execute_script("saveCmptnRegDtl07()") #완료
        # pyautogui.alert("관리비정보등록 입력확인")
        
        
    def 메모기타정보등록():
        # nonlocal object_code
        # driver.execute_script("fn_moveRegDtl('3')") #메모/기타 정보 
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="btn_atlfslRegListRegDtl03"]'))).click()
        
        #매물 특징
        매물특징값 = "oO오방Oo "
        if tr_target == '토지':
            매물특징값 += location_li+" "+representing_purpose+" "
        매물특징값 += tr_target+obinfo_ttype
        driver.find_element(By.XPATH, '//*[@id="regDtl03feature"]').send_keys(매물특징값)
        
        #매물 설명
        if obinfo_ttype == '매매':
            object_code = object_code_new
        else:
            object_code = obang_code        
        detail = ''
        detail += Keys.ENTER + '[☞관리번호: ' + object_code + ']' + Keys.ENTER
        if object_detail != '':
            detail += Keys.ENTER + '[ 매물설명 ]' + Keys.ENTER
            # detail += Keys.ENTER + '📋상세정보'
            detail += object_detail + Keys.ENTER
        # detail += Keys.ENTER + f'↓↓↓ 오방{object_code} 매물 바로 보러가기 ↓↓↓'
        # detail += Keys.ENTER + f'https://osanbang.com/product/view/{object_code}'
        detail += Keys.ENTER + '관심있는 매물이라면 지금 바로 연락주세요~'
        detail += Keys.ENTER + ''
        detail += Keys.ENTER + '▣ 100% 직접보고 직접 찍은 실매물만을 제공합니다.'
        detail += Keys.ENTER + '▣ 365일 정상근무, 모시러 가는 서비스제공!!'
        detail += Keys.ENTER + '▣ 성실하게 정직하게 친절하게 안내해드리겠습니다.'
        detail += Keys.ENTER + '▣ 고객님의 소중한 재산을 최우선으로 생각합니다.'
        detail += Keys.ENTER + '▣지금보신 매물외에도 아직 등록되지 않은 매물들이 많이 있습니다.'
        detail += Keys.ENTER + '▣편하게 연락 주시고 홈페이지(오산에서방구하기)도 방문해보세요!!'
        detail += Keys.ENTER + '☎010-8631-4392 나상권공인중개사 '
        detail += Keys.ENTER + ''
        detail += Keys.ENTER + '※실시간 거래로 인하여 해당물건이 없을 수 있으니 방문전 반드시 문의바랍니다.'
        detail += Keys.ENTER + '※렌트프리, 옵션, 협의사항 등 끝까지 도와드리겠습니다.' + Keys.ENTER
        # detail += Keys.ENTER + '📌홈페이지: osanbang.com'
        detail += Keys.ENTER + '----------------------------------------------------------------------------' + Keys.ENTER
        # detail += Keys.ENTER + ''
        # detail += Keys.ENTER + ''
        # detail += Keys.ENTER + ''
        driver.find_element(By.XPATH, '//*[@id="regDtl03memo"]').send_keys(detail)
        
        #비공개 메모
        nonOpen_memo = '새홈관리번호: ' + object_code_new + Keys.ENTER + object_detail
        driver.find_element(By.XPATH, '//*[@id="regDtl03secretMemo"]').send_keys(nonOpen_memo)
        # pyautogui.alert("고객정보등록 등록 확인")
        driver.execute_script("saveCmptnRegDtl03()") #완료
        print("메모기타정보등록 완료")    
        
    def 고객정보등록():
        # driver.execute_script("fn_moveRegDtl('4')") #고객 정보 
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="btn_atlfslRegListRegDtl04"]'))).click() #고객 정보 
        driver.execute_script("saveCmptnRegDtl04()") #완료
        print("고객정보등록 완료")     
    
    def 신규매물등록():
        최상단알림창("확인 클릭시 신규등록을 시작합니다. :"+obinfo_type)  
        
        driver.execute_script("divShowEvent('atlfslRegIntro','매물|등록')") #매물등록 
        driver.execute_script("fn_atlfslRegNew()") #새로내놓기
        # pyautogui.alert("확인필요")  
        기본주소정보등록()
        # pyautogui.alert("확인필요")  
        금액옵션정보등록()
        # pyautogui.alert("확인필요 "+object_type)  
        if object_type == "주거용":
        # if obinfo_type == "주거용" and basic_mmoney >= 10:
            관리비정보등록()
        메모기타정보등록()
        고객정보등록()
        
        try:
            print("모든 정보 등록완료")
            # pyautogui.alert("모든 정보 등록완료") 
            매물등록하기버튼 = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="atlfslRegListRegBtn"]')))
            매물등록하기버튼.click() #매물등록하기
            # driver.find_element(By.XPATH, '').click() #매물등록하기
            print("매물등록하기버튼 클릭시도")
            # pyautogui.alert("매물등록하기버튼 클릭시도") 
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="popAlertExecuteBtnId"]'))).click() #등록확인 팝업에서 '예' 클릭
            print("등록확인 완료")
            페이지완전로딩대기(driver)
            
            #내매물상세의 이미지 아래 한방"매물번호"가 보이면 프로그램종료
            # '매물번호 '로 시작하는 문자열이 나타날 때까지 대기
            매물번호_text = WebDriverWait(driver, 10).until(
                EC.text_to_be_present_in_element((By.XPATH, '//*[@id="atlfslDtlDisMmNo"]'), '매물번호 ')
            )
            매물번호span = driver.find_element(By.XPATH, '//*[@id="atlfslDtlDisMmNo"]')
            매물번호_text = 매물번호span.text.strip()  # 문자열 앞뒤 공백 제거
            print(f"'{매물번호_text}'가 보임")
            if 매물번호_text.startswith('매물번호 '):
                한방매물번호 = 매물번호span.text.replace('매물번호 ', '')  # '매물번호 '를 제거한 나머지 문자열
                print(f"매물번호: {한방매물번호}")
                # 매물번호 클립보드에 복사
                # pyperclip.copy(한방매물번호)
                #DB에 한방매물번호 업데이트
                # pyautogui.alert(f"한방 매물번호 복사완료!!\n\n등록된 한방매물번호는 '{한방매물번호}'입니다.") 
                def get_ad_dates():
                    """
                    광고 시작일과 종료일을 반환합니다.
                    시작일은 오늘 날짜, 종료일은 30일 후 날짜입니다.
                    """
                    start_date = datetime.now().strftime("%Y-%m-%d")  # 오늘 날짜
                    end_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")  # 30일 후 날짜
                    return start_date, end_date                
                #한방매물번호 DB에 저장하기
                def 한방매물번호저장():

                    # DB 연결
                    conn = pymysql.connect(host='obangkr.cafe24.com', user='obangkr', password='Ddhqkd!1', charset='utf8')

                    # DictCursor 대신 기본 커서 사용
                    cursor = conn.cursor()
                    # cursor = conn.cursor(pymysql.cursors.DictCursor)
                    cursor.execute('USE obangkr;')

                    # 광고 시작일과 종료일 계산
                    ad_start, ad_end = get_ad_dates()   

                    insert_query = """
                        INSERT INTO pr_externalad (
                            admin_id, object_code_new, ad_start, ad_end, ad_site, ad_code, ad_manager, ad_manager_id, ad_udate, ad_utime, ad_wdate, ad_wtime
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """

                    try:
                        # 쿼리 실행
                        conn.begin()  # 트랜잭션 시작
                        cursor.execute(insert_query, (
                            manager_id, object_code_new, ad_start, ad_end, '한방', 한방매물번호, admin_name, manager_id, current_date, current_time, current_date, current_time
                        ))
                        if manager_id and object_code_new and 한방매물번호 :
                            conn.commit()
                            print(f"✅ DB에 매물({object_code_new})의 한방 매물번호를 추가 하였습니다.") 
                            alert_message = f"새 한방 광고 매물이 추가되었습니다.\n\한방매물번호: {한방매물번호}\n\n작업을 종료합니다."
                        else:
                            alert_message = f"DB에 등록하기 위한 필수정보가 확인되지 않습니다.\n\manager_id: {manager_id}\nobject_code_new: {object_code_new}\n한방매물번호: {한방매물번호}\n\n작업을 종료합니다."
                    except Exception as e:
                        alert_message = f"추가 작업 중 오류가 발생했습니다: {e}"    

                    # 알림창으로 결과 표시
                    if alert_message : 
                        print(alert_message)
                        # pyautogui.alert(alert_message)      
                        최상단알림창(alert_message)          
                
                한방매물번호저장() #한방매물번호저장 실행        
            # pyautogui.alert("정상등록확인") 
        except Exception as e:
            print("등록완료파트 에러:"+ str(e))












        
    # 요소가 클릭 가능할 때까지 대기
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="deviceCheck"]/button'))).click() #한방앱/모바일웹 화면선택 팝업닫기
    print("한방앱/모바일웹 화면선택 팝업닫기")
    driver.find_element(By.XPATH, '//*[@id="mptlFooter"]/div/a[5]').click() #메뉴클릭
    print("메뉴클릭")
    # WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="component-mainMenu-7755237386019465"]/div[1]/a/div'))).click() #로그인 및 회원가입 클릭
    driver.find_element(By.XPATH, '//*[@id="popAlertExecuteBtnId"]').click() #메뉴클릭
    print("로그인을 하시겠어요? '예'클릭")

    # # "component-mainMenu-"로 시작하는 아이디를 가진 요소를 찾기
    # element_xpath = "//*[starts-with(@id, 'component-mainMenu-')]/div[1]/a/div"
    # element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, element_xpath)))
    # element.click()    
    # print("로그인 및 회원가입 클릭")
    driver.find_element(By.XPATH, '//*[@id="agntLoginTabBtn"]').click() #공인중개사 로그인 클릭
    print("공인중개사 로그인 클릭")
    driver.find_element(By.XPATH, '//*[@id="userId"]').send_keys('bsleemanse') #아이디 입력
    print("아이디 입력")
    driver.find_element(By.XPATH, '//*[@id="password"]').send_keys('tkdrnjs1001') #비번 입력
    print("비번 입력")
    driver.find_element(By.XPATH, '//*[@id="agntLoginBtn"]').click() #로그인 클릭
    print("로그인 클릭")
    팝업버튼 = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="deviceCheck"]/button'))) #한방앱/모바일웹 화면선택 팝업
    # 요소가 보이면 클릭
    if 팝업버튼.is_displayed():
        팝업버튼.click()
        print("한방앱/모바일웹 화면선택 팝업")
    # pyautogui.alert("확인필요")    
    
    driver.execute_script("fnMmGoViewMove('mamulList')")  # 내 매물 관리
    search_input = driver.find_element(By.XPATH, '//*[@id="atlfslListSearchInput"]')
    if hanbang_code:
        print("검색키워드(한방매물번호): "+hanbang_code)
        keyword = hanbang_code
    else:
        print("검색키워드(주소): "+location_dongli)
        keyword = location_dongli
    search_input.send_keys(keyword)  # 검색어(한방매물번호) 입력
    # pyautogui.alert("확인필요")
    try:

        search_button = driver.find_element(By.XPATH, '//*[@id="atlfslListSearchBtn2"]')
        search_button.click()  # 돋보기 클릭
        # 1. 검색 버튼 누르기 전, 현재 자료수(텍스트)를 먼저 저장해둬.
        # 만약 페이지 로드 시점부터 atlfslListTotCnt가 있다면 초기값을 가져오기 위해 먼저 찾고
        # 없으면 wait로 찾아서 text를 가져와야겠지? 여기서는 있다고 가정할게!
        initial_count_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "atlfslListTotCnt"))
        )
        initial_count_text = initial_count_element.text
        print(f"⭐ 검색 전 초기 자료수: {initial_count_text} ⭐")

        # 2. 명시적 대기(Explicit Wait)를 사용해서 자료수가 업데이트될 때까지 기다려!
        # atlfslListTotCnt의 텍스트가 'initial_count_text'와 달라질 때까지 기다리는 거야.
        # 최대 10초까지 기다릴게.
        WebDriverWait(driver, 10).until(
            # 람다(lambda) 함수로 커스텀 조건을 만들어서, atlfslListTotCnt 요소의 텍스트가
            # 초기 텍스트랑 달라질 때까지 기다리라고 지시하는 거지.
            lambda d: d.find_element(By.ID, "atlfslListTotCnt").text != initial_count_text
        )

        # 3. 텍스트가 업데이트된 후에, 그 값을 가져와!
        result_element = driver.find_element(By.ID, "atlfslListTotCnt")
        result = result_element.text
        print(f"🎉 검색 후 업데이트된 자료수: {result} 🎉")

    except TimeoutException:
        print("😢 지정된 시간 안에 검색 결과 자료수가 업데이트되지 않았습니다. 😢")
        # 타임아웃 발생 시, 현재 요소를 다시 찾아서 값을 가져와 볼 수도 있어.
        # (하지만 이 경우 원하는 업데이트된 값이 아닐 가능성이 높음)
        current_result = driver.find_element(By.ID, "atlfslListTotCnt").text
        print(f"현재 atlfslListTotCnt 값 (타임아웃 시점): {current_result}")
    except Exception as e:
        print(f"⚠️ 에러 발생: {e} ⚠️")    
    # time.sleep(1)
    # search_button = driver.find_element(By.XPATH, '//*[@id="atlfslListSearchBtn2"]')
    # search_button.click()  # 돋보기 클릭
    # result = driver.find_element(By.ID, "atlfslListTotCnt").text
    
    # result = "1"
    print(f"검색결과값은 {result}개 입니다.")
    if hanbang_code:
        if result == "1":
            pyautogui.alert("매물수정작업??")
            # print("1")
            # try:
            #     페이지완전로딩대기(driver)
            #     time.sleep(2)
            #     driver.execute_script("document.title='테스트 중';")
            #     print("2")
            #     driver.execute_script("alert('확인을 눌러주세요.');")
            #     # # JavaScript confirm 대화 상자 띄우기
            #     # driver.execute_script("confirm('등록된 매물이 존재합니다. 매물을 수정하시겠습니까?');")

            #     # Alert 객체가 나타날 때까지 기다림
            #     WebDriverWait(driver, 10).until(EC.alert_is_present())
            #     alert = driver.switch_to.alert

            #     # 대화 상자의 결과에 따라 처리
            #     response = alert.accept()  # '확인' 클릭

            #     if response:
            #         pyautogui.alert("매물수정작업??")
            #     else:
            #         # 사용자가 '취소'를 클릭한 경우, 프로그램 종료
            #         pyautogui.alert("종료된다구??")
            #         driver.quit()
            #         exit()

            # except TimeoutException:
            #     print("사용자가 대화 상자에 응답하지 않음")
            # except Exception as e:
            #     print("alert error:" + str(e))

            print("3")
            # 작업 종료
            driver.quit()
            exit()
        else:
            pyautogui.alert("오류확인필요")

    else:
        if result != "0":#검색어로 검색된 매물이 존재하는 경우
            print("검색어로 검색된 매물이 존재함!!")
            # pyautogui.alert("매물등록을 계속 진행하시려면 확인!!") 
        else: 
            print("텍스트 값은 0입니다.")
            
        신규매물등록()
        
    driver.quit()
    # pyautogui.alert("확인필요")  
    

    
    

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
