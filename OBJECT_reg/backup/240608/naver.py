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
import re
import os
import pymysql

options = Options()

options.add_argument("--disable-blink-features=AutomationControlled")


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

from bs4 import BeautifulSoup  
def remove_html_and_entities(text):
    soup = BeautifulSoup(text, 'html.parser')
    return soup.get_text()

def macro(data, user):
    
    def 그룹별명칭변환(그룹, 대상명칭):
        # 변환 매핑
        변환사전 = {}
        if 그룹 == '건축물용도':
            변환사전 = {
                "근린생활시설": "제1종 근린생활시설",
                "제1종근린생활시설": "제1종 근린생활시설",
                "제2종근린생활시설": "제2종 근린생활시설",
                "노유자시설": "노유자(老幼者: 노인 및 어린이)시설",
                "위락시설": "위락(慰樂)시설",
                "교정군사시설": "교정(矯正) 및 군사 시설",
                "자동차관련시설": "자동차 관련 시설",
                "다세대주택": "공동주택",
                # 추가 매핑
            }
        elif 그룹 == '시설정보':
            변환사전 = {
                "공터": "마당",
                "에어컨": "벽걸이에어컨",
                "가스렌지": "가스레인지",
                "인덕션": "인덕션레인지",
                "전자렌지": "전자레인지",
                # "에어컨": "에어컨",
                # 추가 매핑
            }
        elif 그룹 == '관리비포함내역':
            변환사전 = {
                "공용전기": "공용관리비",
                "공용수도": "기타관리비",
                "개별전기": "전기료",
                "개별수도": "수도료",
                "TV": "TV사용료",
                # 추가 매핑
            }
        elif 그룹 == '주용도':
            변환사전 = {
                "상가점포": "상가전용",
                "사무실": "사무실전용",
                # 추가 매핑
            }
        elif 그룹 == '지역(시/도)':
            변환사전 = {
                "전라북도": "전북특별자치도",
                # 추가 매핑
            }
        elif 그룹 == '전문분야':
            변환사전 = {
                "주거용": "원/투룸",
                "상업용": "상가/사무실",
                "공업용": "공장/창고",
                # 추가 매핑
            }
        elif 그룹 == '방특징':
            변환사전 = {
                "중로접": "큰길가",
                "대로접": "큰길가",
                # 추가 매핑
            }

        # 매핑된 값 반환, 매핑되지 않았으면 원래 값을 반환
        return 변환사전.get(대상명칭, 대상명칭)
    
    def 목록_변환(그룹, 항목들):
        변환된_항목들 = []
        for 항목 in 항목들.split(','):
            변환된_항목들.append(그룹별명칭변환(그룹, 항목.strip()))
        return ','.join(변환된_항목들)    

    # 현재 날짜 출력
    import datetime
    current_date = datetime.date.today()
    formatted_date = current_date.strftime("%Y-%m-%d")
    
    admin_name = data['adminData']['admin_name']
    # naver_id = data['adminData']['naver_id']
    # naver_pw = data['adminData']['naver_pw']
    naver_id = "osanbang6666"
    naver_pw = "dhqkd5555%"
    
    errarr = []
    
    소유자명 = ''
    소유자연락처 = ''
    contactor_data = data['contactorData']['contactor_data']
    print("contactor_data:",contactor_data)
    contactor_keys_list = list(contactor_data.keys())
    # 리스트에 요소가 있는지 확인하고 첫 번째 요소에 접근합니다.
    if contactor_keys_list:  # 리스트가 비어있지 않은 경우
        contactor_info = contactor_data[contactor_keys_list[0]]
    else:
        # contactor_keys_list가 비어 있으면 적절한 처리를 합니다.
        print("contactor_keys_list: No data available")
        contactor_info = None  # 혹은 다른 기본값 할당
    # if len(master_keys_list) > 1:
    #     client_info = master_data[master_keys_list[1]]
    #     print("두 번째 고객의 이름:", client_info['client_name'])
    #     print("두 번째 고객의 연락처:", client_info['client_phone1'])
    # else:
    #     client_info = master_data[master_keys_list[0]]
    #     print("두 번째 고객 정보가 없습니다.")
    #     print("첫 번째 고객의 이름:", client_info['client_name'])
    #     print("첫 번째 고객의 연락처:", client_info['client_phone1'])
    # pyautogui.alert("master_data 확인"+str(len(master_keys_list)))
    master_names = data['writeData']['master_name']
    # pyautogui.alert("master_name 확인:"+master_name)
    # print("master_name:"+master_name)
    master_names_arr = []
    master_names_arr = master_names.split(',')
    if len(master_names_arr) > 0:
        master_name = master_names_arr[0]
    else:
        master_name = ''
    # print("master_name:",master_name)
    # pyautogui.alert("master_name 개수:"+master_name)
    master_check = data['writeData']['master_check']
    
    client_name = data['clientData']['client_name']
    client_phone1 = data['clientData']['client_phone1']
    client_phone = f"{client_phone1[:3]}-{client_phone1[3:7]}-{client_phone1[7:]}"
    client_info = client_name + ' ' + client_phone
    
    tr_target = data['writeData']['tr_target']
    tr_range = data['writeData']['tr_range']
    location_do = data['landData'][0]['land_do']
    location_si = data['landData'][0]['land_si']
    location_dong = data['landData'][0]['land_dong']
    location_li = data['landData'][0]['land_li']
    jibun = data['landData'][0]['land_jibun']
    jibung = data['landData'][0]['land_jibung'] #지번그룹
    jibung_arr = jibung.split(',')
    jibung_len = len(jibung_arr) #지번의 개수
    
        

    location_lijibun = (data['type_path'] + data['landData'][0]['land_jibun']) if data['landData'][0]['land_li'] == '' else (data['landData'][0]['land_li'] + data['type_path'] + data['landData'][0]['land_jibun'])
    location_dongli = (data['landData'][0]['land_dong'] + data['type_path'] + data['landData'][0]['land_jibun']) if data['landData'][0]['land_li'] == '' else location_lijibun
    
    location_detail = f'외 {jibung_len-1}필지' if jibung_len > 1 else '' #다중필지일 경우 '외 ㅇㅇ필지'로 표시

    request_code = data['writeData']['request_code'] #의뢰번호
    object_code_new = data['writeData']['object_code_new'] #새홈매물번호
    obang_code = data['writeData']['obang_code'] #오방매물번호
    optionImportant = ''
    object_type = data['writeData']['object_type']
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
    obinfo_title = data['writeData']['object_title'] #매물제목
    obinfo_content = remove_html_and_entities(data['writeData']['object_content']) #매물설명

    premium = data['writeData']['premium']
    premium_exist = data['writeData']['premium_exist']
    premium_content = data['writeData']['premium_content']
    basic_manager = data['writeData']['manager'] #관리비 별도/포함/미확인
    basic_mmoney = '' if data['writeData']['mmoney']=='' else int(data['writeData']['mmoney'])*10000 #관리비
    basic_mlist = data['writeData']['mlist'] #관리비포함내역
    basic_mmemo = data['writeData']['mmemo'] #관리비메모
    add_warmer = '' #data['writeData']['add_warmer'] 난방
    add_rdate = str(data['writeData']['rdate']) #입주일
    secret_1 = '' if data['writeData']['tr_memo'] == '' else data['writeData']['tr_memo'] + "\n"
    secret_2 = '' if data['landData'][0]['land_memo'] == '' else data['landData'][0]['land_memo'] + "\n"
    basic_secret = secret_1 + secret_2 #비밀메모
    land_option = data['landData'][0]['land_option']#토지옵션

    if tr_target == '토지' or tr_target == '건물':
        land_totarea = data['landData'][0]['land_totarea'] #대지면적
        if tr_target == '토지' :
            land_purpose = data['landData'][0]['land_purpose'] #용도지역
            land_important = data['landData'][0]['land_important'] #토지특징
            land_option = data['landData'][0]['land_option'] #토지옵션
            

    if tr_target == '건물' or tr_target == '층호수':
        location_building = '' if data['buildingData']['building_name'] == '' else ' ' + data['buildingData']['building_name']
        location_detail += location_building
        building_name = data['buildingData']['building_name'] #건물명
        building_gate1 = data['buildingData']['building_gate1'] #건물출입방법
        building_gate2 = data['buildingData']['building_gate2'] #건물출입내용
        building_info = ('' if location_dongli == '' else ' ') + building_name + (("("+building_gate2+")") if building_gate1 == '비밀번호' else "")
        building_archarea = data['buildingData']['building_archarea'] #건축면적
        building_totarea = data['buildingData']['building_totarea'] #연면적
        building_direction = data['buildingData']['building_direction'] #방향
        building_type = data['buildingData']['building_type'] #대장구분
        building_purpose = data['buildingData']['building_purpose'] #주용도
        building_usedate = str(data['buildingData']['building_usedate']) #사용승인일
        basic_totflr = str(int(data['buildingData']['building_grndflr']) + int(data['buildingData']['building_ugrndflr'])) #전체층
        building_ugrndflr = str(data['buildingData']['building_ugrndflr']) if data['buildingData']['building_ugrndflr']!='' else 0 #지하총층
        building_grndflr = str(data['buildingData']['building_grndflr']) #지상총층
        building_important = data['buildingData']['building_important'] #건물특징
        if building_important != '':
            optionImportant += ','+building_important if optionImportant != '' else building_important
        # if building_important != '': optionImportant = building_important
        print("building_important: ", optionImportant)
        building_option = data['buildingData']['building_option'] #건물옵션
        if building_option != '':
            optionImportant += ','+building_option if optionImportant != '' else building_option
        # if building_option != '': optionImportant = optionImportant+','+building_option
        print("building_option: ", optionImportant)
        building_pn = int(data['buildingData']['building_pn']) if data['buildingData']['building_pn'] != '' else 0 #주차대수
        building_hhld = data['buildingData']['building_hhld'] #세대수
        building_fmly = data['buildingData']['building_fmly'] #가구수
        secret_3 = '' if data['buildingData']['building_memo'] == '' else data['buildingData']['building_memo'] + "\n"
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
        room_info = location_room + room_gate
        location_detail += location_room
        basic_area1 = data['roomData']['room_area1'] #전용면적(호실)
        basic_area2 = data['roomData']['room_area2'] #공급면적
        basic_rcount = data['roomData']['room_rcount'] #방수
        basic_bcount = data['roomData']['room_bcount'] #욕실수
        basic_floor = data['roomData']['room_floor'] #해당층
        room_important = data['roomData']['room_important'] #호실특징
        if room_important != '':
            optionImportant += ','+room_important if optionImportant != '' else room_important
        print("room_important: ", optionImportant)
        room_option = data['roomData']['room_option'] #호실옵션
        if room_option != '':
            optionImportant += ','+room_option if optionImportant != '' else room_option
        print("room_option: ", optionImportant)
        r_direction = data['roomData']['direction_stn'] #방향기준
        room_direction = data['roomData']['room_direction'] #방향
        secret_4 = '' if data['roomData']['room_memo'] == '' else data['roomData']['room_memo'] + "\n"
        basic_secret += secret_4
        
    basic_secret = location_dongli + building_info + room_info + " " + client_info + "\n" + formatted_date+" "+admin_name
    basic_secret += "\n" +" https://obangkr.cafe24.com/web/request/request_view/view_give_request_detail.php?request_code="+request_code
    fail_msg = ''
    trading_memo = ''
    rent_memo = ''
    land_memo = ''
    building_memo = ''
    room_memo = ''
    premium_memo = ''
    r_add_memo = ''

    # ChromeDriver 경로 설정
    driver = webdriver.Chrome(options=options)
    # driver = webdriver.Chrome('/chromedriver', options=options)
    # driver = webdriver.Chrome(ChromeDriverManager().install())

    # URL 열기
    driver.maximize_window()
    
    driver.get('https://www.serve.co.kr/member/login')
    driver.find_element(By.XPATH, '//*[@id="input-1"]').send_keys(naver_id)
    driver.find_element(By.XPATH, '//*[@id="input-3"]').send_keys(naver_pw)
    driver.find_element(By.XPATH, '//*[@id="app"]/div/div/div/div/div[2]/div[4]/button').click()

    # 로그인확인겸 첫 파란등록버튼 기다리기(관리자로 로그인시)
    driver.implicitly_wait(10)
    # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/div[1]/div/ul/li[3]/a'))).click()
    # driver.find_element(By.XPATH, '//*[@id="menu-product-1"]/a').click()

    # 확인후 이동
    driver.get('https://ma.serve.co.kr/good/articleRegistManage/')
    

    def 제곱미터_평_변환(제곱미터):
        평 = float(제곱미터) / 3.3058
        return str(round(평, 1))  # 소수점 둘째 자리까지 반올림

    def 한글금액(금액):
        단위 = ["만원", "억", "조"]
        단위_금액 = []
        i = 0
        if 금액.isdigit():
            금액 = int(금액)
            # 만원 단위로 주어진 금액을 억, 조 등으로 나누어 변환
            while 금액 > 0:
                금액, 나머지 = divmod(금액, 10000)  # 10000으로 나누어 몫과 나머지를 구함
                if 나머지 > 0:
                    단위_금액.append(f"{나머지}{단위[i]}")
                i += 1
            # 단위_금액 리스트를 거꾸로 뒤집어서 큰 단위가 먼저 오도록 함
            단위_금액 = 단위_금액[::-1]
            # 결과 문자열 생성
            결과 = ''.join(단위_금액)
            return 결과 if 결과 else "0만원"  # 결과가 비어있으면 "0만원" 반환
    
    def 확인메세지창승인():
        try:
            # 확인 메시지 창이 생성될 때까지 대기 (10초로 설정)
            alert = WebDriverWait(driver, 10).until(EC.alert_is_present())
            # 확인 메시지 창 승인
            alert.accept()
        except:
            # 대기 시간 초과 또는 확인 메시지 창이 없는 경우 예외 처리
            print("확인 메시지 창이 없습니다.")        
    
    def 특정tr요소(strong태그의텍스트):
        print(f"특정tr요소({strong태그의텍스트})")
        요청strong_text = strong태그의텍스트.replace(' ', '')
        try:
            strong_elements = driver.find_elements(By.XPATH, f"//th/strong")
            print(f"'{strong태그의텍스트}' 텍스트를 가진 strong 태그의 개수: {len(strong_elements)}")
            
            # 각 strong 태그의 부모 tr 요소 찾기
            for strong in strong_elements:
                # HTML에서 텍스트 추출 후 모든 공백 및 줄바꿈 제거
                strong_text = strong.get_attribute('textContent').replace('\n', '').replace('\r', '').replace(' ', '')
                print(f"공백과 줄바꿈을 제거한 strong_text vs 요청strong_text: {strong_text} vs {요청strong_text}")
                # print(f"찾은 {strong.text} strong요소: {strong.get_attribute('outerHTML')}")
                # strong 태그의 상위 th 태그를 거쳐 상위 tr 태그 찾기
                # tr_element = strong.find_element(By.XPATH, './ancestor::tr')
                # print(f"찾은 {strong.text} tr요소: {tr_element.get_attribute('outerHTML')}")
                # return tr_element

        except Exception as e:
            print(f"An error occurred: {e}")    
    
    def 특정위치의x번째입력태그찾기(strong태그의텍스트, tag_name, 몇번째):
        print(f"특정위치의x번째태그찾기({strong태그의텍스트}, {tag_name}, {몇번째})")
        try:      
            요청strong_text = strong태그의텍스트.replace(' ', '')
            
            strong_elements = driver.find_elements(By.XPATH, f"//th/strong")
            # print(f"'{strong태그의텍스트}' 텍스트를 가진 strong 태그의 개수: {len(strong_elements)}")
           
            # 각 strong 태그의 부모 tr 요소 찾기
            for strong in strong_elements:
                # HTML에서 텍스트 추출 후 모든 공백 및 줄바꿈 제거
                strong_text = strong.get_attribute('textContent').replace('\n', '').replace('\r', '').replace(' ', '')
                
                # print(f"찾은 strong태그 개수: {len(strong_elements)}개")
                # print(f"Found strong태그: {strong태그의텍스트} {strong.get_attribute('outerHTML')}")
                if 요청strong_text == strong_text:
                    # strong 태그의 상위 th 태그를 거쳐 상위 tr 태그 찾기
                    tr_element = strong.find_element(By.XPATH, './ancestor::tr')
                    # 해당 tr 내의 td 요소들 찾기
                    td_elements = tr_element.find_elements(By.XPATH, './td')
                    # print(f"찾은 td태그 개수: {len(td_elements)}개")
                    visible_elements = []
                    # 원하는 태그만 찾기
                    for td in td_elements:
                        # print(f"Found td태그: {td.get_attribute('outerHTML')}")
                        
                        if tag_name == 'textarea':
                            elements = td.find_elements(By.XPATH, f'./div/div/div/div[3]/{tag_name}')
                        else:
                            elements = td.find_elements(By.XPATH, f'.//input[@type="{tag_name}"]')
                        # print(f"elements 개수: {len(elements)}개")
                        limit_count = 1
                        for elem in elements:
                            # print(f"Found {tag_name} all element: {elem.get_attribute('outerHTML')}")
                            if tag_name in ['checkbox', 'radio']:
                                # print(f"Found {tag_name} element: {elem.get_attribute('outerHTML')}")
                                visible_elements.append(elem)
                            else:
                                if elem.is_displayed():
                                    visible_elements.append(elem)
                                #     print(f"Found {tag_name} element: {elem.get_attribute('outerHTML')}")
                                # else:
                                #     print(f"{tag_name} element is not displayed: {elem.get_attribute('outerHTML')}")

                    # print(f"visible_elements 개수: {len(visible_elements)}개")
                    # 원하는 태그 찾기
                    visible_tag_count = 0
                    for v_elem in visible_elements:
                        visible_tag_count += 1
                        if visible_tag_count == 몇번째:
                            return v_elem
                    break

            print(f"{몇번째}번째 보이는 {tag_name} 태그를 찾을 수 없습니다.")
            return None

        except Exception as e:
            print(f"An error occurred: {e}")
            return None   
    
    def 라벨들로체크박스클릭(strong태그의텍스트, 체크박스_라벨들):
        print(f"라벨들로체크박스클릭({strong태그의텍스트}, [{체크박스_라벨들}])")
        """
        주어진 strong 텍스트를 포함하는 tr 요소 내의 체크박스들 중 주어진 라벨 텍스트와 일치하는 체크박스를 클릭하는 함수.

        Args:
        - driver: Selenium WebDriver 객체
        - strong태그의텍스트: 찾고자 하는 strong 태그의 텍스트
        - 체크박스_라벨들: 클릭하고자 하는 체크박스의 라벨 텍스트 목록 (리스트 형태)
        """
        try:
            # 주어진 텍스트를 포함하는 strong 태그 찾기
            # strong_elements = driver.find_elements(By.XPATH, f'//th//strong[contains(text(), "{strong태그의텍스트}")]')
            strong_elements = driver.find_elements(By.XPATH, f'//th//strong[contains(normalize-space(.), "{strong태그의텍스트}")]')
            all_strong_elements = driver.find_elements(By.XPATH, '//th/strong')
            if not strong_elements:
                print(f"'{strong태그의텍스트}' 텍스트를 가진 strong 태그를 찾을 수 없습니다.")
                return

            # 각 strong 태그의 부모 tr 요소 찾기
            for strong in strong_elements:
                # strong 태그의 상위 th 태그를 거쳐 상위 tr 태그 찾기
                tr_element = strong.find_element(By.XPATH, './ancestor::tr')
                # 이후의 모든 tr 요소를 검색하되 다음 strong을 가진 th가 나타날 때까지
                following_trs = tr_element.find_elements(By.XPATH, './following-sibling::tr[not(.//th/strong)] | .//following-sibling::tr[.//th/strong and not(.//th/strong[normalize-space(.)="{strong태그의텍스트}"])]')

                for tr in [tr_element] + following_trs:
                    # 해당 tr 내의 체크박스들 찾기
                    checkboxes = tr.find_elements(By.XPATH, './/input[@type="checkbox"]')
                    labels = tr.find_elements(By.XPATH, './/label')

                    # 체크박스와 라벨 매칭하여 클릭하기
                    for label in labels:
                        label_text = label.text.strip()
                        # print("label_text:"+label_text)
                        if label_text in 체크박스_라벨들:
                            for checkbox in checkboxes:
                                if checkbox.get_attribute("id") == label.get_attribute("for"):
                                    if not checkbox.is_selected():
                                        label.click()
                                    #     print(f"Clicked checkbox with label: {label_text}")
                                    # else:
                                    #     print(f"Checkbox with label '{label_text}' is already selected")

        except Exception as e:
            print(f"An error occurred: {e}")    
        
    def 태그별개수출력(strong태그의텍스트):
        """
        주어진 strong 텍스트를 포함하는 tr 요소 내의 태그별 보이는 개수를 출력하는 함수.

        Args:
        - driver: Selenium WebDriver 객체
        - strong태그의텍스트: 찾고자 하는 strong 태그의 텍스트

        Returns:
        - 태그별 보이는 개수 (딕셔너리 형태)
        """
        try:
            # 주어진 텍스트를 포함하는 strong 태그 찾기
            # strong_elements = driver.find_elements(By.XPATH, f'//th//strong[contains(text(), "{strong태그의텍스트}")]')
            strong_elements = driver.find_elements(By.XPATH, f'//th//strong[contains(normalize-space(.), "{strong태그의텍스트}")]')
            
            if not strong_elements:
                print(f"'{strong태그의텍스트}' 텍스트를 가진 strong 태그를 찾을 수 없습니다.")
                return None

            # 각 strong 태그의 부모 tr 요소 찾기
            for strong in strong_elements:
                # strong 태그의 상위 th 태그를 거쳐 상위 tr 태그 찾기
                tr_element = strong.find_element(By.XPATH, './ancestor::tr')
                
                # 해당 tr 내의 td 요소들 찾기
                td_elements = tr_element.find_elements(By.XPATH, './/td')
                visible_elements = []
                
                tag_types = ['input', 'select', 'textarea', 'button']
                
                for td in td_elements:
                    for tag in tag_types:
                        if tag == 'input':
                            elements = td.find_elements(By.XPATH, f'.//{tag}[not(@type="radio")]')
                            radio_elements = td.find_elements(By.XPATH, f'.//{tag}[@type="radio"]')
                            elements.extend(radio_elements)
                        else:
                            elements = td.find_elements(By.XPATH, f'.//{tag}')                        

                        for elem in elements:
                            print(f"Found {tag} element: {elem.get_attribute('outerHTML')}")  # 디버깅 출력
                            if elem.get_attribute('style') != 'display: none' and elem.get_attribute('style') != 'visibility: hidden':
                                visible_elements.append(elem)
                            # if elem.is_displayed():
                            #     visible_elements.append(elem)

                # 태그 별 개수 계산
                input_count = len([elem for elem in visible_elements if elem.tag_name == 'input' and elem.get_attribute('type') != 'radio'])
                select_count = len([elem for elem in visible_elements if elem.tag_name == 'select'])
                radio_count = len([elem for elem in visible_elements if elem.get_attribute('type') == 'radio'])
                button_count = len([elem for elem in visible_elements if elem.tag_name == 'button'])
                textarea_count = len([elem for elem in visible_elements if elem.tag_name == 'textarea'])
                
                counts = {
                    'input': input_count,
                    'select': select_count,
                    'radio': radio_count,
                    'button': button_count,
                    'textarea': textarea_count
                }

                print(f"보이는 input 태그 개수: {input_count}")
                print(f"보이는 select 태그 개수: {select_count}")
                print(f"보이는 radio 태그 개수: {radio_count}")
                print(f"보이는 button 태그 개수: {button_count}")
                print(f"보이는 textarea 태그 개수: {textarea_count}")

                return counts

            return None

        except Exception as e:
            print(f"An error occurred: {e}")
            return None
        
    def 셀렉스항목선택(선택항목, 최상위요소div의XPATH):
        print(f"셀렉스항목선택:{선택항목}")
        try:
            driver.find_element(By.XPATH, f'{최상위요소div의XPATH}').click()
            선택항목요소 = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f"//div[@class='v-overlay-container']//div[text()='{선택항목}']"))
            )
            선택항목요소.click()
            print(f"선택완료:{선택항목}")
        except Exception as e:
            print(f"An error occurred: {e}")
            
    def 라디오버튼선택(대상strong텍스트, 선택할텍스트):
        print(f"라디오버튼선택({대상strong텍스트}, {선택할텍스트})")
        try:
            적용대상strong = driver.find_elements(By.XPATH, f'//th//strong[contains(text(), "{대상strong텍스트}")]')
            # print(f"'{대상strong텍스트}' 텍스트를 가진 strong 태그의 개수: {len(적용대상strong)}")
            
            # 해당 strong 태그들이 속한 tr 태그 내에서 td 태그의 첫 번째 div 내에 있는 label의 텍스트 출력
            for strong in 적용대상strong:
                # strong 태그가 속한 tr 태그 찾기
                tr_element = strong.find_element(By.XPATH, './ancestor::tr')
                # 해당 tr 내의 td의 첫 번째 div 내에 있는 label 태그 찾기
                label_elements = tr_element.find_elements(By.XPATH, './/td[1]//div//label')
                # 각 label 태그의 텍스트 출력
                for label in label_elements:
                    # print(f"Label 텍스트: {label.text}") 
                    if label.text==선택할텍스트:
                        label.click()     
                        # print(f"{대상strong텍스트}({label.text}) 클릭완료")   
        except Exception as e:
            print(f"An error occurred: {e}")    

    # pyautogui.alert("계속 하시겠습니까?")
    
    #매물등록버튼 클릭
    매물등록버튼요소 = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/div/div[3]/div/div[3]/div[1]/div/button'))
    )
    if 매물등록버튼요소:
        매물등록버튼요소.click()    
    else:
        print('매물등록버튼요소를 클릭할 수 없습니다.')    
    
    #확인매물등록시 주의사항 체크
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/div/div[3]/div/div[1]/div[3]/div/div/button/div/div[1]/div[1]/div/label'))).click()
    
    # 특정tr요소('등기부상 소유자 이름')
    # pyautogui.alert("go?")
    # 특정위치의x번째입력태그찾기('네이버등록권', 'radio', 1).click()
    # 특정위치의x번째입력태그찾기('상세정보', 'textarea', 1).send_keys("🤝") #느림
    # 특정위치의x번째입력태그찾기('관리자 메모(비공개 정보)', 'textarea', 1).send_keys("basic_secret+obinfo_content") 
    # pyautogui.alert("go?")
    
#기본정보
    #매물분류
    #주거용&방개수1 => 원룸, 상업용
    print("obinfo_type1:", obinfo_type1, "obinfo_type2:", obinfo_type2)
    if obinfo_type1 == '':
        # objectCheckTime()
        pyautogui.alert("매물분류 선택후 확인을 눌러주세요!!")
        매물분류1차 = driver.find_element(By.XPATH, '//*[@id="app"]/div/div/div[3]/div/div[1]/div[4]/table/tbody/tr[1]/td/div[1]/div[1]/div/div[1]/div/div[3]/div/div/span').text
        매물분류2차 = driver.find_element(By.XPATH, '//*[@id="app"]/div/div/div[3]/div/div[1]/div[4]/table/tbody/tr[1]/td/div[1]/div[1]/div/div[1]/div/div[3]/div/div/span').text
        # pyautogui.alert("매물분류1차:"+매물분류1차+"\n"+"매물분류2차:"+매물분류2차)
        obinfo_type1 = 매물분류1차
        obinfo_type2 = 매물분류2차
    else:
        try:
            #소분류
            셀렉스항목선택(obinfo_type1, '//*[@id="app"]/div/div/div[3]/div/div[1]/div[4]/table/tbody/tr[1]/td/div[1]/div[1]')
            #대분류
            셀렉스항목선택(obinfo_type2, '//*[@id="app"]/div/div/div[3]/div/div[1]/div[4]/table/tbody/tr[1]/td/div[1]/div[2]')
            # pyautogui.alert(f"{obinfo_type1} {obinfo_type2} 클릭 완료!")
            
        except Exception as e:
            print(f"An error occurred: {e}")
            pyautogui.alert("요소를 찾을 수 없습니다.")        
        
    
    #거래종류 obinfo_ttype
    라디오버튼선택('거래 종류', obinfo_ttype)  
    
    # 셀렉스항목선택('개별난방', '//*[@id="app"]/div/div/div[3]/div/div[1]/div[13]/table/tbody/tr[1]/td/div')
    # pyautogui.alert("go?"+"\n"+"소유자명:"+소유자명)
#매물소재지
    print(location_do, location_si, location_dong, location_li, jibun)
    리입력칸수 = 1
    #소재지
    셀렉스항목선택(그룹별명칭변환('지역(시/도)', location_do), '//*[@id="app"]/div/div/div[3]/div/div[1]/div[5]/table/tbody/tr[1]/td/div[1]/div/div[1]')
    셀렉스항목선택(location_si, '//*[@id="app"]/div/div/div[3]/div/div[1]/div[5]/table/tbody/tr[1]/td/div[1]/div/div[2]')
    셀렉스항목선택(location_dong, '//*[@id="app"]/div/div/div[3]/div/div[1]/div[5]/table/tbody/tr[1]/td/div[1]/div/div[3]')
    if location_li != '': 
        특정위치의x번째입력태그찾기('소재지', 'text', 리입력칸수).send_keys(location_li)
        # WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="input-1137"]'))).send_keys(location_li)
        # time.sleep(0.5); print("li ok:", data['landData'][0]['land_li'])
    
    # time.sleep(0.5); print("type_path ok:", data['type_path'])
    리입력칸수 = 1
    if data['type_path']=='산':
        # driver.find_element(By.XPATH, '//*[@id="ismount2"]').click()
        라디오버튼선택('소재지', '산')
        if location_li == '':
            지번입력파트 = 특정위치의x번째입력태그찾기('소재지', 'text', 리입력칸수+1)
        else:
            지번입력파트 = 특정위치의x번째입력태그찾기('소재지', 'text', 리입력칸수+2)
        jibun = jibun[1:]
    else:
        라디오버튼선택('소재지', '일반')
        if location_li == '':
            지번입력파트 = 특정위치의x번째입력태그찾기('소재지', 'text', 리입력칸수)
        else:
            지번입력파트 = 특정위치의x번째입력태그찾기('소재지', 'text', 리입력칸수+1)
    지번입력파트.send_keys(jibun)
        
        # driver.find_element(By.XPATH, 일반지번입력파트).send_keys(data['landData'][0]['land_jibun'])
    
    #건물명,상세주소
    상세주소값 = ''
    상세주소입력파트 = 특정위치의x번째입력태그찾기('상세주소', 'text', 1)
    if tr_target == '토지':
        상세주소값 = location_detail.strip()
    else:
        if '무명건물' not in building_name:
            특정위치의x번째입력태그찾기('건물명', 'text', building_name)
        상세주소값 = location_room.strip()
    print("상세주소값:"+상세주소값)
    라디오버튼선택('상세주소', '상세주소 없음') if 상세주소값 == '' else  상세주소입력파트.send_keys(상세주소값)
    
    
    
    #지도
    if object_type == '주거용':
        라디오버튼선택('지도', '지도 표시')
    else:
        라디오버튼선택('지도', '지도 표시안함')
    # pyautogui.alert("go?")
#가격정보
    print('obinfo_ttype:'+str(obinfo_ttype)+' obinfo_trading:'+str(obinfo_trading)+' obinfo_deposit1:'+str(obinfo_deposit1)+' obinfo_rent1:'+str(obinfo_rent1))
    if obinfo_ttype=='매매':
        print("매매가: ",obinfo_trading)
        if obinfo_trading:
            특정위치의x번째입력태그찾기('매매가', 'Number', 1).send_keys(obinfo_trading) #매매가
            trading_memo += "\n"+"-- 거래종류 : "+obinfo_ttype
            trading_memo += "\n"+"-- 거래금액 : "+한글금액(obinfo_trading)
    # pyautogui.alert("go?")
    if (obinfo_ttype=='전세' or obinfo_ttype=='월세') and obinfo_deposit1:
        print("보증금: ",obinfo_deposit1)
        보증금입력파트 = 특정위치의x번째입력태그찾기('보증금', 'Number', 1)
        보증금입력파트.send_keys(obinfo_deposit1)
        rent_memo += "\n"+"-- 거래종류 : "+obinfo_ttype
        rent_memo += "\n"+"-- 보증금 : "+한글금액(obinfo_deposit1)
        if obinfo_ttype=='월세' and obinfo_rent1:
            print("월세: ",obinfo_rent1)
            월세입력파트 = 특정위치의x번째입력태그찾기('월세', 'number', 1)
            월세입력파트.send_keys(obinfo_rent1)
            rent_memo += "\n"+"-- 월세 : "+한글금액(obinfo_rent1)
            if obinfo_deposit2:
                rent_memo += "\n※보증금조정가능(문의)"
        # pyautogui.alert("go?")
    if obinfo_type1 in ['상가점포','사무실']:
        if premium_exist == '있음':
            if premium.isdigit():
                특정위치의x번째입력태그찾기('권리금', 'number', 1).send_keys(premium)
            premium_memo = "\n"+"-- 권리금(시설비) : " + 한글금액(premium) + " 등"
            premium_memo = "\n"+"-- 권시물내역 : " + premium_content + " 등"
    if obinfo_type1 in ['상가점포','사무실']:
        print('basic_manager:'+str(basic_manager))
        if basic_manager == '별도' and obinfo_type1 != '토지':
            관리비항목들 = 그룹별명칭변환('관리비포함내역', basic_mlist)
            print("관리비:"+str(basic_mmoney)+" , 관리비항목들:"+관리비항목들)
            time.sleep(0.5)
            # pyautogui.alert("go?")
            특정위치의x번째입력태그찾기('월 관리비', 'number', 1).send_keys(basic_mmoney) #월관리비
            # pyautogui.alert("go?")
            라벨들로체크박스클릭('월 관리비', 관리비항목들)
        elif basic_manager == '없음': 
            관리비없음체크박스 = 특정위치의x번째입력태그찾기('월 관리비', 'checkbox', 1)
            관리비없음체크박스.click()

#관리비 부과정보
    if obinfo_type1 in ['원룸','주택']:
        if basic_manager == '별도' and obinfo_type1 != '토지':
            관리비항목들 = 목록_변환('관리비포함내역', basic_mlist)
            print("관리비:"+str(float(basic_mmoney))+" , 관리비항목들:"+관리비항목들)
            if float(basic_mmoney) < 100000:
                라디오버튼선택('부과방식', '정액관리비 (세부내역 미고지한 경우)')
                # 라디오버튼선택('부과방식', '정액관리비')
                라디오버튼선택('부과기준', '직전 월 관리비')
                #관리비세부내역
                셀렉스항목선택('정액관리비이지만 중개의뢰인이 세부내역 미고지한 경우', '//*[@id="app"]/div/div/div[3]/div/div[1]/div[9]/table/tbody/tr[1]/td/div[1]/div[3]')
                특정위치의x번째입력태그찾기('관리비', 'number', 1).send_keys(basic_mmoney)
                라벨들로체크박스클릭('포함항목', 관리비항목들)
            elif float(basic_mmoney) >= 100000:
                라디오버튼선택('부과방식', '정액관리비 (세부내역 미고지한 경우)')
                라디오버튼선택('부과기준', '직전 월 관리비')
                #관리비세부내역
                셀렉스항목선택('정액관리비이지만 중개의뢰인이 세부내역 미고지한 경우', '//*[@id="app"]/div/div/div[3]/div/div[1]/div[9]/table/tbody/tr[1]/td/div[1]/div[3]')
                특정위치의x번째입력태그찾기('관리비', 'number', 1).send_keys(basic_mmoney)
                라벨들로체크박스클릭('포함항목', 관리비항목들)
        else:
            print("관리비 확인불가")
            라디오버튼선택('부과방식', '확인불가')
            #확인불가사유
            셀렉스항목선택('미등기건물 신축건물 등 관리비 내역이 확인불가한 경우', '//*[@id="app"]/div/div/div[3]/div/div[1]/div[10]/table/tbody/tr/td/div')
    # pyautogui.alert("go?")
    if obinfo_ttype != '매매':
        if obinfo_type1 != '토지':
            if basic_manager == '없음':
                rent_memo += "\n"+"-- 관리비 별도 없음"
            else:
                rent_memo += "\n"+"-- 관리비 내역 미확인 (문의)"

#매물정보
    # pyautogui.alert("go?")
    #건물유형
    
    if tr_target == '층호수':
        building_memo += "\n"+"\n"+"□■ 건물정보"
        room_memo += "\n"+"\n"+"□■ 호실정보"
        if obinfo_type1 in ['원룸','주택']:
            라디오버튼선택('건물유형', '건물 일부 (방 또는 일부)')
    elif tr_target == '건물':
        building_memo += "\n"+"\n"+"□■ 건물정보"
        if obinfo_type1 in ['원룸','주택']:
            라디오버튼선택('건물유형', '건물 전체')
    elif tr_target == '토지':
        land_memo += "\n"+"\n"+"□■ 토지정보" 
        
        
    #대지면적
    if obinfo_type1 in ['토지']:
        print('land_totarea:'+str(land_totarea))
        if land_totarea : 특정위치의x번째입력태그찾기('대지면적', 'text', 1).send_keys(land_totarea)   
        if land_totarea: land_memo += "\n"+"-- 대지면적: "+land_totarea+f"㎡ (약{제곱미터_평_변환(land_totarea)}평)"
    #계약면적
    if obinfo_type1 in ['상가점포','사무실']:
        print('basic_area2:'+str(basic_area2))
        basic_area2 = basic_area1 if (basic_area2 == '' or basic_area2 == '') else basic_area2
        특정위치의x번째입력태그찾기('임대(계약)면적', 'text', 1).send_keys(basic_area2)
        if basic_area2: room_memo += "\n"+"-- 계약면적: "+basic_area2+f"㎡ (약{제곱미터_평_변환(basic_area2)}평)"
    #전용면적
    if obinfo_type1 in ['원룸','주택','상가점포','사무실']:
        print('basic_area1:'+str(basic_area1)+' basic_rcount:'+str(basic_rcount))
        if object_type == '주거용' and (basic_area1=='' or basic_area1==''):
            if basic_rcount == '1':
                basic_area1 = '20'
            if basic_rcount == '2':
                basic_area1 = '50' 
            else:
                basic_area1
        if building_type != '집합':
            r_add_memo = "\n"+"※ 일반건물의 전용면적은 실측면적과 다를 수 있습니다."
        특정위치의x번째입력태그찾기('전용면적', 'text', 1).send_keys(str(basic_area1))
        if basic_area1: room_memo += "\n"+"-- 전용면적: "+basic_area1+f"㎡ (약{제곱미터_평_변환(basic_area1)}평)"
    #공급면적
    if obinfo_type1 in ['원룸','주택']:
        print('basic_area2:'+str(basic_area2))
        if basic_area1:
            basic_area2 = basic_area1 if (basic_area2=='' or basic_area2=='') else basic_area2
            특정위치의x번째입력태그찾기('공급면적', 'text', 1).send_keys(str(basic_area2))
            if basic_area2: room_memo += "\n"+"-- 공급면적: "+basic_area2+f"㎡ (약{제곱미터_평_변환(basic_area2)}평)"
    #해당층
        print('building_usedate:'+str(basic_floor))
        특정위치의x번째입력태그찾기('해당층 / (해당동) 총층', 'text', 1).send_keys(basic_floor)
        if basic_floor: room_memo += "\n"+"-- 해당층: "+basic_floor+"층"
    # pyautogui.alert("정상?")   
    #총층
        print('building_usedate:'+str(basic_totflr))
        특정위치의x번째입력태그찾기('해당층 / (해당동) 총층', 'number', 1).send_keys(basic_totflr)
        basic_totflr += "\n"+"-- 총층: "+basic_totflr+"층"
    #층노출동의여부
    if obinfo_type1 in ['원룸','주택']:
        if object_type != '주거용':
            라디오버튼선택('층노출 동의여부', '동의 (층 노출)')
        else:
            라디오버튼선택('층노출 동의여부', '동의안함 (고/중/저 노출)')
    #방수/욕실수
    if obinfo_type1 in ['원룸','주택']:
        if obinfo_type1 == '원룸':
            라디오버튼선택('방수 / 욕실수', '1개')
            특정위치의x번째입력태그찾기('방수 / 욕실수', 'number', 1).send_keys(basic_bcount)
        elif obinfo_type1 == '주택':
            특정위치의x번째입력태그찾기('방수 / 욕실수', 'number', 1).send_keys(basic_rcount)
            특정위치의x번째입력태그찾기('방수 / 욕실수', 'number', 2).send_keys(basic_bcount)
        if basic_rcount: room_memo += "\n"+"-- 방수: "+basic_rcount
        if basic_bcount: room_memo += " / 욕실수: "+basic_bcount
    #방향
    print('r_direction:'+r_direction+" room_direction:"+room_direction)
    if obinfo_type1 in ['상가점포','사무실']:
        print('building_usedate:'+str(room_direction))
        room_direction = '남' if room_direction == '' else room_direction
        셀렉스항목선택(room_direction, '//*[@id="app"]/div/div/div[3]/div/div[1]/div[11]/table/tbody/tr[13]/td/div[1]/div')
    #방향기준/방향
    if obinfo_type1 in ['원룸','주택']:
        셀렉스항목선택('안방', '//*[@id="app"]/div/div/div[3]/div/div[1]/div[11]/table/tbody/tr[12]/td/div[1]/div[1]')
        if room_direction: 셀렉스항목선택(room_direction, '//*[@id="app"]/div/div/div[3]/div/div[1]/div[11]/table/tbody/tr[12]/td/div[1]/div[2]')
    # pyautogui.alert("방향기준/방향 확인")
    #세대(가구수)
    if tr_target != '토지':
        print("세대(가구수) building_type:" + building_type )
        if building_type == '집합':
            print("세대(가구수) building_hhld:" + str(building_hhld) )
            세대가구수 = building_hhld
        else:
            print("세대(가구수) building_fmly:" + str(building_fmly) )
            세대가구수 = building_fmly
        if obinfo_type1 in ['원룸','주택']:
            특정위치의x번째입력태그찾기('세대(가구수)', 'number', 1).send_keys(세대가구수)
    # pyautogui.alert("세대(가구수) 확인")
    #방거실형태
    if obinfo_type1 in ['주택']:
        라디오버튼선택('방거실형태', '분리형')
    # pyautogui.alert("방거실형태 확인")
    #복층여부
    if obinfo_type1 in ['원룸','주택']:
        if '복층형' in room_important:
            라디오버튼선택('복층여부', '복층')
        else:
            라디오버튼선택('복층여부', '단층')
    # pyautogui.alert("복층여부 확인")
    #주차가능여부
    if obinfo_type1 in ['원룸','주택','상가점포','사무실']:
        print('building_pn:'+str(building_pn)+' building_option:'+building_option)
        if building_pn=='0' and '주차장' not in building_option:
            라디오버튼선택('주차가능여부', '주차 불가능')
            # 특정위치의x번째태그찾기('주차가능여부', 'radio', 2).click()
        else:
            라디오버튼선택('주차가능여부', '주차 가능')
            # 주차가능여부파트 = 특정위치의x번째태그찾기('주차가능여부', 'radio', 2)
            # 주차가능여부파트.click()
        #총주차대수
        print('building_pn:'+str(building_pn))
        특정위치의x번째입력태그찾기('총 주차대수', 'number', 1).send_keys(building_pn)
        #건축물용도
        print('building_purpose:'+str(building_purpose))

        # 구분자 목록
        delimiters = [',', '.', ' 및 ', '/', '또한']        
        # 구분자들을 이스케이프 처리하고 정규 표현식 패턴을 만듭니다.
        pattern = '|'.join(re.escape(delimiter) for delimiter in delimiters)
        # 주어진 패턴으로 문자열을 분할합니다.
        parts = re.split(pattern, building_purpose)
        # 첫 번째 부분을 반환합니다. 공백 제거를 포함
        building_purpose = parts[0].strip() 
        # if ',' in building_purpose:
        #     building_purpose = building_purpose.split(',')[0]
        # elif '.' in building_purpose:
        #     building_purpose = building_purpose.split('.')[0]
        # elif ' 및 ' in building_purpose:
        #     building_purpose = building_purpose.split(' 및 ')[0]
        셀렉스항목선택(그룹별명칭변환('건축물용도', building_purpose), '//*[@id="app"]/div/div/div[3]/div/div[1]/div[11]/table/tbody/tr[30]/td/div[1]/div/div[1]')
        if building_purpose: building_memo += "\n"+"-- 건축물 주용도: "+building_purpose
        
        #건축물일자
        셀렉스항목선택('사용승인일', '//*[@id="app"]/div/div/div[3]/div/div[1]/div[11]/table/tbody/tr[31]/td/div[1]/div[1]/div/div[1]')
        # pyautogui.alert("사용승인일선택 확인")
        print('building_usedate:'+str(building_usedate))
        usedate = building_usedate.split("-")
        if building_usedate == '0000-00-00':
            셀렉스항목선택('준공인가일', '//*[@id="app"]/div/div/div[3]/div/div[1]/div[11]/table/tbody/tr[31]/td/div[1]/div[1]')
            셀렉스항목선택('2010', '//*[@id="app"]/div/div/div[3]/div/div[1]/div[11]/table/tbody/tr[31]/td/div[1]/div[1]/div/div[2]')
            셀렉스항목선택('없음', '//*[@id="app"]/div/div/div[3]/div/div[1]/div[11]/table/tbody/tr[31]/td/div[1]/div[1]/div/div[3]')
        else:
            셀렉스항목선택('사용승인일', '//*[@id="app"]/div/div/div[3]/div/div[1]/div[11]/table/tbody/tr[31]/td/div[1]/div[1]')
            셀렉스항목선택(usedate[0], '//*[@id="app"]/div/div/div[3]/div/div[1]/div[11]/table/tbody/tr[31]/td/div[1]/div[2]')
            셀렉스항목선택(usedate[1], '//*[@id="app"]/div/div/div[3]/div/div[1]/div[11]/table/tbody/tr[31]/td/div[1]/div[3]')
            셀렉스항목선택(usedate[2], '//*[@id="app"]/div/div/div[3]/div/div[1]/div[11]/table/tbody/tr[31]/td/div[1]/div[4]')
#원룸/투룸 방찾기
    #방구조(타입)
    if obinfo_type1 in ['원룸','주택']:
        if '오픈형' in room_important:
            라디오버튼선택('방 구조(타입)', '오픈형')
        # elif '분리형' in room_important:
        else:
            라디오버튼선택('방 구조(타입)', '분리형')
    #방특징
        #방특징 목록생성
        #신축: 준공일5년이내
        #풀옵션: 냉장고,세탁기,싱크대,가스렌지,에어컨 포함
        #큰길가: 중로이상 접
        #엘리베이터: 건물옵션에 포함
        #애완동물: 호실옵션에 포함
        #옥탑: 해당층이 지상층이상
        방특징항목들 = 목록_변환('방특징', room_important)
        라벨들로체크박스클릭('방 특징', 방특징항목들)
#시설정보
    if obinfo_type1 != '토지':
        if tr_target == '건물':
            if building_important: building_memo += "\n"+"-- 건물특징: "+building_important
            if building_option: building_memo += "\n"+"-- 건물옵션: "+building_option
        if tr_target == '층호수':
            if room_important: room_memo += "\n"+"-- 호실특징: "+room_important
            if room_option: room_memo += "\n"+"-- 호실옵션: "+room_option
        # print("optionImportant:"+optionImportant)
        시설정보항목들 = 목록_변환('시설정보', optionImportant)
        print("시설정보항목들:"+시설정보항목들)
        # if object_type == '주거용':
        #     #난방시설
        #     셀렉스항목선택('개별난방', '//*[@id="app"]/div/div/div[3]/div/div[1]/div[13]/table/tbody/tr[1]/td/div')
        #     #난방연료
        #     셀렉스항목선택('도시가스', '//*[@id="app"]/div/div/div[3]/div/div[1]/div[13]/table/tbody/tr[2]/td/div')
        #냉방시설
        라벨들로체크박스클릭('냉방시설', 시설정보항목들)
        #생활시설
        if obinfo_type1 in ['원룸','주택']:
            라벨들로체크박스클릭('생활시설', 시설정보항목들)
        #보안시설
        라벨들로체크박스클릭('보안시설', 시설정보항목들)
        #기타시설
        라벨들로체크박스클릭('기타시설', 시설정보항목들)
    else:
        if land_important: land_memo += "\n"+"-- 토지특징: "+land_important
#매물상세정보
    print('매물상세정보 시작')
    description = ""
    description += "\n"+" ━━━━━━━━━━━━━━━━━━━━━━"
    description += "\n"+" 【 오산 " + 그룹별명칭변환('전문분야', object_type) + " 전문 『 나상권공인중개사사무소 』】"
    description += "\n"
    description += "\n"+"   ▷ 상호 : 나상권공인중개사사무소  대표 : 나상권 "
    description += "\n"+"   ▶ 등록번호 : 제41370-2015-00046호 "
    description += "\n"+"   ▷ 소재지 : 오산시 궐동 640-9 성지빌딩 102호"
    description += "\n"+"   ▶ 대표번호 : 031) 375 - 5555 "
    description += "\n"
    description += "\n"+"   오산에서방구하기 오방  https://osanbang.com/ "
    description += "\n"+" ━━━━━━━━━━━━━━━━━━━━━━"
    description += "\n"+" "
    description += f"□■ 신속한 상담을 위해 '네이버부동산에서 매물번호[ {object_code_new} ]를 보고 문의드립니다.'라고 말씀해주세요~"
    description += "\n"
    description += "\n"+"□■ 거래정보"
    description += trading_memo
    description += rent_memo
    description += premium_memo
    description += "" if room_memo == "\n□■ 호실정보" else (room_memo + r_add_memo)
    description += "" if building_memo == "\n□■ 건물정보" else building_memo
    description += "" if land_memo == "\n□■ 토지정보" else land_memo
    
    
    # description += "\n"+" "
    # description += "\n"+" □■ 위치"
    # description += "\n"+"--"
    # description += "\n"+"--"
    # description += "\n"+"--"
    # description += "\n"+" "
    # description += "\n"+" □■ 특징"
    # description += "\n"+"--"
    description += "\n"+""
    description += "\n"+""
    description += "\n"+""
    description += "\n"+""" "원하시는 매물을 찾을 때까지 끝까지 최선을 다하겠습니다." """   
    description += "\n"+""
    description += "\n"+""" "매물에 관한 자세한 상담을 원하시면 지금 바로 전화주세요!!" """   
    description += "\n"+""
    description += "\n"+""" "문의주시면 더 많은 비공개 매물까지도 안내받으실 수 있습니다." """   
    description += "\n"+""
    description += "\n"+""" "오산/화성/평택/용인 최대 빅데이터 보유!! 오산에서방구하기 오방!!" """   
    description += "\n"+""
    description += "\n"+""" "차별화된 중개시스템으로 원하는 매물을 쉽게!! 빠르게!! 정확하게!!" """   
    # 태그별개수출력('상세정보')
    # 상세정보script = "arguments[0].value = arguments[1];"
    상세정보script = """
    var textarea = arguments[0];
    var value = arguments[1];
    textarea.value = value;
    var event = new Event('input', { bubbles: true });
    textarea.dispatchEvent(event);
    """
    driver.execute_script(상세정보script, 특정위치의x번째입력태그찾기('상세정보', 'textarea', 1), description)
    # 특정위치의x번째입력태그찾기('상세정보', 'textarea', 1).send_keys(description) #느림 description
    print('매물상세정보 종료')
    # pyautogui.alert("정상?")   
    # 비공개script = "arguments[0].value = arguments[1];"
    비공개script = """
    var textarea = arguments[0];
    var value = arguments[1];
    textarea.value = value;
    var event = new Event('input', { bubbles: true });
    textarea.dispatchEvent(event);
    """
    driver.execute_script(비공개script, 특정위치의x번째입력태그찾기('관리자 메모(비공개 정보)', 'textarea', 1), basic_secret+obinfo_content)
    # 특정위치의x번째입력태그찾기('관리자 메모(비공개 정보)', 'textarea', 1).send_keys(basic_secret+obinfo_content) 
    
#검증방식
    try:
        #네이버등록권
        특정위치의x번째입력태그찾기('네이버등록권', 'radio', 1).click()
        # pyautogui.alert("정상?")
    except:
        fail_msg = '\n- 네이버등록권 선택실패'
          
#의뢰인정보
    # pyautogui.alert("정상?")  
    if master_check=='Y' and len(master_names) > 0: #등기확인된 소유주
        print("master_names:",master_names)
        if contactor_info and 'contactor_name' in contactor_info: #본인 또는 대표인 접촉자정보존재
            print("1")
            if contactor_info['contactor_name'] in master_names and contactor_info['contactor_type'] == '본인': #소유주정보에 등기확인된 소유주 존재
                print("3")
                소유자명 = contactor_info['contactor_name'] if '이름미확인' not in contactor_info['contactor_name'] else ''
            elif contactor_info['contactor_name'] not in master_names and contactor_info['contactor_type'] == '대표':
                print("5")
                소유자명 = master_name
            소유자연락처 = contactor_info['contactor_phone1']
            의뢰인유형 = contactor_info['contactor_type']
        else:
            의뢰인유형 = '본인'  
            소유자명 = master_name     
    else:
        fail_msg = '\n- 소유자이름 입력 실패'

    특정위치의x번째입력태그찾기('등기부상 소유자 이름', 'text', 1).send_keys(소유자명) 
    # pyautogui.alert("정상?")  
    특정위치의x번째입력태그찾기('의뢰인과 등기부상 소유자와의 관계', 'text', 1).send_keys(의뢰인유형) 
    if len(소유자연락처) == 11:
        특정위치의x번째입력태그찾기('소유자 연락처 (홍보확인서2)', 'radio', 1).click()
        # pyautogui.alert("정상?")   
        셀렉스항목선택('010', '//*[@id="app"]/div/div/div[3]/div/div[1]/div[16]/table/tbody/tr[3]/td/div[2]/div[1]') #느림
        # pyautogui.alert("정상?") 
        가운데4자리 = 소유자연락처[3:7]  # 예: '01012345678'에서 '1234' 추출
        마지막4자리 = 소유자연락처[7:11]  # 예: '01012345678'에서 '5678' 추출  
        특정위치의x번째입력태그찾기('소유자 연락처 (홍보확인서2)', 'number', 1).send_keys(가운데4자리)  #느림
        # pyautogui.alert("정상?")   
        특정위치의x번째입력태그찾기('소유자 연락처 (홍보확인서2)', 'number', 2).send_keys(마지막4자리)  #느림
    # pyautogui.alert("정상?") 
      
#약관동의
    # '모두동의 (필수)' 텍스트를 가진 label 태그 찾기
    agreement_label = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//label[normalize-space(.)='모두동의 (필수)']"))
    )
    # label 태그와 연관된 checkbox 클릭
    if agreement_label:
        # label 태그의 for 속성을 사용하여 연관된 input 요소를 찾아 클릭
        checkbox_id = agreement_label.get_attribute('for')
        if checkbox_id:
            checkbox = driver.find_element(By.ID, checkbox_id)
            checkbox.click()
            print("Checkbox has been clicked.")
        else:
            print("No checkbox ID found for the label.")
    else:
        print("Label with text '모두동의 (필수)' not found.")
    # pyautogui.alert("정상?") 

#물건사진 폴더열기
    main_dir = 'Z:\\업무자료\\4사진자료&이미지자료(외부유출금지)\\1주거용물건, 상업용물건\\'
    path_dir = main_dir + data['folderPath'] #'경기도\\오산시\\궐동\\654-9\\썬플라워\\1층\\1층'
    print(path_dir)
    try:
        os.startfile(path_dir)
        print('폴더열기 성공') 
    except:
        print('폴더열기 에러(해당폴더 없음)')  
    
    pyautogui.alert(fail_msg+"\n\n매물등록창을 닫으시겠습니까?")
    driver.close()
    return errarr    

# ☺ 카톡아이디 : cjwcan
# -------------------------------
# ♣ 추천매물

# ◈강남 무권리 매장
# 1.역삼역대(실75평) 보증금2억/월1000만/관200만
#   역삼역대로변 특A급매장
# 2.강남구청역(실62평) 보증금1억5천/월990만/관90만
#    대로변 코너건물
# 3.역삼동(실45평) 보증금5천/월400만/관50만
#    코너건물

# ◈강남상권 카페(강남역메인상권)
# 1. (실20평)보증금5천/월400만/관50만/권리금5천(협의가능)/합1억

# ◈강남상권 음식점
# 1. (실17평) 보증금7천 / 월350만 / 관15만 / 권리금4천 / 합1억천만
# 2. (실9평) 보증금3천 / 월180만/권리금7백/ 합3천7백만

# -------------------------------------------------------

# ✿매물소개

# ✦ 위치 : 강남구 논현동 먹자라인

# ✦ 임대면적 : 실34평

# ✦ 해당층 : 3층

# ✦ 임대내역 : 보증금 3천 / 월세 310만  / 관리비30만

# ✦ 권리금 : 최저가로 진행중 - 전화문의

# ✦ 기타 : 1인룸4개 / 2인룸2개 /샤워실 및 대기실등 인테리어 A급유지


# ✪ 매물특징

# √ 논현동 먹자라인에 위치 입지가 좋아 고객 유치하기 좋음

# √ 인테리어 모던한 스타일로 깔끔하게 유지중

# √ 권리금 강남에서 최저가로 진행중이니 24시간 언제든 연락주세요

# ---------------------------------

# ☺ 고객님이 필요한 매물을 최단시간내 A급으로 찾아드리겠습니다


# ☎ 대표번호 : 02-554-4550

# description += "\n"+"-- 🔴 임차 전속 물건 입니다 / 전화주시면 공동중개 가능합니다.🔴"

# description += "\n"+"-- 1️⃣ 층 수 : 3층 (총 5층 건물)"
# description += "\n"+"-- 2️⃣ 면 적 : 약 40평"
# description += "\n"+"-- 3️⃣ 주 차 : 1대 제공"
# description += "\n"+"-- 4️⃣ 보 증 금 : 3,000만원"
# description += "\n"+"-- 5️⃣ 임 대 료 : 360만원 / 관리비 : 실비정산"
# description += "\n"+"-- 6️⃣ 입주시기 : 항시 가능"
# description += "\n"+"-- 7️⃣ 권 리 금 : 적정한 인테리어 비용 있습니다! 자세한 사항은 부동산으로 연락 부탁 드립니다. "

# description += "\n"+"--  💥 매물 참고 사항 💥"
# description += "\n"+"-- 🔴 학동역 도보 4분 거리 위치"
# description += "\n"+"-- 🟠 직사각형 구조로 활용성 좋음"
# description += "\n"+"-- 🟡 역세권 인접하여 접근성 용이"
# description += "\n"+"-- 🟢 인근 거리 편의점 대형 마트 인접 "
# description += "\n"+"-- 🔵 좋은 위치로 인해 다양한 활용 가능"
# description += "\n"+"-- 🟣 확장성 높은 매물"

# -------------📝직접 눈으로 본 매물정보📝--------------
# ☑️️ 논현동 인테리어 및 시설 갖춘 다이닝

# ☑️️ 전용평수 :　44평

# ☑️️ 메인 업무 홀 + 룸1 + 창고1 + 주방 구조

# ☑️ 소방시설 + 대형 냉난방 + 환기시설 완비

# ☑️ 권리금 : 협의

# ☑️ 고급 다이닝 적극 추천

# ☑️ 무료 주차 1대

# 🚨🚨 날짜, 금액, 렌트프리 조율 해드립니다 🚨🚨
# 🚨🚨 위치, 조건 등에 맞춰 성심껏 찾아드립니다 🚨🚨


# ■ 수(秀)부동산중개법인은 실사진 실매물 광고가 원칙입니다.
# ■ 사진으로만 판단하시기보다 사무실의 컨디션을 직접 눈으로 확인하시는게 좋습니다.
# ■ 고객님께서 마음에 드신다면 보증금,임대료,입주시기 최대한 협의 봐드립니다.


# 🟧 리얼리부동산은?

# 다양한 분야의 책임있는 전문가가 모인 중개사무소 입니다.
# 저희는 협력하고, 공유합니다. 좋은매물소개와 좋은손님소개 하는것에 집중합니다.

# ✅ 고객이 원하는것에 집중합니다.
# 1) 빠르고 정확한 정보를 전달 합니다.
# 2) 구성원 모두가 신속하고 빠릿하게 움직입니다.
# 3) 계약보다는 안전에 우선합니다.

# ✅ 물건접수
# 1) 매물 광고를 아끼지 않습니다.(퀄리티 있는 광고를 지향합니다.)
# 2) 고객이 원할시 보안으로 진행 됩니다.(사내+중개사협력망)

# 📍 물건데이터 多 / 손님데이터 多
# 📍 분양, 분양대행, 건물(호실) 관리

# ❌본 광고 형식은 시작부동산의 창작물로써 무단 사용 금지합니다❌

# ❌임차인 전속(친척입니다) / 오토 운영으로 찾아가셔도 제 번호 알려줍니다❌
# ❌네이버 광고 금지(신고합니다)❌

# 📌 매물정보 📌  
# ✅【 금 액 】 : 보증금 3억원 / 월세 1,100만원(관리비 포함)
# ✅【 권 리 】 : 유선문의 
# ✅【 면 적 】 : 1층(약 20평) + 2층(약 80평)
# ✅【 층 수 】 : 1층 일부 + 2층 전체

# 📌상세정보 📌
# ✅【 위   치 】 : 언주역 도보1분, 차병원사거리 코너 위치
# ✅【 주   차 】 : 협의
# ✅【 입주일 】 : 협의
# ✅【 현업종 】 : 카페
# ✅【 화장실 】 : 외부 남녀 분리 화장실 
# ✅【 간   판 】 : 가능(세부사항 협의) 
# ✅【 냉난방기 】 : 천장형 에어컨
# ✅【 특   징 】 : 
# ➡카페 최적화, 2층 외부 통유리
# ➡내부 연결 계단
# ➡넓은 간판 사용 가능
# ➡이전 업종 투썸플레이스로 10년 넘게 운영
# ➡면적대비 합리적인 임대료
# ➡업종 문의 언제든지 연락 주세요
# ➡렌트프리/금액/세부사항 조율 최대한 신경써드리겠습니다

# 📌시작부동산만의 장점 📌
# 👍【 조율 】 - 렌트프리 / 금액 / 세부사항 / 조건  적극적 협의
# 👍【 순발력 】 빠르고 신속한 응대
# 👍【 젊음 】 - 넘치는 에너지의 기동력
# 👍【 센스 】 - 원스톱 브리핑 및 투어 후 매물 요점 자료 안내
# 👍【 정직 】 - 거짓 없이 정확하고 확실한 정보 전달
# 👍【 신뢰 】 - 계약 후에도 지속적인 관리
# 👍【 픽업 서비스 】
