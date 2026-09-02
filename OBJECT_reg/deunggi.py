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
import pyperclip
import tkinter as tk
from tkinter import messagebox

from selenium.common.exceptions import TimeoutException
import traceback

options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
    
def macro(data, user):
    object_ttype = data['writeData']['object_ttype']
    tr_target = data['writeData']['tr_target']
    master_name = data['writeData']['master_name']
    
    # location_lijibun = data['landData'][0]['representing_jibun'] if data['landData'][0]['land_li'] == '' else (data['landData'][0]['land_li'] + ' ' + data['landData'][0]['representing_jibun'])
    # location_dongli = (data['landData'][0]['land_dong'] + data['landData'][0]['representing_jibun']) if data['landData'][0]['land_li'] == '' else location_lijibun
    location_mainjibun = data['landData'][0]['land_main'] + data['landData'][0]['representing_jibun']

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

    검색주소값 = location_mainjibun
    #집합건물이고 건물명이 "~동"으로 끝날 경우 건물명과 호수추가
    if tr_target == '건물' or tr_target == '층호수':
        print("location_mainjibun:"+location_mainjibun+", location_dongNm:"+location_dongNm)
        print(f"building_type:{building_type}, location_dongNm:{location_dongNm}, brtit_count:{brtit_count}")
        if building_type == '집합':
            검색주소값 += location_dongNm
            if tr_target == '층호수':
                검색주소값 += location_room
        else:
            
            if tr_target != '토지' and brtit_count > 1:
                print("일반건물이지만 건물개수가 2개 이상일 경우")
                검색주소값 += location_dongNm
    # 특수문자 제거: re.sub()를 사용하여 지정된 특수문자를 제거
    검색주소값 = re.sub(r"[?&()'\"%_]", "", 검색주소값)
    # 검색주소값 = '장지동 1014-4'    #테스트용 주소
    # pyautogui.alert("검색주소값:"+검색주소값)


    def 테마별라디오선택(테마값, 선택값):
        try:
            # 1️⃣ 테마값이 포함된 div 요소 찾기
            테마_div = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, f'//div[starts-with(@id, "mf_wfm_potal_main_wfm_content_wq_uuid_") and contains(@class, "w2group element-con")]//p[label[text()="{테마값}"]]/ancestor::div[contains(@class, "w2group element-con")]')
                )
            )

            # 2️⃣ 해당 div 안의 라디오 버튼을 포함한 리스트(li) 찾기
            라디오_li = 테마_div.find_elements(By.XPATH, './/ul[contains(@class, "w2radio")]/li')

            for li in 라디오_li:
                # 3️⃣ li 안의 label 텍스트 가져오기
                라벨 = li.find_element(By.TAG_NAME, 'label')
                if 라벨.text.strip() == 선택값:
                    # 4️⃣ 해당 라벨을 클릭하여 선택
                    라벨.click()
                    print(f'✅ "{테마값}"에서 "{선택값}" 선택 완료')
                    return

            print(f'❌ "{테마값}"에서 "{선택값}"을 찾을 수 없음')

        except Exception as e:
            print(f'❌ 오류 발생: {str(e)}')




    driver = webdriver.Chrome(options=options)

    # 인터넷등기소 메인 URL 열기
    driver.maximize_window()
    driver.get('https://www.iros.go.kr/index.jsp')
    # pyautogui.alert("로그인 셀랙터 선택?")
    driver.implicitly_wait(10)
    time.sleep(2)
    # ─── 로그인 드롭다운 개방 방식 개선 (안정성 강화) ───
    try:
        print("🔍 로그인 셀랙터 대기 및 드롭다운 개방 확인...")
        first_xpath = '//div[@id="mf_wfm_potal_main_wf_header_grp_login"]/a[contains(text(), "로그인")]'
        second_xpath = '//div[@id="mf_wfm_potal_main_wf_header_grp_login"]//div[contains(@class, "box-inner")]/a[contains(text(), "로그인")]'
        
        # 1. 첫 번째 버튼이 화면에 보이고 '클릭 가능한 상태'가 될 때까지 대기
        first_login_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, first_xpath))
        )
        time.sleep(0.5) # 프레임워크 안정화를 위한 최소한의 정지

        # 2. 드롭다운 메뉴가 확실히 열릴 때까지 최대 3회 반복 시도
        dropdown_opened = False
        for i in range(3):
            try:
                # 일반 클릭 시도
                first_login_button.click()
                time.sleep(0.5)
                
                # 내부 로그인 버튼이 실제로 화면에 표시되는지 체크
                second_login_button = driver.find_element(By.XPATH, second_xpath)
                if second_login_button.is_displayed():
                    dropdown_opened = True
                    break
            except:
                # 일반 클릭이 안 통하거나 씹혔을 경우 JavaScript 강제 클릭으로 우회
                try:
                    driver.execute_script("arguments[0].click();", first_login_button)
                    time.sleep(0.5)
                    second_login_button = driver.find_element(By.XPATH, second_xpath)
                    if second_login_button.is_displayed():
                        dropdown_opened = True
                        break
                except:
                    pass
            
            print(f"🔄 드롭다운이 열리지 않아 재시도합니다... ({i+1}/3)")
            time.sleep(1)

        if not dropdown_opened:
            raise Exception("로그인 드롭다운 메뉴를 개방하는 데 실패했습니다.")

        print("✅ 로그인항목 선택 완료")
        time.sleep(0.5)
        second_login_button.click() # 실제 로그인 페이지로 이동하는 버튼 클릭
        
    except Exception as e:
        print(f"로그인선택 오류 발생: {str(e)}")
        traceback.print_exc()  # 전체 오류 메시지 출력
        pyautogui.alert(f"로그인선택 오류 발생: {str(e)}")  # 오류 메시지를 팝업창으로 출력  
        return  
    # ──────────────────────────────────────────────────────
    # try:
    #     print("로그인 셀랙터클릭")
    #     first_login_button = WebDriverWait(driver, 20).until(
    #         EC.presence_of_element_located((By.XPATH, '//div[@id="mf_wfm_potal_main_wf_header_grp_login"]/a[contains(text(), "로그인")]'))
    #     )
    #     # driver.execute_script("arguments[0].click();", first_login_button)
    #     first_login_button.click()
    #     # time.sleep(1)
    #     print("로그인항목 선택")
    #     second_login_button = WebDriverWait(driver, 20).until(
    #         EC.element_to_be_clickable((By.XPATH, '//div[@id="mf_wfm_potal_main_wf_header_grp_login"]//div[contains(@class, "box-inner")]/a[contains(text(), "로그인")]'))
    #     )
    #     # driver.execute_script("arguments[0].click();", second_login_button)
    #     time.sleep(1)
    #     second_login_button.click() #로그인항목 선택
    # except Exception as e:
    #     print(f"로그인선택 오류 발생: {str(e)}")
    #     traceback.print_exc()  # 전체 오류 메시지 출력
    #     pyautogui.alert(f"로그인선택 오류 발생: {str(e)}")  # 오류 메시지를 팝업창으로 출력  
    #     # driver.quit()    
    #     return  

    # pyautogui.alert("계속?")
    driver.implicitly_wait(10)
    # 입력 필드가 보일 때까지 대기
    user_id_input = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, '//*[@id="mf_wfm_potal_main_wfm_content_sbx_user_id_g___input"]'))
    )
    driver.execute_script("arguments[0].value = 'nsk98';", user_id_input)
    print("아이디 입력")
    user_pw_input = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, '//*[@id="mf_wfm_potal_main_wfm_content_sct_mbr_pw_g"]'))
    )
    driver.execute_script("arguments[0].value = 'dhqkd5555%';", user_pw_input)
    print("비번 입력")
    driver.find_element(By.XPATH, '//*[@id="mf_wfm_potal_main_wfm_content_btn_login"]').click()
    print("로그인버튼 클릭")

    address_input = driver.find_element(By.XPATH, '//*[@id="mf_wfm_potal_main_sch_realCorp___input"]')

    driver.execute_script(f"arguments[0].value='{검색주소값}';", address_input)
    print("검색주소값:"+검색주소값+" 입력")
    time.sleep(0.5)
    driver.execute_script("arguments[0].dispatchEvent(new KeyboardEvent('keydown', {'key': 'Enter'}));", address_input)
    # address_input.send_keys(Keys.ENTER)
    print("엔터실행")


    def 최상단알림창(message, title="알림"):
        root = tk.Tk()
        root.withdraw()  # 창 숨기기
        root.attributes("-topmost", True)  # 항상 위에 있도록 설정
        messagebox.showinfo(title, message)
        root.destroy()

    def 다음버튼클릭(text):
        다음버튼 = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="mf_wfm_potal_main_wfm_content_btn_next"]'))
        )
        다음버튼.click()
        print(text+" 다음버튼 클릭")
        time.sleep(1)
    def 결제버튼클릭(text):
        결제버튼 = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="mf_wfm_potal_main_wfm_content_btn_bpay"]'))
        )
        결제버튼.click()
        print(text+" 결제버튼 클릭")
        time.sleep(1)
    def 결제결과확인버튼클릭(text):
        결제버튼 = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[id$='_btn_cfrm']"))
        )
        결제버튼.click()
        print(text+" 확인 버튼 클릭 완료")
        time.sleep(1)

    def 결제대상물건개수_bodyId(tbody_id):
        """
        id가 'mf_wfm_potal_main_wfm_content_grd_bpay_obj_list_body_tbody'인 tbody에서
        display 상태가 'none'이 아닌 tr 태그 개수를 반환하는 함수
        """
        try:
            # tbody 내 display가 'none'이 아닌 tr 개수 찾기
            결제대상_tr목록 = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, f'//tbody[@id="{tbody_id}"]/tr[not(contains(@style, "display: none"))]')
                )
            )
            
            # 개수 출력
            결제대상개수 = len(결제대상_tr목록)
            print(f"✅ 결제 대상 물건 개수: {결제대상개수}개")
            return 결제대상개수

        except Exception as e:
            print(f"❌ 오류 발생: {str(e)}")
            return 0  # 오류 발생 시 0 반환

    # # 물건종류가 토지일 경우
    # if object_type == '토지':

    try:
        # ─── 건물 단일 목록 자동 선택 및 확인 기능 (마우스 물리 클릭 적용) ───
        auto_selected = False
        if tr_target != '토지':
            try:
                # 1. 부동산구분(data-col_id="real_cls_cd")이 '건물'인 눈에 보이는(visible) 행(tr) 찾기
                building_rows = driver.find_elements(By.XPATH, '//tbody[@id="mf_wfm_potal_main_wfm_content_grd_smpl_srch_rslt_body_tbody"]/tr[not(contains(@style, "display: none")) and ./td[@data-col_id="real_cls_cd" and .//text()="건물"]]')
                
                # 2. '건물' 항목이 딱 1개만 존재할 경우 자동 선택
                if len(building_rows) == 1:
                    # 💡 핵심 수정: 라디오 버튼이 들어있는 'td' 셀 자체를 타겟으로 잡습니다.
                    target_td = building_rows[0].find_element(By.XPATH, './/td[@data-col_id="rad_sel"]')
                    
                    # 💡 핵심 수정: ActionChains를 사용하여 실제 마우스를 움직여 클릭하는 물리 이벤트를 발생시킵니다.
                    actions = ActionChains(driver)
                    actions.move_to_element(target_td).click().perform()
                    
                    # 브라우저가 그래픽을 다시 그릴 수 있도록 아주 잠깐 대기
                    time.sleep(0.5)
                    
                    print("✅ '건물' 목록이 1개만 존재하여 자동으로 선택했습니다.")
                    auto_selected = True
            except Exception as e:
                print(f"❌ 자동 선택 중 오류 발생 (수동으로 전환): {str(e)}")

        # 자동 선택 여부와 관계없이 무조건 알림창을 띄워 사용자 확인을 받음
        if auto_selected:
            최상단알림창(검색주소값 + "\n\n'건물' 목록이 자동으로 선택되었습니다.\n화면의 체크 상태를 확인하신 후 '확인' 버튼을 누르세요.", "부동산 소재지번 자동선택")
        else:
            최상단알림창(검색주소값 + "\n\n부동산 소재지번 검색결과 선택후 '확인'버튼 클릭시 계속 진행합니다.", "부동산 소재지번 검색결과")
        
        print("부동산 소재지번 검색결과 선택 완료!!")
        다음버튼클릭("부동산 소재지번 검색결과")
        # ─────────────────────────────────────────
        # 최상단알림창(검색주소값+"\n\n부동산 소재지번 검색결과 선택후 '확인'버튼 클릭시 계속 진행합니다.","부동산 소재지번 검색결과")
        # # pyautogui.alert("열람대상물건의 부동산구분 선택후 계속?")
        # print("부동산 소재지번 검색결과 선택 완료!!")
        # 다음버튼클릭("부동산 소재지번 검색결과")
        # 최상단알림창(f"부동산 소재지번 선택후 '확인'버튼 클릭시 계속 진행합니다.\n\n등록된 소유자: {master_name}\n\n※주의: 자동결제과정을 포함합니다.","부동산 소재지번 선택 및 소유자확인")

        print("부동산 소재지번 선택 완료!!")
        다음버튼클릭("부동산 소재지번 선택")
        # pyautogui.alert("열람대상물건 선택후 '확인'버튼 클릭시 계속 진행합니다.")
        if object_ttype == '매매':
            print("공동담보전세목록 체크")
        #매매가 아닐 경우에만 '현재유효사항' 선택
        elif object_ttype != '매매':
            select_element = driver.find_element(By.ID, "mf_wfm_potal_main_wfm_content_sel_cpab_kncd_input_0") # <select> 요소 찾기
            select = Select(select_element) # Select 객체 생성
            select.select_by_visible_text("현재유효사항") # 옵션 선택 (텍스트 기준)
            print("현재유효사항 선택")
        # pyautogui.alert("다음 버튼 클릭전")
        다음버튼클릭("용도 및 추가사항 선택/등기기록유형 선택")
        # pyautogui.alert("다음 버튼 클릭후")
        print("용도 및 추가사항 선택/등기기록유형 선택 완료!!")
        # 등초본종류선택 = WebDriverWait(driver, 10).until(
        #     EC.visibility_of_element_located((By.XPATH, '//*[@id="mf_wfm_potal_main_wfm_content_btn_bpay"]'))
        # )
        # 등초본종류선택.click()

        def 보이는섹션내h4텍스트들(): #mf_wfm_potal_main_wfm_content
            try:
                print("🔍 보이는 섹션 찾기")
                time.sleep(1)
                # ✅ 보이는 섹션 찾기 (속도 문제 없음)
                보이는_섹션들 = [
                    섹션 for 섹션 in driver.find_elements(By.XPATH, '//div[@id="mf_wfm_potal_main_wfm_content"]//section')
                    if 섹션.is_displayed()
                ]
                print(f"오류확인!!")
                if not 보이는_섹션들:
                    print("❌ 보이는 섹션이 없습니다.")
                    return []

                print(f"✅ 보이는 섹션 개수: {len(보이는_섹션들)}")

                # ✅ 모든 h4 태그 한 번에 가져오기 (Selenium의 DOM 접근 최소화)
                모든_h4태그들 = driver.find_elements(By.XPATH, '//div[@id="mf_wfm_potal_main_wfm_content"]//section/div[1]/div[1]/h4')

                # ✅ 보이는 h4 태그만 필터링하여 텍스트 추출
                h4텍스트들 = [h4.text.strip() for h4 in 모든_h4태그들 if h4.is_displayed() and h4.text.strip()]

                print(f"✅ h4태그들 개수: {len(h4텍스트들)}")
                print(f"📌 찾은 h4 텍스트 리스트: {h4텍스트들}")
                # pyautogui.alert(f"✅ h4태그들 개수: {len(h4텍스트들)}\n\n{h4텍스트들}")

                return h4텍스트들  

            except Exception as e:
                print(f"❌ 오류 발생: {str(e)}")
                return []  # 오류 발생 시 빈 리스트 반환




        # '결제대상확인'이 화면에 보이면 결제대상선택 메세지 표시 //*[@id="mf_wfm_potal_main_wfm_content_wq_uuid_20218"]
        def 시작아이디와클래스로h4텍스트가져오기(시작아이디, 섹션클래스, h4클래스):
            try: 
                print("보이는 섹션찾기")
                보이는_섹션들 = [
                    섹션 for 섹션 in driver.find_elements(By.XPATH, f'//div[@id="mf_wfm_potal_main_wfm_content_contain-content"]//section[starts-with(@id, "{시작아이디}") and @class="{섹션클래스}"]')
                    if 섹션.is_displayed()
                ]                                         

                if not 보이는_섹션들:
                    print("❌ 보이는 섹션이 없습니다.")
                    return None
                print("보이는 섹션의 개수:"+str(len(보이는_섹션들)))
                # ✅ 보이는 섹션 중에서 `h4` 태그 찾기
                for idx, 섹션 in enumerate(보이는_섹션들):
                    print(f"\n🔍 보이는 섹션 {idx + 1}의 HTML:")
                    print(섹션.get_attribute("outerHTML"))  # 전체 HTML 출력
                    try:
                        h4태그요소 = 섹션.find_element(By.XPATH, 
                            f'.//h4[starts-with(@id, "{시작아이디}") and @class="{h4클래스}"]'
                        )

                        # ✅ `h4.text`가 `None`이면 빈 문자열 처리
                        h4텍스트 = h4태그요소.text.strip() if h4태그요소.text else ""

                        if h4텍스트:
                            print(f"✅ 찾은 h4 텍스트: {h4텍스트}")
                            return h4텍스트  # 첫 번째로 찾은 h4 텍스트 반환
                    except:
                        pass  # h4가 없으면 무시하고 다음 섹션 탐색

                print("❌ 보이는 섹션 내에서 해당 h4 태그를 찾지 못했습니다.")
                return None

            except Exception as e:
                print(f"❌ 오류 발생: {str(e)}")
                return None  # 오류 발생 시 None 반환            
            # try:
            #     #h4 태그 찾기 (id가 특정 패턴으로 시작하고, class가 일치하는 요소)
            #     h4태그요소 = WebDriverWait(driver, 10).until(
            #         EC.presence_of_element_located(
            #             (By.XPATH, f'//h4[starts-with(@id, "{시작아이디}") and contains(@class, "{클래스}")]')
            #         )
            #     )
            #     # pyautogui.alert("h4텍스트:"+h4태그요소.text)
            #     print("h4텍스트:"+h4태그요소.text)
            #     #텍스트 반환
            #     return h4태그요소.text.strip()

            # except Exception as e:
            #     print(f"오류 발생: {str(e)}")  
            #     return None  # 오류 발생 시 None 반환
        # pyautogui.alert("h4텍스트 확인전")    
        # h4텍스트 = 시작아이디와클래스로h4텍스트가져오기("mf_wfm_potal_main_wfm_content_wq_uuid_", "w2group content-sec", "w2textbox df-tit")
        h4텍스트들 = 보이는섹션내h4텍스트들()
        if '중복결제 확인' in h4텍스트들:
            print("중복결제 확인")
            try:
                첫번째이동버튼 = WebDriverWait(driver, 3).until(
                        EC.visibility_of_element_located((By.XPATH, '//*[@id="mf_wfm_potal_main_wfm_content_grd_dup_bpay_list_cell_0_8"]'))
                ).click()
                print("첫번째이동버튼 클릭")
                # h4텍스트 = 시작아이디와클래스로h4텍스트가져오기("mf_wfm_potal_main_wfm_content_wq_uuid_", "w2group content-sec", "w2textbox df-tit")
                h4텍스트들 = 보이는섹션내h4텍스트들()
                if '결제대상 확인' in h4텍스트들:
                    print("결제대상 확인")
                    # 전체결제대상체크박스 = WebDriverWait(driver, 3).until(
                    #         EC.visibility_of_element_located((By.XPATH, '//*[@id="mf_wfm_potal_main_wfm_content_grd_bpay_obj_list_chk_all"]/label'))
                    # ).click()

                    #결제대상 개수확인
                    결제대상물건개수 = 결제대상물건개수_bodyId("mf_wfm_potal_main_wfm_content_grd_bpay_obj_list_body_tbody")
                    if 결제대상물건개수 > 1 :
                        첫번째결제대상체크박스 = WebDriverWait(driver, 3).until(
                                EC.visibility_of_element_located((By.XPATH, '//*[@id="mf_wfm_potal_main_wfm_content_grd_bpay_obj_list_cell_0_0"]/label'))
                        ).click()
                        print("첫번째결제대상체크박스 체크(강제)")
                        pyautogui.alert("계속 진행하시려면 결제할 대상의 체크상태를 확인하시고\n\n'확인'버튼을 클릭하세요!! =>결제","열람대상물건의 결제대상 체크상태 확인")
                    else:
                        print("첫번째결제대상체크박스 체크(자동)")
                    
                    결제버튼클릭("결제대상 확인")
                # 다음버튼클릭()
            except Exception as e:
                print(f"중복결제확인중 오류 발생: {str(e)}")
                pyautogui.alert(f"중복결제확인중 오류 발생: {str(e)}")
                다음버튼클릭("중복결제확인중 오류")
        elif '결제대상 확인' in h4텍스트들:
            print("결제대상 확인(자동체크)")
            # 첫번째결제대상체크박스 = WebDriverWait(driver, 3).until(
            #         EC.visibility_of_element_located((By.XPATH, '//*[@id="mf_wfm_potal_main_wfm_content_grd_bpay_obj_list_cell_0_0"]'))
            # ).click()
            # print("첫번째결제대상체크박스 체크")
            pyautogui.alert("계속 진행하시려면 결제할 대상의 체크상태를 확인하시고\n\n'확인'버튼을 클릭하세요!! =>결제","열람대상물건의 결제대상 체크상태 확인")
            결제버튼클릭("결제대상 확인(자동체크)")
            # pyautogui.alert("결제대상 선택후 '확인'버튼을 클릭하세요~!!")
            # 다음버튼클릭()
        elif '(주민)등록번호 공개여부 확인' in h4텍스트들: #mf_wfm_potal_main_wfm_content_contain-content mf_wfm_potal_main_wfm_content_grp_enr_no_publc_msg
            다음버튼클릭("열람대상물건의 (주민)등록번호 공개여부 확인")
            print("열람대상물건의 (주민)등록번호 공개여부 확인")
            # pyautogui.alert("h4텍스트 테스트 시작?")
            # time.sleep(2)
            # h4텍스트 = 시작아이디와클래스로h4텍스트가져오기("mf_wfm_potal_main_wfm_content_wq_uuid_", "w2group content-sec", "w2textbox df-tit")
            h4텍스트들 = 보이는섹션내h4텍스트들()
            # pyautogui.alert("현재 검색된 h4텍스트:"+h4텍스트들)
            if '등기신청사건 처리여부 확인' in h4텍스트들:
                다음버튼클릭("등기신청사건 처리여부 확인")
            결제버튼클릭("결제대상확인")
            print("결제대상확인")
        # elif h4텍스트 == '(주민)등록번호 공개여부 확인':
        #     다음버튼클릭()
        #     print("열람대상물건의 (주민)등록번호 공개여부 확인")
        #     결제버튼클릭()
        #     print("결제대상확인")
        else:
            pyautogui.alert("예상 밖의 진행단계 입니다.")
        # 다음버튼클릭()


        # 결제버튼클릭()
        # pyautogui.alert("계속?")
        # print("선불전자지급수단 조회중")
        선불전자지급수단 = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="mf_wfm_potal_main_wfm_content_tac_bpay_mthd_tab_tab_pp_tabHTML"]'))
        )
        # pyautogui.alert("계속?")
        선불전자지급수단.click()
        선불전자지급수단번호_앞 = driver.find_element(By.XPATH, '//*[@id="mf_wfm_potal_main_wfm_content_sbx_emoney_code1___input"]')
        선불전자지급수단번호_뒤 = driver.find_element(By.XPATH, '//*[@id="mf_wfm_potal_main_wfm_content_sbx_emoney_code2___input"]')
        선불전자지급수단_비밀번호 = driver.find_element(By.XPATH, '//*[@id="mf_wfm_potal_main_wfm_content_sct_emoney_pwd"]')
        선불전자지급수단번호 = 'X5747511 0970'
        # 선불전자지급수단번호에서 앞 8자리를 추출하여 선불전자지급수단번호1에 저장
        선불전자지급수단번호1 = 선불전자지급수단번호[:8]
        # 선불전자지급수단번호에서 뒤 4자리를 추출하여 선불전자지급수단번호2에 저장
        선불전자지급수단번호2 = 선불전자지급수단번호[-4:]
        선불전자지급수단비번 = '3755555'
        선불전자지급수단번호_앞.click()
        driver.execute_script(f"arguments[0].value='{선불전자지급수단번호1}';", 선불전자지급수단번호_앞)
        선불전자지급수단번호_뒤.click()
        driver.execute_script(f"arguments[0].value='{선불전자지급수단번호2}';", 선불전자지급수단번호_뒤)
        선불전자지급수단_비밀번호.click()
        driver.execute_script(f"arguments[0].value='{선불전자지급수단비번}';", 선불전자지급수단_비밀번호)
        전체동의체크박스 = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="mf_wfm_potal_main_wfm_content_chk_whl_agree"]/li/label'))
        )
        전체동의체크박스.click()
        # pyautogui.alert("계속?")
        time.sleep(0.5)
        결제버튼클릭("선불전자지급수단 입력")

        #결제확인버튼 클릭

        try:
            # 1. 팝업이 뜨고 버튼이 클릭 가능할 때까지 대기 (최대 10초)
            # CSS Selector 설명: ID가 '_wframe_btn_confirm2'로 끝나는 a 태그를 찾음
            confirm_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a[id$='_wframe_btn_confirm2']"))
            )
            # 2. 버튼 클릭
            confirm_btn.click()
            print("확인 버튼 클릭 성공")

        except Exception as e:
            print(f"오류 발생: {e}")
        # pyautogui.alert("계속?")  

        try:
            print("결제결과확인")
            결제결과확인버튼클릭("결제결과확인")
        except Exception as e:
            print(f"결제결과확인 오류 발생: {e}")

        # ─── 열람버튼 클릭 방식 개선 (건수 확인 대기 ➡️ 사용자 선택 분기) ───
        doc_saved = False  # 증명서 저장 성공 여부를 체크할 플래그 변수
        try:
            print("🔍 미열람·미발급 목록 로딩 대기 중...")
            
            # 1. 전체 건수 표시 span 요소가 로드될 때까지 대기
            total_count_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "mf_wfm_potal_main_wfm_content_spa_nview_nissue_tacnt"))
            )
            
            # 2. 전체 건수 텍스트가 '1'이 될 때까지 최대 10초간 대기 (비동기 로딩 대응)
            WebDriverWait(driver, 10).until(
                lambda d: total_count_element.text.strip() == "1"
            )
            print(f"✅ 목록 로드 완료! (전체 건수: {total_count_element.text.strip()}건)")

            # 💡 [안전장치] 열람 진행 여부를 묻는 최상단 Yes/No 팝업창 생성
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            is_confirm = messagebox.askyesno(
                "[인터넷등기소] 결제 완료",
                f"{검색주소값}\n\n수수료 결제가 완료되었습니다.\n지금 바로 자동 열람 및 저장을 진행하시겠습니까?\n\n(※ '예' 선택 시 즉시 열람되며 이후 결제취소가 불가능합니다.)"
            )
            root.destroy()

            if is_confirm:  # 사용자가 '예'를 누른 경우에만 진행
                # 3. 목록 테이블의 tbody 요소 찾기
                열람목록tbody = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.ID, "mf_wfm_potal_main_wfm_content_grd_nview_nissue_list_body_tbody"))
                )

                # 4. 화면에 실제로 보이는(visible) tr 행들만 필터링
                visible_trs = [tr for tr in 열람목록tbody.find_elements(By.TAG_NAME, "tr") if tr.is_displayed()]

                if len(visible_trs) >= 1:
                    target_tr = visible_trs[0]  # 첫 번째 행 타겟팅
                    
                    # 5. 행 내부에서 '열람' 버튼 찾기
                    try:
                        열람버튼 = target_tr.find_element(By.ID, "btn_issue")
                    except:
                        열람버튼 = target_tr.find_element(By.XPATH, ".//*[contains(@title, '열람 버튼') or text()='열람']")
                    
                    # 6. 안전하게 클릭 실행
                    driver.execute_script("arguments[0].click();", 열람버튼)
                    print("✅ 첫 번째 목록의 '열람' 버튼 클릭 성공!")
                    
                    # 7. 저장 팝업창 대응 및 저장 버튼 자동 클릭
                    try:
                        print("🔍 열람 팝업창 및 저장 버튼 로딩 대기 중...")
                        저장버튼 = WebDriverWait(driver, 15).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[id$='_btn_download']"))
                        )
                        time.sleep(1)
                        저장버튼.click()
                        print("✅ 열람한 증명서의 '저장' 버튼 클릭 완료!")
                        time.sleep(2)
                        doc_saved = True  # 저장까지 완벽히 마쳤으므로 True 처리
                    except Exception as popup_e:
                        print(f"❌ 저장 팝업창 처리 중 오류 발생: {str(popup_e)}")
                else:
                    print(f"⚠️ 표기 건수는 1건이지만, 실제로 매칭되는 활성화된 행(tr)이 없습니다.")
            else:
                print("🛑 사용자가 '아니오'를 선택하여 자동 열람을 중단합니다.")

        except Exception as e:
            print(f"열람/저장 단계 진행 중 오류 발생: {e}")
        # ──────────────────────────────────────────────────────────────────

    except Exception as e:
        print(f"항목 선택 중 오류 발생: {e}")
    finally:
        folder_msg = ""
        try:
            # 폴더경로 복사
            deunggiPath = data.get("deunggiPath")
            main_dir = 'Z:\\업무자료\\4사진자료&이미지자료(외부유출금지)\\1주거용물건, 상업용물건\\'
            path_dir = main_dir + deunggiPath
            pyperclip.copy(path_dir) 
            folder_msg = "\n\n※폴더경로가 복사되었습니다.\n" + path_dir
        except Exception as e:
            print("❌ 폴더경로 복사중 오류 발생:", str(e))  
        
        # ─── 💡 종료 메시지 동적 분기 처리 ───
        if 'doc_saved' in locals() and doc_saved:
            # '예'를 누르고 다운로드(저장)까지 성공한 경우
            final_msg = "프로세스가 종료되었습니다.\n\n열람한 증명서가 저장되었습니다." + folder_msg
        else:
            # '아니오'를 눌렀거나 저장 전 단계에서 멈춘 경우 (요청하신 기존 문구 유지)
            final_msg = "프로세스가 종료되었습니다.\n\n확인시 진행중인 창을 닫습니다." + folder_msg
            
        pyautogui.alert(final_msg, "[인터넷등기소]")
        driver.quit()
        pass
