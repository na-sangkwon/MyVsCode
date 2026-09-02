from selenium import webdriver
from selenium.webdriver import ActionChains

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options

import pyautogui 
import pymysql
from datetime import datetime, timedelta

import traceback
import time

options = Options()

options.add_argument("--disable-blink-features=AutomationControlled")
# ChromeDriver 경로 설정
driver = webdriver.Chrome(options=options)



# URL 열기
driver.maximize_window()
driver.get('https://www.iros.go.kr/index.jsp')
# pyautogui.alert("로그인 셀랙터 선택?")
driver.implicitly_wait(10)
try:
    first_login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//div[@id="mf_wfm_potal_main_wf_header_grp_login"]/a[contains(text(), "로그인")]'))
    )
    driver.execute_script("arguments[0].click();", first_login_button)
    # first_login_button.click()
    second_login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//div[@id="mf_wfm_potal_main_wf_header_grp_login"]//div[contains(@class, "box-inner")]/a[contains(text(), "로그인")]'))
    )
    driver.execute_script("arguments[0].click();", second_login_button)
    # second_login_button.click()
    print("로그인 버튼 클릭 완료!")

except Exception as e:
    print(f"오류 발생: {str(e)}")
    traceback.print_exc()  # 전체 오류 메시지 출력
    pyautogui.alert(f"오류 발생: {str(e)}")  # 오류 메시지를 팝업창으로 출력

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

검색주소값 = '오산시 궐동 640-9'
# #집합건물이고 건물명이 "~동"으로 끝날 경우 건물명과 호수추가
# if tr_target == '건물' or tr_target == '층호수':
#     print("location_dongli:"+location_dongli+", location_dongNm:"+location_dongNm)
#     if building_type == '집합':
#         검색주소값 = location_dongli + location_dongNm + location_room
#     else:
#         print("일반건물이지만 건물개수가 2개 이상일 경우")
#         if tr_target != '토지' and brtit_count > 1:
#             검색주소값 = location_dongli + location_dongNm
# # 특수문자 제거: re.sub()를 사용하여 지정된 특수문자를 제거
# 검색주소값 = re.sub(r"[?&()'\"%_]", "", 검색주소값)                
driver.execute_script(f"arguments[0].value='{검색주소값}';", address_input)
print("검색주소값:"+검색주소값+" 입력")
time.sleep(0.5)
# pyautogui.alert("계속?")
driver.execute_script("arguments[0].dispatchEvent(new KeyboardEvent('keydown', {'key': 'Enter'}));", address_input)
# address_input.send_keys(Keys.ENTER)
print("엔터실행")
# # 물건종류가 토지일 경우
# if object_type == '토지':

# pyautogui.alert("열람대상물건의 부동산구분 선택후 계속?")

# pyautogui.alert("열람대상물건의 소유자확인후 계속?")
pyautogui.alert("열람대상물건의 용도 및 추가사항, 등기기록유형 선택단계에서 확인시 계속?")

select_element = driver.find_element(By.ID, "mf_wfm_potal_main_wfm_content_sel_cpab_kncd_input_0") # <select> 요소 찾기
select = Select(select_element) # Select 객체 생성
select.select_by_visible_text("현재유효사항") # 옵션 선택 (텍스트 기준)
print("현재유효사항 선택")
def 다음버튼클릭():
    다음버튼 = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, '//*[@id="mf_wfm_potal_main_wfm_content_btn_next"]'))
    )
    다음버튼.click()
def 결제버튼클릭():
    결제버튼 = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, '//*[@id="mf_wfm_potal_main_wfm_content_btn_bpay"]'))
    )
    결제버튼.click()
다음버튼클릭()
# 등초본종류선택 = WebDriverWait(driver, 10).until(
#     EC.visibility_of_element_located((By.XPATH, '//*[@id="mf_wfm_potal_main_wfm_content_btn_bpay"]'))
# )
# 등초본종류선택.click()
try:
    중복결제확인 = WebDriverWait(driver, 1).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="mf_wfm_potal_main_wfm_content_wq_uuid_15078"]'))
    )
    print("중복결제확인")
    첫번째이동버튼 = WebDriverWait(driver, 3).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="mf_wfm_potal_main_wfm_content_grd_dup_bpay_list_cell_0_8"]'))
    ).click()
    print("첫번째이동버튼 클릭")
    첫번째결제대상체크박스 = WebDriverWait(driver, 3).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="mf_wfm_potal_main_wfm_content_grd_bpay_obj_list_cell_0_0"]'))
    ).click()
    print("첫번째결제대상체크박스 체크")
    # pyautogui.alert("열람대상물건의 중복결제 확인 확인후 계속?")
except Exception as e:
    print(f"오류 발생: {str(e)}")
    다음버튼클릭()

# pyautogui.alert("열람대상물건의 (주민)등록번호 공개여부 확인후 계속?")
print("열람대상물건의 (주민)등록번호 공개여부 확인")
결제버튼클릭()
print("결제버튼 클릭")
# pyautogui.alert("계속?")
선불전자지급수단 = WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.XPATH, '//*[@id="mf_wfm_potal_main_wfm_content_tac_bpay_mthd_tab_tab_pp_tabHTML"]'))
)
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
pyautogui.alert("계속?")
결제버튼클릭()

input()
# time.sleep(20)




