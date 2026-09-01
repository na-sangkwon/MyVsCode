# #DB
# import pymysql
# import datetime

# # today = datetime.datetime.now().strftime("%Y-%m-%d")
# # print(today)

# # 현재 날짜 가져오기 (datetime 객체로)
# today = datetime.datetime.now().date()

# import tkinter as tk
# from tkinter import simpledialog, messagebox
# import threading
# import time

# # 사용자로부터 입력 받는 함수
# def get_user_input():
#     # Tkinter 창 생성 (창은 숨겨집니다)
#     root = tk.Tk()
#     root.withdraw()

#     while True:
#         # 간단한 대화 상자를 통해 사용자 입력 받기
#         user_input = simpledialog.askstring("..", "업데이트할 데이터\n\n예시)\n하루전 데이터는 '1'\n이틀전 데이터는 '2'\n\n※한자리 자연수입력!!", initialvalue="1")
#         # 사용자가 취소를 누른 경우
#         if user_input is None:
#             break
#         # 입력값이 한 자리 숫자인지 확인
#         if user_input.isdigit() and 1 <= int(user_input) <= 9:
#             return int(user_input)  # 숫자로 변환하여 반환
#         else:
#             messagebox.showerror("오류", "한 자리 자연수만 입력해주세요 (1-9).")

#     # 입력된 값 반환
#     return user_input

# # before_day 값 설정
# before_day = get_user_input()
# # before_day = 1

# # 시작 날짜 계산
# start_date = today - datetime.timedelta(days=before_day)

# # 날짜를 문자열 형태로 변환
# today_str = today.strftime("%Y-%m-%d")
# start_date_str = start_date.strftime("%Y-%m-%d")

# conn = pymysql.connect(host='obangkr.cafe24.com', user='obangkr', password='Ddhqkd!1', charset='utf8')

# cursor = conn.cursor(pymysql.cursors.DictCursor)
# cursor.execute('USE obangkr;')

# # 2026년 오늘 날짜 기준으로 종료일(ad_end)이 안 지난 당근 광고 캐싱
# carrot_map = {}  # {대표매물번호: 당근광고코드} 구조
# c_query = f'''
#     SELECT object_code_new, ad_code 
#     FROM pr_externalad 
#     WHERE ad_site = '당근' AND ad_end >= "{today_str}"
# '''
# cursor.execute(c_query)
# # 🔥 [DB 로딩 직후 가로채기] 당근 광고 테이블에서 퍼 올린 원본 리스트를 변수에 담아 먼저 출력합니다.
# 당근_광고_원본목록 = cursor.fetchall()
# print("\n" + "🔍" * 35)
# print(f"[🔎 DB 실시간 로딩] 1. 당근 활성 광고 원본 행 데이터 수집 완료 (총 {len(당근_광고_원본목록)}건)")
# print("🔍" * 35)
# import pprint; pprint.pprint(당근_광고_원본목록, indent=4, width=120)

# for c_row in 당근_광고_원본목록:
#     if c_row['object_code_new']:
#         carrot_map[c_row['object_code_new']] = str(c_row['ad_code'])

# # 당근 대시보드용 카운트 세트 (중복 방지)
# dang_new_set = set()
# dang_today_set = set()
# dang_update_set = set()

# #최신등록일을 갱신할 오방코드 수집
# query = f'''SELECT * FROM pr_request AS p LEFT JOIN pr_request_give AS c ON p.request_code = c.request_code
#      WHERE p.request_del="N"
#      AND p.request_date BETWEEN "{start_date_str}" AND "{today_str}"
#      AND p.request_main != "전체"
#      AND p.tr_type = "내놓기"
#      AND (p.request_status = "접수" OR p.request_status = "진행")'''
# cursor.execute(query)
# g_res = cursor.fetchall()
# num_rows = cursor.rowcount

# # 🔥 [DB 로딩 직후 가로채기] 접수/진행 상태로 긁어온 오방 매물 원본 행 데이터를 루프 돌기 전에 출력
# print("\n" + "🔍" * 35)
# print(f"[🔎 DB 실시간 로딩] 2. 오방 최신등록 대상(접수/진행) 원본 데이터 수집 완료 (총 {num_rows}건)")
# print("🔍" * 35)
# import pprint; pprint.pprint(g_res, indent=4, width=120)


# # print(num_rows)
# # print(query)
# # print(g_res[1]['land_code'],g_res[1]['building_code'],g_res[1]['room_code'])
# 금일등록매물 = []
# 미등록의뢰수 = 0
# obang_update = []
# building_code = ''
# room_code = ''
# for row in g_res:
    
#     if row['request_wdate'] == today_str :
#         if o_res[0]['object_code_obang']=='':
#             금일등록매물.append(str(o_res[0]['object_code_obang']))
#         else:
#             미등록의뢰수 += 1
    
#     if row['land_code']:
#         land_code = row['land_code'] 
#     else: 
#         print('land_code is not ==> request_code:'+row['request_code'])
#         continue
#     if row['building_code']:building_code = row['building_code']
#     if row['room_code']:room_code = row['room_code']
#     # print("land_code: "+land_code, "building_code: "+building_code, "room_code: "+ room_code)
#     o_query = 'SELECT land_code,building_code,room_code,object_code_obang,object_code_new FROM pr_object WHERE object_del="N" AND land_code = %s AND building_code = %s AND room_code = %s'
#     params = (land_code, building_code, room_code)
#     cursor.execute(o_query, params)
#     o_res = cursor.fetchall()
#     try:
#         if o_res[0]['object_code_obang'] != '' : obang_update.append(str(o_res[0]['object_code_obang'])) 
#         print("request_code: "+str(row['request_code']), "land_code: "+land_code, "building_code: "+building_code, "room_code: "+ room_code, str(o_res[0]['object_code_obang']))
#     except:
#         print("pass")
#         pass
    
#     # if num_rows > 0:print("land_code: "+land_code, "building_code: "+building_code, "room_code: "+ room_code, o_res[0]['object_code_obang']) 

#     # print("object_code_obang: " + object_code_obang)
# print("미등록의뢰수: ",미등록의뢰수)
# print("금일등록매물("+str(len(금일등록매물))+"): ",금일등록매물)
# print("obang_update: ",obang_update)


# #관심매물(별표의뢰)의 오방코드 수집
# query = '''SELECT DISTINCT p.request_code, p.land_code, p.building_code, p.room_code FROM pr_request_give AS p
#            LEFT JOIN pr_request_fix AS c ON p.request_code = c.request_code
#            WHERE c.fix_del="N"'''
# # query = '''SELECT DISTINCT p.request_code, c.land_code, c.building_code, c.room_code FROM pr_request_fix AS p
# #            LEFT JOIN pr_request_give AS c ON p.request_code = c.request_code
# #            WHERE p.fix_del="N"'''
# cursor.execute(query)
# f_res = cursor.fetchall()

# # 🔥 [DB 로딩 직후 가로채기] pr_request_fix 별표 고정 관심매물 원본 데이터 출력
# print("\n" + "🔍" * 35)
# print(f"[🔎 DB 실시간 로딩] 3. 별표 관심매물 고유 의뢰 원본 데이터 수집 완료 (총 {len(f_res)}건)")
# print("🔍" * 35)
# import pprint; pprint.pprint(f_res, indent=4, width=120)

# print("관심매물개수:",len(f_res))
# obang_complete = []
# for row in f_res:
#     if row['land_code']:land_code = row['land_code']
#     if row['building_code']:building_code = row['building_code']
#     if row['room_code']:room_code = row['room_code']
#     # print("land_code: "+land_code, "building_code: "+building_code, "room_code: "+ room_code)
#     o_query = 'SELECT land_code,building_code,room_code,object_code_obang FROM pr_object WHERE object_del="N" AND land_code = %s AND building_code = %s AND room_code = %s'
#     params = (land_code, building_code, room_code)
#     cursor.execute(o_query, params)
#     o_res = cursor.fetchall()

#     # 🔥 당근부동산 광고 매물 카운트 분기 추가
#     try:
#         if o_res and o_res[0].get('object_code_new') in carrot_map:
#             dang_code = carrot_map[o_res[0]['object_code_new']]
#             dang_update_set.add(dang_code)  # 일반 수정 대상 포함
            
#             req_wdate_str = str(row['request_wdate'])
#             # 신규등록 (기간 기준)
#             if start_date_str <= req_wdate_str <= today_str:
#                 dang_new_set.add(dang_code)
#             # 금일등록 (오늘 기준)
#             if req_wdate_str == today_str:
#                 dang_today_set.add(dang_code)
#     except:
#         pass

#     try:
#         if o_res[0]['object_code_obang'] != '' : obang_update.append(str(o_res[0]['object_code_obang'])) 
#         # print("request_code: "+str(row['request_code']), "land_code: "+land_code, "building_code: "+building_code, "room_code: "+ room_code, str(o_res[0]['object_code_obang']))
#     except:
#         print("pass")
#         pass

# import random
# # 리스트의 순서를 랜덤하게 섞습니다.
# random.shuffle(obang_update)

# #완료처리해야할 오방코드 수집
# query = f'''SELECT * FROM pr_request AS p LEFT JOIN pr_request_give AS c ON p.request_code = c.request_code
#      WHERE p.request_del="N"
#      AND p.request_date BETWEEN "{start_date_str}" AND "{today_str}"
#      AND p.request_main != "전체"
#      AND p.tr_type = "내놓기"
#      AND (p.request_status = "성공" OR p.request_status = "실패")'''
# cursor.execute(query)
# g_res = cursor.fetchall()

# # 🔥 [DB 로딩 직후 가로채기] 성공/실패 처리된 거래완료 대상 원본 데이터 출력
# print("\n" + "🔍" * 35)
# print(f"[🔎 DB 실시간 로딩] 4. 거래완료(성공/실패) 비공개 처리 대상 원본 데이터 수집 완료 (총 {len(g_res)}건)")
# print("🔍" * 35)
# import pprint; pprint.pprint(g_res, indent=4, width=120)

# obang_complete = []
# dang_complete_set = set()  # 🔥 당근 완료 매물 세트 초기화

# for row in g_res:
    
#     if row['land_code']:land_code = row['land_code']
#     if row['building_code']:building_code = row['building_code']
#     if row['room_code']:room_code = row['room_code']
#     # 🔥 쿼리에 object_code_new 필드 추가
#     o_query = 'SELECT land_code,building_code,room_code,object_code_obang,object_code_new FROM pr_object WHERE object_del="N" AND land_code = %s AND building_code = %s AND room_code = %s'
#     params = (land_code, building_code, room_code)
#     cursor.execute(o_query, params)
#     o_res = cursor.fetchall()
#     try:
#         if o_res[0]['object_code_obang'] != '' : obang_complete.append(str(o_res[0]['object_code_obang'])) 
        
#         # 🔥 거래 완료된 매물이 당근 광고 중인 매물이었을 경우 코드 수집
#         if o_res and o_res[0].get('object_code_new') in carrot_map:
#             dang_complete_set.add(carrot_map[o_res[0]['object_code_new']])
#     except:
#         pass

# # 🔥 최종 당근 집계 결과 콘솔 출력 추가
# print("\n--- 당근부동산 집계 결과 ---")
# print("당근_신규등록:", len(dang_new_set))
# print("당근_금일등록:", len(dang_today_set))
# print("당근_일반수정:", len(dang_update_set))
# print("당근_거래완료:", len(dang_complete_set))

# cursor.close()
# conn.close()