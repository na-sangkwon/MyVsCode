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
import tkinter as tk
from tkinter import messagebox
from datetime import datetime, date
import time
import os

options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
        
def macro(data, user):
    def 최상단알림창(message, title="알림"):
        root = tk.Tk()
        root.withdraw()  # 창 숨기기
        root.attributes("-topmost", True)  # 항상 위에 있도록 설정
        messagebox.showinfo(title, message)
        root.destroy()

    tr_target = data['writeData']['tr_target']

    building_code = data['writeData']['building_code']
    if tr_target == '건물' or tr_target == '층호수':
        building_road = data['buildingData']['building_road']
        building_type = data['buildingData']['building_type']
        building_totarea = data['buildingData']['building_totarea']
        if len(data['brtitData']) == 0:
            최상단알림창("건물api정보가 존재하지 않습니다. 프로그램을 종료합니다.")
            return
        brtit_dongNm = data['brtitData']['brtit_dongNm']
        location_dongNm = '' if brtit_dongNm == '' else ' ' + brtit_dongNm    
    if tr_target == '층호수':
        room_num = data['roomData']['room_num']
        room_area1 = data['roomData']['room_area1']
        location_room = '' if room_num == '' else ' ' + room_num        
    
    # pyautogui.alert(room_num)
    
    driver = webdriver.Chrome(options=options)

    # URL 열기
    driver.maximize_window()
    
    #로그인 페이지
    driver.get('https://www.eais.go.kr/moct/awp/abb01/AWPABB01F13')
    driver.find_element(By.XPATH, '//*[@id="membId"]').send_keys("nsk4392")
    driver.find_element(By.XPATH, '//*[@id="pwd"]').send_keys("dhqkd8726^")
    # pyautogui.alert("확인?")
    driver.find_element(By.XPATH, '//*[@id="container"]/div[2]/div/div/div/section[1]/button').click()
    # pyautogui.alert("확인?")
    # driver.get('https://www.eais.go.kr/moct/bci/aaa02/BCIAAA02L01')
    # driver.implicitly_wait(10)
    
    time.sleep(0.3)
    #건축물대장 발급페이지
    driver.get('https://www.eais.go.kr/moct/bci/aaa02/BCIAAA02L01')
    if tr_target == '토지':
        land_main = data['landData'][0]['land_main']
        main_jibun = data['landData'][0]['representing_jibun']
        if land_main and main_jibun:
            main_address = land_main+" "+main_jibun
            print("지번주소:"+main_address)
        pyautogui.alert("확인?")
    else:
        if building_road:
            print("도로명주소:"+building_road)
        else:
            print("지번주소:")
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
        전체대장종류 = driver.find_elements(By.CSS_SELECTOR, '.complaintSelTab li')
        건물선택안됨 = True   
        호실선택안됨 = True  
        # pyautogui.alert("확인? 대장종류 li개수: "+str(len(전체대장종류)))
        # 각 li 요소에서 원하는 정보 추출
        for 선택된대장종류 in 전체대장종류:
            #대장종류
            대장종류 = 선택된대장종류.find_element(By.CSS_SELECTOR, 'a > p').text
            #대장별개수
            대장별개수 = 선택된대장종류.find_element(By.CSS_SELECTOR, 'a > span > em').text
            print(f"{대장종류} {대장별개수}")
            #건물정보 선택
            if 대장별개수 == '1' and (대장종류 == '일반건축물' or 대장종류 == '다가구' or 대장종류 == '표제부'):
                print(대장종류+" 클릭합니다.")
                선택된대장종류.click()
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
                    건물선택안됨 = False
                    time.sleep(0.2)
            else:
                print("집합건물일 경우 "+대장종류+" 클릭합니다.")
                선택된대장종류.click()
                time.sleep(0.2)
                centerContainer_all_divs = driver.find_elements(By.CSS_SELECTOR, 'div[ref="centerContainer"]')
                visible_divs = [div for div in centerContainer_all_divs if div.is_displayed()]
                print(f"건물개수는 {len(visible_divs)}개 입니다.")
                for visible_div in visible_divs:
                    if 대장종류 == '총괄표제부':
                        단지명칭파트들 = visible_div.find_elements(By.CSS_SELECTOR, 'div[col-id="bldNm"]') 
                        if len(단지명칭파트들) == 1:
                            단지명칭파트들[0].click()
                    elif 대장종류 == '일반건축물' or 대장종류 == '표제부':  
                        building_name = data['buildingData']['building_name']
                        # 1) 쉼표로 분리하고 빈 문자열 제거
                        building_name_arr = [bn.strip() for bn in building_name.split(',') if bn.strip()]

                        # 2) brtit_dongNm이 포함된 요소가 하나라도 있으면
                        if any(brtit_dongNm in name for name in building_name_arr):
                            # 분리된 모든 요소를 조회대상건물들에 담고
                            조회대상건물들 = building_name_arr
                        else:
                            # 아니라면 원본 전체 문자열을 한 덩어리로 담는다
                            조회대상건물들 = [building_name]

                        # 동 이름이 있는 모든 div 요소 찾기
                        동명칭파트들 = visible_div.find_elements(By.CSS_SELECTOR, 'div[col-id="dongNm"]')   
                        print("brtit_dongNm:"+brtit_dongNm)    

                        for 동명칭파트 in 동명칭파트들:
                            print(동명칭파트.text)   
                            print("조회대상건물들:",조회대상건물들)   
                            for 조회대상건물 in 조회대상건물들:
                                if 동명칭파트.text in 조회대상건물:
                                    # 1) 동명칭파트의 부모(div.row 같은)로 올라간 뒤
                                    동명칭parent = 동명칭파트.find_element(By.XPATH, "./..")
                                    # 2) 그 안에서 col-id="0"인 셀(체크박스 영역) 선택
                                    해당동체크박스 = 동명칭parent.find_element(By.CSS_SELECTOR, 'div[col-id="0"]')
                                    print(f"{동명칭파트.text}호 체크박스 셀 클릭")
                                    해당동체크박스.click()
                                    건물선택안됨 = False
                        if 대장종류 == '표제부' and 건물선택안됨:
                            최상단알림창(building_name+" 연면적:"+building_totarea+"㎡"+"\n\n건물을 선택하시고 확인시 계속 진행합니다.")
                    elif int(대장별개수) > 0 and 대장종류 == '전유부':
                        print(대장종류+" 클릭합니다.")
                        선택된대장종류.click()
                        # pyautogui.alert("대장클릭후")
                        time.sleep(0.2)
                        room_num = data['roomData']['room_num']
                        # 1) 쉼표로 분리한 뒤 strip() 한 값 중 빈 값은 건너뛰고,
                        #    각 값이 '호'로 끝나면 마지막 글자('호')를 잘라낸 리스트 생성
                        room_nums = [
                            rn.strip()[:-1]           # '102호' -> '102'
                            for rn in room_num.split(',')
                            if rn.strip() and rn.strip().endswith('호')
                        ]   
                        print("room_nums:",room_nums)
                        # 1) 스크롤 가능한 컨테이너를 찾는다
                        scroll_container = driver.find_element(By.CSS_SELECTOR, '#container > div.content.clearFix > div > div.floatWarp.mt30.clearFix > div.contLeft > div.mt20.clearFix > div > div:nth-child(5) > table > tbody > div > div > div.ag-root-wrapper-body.ag-layout-normal.ag-focus-managed > div.ag-root.ag-unselectable.ag-layout-normal > div.ag-body-viewport.ag-layout-normal.ag-row-no-animation') 
                        # 이미 선택된 호실을 추적하기 위한 집합
                        selected_rooms = set()
                        total_rooms_to_find = len(room_nums)
                        found_rooms_count = 0

                        # 이미 처리된 모든 호실 텍스트를 저장할 집합
                        all_processed_room_texts = set()

                        # 스크롤 시도 횟수
                        max_scroll_attempts = 50 # 충분히 시도할 수 있도록 넉넉하게 설정
                        scroll_attempt = 0

                        while found_rooms_count < total_rooms_to_find and scroll_attempt < max_scroll_attempts:
                            scroll_attempt += 1

                            # 현재 보이는 모든 행(div) 요소들을 다시 가져온다
                            visible_rows = scroll_container.find_elements(By.CSS_SELECTOR, '.ag-row[role="row"]')
                            current_scroll_room_texts = set() # 현재 스크롤 위치에서 보이는 호실 텍스트들

                            for row in visible_rows:
                                try:
                                    ho_num_element = row.find_element(By.CSS_SELECTOR, 'div[col-id="hoNm"]')
                                    ho_num_text = ho_num_element.text.strip()[:-1] if ho_num_element.text.strip() and ho_num_element.text.strip().endswith('호') else ho_num_element.text.strip()
                                    current_scroll_room_texts.add(ho_num_text) # 현재 보이는 호실 추가
                                    print("ho_num_text:",ho_num_text)
                                    # print("current_scroll_room_texts:",current_scroll_room_texts)
                                    # 아직 선택되지 않았고, room_nums에 포함된 호실인 경우
                                    if ho_num_text in room_nums and ho_num_text not in selected_rooms:
                                        checkbox_cell = row.find_element(By.CSS_SELECTOR, 'div[col-id="0"]')
                                        print(f"'{ho_num_text}'호 체크박스 셀 클릭")
                                        checkbox_cell.click()
                                        selected_rooms.add(ho_num_text) # 선택된 호실 집합에 추가
                                        found_rooms_count += 1
                                        time.sleep(0.1) # 클릭 후 약간의 대기

                                except Exception as e:
                                    # print(f"호실 정보 처리 중 오류 발생: {e}") # 디버깅용
                                    continue
                            # pyautogui.alert("확인?")
                            # 모든 대상 호실을 찾았으면 루프 종료
                            if found_rooms_count == total_rooms_to_find:
                                print("모든 호실을 찾고 선택했습니다.")
                                break

                            # 새로운 호실이 로드되었는지 확인
                            # 현재 스크롤에서 새로 발견된 호실이 이전에 처리된 호실 집합에 없으면 새로운 데이터가 로드된 것임
                            # 또는, `current_scroll_room_texts`에 새롭게 추가된 호실이 있는지 확인
                            
                            # ⭐️ 중요한 변경: 새로 로드된 행이 있는지 확인하는 로직
                            # 현재 화면에 보이는 모든 호실 중, `all_processed_room_texts`에 없는 호실이 있다면
                            # 새로운 데이터가 로드된 것으로 간주할 수 있습니다.
                            new_data_loaded = False
                            for ho_text in current_scroll_room_texts:
                                if ho_text not in all_processed_room_texts:
                                    new_data_loaded = True
                                    break
                                    
                            # 현재 보이는 모든 호실 텍스트를 `all_processed_room_texts`에 추가
                            all_processed_room_texts.update(current_scroll_room_texts)

                            # 새로운 데이터가 로드되지 않았고, 아직 모든 호실을 찾지 못했다면,
                            # 더 이상 스크롤해도 새로운 데이터가 없을 가능성이 높음
                            if not new_data_loaded and found_rooms_count < total_rooms_to_find:
                                print("새로운 호실 정보가 로드되지 않아 스크롤을 중단합니다.")
                                break
                                
                            # 다음 스크롤을 위해 약간 아래로 내린다 (현재 스크롤 위치에서 500픽셀 내리기 예시)
                            # 스크롤 바가 고정되어 있더라도 JavaScript로 스크롤 위치를 조작하여
                            # 내부 데이터 로드를 트리거하는 경우가 있을 수 있습니다.
                            driver.execute_script("arguments[0].scrollTop += 1000;", scroll_container)
                            time.sleep(0.5)

                        # 스크롤 루프 종료 후 최종 확인
                        if found_rooms_count < total_rooms_to_find:
                            remaining_rooms = [room for room in room_nums if room not in selected_rooms]
                            print(f"경고: 다음 호실들을 찾지 못했습니다: {', '.join(remaining_rooms)}")
                            if 대장종류 == '전유부':
                                missing_room_info = ""
                                for r_num in remaining_rooms:
                                    missing_room_info += f"{r_num}호\n"
                                pyautogui.alert(f"다음 호실들을 찾지 못했습니다:\n\n{missing_room_info}\n건물을 선택하시고 확인시 계속 진행합니다.")
                        else:
                            print("모든 호실 선택 완료!")                                        
                        
                        # # 2) 스크롤을 반복해서 끝까지 내린다
                        # last_height = driver.execute_script("return arguments[0].scrollHeight", scroll_container)
                        # while True:
                        #     driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_container)
                        #     time.sleep(0.5)  # 로딩을 약간 기다려 줘야 새로운 행이 렌더링됩니다.
                        #     new_height = driver.execute_script("return arguments[0].scrollHeight", scroll_container)
                        #     if new_height == last_height:
                        #         break
                        #     last_height = new_height                        
                        # pyautogui.alert("로딩완료?")        
                        # for visible_div in visible_divs:
                        #     # 호실 이름이 있는 모든 div 요소 찾기
                        #     호명칭파트들 = visible_div.find_elements(By.CSS_SELECTOR, 'div[col-id="hoNm"]')
                        #     print("room_num:"+room_num)                    
                        #     for 호명칭파트 in 호명칭파트들:
                        #         print(호명칭파트.text+"호")
                        #         # 화면에 보이는 텍스트(예: '102')가 room_nums 리스트에 있으면 클릭
                        #         if 호명칭파트.text in room_nums:
                        #             # 1) 호명칭파트의 부모(div.row 같은)로 올라간 뒤
                        #             호명칭parent = 호명칭파트.find_element(By.XPATH, "./..")
                        #             # 2) 그 안에서 col-id="0"인 셀(체크박스 영역) 선택
                        #             해당호체크박스 = 호명칭parent.find_element(By.CSS_SELECTOR, 'div[col-id="0"]')
                        #             print(f"{호명칭파트.text}호 체크박스 셀 클릭")
                        #             해당호체크박스.click()   
                        #             호실선택안됨 = False
                        #             # print(f"{호명칭파트.text}호 클릭!")                                 
                        #             # 호명칭파트.click()   
                        #             # pyautogui.alert("확인?")            
                        # if 대장종류 == '전유부' and 호실선택안됨:
                        #     최상단알림창(room_num+" 전용면적:"+room_area1+"㎡"+"\n\n건물을 선택하시고 확인시 계속 진행합니다.")
                        # # pyautogui.alert("확인?")     
        
            # pyautogui.alert(대장종류+" 파트 처리완료")    
                
        # pyautogui.alert("신청할민원담기 확인?")            
        #신청할민원담기 클릭
        print("신청할민원담기 클릭")
        driver.find_element(By.XPATH, '//*[@id="complaintToltal"]/button').click()  
        time.sleep(0.5) #신청할 민원에 추가되는 시간
        #건축물대장발급신청 클릭
        최상단알림창("건축물대장발급 목록을 확인해주세요\n\n 이대로 신청하시겠습니까?")     
        print("건축물대장발급신청 클릭")
        driver.find_element(By.XPATH, '//*[@id="container"]/div[2]/div/div[2]/div[2]/button').click()   
        
        time.sleep(0.5)  
        #신청하기버튼 클릭
        print("신청하기버튼 클릭")
        신청하기버튼 = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '#container > div.content > div > div.btns > button.btnNext.btnSolid.btnLarge.btn_blue'))
        )
        신청하기버튼.click()
        # pyautogui.alert("신청완료되었습니다. 창을 닫습니다.")
        최상단알림창("발급이 완료되었습니다. 확인시 창이 닫힙니다.")
        
        
    except Exception as e:
        print(f"항목 선택 중 오류 발생: {e}")
        pyautogui.alert(f"항목 선택 중 오류 발생: {e}")
    finally:
        driver.quit()