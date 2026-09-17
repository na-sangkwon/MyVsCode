import os
from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
# from selenium.webdriver import ActionChains
# import chromedriver_autoinstaller

# #크롬 브라우저 버전 확인하기
# chrome_ver = chromedriver_autoinstaller.get_chrome_version()
# print(chrome_ver) # 108.0.5359.125

# chromedriver_autoinstaller.install(True)
# chromedriver_path = f'./{chrome_ver.split(".")[0]}/chromedriver.exe'
# print(chromedriver_path) # ./103/chromedriver.exe
# print(os.path.exists(chromedriver_path)) # True
# print(os.path.basename(chromedriver_path)) # chromedriver.exe


# from Check_Chromedriver import Check_Chromedriver
# Check_Chromedriver.driver_mother_path = "C:\\Users\\nasan\\AppData\\Local\\SeleniumBasic"
# Check_Chromedriver.main()


from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.select import Select

from selenium.webdriver.chrome.options import Options

import pyautogui
import time
import pymysql
import traceback
import tkinter as tk
from tkinter import messagebox

from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5.QtWidgets import QMessageBox, QApplication, QMainWindow

import requests
import re


from ftplib import FTP
# ftp = FTP('obangkr.cafe24.com', 'obangkr', 'Ddhqkd!1')
from pathlib import Path

options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("detach", True)

# # ChromeDriver 경로 설정
# driver = webdriver.Chrome(options=options)
# driver = webdriver.Chrome('/chromedriver', options=options)

# 기존 파일 제거
def remove_existing_files(ftp, directory):
    print('directory:', directory)
    try:
        file_list = ftp.nlst()  # 현재 디렉토리의 파일 목록 가져오기
    except Exception as e:
        print(f"Error retrieving file list from {directory}: {str(e)}")
        return
    print("지워질 파일들:", file_list)

    for file in file_list:
        if file not in ('.', '..'):  # 현재 디렉토리 및 상위 디렉토리 제외
            try:
                ftp.delete(file)
                print(f"Deleted file: {file}")
            except Exception as e:
                print(f"Error deleting file {file}: {str(e)}")

# 디렉토리 생성
def is_directory_exists(ftp, directory):
    try:
        ftp.cwd(directory)
        # ftp.cwd('..')
        return True
    except:
        return False        
          
def 최상단알림창(message, title="알림"):
    root = tk.Tk()
    root.withdraw()  # 창 숨기기
    root.attributes("-topmost", True)  # 항상 위에 있도록 설정
    messagebox.showinfo(title, message)
    root.destroy()

def 가장용량이작은파일찾기(photo_list, path):
    smallest_file = None
    smallest_size = float('inf')  # 초기화를 무한대로 설정

    for file in photo_list:
        file_path = os.path.join(path, file)
        size = os.path.getsize(file_path)
        
        # print(f"Checking file {file} with size {size}")  # 파일 이름과 크기 출력
        if size < smallest_size:
            smallest_size = size
            smallest_file = file

    # print(f"Smallest file is {smallest_file} with size {smallest_size}")  # 가장 작은 파일과 그 크기 출력
    return smallest_file

def 그룹별명칭변환(그룹, 대상명칭):
    # 변환 매핑
    변환사전 = {}
    if 그룹 == '구군':
        변환사전 = {
            "수원시 권선구": "수원권선구",
            "수원시 영통구": "수원영통구",
            "수원시 장안구": "수원장안구",
            "수원시 팔달구": "수원팔달구",
            "용인시 처인구": "용인처인구",
            "용인시 기흥구": "용인기흥구",
            "용인시 수지구": "용인수지구",
            # 추가 매핑
        }
    elif 그룹 == '읍면동':
        변환사전 = {
            "남사읍": "남사면",
            "대로접": "큰길가",
            # 추가 매핑
        }

    # 매핑된 값 반환, 매핑되지 않았으면 원래 값을 반환
    return 변환사전.get(대상명칭, 대상명칭)

def 숫자한글로금액변환(숫자금액):
    # print("숫자한글로금액변환("+str(숫자금액)+")")
    # 억과 만원으로 나누기
    billion = int(숫자금액) // 10000  # 억
    million = int(숫자금액) % 10000   # 만원
    # 변환한 값을 문자열로 만들기
    변환된금액 = ''
    if billion > 0:
        변환된금액 += f"{billion}억"
    if million > 0:
        변환된금액 += f"{million}만원"
    # 값이 없는 경우 "0원"으로 설정
    if not 변환된금액:
        변환된금액 = "0원"
    return 변환된금액


def 메모에마크추가(메모, 마크='-- '):
    if not 메모:  # 메모가 None 또는 빈 문자열인 경우 예외 처리
        return ""            
    # 줄 단위로 나누고, 각 줄에 '-- ' 추가
    return "<br>".join([f"{마크}{line}" for line in 메모.split("<br>") if line.strip()])       
    
def macro(data, user, group):
    # ChromeDriver 경로 설정
    # driver = webdriver.Chrome('/chromedriver', options=options)
    driver = webdriver.Chrome(options=options)
    # driver = webdriver.Chrome(ChromeDriverManager().install())    
    errarr = []
    # pyautogui.alert(data['adminData'])
    obang_id = 'omnsk8@gmail.com' if data['adminData']['obang_id'] == '' else data['adminData']['obang_id']
    obang_pw = 'dhqkd5555%' if data['adminData']['obang_pw'] == '' else data['adminData']['obang_pw']
    # obang_id = data['adminData']['obang_id']
    # obang_pw = data['adminData']['obang_pw']
    
    # 현재 날짜 출력
    import datetime
    current_date = datetime.date.today()
    formatted_date = current_date.strftime("%Y-%m-%d")

    I_memo = ''

    admin_name = data['adminData']['admin_name']
    # print(ad_email, ad_pw)
    tr_target = data['writeData']['tr_target']
    location_do = data['landData'][0]['land_do']
    if location_do.endswith('도'):
        if '경상남도' in location_do:
            location_do = '경남'
        elif '경상북도' in location_do:
            location_do = '경북'
        elif '충청남도' in location_do:
            location_do = '충남'
        elif '충청북도' in location_do:
            location_do = '충북'
        elif '전라남도' in location_do:
            location_do = '전남'
        elif '전라북도' in location_do:
            location_do = '전북'
        elif '강원특별자치도' in location_do:
            location_do = '강원'
        else:
            location_do = location_do[:-1]
    elif location_do.endswith('특별시'):
        location_do = location_do[:-3]
    location_si = data['landData'][0]['land_si']
    location_dong = data['landData'][0]['land_dong']

    location_lijibun = data['landData'][0]['land_jibun'] if data['landData'][0]['land_li'] == '' else (data['landData'][0]['land_li'] + ' ' + data['landData'][0]['land_jibun'])
    location_dongli = (data['landData'][0]['land_dong'] + data['landData'][0]['land_jibun']) if data['landData'][0]['land_li'] == '' else location_lijibun
    location_detail = location_dongli
    land_totarea = data['landData'][0]['land_totarea'] #대지면적
    land_memo = data['landData'][0]['land_memo'] #토지메모
    land_memo_formatted = 메모에마크추가(land_memo , '· ')
    if land_memo_formatted:
        I_memo += ("<br>" if I_memo else "") + land_memo_formatted
    main_area = land_totarea
    main_option = ''
    main_important = ''
    object_loan = ''
    sum_deposit = ''
    sum_rent = ''
    sum_mmoney = ''
    sum_etc = ''

    request_code = data['writeData']['request_code'] #의뢰번호
    object_code_new = data['writeData']['object_code_new'] #새홈매물번호
    obang_code = data['writeData']['obang_code'] #오방매물번호
    land_code = data['writeData']['land_code'] #토지코드
    building_code = data['writeData']['building_code'] #건물코드
    room_code = data['writeData']['room_code'] #호실코드
    object_type = data['writeData']['object_type'] #물건종류
    object_type1 = data['writeData']['object_type1']

    obinfo_trading = data['writeData']['trading'] #매매금액    
    obinfo_deposit1 = data['writeData']['deposit1'] #보증금1
    if obinfo_deposit1 == '' :
        pyautogui.alert("임대료는 필수입니다. 확인후 다시 시작하세요~")
    # if obinfo_trading == '' and obinfo_deposit1 == '' :
    #     pyautogui.alert("거래금액은 필수입니다. 확인후 다시 시작하세요~")
        driver.quit()
        return
        # driver.close()
    obinfo_deposit2 = data['writeData']['deposit2'] #보증금2
    obinfo_deposit3 = data['writeData']['deposit3'] #보증금3
    obinfo_rent1 = '0' if data['writeData']['rent1'] == '' else data['writeData']['rent1'] #월세1
    obinfo_rent2 = '0' if data['writeData']['rent2'] == '' else data['writeData']['rent2'] #월세2
    obinfo_rent3 = '0' if data['writeData']['rent3'] == '' else data['writeData']['rent3'] #월세3


    # Step 1: 먼저 기본적인 '전세' 또는 '월세'를 판단합니다.
    # obinfo_deposit1 은 필수라 가정하고, '0'이면 값이 없는 것으로 간주
    if obinfo_rent1 != '0':
        # obinfo_rent1에 값이 있다면 월세 (혹은 전월세의 월세 부분)
        obang_ttype = "월세"
    else:
        # obinfo_rent1이 0이면 전세
        obang_ttype = "전세"

    # Step 2: 이제 '전월세' 여부를 판단합니다.
    # 유효한 두 번째 이상의 거래 옵션이 있는지 확인 (여기서 obinfo_deposit2,3 또는 obinfo_rent2,3에 의미 있는 값이 있는지)
    # '0'은 값이 없음을 의미하므로, '0'이 아닌 다른 값이 들어있어야 '전월세'로 간주
    # obinfo_deposit2/3는 '' 아니면 유효한 값, obinfo_rent2/3는 '0' 아니면 유효한 값

    # Case 1: 이미 '전세'로 분류되었는데, 월세 옵션이 추가로 있는 경우
    if obang_ttype == "전세" and (obinfo_rent2 != '0' or obinfo_rent3 != '0'):
        obang_ttype = "전월세"
    # Case 2: 이미 '월세'로 분류되었는데, 전세 옵션(예: deposit1 외에 deposit2,3에만 값)이나 다른 형태의 월세 옵션이 추가로 있는 경우
    elif obang_ttype == "월세" and (obinfo_deposit2 != '' or obinfo_deposit3 != '' or obinfo_rent2 != '0' or obinfo_rent3 != '0'):
        # 보증금2,3이나 월세2,3에 유효한 값이 있다면 전월세로 변경
        # obinfo_deposit1(필수)과 obinfo_rent1(0이 아님)으로 이미 월세로 분류되었기 때문에
        # 다른 옵션들이 존재하는지만 보면 됨
        if obinfo_deposit2 != '' or obinfo_deposit3 != '': # 추가 보증금이 있다면 전월세
            obang_ttype = "전월세"
        # 이미 월세인 경우, rent2, rent3가 '0'이 아니면 다른 월세 옵션이 있으니 전월세
        elif obinfo_rent2 != '0' or obinfo_rent3 != '0':
            obang_ttype = "전월세"
    # obinfo_ttype = data['writeData']['object_ttype'] #거래종류
    # if ',' in obinfo_ttype: #쉼표가 있다면 쉼표로 분리후 첫번째 항목을 값으로 지정
    #     obinfo_ttype_arr = obinfo_ttype.split(',')
    # else:
    #     obinfo_ttype_arr = [obinfo_ttype]
    # # '매매'를 제외한 배열을 생성
    # obinfo_ttype_arr = [item for item in obinfo_ttype_arr if item != '매매']
    # # 조건에 따라 obinfo_ttype 값을 결정
    # obang_ttype = '매매'
    # if '전세' in obinfo_ttype_arr and '월세' in obinfo_ttype_arr:
    #     obang_ttype = '전/월세'
    # elif '전세' in obinfo_ttype_arr:
    #     obang_ttype = '전세'
    # elif '월세' in obinfo_ttype_arr:
    #     obang_ttype = '월세'
        

    basic_manager = data['writeData']['manager'] #관리비 별도/포함/미확인
    basic_mmoney = data['writeData']['mmoney'] #관리비
    basic_mlist = data['writeData']['mlist'] #관리비포함내역
    
    add_warmer = '' #data['writeData']['add_warmer'] 난방
    add_rdate = str(data['writeData']['rdate']) #입주일
    secret_1 = '' if data['writeData']['tr_memo'] == '' else data['writeData']['tr_memo'] + Keys.ENTER
    secret_2 = '' if data['landData'][0]['land_memo'] == '' else data['landData'][0]['land_memo'] + Keys.ENTER
    basic_secret = secret_1 + secret_2 #비밀메모
        
    if tr_target == '건물' or tr_target == '층호수':
        location_building = '' if data['buildingData']['building_name'] == '' else ' ' + data['buildingData']['building_name']
        building_gate1 = ' '+data['buildingData']['building_gate1'] if data['buildingData']['building_gate1']!='비밀번호' else ' 현' #건물출입1
        building_gate2 = data['buildingData']['building_gate2'] if data['buildingData']['building_gate2'] != '' else '' #건물출입2  
        building_gate = building_gate1+building_gate2 if data['buildingData']['building_gate1'] == '비밀번호' else ''
        location_detail += location_building + building_gate
        # print("building_gate1:", building_gate1)
        # print("building_gate2:", building_gate2)
        building_archarea = data['buildingData']['building_archarea'] #건축면적
        building_totarea = data['buildingData']['building_totarea'] #연면적
        basic_totflr = str(int(data['buildingData']['building_grndflr']) + int(data['buildingData']['building_ugrndflr'])) #전체층
        building_ugrndflr = data['buildingData']['building_ugrndflr'] #지하층수
        building_grndflr = data['buildingData']['building_grndflr'] #지상층수
        building_bolt = data['buildingData']['building_bolt'] #공급전력
        building_height = data['buildingData']['building_height'] #건물높이
        add_usedate = str(data['buildingData']['building_usedate']) #준공일
        building_options = data['buildingData']['building_option'] #건물옵션
        building_importants = data['buildingData']['building_important'] #건물옵션
        add_pn = data['buildingData']['building_pn'] #주차
        building_loan = data['buildingData']['building_loan'] #대출금(건물)
        sum_deposit = data['buildingData']['sum_deposit'] #총보증금
        sum_rent = data['buildingData']['sum_rent'] #총월세
        sum_mmoney = data['buildingData']['sum_mmoney'] #총관리비
        sum_etc = data['buildingData']['sum_etc'] #기타비용
        building_memo = data['buildingData']['building_memo'] #건물메모
        building_memo_formatted = 메모에마크추가(building_memo , '· ')
        if building_memo_formatted:
            I_memo += ("<br>" if I_memo else "") + building_memo_formatted
        secret_3 = '' if data['buildingData']['building_memo'] == '' else data['buildingData']['building_memo'] + Keys.ENTER
        basic_secret += secret_3
        main_area = building_totarea
        main_option += building_options
        main_important += building_importants
        object_loan = building_loan
        
    if tr_target == '층호수':
        location_room = '' if data['roomData']['room_num'] == '' else ' ' + data['roomData']['room_num']
        room_status = ' '+data['roomData']['room_status'] if data['roomData']['room_status']!='미확인' else ' 상태미확인' #호실상태
        room_gate1 = ' '+data['roomData']['room_gate1'] if data['roomData']['room_gate1']!='비밀번호' else ' 방' #내부출입1
        room_gate2 = ':'+data['roomData']['room_gate2'] if data['roomData']['room_gate2'] != '' else '' #내부출입2  
        room_gate = room_status+room_gate1+room_gate2 if room_gate1 != ' 미확인' else ' 미확인'
        location_detail += location_room+room_gate
        basic_area1 = data['roomData']['room_area1'] #실면적
        basic_area2 = data['roomData']['room_area2'] #공급면적
        basic_rcount = data['roomData']['room_rcount'] #방수
        basic_bcount = data['roomData']['room_bcount'] #욕실수
        basic_floor = data['roomData']['room_floor'] #해당층
        add_importants = data['roomData']['room_important'] #호실특징
        room_options = data['roomData']['room_option'] #옵션선택
        room_memo = data['roomData']['room_memo'] #호실메모
        room_memo_formatted = 메모에마크추가(room_memo , '· ')
        if room_memo_formatted:
            I_memo += ("<br>" if I_memo else "") + room_memo_formatted
        secret_4 = '' if data['roomData']['room_memo'] == '' else data['roomData']['room_memo'] + Keys.ENTER
        basic_secret += secret_4
        main_area = basic_area1
        main_option += ','+room_options if main_option != '' else room_options
        main_important += ','+add_importants if main_important != '' else add_importants
    basic_secret = f"[새홈{object_code_new}] 수정일:"+formatted_date+" "+admin_name + Keys.ENTER +" https://obangkr.cafe24.com/web/request/request_view/view_give_request_detail.php?request_code="+request_code
    print("등록될 상세주소:", location_detail)
    main_area_pyeong = str(int(float(main_area)/3.305785)) if main_area != '' else ''

    obinfo_type = object_type1
    obinfo_type2 = ''
    # print(f"tr_target:{tr_target}\nobject_type:{object_type}\n방개수:{data['roomData']['room_rcount']}\nobinfo_type:{obinfo_type}\nadd_importants:{add_importants}")
    # pyautogui.alert(f"tr_target:{tr_target}\nobject_type:{object_type}\n방개수:{data['roomData']['room_rcount']}\nobinfo_type:{obinfo_type}\nadd_importants:{add_importants}")
    if tr_target == '층호수':
        object_info_code = room_code
        if object_type == '주거용':
            if data['roomData']['room_rcount'] == '':
                pyautogui.alert("방개수 확인후 다시 시작하세요")
                # driver.close()
                # # WebDriver 종료
                driver.quit()    
                return            
            else:
                room_rcount = float(data['roomData']['room_rcount'])
                if room_rcount >= 1 and room_rcount < 2:
                    obinfo_type = '원룸'
                    if room_rcount >= 1 and room_rcount < 1.5 :
                        if "오픈형" in add_importants:
                            obinfo_type2 = "오픈형"
                        elif "분리형(현)" in add_importants or "분리형(베)" in add_importants:
                            obinfo_type2 = "분리형"
                        else:
                            obinfo_type2 = "분리형" 
                    elif room_rcount >= 1.5 and room_rcount < 1.8 :
                        obinfo_type2 = '1.5룸'
                    elif room_rcount >= 1.8 and room_rcount < 2 :
                        obinfo_type2 = '1.8룸'
                elif room_rcount >= 2:
                    obinfo_type = '투룸/쓰리룸+'
                    if room_rcount == 2:
                        obinfo_type2 = '투룸'
                    elif room_rcount >= 3:
                        obinfo_type2 = '쓰리룸+'
                # print(f"obinfo_type2:{obinfo_type2}")
                # pyautogui.alert(f"obinfo_type2:{obinfo_type2}")

        elif object_type == '상업용':
            obinfo_type = '상가/사무실'
        elif object_type == '공업용':
            obinfo_type = '공장/창고'
    elif tr_target == '건물':
        object_info_code = building_code
        if object_type == '공업용':
            obinfo_type = '공장/창고'
        else:
            obinfo_type = '통건물'
            if object_type == '주거용':
                obinfo_type2 = '다가구주택'
            elif object_type == '상업용':
                obinfo_type2 = '상업용건물'
    elif tr_target == '토지':
        object_info_code = land_code
        obinfo_type = '토지'

    # URL 열기
    driver.maximize_window()
    driver.get('https://osanbang.com/adminlogin/index')

    driver.find_element(By.XPATH, '//*[@id="login_form"]/div[1]/div/input').send_keys(obang_id)
    driver.find_element(By.XPATH, '//*[@id="login_form"]/div[2]/div/input').send_keys(obang_pw)
    driver.find_element(By.XPATH, '//*[@id="login_form"]/div[3]/button').click()

    # 로그인확인겸 첫 파란등록버튼 기다리기(관리자로 로그인시)

    사이드바매물요소 = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//ul[contains(@class, 'page-sidebar-menu')]//li[.//span[contains(@class, 'title') and text()='매물']]"))
    )
    if 사이드바매물요소:
        사이드바매물요소.click()    
    else:
        print('사이드바매물요소를 클릭할 수 없습니다.')

    사이드바매물관리요소 = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//li[contains(@class, 'open')]//a[contains(text(), '매물 관리')]"))
    )
    if 사이드바매물관리요소:
        사이드바매물관리요소.click()    
    else:
        print('사이드바매물관리요소를 클릭할 수 없습니다.')    
    # pyautogui.alert('확인')
    
    # 찾는오방번호 = WebDriverWait(driver, 10).until(
    #     EC.presence_of_element_located((By.XPATH, '//tbody[@id="search-items"]/tr[1]/td[2]/a/strong'))
    # ).text   

    
    # # 로그인확인겸 첫 파란등록버튼 기다리기(준회원으로 로그인시)
    # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/div[2]/div/div[1]/div/div/div/div/span[1]/button')))
    원본사진들 = [] #원본사진파일들을 담을 빈 리스트
    변환폴더생성일모음 = [] #변환된 사진폴더의 년월일을 담을 빈 리스트    
    try:
        #ftp서버에 DB연결
        conn = pymysql.connect(host='obangkr.cafe24.com', user='obangkr', password='Ddhqkd!1', charset='utf8')
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('USE obangkr;')      
        
        #물건의 원본사진폴더에 이미지가 존재하는지
        main_dir = 'Z:\\업무자료\\4사진자료&이미지자료(외부유출금지)\\1주거용물건, 상업용물건\\'
        path_dir = main_dir + data['folderPath'] #'경기도\\오산시\\궐동\\654-9\\썬플라워\\1층\\1층'
        print("path_dir:", path_dir)
        
        file_list = os.listdir(path_dir)   
        print("file_list:", file_list)

        for filename in file_list:
            # 파일 확장자를 소문자로 변환하여 비교
            if filename.lower().endswith(('.jpeg', '.gif', '.png', '.jpg')):
                원본사진들.append(filename)   
            if "output" in filename: 변환폴더생성일모음.append(filename.split('output')[1])  
        print("원본사진들:", 원본사진들) 
        
        # #변환된 사진폴더의 생성일모음 생성                                
        # for filename in file_list:
        #     if "output" in filename: 변환폴더생성일모음.append(filename.split('output')[1])
            
        #pr_object_img의 output_folder필드에 들어갈 값 지정
        output_folder = max(변환폴더생성일모음)
        print("원본사진개수:", len(원본사진들),"변환된 폴더개수:", len(변환폴더생성일모음)," output_folder:", output_folder)      
        
        if len(원본사진들) == 0 and len(변환폴더생성일모음) == 0: #물건의 원본사진도 없고 변환된 사진도 없음
            print("원본사진폴더에 이미지 없음")
            # driver.execute_script('document.getElementById("is_speed").checked = true') #급매체크
            pass
        else: #원본사진폴더에 이미지 존재=>pr_object의 object_ori_img필드값을 'Y'로 변경
            print("변환된 이미지 존재")  
            if len(변환폴더생성일모음)==0:
                pyautogui.alert("output폴더를 확인해주세요!! 확인을 누르면 계속 진행합니다.")
            최근변환사진경로 = path_dir + "/output" + max(변환폴더생성일모음) # 제일 큰 output찾기

            최근변환사진모음 = [] #변환된 최근사진을 담을 빈 리스트

            for file in os.listdir(최근변환사진경로):
                if file.lower().endswith(('.jpeg', '.gif', '.png', '.jpg')):
                    최근변환사진모음.append(file)
            
            최근변환사진모음 = sorted(최근변환사진모음)
            # pyautogui.alert("\n".join(최근변환사진모음),"최근변환사진 목록(오름차순)")                        

            query = f'SELECT object_ori_img FROM pr_object WHERE object_code_new="{object_code_new}"'
            cursor.execute(query)
            result = cursor.fetchone() 
            object_ori_img = result['object_ori_img']
            print("result:",result)
            # print("object_ori_img:",object_ori_img)
            if result and object_ori_img == 'N':
                # print("object_ori_img 값은 'N'입니다.") 
                update_query = f'UPDATE pr_object SET object_ori_img="Y" WHERE object_code_new="{object_code_new}"'
                cursor.execute(update_query)
                conn.commit()
                print("object_ori_img 값을 'Y'로 업데이트 완료!!") 
            # ftp_directory = 'web/object/'+object_code_new
            ftp_directory = 'img/web/object/object_img/'+object_info_code

            with FTP('obangkr.cafe24.com', 'obangkr', 'Ddhqkd!1') as ftp:
                if not is_directory_exists(ftp, ftp_directory):
                    print("ftp에 이미지저장 디렉토리생성:", ftp_directory)  
                    ftp.mkd(ftp_directory)     
                else:
                    print("ftp에 이미지가 저장된 디렉토리가 이미 존재합니다.")  
                    # remove_existing_files(ftp, ftp_directory) # 기존 파일 제거                                                  

            
            #매물의 기존 대표이미지정보 삭제후 최신정보 저장 
            query = f'DELETE FROM pr_object_img WHERE object_info_code="{object_info_code}"'
            cursor.execute(query)
            
            #1. 저용량변환사진FTP업로드()
            small_file = 가장용량이작은파일찾기(최근변환사진모음, 최근변환사진경로)
            small_file_path = os.path.join(최근변환사진경로, small_file) # 파일 경로를 생성    
            # FTP 연결 및 로그인
            with FTP('obangkr.cafe24.com', 'obangkr', 'Ddhqkd!1') as ftp:
                # 최소 용량의 파일을 FTP 서버에 업로드
                with open(small_file_path, 'rb') as file:
                    # 현재 날짜와 시간을 얻음
                    current_date = datetime.date.today().strftime("%Y-%m-%d")
                    current_time = datetime.datetime.now().time().strftime("%H:%M:%S")
                    # FTP 서버에 파일 업로드
                    ftp.cwd(ftp_directory)
                    ftp.storbinary(f'STOR {small_file}', file)
                    # 데이터베이스에 파일 정보 저장
                    query = f'''
                        INSERT INTO pr_object_img 
                        (object_code_new, object_info_code, output_folder, oimg_name, oimg_index, oimg_wdate, oimg_wtime, oimg_del) 
                        VALUES 
                        ("{object_code_new}", "{object_info_code}", "{max(변환폴더생성일모음)}", "{small_file}", "1", "{current_date}", "{current_time}", "N")
                    '''
                    cursor.execute(query)
                    conn.commit()
                    ftp.close()
                

            # 파일 업로드가 성공적으로 완료되었다는 메시지 출력
            print(f'File "{small_file}" has been successfully uploaded')

    except Exception as e: 
        print("폴더 오류", str(e))
        # driver.execute_script('document.getElementById("is_speed").checked = true')
        errarr.append("폴더 오류")
        pass    

    # print("object_info_code:",object_info_code)
    




    sele = {
    '원룸': [11, ['오픈형', '분리형', '통1.5룸', '1.5룸', '1.8룸']],
    '투룸/쓰리룸+': [12, ['투룸', '쓰리룸+']],
    '상가/사무실': [16, ['상가', '사무실']],
    '오피스텔': [13, []],
    '아파트': [14, []],
    '주택/고급빌라': [15, []],
    '공장/창고': [17, []],
    '토지': [18, []],
    '통건물': [19, ['상업용건물','상가주택','다가구주택','다세대주택','오피스텔','단독주택','도시형생활주택','주상복합건물','지식산업센터',]],
    }







    # #테스트용--------------------------------------------------------------------------------------
    # keywords = [location_dongli, location_building]
    # if tr_target == '층호수':
    #     keywords.append('location_room')
    # print("keywords:",keywords)
    # try:
    #     time.sleep(0.2)
    #     rows = driver.find_elements(By.CSS_SELECTOR, '#search-items tr.admin_column')
    #     print("rows 개수:"+str(len(rows)))
    #     if len(rows) == 0:
    #         pyautogui.alert("리스트의 목록개수 0??")
    # except Exception as e:
    #     print("rows 조회에러:", e)
    # # for row in rows:
    # for i in range(len(rows)):
    #     try:
    #         # 각 요소에 대해 명시적 대기 적용
    #         # 매번 새로 요소를 찾아서 작업
    #         row = driver.find_elements(By.CSS_SELECTOR, '#search-items tr.admin_column')[i]                            
    #         time.sleep(0.5)
    #         print('--')
    #         row구조 = driver.execute_script("return arguments[0].outerHTML;", row)
    #         # row구조 = row.get_attribute('outerHTML')
    #         # pyautogui.alert(f"row구조:{row구조}")
    #         # 주소가 포함된 'help-block' 클래스를 가진 div 찾기
    #         address_div = row.find_element(By.CLASS_NAME, 'help-block')
    #         print(f"0")
    #         address_text = address_div.text.strip()  # 주소 텍스트 추출            
    #         print(f"모든 키워드가 포함된 텍스트: {address_text}")
    #         # 모든 키워드가 텍스트에 포함되어 있는지 확인
    #         if all(keyword in address_text for keyword in keywords):
    #             print(f"모든 키워드포함")
    #             # tr의 두 번째 td 안에 있는 <strong> 태그의 텍스트 추출
    #             second_td = row.find_elements(By.TAG_NAME, 'td')[1]  # 두 번째 td
    #             print(f"1")
    #             strong_tag = second_td.find_element(By.TAG_NAME, 'strong')  # <strong> 태그 찾기
    #             print(f"2")
    #             등록된오방번호 = strong_tag.text  # 텍스트 저장
    #             print(f"등록된오방번호: {등록된오방번호}")    
    #             break            
    #         else:
    #             print(f"키워드가 누락된 텍스트: {address_text}")
    #     # except IndexError:
    #     #     # 만약 td나 div가 없으면 예외 발생을 방지하고 넘어감
    #     #     print("해당 요소가 없습니다.")    
    #     except Exception as e:
    #         print("row 처리 중 오류:", e)                    
    # pyautogui.alert(', '.join(keywords)+f"\n\n등록된오방번호:{등록된오방번호}","찾는 keywords:") 




    if obang_code == '' :
        print('오방 신규등록과정 시작')
        #jibun 데이터가 번지수 형식일 경우
        if re.match('^[0-9-]+$', data['landData'][0]['land_jibun']) or re.match('^산[0-9-]+$', data['landData'][0]['land_jibun']):
            print('지번형식의 주소입니다.')
            # driver.find_element(By.XPATH, '//*[@id="drop_nav"]').click()
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="search_option"]/th[9]/div[1]/ul/li[2]/a'))
            )
            driver.execute_script('view_display("local")')
            # 검색필터를 '전체'에서 '상세주소'로 변경
            print('1')
            driver.find_element(By.XPATH, '//*[@id="keyword_button"]').click()
            print('2')
            # WebDriverWait(driver, 10).until(
            #     EC.element_to_be_clickable((By.XPATH, '//*[@id="keyword_layer"]//label[text()="상세주소"]/preceding-sibling::div'))
            # ).click()
            # JavaScript를 사용하여 '상세주소' 체크박스 클릭
            javascript = """
            var checkboxes = document.querySelectorAll('input[name="keyword_type[]"]');
            for (var i = 0; i < checkboxes.length; i++) {
                if (checkboxes[i].value === 'address') {
                    var label = checkboxes[i].nextSibling; // iCheck를 사용하는 경우 label이나 다른 요소를 클릭해야 할 수 있음
                    label.click(); // 또는 해당 요소를 찾아 클릭하는 로직을 추가
                    break;
                }
            }
            """
            driver.execute_script(javascript)
            # #드롭다운된 체크박스리스트 닫기버튼 보일때까지 대기
            # WebDriverWait(driver, 10).until(
            #     EC.presence_of_element_located((By.XPATH, '//*[@id="keyword_layer"]/div'))
            # )
            #드롭다운된 체크박스리스트 닫기
            driver.execute_script('keyword_layer()')
            # pyautogui.alert("검색필터 계속진행?")
            if tr_target == '층호수':
                # driver.find_element(By.XPATH, '//*[@id="keyword"]').send_keys(location_room[:-1].replace(" ", "")) #호실명의 마지막글자를 제거한 문자(공백제거)를 검색어로 입력
                driver.find_element(By.XPATH, '//*[@id="keyword"]').send_keys(location_room)
            elif tr_target == '건물':
                driver.find_element(By.XPATH, '//*[@id="search_option"]/th[5]/div/button').click() #매물종류버튼 클릭
                if object_type == '공업용':
                    driver.find_element(By.XPATH, '//*[@id="search_option"]/th[5]/div/ul/li[16]/a/label').click() #공장/창고 체크
                else:
                    driver.find_element(By.XPATH, '//*[@id="search_option"]/th[5]/div/ul/li[18]/a/label').click() #통건물 체크
                # pyautogui.alert("통건물 계속진행?")
            driver.find_element(By.XPATH, '//*[@id="sido"]').send_keys(location_do)
            # time.sleep(0.5)
            driver.find_element(By.XPATH, '//*[@id="gugun"]').send_keys(location_si)
            # time.sleep(0.5)
            driver.find_element(By.XPATH, '//*[@id="dong"]').send_keys(location_dong)
            # lijibun = location_lijibun.replace(" ", "") #리+지번 공백제거
            driver.find_element(By.XPATH, '//*[@id="bunzi_start"]').send_keys(location_lijibun)
            # pyautogui.alert("검색어가 정상적으로 입력됨?")
        #jibun데이터가 번지수 형식이 아닐경우
        else:
            print('직접입력형식의 주소입니다.')
            driver.find_element(By.XPATH, '//*[@id="keyword"]').send_keys(data['landData'][0]['land_jibun']) #검색어입력창에 입력
            driver.find_element(By.XPATH, '//*[@id="go_keyword"]').click() #돋보기 클릭
        # print("오류발생 시작예상지점")
        # result = pyautogui.alert(location_detail+'\n\n 매물등록을 진행합니다.\n\n원치 않으시면 창을 닫아주세요~')
        # result = '예'


        try:
            # '검색 매물 수 : 0건' 텍스트가 있는 요소가 나타날 때까지 최대 3초간 기다림
            검색매물수0건 = WebDriverWait(driver, 3).until(
                EC.text_to_be_present_in_element((By.XPATH, '//*[@id="search_form"]/div/div[5]/span'), '검색 매물 수 : 0건')
            )
            print("조건에 해당하는 텍스트가 나타났습니다.")
        except TimeoutException:
            print("3초내에 조건에 해당하는 텍스트가 나타나지 않았습니다.")
            검색된첫번째매물번호 = driver.find_element(By.XPATH, '//*[@id="search-items"]/tr[1]/td[2]/a/strong').text
            pyautogui.alert(f'새홈[{object_code_new}] '+location_detail+f'\n\n등록된 매물[{검색된첫번째매물번호}]이 존재합니다. 신규등록을 종료합니다.')
            driver.quit()  # 브라우저 닫기
            return  
                    
        if 검색매물수0건:
            print('검색 매물 수 : 0건')
            # pyautogui.alert(location_detail+'\n\n 매물등록을 진행합니다.\n\n원치 않으시면 창을 닫아주세요~')
            # 확인후 이동
            driver.get('https://osanbang.com/adminproduct/add?category_id') #매물등록페이지 열기
            print("299 ok?")

            # 이동한 페이지 기다리기 + 불러오기 나올경우 취소
            WebDriverWait(driver, 5)
            try:
                driver.find_element(By.XPATH, '//*[@id="temp_check_dialog"]/div/div[2]/div/button[2]').click()
            except:
                pass

            # Alert 처리
            try:
                alert = WebDriverWait(driver, 2).until(EC.alert_is_present())
                alert_text = alert.text
                alert.accept()
            except:
                pass

            #
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/div[2]/div/div/div/h3')))

            print("320 pass")

            # 위치정보


            # 주소찾기로 주소선택
            driver.find_element(By.XPATH, '//*[@id="product_form"]/div[1]/div[1]/div[2]/div/div[1]/div[1]/div[2]/button').click() #지역 드롭다운버튼 클릭

            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="label_text"]')))
            time.sleep(0.2)
            # pyautogui.alert("시도:"+location_do+" 구군:"+location_si+" 읍면동:"+location_dong)
            sidos = driver.find_elements(By.XPATH, '//*[@id="sido_section"]/ul/li/div/button')
            for sido in sidos:
                if sido.text == location_do:
                    sido.click()
                    time.sleep(0.1)
                    guguns = driver.find_elements(By.XPATH, '//*[@id="gugun_section"]/ul/li/div/button')
                    for gugun in guguns:
                        if gugun.text == 그룹별명칭변환('구군', location_si):
                            gugun.click()
                            time.sleep(0.1)
                            dongs = driver.find_elements(By.XPATH, '//*[@id="dong_section"]/ul/li/div/button')
                            for dong in dongs:
                                if dong.text == 그룹별명칭변환('읍면동', location_dong):
                                    dong.click()
                                    break
            
            time.sleep(0.1)
            # pyautogui.alert(' go? ')
            if re.match('^[0-9-]+$', data['landData'][0]['land_jibun']) or re.match('^산[0-9-]+$', data['landData'][0]['land_jibun']):
                print("location_lijibun:", location_lijibun)
                driver.find_element(By.XPATH, '//*[@id="address"]').send_keys(location_lijibun) # 상세주소 1
                driver.find_element(By.XPATH, '//*[@id="get_coord"]').click() # 위치검색 클릭
            print("location_detail:", location_detail)    
            driver.find_element(By.XPATH, '//*[@id="address_unit"]').send_keys(location_detail) # 상세주소 2
            
            # pyautogui.alert('지번과 지도위치 정상인지 확인필요')
            
            # sele = {
            # '원룸': [11, ['오픈형', '분리형', '통1.5룸', '1.5룸', '1.8룸']],
            # '투룸/쓰리룸+': [12, ['투룸', '쓰리룸+']],
            # '상가/사무실': [16, ['상가', '사무실']],
            # '오피스텔': [13, []],
            # '아파트': [14, []],
            # '주택/고급빌라': [15, []],
            # '공장/창고': [17, []],
            # '토지': [18, []],
            # '통건물': [19, ['상업용건물','상가주택','다가구주택','다세대주택','오피스텔','단독주택','도시형생활주택','주상복합건물','지식산업센터',]],
            # }

            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="product_form"]/div[1]/div[2]/div[2]/div[1]/div[2]/div[2]/div')))
#매물정보
            #매물종류
            print("물건종류:", obinfo_type)
            # for 매물별라디오태그요소 in driver.find_elements(By.NAME, 'category'):
            #     # print(f"F매물별라디오태그요소 html:\n{매물별라디오태그요소.get_attribute('outerHTML')}")
            #     # print("매물별라디오태그요소:"+매물별라디오태그요소.text)
            #     if 매물별라디오태그요소 == obinfo_type:
            #         매물별라디오태그요소.click()    
            if obinfo_type != '':
                driver.find_element(By.ID, f'category_{sele[obinfo_type][0]}').click() #매물종류
                # pyautogui.alert("매물종류 선택 정상?") 
                print("obinfo_type2:", obinfo_type2)
                if len(sele[obinfo_type][1]) != 0: # 소분류
                    for a in driver.find_elements(By.CLASS_NAME, f'main_{sele[obinfo_type][0]}'):
                        print(a.text)
                        if a.text == obinfo_type2: 
                            a.click()   
                # pyautogui.alert("소분류 선택 정상?")
                
            # driver.find_element(By.ID, f'category_{sele["원룸"][0]}').click() # 거래종류
            # 거래종류
            print(f"obang_ttype:{obang_ttype}")
            for a in driver.find_elements(By.XPATH, '//*[@id="product_form"]/div[1]/div[2]/div[2]/div[3]/div[2]/div/div'):
                print(a.text)
                if a.text == obang_ttype: 
                    a.click()
            time.sleep(0.1)
            # pyautogui.alert("거래종류 선택 정상?")
            #매매가
            if driver.find_element(By.XPATH, '//*[@id="sell_price"]').is_displayed() and obinfo_trading !='' : driver.find_element(By.XPATH, '//*[@id="sell_price"]').send_keys(obinfo_trading) 
            
            #융자
            if driver.find_element(By.XPATH, '//*[@id="lease_price"]').is_displayed() and str(object_loan) !='' : driver.find_element(By.XPATH, '//*[@id="lease_price"]').send_keys(str(building_loan)) 
            #총보증금
            if driver.find_element(By.XPATH, '//*[@id="sell_price_area"]/span[2]/input').is_displayed() and str(sum_deposit) !='' : driver.find_element(By.XPATH, '//*[@id="sell_price_area"]/span[2]/input').send_keys(str(sum_deposit))
            #총월세
            if driver.find_element(By.XPATH, '//*[@id="sell_price_area"]/span[3]/input').is_displayed() and str(sum_rent) !='' : driver.find_element(By.XPATH, '//*[@id="sell_price_area"]/span[3]/input').send_keys(str(sum_rent))
            
            
            print(f"obinfo_deposit1:{obinfo_deposit1} obinfo_rent1:{obinfo_rent1}\nobinfo_deposit2:{obinfo_deposit2} obinfo_rent2:{obinfo_rent2}\nobinfo_deposit3:{obinfo_deposit3} obinfo_rent3:{obinfo_rent3}")
            전세보증금 = ''
            if obinfo_deposit1 != '0' and obinfo_rent1 == '0' : 
                전세보증금 = obinfo_deposit1
            elif obinfo_deposit2 != '0' and obinfo_rent2 == '0' :
                전세보증금 = obinfo_deposit2
            elif obinfo_deposit3 != '0' and obinfo_rent3 == '0' :
                전세보증금 = obinfo_deposit3
            print(f"전세보증금:{전세보증금}")
            #전세의 보증금1
            if driver.find_element(By.XPATH, '//*[@id="full_price_area"]').is_displayed(): # and 전세보증금 != ''
                driver.find_element(By.XPATH, '//*[@id="full_rent_price"]').send_keys(전세보증금) 
            else:
                print("전세입력창이 보이지 않음")
            # pyautogui.alert(f"전세보증금:{전세보증금}")
            #월세의 보증금1
            if driver.find_element(By.XPATH, '//*[@id="monthly_rent_deposit"]').is_displayed(): driver.find_element(By.XPATH, '//*[@id="monthly_rent_deposit"]').send_keys(obinfo_deposit1) 
            #월세1
            if driver.find_element(By.XPATH, '//*[@id="monthly_rent_price"]').is_displayed(): driver.find_element(By.XPATH, '//*[@id="monthly_rent_price"]').send_keys(obinfo_rent1) 
            # # 관리내역
            # 관리내역s = driver.find_elements(By.XPATH, '//*[@id="mgr_include_checkbox"]/input')
            # #물건의 관리비포함내역
            # 관리내역ex = basic_mlist.split(',')
            # # '일반관리' 항목을 리스트의 끝에 추가
            # 관리내역ex.append('일반관리')
            # try:
            #     for item in 관리내역ex:
            #         for 관리내역 in 관리내역s:
            #             if item in 관리내역.get_attribute("value"):
            #                 관리내역.click()
            #                 break
            # except:
            #     print(관리내역ex)

            print("223 pass")
            # 비공개 선택
            driver.find_element(By.XPATH, '//*[@id="product_form"]/div[1]/div[2]/div[2]/div[7]/div/div/label[2]').click()

            # 기본정보
            if tr_target == '층호수':
                if data['writeData']['manager'] == '별도' and data['writeData']['mmoney'] != '':
                    driver.find_element(By.XPATH, '//*[@id="mgr_price"]').send_keys(basic_mmoney) # 관리비
                if driver.find_element(By.XPATH, '//*[@id="real_area"]').is_displayed() :driver.find_element(By.XPATH, '//*[@id="real_area"]').send_keys(basic_area1) # 실면적
            
                # if obinfo_type != '원룸' and obinfo_type != '투룸/쓰리룸+' and obinfo_type != '토지' and obinfo_type != '통건물' : driver.find_element(By.XPATH, '//*[@id="law_area"]').send_keys(basic_area2) # 공급면적
                if driver.find_element(By.XPATH, '//*[@id="law_area"]').is_displayed() : driver.find_element(By.XPATH, '//*[@id="law_area"]').send_keys(basic_area2) # 공급면적        
                
                if obinfo_type == '투룸/쓰리룸+' or obinfo_type == '아파트' or obinfo_type == '주택/고급빌라' :
                    # print("basic_rcount:"+basic_rcount, type(basic_rcount))  

                    if basic_rcount != '': Select(driver.find_element(By.XPATH, '//*[@id="bedcnt"]')).select_by_value(basic_rcount) #침실
                    Select(driver.find_element(By.XPATH, '//*[@id="bathcnt"]')).select_by_value(basic_bcount) if basic_bcount != ''else Select(driver.find_element(By.XPATH, '//*[@id="bathcnt"]')).select_by_value('1') #욕실
                print("basic_floor:", basic_floor)
                # pyautogui.alert("stop")
                if  obinfo_type == '공장/창고':
                    driver.find_element(By.XPATH, '//*[@id="total_floor"]').send_keys(basic_floor) # 지상층
                else:
                    driver.find_element(By.XPATH, '//*[@id="current_floor"]').send_keys(basic_floor) # 해당층
                    driver.find_element(By.XPATH, '//*[@id="total_floor"]').send_keys(basic_totflr) # 전체층
                
            if tr_target == '건물':
                print("건물관련 면적, 층수입력")
                #대지면적
                driver.find_element(By.XPATH, '//*[@id="land_area"]').send_keys(land_totarea) #대지면적
                #건축면적
                driver.find_element(By.XPATH, '//*[@id="bld_area"]').send_keys(building_archarea) #건축면적
                #연면적
                driver.find_element(By.XPATH, '//*[@id="bld_sum_area"]').send_keys(building_totarea) #연면적
                if object_type == '주거용':
                    #지하층
                    driver.find_element(By.XPATH, '//*[@id="current_floor"]').send_keys(building_ugrndflr) #지하층수
                    #지상층
                    driver.find_element(By.XPATH, '//*[@id="total_floor"]').send_keys(building_grndflr) #지상층수   
                elif object_type == '공업용':
                    #전기
                    if building_bolt: driver.find_element(By.XPATH, '//*[@id="factory_section"]/div[2]/input').send_keys(building_bolt)
                    print(f"전기: {building_bolt}KW")
                    #층고(높이)
                    if building_height: driver.find_element(By.XPATH, '//*[@id="add_section_item"]/div[1]/div[2]/input').send_keys(building_height)
                    print(f"층고(높이): {building_height}M")
            if tr_target == '토지':
                #대지면적
                driver.find_element(By.XPATH, '//*[@id="land_area"]').send_keys(land_totarea) #대지면적                

            if tr_target != '토지':
                print("입주일:", add_rdate)  
                print("준공일:", add_usedate)    
            # driver.find_element(By.XPATH, '//*[@id="enter_year"]').send_keys('즉시입주') # 입주일
            # pyautogui.alert("준공일 차례")
            if obinfo_type not in ['상가/사무실','토지','공장/창고']:
                print("난방방식:") 
                if driver.find_element(By.XPATH, '//*[@id="heating"]'):driver.find_element(By.XPATH, '//*[@id="heating"]').send_keys("개별가스난방") # 난방                
                if driver.find_element(By.XPATH, '//*[@name="build_year"]').is_displayed() :driver.find_element(By.XPATH, '//*[@name="build_year"]').send_keys(add_usedate) # 준공일
                
            print("비밀메모:", basic_secret)    
            driver.find_element(By.XPATH, '//*[@id="info_base"]/div[2]/div[13]/div[2]/textarea').send_keys(basic_secret) 
            #급매체크
            driver.execute_script('document.getElementById("is_speed").checked = true')
        # else:
        #     print(검색매물수.text) 
        #     pyautogui.alert(location_detail+f'\n\n등록된 매물이 존재합니다. 신규등록을 종료합니다.')
        #     driver.quit()  # 브라우저 닫기
        #     return  

















    else:
        print('오방('+obang_code+') 등록수정과정 시작')
        try:
            # import datetime

            # WebDriverWait(driver, 10).until(EC.element_to_be_clickable(By.CSS_SELECTOR, "#search_id")).clear() #매물번호 입력창의 입력값 초기화
            driver.implicitly_wait(10)
            driver.find_element(By.CSS_SELECTOR, "#search_id").clear() 
            driver.find_element(By.CSS_SELECTOR, "#search_id").send_keys(obang_code) #매물번호입력창에 매물번호 입력
            driver.find_element(By.CSS_SELECTOR, "#admin_member_id > option:nth-child(1)").click() #담당자를 직원별로 선택
            driver.find_element(By.CSS_SELECTOR, "#go_keyword").click() #검색버튼(돋보기) 클릭
            # WebDriverWait(driver, 10).until(EC.presence_of_element_located(By.CSS_SELECTOR, "#tr_20052 > td:nth-child(14) > div:nth-child(1)"))
            # time.sleep(2)

            검색매물수 = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="search_form"]/div/div[5]/span')))
            if 검색매물수.text == '검색 매물 수 : 0건':
                # 등록된 오방번호로 오방매물이 없을 경우
                print('검색 매물 수 : 0건')
                pyautogui.alert(f'삭제된 매물번호[{obang_code}]입니다. 수정등록을 종료합니다.')
                driver.quit()  # 브라우저 닫기
                return
            else:
                print('검색 매물 수 :'+검색매물수.text+'건') 
            

            #업데이트 실행

            #공개전환
            공개모드요소 = driver.find_element(By.XPATH, f'//*[@id="tr_{obang_code}"]/td[3]/div/label')
            공개모드상태 = 공개모드요소.text #공개:on / 비공개:off
            if 공개모드상태 == 'off':
                공개모드요소.click() #비공개상태 클릭하여 공개로 전환
            # pyautogui.alert("공개모드상태:"+공개모드상태)

            def 관리내항목확인():
                driver.find_element(By.CSS_SELECTOR, f'#tr_{obang_code} > td:nth-child(14) > div:nth-child(1)').click() #관리 클릭
                
                # id="search-items"인 tbody 안에 첫 번째 tr의 14번째 td를 찾기
                관리_td = driver.find_element(By.XPATH, '//tbody[@id="search-items"]/tr[1]/td[14]')
                # 해당 td 안의 모든 li 태그 내의 a 태그를 찾기
                관리내항목 = 관리_td.find_elements(By.XPATH, './/li/a')
                수정_있음 = False  # "수정" 텍스트를 찾았는지 여부를 추적하는 플래그
                완료해제_있음 = False  # "거래완료 해제" 텍스트를 찾았는지 여부를 추적하는 플래그
                관리내수정위치 = None
                관리내해제위치 = None
                for 항목 in 관리내항목:
                    print(f'관리 항목: {항목.text}')
                    if "수정" in 항목.text:
                        수정_있음 = True
                        관리내수정위치 = 항목
                        # print(f'찾은 항목: {항목.text}')
                    if "거래완료 해제" in 항목.text:
                        완료해제_있음 = True
                        관리내해제위치 = 항목
                        # print(f'찾은 항목: {항목.text}')
                return 수정_있음,관리내수정위치,완료해제_있음,관리내해제위치
            
            수정_있음,관리내수정위치,완료해제_있음,관리내해제위치 = 관리내항목확인()

            if 완료해제_있음:
                관리내해제위치.click() # 거래완료해제시 목록이 초기화됨
                def 알림창끄기():
                    try:
                        WebDriverWait(driver, 3).until(EC.alert_is_present())  # 최대 3초 대기
                        alert = driver.switch_to.alert
                        print(f"📢 확인창 내용: {alert.text}")
                        alert.accept()  # "확인" 클릭
                        print("✅ '확인' 버튼 클릭 완료")
                    except:
                        print("⏩ 확인창 없음 (confirm 창 미출현)")                    
                알림창끄기() #확인메세지창이 뜨면 닫기
                driver.find_element(By.CSS_SELECTOR, "#search_id").send_keys(obang_code) #매물번호입력창에 매물번호 입력

                수정_있음,관리내수정위치,완료해제_있음,관리내해제위치 = 관리내항목확인()
                # driver.find_element(By.CSS_SELECTOR, f'#tr_{obang_code} > td:nth-child(14) > div.dropdown.open > ul > li:nth-child(13)').click() #수정 클릭   
            # pyautogui.alert(f"{obang_code} 거래완료 해제 확인")   
                
            if not 수정_있음:
                print("텍스트 '수정'을 포함하는 항목이 없습니다.")
                pyautogui.alert("등록된 매물의 담당자를 확인해주세요~")
                driver.quit()
                return
            else:
                try:        
                    관리내수정위치.click() #수정 클릭
                except Exception as e:
                    print(f"⚠️ 수정버튼 클릭 중 오류: {e}")
                    최상단알림창(f"오류로 수정버튼이 클릭되지 않았습니다.\n\n{e}")
                    driver.close()          
    

            # try:        
            #     관리_수정항목 = WebDriverWait(driver, 10).until(
            #         EC.element_to_be_clickable((By.CSS_SELECTOR, f'#tr_{obang_code} > td:nth-child(14) > div.dropdown.open > ul > li:nth-child(1)'))
            #     )
            #     time.sleep(0.3)
            #     관리_수정항목.click() #수정 클릭
            # except Exception as e:
            #     print(f"⚠️ 수정버튼 클릭 중 오류: {e}")
            #     최상단알림창(f"오류로 수정버튼이 클릭되지 않았습니다.\n\n{e}")
            #     driver.close()  
            print("6 완료")
            if re.match('^[0-9-]+$', data['landData'][0]['land_jibun']) or re.match('^산[0-9-]+$', data['landData'][0]['land_jibun']):
                print("location_lijibun:", location_lijibun)
                driver.find_element(By.XPATH, '//*[@id="address"]').clear() # 상세주소 1 초기화
                driver.find_element(By.XPATH, '//*[@id="address"]').send_keys(location_lijibun) # 상세주소 1
                driver.find_element(By.XPATH, '//*[@id="get_coord"]').click() # 위치검색 클릭
            driver.find_element(By.XPATH, '//*[@id="address_unit"]').clear() #상세주소2 초기화
            driver.find_element(By.XPATH, '//*[@id="address_unit"]').send_keys(location_detail) # 상세주소 2

            if group == 'Y': #일괄처리시 주소만 수정하고 저장
                driver.find_element(By.XPATH, '//*[@id="product_form"]/div[7]/button[2]').click() #수정후 최신으로갱신 버튼클릭
                conn.close()  
                cursor.close()
                # driver.close()
                driver.quit()
                print("일괄처리시 수정작업 종료")
                return # 이 부분을 추가하여 함수의 나머지 부분이 실행되지 않도록 합니다.             

            # pyautogui.alert("obang_code:"+obang_code+" 이게 보이면 안돼~~~~~~~~~!!")
            
            #소분류
            if len(sele[obinfo_type][1]) != 0: # 소분류
                print("obinfo_type2:"+obinfo_type2)
                for a in driver.find_elements(By.CLASS_NAME, f'main_{sele[obinfo_type][0]}'):
                    # print(a.text)
                    if a.text == obinfo_type2:
                        # 요소에 "active" 클래스 추가
                        driver.execute_script("arguments[0].classList.add('active');", a)
                        print(a.text + "에 'active' 클래스 추가!!!")
                    else:
                        # 조건에 맞지 않는 요소에서는 "active" 클래스 제거
                        driver.execute_script("arguments[0].classList.remove('active');", a)
                        print(a.text + "에서 'active' 클래스 제거!!!")                    
            # pyautogui.alert("소분류확인")    
            # 거래종류
            print(f"obang_ttype:{obang_ttype}")
            # obang_ttype에 쉼표가 있는지 확인
            if ',' in obang_ttype:
                거래종류값 = '전/월세' if '전세' in obang_ttype and '월세' in obang_ttype else obang_ttype
            else:
                거래종류값 = obang_ttype
            print(f"거래종류값:{거래종류값}")
            # 거래종류 설정
            form_groups = driver.find_elements(By.CLASS_NAME, 'form-group')
            for group in form_groups:
                try:
                    label = group.find_element(By.CLASS_NAME, 'control-label')
                    if '거래종류' in label.text:
                        print("✅ '거래종류' 섹션 찾음")

                        # 거래 버튼 div들 찾기
                        button_divs = group.find_elements(By.XPATH, './/div[contains(@class, "btn-group")]//div[contains(@class, "btn")]')
                        for btn in button_divs:
                            if 거래종류값 in btn.text.strip():
                                print(f"🟢 '{거래종류값}' 버튼 클릭")
                                btn.click()
                                break
                        break
                except Exception as e:
                    print(f"⚠️ 거래종류 설정 중 오류: {e}")
            # pyautogui.alert(f"거래종류값 선택확인:{거래종류값}")   
            # 거래종류값이 '전/월세'일 경우, 전세와 월세를 적절하게 처리
            if 거래종류값 == '전/월세':
                # 전세와 월세에 대한 정보를 쌍으로 처리
                deposit_rent_pairs = [(obinfo_deposit1, obinfo_rent1), (obinfo_deposit2, obinfo_rent2), (obinfo_deposit3, obinfo_rent3)]

                # 첫 번째 월세만을 사용하여 입력하기
                first_deposit = None
                first_rent = None
                for deposit, rent in deposit_rent_pairs:
                    deposit_val = int(deposit or 0)
                    rent_val = int(rent or 0)
                    print(f"============>보증금:{deposit_val}, 월세:{rent_val}")
                    
                    if deposit_val > 0 and rent_val == 0:
                        print(f"전세 입력: {deposit_val}")
                        modify_item(driver, "#full_rent_price", deposit_val)  # 전세 금액 입력란

                    elif rent_val > 0 and first_deposit is None:
                        first_deposit = deposit_val
                        first_rent = rent_val
                        print(f"첫 번째 월세 입력: 보증금 {first_deposit}, 월세 {first_rent}")
                        modify_item(driver, "#monthly_rent_deposit", first_deposit)  # 월세 보증금
                        modify_item(driver, "#monthly_rent_price", first_rent)       # 월세

            else:
                # 거래종류값이 '전/월세'가 아닐 경우, 기존 로직대로 처리
                if obinfo_deposit1 != '':
                    modify_item(driver, "#full_rent_price", obinfo_deposit1)  # 전세금액
                if obinfo_deposit1 != '':
                    modify_item(driver, "#monthly_rent_deposit", obinfo_deposit1)  # 보증금1
                if obinfo_rent1 != '':
                    modify_item(driver, "#monthly_rent_price", obinfo_rent1)  # 월세1
                if obinfo_trading != '':
                    modify_item(driver, "#sell_price", obinfo_trading)  # 매매
            # #전세보증금
            # if obinfo_deposit1 != '' : modify_item(driver, "#full_rent_price", obinfo_deposit1)
            # #보증금1
            # if obinfo_deposit1 != '' : modify_item(driver, "#monthly_rent_deposit", obinfo_deposit1)
            # #월세1
            # if obinfo_rent1 != '' : modify_item(driver, "#monthly_rent_price", obinfo_rent1)
            # #매매
            # # print("obinfo_trading: "+obinfo_trading)
            # if obinfo_trading != '' : modify_item(driver, "#sell_price", obinfo_trading)

            #관리비
            if basic_manager=='별도':
                modify_item(driver, "#mgr_price", basic_mmoney)
            
            if tr_target == '층호수':
                # # 관리내역
                # 관리내역s = driver.find_elements(By.XPATH, '//*[@id="mgr_include_checkbox"]/input')
                # #물건의 관리비포함내역
                # 관리내역ex = basic_mlist.split(',')
                # # '일반관리' 항목을 리스트의 끝에 추가
                # 관리내역ex.append('일반관리')
                # try:
                #     for item in 관리내역ex:
                #         for 관리내역 in 관리내역s:
                #             if item in 관리내역.get_attribute("value"):
                #                 관리내역.click()
                #                 break
                # except:
                #     print(관리내역ex)
                
                # 관리내역 체크박스 요소들을 가져옴
                관리내역s = driver.find_elements(By.XPATH, '//*[@id="mgr_include_checkbox"]/input')
                # 물건의 관리비 포함 내역
                관리내역ex = basic_mlist.split(',')
                # '일반관리' 항목을 리스트의 끝에 추가
                관리내역ex.append('일반관리')
                try:
                    for item in 관리내역ex:
                        for 관리내역 in 관리내역s:
                            체크박스_값 = 관리내역.get_attribute("value")
                            if item == 체크박스_값:
                                # 체크박스가 이미 선택되어 있는지 확인
                                if not 관리내역.is_selected():
                                    관리내역.click()
                                break
                except Exception as e:
                    print(f"Error: {e}")    
                    
                #실면적
                if basic_area1 != '' : modify_item(driver, "#real_area", basic_area1)
                #해당층
                if basic_floor != '' : modify_item(driver, "#current_floor", basic_floor)
                # 입주일
                driver.find_element(By.XPATH, '//*[@id="enter_year"]').clear() 
                #거주자가 있으면 '입주협의', 그외 '즉시입주'
                if '사용' in room_status:
                    입주일값 = '입주협의'
                else:
                    입주일값 = '즉시입주'
                driver.find_element(By.XPATH, '//*[@id="enter_year"]').send_keys(입주일값) 
            #전체층
            # print("전체층: ", type(basic_totflr))
            # pyautogui.alert("전체층: ", basic_totflr)
            # modify_item(driver, "#total_floor", basic_totflr)

            print("비밀메모:", basic_secret)
            # 수정시 비밀메모를 갱신
            secret_box = driver.find_element(By.XPATH, '//*[@id="info_base"]/div[2]/div[13]/div[2]/textarea')
            secret_box.clear()  # 기존 내용을 지우고
            secret_box.send_keys(basic_secret) # 비밀메모
            # # 수정시 비밀메모를 추가
            # # if len(secret_box.text)>0:
            # if len(secret_box.get_attribute("value"))>0:
            #     print("기존비밀메모:"+secret_box.get_attribute("value"))
            #     # 공백 문자 및 특수 문자 정규화 함수
            #     def normalize_space_and_remove_special_chars(s):
            #         normalized = re.sub(r'\s+', ' ', s).strip()  # 모든 공백을 단일 공백으로 변환
            #         return normalized.replace("\ue007", "")  # 특수 문자 제거 
            #     existing_text = normalize_space_and_remove_special_chars(secret_box.get_attribute("value"))  # textarea 값 정규화
            #     basic_secret_normalized = normalize_space_and_remove_special_chars(basic_secret)  # 비밀메모 정규화     
            #     # print("정규화된 기존 비밀메모:", repr(existing_text))
            #     # print("정규화된 새 비밀메모:", repr(basic_secret_normalized))           
            #     if existing_text != basic_secret_normalized:
            #         print("기존메모와 다름")
            #         secret_box.send_keys(Keys.ENTER)
            #     else:
            #         print("기존메모와 같음")
            #         secret_box.clear()  # 기존 내용을 지우고
            #     secret_box.send_keys(basic_secret) # 비밀메모
#################

            


            if tr_target != '토지':
                #옵션선택            
                main_options = main_option.split(',') #옵션을 리스트로 분리
                # print("main_options:", main_options)
                main_importants = main_important.split(',') #옵션을 리스트로 분리
                # print("main_importants:", main_importants)
                # 두 리스트를 집합으로 변환하고 중복을 제거한 후 합친다.
                main_collections = list(set(main_options + main_importants))
                # print("main_collections:",main_collections)
                # 공백 제거
                main_collections = [option.strip() for option in main_collections if option.strip()]
                # print("main_collections:", main_collections)
                given_optionboxs = driver.find_elements(By.XPATH, '//*[@id="option"]/div/label')
                # 변경할 main_options옵션의 매핑 정보를 담은 딕셔너리 생성
                replace_options = {
                    # "벽걸이에어컨": "에어컨",
                    # "전자도어락": "디지털도어락",
                    "가스렌지": "가스레인지",
                    "지상주차장": "주차장",
                    "지하주차장": "주차장",
                    "냉방기": "에어컨",
                    # "천정형에어컨": "에어컨",
                    "건물CCTV": "CCTV",
                    "전자렌지": "전자레인지",
                    "구분공간": "내실",
                    # 필요한 경우 여기에 더 많은 옵션을 추가할 수 있습니다.
                }    
                # 리스트의 각 요소에 대해 딕셔너리를 확인하고, 해당하는 키가 있으면 그 값을 가져와 대체
                updated_options = [replace_options.get(option.strip(), option.strip()) for option in main_collections]
                # if "베란다" in main_options:
                #     updated_options.append("베란다")  # 있다면 updated_options에 추가    
                print("updated_options:",updated_options)
                
                
                given_importantboxs = driver.find_elements(By.XPATH, '//*[@id="info_add"]/div[2]/div[17]/div[2]/div/label')
                # 변경할 main_important옵션의 매핑 정보를 담은 딕셔너리 생성
                replace_importants = {
                    # "벽걸이에어컨": "에어컨",
                    "복층형": "복층형 구조",
                    "무권리": "권리금 무",
                    "전세대출가능": "전세대출",
                    "천정형에어컨": "천정에어컨",
                    "전자렌지": "전자레인지",
                    "지상주차장": "주차장",
                    # 필요한 경우 여기에 더 많은 옵션을 추가할 수 있습니다.
                }    
                # 리스트의 각 요소에 대해 딕셔너리를 확인하고, 해당하는 키가 있으면 그 값을 가져와 대체
                updated_importants = [replace_importants.get(important.strip(), important.strip()) for important in main_collections]
                if "엘리베이터" in updated_options:
                    updated_importants.append("엘리베이터")  # 있다면 updated_importants에 추가    
                if "주차장" in updated_options:
                    updated_importants.append("주차장")  # 있다면 updated_importants에 추가    
                if tr_target == '층호수':
                    if basic_floor == '1':
                        print("1층 추가")
                        updated_importants.append("1층")    
                print("updated_importants:",updated_importants)
                #테마 선택하기
                for given_importantbox in given_importantboxs:
                    input_element = given_importantbox.find_element(By.TAG_NAME, 'input')
                    given_important = given_importantbox.text.strip().replace('\n', ' ').replace('<br>', ' ')  # 텍스트 정리
                    is_active = "active" in given_importantbox.get_attribute("class")
                    # DB에 정의된 테마가 현재 선택되지 않았다면 선택
                    if given_important in updated_importants and not is_active:
                        given_importantbox.click()
                    # 현재 선택된 테마가 DB에 없다면 선택 해제
                    elif given_important not in updated_importants and is_active:
                        given_importantbox.click()
                
                #옵션 선택하기 
                for given_optionbox in given_optionboxs:
                    input_element = given_optionbox.find_element(By.TAG_NAME, 'input')
                    given_option = input_element.get_attribute('value').strip()
                    is_active = "active" in given_optionbox.get_attribute("class")
                    if given_option in updated_options:
                        if not is_active:
                            given_optionbox.click()  # 업데이트할 옵션에 있고 비활성화되어 있으면 활성화
                    else:
                        if is_active:
                            given_optionbox.click()  # 업데이트할 옵션에 없고 활성화되어 있으면 비활성화

            pass 

#################            
            #설명
            object_detail = '[ 매 물 기 본 정 보 ]'
            # print("obinfo_trading:"+obinfo_trading, "obinfo_deposit1:"+obinfo_deposit1)        
            
            # if obinfo_trading != '':
            #     object_detail += '<p>' + f'● 매매금액: {숫자한글로금액변환(obinfo_trading)}</p>' 
            #     if sum_deposit == '':
            #         print("보증금이 공백입니다.")
            #     else:
            #         print("보증금이 존재합니다.")
            #     object_detail += ('<p>' + f'● 총보증금: {숫자한글로금액변환(sum_deposit)}</p>') if str(sum_deposit) != '' else '' 
            #     if sum_rent != '':
            #         object_detail += ('<p>' + f'● 총월세: {숫자한글로금액변환(sum_rent)}</p>') if str(sum_rent) != '' else ''             
                 
            # elif obinfo_deposit1 != '':
            #     object_detail += '<p>' + f'● 보증금: {obinfo_deposit1}만원</p>' 
            #     if obinfo_rent1 != '':
            #         object_detail += '<p>' + f'● 월세: {obinfo_rent1}만원</p>'
            #     if basic_manager == '별도':
            #         if basic_mmoney != '':
            #             if float(basic_mmoney) > 0:
            #                 object_detail += '<p>' + f'● 관리비: {basic_mmoney}만원</p>'
                # if premium_exist == '있음' & premium > 0:
                #     object_detail += f'● 권리금: {premium}만원'
            print("확인2")   
            if object_type == '주거용' and tr_target == '층호수':
                object_detail += (('<p>' + f'● 방: {int(float(basic_rcount))}개')+(f' / 욕실:{basic_bcount}개</p>' if float(basic_rcount) > 0 else '')) if float(basic_rcount) > 0 else ''
            else:
                if tr_target == '건물':
                    object_detail += ('<p>' + f'● 총층: {str(building_grndflr-building_ugrndflr)}층 (지상{str(building_grndflr)}층 / 지하{str(building_ugrndflr)}층)</p>') if int(building_grndflr-building_ugrndflr) > 0 else ''
                elif tr_target == '층호수':
                    if main_area != '':
                        object_detail += ('<p>' + f'● 면적: {main_area}㎡ (약{main_area_pyeong}평)</p>') if float(main_area) > 0 else ''
            
            object_detail += ('<p>' + f'● 건물옵션:{building_options}</p>') if (building_options != '' and tr_target != '토지') else ''
            if tr_target == '층호수':
                object_detail += ('<p>' + f'● 호실옵션:{room_options}</p>') if (room_options != '' and tr_target == '층호수') else ''
            # object_detail += '<p>' + f'● 위치: </p>'
            if I_memo != '':
                object_detail += '<p>' + '<br>' + '[ 매 물 주 요 특 징 ]</p>'
                object_detail += '<p>' + I_memo + '</p>'
            # object_detail += '<p>' + I_memo + '</p>'
            
            print("object_detail: " + object_detail)
            detail = ''
            # detail += '빠른 상담받는 법 ☞ "오방"사이트에서 매물번호가 "' + obang_code + '"인 매물을 보고 문의주셨다고 말씀해주세요~!!' + '<br>'
            # detail += '<br>' + '📋상세정보'
            detail += '<p>' + object_detail + '<br></p>'
            detail += '<p>' + '----------------------------------------------------------------------------------------------</p>'
            detail += '<p>' + '◈아직 등록되지 않은 매물도 다수 보유중이니 더 많은 매물을 안내받길 원하신다면 문의주시기 바랍니다.</p>'
            detail += '<p>' + '◈편하게 연락 주시고 홈페이지도 방문해보세요!!</p>'
            detail += '<p>' + '※렌트프리, 옵션, 협의사항 등 끝까지 도와드리겠습니다.</p>'
            # detail += '<p>' + '📞010-8631-4392'
            # detail += '<p>' + '📌홈페이지: osanbang.com'
            detail += '<p>' + '----------------------------------------------------------------------------------------------' + '<br></p>'
            # iframe으로 스위치
            iframe = driver.find_element(By.XPATH, '//*[@id="cke_1_contents"]/iframe')
            driver.switch_to.frame(iframe)            
            # 텍스트 영역 찾기 및 텍스트 입력
            text_area = driver.find_element(By.XPATH, '//body')
            
            # 텍스트 영역의 현재 내용 확인 (HTML 태그 제거)
            current_content = text_area.get_attribute('innerHTML').strip()
            # 현재 내용이 비어있는 경우에만 detail 입력
            print("current_content:", current_content)
            # 현재 내용이 <br>만 있거나 비어있는 경우에만 detail 입력
            if current_content == '' or current_content == '<p><br></p>':
                # JavaScript를 사용하여 내용을 직접 설정
                new_content = detail if current_content == '' else current_content + detail
                driver.execute_script("arguments[0].innerHTML = arguments[1];", text_area, new_content)
            # if current_content != '<br>':
            #     text_area.send_keys(detail)  
            # text_area.send_keys(detail)
            
            # iframe에서 스위치 되돌리기
            driver.switch_to.default_content()             

            print("796 변환된폴더개수:", len(변환폴더생성일모음))
            if len(변환폴더생성일모음)>0:
                try:
                    print("변환폴더생성일모음:", 변환폴더생성일모음)     
                    # 최근변환사진경로 = path_dir + "/output" + max(변환폴더생성일모음) # 제일 큰 output찾기

                    # 최근변환사진모음 = [] #변환된 최근사진을 담을 빈 리스트

                    # for file in os.listdir(최근변환사진경로):
                    #     if file.lower().endswith(('.jpeg', '.gif', '.png', '.jpg')):
                    #         최근변환사진모음.append(file)

                    print('586 사진갯수:', len(최근변환사진모음))

                    img_count = len(driver.find_element(By.XPATH, '//*[@id="list"]').find_elements(By.XPATH, './li'))
                    print("현재 오방 등록된 사진수: " , img_count)   
                    if img_count == 0 and len(최근변환사진모음) > 0:  
                        # pyautogui.alert("\n".join(최근변환사진모음),"최근변환사진 목록(오름차순)")              
                        #최근변환된 사진존재시 오방에 등록
                        try:
                            try:
                                filePath = driver.find_element(By.XPATH, '//*[@id="product_form"]/div[1]/div[9]/div[2]/div[1]/div/div').get_attribute("outerHTML").split('<input id="')[1].split('" t')[0]
                            except:
                                filePath = driver.find_element(By.XPATH, '//*[@id="product_form"]/div[2]/div[9]/div[2]/div[1]/div/div').get_attribute("outerHTML").split('<input id="')[1].split('" t')[0]
                            index = 0
                            for photo in 최근변환사진모음:
                                index += 1
                                file_path = 최근변환사진경로 + '/' + photo
                                driver.find_element(By.ID, filePath).send_keys(file_path)  
                            driver.execute_script('document.getElementById("is_speed").checked = false')
                            print("오방에 사진업로드 성공후 급매해제")
                        except Exception as e:
                            print("오방에 사진업로드 오류", str(e))
                            driver.execute_script('document.getElementById("is_speed").checked = true')


                    #     print('사진 신규등록과정'+str(index)+' 통과')

                    
                except Exception as e: 
                    print("사진 오류", str(e))
                    # time.sleep(1)
                    # driver.execute_script('return document.getElementById("is_speed").click()')
                    # driver.execute_script('document.getElementById("is_speed").checked = true')
                    print("급매 ㅇㅋ?")
                    pass
            else:
                print("677 변환된 폴더없음")

            # conn.close()
            # ftp.close()
            # cursor.close()
                    
            #오방에 등록된 사진 확인
            print("오방에 등록된 사진개수:",len(driver.find_element(By.XPATH, '//*[@id="list"]').find_elements(By.XPATH, './li')))
            if len(driver.find_element(By.XPATH, '//*[@id="list"]').find_elements(By.XPATH, './li')) == 0:
                print("오방에 등록된 사진 없음")
                # #최근변환된 사진존재시 오방에 등록
                # filePath = driver.find_element(By.XPATH, '//*[@id="product_form"]/div[1]/div[9]/div[2]/div[1]/div/div').get_attribute("outerHTML").split('<input id="')[1].split('" t')[0]
                # # filePath = driver.find_element(By.XPATH, '//*[@id="product_form"]/div[2]/div[9]/div[2]/div[1]/div/div').get_attribute("outerHTML").split('<input id="')[1].split('" t')[0]
                # index = 0
                # for photo in 최근변환사진모음:
                #     index += 1
                #     file_path = path + '/' + photo
                #     driver.find_element(By.ID, filePath).send_keys(file_path)    
                    
                #물건사진 폴더열기
                main_dir = 'Z:\\업무자료\\4사진자료&이미지자료(외부유출금지)\\1주거용물건, 상업용물건\\'
                path_dir = main_dir + data['folderPath'] #'경기도\\오산시\\궐동\\654-9\\썬플라워\\1층\\1층'
                print(path_dir)
                #물건폴더에 원본사진 존재유무
                if len(원본사진들) > 0: #물건의 원본사진없음
                    try:
                        os.startfile(path_dir)
                        print('폴더열기 성공') 
                    except:
                        print('폴더열기 에러(해당폴더 없음)')   
                else:
                    print("원본사진X => 물건사진폴더 미개봉")      
                driver.execute_script('document.getElementById("is_speed").checked = true')
            else:
                print("오방에 등록된 사진 있음")
                driver.execute_script('document.getElementById("is_speed").checked = false') #급매해제
                
            print("오방등록수정과정 정상종료")   

        except Exception as e:
            print("에러 발생1:", str(e))
            pyautogui.alert("에러 발생1:"+ str(e))
            print(f"{obang_code}업데이트 안됨")
            # conn.close()  
            # cursor.close()            
            # driver.quit()

        
    # time.sleep(60)
    
    # 공통적용사항
    print("공통적용사항시작--------------------------------------------------------")
    # import os


    
    if obang_code == '' :  #가등록시 자동 등록완료시키기
        try:
            print("등록완료 시작")
            등록버튼들 = driver.find_elements(By.XPATH, '//*[@id="product_form"]/div[6]/div/button[1]')
            if len(등록버튼들) > 0:
                print("등록버튼 개수:"+str(len(등록버튼들)))
                # 등록버튼이 존재하는 경우의 코드
            else:
                print("등록버튼이 페이지에 존재하지 않습니다.")            
            # 등록버튼의 XPath를 사용하여 요소 찾기
            # time.sleep(1)
            등록버튼 = driver.find_element(By.XPATH, '//*[@id="product_form"]/div[6]/div/button[1]')
            등록버튼.click()
            try:
                # 최대 3초 동안 등록 버튼이 사라질 때까지 대기
                WebDriverWait(driver, 3).until(EC.invisibility_of_element((By.XPATH, '//*[@id="product_form"]/div[6]/div/button[1]')))
                print("정상적으로 등록되었습니다.")
            except:
                # 3초 내에 등록 버튼이 사라지지 않으면 오류 메시지 출력
                pyautogui.alert("정상적으로 등록되지 않았습니다.\n등록완료후 계속 진행가능합니다.")            
            print("등록완료 종료")
            # pyautogui.alert(f"{location_detail}\n\n등록완료 확인!! land_code:{land_code} building_code:{building_code} room_code:{room_code}")
            

            # time.sleep(1)
            # # 검색초기화 필요시
            # driver.get('https://osanbang.com/adminproduct/clean/')
            # print("검색초기화")
            # WebDriverWait(driver, 10)
            # print("로딩대기 10초")


            keywords = [location_dongli, location_building]
            if tr_target == '층호수':
                keywords.append(location_room)
            print("keywords:",keywords)
            등록된오방번호 = ''
            # time.sleep(3)
            # pyautogui.alert(', '.join(keywords)+f"\n\n등록된오방번호:{등록된오방번호}","찾는 keywords:") 
            # tbody 내의 모든 tr 요소 찾기
            try:
                time.sleep(0.2)
                rows = driver.find_elements(By.CSS_SELECTOR, '#search-items tr.admin_column')
                print("rows 개수:"+str(len(rows)))
                if len(rows) == 0:
                    pyautogui.alert("리스트의 목록개수 0??")
            except Exception as e:
                print("rows 조회에러:", e)
            # for row in rows:
            for i in range(len(rows)):
                try:
                    # 각 요소에 대해 명시적 대기 적용
                    # 매번 새로 요소를 찾아서 작업
                    row = driver.find_elements(By.CSS_SELECTOR, '#search-items tr.admin_column')[i]                            
                    time.sleep(0.5)
                    print('--')
                    # row구조 = driver.execute_script("return arguments[0].outerHTML;", row)
                    # row구조 = row.get_attribute('outerHTML')
                    # pyautogui.alert(f"row구조:{row구조}")
                    # 주소가 포함된 'help-block' 클래스를 가진 div 찾기
                    address_div = row.find_element(By.CLASS_NAME, 'help-block')
                    print(f"0")
                    address_text = address_div.text.strip()  # 주소 텍스트 추출            
                    print(f"모든 키워드가 포함된 텍스트: {address_text}")
                    # 모든 키워드가 텍스트에 포함되어 있는지 확인
                    if all(keyword in address_text for keyword in keywords):
                        print(f"모든 키워드포함")
                        # tr의 두 번째 td 안에 있는 <strong> 태그의 텍스트 추출
                        second_td = row.find_elements(By.TAG_NAME, 'td')[1]  # 두 번째 td
                        print(f"1")
                        strong_tag = second_td.find_element(By.TAG_NAME, 'strong')  # <strong> 태그 찾기
                        print(f"2")
                        등록된오방번호 = strong_tag.text  # 텍스트 저장
                        print(f"등록된오방번호: {등록된오방번호}")    
                        break            
                    else:
                        print(f"키워드가 누락된 텍스트: {address_text}")
                # except IndexError:
                #     # 만약 td나 div가 없으면 예외 발생을 방지하고 넘어감
                #     print("해당 요소가 없습니다.")    
                except Exception as e:
                    print("row 처리 중 오류:", e)                    
            # pyautogui.alert(', '.join(keywords)+f"\n\n등록된오방번호:{등록된오방번호}","찾는 keywords:") 
            
            #등록된 오방매물번호 DB에 등록
            try:
                update_query = f"UPDATE pr_object SET object_code_obang='{등록된오방번호}' WHERE object_code_new='{object_code_new}'"
                cursor.execute(update_query)
                conn.commit()
                print(f"{location_detail}\n\nDB에 등록된 오방번호: {등록된오방번호}") 
                # pyautogui.alert(f"{location_detail}\n\n등록된 오방번호: {등록된오방번호}")
            except Exception as e:
                print("DB등록에러 An error occurred:", e)
                traceback.print_exc()
                # pyautogui.alert(f"매물번호 업데이트오류: 새홈[{object_code_new}] => 오방번호[{등록된오방번호}]") 
            # pyautogui.alert(f"새홈[{object_code_new}]의 등록된오방번호[ {등록된오방번호} ]")
        except Exception as e:
            pyautogui.alert("등록완료시키기 에러발생:", str(e))
            print("등록완료시키기 에러발생:", str(e))
    else: #수정등록시 종료확인
        # pyautogui.alert(f"새홈매물번호: {object_code_new}\n{location_detail} \n\n작업을 종료하시겠습니까?")
        최상단알림창(f"새홈매물번호: {object_code_new}\n{location_detail} \n\n작업을 종료하시겠습니까?",'작 업 종 료')   
  
    conn.close()  
    cursor.close()
    # driver.close()
    driver.quit()
    print("작동 종료")
    return errarr


def modify_item(driver, selector , value=''):
    element = driver.find_element(By.CSS_SELECTOR, selector)
    # element = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
    if element.is_displayed():
        try:
            # print(selector, "의 element:", element)
            print(selector, "의 text:", element.get_attribute('value'))
            if element.get_attribute('value'):
                element.clear()
                print(selector + "값 클리어")
        except Exception as e:
            print(selector+"클리어 에러 발생:", str(e))
            pass
            # print(selector+" 수정안됨")

        try:
            print("value: ", value)
            element.send_keys(value)
            print(selector+" 수정완료")
        except Exception as e:
            print(selector+"입력에러 발생:", str(e))
            pass


# ═══════════════════════════════════════════════════════════════════════════════
# [2026-09-14 신규 — 사용자 요청 "공적장부처럼 한 곳에서 관리되는 셀레니움 파이프라인"]
#
# automate_from_payload(payload, credentials, options) — 오방 등록·수정을 "프로중개인 서버가 계산해준
# 값(payload)"만 받아 셀레니움으로 끝까지 돌리는 단 하나의 함수.
#
# [왜 위 macro()와 따로 두는가]
#   macro()는 object_data.py가 본섭 DB에 직접 SQL을 날려 만든 data 딕셔너리를 받아, 값을 어떻게 만들지
#   (금액 표기·제목·설명 조합 등 업무로직)까지 이 파일 안에서 스스로 정한다. 그 업무로직은 웹/크롬확장
#   (core/lib/lib_external_ad.php)에도 따로 한 벌 더 있어서 둘이 조용히 어긋났다. 이 함수는 값을 만드는
#   일을 전혀 하지 않는다 — 웹의 external_ad_register.php?mode=payload가 돌려준 fields[]를 그대로 받아
#   "화면에 넣는 일"만 한다. 값 계산은 이제 PHP 한 곳뿐이다.
#
# [누가 부르는가 — 둘 다 이 함수 하나]
#   ① 웹 버튼 → 크롬확장 → local_helper.exe(obangtest/local_helper/main.py::
#      run_external_ad_automation_headless) → 이 함수      … "웹 실행"
#   ② test.py의 "오방(파이프라인)" 버튼 → 이 함수                        … "직접 실행"(VSCode 디버깅)
#   그래서 VSCode에서 여기를 고쳐 정상 동작을 확인하면, 웹에서 눌러도 똑같이 돈다.
#
# [무엇을 본떴는가] fields[]의 by/key/value/control 계약을 DOM으로 해석하는 크롬확장 코드
#   (obangtest/chrome_extension/obang_autofill/autofill_core.js의 applyFields()/applyUpdateFields(),
#   content_obang.js의 enterRegisterForm()/fillAddress()/runModifySearch()/runModifyRow()/
#   findRegisteredObangCode())를 Selenium으로 그대로 옮겼다. ⚠️ 그쪽 화면 조작 규칙(버튼 글자·id·
#   드롭다운 위치 등)이 바뀌면 여기도 같이 맞출 것 — 같은 사이트를 두 기술로 조작하는 유일한 두 곳이다.
#
# [payload] external_ad_register.php?mode=payload 의 res.payload:
#   site_key='obang', mode='register'|'modify', object_code_new, site_code(수정 대상 오방매물번호),
#   fields[{by,key,value,control,label,required,...}], photo{path,...}|None
# [credentials] {'obang_id','obang_pw'}   [options] {'headless': bool, 'close_when_done': bool}
# [return] {'ok', 'ad_code', 'message', 'filled', 'unchanged', 'failed':[{label,reason}], 'skipped',
#           'changes':[{label,before,after}]}
# ═══════════════════════════════════════════════════════════════════════════════

_PIPELINE_ADD_URL   = 'https://osanbang.com/adminproduct/add?category_id'
_PIPELINE_LIST_URL  = 'https://osanbang.com/adminproduct/index'
_PIPELINE_LOGIN_URL = 'https://osanbang.com/adminlogin/index'
_PIPELINE_REGISTER_BUTTON_TEXT = '등록하기'
_PIPELINE_MODIFY_BUTTON_TEXT   = '수정 후 최신으로 갱신'   # 수정화면 맨 아래 세 버튼 중 가운데(2026-09-13 라이브 확인)


def _pipeline_log(text):
    print(time.strftime('%H:%M:%S') + ' ' + str(text), flush=True)


def _pipeline_clean(s):
    return re.sub(r'\s+', ' ', str('' if s is None else s)).strip()


def _pipeline_same_value(now, want):
    """숫자칸은 화면이 1,000처럼 쉼표를 붙여 다시 찍어주기도 한다 — 쉼표만 다른 것은 같은 값으로 본다
    (autofill_core.js::applyUpdateFields의 sameValue와 같은 규칙)."""
    a, b = _pipeline_clean(now), _pipeline_clean(want)
    return a == b or a.replace(',', '') == b.replace(',', '')


def _pipeline_wait(check, timeout_sec=5.0, step_sec=0.15):
    """조건이 참(값을 돌려줌)이 될 때까지 기다린다 — autofill_core.js::waitFor와 같은 뜻. 없으면 None."""
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        try:
            found = check()
        except Exception:
            found = None
        if found:
            return found
        time.sleep(step_sec)
    return None


def _pipeline_find_one(driver, by, key, scope=None):
    root = scope if scope is not None else driver
    try:
        return root.find_element(by, key)
    except Exception:
        return None


def _pipeline_visible(el):
    try:
        return bool(el) and el.is_displayed()
    except Exception:
        return False


def _pipeline_find_by_exact_text(driver, text, tags=('button', 'label', 'a', 'span', 'div'), scope=None):
    """글자가 정확히 일치하는 보이는 요소들 — autofill_core.js::findByExactText와 같은 뜻."""
    wanted = _pipeline_clean(text)
    root = scope if scope is not None else driver
    tag_expr = ' or '.join('self::' + t for t in tags)
    try:
        candidates = root.find_elements(By.XPATH, f'.//*[{tag_expr}]')
    except Exception:
        return []
    return [el for el in candidates if _pipeline_visible(el) and _pipeline_clean(el.text) == wanted]


def _pipeline_is_checked(el):
    try:
        if el.tag_name.lower() == 'input':
            return bool(el.is_selected())
        inner = _pipeline_find_one(None, By.TAG_NAME, 'input', scope=el)
        return bool(inner and inner.is_selected())
    except Exception:
        return False


def _pipeline_click(driver, el):
    """스크롤해서 보이게 한 뒤 페이지 쪽 JS로 클릭한다 — 진행창·오버레이에 가려 실패하는 일을 막는다."""
    driver.execute_script("arguments[0].scrollIntoView({block:'center'}); arguments[0].click();", el)


def _pipeline_set_value(driver, el, value):
    """값을 넣고 화면이 알아채도록 input/change/keyup을 함께 보낸다 — autofill_core.js::setValue와 동일."""
    driver.execute_script(
        "var el=arguments[0]; el.focus(); el.value=String(arguments[1]);"
        "['input','change','keyup'].forEach(function(t){el.dispatchEvent(new Event(t,{bubbles:true}));}); el.blur();",
        el, value)


def _pipeline_select_option(driver, el, value):
    """고를 수 있는 값이면 고른다(value → 글자 → 정수) — autofill_core.js::selectOption과 동일."""
    wanted = _pipeline_clean(value)
    options_list = el.find_elements(By.TAG_NAME, 'option')
    hit = next((o for o in options_list if _pipeline_clean(o.get_attribute('value')) == wanted), None) \
        or next((o for o in options_list if _pipeline_clean(o.text) == wanted), None)
    if hit is None:
        try:
            as_int = str(int(float(wanted)))
            hit = next((o for o in options_list if _pipeline_clean(o.get_attribute('value')) == as_int), None)
        except ValueError:
            hit = None
    if hit is None:
        seen = ' / '.join(_pipeline_clean(o.text) for o in options_list[:12])
        return {'ok': False, 'reason': f"'{value}' 선택지가 없습니다 · 실제 선택지: {seen}"}
    driver.execute_script(
        "arguments[0].value=arguments[1]; arguments[0].dispatchEvent(new Event('change',{bubbles:true}));",
        el, hit.get_attribute('value'))
    return {'ok': True}


def _pipeline_current_select_text(el):
    try:
        cur = next((o for o in el.find_elements(By.TAG_NAME, 'option') if o.is_selected()), None)
        return (_pipeline_clean(cur.text), _pipeline_clean(cur.get_attribute('value'))) if cur else ('', '')
    except Exception:
        return ('', '')


def _pipeline_apply_checkset(driver, input_name, wanted_csv):
    """그 묶음에서 '켤 이름'만 켜고 나머지는 끈다 — autofill_core.js::applyCheckSet과 동일 규칙."""
    boxes = driver.find_elements(By.CSS_SELECTOR, f'input[name="{input_name}"]')
    if not boxes:
        return {'ok': False, 'reason': f"'{input_name}' 묶음을 화면에서 찾지 못했습니다"}
    wanted = [_pipeline_clean(v) for v in str(wanted_csv or '').split(',') if _pipeline_clean(v)]
    turned_on, turned_off = [], []
    for box in boxes:
        own_label = None
        try:
            wrapper = box.find_element(By.XPATH, './ancestor::label[1]')
            if len(wrapper.find_elements(By.TAG_NAME, 'input')) == 1:
                own_label = wrapper
        except Exception:
            own_label = None
        names = [_pipeline_clean(box.get_attribute('value'))]
        if own_label is not None:
            names.append(_pipeline_clean(own_label.text))
        should_on = any(w in names for w in wanted)
        is_on = (('active' in (own_label.get_attribute('class') or '')) or box.is_selected()) if own_label is not None else box.is_selected()
        if should_on == is_on:
            continue
        _pipeline_click(driver, own_label if own_label is not None else box)
        (turned_on if should_on else turned_off).append(names[-1] if own_label is not None else names[0])
    parts = []
    if turned_on:
        parts.append('켬 ' + '/'.join(turned_on))
    if turned_off:
        parts.append('끔 ' + '/'.join(turned_off))
    return {'ok': True, 'note': ' · '.join(parts) if parts else '이미 그대로임'}


def _pipeline_apply_editor(driver, html):
    """상세설명(CKEditor) — 이미 적혀 있으면 넣지 않는다(autofill_core.js::applyEditorContent와 동일)."""
    frame = _pipeline_find_one(driver, By.CSS_SELECTOR, '#cke_1_contents iframe')
    if frame is None:
        return {'ok': False, 'reason': '상세설명 편집기를 찾지 못했습니다'}
    try:
        driver.switch_to.frame(frame)
        current = _pipeline_clean(driver.execute_script('return document.body ? document.body.innerHTML : "";'))
        if current not in ('', '<p><br></p>', '<br>'):
            return {'ok': True, 'note': '이미 설명이 있어 그대로 둠'}
        driver.execute_script('document.body.innerHTML = arguments[0];', html)
        return {'ok': True}
    finally:
        driver.switch_to.default_content()


def _pipeline_apply_fields(driver, fields, compare):
    """
    값 한 벌을 화면에 채운다. compare=False면 applyFields(무조건 채움), True면 applyUpdateFields
    (지금 값과 같으면 안 건드리고 다를 때만 고침 — 수정용). 반환 형식도 그 두 함수와 같다.
    """
    filled, unchanged, failed, skipped = [], [], [], []
    for f in fields:
        by, key, value = f.get('by'), str(f.get('key') or ''), f.get('value')
        control, label = f.get('control') or '', f.get('label') or key
        if by == 'flow':
            skipped.append(f); continue
        if by != 'checkset' and _pipeline_clean(value) == '':
            skipped.append(f); continue

        result, before = None, None
        try:
            if by == 'checkset':
                result = _pipeline_apply_checkset(driver, key, value)
                if compare and result.get('ok') and result.get('note') == '이미 그대로임':
                    unchanged.append({'label': label, 'before': '(현재 상태 유지)'}); continue
            elif by == 'editor':
                result = _pipeline_apply_editor(driver, value)
                if compare and result.get('ok') and result.get('note'):
                    unchanged.append({'label': label, 'before': '(기존 설명 유지)'}); continue
            elif by == 'text':
                target = next(iter(_pipeline_find_by_exact_text(driver, key)), None)
                if target is None:
                    result = {'ok': False, 'reason': f"'{key}' 선택지를 찾지 못했습니다"}
                elif _pipeline_is_checked(target):
                    if compare:
                        unchanged.append({'label': label, 'before': key}); continue
                    result = {'ok': True, 'note': '이미 선택돼 있음'}
                else:
                    _pipeline_click(driver, target); before = '(다른 선택)'; result = {'ok': True}
            else:
                locator = (By.CSS_SELECTOR, f'[name="{key}"]') if by == 'name' else (By.ID, key)
                el = _pipeline_wait(lambda: _pipeline_find_one(driver, *locator), 1.5)
                if el is None:
                    result = {'ok': False, 'reason': f"'{key}' 칸을 찾지 못했습니다({by})"}
                elif control in ('radio', 'checkbox'):
                    if _pipeline_is_checked(el):
                        if compare:
                            unchanged.append({'label': label, 'before': value}); continue
                        result = {'ok': True, 'note': '이미 선택돼 있음'}
                    else:
                        _pipeline_click(driver, el); before = '(다른 선택)'; result = {'ok': True}
                elif control == 'select' or el.tag_name.lower() == 'select':
                    cur_text, cur_value = _pipeline_current_select_text(el)
                    if compare and (_pipeline_same_value(cur_value, value) or _pipeline_same_value(cur_text, value)):
                        unchanged.append({'label': label, 'before': cur_text or cur_value or '(못 읽음)'}); continue
                    before = cur_text or cur_value or '(못 읽음)'
                    result = _pipeline_select_option(driver, el, value)
                elif not _pipeline_visible(el):
                    # 오방은 매물종류·거래종류에 따라 안 쓰는 칸을 숨긴다 — 보일 때만 넣는다
                    result = {'ok': False, 'reason': '이 매물종류에는 없는 칸입니다(화면에 숨겨져 있음)'}
                else:
                    current = el.get_attribute('value')
                    if compare and _pipeline_same_value(current, value):
                        unchanged.append({'label': label, 'before': current}); continue
                    before = current
                    _pipeline_set_value(driver, el, value)
                    result = {'ok': True}
        except Exception as e:
            result = {'ok': False, 'reason': f'{type(e).__name__}: {e}'}

        if result and result.get('ok'):
            filled.append({'field': f, 'label': label, 'before': before if before is not None else '(이전 값)',
                           'after': value, 'note': result.get('note', '')})
        else:
            failed.append({'field': f, 'label': label, 'reason': (result or {}).get('reason', '알 수 없음')})
        time.sleep(0.08)
    return {'filled': filled, 'unchanged': unchanged, 'failed': failed, 'skipped': skipped}


def _pipeline_login(driver, credentials):
    """오방 관리자 로그인 — 위 macro()의 로그인 절차(login_form XPath, 사이드바 '매물'로 확인)와 동일."""
    driver.get(_PIPELINE_LOGIN_URL)
    driver.find_element(By.XPATH, '//*[@id="login_form"]/div[1]/div/input').send_keys(credentials['obang_id'])
    driver.find_element(By.XPATH, '//*[@id="login_form"]/div[2]/div/input').send_keys(credentials['obang_pw'])
    driver.find_element(By.XPATH, '//*[@id="login_form"]/div[3]/button').click()
    try:
        WebDriverWait(driver, 15).until(EC.presence_of_element_located(
            (By.XPATH, "//ul[contains(@class, 'page-sidebar-menu')]//li[.//span[contains(@class, 'title') and text()='매물']]")))
    except TimeoutException:
        # 왜 못 넘어갔는지 화면 상태를 그대로 남긴다 — 계정 오류 문구, 알림창, 엉뚱한 화면 등을
        # 로그만 보고 가릴 수 있어야 한다(첫 실행에서 "Timeout"만 남아 원인을 못 가렸다, 2026-09-14).
        alert_text = ''
        try:
            alert = driver.switch_to.alert
            alert_text = alert.text
            alert.accept()
        except Exception:
            pass
        try:
            body = _pipeline_clean(driver.execute_script('return document.body ? document.body.innerText : "";'))[:300]
        except Exception:
            body = '(읽지 못함)'
        raise RuntimeError(f'오방 로그인 후 관리자 화면이 뜨지 않았습니다 — url={driver.current_url} 제목={driver.title!r}'
                           + (f' 알림창={alert_text!r}' if alert_text else '') + f' 화면문구={body!r}')
    _pipeline_log('✓ 오방 로그인')


def _pipeline_enter_register_form(driver):
    """등록폼이 뜰 때까지 기다리고, '임시저장 이어쓰기' 창은 두 번째 버튼(이어 쓰지 않기)으로 닫는다
    — content_obang.js::enterRegisterForm()과 동일(이어 쓰면 이전 매물 값이 섞여 들어간다)."""
    def dialog_buttons():
        dialog = _pipeline_find_one(driver, By.ID, 'temp_check_dialog')
        if not _pipeline_visible(dialog):
            return None
        buttons = [b for b in dialog.find_elements(By.TAG_NAME, 'button') if _pipeline_visible(b)]
        return buttons or None
    buttons = _pipeline_wait(dialog_buttons, 2.5)
    if buttons:
        _pipeline_click(driver, buttons[1] if len(buttons) > 1 else buttons[0])
        _pipeline_log('✓ 임시저장 이어쓰기 창을 닫았습니다')
        time.sleep(0.4)
    form = _pipeline_wait(lambda: _pipeline_find_one(driver, By.ID, 'product_form'), 12)
    if form is None:
        raise RuntimeError('매물등록 폼이 열리지 않았습니다 — 오방 로그인 상태를 확인해주세요.')
    _pipeline_log('✓ 등록폼 열림')


def _pipeline_pick_region_button(buttons, want):
    """지역 목록에서 우리 값에 맞는 버튼 — 정확히 일치가 우선, 없으면 앞부분 일치가 하나뿐일 때만
    (새홈 '경기도' vs 오방 '경기' 표기 차이 흡수, content_obang.js::pickRegionButton과 동일)."""
    wanted = _pipeline_clean(want)
    exact = [b for b in buttons if _pipeline_clean(b.text) == wanted]
    if exact:
        return exact[0]
    partial = [b for b in buttons
               if _pipeline_clean(b.text) and (_pipeline_clean(b.text).startswith(wanted) or wanted.startswith(_pipeline_clean(b.text)))]
    return partial[0] if len(partial) == 1 else None


def _pipeline_fill_address(driver, address_text, jibun, address_unit):
    """지역(시/도→구/군→동) 선택 + 지번·상세주소 + [위치 검색] — content_obang.js::fillAddress()와 동일."""
    parts = [p for p in str(address_text or '').split(' ') if p]
    if len(parts) < 3:
        _pipeline_log('· 주소(시/도·구/군·동)가 온전하지 않아 지역 선택을 건너뜁니다.')
    else:
        opener = _pipeline_find_one(driver, By.CSS_SELECTOR, '#product_form button')
        if opener is not None:
            _pipeline_click(driver, opener)
        for section_id, want, label in (('sido_section', parts[0], '시/도'), ('gugun_section', parts[1], '구/군'), ('dong_section', parts[2], '읍/면/동')):
            def visible_buttons(sid=section_id):
                box = _pipeline_find_one(driver, By.ID, sid)
                if box is None:
                    return None
                buttons = [b for b in box.find_elements(By.TAG_NAME, 'button') if _pipeline_visible(b)]
                return buttons or None
            buttons = _pipeline_wait(visible_buttons, 5)
            button = _pipeline_pick_region_button(buttons, want) if buttons else None
            if button is None:
                seen = ' / '.join(_pipeline_clean(b.text) for b in (buttons or [])[:12]) or '(목록이 뜨지 않음)'
                raise RuntimeError(f"{label} '{want}'을 지역 목록에서 찾지 못했습니다 · 실제 목록: {seen}")
            _pipeline_click(driver, button)
            _pipeline_log(f'✓ {label}: {want}')
            time.sleep(0.3)

    address_input = _pipeline_find_one(driver, By.ID, 'address')
    if address_input is not None and jibun:
        _pipeline_set_value(driver, address_input, jibun)
        _pipeline_log(f'✓ 지번: {jibun}')
        coord = _pipeline_find_one(driver, By.ID, 'get_coord')
        if coord is None:
            raise RuntimeError('[위치 검색] 버튼을 찾지 못했습니다.')
        _pipeline_click(driver, coord)
        got = _pipeline_wait(lambda: (
            _pipeline_clean((_pipeline_find_one(driver, By.ID, 'lat') or {}).get_attribute('value') if _pipeline_find_one(driver, By.ID, 'lat') else '') != ''
            and _pipeline_clean((_pipeline_find_one(driver, By.ID, 'lng') or {}).get_attribute('value') if _pipeline_find_one(driver, By.ID, 'lng') else '') != ''
        ) or None, 5)
        if not got:
            raise RuntimeError(f'[위치 검색]을 눌렀지만 좌표가 잡히지 않았습니다 — 지번 {jibun}')
        _pipeline_log('✓ 위치검색 — 좌표를 잡았습니다')

    unit_input = _pipeline_find_one(driver, By.ID, 'address_unit')
    if unit_input is not None and address_unit:
        _pipeline_set_value(driver, unit_input, address_unit)
        _pipeline_log(f'✓ 상세주소: {address_unit}')


def _pipeline_photo_files(photo):
    """올릴 사진 파일 목록 — NAS 원본이 아니라 변환폴더(output…, 이름이 가장 큰 = 최근 것)의 저용량본만
    쓴다(local_helper/main.py::resolve_photo_folder와 같은 규칙). 없으면 빈 목록."""
    path = str((photo or {}).get('path') or '').strip()
    if not path or not os.path.isdir(path):
        return []
    try:
        converted = sorted(n for n in os.listdir(path) if n.lower().startswith('output') and os.path.isdir(os.path.join(path, n)))
    except OSError:
        return []
    if not converted:
        return []
    folder = os.path.join(path, converted[-1])
    try:
        return [os.path.join(folder, n) for n in sorted(os.listdir(folder))
                if n.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')) and os.path.isfile(os.path.join(folder, n))]
    except OSError:
        return []


def _pipeline_set_speed_flag(driver, on):
    """급매 표시 — 사진을 못 올렸다는 표시로 쓴다(macro()/content_obang.js와 같은 규칙)."""
    speed = _pipeline_find_one(driver, By.ID, 'is_speed')
    if speed is not None and bool(speed.is_selected()) != bool(on):
        _pipeline_click(driver, speed)


def _pipeline_upload_photos(driver, photo):
    """사진 올리기 — 오방에 이미 사진이 있으면 손대지 않고, 못 올리면 급매로 표시한다."""
    already = len(driver.find_elements(By.CSS_SELECTOR, '#list li'))
    if already > 0:
        _pipeline_log(f'· 오방에 이미 사진 {already}장이 있어 사진은 건드리지 않습니다')
        return
    files = _pipeline_photo_files(photo)
    if not files:
        _pipeline_log('⚠ 올릴 변환 사진이 없어 급매로 표시합니다')
        _pipeline_set_speed_flag(driver, True)
        return
    file_input = next((el for el in driver.find_elements(By.CSS_SELECTOR, 'input[type="file"]')
                       if el.get_attribute('multiple') is not None and 'image/' in (el.get_attribute('accept') or '')), None)
    if file_input is None:
        _pipeline_log('⚠ 사진 넣는 칸을 찾지 못했습니다 — 급매로 표시합니다')
        _pipeline_set_speed_flag(driver, True)
        return
    file_input.send_keys('\n'.join(files))
    _pipeline_log(f'· 사진 {len(files)}장을 올리는 중…')
    uploaded = _pipeline_wait(lambda: len(driver.find_elements(By.CSS_SELECTOR, '#list li')) >= len(files) or None, 120, 0.5)
    if not uploaded:
        now = len(driver.find_elements(By.CSS_SELECTOR, '#list li'))
        _pipeline_log(f'⚠ 사진 {len(files)}장 중 {now}장만 올라갔습니다 — 급매로 표시합니다')
        _pipeline_set_speed_flag(driver, True)
        return
    _pipeline_log(f'✓ 사진 {len(files)}장을 올렸습니다')
    _pipeline_set_speed_flag(driver, False)


def _pipeline_match_keywords(fields):
    """방금 올린 매물을 목록에서 가려낼 말들(지번·건물명·호실) — content_obang.js::buildMatchKeywords."""
    by_label = {f.get('label'): f for f in fields}
    keywords = []
    jibun = _pipeline_clean((by_label.get('상세주소1(지번)') or {}).get('value'))
    unit = _pipeline_clean((by_label.get('상세주소2(건물·호실)') or {}).get('value'))
    if jibun:
        keywords.append(jibun)
    keywords.extend(w for w in unit.split(' ') if w)
    return keywords


def _pipeline_reset_list_keyword(driver):
    """[2026-09-17 추가 — 사용자 요청] 매물목록에 들어오면 검색칸(#search_id)에 남아 있는 이전 키워드부터
    지운다 — 걸러진 목록에서는 방금 올린 매물이나 고칠 매물이 안 보여 "찾지 못함"으로 끝나기 때문.
    오방은 검색 시 화면 이동 없이 그 자리에서 목록을 다시 그린다(2026-09-17 실측). 값이 비어 있으면
    아무 것도 하지 않는다(불필요한 재검색으로 느려지지 않게). content_obang.js::resetListKeywordIfAny()와 짝."""
    box = _pipeline_find_one(driver, By.ID, 'search_id')
    btn = _pipeline_find_one(driver, By.ID, 'go_keyword')
    if box is None or btn is None:
        return False
    leftover = (box.get_attribute('value') or '').strip()
    if leftover == '':
        return False
    _pipeline_log(f"[목록] 검색칸에 남아 있던 '{leftover}' 를 지우고 목록을 다시 불러옵니다")
    _pipeline_set_value(driver, box, '')
    _pipeline_click(driver, btn)
    time.sleep(1.5)   # 그 자리에서 다시 그려질 시간
    return True


def _pipeline_find_registered_code(driver, keywords):
    """등록 후 목록에서 방금 올린 매물의 오방매물번호 — 주소(.help-block)에 지번·건물명·호실이 모두 든
    줄의 두 번째 칸 굵은 글씨(첫 줄을 그냥 집으면 남이 그 사이 올린 매물번호를 저장한다)."""
    _pipeline_wait(lambda: _pipeline_find_one(driver, By.ID, 'search_id'), 15)
    _pipeline_reset_list_keyword(driver)
    rows = _pipeline_wait(lambda: driver.find_elements(By.CSS_SELECTOR, '#search-items tr') or None, 15)
    if not rows:
        return {'ok': False, 'reason': '등록 후 매물목록이 뜨지 않았습니다'}
    seen = []
    for row in rows:
        address_box = _pipeline_find_one(None, By.CSS_SELECTOR, '.help-block', scope=row)
        cells = row.find_elements(By.TAG_NAME, 'td')
        strong = _pipeline_find_one(None, By.TAG_NAME, 'strong', scope=cells[1]) if len(cells) > 1 else None
        if address_box is None or strong is None:
            continue
        address, code = _pipeline_clean(address_box.text), _pipeline_clean(strong.text)
        seen.append(f'{code} — {address}')
        if all(w in address for w in keywords):
            return {'ok': True, 'code': code, 'address': address}
    return {'ok': False, 'reason': f"방금 올린 매물을 목록에서 찾지 못했습니다(찾던 말: {' / '.join(keywords)}) · 목록: {' · '.join(seen[:5])}"}


def _pipeline_dong_token(payload):
    """요약 주소("경기 오산시 은계동 92-4")에서 동/리 이름 하나 — 다른 동의 같은 지번을 걸러내는 데 쓴다."""
    tokens = [t for t in str((payload.get('summary') or {}).get('주소', '')).split() if t]
    for t in reversed(tokens):
        if re.search(r'(동|리|가|읍|면)$', t) and not re.search(r'\d', t):
            return t
    return ''


def _pipeline_find_duplicates(driver, payload, keywords):
    """[2026-09-17 추가 — 사용자 지적 "파이썬의 중복등록 방지가 빠졌다"] 신규등록 전에 매물목록을 주소로
    검색해 이미 올라간 매물을 찾는다 — 위 macro()(639~713)가 하던 것을 파이프라인에도 넣은 것.
    content_obang.js::runDuplicateCheck()와 같은 기준(층호수: 지번+호실/건물명, 그 외: 지번+매물종류)이고,
    오방 검색어는 낱말 하나만 통째로 대조하므로 지번만 넣어 줄인 뒤 나머지는 줄마다 대조한다.
    @return [{'code','address'}] — 비어 있으면 중복 없음"""
    if not keywords:
        _pipeline_log('[등록] 중복 확인 건너뜀 — 지번 없음')
        return []
    driver.get(_PIPELINE_LIST_URL)
    box = _pipeline_wait(lambda: _pipeline_find_one(driver, By.ID, 'keyword'), 15)
    btn = _pipeline_find_one(driver, By.ID, 'go_keyword')
    if box is None or btn is None:
        _pipeline_log('[등록] 중복 확인 건너뜀 — 목록 검색칸 없음(오방 로그인 상태 확인)')
        return []
    _pipeline_reset_list_keyword(driver)
    jibun_token = keywords[0].split(' ')[-1]
    _pipeline_log(f'[등록] 오방 목록에서 지번 "{jibun_token}" 검색 — 이미 올라간 매물이 있는지 확인')
    _pipeline_set_value(driver, box, jibun_token)
    _pipeline_click(driver, btn)
    time.sleep(2.5)
    unit_words = keywords[1:]
    by_label = {f.get('label'): f for f in payload.get('fields') or []}
    category = '' if unit_words else _pipeline_clean((by_label.get('매물종류') or {}).get('value'))
    words = list(keywords)
    dong = _pipeline_dong_token(payload)
    if dong:
        words.append(dong)
    found = []
    for row in driver.find_elements(By.CSS_SELECTOR, '#search-items tr'):
        address_box = _pipeline_find_one(None, By.CSS_SELECTOR, '.help-block', scope=row)
        cells = row.find_elements(By.TAG_NAME, 'td')
        strong = _pipeline_find_one(None, By.TAG_NAME, 'strong', scope=cells[1]) if len(cells) > 1 else None
        if address_box is None or strong is None:
            continue
        address = _pipeline_clean(address_box.text)
        if not all(w in address for w in words):
            continue
        if category and category not in _pipeline_clean(row.text):
            continue
        found.append({'code': _pipeline_clean(strong.text), 'address': address})
    _pipeline_set_value(driver, box, '')   # 검색어를 남기지 않는다
    return found


def _pipeline_register(driver, payload, result):
    fields = payload.get('fields') or []
    by_label = {f.get('label'): f for f in fields}
    duplicates = _pipeline_find_duplicates(driver, payload, _pipeline_match_keywords(fields))
    if duplicates:
        raise RuntimeError('오방에 같은 주소의 매물이 이미 있어 신규등록을 중단했습니다: '
                           + ' · '.join(f"{d['code']}({d['address']})" for d in duplicates)
                           + ' — 외부광고 관리에서 그 오방매물번호를 연결한 뒤 수정으로 진행해주세요.')
    driver.get(_PIPELINE_ADD_URL)
    _pipeline_enter_register_form(driver)
    _pipeline_fill_address(driver,
                           (by_label.get('시/도·구/군·동') or {}).get('value', ''),
                           _pipeline_clean((by_label.get('상세주소1(지번)') or {}).get('value')),
                           _pipeline_clean((by_label.get('상세주소2(건물·호실)') or {}).get('value')))
    applied = _pipeline_apply_fields(driver, fields, compare=False)
    _pipeline_summarize(applied, result)
    _pipeline_upload_photos(driver, payload.get('photo'))

    keywords = _pipeline_match_keywords(fields)
    if not keywords:
        raise RuntimeError('매물을 가려낼 주소 정보가 없어 등록 후 매물번호를 찾을 수 없습니다.')
    submit = next(iter(_pipeline_find_by_exact_text(driver, _PIPELINE_REGISTER_BUTTON_TEXT, ('button',))), None)
    if submit is None:
        raise RuntimeError(f'[{_PIPELINE_REGISTER_BUTTON_TEXT}] 버튼을 찾지 못했습니다.')
    _pipeline_click(driver, submit)
    _pipeline_log(f'✓ [{_PIPELINE_REGISTER_BUTTON_TEXT}] 클릭 — 등록 결과 화면을 기다립니다…')
    _pipeline_dismiss_alert(driver)

    found = _pipeline_find_registered_code(driver, keywords)
    if not found['ok']:
        raise RuntimeError(found['reason'] + ' — 등록 자체는 끝났을 수 있으니 오방 목록을 확인해주세요.')
    result.update({'ok': True, 'ad_code': found['code'], 'message': f"오방매물번호 {found['code']} ({found['address']})"})


def _pipeline_open_manage_menu(driver, row):
    """[관리] 드롭다운을 열고 항목 목록을 돌려준다 — 14번째 칸 안의 div.dropdown, 여는 건 [data-toggle]."""
    cells = row.find_elements(By.TAG_NAME, 'td')
    manage_cell = cells[13] if len(cells) > 13 else None
    dropdown = _pipeline_find_one(None, By.CSS_SELECTOR, 'div.dropdown', scope=manage_cell) if manage_cell is not None else None
    toggle = _pipeline_find_one(None, By.CSS_SELECTOR, '[data-toggle="dropdown"]', scope=dropdown) if dropdown is not None else None
    if dropdown is None or toggle is None:
        raise RuntimeError('그 매물의 [관리] 메뉴를 찾지 못했습니다.')
    _pipeline_click(driver, toggle)
    items = _pipeline_wait(lambda: [a for a in dropdown.find_elements(By.CSS_SELECTOR, 'ul.dropdown-menu li a') if _pipeline_visible(a)] or None, 5)
    if not items:
        items = dropdown.find_elements(By.CSS_SELECTOR, 'ul.dropdown-menu li a')   # 안 열려도 항목은 DOM에 있다
    if not items:
        raise RuntimeError('[관리] 메뉴가 열리지 않았습니다.')
    return items


def _pipeline_search_row(driver, code):
    driver.get(_PIPELINE_LIST_URL)
    search_box = _pipeline_wait(lambda: _pipeline_find_one(driver, By.ID, 'search_id'), 15)
    search_btn = _pipeline_find_one(driver, By.ID, 'go_keyword')
    if search_box is None or search_btn is None:
        raise RuntimeError('오방 매물목록의 검색칸을 찾지 못했습니다 — 로그인 상태를 확인해주세요.')
    _pipeline_reset_list_keyword(driver)   # 남은 키워드가 있으면 먼저 비우고 전체 목록으로 되돌린다
    _pipeline_set_value(driver, search_box, code)
    _pipeline_click(driver, search_btn)
    row = _pipeline_wait(lambda: _pipeline_find_one(driver, By.ID, f'tr_{code}'), 20)
    if row is None:
        raise RuntimeError(f'매물번호 {code} 를 오방에서 찾지 못했습니다 — 이미 삭제된 매물입니다.')
    time.sleep(0.8)
    return _pipeline_find_one(driver, By.ID, f'tr_{code}')


def _pipeline_modify(driver, payload, result):
    """수정 — 목록에서 매물을 찾아 상태(공개·거래완료)를 정리하고 수정화면에서 다른 값만 고친 뒤
    [수정 후 최신으로 갱신]을 누른다(content_obang.js runModifySearch/Row/Fill과 동일한 순서)."""
    code = _pipeline_clean(payload.get('site_code'))
    if not code:
        raise RuntimeError('고칠 오방매물번호(site_code)가 없습니다.')

    released = False
    for _ in range(2):   # 거래완료 해제 후 한 번 더 검색한다 — 그 이상 반복하지 않는다
        row = _pipeline_search_row(driver, code)
        cells = row.find_elements(By.TAG_NAME, 'td')
        public_label = _pipeline_find_one(None, By.TAG_NAME, 'label', scope=cells[2]) if len(cells) > 2 else None
        if public_label is not None and _pipeline_clean(public_label.text) == 'off':
            _pipeline_click(driver, public_label)
            _pipeline_log('✓ 비공개 → 공개로 전환했습니다')
            time.sleep(0.6)
        items = _pipeline_open_manage_menu(driver, row)
        named = {_pipeline_clean(a.text): a for a in items}
        release = named.get('거래완료 해제')
        if release is not None and not released:
            m = re.search(r"change\('([^']+)','([^']+)','([^']+)'\)", release.get_attribute('href') or '')
            if m:
                url = f'/adminproduct/change/{m.group(1)}/{m.group(2)}/{m.group(3)}/{int(time.time()*1000)}'
                status = driver.execute_async_script(
                    "var cb=arguments[arguments.length-1];fetch(arguments[0],{credentials:'same-origin'}).then(r=>cb(r.status)).catch(e=>cb('ERR:'+e.message));", url)
                _pipeline_log(f'· 거래완료 해제 요청 — {status}')
            else:
                _pipeline_log('⚠ 거래완료 해제 주소를 읽지 못했습니다 — 오방에서 직접 해제해주세요')
            released = True
            time.sleep(1.0)
            continue
        if release is not None and released:
            _pipeline_log('⚠ 거래완료 해제가 되지 않았습니다 — 오방에서 직접 해제해주세요')
        modify_item_link = named.get('수정')
        if modify_item_link is None:
            raise RuntimeError('[관리] 메뉴에 [수정]이 없습니다 — 그 매물을 고칠 권한이 없습니다(담당자 확인). 메뉴: ' + ' · '.join(named.keys()))
        href = modify_item_link.get_attribute('href') or ''
        if href and not href.startswith('javascript:'):
            driver.get(href)
        else:
            _pipeline_click(driver, modify_item_link)
        break

    if _pipeline_wait(lambda: _pipeline_find_one(driver, By.ID, 'product_form'), 15) is None:
        raise RuntimeError('수정 폼이 열리지 않았습니다.')
    # 대분류(category_*)는 화면 주소로 이미 정해져 있어 건드리면 폼이 다시 그려진다 — 수정에서는 제외
    fields = [f for f in (payload.get('fields') or []) if not str(f.get('key') or '').startswith('category_')]
    applied = _pipeline_apply_fields(driver, fields, compare=True)
    _pipeline_summarize(applied, result)
    if any(x['field'].get('key') == 'address' for x in applied['filled']):
        coord = _pipeline_find_one(driver, By.ID, 'get_coord')
        if coord is not None:
            _pipeline_click(driver, coord)
            _pipeline_log('✓ [위치 검색]으로 좌표를 다시 잡았습니다')
    _pipeline_upload_photos(driver, payload.get('photo'))

    submit = next(iter(_pipeline_find_by_exact_text(driver, _PIPELINE_MODIFY_BUTTON_TEXT, ('button',))), None)
    if submit is None:
        raise RuntimeError(f'[{_PIPELINE_MODIFY_BUTTON_TEXT}] 버튼을 찾지 못했습니다.')
    _pipeline_click(driver, submit)
    _pipeline_log(f'✓ [{_PIPELINE_MODIFY_BUTTON_TEXT}] 클릭 — 목록으로 돌아가길 기다립니다…')
    _pipeline_dismiss_alert(driver)
    if _pipeline_wait(lambda: ('/adminproduct/index' in driver.current_url) or None, 20) is None:
        raise RuntimeError('수정 후 매물목록으로 돌아오지 않았습니다 — 오방 화면을 확인해주세요.')
    result.update({'ok': True, 'ad_code': code, 'message': f'오방매물번호 {code} 수정 완료'})


def _pipeline_dismiss_alert(driver):
    """저장 직후 사이트가 띄우는 확인/오류 alert가 있으면 글자를 남기고 닫는다."""
    try:
        WebDriverWait(driver, 2).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        text = alert.text
        alert.accept()
        _pipeline_log(f'· 사이트 알림창: {text}')
        if any(w in text for w in ('확인 해주시기', '필수', '입력해', '선택해')):
            raise RuntimeError(f'오방이 저장을 거부했습니다: {text}')
    except TimeoutException:
        pass


def _pipeline_summarize(applied, result):
    result['filled'] = len(applied['filled'])
    result['unchanged'] = len(applied['unchanged'])
    result['skipped'] = len(applied['skipped'])
    result['failed'] = [{'label': x['label'], 'reason': x['reason']} for x in applied['failed']]
    result['changes'] = [{'label': x['label'], 'before': x['before'], 'after': x['after']} for x in applied['filled']]
    _pipeline_log(f"값 채우기 — 채움 {result['filled']} / 안 건드림 {result['unchanged']} / 실패 {len(result['failed'])} / 건너뜀 {result['skipped']}")
    for x in applied['filled']:
        _pipeline_log(f"  고침 {x['label']}: '{x['before']}' → '{x['after']}'" + (f" ({x['note']})" if x['note'] else ''))
    for x in applied['failed']:
        _pipeline_log(f"  실패 {x['label']}: {x['reason']}")
    must = [x for x in applied['failed'] if (x['field'] or {}).get('required')]
    if must:
        raise RuntimeError('필수항목을 채우지 못했습니다: ' + ', '.join(f"{x['label']}({x['reason']})" for x in must))


def automate_from_payload(payload, credentials, options=None):
    options = options or {}
    headless = bool(options.get('headless', False))
    close_when_done = bool(options.get('close_when_done', True))
    result = {'ok': False, 'ad_code': '', 'message': '', 'filled': 0, 'unchanged': 0, 'failed': [], 'skipped': 0, 'changes': []}
    if str(payload.get('site_key') or '') != 'obang':
        result['message'] = f"오방 payload가 아닙니다(site_key={payload.get('site_key')!r})"
        return result
    if not credentials or not credentials.get('obang_id'):
        result['message'] = '오방 로그인정보(obang_id/obang_pw)가 없습니다.'
        return result
    mode = str(payload.get('mode') or 'register')
    _pipeline_log(f"오방 셀레니움 시작 — mode={mode}, 새홈매물번호={payload.get('object_code_new')}, 오방번호={payload.get('site_code') or '-'}, headless={headless}")

    # 위 macro()의 전역 options(detach=True: 스크립트가 끝나도 브라우저를 남김)는 쓰지 않는다 —
    # 이 함수는 close_when_done으로 창 수명을 직접 관리한다.
    chrome_options = Options()
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    driver = webdriver.Chrome(options=chrome_options)
    try:
        if headless:
            # 진짜 headless(--headless) 대신 화면 밖으로 밀어둔다 — iros_document_issue.py와 같은 이유
            # (보이는 창과 동작 차이를 없앰). 크기는 데스크톱 레이아웃이 나오도록 넉넉히 잡는다 —
            # 작으면 관리자 사이드바가 접혀 요소 구조가 달라진다. 작업이 끝나면 close_when_done으로 닫힌다.
            driver.set_window_size(1400, 1000)
            driver.set_window_position(-32000, -32000)
        else:
            driver.maximize_window()
        _pipeline_login(driver, credentials)
        if mode == 'modify':
            _pipeline_modify(driver, payload, result)
        else:
            _pipeline_register(driver, payload, result)
    except Exception as e:
        result['ok'] = False
        result['message'] = f'{type(e).__name__}: {e}' if not isinstance(e, RuntimeError) else str(e)
        _pipeline_log('✗ ' + result['message'])
        traceback.print_exc()
    finally:
        if close_when_done:
            try:
                driver.quit()
            except Exception:
                pass
    _pipeline_log(('✓ ' if result['ok'] else '✗ ') + result['message'])
    return result