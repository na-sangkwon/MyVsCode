import os
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

from selenium.webdriver.common.alert import Alert
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
        
        if li_id == 'li_regDtl02gsanggaIpjiCd': #난방방식 선택
            pyautogui.alert("버튼클릭("+li_text+") 준비 button_id:"+button_id)
        
        # 버튼 ID를 사용하여 버튼 요소 찾기
        # dropdown_button = li_element.find_element(By.ID, button_id)
        dropdown_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, button_id))
        )
        ActionChains(driver).move_to_element(dropdown_button).perform()
        
        if li_id == 'li_regDtl02gsanggaIpjiCd': #난방방식 선택
            pyautogui.alert("버튼클릭("+li_text+") 종료")
             
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


def 라벨텍스트로입력값넣기(driver, 라벨텍스트, 넣을값):
    try:
        # 넣을값 = str(넣을값)
        print(f"라벨텍스트로입력값넣기({driver}, {라벨텍스트}, {넣을값})")
        
        # '방향 기준' 라벨에 해당하는 span 내의 input 요소 찾기
        
        # pyautogui.alert("여기가 문제??")
        span_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//label[contains(text(), '" + 라벨텍스트 + "')]/following-sibling::span"))
            # EC.presence_of_all_elements_located((By.XPATH, "//label[contains(text(), '" + 라벨텍스트 + "')]/following-sibling::span[input[@type='text']]"))
        )
        print(라벨텍스트+" span요소들:"+ str(len(span_elements)))
        if len(span_elements)==1:
            print(라벨텍스트+" 입력요소 1개보임")
            input_element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(span_elements[0].find_element(By.XPATH, ".//input"))
            )
            ActionChains(driver).move_to_element(input_element).perform()
            input_element.send_keys(넣을값)
        else:
            print(라벨텍스트+f" 입력요소 {str(len(span_elements))}개보임")
            for span in span_elements:
                # input_element = span.find_element(By.XPATH, ".//input")
                print("span: ", span)
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
                    print("입력값넣기 성공")
                    return True
                else:
                    print(라벨텍스트+" 입력요소 안보임")
        
    except TimeoutException as e:
        print("라벨텍스트로입력값넣기 타임아웃 오류 발생: ", e)
        pyautogui.alert("여기가 문제맞아??")
    except Exception as e:
        print(f"라벨텍스트로입력값넣기 오류 발생: {e}")
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
    
    hanbang_code = '' if data['adData']['한방']=='' else data['adData']['한방']
    
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
    land_totarea = data['landData'][0]['land_totarea']#대지면적
    land_option = data['landData'][0]['land_option']#토지옵션
    
    
    
    

    if tr_target == '건물' or tr_target == '층호수':
        building_name = data['buildingData']['building_name'] if  data['buildingData']['building_name'] not in ['무명건물'] else '' #건물명
        location_building = '' if building_name == '' else ' ' + building_name
        location_detail += location_building
        basic_totflr = str(int(data['buildingData']['building_grndflr']) + int(data['buildingData']['building_ugrndflr'])) #전체층
        building_usedate = str(data['buildingData']['building_usedate']) #준공일
        building_pn = data['buildingData']['building_pn'] #주차
        secret_3 = '' if data['buildingData']['building_memo'] == '' else data['buildingData']['building_memo'] + Keys.ENTER
        if secret_3 != '' : object_detail += Keys.ENTER + '- ' + secret_3
        building_archarea = data['buildingData']['building_archarea'] #건축면적
        building_totarea = data['buildingData']['building_totarea'] #연면적
        building_direction = data['buildingData']['building_direction'] #방향
        building_purpose = data['buildingData']['building_purpose'] #주용도
        building_elvcount = data['buildingData']['building_elvcount'] #승강기수
        building_option = data['buildingData']['building_option']#건물옵션
        building_option_arr = building_option.split(',')
        tot_options = ",".join([land_option, building_option])

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
        if room_direction == '': 
            pyautogui.alert("호실방향 설정후 다시시작하세요~")
            exit()
            

    
    # ChromeDriver 경로 설정
    driver = webdriver.Chrome(options=options)
    # driver = webdriver.Chrome('/chromedriver', options=options)
    # driver = webdriver.Chrome(ChromeDriverManager().install())

    # URL 열기
    # driver.maximize_window()
    
    #driver.get('https://mobile.karhanbang.com/kren/mamul/list')
    driver.get('https://m.karhanbang.com/mptl/main')
    
    def 기본주소정보등록():
        nonlocal basic_area1,basic_area2,direction_stn
        driver.execute_script("fn_moveRegDtl('1')") #기본/주소 정보
        
        # pyautogui.alert("확인필요")  
        # driver.find_element(By.XPATH, '//*[@id="regDtl01cateCd-button"]').click() #매물유형 클릭
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
        리스트선택(driver, 'li_regDtl01cateCd', obinfo_type) #매물유형선택
        리스트선택(driver, 'li_regDtl01gureCd', obinfo_ttype) #거래유형선택
        WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="div_regDtl01soonMoveYn"]/span/label'))).click() #즉시입주 클릭
        
        # pyautogui.alert("확인필요")  
        #임대 구분(전체임대 기본설정)
        # WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.ID, "regDtl01rentCd01"))).click()
        driver.execute_script("arguments[0].click();", driver.find_element(By.ID, "regDtl01rentCd01"))

        
        #매물 주소
        driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, '//*[@id="li_regDtl01address"]/span/button')) #지역검색 버튼 클릭
        print("주소 입력창에 "+dosidongli+"입력")
        주소입력창 = WebDriverWait(driver, 3).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="asp_text"]')))
        주소입력창.send_keys(dosidongli+Keys.ENTER) #검색어 입력창에 동+리까지 입력
        # driver.find_element(By.XPATH, '//*[@id="asp_icSearch"]').click() #돋보기 클릭 
        time.sleep(0.5)
        주소입력창.send_keys(Keys.ENTER)
        페이지완전로딩대기(driver)
        # 검색된 리스트 "asp_areaSelWrap_div"를 가진 div 내부의 모든 'li' 요소 찾기
        li_elements = WebDriverWait(driver, 3).until(
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
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, '//*[@id="regDtl01bonNo"]'))).send_keys(land_bon) #본번 입력
        # driver.find_element(By.XPATH, '//*[@id="regDtl01bonNo"]').send_keys(land_bon) #본번 입력
        # # JavaScript를 사용하여 본번과 부번 값을 직접 설정
        # driver.execute_script("document.getElementById('regDtl01bonNo').value = arguments[0];", land_bon)

        # time.sleep(0.1)
        driver.find_element(By.XPATH, '//*[@id="regDtl01buNo"]').send_keys(land_bu) #부번 입력
        # pyautogui.alert("올바르게 지번이 입력되었는지 확인")
        
        #건물명
        라벨텍스트로입력값넣기(driver, '건물명', building_name)
        
        #층
        # pyautogui.alert("확인필요")  
        if int(basic_floor) < 0 : driver.execute_script("arguments[0].click();", driver.find_element(By.ID, "regDtl01currTopBottom02")) #지하 클릭
        라벨텍스트로입력값넣기(driver, '층', basic_floor)
        # pyautogui.alert("올바르게 층 입력되었는지 확인")
        #총층
        라벨텍스트로입력값넣기(driver, '총 층', int(basic_totflr))
        print("object_type:",object_type)
        # pyautogui.alert("object_type확인: "+object_type)
        if object_type == '주거용':
            #공급 면적
            라벨텍스트로입력값넣기(driver, '공급 면적', basic_area2)
        elif object_type == '상업용' :
            #계약 면적
            라벨텍스트로입력값넣기(driver, '계약 면적', basic_area2)
        # pyautogui.alert("올바르게 계약 입력되었는지 확인")   
        #전용 면적  
        라벨텍스트로입력값넣기(driver, '전용 면적', basic_area1)
        # pyautogui.alert("올바르게 전용 입력되었는지 확인")
        #방향
        if room_direction != '':
            print("방향 입력시작")
            라벨텍스트로라디오선택(driver, 'li_regDtl01directionCd', room_direction)
        
        #방향 기준
        print("방향기준 입력시작")
        if object_type != '주거용':
            라벨텍스트로입력값넣기(driver, '방향 기준', '주출입문')
        else:
            if direction_stn=='': direction_stn='안방'
            라벨텍스트로라디오선택(driver, 'li_regDtl01directionInfo', direction_stn)
            라벨텍스트로입력값넣기(driver, '룸 수', '9')
            라벨텍스트로입력값넣기(driver, '욕실 수', '4')
            
        # pyautogui.alert("전송종료 준비")
        # 'togList' 클래스를 가진 ul 요소 아래의 모든 li 요소를 찾음
        매물노출리스트 = driver.find_elements(By.CSS_SELECTOR, 'ul.togList li')
        # 각 li 요소를 순회하면서 체크박스가 체크되어 있지 않은 경우 클릭
        for li in 매물노출리스트:
            label = li.find_element(By.CSS_SELECTOR, 'label')
            if label.text == "전송종료":
                li.click()
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
        #월세금    
        라벨텍스트로입력값넣기(driver, '월세금', obinfo_rent1)
        #보증금    
        라벨텍스트로입력값넣기(driver, '보증금', obinfo_deposit1)
        if object_type != '주거용':
            #시설비    
            라벨텍스트로입력값넣기(driver, '시설비', '0')
            #권리금
            if isinstance(premium, int) and premium > 0:   #자연수일 경우에만 실행
                라벨텍스트로입력값넣기(driver, '권리금', premium)
            else:
                라벨텍스트로입력값넣기(driver, '권리금', '0')
        else:
            #발코니
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
            print("개별세탁 선택")
            리스트선택(driver, 'li_regDtl02setakCd', '개별세탁')
            #주방
            print("개별주방 선택")
            리스트선택(driver, 'li_regDtl02jubangCd', '개별주방')
            #욕실 구분
            print("개별 욕실 선택")
            라벨텍스트로라디오선택(driver, 'li_regDtl02yoksilCd','개별 욕실')
            #옵션
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
            라벨텍스트로라디오선택(driver, 'li_regDtl02warmCd', 그룹별명칭변환('난방 방식', '개별난방'))
        elif object_type== '상업용':
            리스트선택(driver, 'li_regDtl02warmCd', '개별난방')
            라벨텍스트로라디오선택(driver, 'li_regDtl02coldCd', '개별냉방')
        # pyautogui.alert("난방방식 확인")
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
        if obinfo_type1 == '상가점포':
            라벨텍스트로라디오선택(driver, 'li_regDtl02storeUseCd', 그룹별명칭변환('주용도', obinfo_type1))
        elif obinfo_type1 == '사무실':
            라벨텍스트로라디오선택(driver, 'li_regDtl02officeUseCd', 그룹별명칭변환('주용도', obinfo_type1))
        
        #주차
        
        
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
        print("건축물용도", 그룹별명칭변환('건축물용도', building_purpose))
        리스트선택(driver, "li_regDtl02buildUseCd", 그룹별명칭변환('건축물용도', building_purpose))
        # pyautogui.alert("올바르게 건축물용도 선택되었는지 확인")
        
        #사용승인일
        if building_usedate == '' :
            driver.find_element(By.XPATH, '//*[@id="regDtl02dayCheck"]').click() #확인불가 클릭
        else:
            # building_usedate = building_usedate.replace('-', '')
            print("building_usedate",building_usedate)
            # driver.find_element(By.XPATH, '//*[@id="regDtl02useApprovalDay"]').send_keys(building_usedate)
            driver.execute_script("document.getElementById('regDtl02useApprovalDay').value = arguments[0];", building_usedate)
        driver.execute_script("saveCmptnRegDtl02()") #완료
        # pyautogui.alert("메모기타정보등록 입력확인")
        
        # driver.execute_script("saveTempRegDtl02()") #임시저장
        # WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="popAlertExecuteBtnId"]'))).click() #임시저장 확인팝업 예 클릭
        print("금액옵션정보등록 완료")
        
    def 메모기타정보등록():
        # nonlocal object_code
        # driver.execute_script("fn_moveRegDtl('3')") #메모/기타 정보 
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="btn_atlfslRegListRegDtl03"]'))).click()
        
        # #매물 특징
        # driver.find_element(By.XPATH, '//*[@id="regDtl03feature"]').send_keys("관리비내역")
        
        #매물 설명
        if obinfo_ttype == '매매':
            object_code = object_code_new
        else:
            object_code = obang_code        
        detail = ''
        detail += Keys.ENTER + '고객님께서는 한방 사이트에서 등록된 매물[☞매물번호: ' + object_code + ']을 보고 계십니다.' + Keys.ENTER
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
        detail += Keys.ENTER + '▣편하게 연락 주시고 홈페이지도 방문해보세요!!'
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
        driver.find_element(By.XPATH, '//*[@id="regDtl03secretMemo"]').send_keys(object_detail)
        # pyautogui.alert("고객정보등록 등록 확인")
        driver.execute_script("saveCmptnRegDtl03()") #완료
        print("메모기타정보등록 완료")    
        
    def 고객정보등록():
        # driver.execute_script("fn_moveRegDtl('4')") #고객 정보 
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="btn_atlfslRegListRegDtl04"]'))).click() #고객 정보 
        driver.execute_script("saveCmptnRegDtl04()") #완료
        print("고객정보등록 완료")     
    
    # 요소가 클릭 가능할 때까지 대기
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="deviceCheck"]/button'))).click() #한방앱/모바일웹 화면선택 팝업닫기
    driver.find_element(By.XPATH, '//*[@id="mptlFooter"]/div/a[5]').click() #메뉴클릭
    # WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="component-mainMenu-7755237386019465"]/div[1]/a/div'))).click() #로그인 및 회원가입 클릭
    # "component-mainMenu-"로 시작하는 아이디를 가진 요소를 찾기
    element_xpath = "//*[starts-with(@id, 'component-mainMenu-')]/div[1]/a/div"
    element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, element_xpath)))
    element.click()    
    driver.find_element(By.XPATH, '//*[@id="agntLoginTabBtn"]').click() #공인중개사 로그인 클릭
    driver.find_element(By.XPATH, '//*[@id="userId"]').send_keys('bsleemanse') #아이디 입력
    driver.find_element(By.XPATH, '//*[@id="password"]').send_keys('tkdrnjs1001') #비번 입력
    driver.find_element(By.XPATH, '//*[@id="agntLoginBtn"]').click() #로그인 클릭
    팝업버튼 = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="deviceCheck"]/button'))) #한방앱/모바일웹 화면선택 팝업
    # 요소가 보이면 클릭
    if 팝업버튼.is_displayed():
        팝업버튼.click()
    # pyautogui.alert("확인필요")    
    
    driver.execute_script("fnMmGoViewMove('mamulList')")  # 내 매물 관리
    search_input = driver.find_element(By.XPATH, '//*[@id="atlfslListSearchInput"]')
    search_input.send_keys(hanbang_code)  # 검색어(한방매물번호) 입력
    print("입력한 한방매물번호:"+hanbang_code)
    search_button = driver.find_element(By.XPATH, '//*[@id="atlfslListSearchBtn2"]')
    search_button.click()  # 돋보기 클릭
    time.sleep(1)

    result = driver.find_element(By.ID, "atlfslListTotCnt").text
    
    # result = "1"
    print(f"검색결과값은 {result}개 입니다.")
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

        # print("3")
        # # 작업 종료
        # driver.quit()
        # exit()

    else:
        print("텍스트 값은 0입니다.")
        # pyautogui.alert("확인 클릭시 신규등록을 시작합니다.")  
        
        driver.execute_script("divShowEvent('atlfslRegIntro','매물|등록')") #매물등록 
        driver.execute_script("fn_atlfslRegNew()") #새로내놓기
        # pyautogui.alert("확인필요")  
        # 기본주소정보등록()
        기본주소정보등록()
        금액옵션정보등록()
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
                매물번호 = 매물번호span.text.replace('매물번호 ', '')  # '매물번호 '를 제거한 나머지 문자열
                print(f"매물번호: {매물번호}")
                #DB에 한방매물번호 업데이트
                pyautogui.alert(f"등록된 한방매물번호는 '{매물번호}'입니다.") 
            # pyautogui.alert("정상등록확인") 
        except Exception as e:
            print("등록완료파트 에러:"+ str(e))
    
    driver.quit()
    # pyautogui.alert("확인필요")  
    

 
 
    

    

    # 한방번호 = ''
    # options = driver.find_elements(By.XPATH, '//*[@id="in_search_so"]/option')
    # if 한방번호 != '':
    #     print('한방번호가 존재할때')
    #     choice = '한방매물번호'
    #     value = ''
    # else:
    #     print('한방번호가 존재하지 않을 때')
    #     choice = '본번-부번'
    #     value = data['landData'][0]['land_jibun']
    # for opt in options:
    #     print(opt.text)
    #     if opt.text == choice: 
    #         opt.click()
    #         driver.find_element(By.XPATH, '//*[@id="in_keyword"]').send_keys(value)
    #         driver.find_element(By.XPATH, '//*[@id="mainSearchBtn"]').click()
    #         break
    # print("진행확인 전")        
    # # result = pyautogui.confirm('\n\n 매물등록을 진행하시겠습니까?', buttons=['예', '아니오'])   
    # result = pyautogui.alert(location_detail+'\n\n 매물등록을 진행합니다.\n\n원치 않으시면 창을 닫아주세요~')
    # result = '예' 
    # print("진행확인 후")
    # if result == '예':
    #     driver.get('https://mobile.karhanbang.com/kren/mamul/regist')
    #     # print("93")
    #     # # 로딩 완료를 기다리기 위한 암묵적 대기 설정
    #     # driver.implicitly_wait(10)
    #     print("95")
        

    #     # 매물종류 변경버튼 클릭
    #     WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#formAddress > div.top_basic_box > div.base_info_option > ul > li.bx.view.pt5 > div > a'))).click()
    #     print("obinfo_type: "+obinfo_type)
        
    #     if obinfo_type == '':
    #         pyautogui.alert("매물분류를 선택하셨습니까? 계속하려면 '확인'을 누르세요")   
    #     else:
    #         time.sleep(0.2)
    #         s_li_tags = driver.find_element(By.CLASS_NAME, 's_box_list').find_elements(By.TAG_NAME,"li") #각 element속에 li 태그들을 모두 찾기
    #         s_box_list_text(s_li_tags, obinfo_type)
    #     # li_tags = driver.find_element(By.CLASS_NAME, 's_box_list').find_elements(By.TAG_NAME,"li") #각 element속에 li 태그들을 모두 찾기
    #     # for li in li_tags:
    #     #     print(li.text)
    #     #     if li.text == '아파트':
    #     #         li.click()
    #     #         break
    #     # option = driver.find_element(By.XPATH, "//*[@id='in_gure_cd_name2'][text()='전세']")
    #     # driver.execute_script("arguments[0].scrollIntoView();", option) #현재 상태에서 스크롤을 진행하되, option값이 나올때 까지 스크롤을 하는 함수
    #     # option.click()



    #     #거래구분
    #     print("obinfo_ttype: "+obinfo_ttype)
    #     driver.find_element(By.XPATH, '//*[@id="formAddress"]/div[2]/div[2]/ul/li[2]/div/ul/li[1]/div/div/div').click()
    #     WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 's_box_list'))) #매물종류 레이어팝업창이 뜰때까지 대기
    #     # print(driver.find_element(By.CLASS_NAME, 's_box_list').is_displayed())
    #     s_li_tags = driver.find_element(By.CLASS_NAME, 's_box_list').find_elements(By.TAG_NAME,"li") #각 element속에 li 태그들을 모두 찾기
    #     s_box_list_text(s_li_tags, obinfo_ttype)

    #     #입주가능일
    #     driver.execute_script("selValues('Y','즉시입주','in_soon_move_yn')") #js코드로 selValues함수 실행
    #     # s_li_tags = driver.find_element(By.CLASS_NAME, 's_box_list').find_elements(By.TAG_NAME,"li") #각 element속에 li 태그들을 모두 찾기
    #     # s_box_list_text(s_li_tags, '즉시입주')

    #     #시도
    #     driver.find_element(By.XPATH, '//*[@id="in_sido_name"]').click()
    #     time.sleep(0.3)
    #     s_li_tags = driver.find_element(By.CLASS_NAME, 's_box_list').find_elements(By.TAG_NAME,"li") #각 element속에 li 태그들을 모두 찾기
    #     s_box_list_text(s_li_tags, location_do)
    #     #시군구
    #     driver.find_element(By.XPATH, '//*[@id="in_gugun_name"]').click()
    #     time.sleep(0.3)
    #     s_li_tags = driver.find_element(By.CLASS_NAME, 's_box_list').find_elements(By.TAG_NAME,"li") #각 element속에 li 태그들을 모두 찾기
    #     s_box_list_text(s_li_tags, location_si)
    #     #읍면동
    #     driver.find_element(By.XPATH, '//*[@id="in_dong_name"]').click()
    #     s_li_tags = driver.find_element(By.CLASS_NAME, 's_box_list').find_elements(By.TAG_NAME,"li") #각 element속에 li 태그들을 모두 찾기
    #     # print("s_li_tags: " , s_li_tags)
    #     s_box_list_text(s_li_tags, location_dong)
    #     #일반/산
    #     driver.find_element(By.XPATH, '//*[@id="in_san_cd_name"]').click()
    #     s_li_tags = driver.find_element(By.CLASS_NAME, 's_box_list').find_elements(By.TAG_NAME,"li") #각 element속에 li 태그들을 모두 찾기
    #     s_box_list_text(s_li_tags, land_type)
    #     #본번
    #     jibun_main = data['landData'][0]['land_jibun'].split('-')[0]
    #     driver.find_element(By.XPATH, '//*[@id="in_old_bon_no"]').send_keys(jibun_main)

    #     #부번
    #     if '-' in data['landData'][0]['land_jibun']:
    #         jibun_sub = data['landData'][0]['land_jibun'].split('-')[-1]
    #         driver.find_element(By.XPATH, '//*[@id="in_old_bu_no"]').send_keys(jibun_sub)

    #     if tr_target == '건물' or tr_target == '층호수' :
    #         # 건물명
    #         print("building_name: "+building_name)
    #         driver.find_element(By.XPATH, '//*[@id="in_bd_nm"]').send_keys(building_name)
            
    #         #회사명
    #         #건물위치
    #     #층
    #     if tr_target == '층호수':
    #         #호
    #         driver.find_element(By.XPATH, '//*[@id="in_ho_nm"]').send_keys(room_num)
            
    #         print(f"selValues('{basic_floor}','{basic_floor}','in_curr_floor')")
    #         driver.execute_script("openPopupCurrFloor()") #js코드로 openPopupCurrFloor 실행
    #         driver.execute_script(f"selValues('{basic_floor}','{basic_floor}','in_curr_floor')") #js코드로 selValues 실행

    #         # driver.find_element(By.XPATH, '//*[@id="in_curr_floor_name"]').click()
    #         # s_li_tags = driver.find_element(By.CLASS_NAME, 's_box_list').find_element(By.TAG_NAME, "in_curr_floor") #각 element속에 li 태그들을 모두 찾기
    #         # for li in s_li_tags:
    #         #     print(li)

    #         # s_box_list_value(s_li_tags, basic_floor)
    #         #총층
    #         driver.execute_script("openPopupTotalFloor()") #js코드로 openPopupTotalFloor 실행
    #         driver.execute_script(f"selValues({basic_totflr},{basic_totflr},'in_total_floor')") #js코드로 selValues 실행
    #         # driver.find_element(By.XPATH, '//*[@id="in_total_floor_name"]').click()
    #         # s_li_tags = driver.find_element(By.CLASS_NAME, 's_box_list').find_elements(By.TAG_NAME,"li") #각 element속에 li 태그들을 모두 찾기
    #         # s_box_list_value(s_li_tags, basic_totflr)

    # #가격정보
    #     #매매가
    #     print("obinfo_trading: "+obinfo_trading ,"obinfo_rent1: "+obinfo_rent1 ,"obinfo_deposit1: "+obinfo_deposit1)

    #     if obinfo_ttype == '매매':
    #         driver.find_element(By.XPATH, '//*[@id="in_amt_sell"]').send_keys(obinfo_trading)
    #         object_code = object_code_new
    #     else:
    #         object_code = obang_code
    #     # if driver.find_element(By.XPATH, '//*[@id="in_amt_sell"]').is_displayed() and obinfo_trading !='' : driver.find_element(By.XPATH, '//*[@id="in_amt_sell"]').send_keys(obinfo_trading) 
    #     if obinfo_ttype == '월세':
    #         #현월세금
    #         if driver.find_element(By.XPATH, '//*[@id="in_amt_month"]').is_displayed() and obinfo_rent1 !='' : driver.find_element(By.XPATH, '//*[@id="in_amt_month"]').send_keys(obinfo_rent1) 
    #     if obinfo_ttype == '월세' or obinfo_ttype == '전세':
    #         #현보증금
    #         if driver.find_element(By.XPATH, '//*[@id="in_amt_guar"]').is_displayed() and obinfo_deposit1 !='' : driver.find_element(By.XPATH, '//*[@id="in_amt_guar"]').send_keys(obinfo_deposit1) 
    #     #융자금
    #     driver.execute_script("openPopupLoanCode()")
    #     # driver.find_element(By.XPATH, '//*[@id="dialog_1683013148826"]/div/div/ul/li/div/ul/li[3]').click()
    #     driver.execute_script("selValues('2','30%이상(시세대비)','in_loanCode')")
        
    # #면적정보
    #     print("면적정보")
    #     if tr_target == '층호수':
    #         #공급면적 
    #         if basic_area2 == '' and basic_area1 != '' : basic_area2 = basic_area1
    #         if driver.find_element(By.XPATH, '//*[@id="in_gong_meter"]').is_displayed() and basic_area2 !='' : driver.find_element(By.XPATH, '//*[@id="in_gong_meter"]').send_keys(basic_area2) 
    #         #전용면적
    #         if driver.find_element(By.XPATH, '//*[@id="in_jun_meter"]').is_displayed() and basic_area1 !='' : driver.find_element(By.XPATH, '//*[@id="in_jun_meter"]').send_keys(basic_area1) 
    #     if tr_target == '건물':
    #         #건축면적
    #         driver.find_element(By.XPATH, '//*[@id="in_gun_meter"]').send_keys(building_archarea)
    #         #연면적
    #         driver.find_element(By.XPATH, '//*[@id="in_yun_meter"]').send_keys(building_totarea)
    #     if tr_target == '토지' or tr_target == '건물':
    #         #대지면적
    #         driver.find_element(By.XPATH, '//*[@id="in_toji_meter"]').send_keys(land_totarea)

    # #기타정보
    #     if tr_target != '토지':
    #         print("기타정보")
    #         #룸수
    #         #욕실수
    #         #승강기
    #         if int(building_elvcount) > 0:
    #             driver.execute_script("selValues('Y','유','in_elevator_yn')")
    #         elif int(building_elvcount) == 0:
    #             driver.execute_script("selValues('N','무','in_elevator_yn')")
            
        
    #         # #총주차
    #         # if building_pn != '' : driver.find_element(By.XPATH, '//*[@id="in_total_park_cnt"]').send_keys(building_pn)
    #         #가구당 주차
    #         if building_pn != '' : driver.find_element(By.XPATH, '//*[@id="in_total_park_cnt"]').send_keys(building_pn)
            
    #         #방향
    #         time.sleep(0.5)
    #         if tr_target == '건물' and building_direction != '': 
    #             print("건물방향: " + building_direction)
    #             driver.execute_script("openPopupDirectionCd()") #js코드로 openPopupDirectionCd 실행
    #             # driver.find_element(By.XPATH, f"//span[text()='{building_direction}']").click()  
    #             WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 's_box_list'))) 
    #             s_li_tags = driver.find_element(By.CLASS_NAME, 's_box_list').find_elements(By.TAG_NAME,"li") #각 element속에 li 태그들을 모두 찾기
    #             # print("s_li_tags: " , s_li_tags)
    #             s_box_list_text(s_li_tags, building_direction)
    #         elif tr_target == '층호수' and room_direction != '':
    #             #호실방향기준
    #             print("호실방향기준: " + direction_stn)
    #             if obinfo_type in ['상가점포','사무실']: 
    #                 direction_stn = '주출입문'
    #                 driver.find_element(By.XPATH, '//*[@id="in_direction_info"]').send_keys(direction_stn)
    #             else:
    #                 driver.execute_script("openPopupDirectionInfo()") #js코드로 openPopupDirectionInfo 실행
    #                 WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 's_box_list'))) 
    #                 s_li_tags = driver.find_element(By.CLASS_NAME, 's_box_list').find_elements(By.TAG_NAME,"li") 
    #                 s_box_list_text(s_li_tags, direction_stn)
    #             # print("호실방향기준: " + room_direction)
    #             driver.execute_script("openPopupDirectionCd()") #js코드로 openPopupDirectionCd 실행
    #             WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 's_box_list'))) 
    #             s_li_tags = driver.find_element(By.CLASS_NAME, 's_box_list').find_elements(By.TAG_NAME,"li") #각 element속에 li 태그들을 모두 찾기
    #             # print("s_li_tags: " , s_li_tags)
    #             s_box_list_text(s_li_tags, room_direction)
    #         #난방방식(초기값: 개별난방)
    #         driver.execute_script("openPopupWarmCd()") #js코드로 openPopupWarmCd 실행
    #         WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 's_box_list')))
    #         s_li_tags = driver.find_element(By.CLASS_NAME, 's_box_list').find_elements(By.TAG_NAME,"li")
    #         s_box_list_text(s_li_tags, '개별난방')
    #         #냉방방식(초기값: 개별냉방)
    #         driver.execute_script("openPopupColdCd()") #js코드로 openPopupColdCd 실행
    #         WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 's_box_list')))
    #         s_li_tags = driver.find_element(By.CLASS_NAME, 's_box_list').find_elements(By.TAG_NAME,"li")
    #         s_box_list_text(s_li_tags, '개별냉방')
    #         # #난방연료(초기값: 개별난방)
    #         # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 's_box_list')))
    #         # s_li_tags = driver.find_element(By.CLASS_NAME, 's_box_list').find_elements(By.TAG_NAME,"li")
    #         # s_box_list_text(s_li_tags, '개별난방')
    #         #건축물용도
    #         print("건축물용도: ", building_purpose)
    #         if building_purpose != '':
    #             driver.execute_script("openPopUpBuildCd()") #js코드로 openPopUpBuildCd 실행
    #             if building_purpose == '제1종근린생활시설': building_purpose = '제1종 근린생활시설'
    #             if building_purpose == '제2종근린생활시설': building_purpose = '제2종 근린생활시설'
    #             if building_purpose == '자동차관련시설': building_purpose = '자동차 관련 시설'
    #             if building_purpose == '자동차관련시설': building_purpose = '동물 및 식물 관련 시설'
    #             if building_purpose == '자동차관련시설': building_purpose = '자원순환 관련 시설'
    #             if building_purpose == '자동차관련시설': building_purpose = '교정(교정) 및 군사 시설'
    #             WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 's_box_list')))
    #             s_li_tags = driver.find_element(By.CLASS_NAME, 's_box_list').find_elements(By.TAG_NAME,"li")
    #             s_box_list_text(s_li_tags, building_purpose)

    #         #사용승인일 building_usedate 
    #         driver.execute_script("checkApprovalDayManual()") #js코드로 checkApprovalDayManual 실행
    #         WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="manual_approval_year"]')))
    #         usedate = building_usedate.split("-")

    #         # pyautogui.alert("사용승인일 차례")
            
    #         driver.find_element(By.XPATH, '//*[@id="manual_approval_year"]').send_keys(usedate[0])
    #         driver.find_element(By.XPATH, '//*[@id="manual_approval_month"]').send_keys(usedate[1])
    #         driver.find_element(By.XPATH, '//*[@id="manual_approval_day"]').send_keys(usedate[2])
    #         # WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="basic"]/div[11]/ul/li[12]/div/ul/li/div/div/div/div[1]/div/div/label[3]/span/span'))).click() 

    #         if basic_manager == '별도':
    #             #관리비항목
    #             driver.execute_script("openPopupmnexItem()") #js코드로 openPopupmnexItem 실행
    #             WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'option_list')))
    #             o_li_tags = driver.find_element(By.CLASS_NAME, 'option_list').find_elements(By.TAG_NAME,"li")
    #             for li in o_li_tags:
    #                 # print("li.text: ", li.text)
    #                 mlist =  basic_mlist.split(",")
    #                 for item in mlist:
    #                     if item == '개별수도': item = '수도'
    #                     if item == '유선': item = 'TV'
    #                     # print("item: ",item)
    #                     if item == li.text:
    #                         li.click()
    #             driver.execute_script("confirmMnixItem()") #선택완료버튼 클릭
    #             #비목
    #             driver.find_element(By.XPATH, '//*[@id="in_expenses_item_info"]').send_keys(basic_mmemo) 
    #         elif basic_manager == '없음': 
    #             basic_mmoney = 0
    #         elif basic_manager == '' or basic_manager == '미확인': 
    #             basic_mmoney = 9999999 # 관리비 미확인시 999원입력
    #             object_detail += Keys.ENTER + Keys.ENTER + '- 관리비 확인필요'
    #         # 관리비
    #         driver.find_element(By.XPATH, '//*[@id="in_managefee_info"]').send_keys(basic_mmoney)      
                      
    #         #옵션내역
    #         if obinfo_type not in ['아파트']: #옵션항목이 없는 리스트 설정
    #             driver.execute_script("openPopupOption()") #옵션선택 팝업창열기
    #             WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'option_list')))
    #             o_li_tags = driver.find_element(By.CLASS_NAME, 'option_list').find_elements(By.TAG_NAME,"li")
    #             for li in o_li_tags:
    #                 # print("li.text: ", li.text)
    #                 options =  tot_options.split(",")
    #                 for item in options:
    #                     # if item == '개별수도': item = '수도'
    #                     # if item == '유선': item = 'TV'
    #                     # print("item: ",item)
    #                     if item == li.text:
    #                         li.click()
    #             driver.execute_script("confirmOption()") #선택완료버튼 클릭 
    #     if tr_target == '토지':
    #         #지목 representing_jimok   
    #         jimok = f"({data['landData'][0]['representing_jimok'][0]}){data['landData'][0]['representing_jimok']}" 
    #         driver.find_element(By.XPATH, '//*[@id="in_jimok_cd_name"]').click()
    #         s_li_tags = driver.find_element(By.CLASS_NAME, 's_box_list').find_elements(By.TAG_NAME,"li") #각 element속에 li 태그들을 모두 찾기
    #         s_box_list_text(s_li_tags, jimok)   
    #         #용도지역  
    #         representing_purpose = data['landData'][0]['representing_purpose']
    #         if '주거' in representing_purpose or '상업' in representing_purpose or '공업' in representing_purpose or '녹지' in representing_purpose:
    #             purpose1 = '도시지역'
    #         elif '관리' in representing_purpose:
    #             purpose1 = '관리지역'
    #         elif '농림' in representing_purpose or '농업' in representing_purpose:
    #             purpose1 = '농림지역'
    #         elif '보전' in representing_purpose:
    #             purpose1 = '자연환경보전지역'
            
    #         driver.find_element(By.XPATH, '//*[@id="in_yong_jiyuk1_cd_name"]').click()
    #         s_li_tags = driver.find_element(By.CLASS_NAME, 's_box_list').find_elements(By.TAG_NAME,"li") #각 element속에 li 태그들을 모두 찾기
    #         s_box_list_text(s_li_tags, purpose1)  
    #         #용도지역2
    #         driver.find_element(By.XPATH, '//*[@id="in_yong_jiyuk2_cd_name"]').click()
    #         pyautogui.alert(f"용도지역: {data['landData'][0]['representing_purpose']} \n용도지역2 선택후 확인!!")
    #         # time.sleep(0.5)
    #         # #접한도로 //*[@id="in_road_meter_name"]
    #         # driver.find_element(By.XPATH, '//*[@id="in_road_meter_name"]').click()
    #         # pyautogui.alert(f"{data['landData'][0]['land_road']} 토지입니다. \n선택후 확인!!")
                   
    #     #매물특징
    #     driver.find_element(By.XPATH, '//*[@id="in_feature"]').send_keys()
    #     #매물설명
    #     detail = ''
    #     detail += Keys.ENTER + '고객님께서는 한방 사이트에서 등록된 매물[☞매물번호: ' + object_code + ']을 보고 계십니다.' + Keys.ENTER
    #     if object_detail != '':
    #         detail += Keys.ENTER + '[ 매물설명 ]' + Keys.ENTER
    #         # detail += Keys.ENTER + '📋상세정보'
    #         detail += object_detail + Keys.ENTER
    #     # detail += Keys.ENTER + f'↓↓↓ 오방{object_code} 매물 바로 보러가기 ↓↓↓'
    #     # detail += Keys.ENTER + f'https://osanbang.com/product/view/{object_code}'
    #     detail += Keys.ENTER + '관심있는 매물이라면 지금 바로 연락주세요~'
    #     detail += Keys.ENTER + ''
    #     detail += Keys.ENTER + '▣ 100% 직접보고 직접 찍은 실매물만을 제공합니다.'
    #     detail += Keys.ENTER + '▣ 365일 정상근무, 모시러 가는 서비스제공!!'
    #     detail += Keys.ENTER + '▣ 성실하게 정직하게 친절하게 안내해드리겠습니다.'
    #     detail += Keys.ENTER + '▣ 고객님의 소중한 재산을 최우선으로 생각합니다.'
    #     detail += Keys.ENTER + '▣지금보신 매물외에도 아직 등록되지 않은 매물들이 많이 있습니다.'
    #     detail += Keys.ENTER + '▣편하게 연락 주시고 홈페이지도 방문해보세요!!'
    #     detail += Keys.ENTER + '☎010-8631-4392 나상권공인중개사 '
    #     detail += Keys.ENTER + ''
    #     detail += Keys.ENTER + '※실시간 거래로 인하여 해당물건이 없을 수 있으니 방문전 반드시 문의바랍니다.'
    #     detail += Keys.ENTER + '※렌트프리, 옵션, 협의사항 등 끝까지 도와드리겠습니다.' + Keys.ENTER
    #     # detail += Keys.ENTER + '📌홈페이지: osanbang.com'
    #     detail += Keys.ENTER + '----------------------------------------------------------------------------' + Keys.ENTER
    #     # detail += Keys.ENTER + ''
    #     # detail += Keys.ENTER + ''
    #     # detail += Keys.ENTER + ''
    #     driver.find_element(By.XPATH, '//*[@id="in_memo"]').send_keys(detail)
    #     #비공개메모
    #     basic_secret = secret_1 + formatted_date+" "+admin_name+Keys.ENTER+"https://obangkr.cafe24.com/web/request/request_view/view_give_request_detail.php?request_code="+request_code
    #     driver.find_element(By.XPATH, '//*[@id="in_secret_memo"]').send_keys(basic_secret)
    #     # #사진 (미적용: 고난이도 작업ㅠ)
    #     # filePath = driver.find_element(By.XPATH, '//*[@id="product_form"]/div[1]/div[9]/div[2]/div[1]/div/div').get_attribute("outerHTML").split('<input id="')[1].split('" t')[0]
        
    #     # import os

    #     # try:
    #     #     main_dir = 'Z:\\업무자료\\4사진자료&이미지자료(외부유출금지)\\1주거용물건, 상업용물건\\'
    #     #     # path_dir = main_dir + data['folderPath'] #'경기도\\오산시\\궐동\\654-9\\썬플라워\\1층\\1층'
    #     #     # print(path_dir)
    #     #     path_dir = 'Z:\\업무자료\\4사진자료&이미지자료(외부유출금지)\\1주거용물건, 상업용물건\\경기도\\오산시\\궐동\\672-1\\신도빌딩\\3층\\301호 세븐당구클럽'
    #     #     try:
    #     #         file_list = os.listdir(path_dir)
    #     #         arr = []
    #     #         for filename in file_list:
    #     #             if "output" in filename: arr.append(filename.split('output')[1]) #output폴더들의 생성일을 arr에 담기

    #     #         if len(arr) == 0: #output폴더가 없다면
    #     #             arr2 = []
    #     #             for file in file_list: #원본사진을 arr2에 담기(원본사진은 있는지 확인)
    #     #                 if file.endswith('.jpeg') or file.endswith('.gif') or file.endswith('.png') or file.endswith('.jpg'):
    #     #                     arr2.append(file)
    #     #             if len(arr2) == 0: #원본사진도 없다면?
    #     #                 # driver.execute_script('return document.getElementById("is_speed").click()') #급매 체크
    #     #                 pass


    #     #         path = path_dir + "/output" + max(arr) #최근에 변환된 사진이 있는 폴더경로 설정

    #     #         photo_list = []

    #     #         for file in os.listdir(path):
    #     #             if file.endswith('.jpeg') or file.endswith('.gif') or file.endswith('.png') or file.endswith('.jpg'):
    #     #                 photo_list.append(file) #사진파일들만 photo_list에 추가

    #     #         for photo in photo_list:
    #     #             file_path = path + '/' + photo #사진파일의 전체경로 설정
    #     #             driver.find_element(By.ID, '#apdPicSwiper').send_keys(file_path)
    #     #             driver.execute_script("confirmOption()")
    #     #     except: 
    #     #         # driver.execute_script('return document.getElementById("is_speed").click()')
    #     #         print("사진 오류")
    #     #         pass
    #     # except:
    #     #     print("폴더 오류", data['folderPath'])
    #     #     # driver.execute_script('return document.getElementById("is_speed").click()')
    #     #     errarr.append("폴더 오류")
    #     #     pass

    #     #개인정보수집이용동의
    #     driver.execute_script('document.getElementById("checkAgree").checked = true') #동의 체크하기
    #     #물건사진 폴더열기
    #     원본사진들 = [] #원본사진파일들을 담을 빈 리스트
    #     변환폴더생성일모음 = [] #변환된 사진폴더의 년월일을 담을 빈 리스트    
    #     #물건의 원본사진폴더에 이미지가 존재하는지
    #     main_dir = 'Z:\\업무자료\\4사진자료&이미지자료(외부유출금지)\\1주거용물건, 상업용물건\\'
    #     path_dir = main_dir + data['folderPath'] #'경기도\\오산시\\궐동\\654-9\\썬플라워\\1층\\1층'
    #     print("path_dir:", path_dir)
        
    #     file_list = os.listdir(path_dir)   
    #     print("file_list:", file_list)

    #     for filename in file_list:
    #         # 파일 확장자를 소문자로 변환하여 비교
    #         if filename.lower().endswith(('.jpeg', '.gif', '.png', '.jpg')):
    #             원본사진들.append(filename)   
    #         if "output" in filename: 변환폴더생성일모음.append(filename.split('output')[1])  
    #     print("원본사진들:", 원본사진들) 
    #     #물건폴더에 원본사진 존재유무
    #     if len(원본사진들) > 0: #물건의 원본사진없음
    #         try:
    #             os.startfile(path_dir)
    #             print('폴더열기 성공') 
    #         except:
    #             print('폴더열기 에러(해당폴더 없음)')   
    #     else:
    #         print("원본사진X => 물건사진폴더 미개봉")    

    #     # time.sleep(120)
    #     pyautogui.alert("확인을 누르면 프로그램이 종료됩니다.") 

    #     # driver.close()
    #     driver.quit()
    #     return errarr

    #     #등록하기


    #     # try:
    #     #     driver.execute_script("checkApprovalDayManual()") #js코드로 checkApprovalDayManual 실행
    #     #     # time.sleep(5)
    #     #     # print(driver.find_element(By.XPATH, '//*[@id="basic"]/div[13]/ul/li[11]/div/ul/li/div/div/div/div[1]/div/div/label[3]'))
    #     #     # driver.find_element(By.XPATH, '//*[@id="basic"]/div[13]/ul/li[11]/div/ul/li/div/div/div/div[1]/div/div/label[3]').click()
    #     # except Exception as e:
    #     #     print("에러 발생:", str(e))
    # elif result == '아니오':
    #     # driver.close()
    #     driver.quit()
    #     return errarr
    
    

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
