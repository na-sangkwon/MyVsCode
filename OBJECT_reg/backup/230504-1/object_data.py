import numpy as np

def getData(object_code_new):
    print("object_code_new: "+object_code_new)
    return_data = {}
    import pymysql

    conn = pymysql.connect(host='obangkr.cafe24.com', user='obangkr', password='Ddhqkd!1', charset='utf8')

    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('USE obangkr;')

    query = 'SELECT * FROM pr_object WHERE object_code_new = "%s"' % object_code_new
    cursor.execute(query)
    o_res = cursor.fetchall()
    num_rows = cursor.rowcount
    for row in o_res:
        # print(row['object_address'].decode('utf8'))
        
        obang_code = row['object_code_obang'].decode('utf8')
        land_code = row['land_code'].decode('utf8')
        building_code = row['building_code'].decode('utf8')
        room_code = row['room_code'].decode('utf8')
        object_ttype = row['object_ttype'].decode('utf8') #거래종류
        print('room_code: '+room_code)

    # object_type = o_res['object_type'].decode('utf8')
    # land_code = o_res['land_code'].decode('utf8')
    # building_code = o_res['building_code'].decode('utf8')
    # room_code = o_res['room_code'].decode('utf8')
    # print(f"{num_rows} rows returned by the query.")

    # query = 'SELECT * FROM pr_request AS p LEFT JOIN pr_request_give AS c ON p.request_code = c.request_code WHERE c.land_code = "%s" AND c.building_code = "%s" AND c.room_code = "%s"' % (land_code, building_code, room_code)
    # cursor.execute(query)
    query = 'SELECT * FROM pr_request AS p LEFT JOIN pr_request_give AS c ON p.request_code = c.request_code WHERE c.land_code = %s AND c.building_code = %s AND c.room_code = %s'
    params = (land_code, building_code, room_code)
    cursor.execute(query, params)
    g_res = cursor.fetchall()
    # request_main = g_res[0]['request_main'].decode('utf8')
    # print("request_main: "+request_main)

    query = 'SELECT * FROM pr_land WHERE land_code = "%s"' % land_code
    cursor.execute(query)
    l_res = cursor.fetchall()
    land_address = l_res[0]['land_address'].decode('utf8')
    # print(land_address)

    query = 'SELECT * FROM pr_building WHERE building_code = "%s"' % building_code
    cursor.execute(query)
    b_res = cursor.fetchall()

    query = 'SELECT * FROM pr_room WHERE room_code = "%s"' % room_code
    cursor.execute(query)
    r_res = cursor.fetchall()

    #거래정보
    request_code = g_res[0]['request_code'].decode('utf8') #의뢰번호
    object_type = g_res[0]['object_type'].decode('utf8') #물건종류
    object_type1 = g_res[0]['object_type1'].decode('utf8') #물건분류1
    object_type2 = g_res[0]['object_type2'].decode('utf8') #물건분류1
    tr_target = g_res[0]['tr_target'].decode('utf8') #거래대상
    tr_range = g_res[0]['tr_range'].decode('utf8') #거래범위
    trading = g_res[0]['request_trading'].decode('utf8') #매매금액
    deposit1 = g_res[0]['request_deposit1'].decode('utf8') #보증금1
    deposit2 = g_res[0]['request_deposit2'].decode('utf8') #보증금2
    deposit3 = g_res[0]['request_deposit3'].decode('utf8') #보증금3
    rent1 = g_res[0]['request_rent1'].decode('utf8') #월세1
    rent2 = g_res[0]['request_rent2'].decode('utf8') #월세2
    rent3 = g_res[0]['request_rent3'].decode('utf8') #월세3
    rdate = g_res[0]['request_rdate'] #거래가능시기
    surtax = g_res[0]['surtax'].decode('utf8') #부가세별도: Y
    manager = g_res[0]['request_manager'].decode('utf8') #관리비 미확인,있음,없음
    mmoney = g_res[0]['request_mmoney'].decode('utf8') #관리비금액
    mlist = g_res[0]['request_mlist'].decode('utf8') #관리비포함내역
    mmemo = g_res[0]['request_mmemo'].decode('utf8') #관리비메모
    tr_memo = g_res[0]['tr_memo'].decode('utf8') #거래메모
    premium_exist = g_res[0]['premium_exist'].decode('utf8') #권리금 미확인, 있음, 없음
    premium = g_res[0]['premium'].decode('utf8') #권리금+시설물 금액
    premium_content = g_res[0]['premium_content'].decode('utf8') #시설물포함내역

    #토지정보
    address = land_address #전체주소
    land_do = l_res[0]['land_do'].decode('utf8') #시도
    land_si = l_res[0]['land_si'].decode('utf8') #시군구
    land_dong = l_res[0]['land_dong'].decode('utf8') #읍면동
    land_li = l_res[0]['land_li'].decode('utf8') #리
    land_type = '산' if l_res[0]['land_type'].decode('utf8') == '2' else '일반' #대장구분 일반:1 산:2
    land_jibun = l_res[0]['land_jibun'].decode('utf8') #지번(숫자)
    land_important = l_res[0]['land_important'].decode('utf8') #토지특성
    land_option = l_res[0]['land_option'].decode('utf8') #토지옵션
    land_memo = l_res[0]['land_memo'].decode('utf8') #토지메모
    land_purpose = l_res[0]['land_purpose'].decode('utf8') #용도지역
    land_totarea = l_res[0]['land_totarea'].decode('utf8') #거래대상면적(총토지면적)
    landData = {
    'address': address
    ,'land_do': land_do
    ,'land_si': land_si
    ,'land_dong': land_dong
    ,'land_li': land_li
    ,'land_type': land_type
    ,'land_jibun': land_jibun
    ,'land_important': land_important
    ,'land_option': land_option
    ,'land_memo': land_memo
    ,'land_purpose': land_purpose
    ,'land_totarea': land_totarea
    }
    return_data["landData"] = landData

    #건물정보
    if tr_target == '건물' or tr_target == '층호수':
        building_name = '' if b_res[0]['building_name'].decode('utf8') == '' else b_res[0]['building_name'].decode('utf8') #건물명
        building_gate1 = b_res[0]['building_gate1'].decode('utf8') #건물출입 구분: 미확인,개방,열쇠,비밀번호 등
        building_gate2 = b_res[0]['building_gate2'].decode('utf8') #건물출입 세부정보
        building_pn = b_res[0]['building_pn'].decode('utf8') #전체주차가능대수
        building_memo = b_res[0]['building_memo'].decode('utf8') #건물메모
        building_important = b_res[0]['building_important'].decode('utf8') #건물특징
        building_option = b_res[0]['building_option'].decode('utf8') #건물옵션
        building_grndflr = b_res[0]['building_grndflr'] #지상층수
        building_ugrndflr = b_res[0]['building_ugrndflr'] #지하층수
        building_usedate = b_res[0]['building_usedate'] #사용승인일
        building_archarea = str(b_res[0]['building_archarea']) #건축면적
        building_totarea = str(b_res[0]['building_totarea']) #연면적
        building_direction = b_res[0]['building_direction'].decode('utf8') #건물방향
        building_purpose = b_res[0]['building_purpose'].decode('utf8') #건물방향
        building_elvcount = b_res[0]['building_elvcount'] #승강기수

        buildingData = {
        'building_name': building_name
        ,'building_gate1': building_gate1
        ,'building_gate2': building_gate2
        ,'building_pn': building_pn
        ,'building_memo': building_memo
        ,'building_important': building_important
        ,'building_option': building_option
        ,'building_grndflr': building_grndflr
        ,'building_ugrndflr': building_ugrndflr
        ,'building_usedate': building_usedate
        ,'building_archarea': building_archarea
        ,'building_totarea': building_totarea
        ,'building_direction': building_direction
        ,'building_purpose': building_purpose
        ,'building_elvcount': building_elvcount
        }
        return_data["buildingData"] = buildingData

    #호실정보
    if tr_target == '층호수':
        room_num = r_res[0]['room_num'].decode('utf8') #호실명
        room_floor = '' if r_res[0]['room_floor'].decode('utf8') == '' else r_res[0]['room_floor'].decode('utf8') #호실층수
        room_status = r_res[0]['room_status'].decode('utf8') #호실상태
        room_gate1 = r_res[0]['room_gate1'].decode('utf8') #내부출입 구분: 미확인,개방,열쇠,비밀번호 등
        room_gate2 = r_res[0]['room_gate2'].decode('utf8') #내부출입 세부정보
        room_memo = r_res[0]['room_memo'].decode('utf8') #호실메모
        room_rcount = r_res[0]['room_rcount'].decode('utf8') #방개수
        room_bcount = r_res[0]['room_bcount'].decode('utf8') #욕실수
        direction_stn = r_res[0]['r_direction'].decode('utf8') #호실방향기준
        room_direction = r_res[0]['room_direction'].decode('utf8') #호실방향
        room_area1 = r_res[0]['room_area1'].decode('utf8') #전용면적
        room_area2 = r_res[0]['room_area2'].decode('utf8') #공급면적
        room_important = r_res[0]['room_important'].decode('utf8') #호실특징
        room_option = r_res[0]['room_option'].decode('utf8') #호실옵션
        roomData = {
        'room_num': room_num
        ,'room_floor': room_floor
        ,'room_status': room_status
        ,'room_gate1': room_gate1
        ,'room_gate2': room_gate2
        ,'room_memo': room_memo
        ,'room_rcount': room_rcount
        ,'room_bcount': room_bcount
        ,'direction_stn': direction_stn
        ,'room_direction': room_direction
        ,'room_area1': room_area1
        ,'room_area2': room_area2
        ,'room_important': room_important
        ,'room_option': room_option
        }
        return_data["roomData"] = roomData
        

    do_path = land_do if land_do != '' else ''
    si_path = '\\'+land_si if land_si != '' else ''
    dong_path = '\\'+land_dong if land_dong != '' else ''
    li_path = '\\'+land_li if land_li != '' else ''
    type_path = '산' if land_type == '산' else ''
    jibun_path = '\\'+land_jibun if land_jibun != '' else ''
    folder_path = do_path + si_path + dong_path + li_path + type_path + jibun_path
    if tr_target == '건물' or tr_target == '층호수':
        building_name_path = '\\'+building_name if building_name != '' else ''
        folder_path += building_name_path
    if tr_target == '층호수':
        floor_path = '\\'+room_floor+'층' if room_floor != '' else ''
        num_path = '\\'+room_num+'' if room_num != '' else ''
        folder_path += floor_path + num_path

    print (folder_path)


    writeData = {
    'request_code': request_code
    ,'obang_code': obang_code
    ,'object_type': object_type
    ,'object_type1': object_type1
    ,'object_type2': object_type2
    ,'tr_target': tr_target
    ,'object_ttype': object_ttype
    ,'address': address
    ,'tr_range': tr_range
    ,'trading': trading
    ,'deposit1': deposit1
    ,'deposit2': deposit2
    ,'deposit3': deposit3
    ,'rent1': rent1
    ,'rent2': rent2
    ,'rent3': rent3
    ,'rdate': rdate
    ,'surtax': surtax
    ,'manager': manager
    ,'mmoney': mmoney
    ,'mlist': mlist
    ,'mmemo': mmemo
    ,'tr_memo': tr_memo
    ,'premium_exist': premium_exist
    ,'premium': premium
    ,'premium_content': premium_content
    }
    conn.close()
    # return {"landData": landData, "buildingData": buildingData, "roomData": roomData, "writeData": writeData, 'folderPath': folder_path, 'type_path': type_path}
    return_data.update({"writeData": writeData, 'folderPath': folder_path, 'type_path': type_path})
    print("writeData",writeData)
    # print("roomData",roomData)
    # print("buildingData",buildingData)
    # print("landData",landData)
    return return_data


