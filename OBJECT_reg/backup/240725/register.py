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
    tr_target = data['writeData']['tr_target']
    building_code = data['writeData']['building_code']
    
    building_road = data['buildingData']['building_road'].decode('utf-8')
    if tr_target == '건물' or tr_target == '층호수':
        building_type = data['buildingData']['building_type']
        brtit_dongNm = data['brtitData']['brtit_dongNm']
        location_dongNm = '' if brtit_dongNm == '' else ' ' + brtit_dongNm    
    if tr_target == '층호수':
        room_num = data['roomData']['room_num']
        location_room = '' if room_num == '' else ' ' + room_num        
    
    # pyautogui.alert(room_num)
    
    driver = webdriver.Chrome(options=options)

    # URL 열기
    driver.maximize_window()
    
    #로그인 페이지
    driver.get('https://www.eais.go.kr/moct/awp/abb01/AWPABB01F01')
    driver.find_element(By.XPATH, '//*[@id="membId"]').send_keys("nsk4392")
    driver.find_element(By.XPATH, '//*[@id="pwd"]').send_keys("dhqkd8726^")
    # pyautogui.alert("확인?")
    driver.find_element(By.XPATH, '//*[@id="container"]/div[2]/div/div/div[1]/div[1]/button').click()
    # pyautogui.alert("확인?")
    # driver.get('https://www.eais.go.kr/moct/bci/aaa02/BCIAAA02L01')
    # driver.implicitly_wait(10)
    
    time.sleep(0.3)
    if building_road:
        print("도로명주소:"+building_road)
    else:
        print("지번주소:")
    
    #건축물대장 발급페이지
    driver.get('https://www.eais.go.kr/moct/bci/aaa02/BCIAAA02L01')
    도로명주소로조회요소 = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="container"]/div[2]/div/div[2]/div[1]/div[1]/div[1]/div[2]/button[1]'))
    )
    if 도로명주소로조회요소:
        print('도로명주소로조회요소를 클릭.')  
        도로명주소로조회요소.click()
    else:
        print('도로명주소로조회요소를 클릭할 수 없습니다.')  
        pyautogui.alert("도로명주소가 없습니다. 관리자에게 문의하세요!!")
        driver.quit()    
    # pyautogui.alert("확인?")
    
    #도로명주소 입력
    print('도로명주소로 입력:'+building_road)
    if building_road == '':
        pyautogui.alert(f"건물정보({building_code})에 도로명주소 값이 없습니다. \n\n건물정도api를 업데이트 해보세요!!")
    else:
        # driver.find_element(By.XPATH, '//*[@id="keyword"]').send_keys(building_road)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="keyword"]'))).send_keys(building_road)
    # pyautogui.alert("확인?")
    
    #조회하기 버튼클릭
    driver.find_element(By.XPATH, '//*[@id="container"]/div[2]/div/div[2]/div[1]/div[1]/div[3]/div/div/button').click()
    # 조회된 검색결과 개수 확인
    addList = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.addrList ul li'))
    )
    # pyautogui.alert(f"검색 결과의 개수: {len(addList)}")  # 이 줄은 검색 결과의 개수를 출력합니다.
    if len(addList) == 1:
        선택버튼 = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '.addrList ul li button'))
        )
        선택버튼.click()
        print("검색 결과가 1개 있어서 해당 결과의 선택 버튼을 클릭했습니다.")
    else:
        print(f"검색 결과의 개수: {len(addList)}")
        첫번째항목_선택버튼 = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#container > div.content.clearFix > div > div.floatWarp.mt30.clearFix > div.contLeft > div.srchArchitecture > div.popAddrSearch > div > div.addrList > ul > li:nth-child(1) > button'))
        )
        첫번째항목_선택버튼.click()
    
    try:
        # 대장종류와 수 표시창: 목표하는 요소가 로드될 때까지 대기
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'complaintSelTab'))
        )
        # 창이 준비될 때까지 대기
        time.sleep(0.5)
        # pyautogui.alert("확인?")
        # 대장종류요소: 'complaintSelTab' 클래스를 가진 ul 요소 내의 모든 li 요소 찾기
        list_items = driver.find_elements(By.CSS_SELECTOR, '.complaintSelTab li')

        # 각 li 요소에서 원하는 정보 추출
        for item in list_items:
            #대장종류
            대장종류 = item.find_element(By.CSS_SELECTOR, 'a > p').text
            #대장별개수
            대장별개수 = item.find_element(By.CSS_SELECTOR, 'a > span > em').text
            print(f"{대장종류} {대장별개수}")
            #건물정보 선택
            if 대장별개수 == '1' and (대장종류 == '일반건축물' or 대장종류 == '다가구' or 대장종류 == '표제부'):
                print(대장종류+" 클릭합니다.")
                item.click()
                # pyautogui.alert("대장클릭후")
                time.sleep(0.2)
                centerContainer_all_divs = driver.find_elements(By.CSS_SELECTOR, 'div[ref="centerContainer"]')
                visible_divs = [div for div in centerContainer_all_divs if div.is_displayed()]
                print(f"건물개수는 {len(visible_divs)}개 입니다.")
                if len(visible_divs) == 1:
                    # visible_divs[0]에서 ref="eContainer" 속성을 가진 div 요소를 찾음
                    e_container = WebDriverWait(visible_divs[0], 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[ref="eContainer"]'))
                    )              
                    # 해당 요소 클릭
                    e_container.click()
                    time.sleep(0.2)
            else:
                print("집합건물일 경우 "+대장종류+" 클릭합니다.")
                item.click()
                time.sleep(0.2)
                centerContainer_all_divs = driver.find_elements(By.CSS_SELECTOR, 'div[ref="centerContainer"]')
                visible_divs = [div for div in centerContainer_all_divs if div.is_displayed()]
                print(f"건물개수는 {len(visible_divs)}개 입니다.")
                for visible_div in visible_divs:
                    if 대장종류 == '총괄표제부':
                        단지명칭파트들 = visible_div.find_elements(By.CSS_SELECTOR, 'div[col-id="bldNm"]') 
                        if len(단지명칭파트들) == 1:
                            단지명칭파트들[0].click()
                    elif 대장종류 == '표제부':  
                        # 동 이름이 있는 모든 div 요소 찾기
                        동명칭파트들 = visible_div.find_elements(By.CSS_SELECTOR, 'div[col-id="dongNm"]')   
                        print("brtit_dongNm:"+brtit_dongNm)                    
                        for 동명칭파트 in 동명칭파트들:
                            print(동명칭파트.text)   
                            if 동명칭파트.text == brtit_dongNm:
                                # print(f"{str(room_num_int)}호를 선택합니다.")
                                동명칭파트.click()   
                    elif int(대장별개수) > 0 and 대장종류 == '전유부':
                        print(대장종류+" 클릭합니다.")
                        item.click()
                        # pyautogui.alert("대장클릭후")
                        time.sleep(0.2)
                        room_num = data['roomData']['room_num']
                        for visible_div in visible_divs:
                            # 호실 이름이 있는 모든 div 요소 찾기
                            호명칭파트들 = visible_div.find_elements(By.CSS_SELECTOR, 'div[col-id="hoNm"]')
                            print("room_num:"+room_num)                    
                            for 호명칭파트 in 호명칭파트들:
                                print(호명칭파트.text+"호")
                                # 마지막 글자가 '호'인지 확인하고, 맞다면 '호'를 제거
                                if room_num.endswith("호"):
                                    room_num_int = room_num[:-1]  # 마지막 한 글자 제거
                                    # if room_num.isdigit():
                                    #     print(str(room_num)+"는 숫자입니다.")
                                    # else:
                                    #     print(str(room_num)+"는 문자입니다.")
                                    # if 호명칭파트.text == str(room_num_int):
                                    #     print("참 "+호명칭파트.text+" vs "+str(room_num_int))
                                    # else:
                                    #     print(호명칭파트.text+" vs "+str(room_num_int))
                                    if 호명칭파트.text == str(room_num_int) and room_num_int.isdigit():
                                        # print(f"{str(room_num_int)}호를 선택합니다.")
                                        호명칭파트.click()             
                        # pyautogui.alert("확인?")             
            pyautogui.alert(대장종류+" 파트 처리완료")    
                
        pyautogui.alert("확인?")            
        #신청할민원담기 클릭
        print("신청할민원담기 클릭")
        driver.find_element(By.XPATH, '//*[@id="complaintToltal"]/button').click()  
        time.sleep(0.5) #신청할 민원에 추가되는 시간
        #건축물대장발급신청 클릭
        print("건축물대장발급신청 클릭")
        driver.find_element(By.XPATH, '//*[@id="container"]/div[2]/div/div[2]/div[2]/button').click()   
        pyautogui.alert("신청준비가 완료되었습니다. 확인시 창이 닫힙니다.")
        
        # time.sleep(0.5)  
        # #신청하기버튼 클릭
        # print("신청하기버튼 클릭")
        # 신청하기버튼 = WebDriverWait(driver, 10).until(
        #     EC.visibility_of_element_located((By.CSS_SELECTOR, '#container > div.content > div > div.btns > button.btnNext.btnSolid.btnLarge.btn_blue'))
        # )
        # 신청하기버튼.click()
        # pyautogui.alert("신청완료되었습니다. 창을 닫습니다.")
        
        
    except Exception as e:
        print(f"항목 선택 중 오류 발생: {e}")
        pyautogui.alert(f"항목 선택 중 오류 발생: {e}")
    finally:
        driver.quit()