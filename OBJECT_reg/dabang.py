from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
import pyautogui 
import time
import pyperclip
import pymysql
from datetime import timedelta
from datetime import datetime, date

import os
import sys
# 🚀 상위 폴더의 패키지를 인식할 수 있도록 시스템 경로(sys.path)에 추가하는 마법의 코드
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# 이제 공용 함수를 내 파일 안에 있는 것처럼 자유롭게 불러옵니다!
from util.property_utils import 건축법상건축물용도로변환

options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

def 최상단알림창(message, title="알림"):
    """
    크롬 전체화면 뒤로 팝업창이 숨는 현상을 방지하는 윈도우 레벨 최상단 고정 알림창입니다.
    """
    import tkinter as tk
    from tkinter import messagebox
    
    root = tk.Tk()
    root.withdraw()                     # 배경이 되는 빈 메인 윈도우 창 숨김
    root.attributes("-topmost", True)   # 화면 가장 앞쪽 레이어로 강제 고정
    messagebox.showinfo(title, message) # 알림창 팝업 실행
    root.destroy()                      # [확인] 클릭 시 메모리 청소 및 닫기
    
def 알림창건너뛰기(driver):
    try:
        WebDriverWait(driver, 3).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        print(f"⚠️ 다방 경고창 감지: {alert.text}")
        alert.accept()  
        print("✅ 다방 경고창 자동 승인 완료")
        time.sleep(0.5)
    except:
        print("알림 창 없음 (바로 통과)")    

def macro(data, user):
    # ChromeDriver 가동 및 초기화
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => false})")
    driver.maximize_window()
    
    # 1. 다방프로 중개사 로그인 페이지 접속
    driver.get('https://pro.dabangapp.com/login')
    
    dabang_id = data['adminData'].get('dabang_id', '')
    dabang_pw = data['adminData'].get('dabang_pw', '')
    
    if not dabang_id or not dabang_pw:
        pyautogui.alert("DB에 다방 아이디 또는 비밀번호 정보가 없습니다.")
        driver.quit()
        return

    try:
        # 2. 로그인 처리
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@name='email']"))
        )
        email_input.send_keys(Keys.CONTROL + 'a')
        email_input.send_keys(Keys.DELETE)
        email_input.send_keys(dabang_id)
        
        pw_input = driver.find_element(By.XPATH, "//input[@name='password']")
        pw_input.send_keys(Keys.CONTROL + 'a')
        pw_input.send_keys(Keys.DELETE)
        pw_input.send_keys(dabang_pw)
        time.sleep(0.1)
        
        driver.find_element(By.XPATH, "//button[@type='submit' and .//span[text()='로그인']]").click()
        print("✅ 다방프로 로그인 버튼 클릭 완료")
        
        # 💡 [신규 추가] 대시보드 진입 후 공지/이벤트 팝업 자동 차단 로직
        time.sleep(2.0)  # 대시보드 화면 및 가끔 뜨는 공지 팝업이 완전히 로드될 때까지 대기
        print("▶ 대시보드 공지 팝업 존재 여부 확인 중...")
        try:
            # 1순위: '오늘 하루 보지 않기' 텍스트 버튼이 뜨는지 최대 3초만 대기 후 클릭
            notice_close_btn = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@id='modal-container']//button[text()='오늘 하루 보지 않기']"))
            )
            notice_close_btn.click()
            print("✅ 공지 팝업 '[오늘 하루 보지 않기]' 클릭 완료 (내일 전까지 차단)")
            time.sleep(0.5)
        except:
            # 2순위: 만약 텍스트 버튼 인식에 실패했다면 상단의 'X' 아이콘 버튼으로 예외 시도
            try:
                x_btn = driver.find_element(By.XPATH, "//div[@id='modal-container']//button[.//svg]")
                x_btn.click()
                print("✅ 공지 팝업 'X' 아이콘 버튼으로 닫기 완료")
                time.sleep(0.5)
            except:
                # 팝업이 아예 안 뜨는 평소 상황에는 에러 없이 자연스럽게 패스합니다.
                print("알림: 현재 화면에 대시보드 공지 팝업이 없습니다. (정상 패스)")
        
        # 3. 대시보드 진입 후 매물등록 버튼 클릭
        register_btn = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div[2]/div/div[2]/button'))
        )
        register_btn.click()
        
        # 양식 페이지 로드 대기
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "room_info")))
        time.sleep(1)

        # ------------------------------------------------------------------
        # 💡 [데이터 파싱 및 변환 변수 설정 - 스코프 에러 원천 차단]
        # ------------------------------------------------------------------
        write_data = data.get('writeData', {})
        land_data = data.get('landData', [{}])[0]
        room_data = data.get('roomData', {})
        building_data = data.get('buildingData', {})
        
        object_code_new = write_data.get('object_code_new', '')
        request_main = write_data.get('request_main', '')
        object_type1 = write_data.get('object_type1', '')    # '원룸/오피'
        object_type2 = write_data.get('object_type2', '')    # '일반원룸'
        building_purpose = building_data.get('building_purpose', '다가구주택') 
        building_option = building_data.get('building_option', '') # 변수 최상단 고정
        
        # 주소 정보
        address_base = write_data.get('address', '')  
        land_main = land_data.get('land_main', '')     
        room_num = room_data.get('room_num', '')              
        brtit_dongNm = data.get('brtitData', {}).get('brtit_dongNm', '').strip() if data.get('brtitData') else ''
        
        # 면적 예외 처리
        room_area1 = room_data.get('room_area1', '')
        if not room_area1 or room_area1 == '':
            room_area1 = '20' if room_data.get('room_rcount', '1') == '1' else '30'
            
        # ---------------------------------------------------------
        # 1. 매물유형 대분류 & 소분류 선택
        # ---------------------------------------------------------
        print(f"▶ 1단계: 매물 유형 선택 object_type1:{object_type1}, object_type2:{object_type2}")
        if '원룸' in object_type2 or '주택' in object_type1:
            driver.find_element(By.XPATH, "//button[.//span[text()='주택 / 빌라']]").click()
            
            알림창건너뛰기(driver)
            # try:
            #     WebDriverWait(driver, 3).until(EC.alert_is_present())
            #     alert = driver.switch_to.alert
            #     print(f"⚠️ 다방 경고창 감지: {alert.text}")
            #     alert.accept()  
            #     print("✅ 다방 경고창 자동 승인 완료")
            #     time.sleep(0.5)
            # except:
            #     print("알림 창 없음 (바로 통과)")

            sub_type = '다가구주택' if '다가구' in building_purpose else '단독주택'
            driver.find_element(By.XPATH, f"//label[.//p[text()='{sub_type}']]/input[@type='radio']").click()

        elif object_type1 == '오피스텔':
            driver.find_element(By.XPATH, "//button[.//span[text()='오피스텔']]").click()
            
        elif '아파트' in object_type1 or '아파트' in object_type2:
            driver.find_element(By.XPATH, "//button[.//span[text()='아파트(도시형)']]").click()
            
        if '미등기' in building_data.get('building_important', ''):
            driver.find_element(By.XPATH, "//label[.//p[contains(text(), '미등기건물')]]/input[@type='checkbox']").click()

        time.sleep(0.5)
        
        알림창건너뛰기(driver)
        # try:
        #     WebDriverWait(driver, 3).until(EC.alert_is_present())
        #     alert = driver.switch_to.alert
        #     print(f"⚠️ 다방 경고창 감지: {alert.text}")
        #     alert.accept()  
        #     print("✅ 다방 경고창 자동 승인 완료")
        #     time.sleep(0.5)
        # except:
        #     print("알림 창 없음 (바로 통과)")

        # ------------------------------------------------------------------
        # 2. 매물 주소 검색 및 제어 (일반 주택 vs 아파트 단지 조회 분기)
        # ------------------------------------------------------------------
        is_apartment = '아파트' in object_type1 or '아파트' in object_type2

        if is_apartment:
            print("▶ 2단계: 아파트 단지 및 동/호수 입력 (새로운 단지형 구조)")
            try:
                # 💡 DB 주소 문자열 파싱 (예: "경기도 오산시 갈곶동 181-8번지" -> ['경기도', '오산시', '갈곶동', ...])
                addr_parts = land_main.split()
                city_part = addr_parts[0] if len(addr_parts) > 0 else ""
                gu_part = addr_parts[1] if len(addr_parts) > 1 else ""
                dong_part = addr_parts[2] if len(addr_parts) > 2 else ""
                
                # 1. 시/도 선택 (예: 경기도)
                city_select = Select(driver.find_element(By.XPATH, "//select[@name='city']"))
                city_select.select_by_visible_text(city_part)
                time.sleep(0.5)
                
                # 2. 시/군/구 선택 (락 해제 활성화 대기 후 오산시 선택)
                gu_elem = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//select[@name='gu']"))
                )
                Select(gu_elem).select_by_visible_text(gu_part)
                time.sleep(0.5)
                
                # 3. 동/읍/면 선택 (락 해제 활성화 대기 후 갈곶동 선택)
                dong_elem = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//select[@name='dong']"))
                )
                Select(dong_elem).select_by_visible_text(dong_part)
                time.sleep(0.5)
                
                # 4. 단지검색어 주입 및 입력
                search_input = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='단지검색']"))
                )
                
                # DB 건물명 또는 매물명 추출
                bld_name = building_data.get('building_name', '').strip()
                if not bld_name:
                    bld_name = write_data.get('object_name', '').strip()
                    
                search_input.send_keys(bld_name)
                search_input.send_keys(Keys.ENTER)
                time.sleep(1.0)
                
                # 🎯 [신규 기능] 검색된 단지 리스트 개수 판별 및 자동 선택 로직
                # 다방의 검색 결과 레이아웃 내 목록 요소들을 멀티 타겟팅 구조로 수집
                result_elements = driver.find_elements(By.XPATH, "//div[@id='complex-search-list']//ul/li")
                
                if len(result_elements) == 1:
                    result_elements[0].click()
                    print(f"✅ 검색된 아파트 단지가 1개이므로 자동으로 선택 완료: {bld_name}")
                    time.sleep(1.0) # 단지 선택 후 동/호수 인풋창의 disabled(비활성화)가 풀릴 때까지 대기
                elif len(result_elements) > 1:
                    print(f"⚠️ 검색된 아파트 단지가 {len(result_elements)}개임 - 사용자 수동 선택 대기")
                    pyautogui.alert(f"아파트 단지 검색 결과가 여러 개 존재합니다.\n\n화면에서 정확한 단지를 '마우스로 직접 클릭'하신 후 이 확인 창을 눌러주세요.")
                else:
                    print("⚠️ 검색 결과 요소를 판별하지 못함 - 안전장치 가동")
                    pyautogui.alert(f"아파트 단지 검색창에 [{bld_name}]이(가) 입력되었습니다.\n\n화면의 검색 결과 목록에서 정확한 단지를 '마우스로 직접 클릭'하신 후 이 확인 창을 눌러주세요.")
                
                # 5. 아파트 동(Dong) 입력
                if not brtit_dongNm or brtit_dongNm == '':
                    driver.find_element(By.XPATH, "//label[.//p[contains(text(), '동’ 정보가 없을 경우')]]/input").click()
                else:
                    dong_input = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//input[@name='dong' and @placeholder='예) 101']"))
                    )
                    dong_input.send_keys(Keys.CONTROL + 'a')
                    dong_input.send_keys(Keys.DELETE)
                    dong_input.send_keys(brtit_dongNm.replace('동',''))
                    
                # 6. 아파트 호(Ho) 입력
                if room_num:
                    ho_input = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//input[@name='ho' and @placeholder='예) 101']"))
                    )
                    ho_input.send_keys(Keys.CONTROL + 'a')
                    ho_input.send_keys(Keys.DELETE)
                    ho_input.send_keys(room_num.replace('호',''))
                    print("✅ 아파트 단지 및 동/호수 매핑 자동화 완료")
                    time.sleep(1.0)
                    
            except Exception as apt_addr_e:
                print("⚠️ 아파트 주소 입력 중 예외 발생:", str(apt_addr_e))
                pyautogui.alert("아파트 주소/단지/동/호수를 화면에서 수동으로 선택 및 입력하신 후 확인을 눌러주세요.")

        else:
            # 💡 [기존 구조] 일반 주택 / 빌라 / 오피스텔용 카카오 우편번호 및 대장 팝업 제어 로직
            keyword_input = driver.find_element(By.XPATH, "//input[@name='keyword']")
            keyword_input.send_keys(address_base)
            driver.find_element(By.XPATH, "//button[.//span[text()='검색']]").click()
            time.sleep(1.5) 
            
            main_handle = driver.current_window_handle
            all_handles = driver.window_handles
            
            if len(all_handles) > 1:
                driver.switch_to.window(all_handles[-1])
                print("-> 카카오 주소 팝업창으로 제어권 전환")
                try: driver.switch_to.frame(0)
                except: pass
            else:
                print("-> 본문 내 iframe 제어 시도")
                try:
                    kakao_frame = driver.find_element(By.XPATH, "//iframe[contains(@src, 'postcode') or contains(@id, 'daum')]")
                    driver.switch_to.frame(kakao_frame)
                except:
                    try: driver.switch_to.frame(0)
                    except: print("⚠️ 카카오 iframe을 포착하지 못했습니다.")

            try:
                kakao_address_xpaths = [
                    "/html/body/div[1]/div/div[2]/ul/li/dl/dd[2]/span/button[1]/span[1]",
                    "/html/body/div[1]/div/div[2]/ul/li/dl/dd[2]/span/button[1]",
                    "//ul[@class='list_post']//button",
                    "//div[@class='res_list']//a"
                ]
                
                addr_clicked = False
                for path in kakao_address_xpaths:
                    try:
                        addr_btn = WebDriverWait(driver, 3).until(
                            EC.element_to_be_clickable((By.XPATH, path))
                        )
                        addr_btn.click()
                        print("✅ 카카오 첫 번째 주소지 자동 선택 완료")
                        addr_clicked = True
                        break
                    except: continue
                    
                if not addr_clicked:
                    raise Exception("적합한 카카오 주소 클릭 요소를 찾을 수 없음")
                    
            except Exception as addr_e:
                print(f"⚠️ 주소 자동 선택 실패 ({addr_e}) -> 수동 안전장치 가동")
                pyautogui.alert("카카오 우편번호 검색창에서 원하는 주소를 '마우스로 직접 클릭'하신 후 확인을 눌러주세요.")
                
            driver.switch_to.default_content()
            if len(driver.window_handles) > 1:
                driver.switch_to.window(main_handle)
                
            print("▶ 레이어 팝업: 건축물대장 정보 조회 대기")
            try:
                ledger_confirm_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='네, 조회할게요']]"))
                )
                ledger_confirm_btn.click()
                print("✅ '네, 조회할게요' rejection 버튼 자동 클릭 완료")
                time.sleep(2.0) 
                
                print("▶ 레이어 팝업: 건축물대장 정보 확인 단계 진입")
                try:
                    bld_select_elem = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, "(//div[@id='modal-container']//select)[1]"))
                    )
                    bld_select = Select(bld_select_elem)
                    bld_options = bld_select.options  
                    valid_bld_count = len(bld_options) - 1
                    
                    if valid_bld_count == 1:
                        bld_select.select_by_index(1) 
                        print("✅ 검색된 건물이 1개이므로 자동 선택 완료")
                    elif valid_bld_count >= 2:
                        pyautogui.alert("건물이 2개 이상 검색되었습니다.\n\n화면에서 올바른 건물을 마우스로 직접 선택하신 후 확인을 눌러주세요.")
                    
                    flr_select_elem = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, "(//div[@id='modal-container']//select)[2]"))
                    )
                    flr_select = Select(flr_select_elem)
                    
                    db_floor = str(room_data.get('room_floor', '')).strip() 
                    target_floor_text = f"{db_floor}층" 
                    
                    flr_selected = False
                    for op in flr_select.options:
                        if op.text.strip() == target_floor_text or op.text.strip() == db_floor:
                            flr_select.select_by_visible_text(op.text)
                            print(f"✅ DB 층수({db_floor})에 일치하는 '{op.text}' 자동 선택 완료")
                            flr_selected = True
                            break
                    if not flr_selected:
                        for op in flr_select.options:
                            if op.text.strip() == '전체':
                                flr_select.select_by_visible_text('전체')
                                print("✅ DB 층수가 대장 옵션에 없어 '전체' 항목으로 자동 대체 선택 완료")
                                flr_selected = True
                                break
                    if not flr_selected and len(flr_select.options) > 1:
                        last_op_text = flr_select.options[-1].text
                        flr_select.select_by_index(len(flr_select.options) - 1)
                        print(f"✅ 대장에 일치하는 층이 없어 가장 높은 층수 항목('{last_op_text}')으로 자동 대체 선택 완료")
                        flr_selected = True
                    
                    time.sleep(0.5)
                    
                    search_submit_btn = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, "//div[@id='modal-container']//button[.//span[text()='조회하기']]"))
                    )
                    driver.execute_script("arguments[0].click();", search_submit_btn)
                    print("✅ '조회하기' 버튼 자동 클릭 완료")
                    time.sleep(1.5) 
                    
                    print("▶ 레이어 팝업: 대장 정보 최종 적용 단계 진입")
                    try:
                        apply_btn = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, "//div[@id='modal-container']//button[.//span[text()='적용하기']]"))
                        )
                        driver.execute_script("arguments[0].click();", apply_btn)
                        print("✅ '적용하기' 버튼 자동 클릭 완료 (본문 폼에 대장 정보 연동)")
                        time.sleep(2.0) 
                    except Exception as apply_e:
                        pyautogui.alert("면적 확인 팝업에서 [적용하기] 버튼을 마우스로 직접 누르신 뒤 확인을 눌러주세요.")
                    
                except Exception as pop_e:
                    pyautogui.alert(request_main+"\n\n건축물대장 팝업 자동 처리에 실패했습니다.\n\n화면의 팝업창에서 건물 및 층 선택 후 [조회하기] -> [적용하기]까지 직접 완료하신 후에 확인 창을 눌러주세요.")
            except Exception as modal_e:
                print("알림: 건축물대장 조회 팝업창이 뜨지 않았거나 클릭에 실패했습니다. (패스)", str(modal_e))
                
            if not brtit_dongNm or brtit_dongNm == '':
                driver.find_element(By.XPATH, "//label[.//p[contains(text(), '동’ 정보가 없을 경우')]]/input[@type='checkbox']").click()
            else:
                dong_input = driver.find_element(By.XPATH, "//input[@name='dong']")
                dong_input.send_keys(brtit_dongNm.replace('동',''))
                
            if room_num:
                ho_input = driver.find_element(By.XPATH, "//input[@name='ho']")
                ho_input.send_keys(room_num.replace('호',''))

        # ------------------------------------------------------------------
        # 3. 매물 크기 입력 (일반 타이핑 vs 아파트 평형 선택 분기 완벽 해결)
        # ------------------------------------------------------------------
        print("▶ 3단계: 매물 크기 입력")
        if is_apartment:
            try:
                # 아파트 전용 평형 선택 드롭다운 요소 대기 및 객체화
                size_select_elem = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//select[@name='complexSpaceSeq']"))
                )
                size_select = Select(size_select_elem)
                
                # DB 면적 데이터 추출
                area1 = str(room_data.get('room_area1', '')).strip() # 전용면적 '19.51'
                area2 = str(room_data.get('room_area2', '')).strip() # 공급면적 '31.3566'
                
                # 매칭 정확도를 올리기 위한 소수점 2자리 포맷팅 정제
                try:
                    area1_fixed = f"{float(area1):.2f}" # '19.51'
                except:
                    area1_fixed = area1
                
                # 다방 특유의 소수점 아래 버림 처리 대응 (앞 5자리 '31.35'만 슬라이싱)
                area2_short = area2[:5] if len(area2) > 5 else area2 
                
                matched = False
                
                # 🎯 [1순위 매칭] 소수점이 정확한 전용면적(19.51)이 옵션 텍스트에 포함되어 있는지 검사
                for op in size_select.options:
                    if area1_fixed in op.text:
                        size_select.select_by_visible_text(op.text)
                        print(f"✅ 아파트 평형 자동 선택 완료 (전용면적 {area1_fixed}㎡ 기준): {op.text}")
                        matched = True
                        break
                        
                # 🎯 [2순위 매칭] 1순위 실패 시 소수점 버림 처리된 공급면적 앞자리(31.35)로 매칭
                if not matched and area2_short:
                    for op in size_select.options:
                        if area2_short in op.text:
                            size_select.select_by_visible_text(op.text)
                            print(f"✅ 아파트 평형 자동 선택 완료 (공급면적 {area2_short}㎡ 기준): {op.text}")
                            matched = True
                            break
                
                # 🎯 [3순위 매칭] 규격 외 데이터일 경우 안전하게 수동 선택 유도
                if not matched:
                    print("⚠️ DB 면적과 일치하는 아파트 평형 옵션을 찾지 못했습니다. - 수동 대기")
                    pyautogui.alert(f"DB 면적(전용: {area1} / 공급: {area2})과 일치하는 평형 항목이 드롭다운에 없습니다.\n\n화면에서 올바른 평형을 직접 마우스로 선택하신 후 확인을 눌러주세요.")
                    
                time.sleep(0.5)
                
            except Exception as size_e:
                print("⚠️ 아파트 평형 선택 중 예외 발생:", str(size_e))
                pyautogui.alert("아파트 평형 선택창을 제어하지 못했습니다.\n\n화면에서 평형을 직접 선택하신 후 확인을 눌러주세요.")
        else:
            # 💡 [기존 구조] 일반 주택 / 빌라 / 오피스텔용 면적 직접 타이핑 구조
            size_input = driver.find_element(By.XPATH, "(//input[@name='room'])[2]") 
            size_input.send_keys(Keys.CONTROL + 'a')
            size_input.send_keys(Keys.DELETE)
            size_input.send_keys(str(room_area1))
            print(f"✅ 일반 매물 전용면적 입력 완료: {room_area1}㎡")

        # ---------------------------------------------------------
        # 4. 방 정보 입력 및 방 특징 조건별 자동 체크 (호실특약 필드 반영)
        # ---------------------------------------------------------
        print("▶ 4단계: 방 수 및 형태")
        rcount_raw = room_data.get('room_rcount', '1')
        try:
            rcount_fixed = str(int(float(rcount_raw)))
        except:
            rcount_fixed = '1'
            
        rcount_input = driver.find_element(By.XPATH, "//div[contains(@class, 's3Pack__group') and .//h1[text()='방 수']]//input")
        rcount_input.send_keys(Keys.CONTROL + 'a')
        rcount_input.send_keys(Keys.DELETE)
        rcount_input.send_keys(rcount_fixed)  
        
        room_important = room_data.get('room_important', '')
        r_shape = '오픈형' if '오픈형' in room_important else '분리형'
        driver.find_element(By.XPATH, f"//label[.//p[text()='{r_shape}']]/input[@type='radio']").click()
        time.sleep(0.2)

        # 방 특징 조건별 매핑 자동화
        try:
            dabang_room_features = []
            
            # 🎯 [수정] 호실특약(room_terms) 필드에서 '애완동물가능(호실)' 여부 검사
            room_terms = room_data.get('room_terms', '')
            if '애완동물가능(호실)' in str(room_terms):
                dabang_room_features.append("반려동물")
                
            # 조건 2: 사용승인일이 현재(2026년) 기준 3년 이내인 경우 -> 신축
            b_usedate = building_data.get('building_usedate', '')
            if b_usedate and b_usedate != '0000-00-00':
                try:
                    usedate_year = int(b_usedate.split('-')[0]) 
                    if 2026 - usedate_year <= 3:  
                        dabang_room_features.append("text" if False else "신축")
                except: pass
                
            # 조건 3: 토지특징 중 '중로접' 또는 '광대로접'이 포함된 경우 -> 큰길가
            land_important = land_data.get('land_important', '')
            if '중로접' in land_important or '광대로접' in land_important:
                dabang_room_features.append("큰길가")
                
            print(f"-> 파싱된 방 특징 목록: {dabang_room_features}")
            
            # 수집된 매물 특징 순회하며 다방 화면 체크박스 자동 매핑
            for feature in dabang_room_features:
                try:
                    feat_label = driver.find_element(By.XPATH, f"//div[contains(@class, 's3Pack__group') and .//h1[contains(text(), '방 특징')]]//label[.//p[text()='{feature}']]")
                    feat_input = feat_label.find_element(By.TAG_NAME, "input")
                    
                    if not feat_input.is_selected():
                        feat_label.click()
                        time.sleep(0.1)
                except Exception as fe:
                    print(f"⚠️ 방 특징 [{feature}] 체크 실패:", str(fe))
                    
            print("✅ 방 특징 조건별 자동 선택 완료")
            
        except Exception as room_feat_e:
            print("⚠️ 방 특징 자동화 블록 실행 중 오류 발생:", str(room_feat_e))

        # ------------------------------------------------------------------
        # 5. [거래 정보] 섹션 자동 입력 (sell, lease1, lease2, lease3 완벽 대응)
        # ------------------------------------------------------------------
        print("▶ 7단계: 거래 종류 및 가격 정보")
        first_trade = write_data.get('first_trade', '').strip()
        
        trade_type = '전세' # 기본 매칭값 초기화
        deposit_val = ''
        rent_val = '0'
        
        # 💡 [보완] first_trade 접미사 숫자를 파싱하여 해당하는 금액 컬럼을 동적으로 조준
        if first_trade == 'sell':
            trade_type = '매매'
            deposit_val = write_data.get('trading', '')
        elif first_trade in ['lease1', 'lease2', 'lease3']:
            # 'lease1' -> '1', 'lease3' -> '3' 숫지만 추출
            suffix = first_trade.replace('lease', '') 
            
            # f-string을 이용해 deposit1, deposit2, deposit3 등을 동적으로 매핑
            deposit_val = write_data.get(f'deposit{suffix}', '')
            rent_val = write_data.get(f'rent{suffix}', '0')
            
            try:
                # 해당 차수의 월세 값이 0보다 크면 '월세', 없거나 0이면 '전세'
                if float(rent_val) > 0:
                    trade_type = '월세'
                else:
                    trade_type = '전세'
            except:
                trade_type = '전세'
        
        # 판별된 거래 종류 라디오 버튼 클릭
        driver.find_element(By.XPATH, f"//label[.//p[text()='{trade_type}']]/input[@type='radio']").click()
        time.sleep(0.5) # 레이아웃 전환 대기
        
        # 금액 최종 주입
        if trade_type == '매매':
            deposit_input = driver.find_element(By.XPATH, "//input[@name='deposit']")
            deposit_input.send_keys(Keys.CONTROL + 'a')
            deposit_input.send_keys(Keys.DELETE)
            deposit_input.send_keys(str(deposit_val))
            print(f"✅ 매매 선택 및 매매가 입력 완료: {deposit_val}만원")
            
        elif trade_type in ['전세', '월세']:
            deposit_input = driver.find_element(By.XPATH, "//input[@name='deposit']")
            deposit_input.send_keys(Keys.CONTROL + 'a')
            deposit_input.send_keys(Keys.DELETE)
            deposit_input.send_keys(str(deposit_val))
            print(f"✅ {trade_type} 선택 및 보증금(전세가) 입력 완료: {deposit_val}만원 (출처: deposit{suffix})")
            
            # 월세 조건일 때 일치하는 차수의 월세 금액 추가 주입
            if trade_type == '월세':
                try:
                    rent_input = driver.find_element(By.XPATH, "//input[@name='price'] | //div[contains(@class, 's3Pack__group') and .//h1[text()='월세']]//input")
                    rent_input.send_keys(Keys.CONTROL + 'a')
                    rent_input.send_keys(Keys.DELETE)
                    rent_input.send_keys(str(rent_val))
                    print(f"✅ 월세 금액 입력 완료: {rent_val}만원 (출처: rent{suffix})")
                except Exception as rent_err:
                    print(f"⚠️ 월세 입력창 탐색 실패: {rent_err}")
        
        loan_select = Select(driver.find_element(By.XPATH, "//select[./option[text()='시세대비30% 이상']]"))
        loan_select.select_by_value("NOT_EXIST") 
        
        manager_select = Select(driver.find_element(By.XPATH, "//select[./option[text()='있음']]"))
        manager_select.select_by_value("true") 
        time.sleep(1.0) 
        
        print("▶ 레이어 팝업: 월 관리비 상세입력 진입")
        try:
            # 기존 기본값 '8'을 지우고, None이나 공백 처리 대비 안전하게 스트링 변환
            mmoney_raw = str(write_data.get('mmoney') or '').strip() 

            # DB에 값이 없거나(빈 문자열), 0인 경우 처리
            if not mmoney_raw or mmoney_raw in ['0', '0.0']:
                mmoney_val = 0
                fee_amount = 100  # 💡 값이 없는 경우 100원으로 강제 설정
            else:
                mmoney_val = float(mmoney_raw)             
                fee_amount = int(mmoney_val * 10000)    
            
            fee_input = None 
            
            if mmoney_val >= 10:
                print(f"-> 관리비 {mmoney_raw}만원 (10만원 이상 조건 처리)")
                driver.find_element(By.XPATH, "//div[@id='modal-container']//label[./p[text()='10만원 이상 (세부내역 미고지)']]/input").click()
                time.sleep(0.3)
                
                type_select = Select(driver.find_element(By.XPATH, "//div[@id='modal-container']//select"))
                type_select.select_by_value("E98")
                time.sleep(0.2)
                
                fee_input = driver.find_element(By.XPATH, "//div[@id='modal-container']//li[./div[contains(@class, 'th')]/h1[contains(text(), '관리비')]]//input")
            else:
                print(f"-> 관리비 {mmoney_raw}만원 (10만원 미만 조건 처리)")
                driver.find_element(By.XPATH, "//div[@id='modal-container']//label[./p[text()='10만원 미만']]/input").click()
                time.sleep(0.3)
                
                fee_input = driver.find_element(By.XPATH, "//div[@id='modal-container']//input[@name='detailCost']")
            
            if fee_input:
                fee_input.send_keys(Keys.CONTROL + 'a')
                fee_input.send_keys(Keys.DELETE)
                fee_input.send_keys(str(fee_amount))
                print(f"✅ 관리비 금액 입력 완료: {fee_amount}원")
            else:
                raise Exception("적절한 관리비 입력창을 탐색하지 못했습니다.")
            
            mlist = write_data.get('mlist', '')
            print(f"-> DB 관리비 포함 내역 파싱: {mlist}")
            
            dabang_checkboxes = ['기타 관리비']
            if '일반관리' in mlist or '건물청소' in mlist:
                dabang_checkboxes.append("공용 관리비")
            if '개별전기' in mlist:
                dabang_checkboxes.append("전기")
            if '개별수도' in mlist:
                dabang_checkboxes.append("수도")
            if '개별가스' in mlist:
                dabang_checkboxes.append("가스")
            # if '난방' in mlist:
            #     dabang_checkboxes.append("난방")
            if '인터넷' in mlist:
                dabang_checkboxes.append("인터넷")
            if '유선' in mlist or 'TV' in mlist:
                dabang_checkboxes.append("TV")
                
            # if not dabang_checkboxes:
            #     dabang_checkboxes.append("기타 관리비")
                
            for item in dabang_checkboxes:
                try:
                    chk_label = driver.find_element(By.XPATH, f"//div[@id='modal-container']//label[./p[text()='{item}']]")
                    chk_input = chk_label.find_element(By.TAG_NAME, "input")
                    if not chk_input.is_selected():
                        chk_label.click()
                        time.sleep(0.1)
                except Exception as e:
                    print(f"⚠️ 포함 항목 [{item}] 체크 실패:", str(e))
            
            print("✅ 포함 항목 체크박스 매핑 완료")
            time.sleep(0.3)
            
            popup_confirm_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@id='modal-container']//button[./span[text()='확인']]"))
            )
            popup_confirm_btn.click()
            print("✅ 관리비 상세입력 팝업 [확인] 클릭 완료 (창 닫힘)")
            time.sleep(1.2) 

            if fee_amount <= 100: 알림창건너뛰기(driver)
            
        except Exception as pop_e:
            pyautogui.alert(f"관리비 상세입력 팝업 처리 중 문제가 발생했습니다.\n{pop_e}")
            
        print("▶ 8단계: 입주 가능 일자")
        driver.find_element(By.XPATH, "//label[.//p[text()='즉시 입주']]/input[@type='radio']").click()

        # ------------------------------------------------------------------
        # 6. [추가 정보] 섹션 자동 입력 (XPath 문법 오류 완벽 수정)
        # ------------------------------------------------------------------
        print("▶ 9단계: 층수 / 방향 / 주차 등 추가정보")
        b_grnd = str(building_data.get('building_grndflr', '3')).strip()
        r_floor = str(room_data.get('room_floor', '4')).strip()
        
        if int(r_floor) > int(b_grnd):
            print(f"-> 건물 지상층({b_grnd}층)보다 호실 층수({r_floor}층)가 높아 전체 층수를 {r_floor}층으로 보정합니다.")
            b_grnd = r_floor

        try:
            # 1. 전체 층 수 정밀 선택
            total_flr_elem = driver.find_element(By.XPATH, "//div[contains(@class, 's3Pack__group') and .//h1[contains(text(), '전체 층 수')]]//select")
            Select(total_flr_elem).select_by_value(b_grnd)
            time.sleep(0.5)
            
            # 2. 해당 층 수 정밀 선택
            my_flr_elem = driver.find_element(By.XPATH, "//div[contains(@class, 's3Pack__group') and .//h1[contains(text(), '해당 층 수')]]//select")
            my_flr_select = Select(my_flr_elem)
            try:
                my_flr_select.select_by_value(r_floor)
            except:
                try: my_flr_select.select_by_visible_text(f"{r_floor}층")
                except: pass
            time.sleep(0.2)
            
            # 3. 방향 기준 및 방향 선택
            r_direction = room_data.get('direction_stn', '').strip()  
            room_direction = room_data.get('room_direction', '').strip()  
            
            if not r_direction or r_direction == '': r_direction = '안방'
            if not room_direction or room_direction == '': room_direction = '남'
            
            dir_base_map = {'안방': 'MAIN_ROOM', '거실': 'LIVING_ROOM'}
            dir_map = {
                '동': 'EAST', '서': 'WEST', '남': 'SOUTH', '북': 'NORTH',
                '북동': 'NORTH_EAST', '북서': 'NORTH_WEST', '남동': 'SOUTH_EAST', '남서': 'SOUTH_WEST'
            }
            clean_dir = room_direction.replace('향', '').strip() 
            
            dir_base_val = dir_base_map.get(r_direction, 'MAIN_ROOM')
            dir_val = dir_map.get(clean_dir, 'SOUTH')
            
            dir_base_select = Select(driver.find_element(By.XPATH, "(//tr[.//h1[contains(text(), '방향')]]//select)[1]"))
            dir_base_select.select_by_value(dir_base_val)
            time.sleep(0.3)
            
            dir_select = Select(driver.find_element(By.XPATH, "(//tr[.//h1[contains(text(), '방향')]]//select)[2]"))
            dir_select.select_by_value(dir_val)
            print(f"✅ 방향 설정 완료 -> 기준: {r_direction}, 방향: {room_direction}향")
            
            # 4. 🎯 [문법 오류 수정] 욕실 수 입력
            bath_input = driver.find_element(By.XPATH, "//tr[.//h1[contains(text(), '욕실 수')]]//input")
            bath_input.send_keys(Keys.CONTROL + 'a')
            bath_input.send_keys(Keys.DELETE)
            bath_input.send_keys(room_data.get('room_bcount', '1'))
            print("✅ 욕실 수 입력 완료")
            
            # 5. 엘리베이터 선택
            elv_choice = '있음' if '엘리베이터' in building_option else '없음'
            driver.find_element(By.XPATH, f"//tr[.//h1[contains(text(), '엘리베이터')]]//label[.//p[text()='{elv_choice}']]/input").click()
            print(f"✅ 엘리베이터 옵션 선택 완료: {elv_choice}")
            
            # 6. 🎯 [문법 오류 수정] 주차 가능 여부 선택 및 주차대수 입력 (React 세터 작동)
            parking_select = Select(driver.find_element(By.XPATH, "//tr[.//h1[contains(text(), '주차 가능 여부')]]//select"))
            parking_select.select_by_value("true") 
            time.sleep(0.5) 
            
            parking_count_input = driver.find_element(By.XPATH, "//input[@placeholder='총 가능 주차수']")
            building_pn = building_data.get('building_pn', '4')
            
            react_force_setter = """
            var input = arguments[0];
            var value = arguments[1];
            input.disabled = false;
            var setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
            if (setter) {
                setter.call(input, value);
            } else {
                input.value = value;
            }
            input.dispatchEvent(new Event('input', { bubbles: true }));
            input.dispatchEvent(new Event('change', { bubbles: true }));
            """
            driver.execute_script(react_force_setter, parking_count_input, str(building_pn))
            print(f"✅ 주차대수 입력 완료: {building_pn}대")
            
            # 7. 복층 여부 (단층 고정)
            driver.find_element(By.XPATH, "//tr[.//h1[contains(text(), '복층 여부')]]//label[.//p[text()='단층']]/input").click()
            
            # 8. 세대(가구수) 입력
            fmly_input = driver.find_element(By.XPATH, "//tr[.//h1[contains(text(), '세대(가구수)')]]//input")
            fmly_input.send_keys(Keys.CONTROL + 'a')
            fmly_input.send_keys(Keys.DELETE)
            fmly_input.send_keys(str(building_data.get('building_fmly', '19')))

        except Exception as section_e:
            print("⚠️ 9단계 추가정보 섹션 처리 중 예외 발생:", str(section_e))

        # ------------------------------------------------------------------
        # 7. [시설 정보] 및 [상세 설명] 자동화
        # ------------------------------------------------------------------
        print("▶ 10단계: 시설 정보 및 옵션 매핑")
        try:
            driver.find_element(By.XPATH, "//label[.//p[text()='개별난방']]/input[@type='radio']").click()
            
            # 💡 [보안 시설 매핑] 공동현관보안 처리
            if '공동현관보안' in building_option:
                try:
                    sec_label = driver.find_element(By.XPATH, "//section[@id='facility_info']//label[.//p[text()='현관보안']]")
                    if not sec_label.find_element(By.TAG_NAME, "input").is_selected():
                        sec_label.click()
                        print("✅ 보안시설 [현관보안] 자동 체크 완료")
                except: pass

            # 💡 [보안 시설 추가 매핑] 건물옵션에 '건물CCTV'가 있는 경우 'CCTV' 체크박스 클릭
            if '건물CCTV' in building_option:
                try:
                    cctv_label = driver.find_element(By.XPATH, "//section[@id='facility_info']//label[.//p[text()='CCTV']]")
                    if not cctv_label.find_element(By.TAG_NAME, "input").is_selected():
                        cctv_label.click()
                        print("✅ 보안시설 [CCTV] 자동 체크 완료")
                except: pass

            # 💡 [생활 시설 매핑] 호실옵션 매핑 확장 ('옷장' 포함)
            room_options = room_data.get('room_option', '')
            option_list = ['세탁기', '냉장고', 'TV', '신발장', '싱크대', '가스레인지', '인덕션', '전자레인지', '붙박이장', '옷장']
            for opt in option_list:
                if opt in room_options or (opt == '가스레인지' and '가스렌지' in room_options):
                    try:
                        opt_label = driver.find_element(By.XPATH, f"//section[@id='facility_info']//label[.//p[text()='{opt}']]")
                        if not opt_label.find_element(By.TAG_NAME, "input").is_selected():
                            opt_label.click()
                    except: pass
                    
            if '냉방기' in room_options:
                driver.find_element(By.XPATH, "//label[.//p[text()='벽걸이형']]/input[@type='checkbox']").click()
            print("✅ 생활/냉방/보안 시설 옵션 체크 완료")

        except Exception as facility_e:
            print("⚠️ 시설 정보 처리 중 예외 발생:", str(facility_e))

        # ------------------------------------------------------------------
        # 8. 상세 설명 및 제목 주입
        # ------------------------------------------------------------------
        print("▶ 11단계: 상세 설명 주입")
        try:
            rcount_raw = room_data.get('room_rcount', '1')
            try: rcount_fixed = str(int(float(rcount_raw)))
            except: rcount_fixed = '1'

            title_text = f"★리모델링 완료된 깔끔한 갈곶동 원룸 전세, 보증보험 가입완료"
            title_input = driver.find_element(By.XPATH, "//input[contains(@placeholder, '리스트에 노출되는 문구')]")
            title_input.send_keys(title_text)
            
            description = (
                f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"  오산 원·투룸 전문 [ 나상권공인중개사사무소 ]\n"
                f"  대표번호 : 031-375-5555\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"□ 물건관리번호 : {object_code_new}\n"
                f"□ 방 구조 : 방 {rcount_fixed}개 / 욕실 1개\n"
                f"□ 주요특징 : 리모델링 완료되어 내부 아주 깨끗합니다.\n"
                f"□ 보안/안전 : {write_data.get('tr_memo', '')}\n"
                f"□ 기타안내 : {building_data.get('building_memo', '')}\n\n"
                f"원하시는 조건에 맞춰 최선을 다해 중개해 드리겠습니다. 편하게 문의주세요!"
            )
            
            desc_textarea = driver.find_element(By.XPATH, "//textarea[contains(@placeholder, '매물 상세 페이지에 노출되는 문구')]")
            desc_textarea.click()
            driver.execute_script("arguments[0].value = arguments[1];", desc_textarea, description)
            desc_textarea.send_keys(" ")
            desc_textarea.send_keys(Keys.BACK_SPACE)
            
            secret_memo = f"새홈[{object_code_new}] 의뢰번호:{data['writeData']['request_code']} / 비밀번호:{room_data.get('room_gate2', '')}"
            secret_textarea = driver.find_element(By.XPATH, "//textarea[contains(@placeholder, '해당 내용은 외부에 공개되지 않으며')]")
            driver.execute_script("arguments[0].value = arguments[1];", secret_textarea, secret_memo)

            main_dir = 'Z:\\업무자료\\4사진자료&이미지자료(외부유출금지)\\1주거용물건, 상업용물건\\'
            path_dir = main_dir + data['folderPath']
            try:
                os.startfile(path_dir)
                pyperclip.copy(path_dir)
            except: pass

            # 사진 등록용 폴더 및 마감 안내
            main_dir = 'Z:\\업무자료\\4사진자료&이미지자료(외부유출금지)\\1주거용물건, 상업용물건\\'
            path_dir = main_dir + data['folderPath']
            try:
                os.startfile(path_dir)
                pyperclip.copy(path_dir)
            except: pass

            # ------------------------------------------------------------------
            # 🎯 [신설] 다방 매물 등록 최종 검수 및 번호 추출 DB 저장 엔진
            # ------------------------------------------------------------------
            base_msg = (
                "[다방 매물번호 추출용] 최종 검수 대기 창입니다.\n\n"
                "1. 복사된 사진 경로를 활용해 사진 파일들을 업로드해 주세요.\n"
                "2. 오입력된 내용이 없는지 최종 검토 후 화면 하단의 [등록 완료]를 클릭해 주세요.\n"
                "3. 매물 등록이 성공하여 '다방 매물 관리' 목록 화면으로 성공적으로 복귀하면,\n"
                "   이 프로그램 안내창의 [확인] 버튼을 눌러주세요."
            )
            
            # 최상단 강제 고정 알림창 가동하여 소장님 검수 대기
            최상단알림창(base_msg, title="🔍 다방 매물 등록 최종 검수 대기")
            
            try:
                print("⏳ [매물번호 추출] 목록 화면에서 다방 매물 번호 추적을 시작합니다 (최대 10초 대기)...")
                
                # 매물 리스트(RoomList) 내부의 첫 번째 아이템 배지 단추 내 span 태그 정밀 조준
                target_badge_xpath = "(//ul[contains(@class, 'RoomList') or contains(@class, 'lkwaKR')]/li)[1]//button[contains(@class, 'BadgeBtn')]/span"
                
                da_code_el = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, target_badge_xpath))
                )
                dabang_code = da_code_el.text.strip()
                print(f"🎯 [추출 성공] 다방프로 최신 매물 번호 수거 완료 ➡️ {dabang_code}")
                
                # 💾 당근 매크로 동기화 규격 100% 매칭 데이터 가공
                print(f"💾 [DB 연동 시작] 새홈 매물번호 [{object_code_new}] 다방 광고 데이터 동기화 중...")
                
                admin_data = data.get('adminData', {})
                admin_name = admin_data.get('admin_name', '나상권')
                manager_id = admin_data.get('ad_id', '')
                
                current_date = datetime.now().strftime("%Y-%m-%d")
                current_time = datetime.now().strftime("%H:%M:%S")
                ad_start = current_date
                ad_end = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
                new_ad_memo = f"{admin_name} 등록, 다방:{dabang_code}"

                conn = None
                try:
                    conn = pymysql.connect(
                        host='obangkr.cafe24.com', user='obangkr', password='Ddhqkd!1', database='obangkr', charset='utf8'
                    )
                    cursor = conn.cursor()
                    
                    # 다방 광고 데이터 존재 여부 전수 검사
                    check_query = "SELECT * FROM pr_externalad WHERE object_code_new = %s AND ad_site = '다방'"
                    cursor.execute(check_query, (object_code_new,))
                    existing_record = cursor.fetchone()
                    
                    if existing_record:
                        update_query = """
                            UPDATE pr_externalad 
                            SET ad_code = %s, ad_udate = %s, ad_utime = %s, ad_memo = %s, ad_start = %s, ad_end = %s
                            WHERE object_code_new = %s AND ad_site = '다방'
                        """
                        cursor.execute(update_query, (dabang_code, current_date, current_time, new_ad_memo, ad_start, ad_end, object_code_new))
                        db_action_text = "기존 매물 광고코드 업데이트(UPDATE) 성공"
                    else:
                        insert_query = """
                            INSERT INTO pr_externalad (
                                admin_id, object_code_new, ad_start, ad_end, ad_site, ad_code, 
                                ad_manager, ad_manager_id, ad_udate, ad_utime, ad_memo, ad_wdate, ad_wtime
                            ) VALUES (%s, %s, %s, %s, '다방', %s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        cursor.execute(insert_query, (
                            manager_id, object_code_new, ad_start, ad_end, dabang_code, 
                            admin_name, manager_id, current_date, current_time, new_ad_memo, current_date, current_time
                        ))
                        db_action_text = "신규 매물 외부광고 데이터 삽입(INSERT) 성공"
                    
                    conn.commit()
                    print(f"   .. ✅ 다방 DB 동기화 최종 승인 완료! ({db_action_text})")
                    
                    # 최종 완료 브리핑 알림창
                    최상단알림창(
                        f"🎉 다방 매물 등록 및 오방 DB 저장 성공!\n\n"
                        f"• 새홈 매물번호 : {object_code_new}\n"
                        f"• 다방 등록번호 : {dabang_code}\n"
                        f"• 실시간 DB 조치 : {db_action_text}\n\n"
                        f"서버 데이터베이스에 매핑 정보가 정상 반영되었습니다.\n"
                        f"[확인]을 누르면 매크로 프로그램이 완전히 종료됩니다.",
                        title="✅ 다방 광고 연동 완료"
                    )
                    
                except Exception as db_err:
                    if conn: conn.rollback()
                    print(f"❌ [DB 동기화 실패] 트랜잭션 오류로 인해 롤백되었습니다 -> {db_err}")
                    최상단알림창(f"⚠️ 매물은 등록되었으나 오방 DB 저장에 실패했습니다.\n\n오류 내용: {db_err}", title="❌ DB 동기화 오류")
                finally:
                    if conn: conn.close()
                
            except Exception as extract_err:
                print(f"❌ [매물번호 추출 실패] 목록 화면을 찾지 못했거나 타임아웃 발생 -> {extract_err}")
                최상단알림창(
                    "완료 페이지에서 다방 매물번호를 자동으로 추출하는 데 실패했습니다.\n\n"
                    "리스트 로딩 지연 등으로 화면이 미처 다 켜지지 않았을 수 있으니,\n"
                    "다방 관리 화면 첫 번째 매물 우측에 생성된 번호를 확인 후 수동 저장해 주세요.",
                    title="⚠️ 추출 타임아웃"
                )

        except Exception as desc_e:
            print("⚠️ 상세 설명 주입 중 예외 발생:", str(desc_e))

    except Exception as e:
        print(f"프로세스 내부 오류 발생:\n{e}")
        pyautogui.alert(f"프로세스 내부 오류 발생:\n{e}")
        driver.quit()
        return