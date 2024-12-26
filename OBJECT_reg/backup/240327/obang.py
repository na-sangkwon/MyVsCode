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

def 숫자한글로금액변환(숫자금액):
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
           
def macro(data, user, group):
    # ChromeDriver 경로 설정
    # driver = webdriver.Chrome('/chromedriver', options=options)
    driver = webdriver.Chrome(options=options)
    # driver = webdriver.Chrome(ChromeDriverManager().install())    
    errarr = []
    
    obang_id = data['adminData']['obang_id']
    obang_pw = data['adminData']['obang_pw']
    
    # 현재 날짜 출력
    import datetime
    current_date = datetime.date.today()
    formatted_date = current_date.strftime("%Y-%m-%d")
    
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

    obinfo_trading = data['writeData']['trading'] #매매금액    
    obinfo_deposit1 = data['writeData']['deposit1'] #보증금1
    if obinfo_trading == '' and obinfo_deposit1 == '' :
        pyautogui.alert("거래금액은 필수입니다. 확인후 다시 시작하세요~")
        driver.quit()
        return
        # driver.close()
    obinfo_deposit2 = data['writeData']['deposit2'] #보증금2
    obinfo_deposit3 = data['writeData']['deposit3'] #보증금3
    obinfo_rent1 = data['writeData']['rent1'] #월세1
    obinfo_rent2 = data['writeData']['rent2'] #월세2
    obinfo_rent3 = data['writeData']['rent3'] #월세3
    obinfo_ttype = data['writeData']['object_ttype'] #거래종류

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
        add_usedate = str(data['buildingData']['building_usedate']) #준공일
        building_options = data['buildingData']['building_option'] #건물옵션
        building_importants = data['buildingData']['building_important'] #건물옵션
        add_pn = data['buildingData']['building_pn'] #주차
        building_loan = data['buildingData']['building_loan'] #대출금(건물)
        sum_deposit = data['buildingData']['sum_deposit'].decode('utf-8') #총보증금
        sum_rent = data['buildingData']['sum_rent'].decode('utf-8') #총월세
        sum_mmoney = data['buildingData']['sum_mmoney'] #총관리비
        sum_etc = data['buildingData']['sum_etc'] #기타비용
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
        secret_4 = '' if data['roomData']['room_memo'] == '' else data['roomData']['room_memo'] + Keys.ENTER
        basic_secret += secret_4
        main_area = basic_area1
        main_option += ','+room_options if main_option != '' else room_options
        main_important += ','+add_importants if main_important != '' else add_importants
    basic_secret = formatted_date+" "+admin_name + Keys.ENTER +" https://obangkr.cafe24.com/web/request/request_view/view_give_request_detail.php?request_code="+request_code
    print("등록될 상세주소:", location_detail)
    main_area_pyeong = str(int(float(main_area)/3.305785)) if main_area != '' else ''

    obinfo_type = ''
    obinfo_type2 = ''
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

        elif object_type == '상업용':
            obinfo_type = '상가/사무실'
        elif object_type == '공업용':
            obinfo_type = '공장/창고'
    elif tr_target == '건물':
        object_info_code = building_code
        obinfo_type = '통건물'
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
                                    

            query = f'SELECT object_ori_img FROM pr_object WHERE object_code_new="{object_code_new}"'
            cursor.execute(query)
            result = cursor.fetchone() 
            object_ori_img = result['object_ori_img'].decode('utf-8')
            print("result:",result)
            print("object_ori_img:",object_ori_img)
            if result and object_ori_img == 'N':
                print("object_ori_img 값은 'N'입니다.") 
                update_query = f'UPDATE pr_object SET object_ori_img="Y" WHERE object_code_new="{object_code_new}"'
                cursor.execute(update_query)
                conn.commit()
                 
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

    print("object_info_code:",object_info_code)




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
            driver.find_element(By.XPATH, '//*[@id="sido"]').send_keys(location_do)
            # time.sleep(0.5)
            driver.find_element(By.XPATH, '//*[@id="gugun"]').send_keys(location_si)
            # time.sleep(0.5)
            driver.find_element(By.XPATH, '//*[@id="dong"]').send_keys(location_dong)
            lijibun = location_lijibun.replace(" ", "") #리+지번 공백제거
            driver.find_element(By.XPATH, '//*[@id="bunzi_start"]').send_keys(lijibun)
        
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
            pyautogui.alert(location_detail+f'\n\n등록된 매물[{검색된첫번째매물번호}]이 존재합니다. 신규등록을 종료합니다.')
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
                        if gugun.text == location_si:
                            gugun.click()
                            time.sleep(0.1)
                            dongs = driver.find_elements(By.XPATH, '//*[@id="dong_section"]/ul/li/div/button')
                            for dong in dongs:
                                if dong.text == location_dong:
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
            print("물건종류:", obinfo_type)
            for 매물 in driver.find_elements(By.NAME, 'category'):
                if 매물 == obinfo_type:
                    매물.click()
            if obinfo_type != '':
                driver.find_element(By.ID, f'category_{sele[obinfo_type][0]}').click() #매물 종류
                # pyautogui.alert(obinfo_type2)
                if len(sele[obinfo_type][1]) != 0: # 소분류
                    for a in driver.find_elements(By.CLASS_NAME, f'main_{sele[obinfo_type][0]}'):
                        print(a.text)
                        if a.text == obinfo_type2: 
                            a.click()
            # driver.find_element(By.ID, f'category_{sele["원룸"][0]}').click() # 거래종류
            # 거래종류
            for a in driver.find_elements(By.XPATH, '//*[@id="product_form"]/div[1]/div[2]/div[2]/div[3]/div[2]/div/div'):
                # print(a.text)
                if a.text == obinfo_ttype: 
                    a.click()
            time.sleep(0.1)
            #매매가
            if driver.find_element(By.XPATH, '//*[@id="sell_price"]').is_displayed() and obinfo_trading !='' : driver.find_element(By.XPATH, '//*[@id="sell_price"]').send_keys(obinfo_trading) 
            
            #융자
            if driver.find_element(By.XPATH, '//*[@id="lease_price"]').is_displayed() and str(object_loan) !='' : driver.find_element(By.XPATH, '//*[@id="lease_price"]').send_keys(str(building_loan)) 
            #총보증금
            if driver.find_element(By.XPATH, '//*[@id="sell_price_area"]/span[2]/input').is_displayed() and str(sum_deposit) !='' : driver.find_element(By.XPATH, '//*[@id="sell_price_area"]/span[2]/input').send_keys(str(sum_deposit))
            #총월세
            if driver.find_element(By.XPATH, '//*[@id="sell_price_area"]/span[3]/input').is_displayed() and str(sum_rent) !='' : driver.find_element(By.XPATH, '//*[@id="sell_price_area"]/span[3]/input').send_keys(str(sum_rent))
            
            
            print("obinfo_deposit1: "+obinfo_deposit1, "obinfo_rent1: "+obinfo_rent1)

            #전세의 보증금1
            if driver.find_element(By.XPATH, '//*[@id="full_price_area"]').is_displayed() and (obinfo_rent1=='' or obinfo_rent1=='0'): driver.find_element(By.XPATH, '//*[@id="full_rent_price"]').send_keys(obinfo_deposit1) 
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
                #지하층
                driver.find_element(By.XPATH, '//*[@id="current_floor"]').send_keys(building_ugrndflr) #지하층수
                #지상층
                driver.find_element(By.XPATH, '//*[@id="total_floor"]').send_keys(building_grndflr) #지상층수   
            if tr_target == '토지':
                #대지면적
                driver.find_element(By.XPATH, '//*[@id="land_area"]').send_keys(land_totarea) #대지면적                

            if tr_target != '토지':
                print("입주일:", add_rdate)  
                print("준공일:", add_usedate)    
            # driver.find_element(By.XPATH, '//*[@id="enter_year"]').send_keys('즉시입주') # 입주일
            # pyautogui.alert("준공일 차례")
            if obinfo_type not in ['상가/사무실','토지']:
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
        print('오방 등록수정과정 시작')
        try:
            # import datetime

            # WebDriverWait(driver, 10).until(EC.element_to_be_clickable(By.CSS_SELECTOR, "#search_id")).clear() #매물번호 입력창의 입력값 초기화
            driver.implicitly_wait(10)
            driver.find_element(By.CSS_SELECTOR, "#search_id").clear() 
            print("1", obang_code)
            driver.find_element(By.CSS_SELECTOR, "#search_id").send_keys(obang_code) #매물번호입력창에 매물번호 입력
            print("2")
            driver.find_element(By.CSS_SELECTOR, "#admin_member_id > option:nth-child(1)").click() #담당자를 직원별로 선택
            print("3")
            driver.find_element(By.CSS_SELECTOR, "#go_keyword").click() #검색버튼(돋보기) 클릭
            print("4")
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
                print('검색매물수.text') 
            

            #업데이트 실행
            driver.find_element(By.CSS_SELECTOR, f'#tr_{obang_code} > td:nth-child(14) > div:nth-child(1)').click() #관리 클릭
            print("5")
            
            # id="search-items"인 tbody 안에 첫 번째 tr의 14번째 td를 찾기
            관리_td = driver.find_element(By.XPATH, '//tbody[@id="search-items"]/tr[1]/td[14]')
            # 해당 td 안의 모든 li 태그 내의 a 태그를 찾기
            관리내항목 = 관리_td.find_elements(By.XPATH, './/li/a')

            # "수정" 텍스트가 포함된 항목이 있는지 확인
            수정_있음 = False  # "수정" 텍스트를 찾았는지 여부를 추적하는 플래그
            for 항목 in 관리내항목:
                if "수정" in 항목.text:
                    수정_있음 = True
                    print(f'찾은 항목: {항목.text}')  # "수정" 텍스트를 포함하는 항목 출력
            if not 수정_있음:
                print("텍스트 '수정'을 포함하는 항목이 없습니다.")
                pyautogui.alert("등록된 매물의 담당자를 확인해주세요~")
                driver.quit()
                return
            # pyautogui.alert("확인")           
            # time.sleep(1)
            driver.find_element(By.CSS_SELECTOR, f'#tr_{obang_code} > td:nth-child(14) > div.dropdown.open > ul > li:nth-child(1)').click() #수정 클릭
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
                        print(a.text+" 클릭!!!")
                        a.click()  
            # pyautogui.alert("소분류확인")                      
            #전세보증금
            if obinfo_deposit1 != '' : modify_item(driver, "#full_rent_price", obinfo_deposit1)
            #보증금1
            if obinfo_deposit1 != '' : modify_item(driver, "#monthly_rent_deposit", obinfo_deposit1)
            #월세1
            if obinfo_rent1 != '' : modify_item(driver, "#monthly_rent_price", obinfo_rent1)
            #매매
            # print("obinfo_trading: "+obinfo_trading)
            if obinfo_trading != '' : modify_item(driver, "#sell_price", obinfo_trading)

            #관리비
            if basic_manager=='별도':
                modify_item(driver, "#mgr_price", basic_mmoney)
            
            if tr_target == '층호수':
                # 관리내역
                관리내역s = driver.find_elements(By.XPATH, '//*[@id="mgr_include_checkbox"]/input')
                #물건의 관리비포함내역
                관리내역ex = basic_mlist.split(',')
                # '일반관리' 항목을 리스트의 끝에 추가
                관리내역ex.append('일반관리')
                try:
                    for item in 관리내역ex:
                        for 관리내역 in 관리내역s:
                            if item in 관리내역.get_attribute("value"):
                                관리내역.click()
                                break
                except:
                    print(관리내역ex)
                #실면적
                if basic_area1 != '' : modify_item(driver, "#real_area", basic_area1)
                #해당층
                if basic_floor != '' : modify_item(driver, "#current_floor", basic_floor)
                # 입주일
                driver.find_element(By.XPATH, '//*[@id="enter_year"]').clear() 
                driver.find_element(By.XPATH, '//*[@id="enter_year"]').send_keys('즉시입주') 
            #전체층
            # print("전체층: ", type(basic_totflr))
            # pyautogui.alert("전체층: ", basic_totflr)
            # modify_item(driver, "#total_floor", basic_totflr)

            print("비밀메모:", basic_secret)
            # # 수정시 비밀메모를 추가
            # secret_box = driver.find_element(By.XPATH, '//*[@id="info_base"]/div[2]/div[13]/div[2]/textarea')
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
                main_important = add_importants.split(',') #옵션을 리스트로 분리
                # 두 리스트를 집합으로 변환하고 중복을 제거한 후 합친다.
                main_collection = list(set(main_options + main_important))
                # print("main_options:",main_options)        
                given_optionboxs = driver.find_elements(By.XPATH, '//*[@id="option"]/div/label')
                # 변경할 main_options옵션의 매핑 정보를 담은 딕셔너리 생성
                replace_options = {
                    # "벽걸이에어컨": "에어컨",
                    # "전자도어락": "디지털도어락",
                    "가스렌지": "가스레인지",
                    "지상주차장": "주차장",
                    "지하주차장": "주차장",
                    "벽걸이에어컨": "에어컨",
                    "천정형에어컨": "에어컨",
                    "건물CCTV": "CCTV",
                    "전자렌지": "전자레인지",
                    "구분공간": "내실",
                    # 필요한 경우 여기에 더 많은 옵션을 추가할 수 있습니다.
                }    
                # 리스트의 각 요소에 대해 딕셔너리를 확인하고, 해당하는 키가 있으면 그 값을 가져와 대체
                updated_options = [replace_options.get(option.strip(), option.strip()) for option in main_collection]
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
                updated_importants = [replace_importants.get(important.strip(), important.strip()) for important in main_collection]
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
                # for given_optionbox in given_optionboxs:
                #     # 각 레이블 내부의 input 요소 찾기
                #     input_element = given_optionbox.find_element(By.TAG_NAME, 'input')
                    
                #     # input 요소의 value 속성 값 가져오기
                #     given_option = input_element.get_attribute('value').strip()
                #     # 현재 옵션의 활성화 상태 확인
                #     is_active = "active" in given_optionbox.get_attribute("class")
                #     # print("주어진 옵션: "+given_option+"--------------------")  # input의 value 출력      
                #     for option in updated_options:
                #         # print(option)
                #         if option == given_option and not is_active:
                #             # print(option+" 옵션있음")
                #             given_optionbox.click()                    
                #     # # input 요소의 value 속성 값 가져오기
                #     # given_option = input_element.get_attribute('value')
                #     # # print("주어진 옵션: "+given_option+"--------------------")  # input의 value 출력      
                #     # for option in updated_options:
                #     #     # print(option)
                #     #     if option == given_option:
                #     #         # print(option+" 옵션있음")
                #     #         given_optionbox.click()
            
            # #테마
            # if tr_target != '토지':
            #     main_important = add_importants.split(',') #옵션을 리스트로 분리
            #     given_importantboxs = driver.find_elements(By.XPATH, '//*[@id="info_add"]/div[2]/div[17]/div[2]/div/label')
            #     # 변경할 main_important옵션의 매핑 정보를 담은 딕셔너리 생성
            #     replace_importants = {
            #         # "벽걸이에어컨": "에어컨",
            #         "복층형": "복층형 구조",
            #         "무권리": "권리금 무",
            #         "전세대출가능": "전세대출",
            #         "천정형에어컨": "천정에어컨",
            #         "전자렌지": "전자레인지",
            #         "지상주차장": "주차장",
            #         # 필요한 경우 여기에 더 많은 옵션을 추가할 수 있습니다.
            #     }    
            #     # 리스트의 각 요소에 대해 딕셔너리를 확인하고, 해당하는 키가 있으면 그 값을 가져와 대체
            #     updated_importants = [replace_importants.get(important.strip(), important.strip()) for important in main_important]
            #     if "엘리베이터" in updated_options:
            #         updated_importants.append("엘리베이터")  # 있다면 updated_importants에 추가    
            #     if "주차장" in updated_options:
            #         updated_importants.append("주차장")  # 있다면 updated_importants에 추가    
            #     if tr_target == '층호수':
            #         if basic_floor == '1':
            #             print("1층 추가")
            #             updated_importants.append("1층")    
            #     print("updated_importants:",updated_importants)
                
            #     for given_importantbox in given_importantboxs:
            #         input_element = given_importantbox.find_element(By.TAG_NAME, 'input')
            #         given_important = given_importantbox.text.strip().replace('\n', ' ').replace('<br>', ' ')  # 텍스트 정리
            #         is_active = "active" in given_importantbox.get_attribute("class")
            #         # DB에 정의된 테마가 현재 선택되지 않았다면 선택
            #         if given_important in updated_importants and not is_active:
            #             given_importantbox.click()
            #         # 현재 선택된 테마가 DB에 없다면 선택 해제
            #         elif given_important not in updated_importants and is_active:
            #             given_importantbox.click()         
            #     # if updated_importants != '':
            #     #     for given_importantbox in given_importantboxs:
            #     #         # 각 레이블 내부의 input 요소 찾기
            #     #         input_element = given_importantbox.find_element(By.TAG_NAME, 'input')
            #     #         # input 요소의 value 속성 값 가져오기
            #     #         # given_important = input_element.get_attribute('text')   
            #     #         print("주어진 특징: "+given_importantbox.text+"--------------------")  # input의 value 출력     
            #     #         for important in updated_importants:
            #     #             print(important)
            #     #             if important == given_importantbox.text:
            #     #                 given_importantbox.click()
            pass 

#################            
            #설명
            object_detail = '[ 매 물 기 본 정 보 ]'
            if obinfo_trading != '':
                object_detail += '<p>' + f'● 매매금액: {숫자한글로금액변환(obinfo_trading)}</p>' 
                if sum_deposit == '':
                    print("보증금이 공백입니다.")
                else:
                    print("보증금이 존재합니다.")
                object_detail += ('<p>' + f'● 총보증금: {숫자한글로금액변환(sum_deposit)}</p>') if str(sum_deposit) != '' else '' 
                if sum_rent != '':
                    object_detail += ('<p>' + f'● 총월세: {숫자한글로금액변환(sum_rent)}</p>') if str(sum_rent) != '' else ''             
                    
            elif obinfo_deposit1 != '':
                object_detail += '<p>' + f'● 보증금: {obinfo_deposit1}만원</p>' 
                if obinfo_rent1 != '':
                    object_detail += '<p>' + f'● 월세: {obinfo_rent1}만원</p>'
                if basic_manager == '별도' and float(basic_mmoney) > 0:
                    object_detail += '<p>' + f'● 관리비: {basic_mmoney}만원</p>'
                # if premium_exist == '있음' & premium > 0:
                #     object_detail += f'● 권리금: {premium}만원'
            if object_type == '주거용' and tr_target == '층호수':
                object_detail += (('<p>' + f'● 방: {int(float(basic_rcount))}개')+(f' / 욕실:{basic_bcount}개</p>' if float(basic_rcount) > 0 else '')) if float(basic_rcount) > 0 else ''
            else:
                if tr_target == '건물':
                    object_detail += ('<p>' + f'● 총층: {str(building_grndflr-building_ugrndflr)}층 (지상{str(building_grndflr)}층 / 지하{str(building_ugrndflr)}층)</p>') if int(building_grndflr-building_ugrndflr) > 0 else ''
                elif tr_target == '층호수':
                    if main_area != '':
                        object_detail += ('<p>' + f'● 면적: {main_area}㎡ (약{main_area_pyeong}평)</p>') if float(main_area) > 0 else ''
            
            object_detail += ('<p>' + f'● 건물옵션:{building_options}</p>') if (building_options != '' and tr_target != '토지') else ''
            object_detail += ('<p>' + f'● 호실옵션:{room_options}</p>') if (room_options != '' and tr_target == '층호수') else ''
            object_detail += '<p>' + f'● 위치: </p>'
            
            object_detail += '<p>' + '<br>' + '[ 매 물 주 요 특 징 ]</p>'
            object_detail += '<p>' + 'ㅇ </p>'
            object_detail += '<p>' + 'ㅇ </p>'
            
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
            text_area = driver.find_element(By.XPATH, '//body/p')
            
            # 텍스트 영역의 현재 내용 확인 (HTML 태그 제거)
            current_content = text_area.get_attribute('innerHTML').strip()
            # 현재 내용이 비어있는 경우에만 detail 입력
            print("current_content:", current_content)
            # 현재 내용이 <br>만 있거나 비어있는 경우에만 detail 입력
            if current_content == '' or current_content == '<br>':
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
            print("에러 발생:", str(e))
            pyautogui.alert("에러 발생:"+ str(e))
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
            # # JavaScript를 사용하여 등록버튼에 포커스 이동
            # driver.execute_script("arguments[0].focus();", 등록버튼)
            print("등록완료 종료")
            # pyautogui.alert(f"등록완료 확인!! land_code:{land_code} building_code:{building_code} room_code:{room_code}")
            
            # 검색초기화 필요시
            driver.get('https://osanbang.com/adminproduct/clean/')
            
            등록된오방번호 = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//tbody[@id="search-items"]/tr[1]/td[2]/a/strong'))
            ).text
            
            #등록된 오방매물번호 DB에 등록
            try:
                update_query = f"UPDATE pr_object SET object_code_obang='{등록된오방번호}' WHERE object_code_new='{object_code_new}'"
                cursor.execute(update_query)
                conn.commit()
                # pyautogui.alert(f"등록된 오방번호: {등록된오방번호}")
            except Exception as e:
                print("An error occurred:", e)
                traceback.print_exc()
                # pyautogui.alert(f"매물번호 업데이트오류: 새홈[{object_code_new}] => 오방번호[{등록된오방번호}]") 
            # pyautogui.alert(f"새홈[{object_code_new}]의 등록된오방번호[ {등록된오방번호} ]")
        except Exception as e:
            print("등록완료시키기 에러발생:", str(e))
    else: #수정등록시 종료확인
        pyautogui.alert(f"새홈매물번호: {object_code_new}\n{location_detail} \n\n작업을 종료하시겠습니까?")
  
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