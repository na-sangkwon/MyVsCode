#DB
import pymysql
import datetime

today = datetime.datetime.now().strftime("%Y-%m-%d")
print(today)
conn = pymysql.connect(host='obangkr.cafe24.com', user='obangkr', password='Ddhqkd!1', charset='utf8')

cursor = conn.cursor(pymysql.cursors.DictCursor)
cursor.execute('USE obangkr;')

query = f'''SELECT * FROM pr_request AS p LEFT JOIN pr_request_give AS c ON p.request_code = c.request_code
     WHERE p.request_del="N"
     AND p.request_date = "{today}"
     AND p.request_main != "전체"
     AND p.tr_type = "내놓기"
     AND (p.request_status = "접수" OR p.request_status = "진행")'''
cursor.execute(query)
g_res = cursor.fetchall()
num_rows = cursor.rowcount
# print(num_rows)
# print(query)
# print(g_res[1]['land_code'],g_res[1]['building_code'],g_res[1]['room_code'])
obang_codes = []
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
        if o_res[0]['object_code_obang'].decode('utf8') != '' : obang_codes.append(str(o_res[0]['object_code_obang'].decode('utf8'))) 
        print("request_code: "+str(row['request_code'].decode('utf8')), "land_code: "+land_code, "building_code: "+building_code, "room_code: "+ room_code, str(o_res[0]['object_code_obang'].decode('utf8')))
    except:
        print("pass")
        pass
    
    # if num_rows > 0:print("land_code: "+land_code, "building_code: "+building_code, "room_code: "+ room_code, o_res[0]['object_code_obang'].decode('utf8')) 

    # print("object_code_obang: " + object_code_obang)
print(obang_codes)

# print("object_code_obang: "+object_code_obang)
#내놓기의뢰에서 의뢰상태가 접수 또는 진행 중인 의뢰코드 수집
