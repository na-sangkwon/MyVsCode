#테스트용파일

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options

import pyautogui 
import time

# options = Options()

# options.add_argument("--disable-blink-features=AutomationControlled")

# # ChromeDriver 경로 설정
# driver = webdriver.Chrome('/chromedriver', options=options)
# driver = webdriver.Chrome(options=options)

# driver.maximize_window()

# # driver.get('https://mobile.karhanbang.com/kren/mamul/list')
# driver.get('https://osan-bns.com/admin_item/insert') #오부사 신규등록페이지

# # driver.get('https://mobile.karhanbang.com/snsLogin/login')
# driver.execute_script('return document.getElementById("realtorYn").click()') #개업공인중개사여부 체크
# driver.find_element(By.XPATH, '//*[@id="userId"]').send_keys('bsleemanse')
# driver.find_element(By.XPATH, '//*[@id="userPw"]').send_keys('tkdrnjs1001')
# driver.find_element(By.XPATH, '//*[@id="loginBtn"]/a/span').click()

# WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="in_search_so"]'))).click()
# 한방번호 = ''
# options = driver.find_elements(By.XPATH, '//*[@id="in_search_so"]/option')
# if 한방번호 != '':
#     print('한방번호가 존재할때')
#     choice = '한방매물번호'
# else:
#     print('한방번호가 존재하지 않을 때')
#     choice = '본번-부번'
# for opt in options:
#     print(opt.text)
#     if opt.text == choice: 
#         opt.click()
#         driver.find_element(By.XPATH, '//*[@id="in_keyword"]').send_keys('640-9')
#         driver.find_element(By.XPATH, '//*[@id="mainSearchBtn"]').click()
#         break

# result = pyautogui.confirm('\n\n 매물등록을 진행하시겠습니까?', buttons=['예', '아니오'])    
# if result == '예':
#     driver.get('https://mobile.karhanbang.com/kren/mamul/regist')
    
# pyautogui.alert("이상없습니까?") 
# driver.quit()

import object_data
import os
import pymysql
from ftplib import FTP
from pathlib import Path
import datetime

# # FTP 서버에 연결
# with FTP('obangkr.cafe24.com', 'obangkr', 'Ddhqkd!1') as ftp:
#     try:
#         # 디렉토리 존재 확인
#         ftp.cwd('img/web/object/object_img/220922_L0300B01R001')
#         print("The directory exists on the FTP server.")
#     except:
#         print("The directory does not exist on the FTP server.")
# quit()
userid = '상가팀원'
userpw = '1234'
# # getData 함수 호출
# result_data = object_data.getData('19801', '상가팀원', '1234')
    
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


#ftp서버에 DB연결
conn = pymysql.connect(host='obangkr.cafe24.com', user='obangkr', password='Ddhqkd!1', charset='utf8')
cursor = conn.cursor(pymysql.cursors.DictCursor)
cursor.execute('USE obangkr;')     

query = f'SELECT object_code_new,tr_target,land_code,building_code,room_code FROM pr_object WHERE object_del="N" AND object_ori_img="N"'
cursor.execute(query)
result = cursor.fetchall() 

# 결과 개수 확인
row_count = cursor.rowcount
print(f"쿼리 실행 결과 개수: {row_count}")
count = 1
for row in result:
    object_code_new = row['object_code_new'].decode('utf-8')
    tr_target = row['tr_target'].decode('utf-8')
    land_code = row['land_code'].decode('utf-8')
    building_code = row['building_code'].decode('utf-8')
    room_code = row['room_code'].decode('utf-8')

    # getData 함수 호출
    result_data = object_data.getData(object_code_new, userid, userpw)
    # 리턴된 데이터 사용
    adminData = result_data.get("adminData")
    writeData = result_data.get("writeData")
    folderPath = result_data.get("folderPath")
    type_path = result_data.get("type_path")
    # print("folderPath:" , folderPath)
    
    errarr = []
    try:
        #물건의 원본사진폴더에 이미지가 존재하는지
        main_dir = 'Z:\\업무자료\\4사진자료&이미지자료(외부유출금지)\\1주거용물건, 상업용물건\\'
        path_dir = main_dir + folderPath #'경기도\\오산시\\궐동\\654-9\\썬플라워\\1층\\1층'
        print(path_dir)
        
        file_list = os.listdir(path_dir)   
        # print("file_list:", file_list)
        
        원본사진들 = [] #원본사진파일들을 담을 빈 리스트
        변환폴더생성일모음 = [] #변환된 사진폴더의 년월일을 담을 빈 리스트
        for file in file_list:
            # 파일 확장자를 소문자로 변환하여 비교
            if file.lower().endswith(('.jpeg', '.gif', '.png', '.jpg')):
                원본사진들.append(file)  
            # if file.endswith('.jpeg') or file.endswith('.gif') or file.endswith('.png') or file.endswith('.jpg') or file.endswith('.JGP'):
            #     원본사진들.append(file)          
        # print("원본사진들:", 원본사진들)
        if len(원본사진들) == 0: #물건의 원본사진없음
            print("원본사진폴더에 이미지 없음")
            # driver.execute_script('document.getElementById("is_speed").checked = true') #급매체크
            pass
        else: #원본사진폴더에 이미지 존재=>DB에 샘플이미지를 등록
            print("원본사진폴더에 이미지 존재")  
            if tr_target == '토지':
                object_info_code = room_code
            elif tr_target == '건물':
                object_info_code = room_code
            elif tr_target == '층호수':
                object_info_code = room_code
                
            #ftp서버에 DB연결
            conn = pymysql.connect(host='obangkr.cafe24.com', user='obangkr', password='Ddhqkd!1', charset='utf8')
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute('USE obangkr;')      
            
            query = f'SELECT object_ori_img FROM pr_object WHERE object_code_new="{object_code_new}" AND object_ori_img="N"'
            cursor.execute(query)
            result = cursor.fetchone() 
            object_ori_img = result['object_ori_img'].decode('utf-8')
            print("result:",result)
            print("object_ori_img:",object_ori_img)
            #pr_object의 object_ori_img값 수정
            if result and object_ori_img == 'N':
                print("object_ori_img 값은 'N'입니다.") 
                update_query = f'UPDATE pr_object SET object_ori_img="Y" WHERE object_code_new="{object_code_new}"'
                cursor.execute(update_query)
                conn.commit()
            #변환된 사진폴더의 생성일모음 생성                                
            for filename in file_list:
                if "output" in filename: 변환폴더생성일모음.append(filename.split('output')[1])
            #pr_object_img의 output_folder필드에 들어갈 값 지정
            output_folder = max(변환폴더생성일모음)
            print("output_folder:", output_folder)      
    except Exception as e: 
        print("폴더 오류", str(e))
        errarr.append("폴더 오류")
        pass    
    
        # 사진
        # filePath = driver.find_element(By.XPATH, '//*[@id="product_form"]/div[1]/div[9]/div[2]/div[1]/div/div').get_attribute("outerHTML").split('<input id="')[1].split('" t')[0]
        

    if len(변환폴더생성일모음)>0:
        try:
            print("변환폴더생성일모음:", 변환폴더생성일모음)     
            #가장 최근에 변환된 사진이 있는 폴더지정
            path = path_dir + "/output" + max(변환폴더생성일모음) # 제일 큰 output찾기

            photo_list = [] #변환된 최근사진을 담을 빈 리스트
            for file in os.listdir(path):
                if file.lower().endswith(('.jpeg', '.gif', '.png', '.jpg')):
                    photo_list.append(file)
            print("photo_list:",photo_list)
            print('사진갯수:', len(photo_list))
            
            ftp_directory = 'img/web/object/object_img/'+object_info_code

            
            with FTP('obangkr.cafe24.com', 'obangkr', 'Ddhqkd!1') as ftp:
                # ftp.set_debuglevel(2)  # 디버깅 레벨 설정
                if not is_directory_exists(ftp, ftp_directory):
                    print("신규등록시 디렉토리생성:", ftp_directory)  
                    ftp.mkd(ftp_directory)     
                else:
                    print("신규등록시 디렉토리가 이미 존재합니다.")  
                    print(f"The FTP directory is: {ftp_directory}")  # ftp_directory 변수 값 확인
                    remove_existing_files(ftp, ftp_directory) # 기존 파일 제거                                                  
            
            #매물의 기존 대표이미지정보 삭제후 최신정보 저장 
            query = f'DELETE FROM pr_object_img WHERE object_info_code="{object_info_code}"'
            cursor.execute(query)
            index = 0
            
            small_file = 가장용량이작은파일찾기(photo_list, path)

            # 파일 경로를 생성
            small_file_path = os.path.join(path, small_file)

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

            # 파일 업로드가 성공적으로 완료되었다는 메시지 출력
            print(f'File "{small_file}" has been successfully uploaded')

        except Exception as e: 
            print("사진 오류", str(e))
            pass
    else:
        print("변환된 폴더없음")
    print(count)
    count += 1
    time.sleep(0.2)


cursor.close()
conn.close()