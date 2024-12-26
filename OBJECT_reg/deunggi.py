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
import re

from selenium.common.exceptions import TimeoutException
import traceback

options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
        
def macro(data, user):
    
    driver = webdriver.Chrome(options=options)

    # URL 열기
    driver.maximize_window()
    driver.get('http://www.iros.go.kr/PMainJ.jsp')
    
    tr_target = data['writeData']['tr_target']
    
    location_lijibun = data['landData'][0]['representing_jibun'] if data['landData'][0]['land_li'] == '' else (data['landData'][0]['land_li'] + ' ' + data['landData'][0]['representing_jibun'])
    location_dongli = (data['landData'][0]['land_dong'] + data['landData'][0]['representing_jibun']) if data['landData'][0]['land_li'] == '' else location_lijibun
    
    if tr_target == '건물' or tr_target == '층호수':
        building_type = data['buildingData']['building_type']
        brtit_count = 0
        if data['brtitData'] and building_type == '집합':
            brtit_dongNm = data['brtitData']['brtit_dongNm']
            brtit_count = data['brtitData']['brtit_count']
        else:
            brtit_dongNm = ''
            # pyautogui.alert("건축데이터('brtit_dongNm')가 존재하지 않습니다.")
        location_dongNm = '' if brtit_dongNm == '' else ' ' + brtit_dongNm  
    if tr_target == '층호수':
        room_num = data['roomData']['room_num']
        location_room = '' if room_num == '' else ' ' + room_num
    # time.sleep(2)
    # 모든 윈도우 핸들을 가져온다.
    all_windows = driver.window_handles
    print("all_windows:",all_windows)
    # pyautogui.alert("확인?")
    # 메인 윈도우 핸들 저장 (첫 번째로 열린 윈도우)
    main_window_handle = driver.current_window_handle
    print("메인 윈도우 핸들:", main_window_handle)
    # 팝업 윈도우가 있을 경우, 메인 윈도우로 전환
    for handle in all_windows:
        if handle != main_window_handle:
            print("팝업 윈도우 핸들로 전환:", handle)
            # 팝업 윈도우로 전환
            driver.switch_to.window(handle)
            time.sleep(1)  # 윈도우 전환 후 잠시 대기
            
            try:
                # # 팝업 윈도우를 닫습니다.
                # driver.close()
                # print("팝업 윈도우 닫기")
                
                #오늘하루 이창을 열지 않음 체크
                # driver.find_element(By.XPATH, '/html/body/div[2]/div').click()  
                driver.execute_script("cookieset();")
                time.sleep(1)  # 윈도우 닫은 후 잠시 대기
            except Exception as e:
                print("팝업 윈도우 닫는 중 예외 발생:", e)

    # pyautogui.alert("윈도우개수:",len(all_windows))
    # 다시 메인 윈도우로 전환
    print("다시 메인 윈도우로 전환:", main_window_handle)
    driver.switch_to.window(main_window_handle)
    time.sleep(1)  # 윈도우 전환 후 잠시 대기

    # 이제 메인 윈도우에서 요소를 찾아 작업을 계속할 수 있습니다.
    # pyautogui.alert("확인?")
    try:
        # 로그인 정보 입력
        user_id_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "id_user_id"))
        )
        driver.execute_script("arguments[0].value='nsk98';", user_id_input)

        password_input = driver.find_element(By.ID, "password")
        driver.execute_script("arguments[0].value='dhqkd5555%';", password_input)
        # driver.find_element(By.XPATH, '//*[@id="id_user_id"]').send_keys("nsk98")
        # pyautogui.alert("확인?")
        # driver.find_element(By.XPATH, '//*[@id="password"]').send_keys("dhqkd5555%")
        # pyautogui.alert("확인?")
        # 로그인 버튼 클릭
        로그인버튼 = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="leftS"]/div[2]/form/div[1]/ul/li[4]'))
        )
        로그인버튼.click()
        
        #로그아웃버튼 표시확인
        로그아웃버튼 = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '#leftS > div:nth-child(2) > div.logout'))
        )
        if 로그아웃버튼.is_displayed():
            print('로그아웃버튼 보임')
        else:
            print('로그아웃버튼 안보임')  
        time.sleep(0.5)    
        # 열람/발급 클릭
        driver.find_element(By.XPATH, '//*[@id="cenS"]/div/ul/li[1]/div/ul/li[1]').click()
        # 현재 윈도우 핸들을 가져온다.
        current_window_handle = driver.current_window_handle
        print("현재 윈도우 핸들:", current_window_handle)
        # pyautogui.alert("열람/발급 확인?")

        
        # 아이프레임으로 전환
        driver.switch_to.frame("inputFrame")
        
        # 검색버튼 표시확인 #btnSrchSojae #line3 > td:nth-child(4)
        검색버튼 = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, '#btnSrchSojae'))
        )
        if 검색버튼.is_displayed():
            print('검색버튼 보임')
        else:
            print('검색버튼 안보임') 
                
        # 간편검색창에 소재지 입력
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "txt_simple_address"))
        )
        address_input = driver.find_element(By.ID, "txt_simple_address")
        address_value = '오산시 궐동 640-9'
        검색주소값 = location_dongli
        #집합건물이고 건물명이 "~동"으로 끝날 경우 건물명과 호수추가
        if tr_target == '건물' or tr_target == '층호수':
            print("location_dongli:"+location_dongli+", location_dongNm:"+location_dongNm)
            if building_type == '집합':
                검색주소값 = location_dongli + location_dongNm + location_room
            else:
                print("일반건물이지만 건물개수가 2개 이상일 경우")
                if tr_target != '토지' and brtit_count > 1:
                    검색주소값 = location_dongli + location_dongNm
        # 특수문자 제거: re.sub()를 사용하여 지정된 특수문자를 제거
        검색주소값 = re.sub(r"[?&()'\"%_]", "", 검색주소값)                
        driver.execute_script(f"arguments[0].value='{검색주소값}';", address_input)
        print("검색주소값:"+검색주소값+" 검색실행")
        # 검색버튼.click()
        address_input.send_keys(Keys.ENTER)
        # driver.execute_script("return f_search(this.form, 1, 0, 0);")
        # time.sleep(2)
        # 작업을 마친 후, 메인 컨텐츠로 다시 전환
        driver.switch_to.default_content()
        # time.sleep(5)

        pyautogui.alert("부동산과 소유자선택후 확인버튼 클릭시 자동으로 다음단계를 진행합니다.")
        try:
            # 최상위 아이프레임인 'resultFrame'으로 전환
            WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "resultFrame")))
            # driver.switch_to.frame("resultFrame")
            # print(driver.page_source)  # 현재 resultFrame DOM 구조 확인

            # 'resultFrame' 내부의 'frmOuterModal' 아이프레임으로 다시 전환
            WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "frmOuterModal")))
            # driver.switch_to.frame("frmOuterModal")
            # print(driver.page_source)  # 현재 frmOuterModal DOM 구조 확인

            try:
                WebDriverWait(driver, 20).until(
                    EC.invisibility_of_element_located((By.CLASS_NAME, "loading_area"))
                )
                # print("Loading area disappeared. DOM might be ready.")
            except Exception as e:
                print("Loading area still visible or error occurred:", e)
            #등기기록 유형선택(매매-말소사항포함, 임대-현재유효사항)
            object_ttype = '임대'
            if object_ttype == '임대':
                print("현재유효사항 선택")

                # "전부요소" 찾기
                try:
                    # iframe 전환 후 요소 대기
                    전부요소 = WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.ID, "dungbon_cls"))
                    )
                    # print("Found dungbon_cls element.")
                except Exception as e:
                    print("dungbon_cls element not found:", e)
                전부요소 = Select(전부요소)             
                # '현재유효사항'이라는 텍스트를 가진 옵션을 선택합니다.
                전부요소.select_by_visible_text("현재유효사항")  
                # pyautogui.alert("전부요소 '현재유효사항'선택")   
                print("현재유효사항 선택 완료")       
            else:
                print("말소사항포함 선택")
            
            # pyautogui.alert("등기기록 확인?")
            print("다음 버튼클릭")
            time.sleep(0.5) 
            driver.find_element(By.XPATH, '/html/body/div/form/div[4]/button').click()
            
            # pyautogui.alert("다음 확인?")
            print("등록번호공개여부검증 다음 버튼클릭")
            time.sleep(0.5) 
            driver.find_element(By.XPATH, '/html/body/div/form/div[5]/button').click()
            
            # pyautogui.alert("등록번호공개여부검증 확인?")
            # 'frmOuterModal' 아이프레임 내부에서 작업을 수행한 후,
            # 'resultFrame' 아이프레임으로 돌아가기 위해 parent_frame()을 사용합니다.
            driver.switch_to.parent_frame()
            print("결제대상부동산 결제 버튼클릭")
            time.sleep(0.5) 
            driver.find_element(By.XPATH, '/html/body/div/form[2]/div[1]/table/tbody/tr[3]/td[3]/button').click()
        except Exception as e:
            # print("등기기록유형 Error: " + str(e))
            print("등기기록유형 Error:")
            traceback.print_exc()        
            
        # 작업을 마친 후, 메인 컨텐츠로 다시 전환
        driver.switch_to.default_content()
        # pyautogui.alert("결제방법(선불전자지급수단) 선택단계에서 확인을 클릭하세요!!")
        
        print("결제방법(선불전자지급수단) 선택")
        선불전자지급수단 = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="mainTableId"]/div[4]/div/div/div/fieldset/ul/li/div[2]/label[3]'))
        )        
        time.sleep(0.5) 
        선불전자지급수단.click()
        
        # pyautogui.alert("결제방법 확인?")
        print("선불전자지급수단번호 입력")
        선불전자지급수단번호 = 'X5747511 0970'
        # 선불전자지급수단번호에서 앞 8자리를 추출하여 선불전자지급수단번호1에 저장
        선불전자지급수단번호1 = 선불전자지급수단번호[:8]
        # 선불전자지급수단번호에서 뒤 4자리를 추출하여 선불전자지급수단번호2에 저장
        선불전자지급수단번호2 = 선불전자지급수단번호[-4:]
        선불전자지급수단비번 = '3755555'
        선불_input1 = driver.find_element(By.ID, "inpEMoneyNo1")
        driver.execute_script(f"arguments[0].value='{선불전자지급수단번호1}';", 선불_input1)
        선불_input2 = driver.find_element(By.ID, "inpEMoneyNo2")
        driver.execute_script(f"arguments[0].value='{선불전자지급수단번호2}';", 선불_input2)
        선불_pw = driver.find_element(By.ID, "inpEMoneyPswd")
        driver.execute_script(f"arguments[0].value='{선불전자지급수단비번}';", 선불_pw)
        
        # pyautogui.alert("선불전자지급수단번호 확인?")
        print("전체동의 체크")
        time.sleep(0.5) 
        driver.find_element(By.XPATH, '//*[@id="chk_term_agree_all_emoney"]').click()
        
        # pyautogui.alert("전체동의 확인?")
        print("결제 버튼클릭")
        time.sleep(0.5) 
        driver.find_element(By.XPATH, '//*[@id="EMO"]/div[5]/button[1]').click()
        
        # pyautogui.alert("결제성공 확인창 표시상태에서 계속 진행?")
        # # 결제성공 확인창 닫기
        # driver.execute_script("return f_confirm();")
        # time.sleep(1) 
        # # 미열람/미발급 보기에서 첫번째 리스트 열람버튼 클릭
        # driver.execute_script("return f_MAWS_CheckVM_Sinchung( frmPayDoneList, '0', '1', '/frontservlet?cmd=RISUSubmitUnissuedListC', 'VW', 'ifraSubmitUnisu','','',0,0);")
        # time.sleep(1)
        # # 테스트열람하기 버튼클릭
        # driver.execute_script("javascript:f_goTestView(); return false;")
        # time.sleep(1)
        # # "RPRTRegisterXCtrl"메세지창에서 열기버튼 클릭
        # # 테스트열람이 정상실행되었다는 알림창 확인버튼 클릭
        # # 다시 첫번째 리스트 열람버튼 클릭
        # # "RPRTRegisterXCtrl"메세지창에서 열기버튼 클릭
        # # 열람화면에서 출력버튼 클릭

        # 저장위치 폴더 열기(거래대상이 '층호수'일 경우 일반건물이면 해당 건물위치를 열고 집합건물이면 '호실'위치를 연다.)

        
        
    except Exception as e:
        print(f"항목 선택 중 오류 발생: {e}")
    finally:
        pyautogui.alert("프로세스가 종료되었습니다.\n\n확인시 진행중인 창을 닫습니다.","[인터넷등기소]")
        driver.quit()
        pass