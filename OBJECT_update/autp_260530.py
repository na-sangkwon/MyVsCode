#기존 두개의 파일을 한개의 파일로 합침

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

def obang_data(before_day):
    import pymysql
    import datetime

    # today = datetime.datetime.now().strftime("%Y-%m-%d")
    # print(today)

    import tkinter as tk
    from tkinter import simpledialog, messagebox
    import threading
    import time

    import os





    # 현재 날짜 가져오기 (datetime 객체로)
    today = datetime.datetime.now().date()
    금일등록매물 = []
    신규등록매물 = []
    미등록의뢰수 = 0
    img_update = [] #프로중개인 이미지 업데이트용
    obang_update = []              # 전체 (기존 유지)
    obang_update_fav = []          # 관심의뢰
    obang_update_normal = []       # 일반의뢰

    obang_map = {}          # 키: object_code_obang → 값: pr_object 한 행(dict)
    obang_update_seen = set()  # (선택) 중복 방지용

    # before_day 값 설정
    # before_day = get_user_input()
    # before_day = 1

    # 시작 날짜 계산
    start_date = today - datetime.timedelta(days=before_day)

    # 날짜를 문자열 형태로 변환
    today_str = today.strftime("%Y-%m-%d")
    start_date_str = start_date.strftime("%Y-%m-%d")
    today_date = today
    start_date_date = start_date    

    conn = pymysql.connect(host='obangkr.cafe24.com', user='obangkr', password='Ddhqkd!1', charset='utf8')

    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('USE obangkr;')


    #내놓기관심의뢰(별표의뢰)의 오방코드 수집
    query = '''SELECT DISTINCT p.request_code, p.land_code, p.building_code, p.room_code FROM pr_request_give AS p
            LEFT JOIN pr_request_fix AS c ON p.request_code = c.request_code
            WHERE c.fix_del="N"'''
    cursor.execute(query)
    f_res = cursor.fetchall()
    f_codes_arr = []
    # print(f_res[0])
    print("내놓기관심의뢰개수:",len(f_res))
    # obang_complete = []
    for row in f_res:
        if row['request_code']:request_code = row['request_code']
        if row['land_code']:land_code = row['land_code']
        if row['building_code']:building_code = row['building_code']
        if row['room_code']:room_code = row['room_code']
        # print("land_code: "+land_code, "building_code: "+building_code, "room_code: "+ room_code)
        o_query = '''  
            SELECT land_code,building_code,room_code,object_code_obang FROM pr_object WHERE object_status="중개요청" AND object_del="N" AND land_code = %s AND building_code = %s AND room_code = %s
        '''
        params = (land_code, building_code, room_code)
        cursor.execute(o_query, params)
        o_res = cursor.fetchall()
        # print(o_res)
        # pyautogui.alert(o_res, "o_res")
        try:
            if o_res and o_res[0]['object_code_obang'] != '' : obang_update.append(str(o_res[0]['object_code_obang'])) 
            f_codes_arr.append(request_code)
            # print("request_code: "+str(row['request_code']), "land_code: "+land_code, "building_code: "+building_code, "room_code: "+ room_code, str(o_res[0]['object_code_obang']))
        except:
            # print("pass")
            pass

    f_codes = "','".join(f_codes_arr) if len(f_codes_arr) > 0 else ''
    f_codes = f"'{f_codes}'"
    print(f"f_codes:{f_codes}")



    #최신등록일을 갱신할 오방코드 수집(의뢰확인일 기준 request_date)
    query = f'''SELECT 
        p.request_code,
        p.tr_target,
        p.object_type1,
        p.object_type2,
        p.admin_name,
        p.request_date,
        p.request_udate,
        p.request_wdate,
        
        c.land_code,
        c.building_code,
        c.room_code,
        c.request_trading,
        c.request_deposit1,
        c.request_deposit2,
        c.request_deposit3,
        c.request_rent1,
        c.request_rent2,
        c.request_rent3,
        c.request_manager,
        c.request_mmoney,
        c.request_mlist,
        c.tr_memo,
        c.request_area1,
        c.request_area2,
        c.request_areatype1,
        c.request_areatype2,
        c.first_trade 
        
        FROM pr_request AS p LEFT JOIN pr_request_give AS c ON p.request_code = c.request_code
        WHERE p.request_del="N"
        AND (p.request_date BETWEEN "{start_date_str}" AND "{today_str}" OR p.request_code IN ({f_codes}))
        -- AND p.request_code = "230329_0300"
        AND p.request_main != "전체"
        AND p.tr_type = "내놓기"
        AND (p.request_status = "접수" OR p.request_status = "진행")
        AND (c.request_deposit1 != "" OR c.request_rent1 != "")'''
    cursor.execute(query)
    recently_res = cursor.fetchall()
    num_rows = cursor.rowcount
    
    
    print("최신등록일을 갱신할 의뢰개수: ",num_rows)
    # print(query)
    # pyautogui.alert(query)
    # print(recently_res[1]['land_code'],recently_res[1]['building_code'],recently_res[1]['room_code'])


    for row in recently_res:
        # pyautogui.alert(f"row:{row}")
        building_code = ''
        room_code = ''        
        tr_target = row['tr_target']
        # print("tr_target:"+tr_target, "")

        # 필수키 점검
        if row['land_code']:
            land_code = row['land_code'] 
        else: 
            print('land_code is not ==> request_code:'+row['request_code'])
            continue
        if row['building_code']:building_code = row['building_code']
        if row['room_code']:room_code = row['room_code']
        # print("조회할 물건정보: "+"request_code: "+str(row['request_code'])+"land_code: "+land_code+"building_code: "+building_code+"room_code: "+ room_code)
        
        o_query = '''
            SELECT
            -- pr_object (기본)
            o.object_code_new,
            o.land_code, o.building_code, o.room_code,
            o.object_code_obang,
            o.object_type, 
            o.object_ttype, 
            o.object_rtype,
            o.object_del,

            -- pr_land (토지)
            l.land_do,
            l.land_si,
            l.land_dong,
            l.land_li,
            l.land_main,
            l.land_jibun,
            l.land_jibung,
            l.land_address,
            l.land_totarea,
            l.land_important,
            l.land_option,
            l.land_memo,
            l.representing_jibun,
            l.representing_jimok,
            l.representing_purpose,

            -- pr_building (건물)
            b.building_del,
            b.building_gate1,
            b.building_gate2,
            b.building_parking,
            b.building_pn,
            b.building_direction,
            b.building_bolt,
            b.building_height,
            b.building_element,
            b.building_memo,
            b.building_important,
            b.building_option,
            b.building_purpose,
            b.building_grndflr,
            b.building_ugrndflr,
            b.building_archarea,
            b.building_totarea,
            b.building_usedate,
            b.building_stract,
            b.building_elvcount,

            -- pr_room (호실)
            r.room_num,
            r.room_floor,
            r.room_status,
            r.room_nmemo,
            r.room_gate1,
            r.room_gate2,
            r.room_memo,
            r.room_rcount,
            r.room_bcount,
            r.r_direction,
            r.room_direction,
            r.room_area1,
            r.room_areatype1,
            r.room_area2,
            r.room_areatype2,
            r.room_important,
            r.room_option,
            r.room_purpose

            FROM pr_object AS o
            LEFT JOIN pr_land     AS l ON l.land_code     = o.land_code
            LEFT JOIN pr_building AS b ON b.building_code = o.building_code
            LEFT JOIN pr_room     AS r ON r.room_code     = o.room_code

            WHERE
            o.object_del = 'N'
            AND o.land_code     = %s
            AND o.building_code = %s
            AND o.room_code     = %s
            -- (선택) 연관 테이블도 삭제/비활성 필터를 적용하고 싶다면 아래처럼 추가
            AND l.land_del = 'N'
            AND b.building_del = 'N'
            AND r.room_del = 'N'
            LIMIT 1;        
        '''
        # o_query = 'SELECT object_code_new,land_code,building_code,room_code,object_code_obang,object_ttype,object_rtype FROM pr_object WHERE object_del="N" AND land_code = %s AND building_code = %s AND room_code = %s'
        params = (land_code, building_code, room_code)
        cursor.execute(o_query, params)
        o_row = cursor.fetchone()  # 단일행만 필요하므로 fetchone 권장
        # o_res = cursor.fetchall()
        # pyautogui.alert(f"o_row:{o_row}")
        if not o_row:
            # pyautogui.alert(f"[경고] 조회 결과 없음: land_code={land_code}, building_code={building_code}, room_code={room_code}")
            continue

        # print("o_row:", o_row)

        # 오방번호 정규화(문자열/공백 제거)
        obang_code = str(o_row.get('object_code_obang') or '').strip()
        if not obang_code:
            # 오방번호가 없으면 스킵(또는 로깅)
            continue

        # 🔥 신규등록 (기간 기준)
        if start_date_date <= row['request_wdate'] <= today_date:

            if obang_code:
                신규등록매물.append(obang_code)   # 오방 등록된 매물
            else:
                미등록의뢰수 += 1   # 🔥 핵심 (미등록 의뢰)

        # 🔥 금일등록 (오늘 기준)
        if row['request_wdate'] == today_date:

            if obang_code:
                금일등록매물.append(obang_code)

        # 업데이트 대상 목록(중복 방지)
        if obang_code not in obang_update_seen:
            obang_update.append(obang_code)

            # 🔥 관심의뢰 / 일반의뢰 분리
            if row['request_code'] in f_codes_arr:
                obang_update_fav.append(obang_code)
            else:
                obang_update_normal.append(obang_code)

            obang_update_seen.add(obang_code)

        def build_entry(o_row: dict, req_row: dict) -> dict:
            """
            pr_object(o_row)와 의뢰정보(req_row)를 합쳐 엔트리 생성.
            - 키 충돌 시 pr_object(o_row) 우선
            - 원본도 보존: _obj / _req
            """
            # o_row가 우선이 되도록 o_row를 뒤에 두어 병합
            merged = {**req_row, **o_row}
            # merged['_obj'] = o_row
            # merged['_req'] = req_row
            return merged

        # 번호 → (o_row + row 병합) 캐시에 저장
        entry = build_entry(o_row, row)

        # 새로 들어오면 추가, 기존 있으면 갱신
        obang_map[obang_code] = entry
        
        #폴더경로 만들기
        # img_update.append(object_code_new) 
        if tr_target == '층호수' and room_code == '':
            print("호실정보없는 층호수의뢰: "+str(row['request_code']))
            pass
        else:
            object_code_new = o_row['object_code_new']
            query = 'SELECT * FROM pr_land WHERE land_code = "%s"' % land_code
            cursor.execute(query)
            l_res = cursor.fetchall()
            for row in l_res:
                land_do = row['land_do'] #시도
                land_si = row['land_si'] #시군구
                land_dong = row['land_dong'] #읍면동
                land_li = row['land_li'] #리
                land_type = '산' if row['land_type'] == '2' else '일반' #대장구분 일반:1 산:2
                land_jibun = row['land_jibun'] #지번(숫자)  
                land_jibung = row['land_jibung'] #지번(숫자)  
                
            if tr_target == '건물' or tr_target == '층호수':
                query = 'SELECT * FROM pr_building WHERE building_code = "%s"' % building_code
                cursor.execute(query)
                b_res = cursor.fetchall()   
                building_name = '' if b_res[0]['building_name'] == '' else b_res[0]['building_name'] #건물명
            
            if tr_target == '층호수':
                query = 'SELECT * FROM pr_room WHERE room_code = "%s"' % room_code
                cursor.execute(query)
                r_res = cursor.fetchall()
                room_num = r_res[0]['room_num'] #호실명
                room_floor = '' if r_res[0]['room_floor'] == '' else r_res[0]['room_floor'] #호실층수
            
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

                # if os.path.exists(path_dir):
                #     print(f"{path_dir} 접근 가능")
                # else:
                #     print(f"{path_dir} 접근 불가능") 
                    
                file_list = os.listdir(path_dir)   
                # print("file_list:", file_list)

                for file in file_list:
                    # 파일 확장자를 소문자로 변환하여 비교
                    if file.lower().endswith(('.jpeg', '.gif', '.png', '.jpg')):
                        원본사진들.append(file)         
                # print("원본사진들:", 원본사진들)
                if len(원본사진들) == 0: #물건의 원본사진없음
                    # print("원본사진폴더에 이미지 없음")
                    pass
                else: #원본사진폴더에 이미지 존재=>DB에 샘플이미지를 등록
                    # print("원본사진폴더에 이미지 존재")  
                    if tr_target == '토지':
                        object_info_code = land_code
                    elif tr_target == '건물':
                        object_info_code = building_code
                    elif tr_target == '층호수':
                        object_info_code = room_code
 
                    
                    #원본사진폴더에 원본이미지는 존재하지만 DB에는 없는 걸로 되어있는 경우
                    query = f'SELECT object_ori_img FROM pr_object WHERE object_code_new="{object_code_new}" AND object_ori_img="N"'
                    cursor.execute(query)
                    result = cursor.fetchone() 
                    
                    #pr_object의 object_ori_img값 수정
                    if result:
                        object_ori_img = result['object_ori_img'].decode('utf-8')
                        # print("object_ori_img:", object_ori_img)
                        if object_ori_img == 'N':
                            # print(f"매물({object_code_new})의 object_ori_img 값은 'N'입니다.") 
                            update_query = f'UPDATE pr_object SET object_ori_img="Y" WHERE object_code_new="{object_code_new}"'
                            cursor.execute(update_query)           
                    #변환된 사진폴더의 생성일모음 생성                                
                    for filename in file_list:
                        if "output" in filename: 변환폴더생성일모음.append(filename.split('output')[1])
                    #pr_object_img의 output_folder필드에 들어갈 값 지정
                    output_folder = max(변환폴더생성일모음)
                    # print("output_folder:", output_folder)
            except Exception as e: 
                # print("폴더 오류", str(e))
                errarr.append("폴더 오류")
                pass            
        
        
        
        

        
        # if num_rows > 0:print("land_code: "+land_code, "building_code: "+building_code, "room_code: "+ room_code, o_res[0]['object_code_obang']) 

        # print("object_code_obang: " + object_code_obang)
    print("미등록의뢰수: ",미등록의뢰수)
    print("금일등록매물("+str(len(금일등록매물))+"): ",금일등록매물)
    # pyautogui.alert("금일등록매물("+str(len(금일등록매물))+")")
    print("obang_update: ",obang_update)
    print("obang_update 개수: ",len(obang_update))
    print("obang_update_seen 개수: ",len(obang_update_seen))
    # pyautogui.alert(obang_update, "obang_update")



    import random
    # 리스트의 순서를 랜덤하게 섞습니다.
    random.shuffle(obang_update)

    
    # 완료처리해야할 오방코드 수집 (단일 쿼리 버전)
    query = """
    SELECT o.object_code_obang
    FROM pr_request AS p
    JOIN pr_request_give AS c
    ON p.request_code = c.request_code
    JOIN pr_object AS o
    ON o.object_del = 'N'
    AND o.land_code = c.land_code
    AND o.building_code = c.building_code
    AND o.room_code = c.room_code
    WHERE p.request_del = 'N'
    AND p.request_main <> '전체'
    AND p.tr_type = '내놓기'
    AND p.request_status IN ('성공','실패')
    -- AND p.request_udate BETWEEN %s AND %s           -- 날짜 필터 필요 시 주석 해제
    AND o.object_code_obang <> ''
    """

    cursor.execute(query)
    rows = cursor.fetchall()

    # 기존과 동일하게 문자열 리스트로 변환
    obang_complete = [str(r['object_code_obang']) for r in rows]
    # print("obang_complete: ",obang_complete)
    cursor.close()
    conn.close()
    data = {
        '금일등록매물': 금일등록매물,
        '신규등록매물': 신규등록매물,
        '미등록의뢰수': 미등록의뢰수,
        'img_update': img_update,
        '업데이트매물': obang_update,                 # 기존 유지
        '업데이트매물_관심': obang_update_fav,         # 🔥 추가
        '업데이트매물_일반': obang_update_normal,      # 🔥 추가
        '거래완료매물': obang_complete,
        '오방매물정보': obang_map
    }   
    return data


def show_update_preview(data, before_day):
    import tkinter as tk
    from tkinter import messagebox
    import datetime

    today = datetime.datetime.now().date()
    start_date = today - datetime.timedelta(days=before_day)

    # 데이터
    new_total_count = len(data.get('신규등록매물', []))
    today_count = len(data.get('금일등록매물', []))
    미등록_count = data.get('미등록의뢰수', 0)
    fav_count = len(data.get('업데이트매물_관심', []))
    normal_count = len(data.get('업데이트매물_일반', []))
    complete_count = len(data.get('거래완료매물', []))

    total_update = fav_count + normal_count

    msg = f"""
    [업데이트 사전 안내]

    조회 기준: 최근 {before_day}일
    ({start_date} ~ {today})

    ━━━━━━━━━━━━━━━━━━━

    [신규등록매물(기간기준)] : {new_total_count}개
    [금일등록매물] : {today_count}개
    [미등록의뢰] : {미등록_count}개   🔥

    [수정일 업데이트매물]
    - 관심의뢰 : {fav_count}개
    - 일반의뢰 : {normal_count}개
    → 합계 : {total_update}개

    [거래완료매물] : {complete_count}개

    ━━━━━━━━━━━━━━━━━━━

    계속 진행하시겠습니까?
    """

    root = tk.Tk()
    root.withdraw()

    result = messagebox.askyesno("업데이트 미리보기", msg)

    root.destroy()
    return result
    

import tkinter as tk
from tkinter import messagebox
import datetime
import pyautogui 
# 메시지 박스를 호출하는 함수
def popup_message(complete_count, 신규등록개수, restart_ok, update_ok, end_ok):
    # messagebox.showinfo("알림", f"{complete_count}개의 매물을 업데이트 하였습니다.") 내놓기관심의뢰,
    print(f"(신규등록:{신규등록개수} , 업데이트:{update_ok} , 재등록:{restart_ok} , 비공개:{end_ok})")
    response = messagebox.askyesno("알림", f"{complete_count}개의 매물을 업데이트 하였습니다.\n(신규등록:{신규등록개수} , 업데이트:{update_ok} , 재등록:{restart_ok} , 비공개:{end_ok}) \n 계속진행하시겠습니까?")

    # tkinter 윈도우 생성
    root = tk.Tk()
    root.withdraw()  # 창 숨기기
    root.attributes("-topmost", True)  # 항상 위에 있도록 설정
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
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.chrome.options import Options



def 현재페이지_매물번호수집(driver, timeout: int = 5):
    # tbody 내 목록 로드 대기
    WebDriverWait(driver, timeout).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#search-items tr.admin_column"))
    )
    ids = []
    for row in driver.find_elements(By.CSS_SELECTOR, "#search-items tr.admin_column"):
        try:
            pid = row.find_element(By.CSS_SELECTOR, "td:nth-of-type(2) strong").text.strip()
            if pid:
                ids.append(pid)
        except Exception:
            continue
    
    return ids

def 비공개여부(토글):
    """토글의 data-state가 '1'이면 비공개로 간주"""
    return (토글.get_attribute("data-state") or "").strip() == "1"

def 비공개로_전환(driver, 매물번호, timeout=6):
    """
    한 매물번호의 3번째 TD 토글을 눌러 비공개로 바꾼다.
    이미 비공개면 건너뛴다.
    """
    # 행과 토글 찾기
    행 = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, f"#tr_{매물번호}"))
    )
    토글 = WebDriverWait(행, timeout).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "td:nth-of-type(3) .btn-group[onclick^='activated_change']"))
    )

    # 이미 비공개면 스킵
    if 비공개여부(토글):
        return "skip"

    # 클릭 후 비공개가 될 때까지 대기 (DOM 갱신 가능성 있어 재탐색)
    토글.click()
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: 비공개여부(d.find_element(By.CSS_SELECTOR, f"#tr_{매물번호} td:nth-of-type(3) .btn-group[onclick^='activated_change']"))
        )
        return "ok"
    except Exception:
        return "fail"

def 선택목록_비공개처리(driver, 비공개할매물번호들_arr, timeout=6):
    """
    목록의 매물번호들에 대해 비공개로 전환하고 결과를 출력/반환.
    """
    성공, 스킵, 실패 = [], [], []
    for pid in 비공개할매물번호들_arr:
        try:
            결과 = 비공개로_전환(driver, pid, timeout=timeout)
            if 결과 == "ok":
                성공.append(pid)
            elif 결과 == "skip":
                스킵.append(pid)
            else:
                실패.append(pid)
        except Exception:
            실패.append(pid)

    print(f"[비공개 처리] 성공:{len(성공)} / 이미 비공개:{len(스킵)} / 실패:{len(실패)}")
    if 성공: print("성공:", ", ".join(성공))
    if 스킵: print("이미 비공개:", ", ".join(스킵))
    if 실패: print("실패:", ", ".join(실패))
    return {"성공": 성공, "이미비공개": 스킵, "실패": 실패}

def 현재페이지_비공개처리(driver, DB완료_set, timeout=6):
    """현재 페이지의 매물번호를 수집해 DB완료와 교집합만 비공개 처리"""
    현재페이지_매물번호들_arr = 현재페이지_매물번호수집(driver)
    비공개할매물번호들_arr = [pid for pid in 현재페이지_매물번호들_arr if pid in DB완료_set]
    if not 비공개할매물번호들_arr:
        print("[현재페이지] 비공개 대상 없음")
        return {"성공": [], "이미비공개": [], "실패": []}
    return 선택목록_비공개처리(driver, 비공개할매물번호들_arr, timeout=timeout)

def 다음페이지_있나(driver):
    """#paging 안에서 '다음' 텍스트를 가진 링크가 있는지 반환 (요소 자체 또는 None)"""
    els = driver.find_elements(By.XPATH, "//ul[@id='paging']//a[contains(., '다음')]")
    return els[0] if els else None

def 다음페이지로_이동(driver, timeout=10):
    """'다음'을 클릭하고 목록이 갱신될 때까지 대기. 성공 시 True, 없으면 False"""
    링크 = 다음페이지_있나(driver)
    if not 링크:
        return False

    # 현재 목록의 첫 행을 기준으로 '바뀔 때까지' 대기
    기존_첫행 = None
    기존행들 = driver.find_elements(By.CSS_SELECTOR, "#search-items tr.admin_column")
    if 기존행들:
        기존_첫행 = 기존행들[0]

    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", 링크)
    링크.click()

    # 페이지 갱신 대기: 1) 기존 첫행이 사라짐(staleness) 또는 2) 새 목록 로드
    wait = WebDriverWait(driver, timeout)
    if 기존_첫행:
        try:
            wait.until(EC.staleness_of(기존_첫행))
        except Exception:
            pass
    # 새 행 로드 보장
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#search-items tr.admin_column")))
    return True

def 모든페이지_비공개처리(driver, obangData, 최대페이지=None, timeout=8):
    """
    첫 페이지부터 '다음'이 없을 때까지 반복 처리.
    - obangData['거래완료매물']과 현재 페이지를 교집합 후 비공개 처리
    - 최대페이지: 안전장치(정수). None이면 제한 없음.
    """
    DB완료_set = set(str(x).strip() for x in (obangData.get('거래완료매물') or []) if str(x).strip())
    총성공, 총스킵, 총실패 = [], [], []
    페이지 = 1

    while True:
        print(f"\n=== [{페이지}페이지] 비공개 처리 시작 ===")
        결과 = 현재페이지_비공개처리(driver, DB완료_set, timeout=timeout)
        총성공 += 결과.get("성공", [])
        총스킵 += 결과.get("이미비공개", [])
        총실패 += 결과.get("실패", [])

        if 최대페이지 and 페이지 >= 최대페이지:
            print(f"[알림] 최대페이지({최대페이지})에 도달하여 중단합니다.")
            break

        이동됨 = 다음페이지로_이동(driver, timeout=timeout)
        if not 이동됨:
            print("[알림] '다음' 링크가 없어 탐색을 종료합니다.")
            break

        페이지 += 1

    print("\n=== 전체 결과 ===")
    print(f"성공:{len(총성공)} / 이미비공개:{len(총스킵)} / 실패:{len(총실패)}")
    if 총성공: print("성공:", ", ".join(총성공))
    if 총스킵: print("이미 비공개:", ", ".join(총스킵))
    if 총실패: print("실패:", ", ".join(총실패))
    return {"성공": 총성공, "이미비공개": 총스킵, "실패": 총실패}

def 공개로_전환(driver, 매물번호, timeout=6):
    """
    한 매물번호의 3번째 TD 토글을 눌러 공개로 바꾼다.
    이미 공개면 건너뛴다.
    """
    # 행과 토글 찾기
    행 = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, f"#tr_{매물번호}"))
    )
    토글 = WebDriverWait(행, timeout).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "td:nth-of-type(3) .btn-group[onclick^='activated_change']"))
    )

    # 이미 비공개면 스킵
    if not 비공개여부(토글):
        return "skip"

    # 클릭 후 비공개가 될 때까지 대기 (DOM 갱신 가능성 있어 재탐색)
    토글.click()
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: 비공개여부(d.find_element(By.CSS_SELECTOR, f"#tr_{매물번호} td:nth-of-type(3) .btn-group[onclick^='activated_change']"))
        )
        return "ok"
    except Exception:
        return "fail"

def 메모에마크추가(메모, 마크='-- '):
    if not 메모:  # 메모가 None 또는 빈 문자열인 경우 예외 처리
        return ""            
    # 줄 단위로 나누고, 각 줄에 '-- ' 추가
    return "<br>".join([f"{마크}{line}" for line in 메모.split("<br>") if line.strip()])       

def 단일오방매물업데이트(driver, 업데이트정보):
    print(f"단일오방매물업데이트(업데이트정보)")
    
    if not 업데이트정보:
        print("업데이트정보 없음")
        return
    
    main_option = ''
    main_important = ''
    I_memo = ''
    current_date = datetime.date.today()
    formatted_date = current_date.strftime("%Y-%m-%d")

    print("업데이트정보:",업데이트정보)

    admin_name = 업데이트정보['admin_name']
    object_code_new = 업데이트정보['object_code_new']
    request_code = 업데이트정보['request_code']
    object_type1  = 업데이트정보.get('object_type1', '')
    object_type2  = 업데이트정보.get('object_type2', '')
    land_code  = 업데이트정보.get('land_code', '')
    building_code   = 업데이트정보.get('building_code', '')
    room_code   = 업데이트정보.get('room_code', '')
    tr_target = 업데이트정보.get('tr_target', '')
    # pyautogui.alert(f"tr_target:{tr_target}")     
    object_type = 업데이트정보.get('object_type', '')
    object_ttype = 업데이트정보.get('object_ttype', '')
    object_rtype = 업데이트정보.get('object_rtype', '')
    obinfo_trading = '' if 업데이트정보['request_trading'] =='' else 업데이트정보['request_trading']
    obinfo_deposit1 = '' if 업데이트정보['request_deposit1'] =='' else 업데이트정보['request_deposit1'] #보증금1
    if obinfo_deposit1 == '' :
        pyautogui.alert("임대료는 필수입니다. 확인후 다시 시작하세요~")
    # if obinfo_trading == '' and obinfo_deposit1 == '' :
    #     pyautogui.alert("거래금액은 필수입니다. 확인후 다시 시작하세요~")
        driver.quit()
        return
        # driver.close()
    # pyautogui.alert(f"obinfo_trading:{obinfo_trading}") 
    obinfo_deposit2 = '' if 업데이트정보['request_deposit2'] =='' else 업데이트정보['request_deposit2'] #보증금2
    obinfo_deposit3 = '' if 업데이트정보['request_deposit3'] =='' else 업데이트정보['request_deposit3'] #보증금3
    obinfo_rent1 = '' if 업데이트정보['request_rent1'] =='' else 업데이트정보['request_rent1'] #월세1
    obinfo_rent2 = '' if 업데이트정보['request_rent2'] =='' else 업데이트정보['request_rent2'] #월세2
    obinfo_rent3 = 업데이트정보.get('obinfo_rent3', '')
    obinfo_rent3 = '' if 업데이트정보['request_rent3'] =='' else 업데이트정보['request_rent3'] #월세3    
    # pyautogui.alert(f" obinfo_deposit1:{obinfo_deposit2}/obinfo_rent1:{obinfo_rent1}\n obinfo_deposit2:{obinfo_deposit2}/obinfo_rent2:{obinfo_rent2}\n obinfo_deposit3:{obinfo_deposit3}/obinfo_rent3:{obinfo_rent3}") 
    request_manager = '' if 업데이트정보['request_manager'] =='' else 업데이트정보['request_manager']
    # pyautogui.alert(f"request_manager:{request_manager}") 
    request_mmoney = 업데이트정보['request_mmoney']
    # pyautogui.alert(f"request_mmoney:{request_mmoney}") 
    request_area1 = 업데이트정보['request_area1']
    # pyautogui.alert(f"request_area1:{request_area1}") 
    request_area2 = 업데이트정보['request_area2']
    # pyautogui.alert(f"request_area2:{request_area2}") 
    request_areatype1 = 업데이트정보['request_areatype1']
    # pyautogui.alert(f"request_areatype1:{request_areatype1}") 
    request_areatype2 = 업데이트정보['request_areatype2']
    # pyautogui.alert(f"request_areatype2:{request_areatype2}") 
    request_mlist = 업데이트정보['request_mlist']
    # pyautogui.alert(f"request_mlist:{request_mlist}") 
    tr_memo = 업데이트정보['tr_memo']
    # pyautogui.alert(f"tr_memo:{tr_memo}") 

    location_do = 업데이트정보['land_do']
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
    location_si = 업데이트정보['land_si']
    location_dong = 업데이트정보['land_dong']

    location_lijibun = 업데이트정보['land_jibun'] if 업데이트정보['land_li'] == '' else (업데이트정보['land_li'] + ' ' + 업데이트정보['land_jibun'])
    location_dongli = (업데이트정보['land_dong'] + 업데이트정보['land_jibun']) if 업데이트정보['land_li'] == '' else location_lijibun
    location_detail = location_dongli
    land_totarea = 업데이트정보['land_totarea']
    main_area = land_totarea
    land_memo = 업데이트정보['land_memo']
    land_memo_formatted = 메모에마크추가(land_memo , '· ')
    if land_memo_formatted:
        I_memo += ("<br>" if I_memo else "") + land_memo_formatted
    # pyautogui.alert(f"I_memo:{I_memo}") 
    land_importants = 업데이트정보.get('land_important', '').strip()
    main_important = land_importants 

    secret_1 = '' if tr_memo == '' else tr_memo + Keys.ENTER
    secret_2 = '' if land_memo == '' else land_memo + Keys.ENTER
    basic_secret = secret_1 + secret_2 #비밀메모
    # pyautogui.alert(f"basic_secret:{basic_secret}") 
        
    if tr_target == '건물' or tr_target == '층호수':
        building_grndflr = 업데이트정보['building_grndflr']
        building_ugrndflr = 업데이트정보['building_ugrndflr']
        building_archarea = 업데이트정보['building_archarea']
        building_totarea = 업데이트정보['building_totarea']
        main_area = building_totarea
        building_usedate = 업데이트정보['building_usedate']
        building_memo = 업데이트정보['building_memo']
        building_memo_formatted = 메모에마크추가(building_memo , '· ')
        # pyautogui.alert(f"building_memo_formatted:{building_memo_formatted}") 
        building_options = 업데이트정보.get('building_option', '').strip()
        main_option += ','+building_options if main_option != '' else building_options
        building_importants = 업데이트정보.get('building_important', '').strip()
        # pyautogui.alert(f"building_importants:{building_importants}") 
        main_important += ','+building_importants if building_importants != '' else building_importants
        if building_memo_formatted:
            I_memo += ("<br>" if I_memo else "") + building_memo_formatted
        secret_3 = '' if building_memo == '' else building_memo + Keys.ENTER
        basic_secret += secret_3
        # pyautogui.alert(f"secret_3:{secret_3}") 

    if tr_target == '층호수':
        room_num = 업데이트정보['room_num']
        location_room = '' if room_num == '' else ' ' + room_num
        room_floor = 업데이트정보['room_floor']
        # pyautogui.alert(f"room_floor:{room_floor}") 
        room_status = ' '+업데이트정보['room_status'] if 업데이트정보['room_status']!='미확인' else ' 상태미확인' #호실상태
        room_gate1 = ' '+업데이트정보['room_gate1'] if 업데이트정보['room_gate1']!='비밀번호' else ' 방' #내부출입1
        room_gate2 = ':'+업데이트정보['room_gate2'] if 업데이트정보['room_gate2'] != '' else '' #내부출입2  
        room_gate = room_status+room_gate1+room_gate2 if room_gate1 != ' 미확인' else ' 미확인'
        location_detail += location_room+room_gate
        # pyautogui.alert(f"location_detail:{location_detail}") 
        room_memo = 업데이트정보['room_memo'] #호실메모
        room_rcount = 업데이트정보.get('room_rcount', '')
        room_bcount = 업데이트정보.get('room_bcount', '')
        room_area1 = 업데이트정보['room_area1']
        main_area = room_area1
        room_areatype1 = 업데이트정보['room_areatype1']
        room_options = 업데이트정보.get('room_option', '').strip() #옵션선택
        main_option += ','+room_options if main_option != '' else room_options
        room_importants = 업데이트정보.get('room_important', '').strip()
        main_important += ','+room_importants if room_importants != '' else room_importants
        room_memo_formatted = 메모에마크추가(room_memo , '· ')
        if room_memo_formatted:
            I_memo += ("<br>" if I_memo else "") + room_memo_formatted
        secret_4 = '' if room_memo == '' else room_memo + Keys.ENTER
        basic_secret += secret_4
        # pyautogui.alert(f"secret_4:{secret_4}") 
    # print(f"object_code_new:{object_code_new}, formatted_date:{formatted_date}, admin_name:{admin_name}, request_code:{request_code}, ")
    basic_secret = f"[새홈{object_code_new}] 수정일:"+formatted_date+" "+admin_name + Keys.ENTER +" https://obangkr.cafe24.com/web/request/request_view/view_give_request_detail.php?request_code="+request_code
    main_area_pyeong = str(int(float(main_area)/3.305785)) if main_area != '' else ''

    # object_rtype = 업데이트정보['object_rtype']
    # pyautogui.alert(f"basic_secret:{basic_secret}") 
    # print(f"tr_target:{tr_target}, object_type1:{object_type1}, object_type2:{object_type2}, room_rcount:{room_rcount}, ")
    if tr_target == '층호수':
        object_info_code = room_code
        if object_type == '주거용':
            if room_rcount == '':
                pyautogui.alert("방개수 확인후 다시 시작하세요")
                # driver.close()
                # # WebDriver 종료
                driver.quit()    
                return            
            else:
                if float(room_rcount) >= 1 and float(room_rcount) < 2:
                    object_type1 = '원룸'
                    # pyautogui.alert(f"room_importants:{room_importants}") 
                    if float(room_rcount) >= 1 and float(room_rcount) < 1.5 :
                        if "오픈형" in room_importants:
                            object_type2 = "오픈형"
                        elif "분리형(현)" in room_importants or "분리형(베)" in room_importants:
                            object_type2 = "분리형"
                        else:
                            object_type2 = "분리형" 
                    elif float(room_rcount) >= 1.5 and float(room_rcount) < 1.8 :
                        object_type2 = '1.5룸'
                    elif float(room_rcount) >= 1.8 and float(room_rcount) < 2 :
                        object_type2 = '1.8룸'
                elif float(room_rcount) >= 2:
                    object_type1 = '투룸/쓰리룸+'
                    if float(room_rcount) == 2:
                        object_type2 = '투룸'
                    elif float(room_rcount) >= 3:
                        object_type2 = '쓰리룸+'
                # print(f"object_type2:{object_type2}")
                # pyautogui.alert(f"object_type2:{object_type2}")

        elif object_type == '상업용':
            object_type1 = '상가/사무실'
        elif object_type == '공업용':
            object_type1 = '공장/창고'
    elif tr_target == '건물':
        object_info_code = building_code
        if object_type == '공업용':
            object_type1 = '공장/창고'
        else:
            object_type1 = '통건물'
            if object_type == '주거용':
                object_type2 = '다가구주택'
            elif object_type == '상업용':
                object_type2 = '상업용건물'
    elif tr_target == '토지':
        object_info_code = land_code
        object_type1 = '토지'

    # pyautogui.alert("매물종류 선택 정상?")     
    if object_type1 != '':
        # pyautogui.alert(f"sele[object_type1]:{sele[object_type1]}") 
        driver.find_element(By.ID, f'category_{sele[object_type1][0]}').click() #매물종류
        print("object_type2:", object_type2)
        if len(sele[object_type1][1]) != 0: # 소분류
            for a in driver.find_elements(By.CLASS_NAME, f'main_{sele[object_type1][0]}'):
                print(a.text)
                if a.text == object_type2: 
                    a.click()   
        # pyautogui.alert("소분류 선택 정상?")    

    # 거래종류
    print(f"object_ttype:{object_ttype}")
    # object_ttype에 쉼표가 있는지 확인
    if ',' in object_ttype:
        거래종류값 = '전/월세' if '전세' in object_ttype and '월세' in object_ttype else object_ttype
    else:
        거래종류값 = object_ttype
    print(f"거래종류값:{거래종류값}")
    # pyautogui.alert(f"거래종류값:{거래종류값}")  
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
    # pyautogui.alert("거래금액수정 정상?")   

    #관리비
    if request_manager=='별도':
        modify_item(driver, "#mgr_price", request_mmoney)
    if tr_target == '층호수':
        
        # 관리내역 체크박스 요소들을 가져옴
        관리내역s = driver.find_elements(By.XPATH, '//*[@id="mgr_include_checkbox"]/input')
        # 물건의 관리비 포함 내역
        관리내역ex = request_mlist.split(',')
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
        # pyautogui.alert("관리내역ex 수정 정상?")  
            
        #실면적
        if request_area1 != '' : modify_item(driver, "#real_area", request_area1)
        #해당층
        if room_floor != '' : modify_item(driver, "#current_floor", room_floor)
        # 입주일
        driver.find_element(By.XPATH, '//*[@id="enter_year"]').clear() 
        #거주자가 있으면 '입주협의', 그외 '즉시입주'
        if '사용' in room_status:
            입주일값 = '입주협의'
        else:
            입주일값 = '즉시입주'
        driver.find_element(By.XPATH, '//*[@id="enter_year"]').send_keys(입주일값) 
        # pyautogui.alert("입주일값 수정 정상?")  
    #전체층
    # print("전체층: ", type(basic_totflr))
    # pyautogui.alert("전체층: ", basic_totflr)
    # modify_item(driver, "#total_floor", basic_totflr)

    print("비밀메모:", basic_secret)
    # 수정시 비밀메모를 갱신
    secret_box = driver.find_element(By.XPATH, '//*[@id="info_base"]/div[2]/div[13]/div[2]/textarea')
    secret_box.clear()  # 기존 내용을 지우고
    secret_box.send_keys(basic_secret) # 비밀메모
    # pyautogui.alert("비밀메모 수정 정상?")  

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
            "벽걸이에어컨": "에어컨",
            "천정형에어컨": "에어컨",
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
            if room_floor == '1':
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
        # pyautogui.alert("테마 수정 정상?")

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
        # pyautogui.alert("옵션 수정 정상?")

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
            object_detail += (('<p>' + f'● 방: {int(float(room_rcount))}개')+(f' / 욕실:{room_bcount}개</p>' if float(room_rcount) > 0 else '')) if float(room_rcount) > 0 else ''
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

        try:
            # time.sleep(1)
            print("수정후 시작")
            수정후최신으로갱신버튼들 = driver.find_elements(By.XPATH, '//*[@id="product_form"]/div[7]/button[2]')
            if len(수정후최신으로갱신버튼들) > 0:
                print("수정후최신으로갱신버튼들 개수:"+str(len(수정후최신으로갱신버튼들)))
                # 수정후최신으로갱신버튼들이 존재하는 경우의 코드
            else:
                print("수정후최신으로갱신버튼들이 페이지에 존재하지 않습니다.")       
            # pyautogui.alert("등록완료 수정 정상?")     
            # 수정후최신으로갱신버튼의 XPath를 사용하여 요소 찾기
            # time.sleep(1)
            수정후최신으로갱신버튼 = driver.find_element(By.XPATH, '//*[@id="product_form"]/div[7]/button[2]')
            수정후최신으로갱신버튼.click()
            try:
                # 최대 3초 동안 수정후최신으로갱신버튼이 사라질 때까지 대기
                WebDriverWait(driver, 3).until(EC.invisibility_of_element((By.XPATH, '//*[@id="product_form"]/div[7]/button[2]')))
                print("정상적으로 최신등록일로갱신되었습니다.")
            except:
                # 3초 내에 최신등록일로갱신 버튼이 사라지지 않으면 오류 메시지 출력
                pyautogui.alert("정상적으로 최신등록일로갱신되지 않았습니다.\n최신등록일로갱신완료후 계속 진행가능합니다.")            
            print("최신등록일로갱신 종료")

            # pyautogui.alert(f"{location_detail}\n\n등록완료 확인!! land_code:{land_code} building_code:{building_code} room_code:{room_code}")
        except Exception as e:
            pyautogui.alert("최신등록일로갱신시키기 에러발생:", str(e))
            print("최신등록일로갱신시키기 에러발생:", str(e))

#obang_data에서 가져온 obang_update에 포함된 obang_code를 업데이트 할 예정임





































complete_count = 0
restart_ok = 0
update_ok = 0
end_ok = 0
#작업순서 : 최신등록일업데이트 - 거래완료 및 비공개처리
def update_start():
    
    import datetime
    global complete_count
    global restart_ok
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
    # pyautogui.alert(obangData)
    # imgUpdate = obangData['업데이트매물']

    if not show_update_preview(obangData, before_day):
        print("사용자가 취소함")
        exit()
    
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
    오방매물정보 = obangData['오방매물정보']
    
    for update_code in obang_update:
        try:
            # WebDriverWait(driver, 10).until(EC.element_to_be_clickable(By.CSS_SELECTOR, "#search_id")).clear() #매물번호 입력창의 입력값 초기화
            driver.implicitly_wait(10)
            매물번호입력창 = driver.find_element(By.CSS_SELECTOR, "#search_id")
            매물번호입력창.clear() 
            print(f"{update_code} 1.매물번호입력창 초기화")
            매물번호입력창.send_keys(update_code) #매물번호입력창에 매물번호 입력
            print("----- 2.매물번호입력창에 매물번호 입력")
            time.sleep(0.2)
            매물번호입력창.send_keys(Keys.ENTER)
            print("----- 3.엔터(매물조회)")
            # driver.find_element(By.CSS_SELECTOR, "#admin_member_id > option:nth-child(1)").click() #담당자를 직원별로 선택
            # print("----- 3.담당자를 직원별로 선택")
            # WebDriverWait(driver, 10).until(
            #     EC.element_to_be_clickable((By.CSS_SELECTOR, "#go_keyword"))
            # ).click()
            # driver.find_element(By.CSS_SELECTOR, "#go_keyword").click() #검색버튼(돋보기) 클릭
            # print("----- 4.검색버튼(돋보기) 클릭")

            # 최대 5초 동안 기다리면서 strong 태그의 텍스트가 update_code와 같아질 때까지 대기
            WebDriverWait(driver, 5).until(
                lambda d: d.find_elements(By.CSS_SELECTOR, "#search-items tr strong")[0].text.strip() == update_code
            )



            #자료 존재유무 확인 = 첫번째목록의열개수가 1이면 자료없음을 의미
            첫번째목록의열개수 = len(driver.find_element(By.ID, "search-items").find_element(By.TAG_NAME, "tr").find_elements(By.TAG_NAME, "td"))
            # print(첫번째목록의열개수)
            # pyautogui.alert(f"첫번째목록의열개수 확인:{update_code}")
            if 첫번째목록의열개수 == 1:
                print(f"자료없는 오방코드: {update_code}")
                continue

            # 업데이트 전 등록일
            before_target = driver.find_element(By.CSS_SELECTOR, f"#tr_{update_code} > td:nth-child(15) > div").get_attribute('title').split(' ')[0]
            before_date = datetime.datetime.strptime(before_target , '%Y-%m-%d')
            today = datetime.datetime.today()
            print(f"----- before_date: ", before_date)
            # print(f"{update_code} today: ", today)
            # if before_date == today:            

            # 오늘 날짜와 비교하여 출력
            if before_target == str(datetime.date.today()):
                print("----- 5.Today! pass")
            elif before_date > today:
                print("----- 5.Future Date! pass")
            else:
                #업데이트 실행

                # 행과 토글 찾기
                행 = WebDriverWait(driver, 6).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, f"#tr_{update_code}"))
                )
                토글 = WebDriverWait(행, 6).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "td:nth-of-type(3) .btn-group[onclick^='activated_change']"))
                )
                제목 = WebDriverWait(행, 6).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "td:nth-of-type(9) .admin_title_section"))
                ).text
                # 조회수입력란 = WebDriverWait(행, 6).until(
                #     EC.presence_of_element_located((By.CSS_SELECTOR, "td:nth-of-type(18) span:nth-of-type(2) input[type='text']"))
                # )

                print("조회수입력란 찾음")
                # 기본제목여부 확인

                # 이미 비공개면 스킵
                if 비공개여부(토글) and not 제목 in ['상가/사무실','원룸','투룸','테스트','투룸/쓰리룸+']:
                    print(f"기본제목을 사용하지 않는 비공개매물 오방코드:{update_code}")  
                    #제목에 '금액'정보있으면 자동업데이트하지 않음

                    # continue

                    try:
                        #조회수 초기화2

                        # 1. viewbadge span 클릭해서 input 보이게 하기
                        view_span = WebDriverWait(행, 6).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, "td:nth-of-type(18) .viewbadge"))
                        )
                        view_span.click()
                        # 2. input 태그가 보이게 된 후 다시 찾기
                        조회수입력란 = WebDriverWait(행, 6).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, "td:nth-of-type(18) span:nth-of-type(2) input[type='text']"))
                        )
                        조회수입력란.send_keys(Keys.CONTROL + "a")
                        조회수입력란.send_keys("0")
                        print("조회수입력란 초기화")

                        토글.click() #공개로 전환
                        print("공개전환 완료")
                        restart_ok += 1  
                        # pyautogui.alert(f"조회수 초기화 확인")
                    except Exception as e:
                        print("조회수 초기화 및 공개전환 실패")
                        pyautogui.alert(f"토글버튼을 찾을 수 없습니다.\n{e}")

                    #수정페이지로 전환
                    driver.find_element(By.CSS_SELECTOR, f'#tr_{update_code} > td:nth-child(14) > div:nth-child(1)').click() #관리 클릭
                    driver.find_element(By.CSS_SELECTOR, f'#tr_{update_code} > td:nth-child(14) > div.dropdown.open > ul > li:nth-child(1)').click() #수정 클릭
                    #재등록 프로세스 시작
                    # pyautogui.alert(f"오방매물정보:{오방매물정보}")
                    선택된매물정보 = 오방매물정보.get(update_code)
                    print("선택된매물정보:",선택된매물정보)
                    # pyautogui.alert(f"선택된매물정보:{선택된매물정보}")
                    단일오방매물업데이트(driver, 선택된매물정보)
                    # try:
                    #     driver.implicitly_wait(10)
                    #     토글 = WebDriverWait(행, 10).until(
                    #         EC.element_to_be_clickable((By.CSS_SELECTOR, f"#tr_{update_code} > td:nth-child(3) > div"))
                    #     )   
                    #     토글.click()
                    # except Exception as e:
                    #     pyautogui.alert(f"토글버튼을 찾을 수 없습니다.\n{e}")
                    # pyautogui.alert(f"비공개 매물 오방코드:{update_code}")
                else:
                    print("----- 이미 공개된 매물")
                    # continue
                    # pyautogui.alert(f"이미 공개된 매물 오방코드:{update_code}")
                    print("----- 5.past Date! update")
                    driver.find_element(By.CSS_SELECTOR, f'#tr_{update_code} > td:nth-child(14) > div:nth-child(1)').click() #관리 클릭
                    print("----- 5-1.관리 클릭")
                    # time.sleep(1)
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
            pyautogui.alert(f"{update_code}업데이트 안됨")





    # pyautogui.alert("거래완료된 매물 전체 비공개처리를 진행하시겠습니까?")
    driver.find_element(By.CSS_SELECTOR, '#menu-product-1 > a').click() #매물->매물관리 클릭
    #거래완료된 매물 전체 비공개처리
    driver.implicitly_wait(10)
    # 비공개 선택
    driver.execute_script("""
    const v = 'public';  // 또는 'private' / ''
    const hidden = document.querySelector('#only_public');
    const form = document.querySelector('#search_form');
    if (hidden) hidden.value = v;
    if (form) form.dispatchEvent(new Event('submit', {bubbles:true, cancelable:true}));
    """)
    # 100개씩 보기
    Select(WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.NAME, "per_page")))).select_by_value("100")
    모든페이지_비공개처리결과 = 모든페이지_비공개처리(driver, obangData)
    if 모든페이지_비공개처리결과: 
        완료처리매물들 = 모든페이지_비공개처리결과.get("성공", [])
        end_ok += len(완료처리매물들)
    # pyautogui.alert(모든페이지_비공개처리결과,"코드점검")



    if popup_message(complete_count, len(금일등록매물), restart_ok, update_ok, end_ok):
        print(" 계속진행합니다.")
        process_wait(10) # 몇 시간뒤에 재작동할지 설정
        # update_start()
    else:
        print("멈춥니다")
        # 드라이버 종료
        driver.quit()

update_start()
