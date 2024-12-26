#테스트용파일

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options

import pyautogui 
import time

import object_data
import os
import pymysql
from ftplib import FTP
from pathlib import Path
import datetime

import tkinter as tk
from tkinter import simpledialog
from tkinter import messagebox

userid = '상가팀원' #brst4517
userpw = '1234' #ljs13466!
# 데이터베이스 연결 및 기타 초기 설정
def 데이터베이스_연결_초기화():
    return pymysql.connect(host='obangkr.cafe24.com', user='obangkr', password='Ddhqkd!1', charset='utf8')

def 데이터베이스_데이터_가져오기(cursor):
    # 사용자로부터 입력 받는 함수
    def get_user_input():
        # Tkinter 창 생성 (창은 숨겨집니다)
        root = tk.Tk()
        root.withdraw()

        while True:
            # 간단한 대화 상자를 통해 사용자 입력 받기
            user_input = simpledialog.askstring("..", "업데이트할 데이터 개수\n\n최근수정된 데이터 기준\n\n예시)\n50 => 최근수정된 50개데이터", initialvalue="50")
            # 사용자가 취소를 누른 경우
            if user_input is None:
                break
            return int(user_input)  # 숫자로 변환하여 반환

        # 입력된 값 반환
        return user_input
    limit_value = get_user_input()
    query = f'SELECT object_code_new,tr_target,land_code,building_code,room_code FROM pr_object WHERE object_del="N" AND object_out_img="N"'
    # query = f'SELECT object_code_new,tr_target,land_code,building_code,room_code FROM pr_object WHERE object_del="N" AND object_m="N"'
    if limit_value >= 100000:
         query += f' AND object_code_new="{limit_value}"'
    else:
        query += ' ORDER BY object_udate DESC, object_utime DESC'
        query += f' LIMIT {limit_value}'
    # query = f'SELECT object_code_new,tr_target,land_code,building_code,room_code FROM pr_object WHERE object_del="N" AND object_m="Y" AND object_ori_img="N"'
    cursor.execute(query)
    return cursor.fetchall()
    
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



# 가져온 데이터를 처리하는 함수
def 데이터_처리(cursor, row):
    object_code_new = row['object_code_new'].decode('utf-8')
    tr_target = row['tr_target'].decode('utf-8')
    land_code = row['land_code'].decode('utf-8')
    building_code = row['building_code'].decode('utf-8')
    room_code = row['room_code'].decode('utf-8')

    if ((tr_target=='층호수' and room_code=='') or (tr_target=='건물' and building_code=='')): return
    room_query = f'SELECT room_floor FROM pr_room WHERE room_code="{room_code}" AND room_del="N"'
    cursor.execute(room_query)
    room_result = cursor.fetchone()     
    # room_result가 None이거나 room_floor가 비어있는 경우, 다음 루프로 넘어갑니다.
    if room_result is None or room_result['room_floor'] == '':
        print("데이터처리중 1")
        return
    print("데이터처리중 2")
    time.sleep(0.1)
    # getData 함수 호출
    result_data = object_data.getData(object_code_new, userid, userpw)
    # 리턴된 데이터 사용
    adminData = result_data.get("adminData")
    writeData = result_data.get("writeData")
    folderPath = result_data.get("folderPath")
    # print("folderPath:" , folderPath)
    type_path = result_data.get("type_path")
    
    errarr = []
    원본사진들 = [] #원본사진파일들을 담을 빈 리스트
    변환폴더생성일모음 = [] #변환된 사진폴더의 년월일을 담을 빈 리스트
    try:
        #물건의 원본사진폴더에 이미지가 존재하는지
        main_dir = 'Z:\\업무자료\\4사진자료&이미지자료(외부유출금지)\\1주거용물건, 상업용물건\\'
        path_dir = main_dir + folderPath #'경기도\\오산시\\궐동\\654-9\\썬플라워\\1층\\1층'
        # main_dir = Path('Z:/업무자료/4사진자료&이미지자료(외부유출금지)/1주거용물건, 상업용물건/')
        # path_dir = main_dir / folderPath #'경기도\\오산시\\궐동\\654-9\\썬플라워\\1층\\1층'
        # # print(path_dir)
        # path_dir = Path("Z:/업무자료/4사진자료&이미지자료(외부유출금지)/1주거용물건, 상업용물건/경기도/오산시/궐동/645-5/황금빌/4층/406호") #

        if os.path.exists(path_dir):
            print(f"{path_dir} 접근 가능")
        else:
            print(f"{path_dir} 접근 불가능") 
        # for part in folderPath.split('\\'):
        #     main_dir /= part  # 경로 추가
        #     print(f"Checking {main_dir}...")
        #     if main_dir.exists():
        #         print(f"{main_dir} exists.")
        #     else:
        #         print(f"{main_dir} does not exist.")
        #         break  
            
        file_list = os.listdir(path_dir)   
        # print("file_list:", file_list)

        for file in file_list:
            # 파일 확장자를 소문자로 변환하여 비교
            if file.lower().endswith(('.jpeg', '.gif', '.png', '.jpg')):
                원본사진들.append(file)         
        # print("원본사진들:", 원본사진들)
        if len(원본사진들) == 0: #물건의 원본사진없음
            print("원본사진폴더에 이미지 없음")
            # driver.execute_script('document.getElementById("is_speed").checked = true') #급매체크
            pass
        else: #원본사진폴더에 이미지 존재=>DB에 샘플이미지를 등록
            print("원본사진폴더에 이미지 존재")  
            if tr_target == '토지':
                object_info_code = land_code
            elif tr_target == '건물':
                object_info_code = building_code
            elif tr_target == '층호수':
                object_info_code = room_code
                
            # #ftp서버에 DB연결
            # conn = pymysql.connect(host='obangkr.cafe24.com', user='obangkr', password='Ddhqkd!1', charset='utf8')
            # cursor = conn.cursor(pymysql.cursors.DictCursor)
            # cursor.execute('USE obangkr;')      
            
            #원본사진폴더에 원본이미지는 존재하지만 DB에는 없는 걸로 되어있는 경우
            query = f'SELECT object_ori_img FROM pr_object WHERE object_code_new="{object_code_new}" AND object_ori_img="N"'
            cursor.execute(query)
            result = cursor.fetchone() 
            
            #pr_object의 object_ori_img값 수정
            if result:
                object_ori_img = result['object_ori_img'].decode('utf-8')
                print("object_ori_img:", object_ori_img)
                if object_ori_img == 'N':
                    print(f"매물({object_code_new})의 object_ori_img 값은 'N'입니다.") 
                    update_query = f'UPDATE pr_object SET object_ori_img="Y" WHERE object_code_new="{object_code_new}"'
                    cursor.execute(update_query)           
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
        
    if len(변환폴더생성일모음) == 0 and len(원본사진들) : pyautogui.alert(f"해당매물({object_code_new})은 원본사진만 존재합니다. 변환작업을 해주세요~")
        
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
                    

            # 파일 업로드가 성공적으로 완료되었다는 메시지 출력
            print(f'File "{small_file}" has been successfully uploaded')
            
            if len(photo_list) == 0: #output폴더에 사진없음
                print("output폴더에 이미지 없음")
                pass
            else: #output폴더에 이미지 존재
                print("output폴더에 이미지 존재")
                update_query = f'UPDATE pr_object SET object_out_img="Y" WHERE object_code_new="{object_code_new}"'
                cursor.execute(update_query)   
                print(f'pr_object테이블에서 매물({object_code_new})의 object_out_img="Y"로 변경예정')
        except Exception as e: 
            print("사진 오류", str(e))
            pass
    else:
        print("변환된 폴더없음")

    pass

# 메인 함수
def 메인():
    try:
        # 데이터베이스 연결을 초기화합니다.
        #ftp서버에 DB연결
        conn = 데이터베이스_연결_초기화()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('USE obangkr;')     
        
        # 데이터베이스에서 데이터를 가져옵니다.
        result = 데이터베이스_데이터_가져오기(cursor)
        # 결과 개수 확인
        row_count = cursor.rowcount
        print(f"쿼리 실행 결과 개수: {row_count}")
        pyautogui.alert(str(row_count)+"개의 매물을 사진업데이트를 진행합니다.")    
        count = 0
        for row in result:
            # 각 row에 대해 데이터 처리 함수를 호출합니다.
            데이터_처리(cursor, row)
            # time.sleep(0.2) 
            object_code_new = row['object_code_new'].decode('utf-8')
            count += 1
            # pyautogui.alert(f"{count}번째 매물번호:{object_code_new} 처리완료")
            print(count)
     

    except Exception as 예외:
        # 오류가 발생했을 경우, 오류 메시지를 출력합니다.
        print("메인 오류:", str(예외))
    finally:
        # 모든 데이터 처리가 끝난 후 변경 사항을 커밋합니다.
        conn.commit()   
        print(count,"개의 변환작업을 완료하였습니다.")
        # 작업이 완료되면 cursor와 conn을 닫습니다.
        cursor.close()
        conn.close()

# 파이썬 스크립트가 직접 실행될 때만 메인 함수를 호출합니다.
if __name__ == "__main__":
    메인()
    
    
    
# #ftp서버에 DB연결
# conn = pymysql.connect(host='obangkr.cafe24.com', user='obangkr', password='Ddhqkd!1', charset='utf8')
# cursor = conn.cursor(pymysql.cursors.DictCursor)
# cursor.execute('USE obangkr;')     

# query = f'SELECT object_code_new,tr_target,land_code,building_code,room_code FROM pr_object WHERE object_del="N" AND object_m="Y" AND object_ori_img="N"'
# cursor.execute(query)
# result = cursor.fetchall() 

# # 결과 개수 확인
# row_count = cursor.rowcount
# print(f"쿼리 실행 결과 개수: {row_count}")
# pyautogui.alert(str(row_count)+"개의 매물을 사진업데이트를 진행합니다.")
# count = 1
# for row in result:
#     object_code_new = row['object_code_new'].decode('utf-8')
#     tr_target = row['tr_target'].decode('utf-8')
#     land_code = row['land_code'].decode('utf-8')
#     building_code = row['building_code'].decode('utf-8')
#     room_code = row['room_code'].decode('utf-8')

#     if ((tr_target=='층호수' and room_code=='') or (tr_target=='건물' and building_code=='')): continue
#     room_query = f'SELECT room_floor FROM pr_room WHERE room_code="{room_code}" AND room_del="N"'
#     cursor.execute(room_query)
#     room_result = cursor.fetchone()     
#     # room_result가 None이거나 room_floor가 비어있는 경우, 다음 루프로 넘어갑니다.
#     if room_result is None or room_result['room_floor'] == '':
#         continue
#     time.sleep(0.1)
#     # getData 함수 호출
#     result_data = object_data.getData(object_code_new, userid, userpw)
#     # 리턴된 데이터 사용
#     adminData = result_data.get("adminData")
#     writeData = result_data.get("writeData")
#     folderPath = result_data.get("folderPath")
#     type_path = result_data.get("type_path")
#     # print("folderPath:" , folderPath)
    
#     errarr = []
#     원본사진들 = [] #원본사진파일들을 담을 빈 리스트
#     변환폴더생성일모음 = [] #변환된 사진폴더의 년월일을 담을 빈 리스트
#     try:
#         #물건의 원본사진폴더에 이미지가 존재하는지
#         main_dir = 'Z:\\업무자료\\4사진자료&이미지자료(외부유출금지)\\1주거용물건, 상업용물건\\'
#         path_dir = main_dir + folderPath #'경기도\\오산시\\궐동\\654-9\\썬플라워\\1층\\1층'
#         print(path_dir)
        
#         file_list = os.listdir(path_dir)   
#         # print("file_list:", file_list)
        
        
#         for file in file_list:
#             # 파일 확장자를 소문자로 변환하여 비교
#             if file.lower().endswith(('.jpeg', '.gif', '.png', '.jpg')):
#                 원본사진들.append(file)         
#         # print("원본사진들:", 원본사진들)
#         if len(원본사진들) == 0: #물건의 원본사진없음
#             print("원본사진폴더에 이미지 없음")
#             # driver.execute_script('document.getElementById("is_speed").checked = true') #급매체크
#             pass
#         else: #원본사진폴더에 이미지 존재=>DB에 샘플이미지를 등록
#             print("원본사진폴더에 이미지 존재")  
#             if tr_target == '토지':
#                 object_info_code = room_code
#             elif tr_target == '건물':
#                 object_info_code = room_code
#             elif tr_target == '층호수':
#                 object_info_code = room_code
                
#             #ftp서버에 DB연결
#             conn = pymysql.connect(host='obangkr.cafe24.com', user='obangkr', password='Ddhqkd!1', charset='utf8')
#             cursor = conn.cursor(pymysql.cursors.DictCursor)
#             cursor.execute('USE obangkr;')      
            
#             query = f'SELECT object_ori_img FROM pr_object WHERE object_code_new="{object_code_new}" AND object_ori_img="N"'
#             cursor.execute(query)
#             result = cursor.fetchone() 
#             object_ori_img = result['object_ori_img'].decode('utf-8')
#             print("result:",result)
#             print("object_ori_img:",object_ori_img)
#             #pr_object의 object_ori_img값 수정
#             if result and object_ori_img == 'N':
#                 print("object_ori_img 값은 'N'입니다.") 
#                 update_query = f'UPDATE pr_object SET object_ori_img="Y" WHERE object_code_new="{object_code_new}"'
#                 cursor.execute(update_query)
#                 conn.commit()
#             #변환된 사진폴더의 생성일모음 생성                                
#             for filename in file_list:
#                 if "output" in filename: 변환폴더생성일모음.append(filename.split('output')[1])
#             #pr_object_img의 output_folder필드에 들어갈 값 지정
#             output_folder = max(변환폴더생성일모음)
#             print("output_folder:", output_folder)      
#     except Exception as e: 
#         print("폴더 오류", str(e))
#         errarr.append("폴더 오류")
#         pass    
    
#         # 사진
#         # filePath = driver.find_element(By.XPATH, '//*[@id="product_form"]/div[1]/div[9]/div[2]/div[1]/div/div').get_attribute("outerHTML").split('<input id="')[1].split('" t')[0]
        

#     if len(변환폴더생성일모음)>0:
#         try:
#             print("변환폴더생성일모음:", 변환폴더생성일모음)     
#             #가장 최근에 변환된 사진이 있는 폴더지정
#             path = path_dir + "/output" + max(변환폴더생성일모음) # 제일 큰 output찾기

#             photo_list = [] #변환된 최근사진을 담을 빈 리스트
#             for file in os.listdir(path):
#                 if file.lower().endswith(('.jpeg', '.gif', '.png', '.jpg')):
#                     photo_list.append(file)
#             print("photo_list:",photo_list)
#             print('사진갯수:', len(photo_list))
            
#             ftp_directory = 'img/web/object/object_img/'+object_info_code

            
#             with FTP('obangkr.cafe24.com', 'obangkr', 'Ddhqkd!1') as ftp:
#                 # ftp.set_debuglevel(2)  # 디버깅 레벨 설정
#                 if not is_directory_exists(ftp, ftp_directory):
#                     print("신규등록시 디렉토리생성:", ftp_directory)  
#                     ftp.mkd(ftp_directory)     
#                 else:
#                     print("신규등록시 디렉토리가 이미 존재합니다.")  
#                     print(f"The FTP directory is: {ftp_directory}")  # ftp_directory 변수 값 확인
#                     remove_existing_files(ftp, ftp_directory) # 기존 파일 제거                                                  
            
#             #매물의 기존 대표이미지정보 삭제후 최신정보 저장 
#             query = f'DELETE FROM pr_object_img WHERE object_info_code="{object_info_code}"'
#             cursor.execute(query)
#             index = 0
            
#             small_file = 가장용량이작은파일찾기(photo_list, path)

#             # 파일 경로를 생성
#             small_file_path = os.path.join(path, small_file)

#             # FTP 연결 및 로그인
#             with FTP('obangkr.cafe24.com', 'obangkr', 'Ddhqkd!1') as ftp:
#                 # 최소 용량의 파일을 FTP 서버에 업로드
#                 with open(small_file_path, 'rb') as file:
                    
#                     # 현재 날짜와 시간을 얻음
#                     current_date = datetime.date.today().strftime("%Y-%m-%d")
#                     current_time = datetime.datetime.now().time().strftime("%H:%M:%S")
                    
#                     # FTP 서버에 파일 업로드
#                     ftp.cwd(ftp_directory)
#                     ftp.storbinary(f'STOR {small_file}', file)
                    
#                     # 데이터베이스에 파일 정보 저장
#                     query = f'''
#                         INSERT INTO pr_object_img 
#                         (object_code_new, object_info_code, output_folder, oimg_name, oimg_index, oimg_wdate, oimg_wtime, oimg_del) 
#                         VALUES 
#                         ("{object_code_new}", "{object_info_code}", "{max(변환폴더생성일모음)}", "{small_file}", "1", "{current_date}", "{current_time}", "N")
#                     '''
#                     cursor.execute(query)
#                     conn.commit()

#             # 파일 업로드가 성공적으로 완료되었다는 메시지 출력
#             print(f'File "{small_file}" has been successfully uploaded')

#         except Exception as e: 
#             print("사진 오류", str(e))
#             pass
#     else:
#         print("변환된 폴더없음")
#     print(count)
#     count += 1
#     time.sleep(0.2)


# cursor.close()
# conn.close()