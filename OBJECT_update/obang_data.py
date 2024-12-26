#DB
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

# 사용자로부터 입력 받는 함수
def get_user_input():
    # Tkinter 창 생성 (창은 숨겨집니다)
    root = tk.Tk()
    root.withdraw()

    while True:
        # 간단한 대화 상자를 통해 사용자 입력 받기
        user_input = simpledialog.askstring("..", "업데이트할 데이터\n\n예시)\n하루전 데이터는 '1'\n이틀전 데이터는 '2'\n\n※한자리 자연수입력!!", initialvalue="1")
        # 사용자가 취소를 누른 경우
        if user_input is None:
            break
        # 입력값이 한 자리 숫자인지 확인
        if user_input.isdigit() and 1 <= int(user_input) <= 9:
            return int(user_input)  # 숫자로 변환하여 반환
        else:
            messagebox.showerror("오류", "한 자리 자연수만 입력해주세요 (1-9).")

    # 입력된 값 반환
    return user_input

# before_day 값 설정
before_day = get_user_input()
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
obang_update = []
building_code = ''
room_code = ''
for row in g_res:
    
    if row['request_wdate'] == today_str :
        if o_res[0]['object_code_obang']=='':
            금일등록매물.append(str(o_res[0]['object_code_obang']))
        else:
            미등록의뢰수 += 1
    
    if row['land_code']:
        land_code = row['land_code'] 
    else: 
        print('land_code is not ==> request_code:'+row['request_code'])
        continue
    if row['building_code']:building_code = row['building_code']
    if row['room_code']:room_code = row['room_code']
    # print("land_code: "+land_code, "building_code: "+building_code, "room_code: "+ room_code)
    o_query = 'SELECT land_code,building_code,room_code,object_code_obang FROM pr_object WHERE object_del="N" AND land_code = %s AND building_code = %s AND room_code = %s'
    params = (land_code, building_code, room_code)
    cursor.execute(o_query, params)
    o_res = cursor.fetchall()
    try:
        if o_res[0]['object_code_obang'] != '' : obang_update.append(str(o_res[0]['object_code_obang'])) 
        print("request_code: "+str(row['request_code']), "land_code: "+land_code, "building_code: "+building_code, "room_code: "+ room_code, str(o_res[0]['object_code_obang']))
    except:
        print("pass")
        pass
    
    # if num_rows > 0:print("land_code: "+land_code, "building_code: "+building_code, "room_code: "+ room_code, o_res[0]['object_code_obang']) 

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
    if row['land_code']:land_code = row['land_code']
    if row['building_code']:building_code = row['building_code']
    if row['room_code']:room_code = row['room_code']
    # print("land_code: "+land_code, "building_code: "+building_code, "room_code: "+ room_code)
    o_query = 'SELECT land_code,building_code,room_code,object_code_obang FROM pr_object WHERE object_del="N" AND land_code = %s AND building_code = %s AND room_code = %s'
    params = (land_code, building_code, room_code)
    cursor.execute(o_query, params)
    o_res = cursor.fetchall()
    try:
        if o_res[0]['object_code_obang'] != '' : obang_update.append(str(o_res[0]['object_code_obang'])) 
        # print("request_code: "+str(row['request_code']), "land_code: "+land_code, "building_code: "+building_code, "room_code: "+ room_code, str(o_res[0]['object_code_obang']))
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
    
    if row['land_code']:land_code = row['land_code']
    if row['building_code']:building_code = row['building_code']
    if row['room_code']:room_code = row['room_code']
    # print("land_code: "+land_code, "building_code: "+building_code, "room_code: "+ room_code)
    o_query = 'SELECT land_code,building_code,room_code,object_code_obang FROM pr_object WHERE object_del="N" AND land_code = %s AND building_code = %s AND room_code = %s'
    params = (land_code, building_code, room_code)
    cursor.execute(o_query, params)
    o_res = cursor.fetchall()
    try:
        if o_res[0]['object_code_obang'] != '' : obang_complete.append(str(o_res[0]['object_code_obang'])) 
        # print("request_code: "+str(row['request_code']), "land_code: "+land_code, "building_code: "+building_code, "room_code: "+ room_code, str(o_res[0]['object_code_obang']))
    except:
        # print("pass")
        pass
# print("obang_complete: ",obang_complete)
cursor.close()
conn.close()