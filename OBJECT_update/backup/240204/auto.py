#기존 두개의 파일을 한개의 파일로 합침

def obang_data(before_day):
    import pymysql
    import datetime

    # today = datetime.datetime.now().strftime("%Y-%m-%d")
    # print(today)

    # 현재 날짜 가져오기 (datetime 객체로)
    today = datetime.datetime.now().date()

    import tkinter as tk
    from tkinter import simpledialog, messagebox
    import threading
    import time

    import os



    # before_day 값 설정
    # before_day = get_user_input()
    # before_day = 1

    # 시작 날짜 계산
    start_date = today - datetime.timedelta(days=before_day)

    # 날짜를 문자열 형태로 변환
    today_str = today.strftime("%Y-%m-%d")
    start_date_str = start_date.strftime("%Y-%m-%d")

    conn = pymysql.connect(host='obangkr.cafe24.com', user='obangkr', password='Ddhqkd!1', charset='utf8')

    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('USE obangkr;')

    #최신등록일을 갱신할 오방코드 수집
    query = f'''SELECT * FROM pr_request AS p LEFT JOIN pr_request_give AS c ON p.request_code = c.request_code
        WHERE p.request_del="N"
        AND p.request_date BETWEEN "{start_date_str}" AND "{today_str}"
        AND p.request_main != "전체"
        AND p.tr_type = "내놓기"
        AND (p.request_status = "접수" OR p.request_status = "진행")'''
    cursor.execute(query)
    g_res = cursor.fetchall()
    num_rows = cursor.rowcount


    # print(num_rows)
    # print(query)
    # print(g_res[1]['land_code'],g_res[1]['building_code'],g_res[1]['room_code'])
    금일등록매물 = []
    미등록의뢰수 = 0
    img_update = [] #프로중개인 이미지 업데이트용
    obang_update = []

    for row in g_res:
        building_code = ''
        room_code = ''        
        if row['request_wdate'] == today_str :
            if o_res[0]['object_code_obang']=='':
                금일등록매물.append(str(o_res[0]['object_code_obang'].decode('utf8')))
            else:
                미등록의뢰수 += 1
        
        if row['land_code']:
            land_code = row['land_code'].decode('utf8') 
        else: 
            print('land_code is not ==> request_code:'+row['request_code'].decode('utf8'))
            continue
        if row['building_code']:building_code = row['building_code'].decode('utf8')
        if row['room_code']:room_code = row['room_code'].decode('utf8')
        print("land_code: "+land_code, "building_code: "+building_code, "room_code: "+ room_code)

        o_query = 'SELECT object_code_new,land_code,building_code,room_code,object_code_obang FROM pr_object WHERE object_del="N" AND land_code = %s AND building_code = %s AND room_code = %s'
        params = (land_code, building_code, room_code)
        cursor.execute(o_query, params)
        o_res = cursor.fetchall()
        
        try:
            if o_res[0]['object_code_obang'].decode('utf8') != '' : obang_update.append(str(o_res[0]['object_code_obang'].decode('utf8'))) 
            print("request_code: "+str(row['request_code'].decode('utf8')), "land_code: "+land_code, "building_code: "+building_code, "room_code: "+ room_code, str(o_res[0]['object_code_obang'].decode('utf8')))
        except:
            print("pass request_code: "+str(row['request_code'].decode('utf8')))
            pass
        
        #폴더경로 만들기
        # img_update.append(object_code_new) 
        tr_target = row['tr_target'].decode('utf8')
        print("tr_target:"+tr_target, "")
        if tr_target == '층호수' and room_code == '':
            print("호실정보없는 층호수의뢰: "+str(row['request_code'].decode('utf8')))
            pass
        else:
            object_code_new = o_res[0]['object_code_new'].decode('utf8')
            query = 'SELECT * FROM pr_land WHERE land_code = "%s"' % land_code
            cursor.execute(query)
            l_res = cursor.fetchall()
            for row in l_res:
                land_do = row['land_do'].decode('utf8') #시도
                land_si = row['land_si'].decode('utf8') #시군구
                land_dong = row['land_dong'].decode('utf8') #읍면동
                land_li = row['land_li'].decode('utf8') #리
                land_type = '산' if row['land_type'].decode('utf8') == '2' else '일반' #대장구분 일반:1 산:2
                land_jibun = row['land_jibun'].decode('utf8') #지번(숫자)  
                land_jibung = row['land_jibung'].decode('utf8') #지번(숫자)  
                
            if tr_target == '건물' or tr_target == '층호수':
                query = 'SELECT * FROM pr_building WHERE building_code = "%s"' % building_code
                cursor.execute(query)
                b_res = cursor.fetchall()   
                building_name = '' if b_res[0]['building_name'].decode('utf8') == '' else b_res[0]['building_name'].decode('utf8') #건물명
            
            if tr_target == '층호수':
                query = 'SELECT * FROM pr_room WHERE room_code = "%s"' % room_code
                cursor.execute(query)
                r_res = cursor.fetchall()
                room_num = r_res[0]['room_num'].decode('utf8') #호실명
                room_floor = '' if r_res[0]['room_floor'].decode('utf8') == '' else r_res[0]['room_floor'].decode('utf8') #호실층수
            
            do_path = land_do if land_do != '' else ''
            si_path = '\\'+land_si if land_si != '' else ''
            dong_path = '\\'+land_dong if land_dong != '' else ''
            li_path = '\\'+land_li if land_li != '' else ''
            type_path = '산' if land_type == '산' else ''
            jibun_path = '\\'+land_jibung if land_jibung != '' else ''
            folderPath = do_path + si_path + dong_path + li_path + type_path + jibun_path
            if tr_target == '건물' or tr_target == '층호수':
                building_name_path = '\\'+building_name if building_name != '' else ''
                folderPath += building_name_path
            if tr_target == '층호수':
                if room_floor != '':
                    room_floor = room_floor if int(room_floor) > 0 else '지하'+str(int(room_floor) * (-1))
                    floor_path = '\\'+room_floor+'층' if room_floor != '' else ''
                    num_path = '\\'+room_num+'' if room_num != '' else ''
                    folderPath += floor_path + num_path        
            
            errarr = []
            원본사진들 = [] #원본사진파일들을 담을 빈 리스트
            변환폴더생성일모음 = [] #변환된 사진폴더의 년월일을 담을 빈 리스트
            try:
                #물건의 원본사진폴더에 이미지가 존재하는지
                main_dir = 'Z:\\업무자료\\4사진자료&이미지자료(외부유출금지)\\1주거용물건, 상업용물건\\'
                path_dir = main_dir + folderPath #'경기도\\오산시\\궐동\\654-9\\썬플라워\\1층\\1층'

                if os.path.exists(path_dir):
                    print(f"{path_dir} 접근 가능")
                else:
                    print(f"{path_dir} 접근 불가능") 
                    
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
        
        
        
        

        
        # if num_rows > 0:print("land_code: "+land_code, "building_code: "+building_code, "room_code: "+ room_code, o_res[0]['object_code_obang'].decode('utf8')) 

        # print("object_code_obang: " + object_code_obang)
    print("미등록의뢰수: ",미등록의뢰수)
    print("금일등록매물("+str(len(금일등록매물))+"): ",금일등록매물)
    print("obang_update: ",obang_update)


    #관심매물(별표의뢰)의 오방코드 수집
    query = '''SELECT DISTINCT p.request_code, p.land_code, p.building_code, p.room_code FROM pr_request_give AS p
            LEFT JOIN pr_request_fix AS c ON p.request_code = c.request_code
            WHERE c.fix_del="N"'''
    # query = '''SELECT DISTINCT p.request_code, c.land_code, c.building_code, c.room_code FROM pr_request_fix AS p
    #            LEFT JOIN pr_request_give AS c ON p.request_code = c.request_code
    #            WHERE p.fix_del="N"'''
    cursor.execute(query)
    f_res = cursor.fetchall()
    # print(f_res[0])
    print("관심매물개수:",len(f_res))
    obang_complete = []
    for row in f_res:
        if row['land_code']:land_code = row['land_code'].decode('utf8')
        if row['building_code']:building_code = row['building_code'].decode('utf8')
        if row['room_code']:room_code = row['room_code'].decode('utf8')
        # print("land_code: "+land_code, "building_code: "+building_code, "room_code: "+ room_code)
        o_query = 'SELECT land_code,building_code,room_code,object_code_obang FROM pr_object WHERE object_del="N" AND land_code = %s AND building_code = %s AND room_code = %s'
        params = (land_code, building_code, room_code)
        cursor.execute(o_query, params)
        o_res = cursor.fetchall()
        try:
            if o_res[0]['object_code_obang'].decode('utf8') != '' : obang_update.append(str(o_res[0]['object_code_obang'].decode('utf8'))) 
            # print("request_code: "+str(row['request_code'].decode('utf8')), "land_code: "+land_code, "building_code: "+building_code, "room_code: "+ room_code, str(o_res[0]['object_code_obang'].decode('utf8')))
        except:
            print("pass")
            pass

    import random
    # 리스트의 순서를 랜덤하게 섞습니다.
    random.shuffle(obang_update)

    #완료처리해야할 오방코드 수집
    query = f'''SELECT * FROM pr_request AS p LEFT JOIN pr_request_give AS c ON p.request_code = c.request_code
        WHERE p.request_del="N"
        AND p.request_date BETWEEN "{start_date_str}" AND "{today_str}"
        AND p.request_main != "전체"
        AND p.tr_type = "내놓기"
        AND (p.request_status = "성공" OR p.request_status = "실패")'''
    cursor.execute(query)
    g_res = cursor.fetchall()

    obang_complete = []
    for row in g_res:
        
        if row['land_code']:land_code = row['land_code'].decode('utf8')
        if row['building_code']:building_code = row['building_code'].decode('utf8')
        if row['room_code']:room_code = row['room_code'].decode('utf8')
        # print("land_code: "+land_code, "building_code: "+building_code, "room_code: "+ room_code)
        o_query = 'SELECT land_code,building_code,room_code,object_code_obang FROM pr_object WHERE object_del="N" AND land_code = %s AND building_code = %s AND room_code = %s'
        params = (land_code, building_code, room_code)
        cursor.execute(o_query, params)
        o_res = cursor.fetchall()
        try:
            if o_res[0]['object_code_obang'].decode('utf8') != '' : obang_complete.append(str(o_res[0]['object_code_obang'].decode('utf8'))) 
            # print("request_code: "+str(row['request_code'].decode('utf8')), "land_code: "+land_code, "building_code: "+building_code, "room_code: "+ room_code, str(o_res[0]['object_code_obang'].decode('utf8')))
        except:
            # print("pass")
            pass
    # print("obang_complete: ",obang_complete)
    cursor.close()
    conn.close()
    data = {'금일등록매물':금일등록매물,
            'img_update': img_update,
            '업데이트매물': obang_update,
            '거래완료매물': obang_complete}
    return data
    

import tkinter as tk
from tkinter import messagebox
import datetime
import pyautogui 
# 메시지 박스를 호출하는 함수
def popup_message(complete_count, 신규등록개수, update_ok, end_ok):
    # messagebox.showinfo("알림", f"{complete_count}개의 매물을 업데이트 하였습니다.")
    response = messagebox.askyesno("알림", f"{complete_count}개의 매물을 업데이트 하였습니다.\n(신규등록:{신규등록개수} , 업데이트:{update_ok} , 거래완료:{end_ok}) \n 계속진행하시겠습니까?")

    # tkinter 윈도우 생성
    root = tk.Tk()
    print('팝업생성')

    # 메시지 창 닫기
    root.destroy()
    return response
    # # 윈도우 실행
    # root.mainloop()

def process_wait(hour):
    # 경과될 시간 계산
    now = datetime.datetime.now()
    end_time = now + datetime.timedelta(hours=hour)

    # GUI 설정
    root = tk.Tk()
    root.title("실시간 남은 시간")
    root.geometry("500x150")

    # 남은 시간 표시 라벨
    remaining_time_label = tk.Label(root, text="", font=("Helvetica", 20))
    remaining_time_label.pack(pady=20)

    # 멈춤 버튼
    stop_button = tk.Button(root, text="멈춤", font=("Helvetica", 14), command=root.destroy)
    stop_button.pack(pady=10)

    # 실시간으로 남은 시간 업데이트
    def update_remaining_time():
        remaining_time = end_time - datetime.datetime.now()
        remaining_time_str = str(remaining_time).split('.')[0]  # 소수점 이하 제거
        remaining_time_label.configure(text=f"업데이트 개시까지 {remaining_time_str} 남았습니다.")
        if remaining_time.total_seconds() > 0:
            root.after(1000, update_remaining_time)  # 1초마다 업데이트
        else:
            # messagebox.showinfo("시간 종료", f"{hour}시간이 경과되었습니다.")
            root.destroy()
            update_start()

    # 실시간으로 남은 시간 업데이트 시작
    update_remaining_time()

    # Tkinter 루프 시작
    root.mainloop()


# pyautogui.alert("오방매물 최신등록일을 업데이트 합니다.")

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.chrome.options import Options


#obang_data에서 가져온 obang_update에 포함된 obang_code를 업데이트 할 예정임

complete_count = 0
update_ok = 0
end_ok = 0
#작업순서 : 최신등록일업데이트 - 거래완료 및 비공개처리
def update_start():
    
    import datetime
    global complete_count
    global update_ok
    global end_ok
    print(str(complete_count+1) + "번째 업데이트 시작: " + str(datetime.datetime.now()))

    # 사용자로부터 입력 받는 함수
    def get_user_input():
        import sys  # sys 모듈 임포트
        def on_ok():
            nonlocal user_input
            user_input = entry.get()
            if not user_input.isdigit() or not (1 <= int(user_input) <= 9):
                user_input = str(default)  # 유효하지 않은 입력에 대해 기본값 사용
            root.destroy()

        def on_cancel():
            sys.exit()  # 프로그램 종료
            # root.destroy()

        def on_close():
            # 엑스 박스를 눌렀을 때 실행할 코드
            print("프로그램이 사용자에 의해 종료되었습니다.")
            root.destroy()
            sys.exit()  # 프로그램 종료

        def update_timer():
            nonlocal counter
            counter -= 1
            timer_label.config(text=f"남은 시간: {counter}초")
            if counter > 0:
                root.after(1000, update_timer)
            else:
                on_ok()  # 시간 초과 시 on_ok() 호출

        default = 1
        counter = 10
        user_input = str(default)

        root = tk.Tk()
        root.title("입력")

        # 화면 중앙에 창 위치 설정
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        window_width = 300
        window_height = 150
        x = int((screen_width / 2) - (window_width / 2))
        y = int((screen_height / 2) - (window_height / 2))
        root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        root.protocol("WM_DELETE_WINDOW", on_close) #엑스박스 클릭을 사용하여 창닫기
        
        tk.Label(root, text="\n업데이트할 데이터 입력 (1-9):\n\n※미입력시 기본값 1적용").pack()

        entry = tk.Entry(root)
        entry.pack()
        # entry.insert(0, str(default))  # 기본값 삽입
        entry.focus_set()

        timer_label = tk.Label(root, text=f"남은 시간: {counter}초")
        timer_label.pack()

        # 버튼을 배치할 프레임 생성
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)

        # 프레임 안에 버튼 배치
        tk.Button(button_frame, text="확인", command=on_ok).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="취소", command=on_cancel).pack(side=tk.RIGHT, padx=10)

        root.after(1000, update_timer)  # 1초 후에 타이머 업데이트 시작
        root.mainloop()

        return int(user_input)

    
    #최신등록일 업데이트
    before_day = get_user_input()
    obangData = obang_data(before_day)
    # imgUpdate = obangData['업데이트매물']
    
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled") #봇으로 인식안하게 하는 옵션

    # admin_id = 'test@osanbang.com'
    # admin_pw = '1234'
    admin_id = "nasangkwon@outlook.kr"
    admin_pw = 'tkdrnjs2@'

    # driver = webdriver.Chrome('/chromedriver', options=options)
    driver = webdriver.Chrome(options=options)

    driver.implicitly_wait(10)
    # URL 열기
    driver.maximize_window()
    driver.get('https://osanbang.com/adminlogin/index')

    # WebDriverWait(driver, 30).until(EC.presence_of_element_located(
    #     By.CSS_SELECTOR, "body > div.logo > a > img"
    # ))

    driver.find_element(By.XPATH, '//*[@id="login_form"]/div[1]/div/input').send_keys(admin_id)
    driver.find_element(By.XPATH, '//*[@id="login_form"]/div[2]/div/input').send_keys(admin_pw)
    driver.find_element(By.XPATH, '//*[@id="login_form"]/div[3]/button').click()

    driver.implicitly_wait(10)
    driver.find_element(By.CSS_SELECTOR, 'body > div.page-container > div.page-sidebar-wrapper > div > ul > li:nth-child(3) > a > span.title').click() #사이드바 매물 클릭
    driver.find_element(By.CSS_SELECTOR, '#menu-product-1 > a').click() #매물->매물관리 클릭
    # driver.get('https://osanbang.com/adminproduct/index')    
    
    금일등록매물 = obangData['금일등록매물']
    obang_update = obangData['업데이트매물']
    for update_code in obang_update:
        try:
            # WebDriverWait(driver, 10).until(EC.element_to_be_clickable(By.CSS_SELECTOR, "#search_id")).clear() #매물번호 입력창의 입력값 초기화
            driver.implicitly_wait(10)
            driver.find_element(By.CSS_SELECTOR, "#search_id").clear() 
            print(f"{update_code} 1.검색창 초기화")
            driver.find_element(By.CSS_SELECTOR, "#search_id").send_keys(update_code) #매물번호입력창에 매물번호 입력
            print("----- 2.매물번호입력창에 매물번호 입력")
            driver.find_element(By.CSS_SELECTOR, "#admin_member_id > option:nth-child(1)").click() #담당자를 직원별로 선택
            print("----- 3.담당자를 직원별로 선택")
            driver.find_element(By.CSS_SELECTOR, "#go_keyword").click() #검색버튼(돋보기) 클릭
            print("----- 4.검색버튼(돋보기) 클릭")
            # WebDriverWait(driver, 10).until(EC.presence_of_element_located(By.CSS_SELECTOR, "#tr_20052 > td:nth-child(14) > div:nth-child(1)"))
            # time.sleep(2)
            
            # 업데이트 전 등록일
            before_target = driver.find_element(By.CSS_SELECTOR, f"#tr_{update_code} > td:nth-child(15) > div").get_attribute('title').split(' ')[0]
            before_date = datetime.datetime.strptime(before_target , '%Y-%m-%d')
            today = datetime.datetime.today()
            print(f"{update_code} before_date: ", before_date)
            # print(f"{update_code} today: ", today)
            # if before_date == today:            

            # 오늘 날짜와 비교하여 출력
            if before_target == str(datetime.date.today()):
                print("----- 5.Today! pass")
            elif before_date > today:
                print("----- 5.Future Date! pass")
            else:
                #업데이트 실행
                print("----- 5.past Date! update")
                driver.find_element(By.CSS_SELECTOR, f'#tr_{update_code} > td:nth-child(14) > div:nth-child(1)').click() #관리 클릭
                print("----- 5-1.관리 클릭")
                # time.sleep(1)
                # WebDriverWait(driver, 10).until(EC.presence_of_element_located(By.CSS_SELECTOR, f"#tr_{update_code} > td:nth-child(14) > div:nth-child(1) > a")).click() #관리 클릭
                # WebDriverWait(driver, 10).until(EC.presence_of_element_located(By.CSS_SELECTOR, f"#tr_{update_code} > td:nth-child(14) > div.dropdown.open > ul > li:nth-child(7) > a")).click() #최신등록일로갱신 클릭
                driver.find_element(By.CSS_SELECTOR, f'#tr_{update_code} > td:nth-child(14) > div.dropdown.open > ul > li:nth-child(7)').click() #최신등록일로갱신 클릭
                print("----- 5-2.최신등록일로갱신 클릭")
                
                #거래완료 해제
                status_span = driver.find_elements(By.XPATH, f'//*[@id="tr_{update_code}"]/td[10]/span')
                # print(status_span.text)
                span_texts = []
                for span in status_span: span_texts.append(span.text)
                if "완료" in span_texts:
                    print("----- 6.완료라벨 표시중 -> 완료라벨 제거")

                    driver.execute_script(f"change('is_finished','{update_code}','0');")
                    try:
                        alert = WebDriverWait(driver, 0.2).until(EC.alert_is_present())
                        alert.accept()
                    except Exception as e:
                        print("alert오류", str(e))
                        pass  # alert 창이 없는 경우, 그냥 넘어갑니다.  
        
                else:
                    print("----- 6.완료라벨 없음")
                    pass
                update_ok += 1  
                complete_count += 1                

        except:
            # print(update_code,"업데이트 안됨")
            print(f"{update_code}업데이트 안됨")

    #거래완료 및 비공개처리
    print("거래완료 및 비공개처리 시작")
    obang_complete = obangData['거래완료매물']
    print("obang_complete:", obang_complete)
    for complete_code in obang_complete:
        try:
            # WebDriverWait(driver, 10).until(EC.element_to_be_clickable(By.CSS_SELECTOR, "#search_id")).clear() #매물번호 입력창의 입력값 초기화
            driver.implicitly_wait(10)
            driver.find_element(By.CSS_SELECTOR, "#search_id").clear() 
            print(f"{update_code} 1.검색창 초기화")
            driver.find_element(By.CSS_SELECTOR, "#search_id").send_keys(complete_code) #매물번호입력창에 매물번호 입력
            print("----- 2.매물번호입력창에 매물번호 입력")
            driver.find_element(By.CSS_SELECTOR, "#admin_member_id > option:nth-child(1)").click() #담당자를 직원별로 선택
            print("----- 3.담당자를 직원별로 선택")
            driver.find_element(By.CSS_SELECTOR, "#go_keyword").click() #검색버튼(돋보기) 클릭
            print("----- 4.검색버튼(돋보기) 클릭")

            #비공개처리
            element = driver.find_element(By.XPATH, f'//*[@id="tr_{complete_code}"]/td[3]/div/label')
            driver.execute_script("arguments[0].setAttribute('class', 'btn btn-gray lock')", element)
            print("----- 5.비공개처리")
            
            #완료처리
            status_span = driver.find_elements(By.XPATH, f'//*[@id="tr_{complete_code}"]/td[10]/span')
            print("status_span 개수: ",str(len(status_span)))
            span_texts = []
            for span in status_span: span_texts.append(span.text)
            if "완료" not in span_texts:
                driver.execute_script(f"change('is_finished','{complete_code}','1');")
                print("----- 6.완료라벨 미표시상태 -> 완료라벨 표시")
                
                try:
                    alert = WebDriverWait(driver, 0.2).until(EC.alert_is_present())
                    alert.accept()
                except Exception as e:
                    print("alert오류", str(e))
                    pass  # alert 창이 없는 경우, 그냥 넘어갑니다.                
            else:
                print("----- 6.완료라벨 표시상태")
                pass
            end_ok += 1
            complete_count += 1

        except Exception as e:
            print("오류:" , str(e))
            print(f"{complete_code}거래완료 안됨")

    if popup_message(complete_count, len(금일등록매물), update_ok, end_ok):
        print(" 계속진행합니다.")
        process_wait(10) # 몇 시간뒤에 재작동할지 설정
        # update_start()
    else:
        print("멈춥니다")
        # 드라이버 종료
        driver.quit()

update_start()
