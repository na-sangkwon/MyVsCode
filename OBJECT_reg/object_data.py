import numpy as np
import pyautogui 
import datetime
import pymysql

def DB연결후ConCursor반환():
    """DB 연결을 수행하고 커넥션과 커서를 반환"""
    try:
        conn = pymysql.connect(
            host='obangkr.cafe24.com',
            user='obangkr',
            password='Ddhqkd!1',
            charset='utf8',
            database='obangkr'
        )
        print("✅ DB 연결 성공")
        return conn, conn.cursor(pymysql.cursors.DictCursor)  # (conn, cursor) 반환
    except pymysql.err.OperationalError as e:
        print("❌ DB 연결 실패1:", str(e))
        return None, None  # 연결 실패 시 (None, None) 반환
    
def getAdminData(cursor, userid):
    try:
        query = 'SELECT * FROM pr_admin WHERE admin_del="N" AND admin_id = "%s"' % userid
        # params = (userid, userpw)
        cursor.execute(query)
        admin_res = cursor.fetchall() 
        # print('admin_res:',admin_res)
        # 사용자정보
        admin_id = admin_res[0]['admin_id']   
        admin_name = admin_res[0]['admin_name']
        admin_phone1 = admin_res[0]['admin_phone1']
        ad_id = admin_res[0]['admin_id']
        # admin_email = admin_res[0]['admin_email']
        # admin_pw = admin_res[0]['admin_pw']
        ad_email = admin_res[0]['ad_email']
        ad_pw = admin_res[0]['ad_pw']
        zigbang_tag = admin_res[0]['zigbang_tag']
        obang_id = admin_res[0]['obang_id']
        obang_pw = admin_res[0]['obang_pw']
        zigbang_id = admin_res[0]['zigbang_id']
        zigbang_pw = admin_res[0]['zigbang_pw']
        obs_id = admin_res[0]['obs_id']
        obs_pw = admin_res[0]['obs_pw']
        naver_id = admin_res[0]['naver_id']
        naver_pw = admin_res[0]['naver_pw']
        hanbang_id = admin_res[0]['hanbang_id']
        hanbang_pw = admin_res[0]['hanbang_pw']
        dabang_id = admin_res[0].get('dabang_id', '') 
        dabang_pw = admin_res[0].get('dabang_pw', '')
        daangn_id = admin_res[0].get('daangn_id', '') 
        daangn_pw = admin_res[0].get('daangn_pw', '')

        adminData = {
            'admin_id': admin_id,
            'admin_name': admin_name,
            'admin_phone1': admin_phone1,
            'ad_id': ad_id,
            'ad_pw': ad_pw,
            'zigbang_tag': zigbang_tag,
            'ad_email': ad_email,
            'obang_id': obang_id,
            'obang_pw': obang_pw,
            'zigbang_id': zigbang_id,
            'zigbang_pw': zigbang_pw,
            'obs_id': obs_id,
            'obs_pw': obs_pw,
            'naver_id': naver_id,
            'naver_pw': naver_pw,
            'hanbang_id': hanbang_id,
            'hanbang_pw': hanbang_pw,
            'dabang_id': dabang_id,
            'dabang_pw': dabang_pw,  
            'daangn_id': daangn_id,
            'daangn_pw': daangn_pw          
        }
        return adminData
    except Exception as e:
        print("❌ DB 연결 실패2:", str(e))
        return None
def getAdData(광고사이트명, userid, userpw, object_code_new_list=None):
    # [2026-09-02 추가] object_code_new_list(매물번호 리스트)를 주면 그 매물들만 대상으로 좁힌다 —
    # 웹에서 "이 매물들만 연장등록" 요청을 그대로 이 함수로 흘려보내기 위함(안 주면 기존과 100%
    # 동일하게 전체 만료매물 대상). 기존 호출부(test.py 등)는 이 인자를 안 넘기므로 동작이 전혀
    # 바뀌지 않는다.
    print("광고사이트명: "+광고사이트명)
    # pyautogui.alert("광고사이트명: "+광고사이트명)
    print("userid: "+userid)
    print("userpw: "+userpw)
    return_data = {}
    conn, cursor = DB연결후ConCursor반환()  # ✅ DB 연결 함수 호출
    adminData = getAdminData(cursor, userid)
    print('adminData:',adminData)
    return_data['adminData'] = adminData

    try:
        today = datetime.date.today()
        # query = """
        #     SELECT
        #         e.object_code_new, e.admin_id, e.ad_site, e.ad_code, e.ad_start, e.ad_end,
        #         e.ad_memo, o.object_status
        #     FROM pr_externalad e
        #     LEFT JOIN pr_object o
        #         ON e.object_code_new = o.object_code_new
        #     WHERE e.object_code_new = %s
        # """
        # cursor.execute(query, ('646543'))
        query = """
            SELECT
                e.object_code_new, e.admin_id, e.ad_site, e.ad_code, e.ad_start, e.ad_end,
                e.ad_memo, o.object_status, o.object_rtype, o.object_ttype, o.object_tmoney1, o.object_tmoney2, o.object_mmoney,
                r.master_name  -- 소유자 이름 필드 추가
            FROM pr_externalad e
            LEFT JOIN pr_object o
                ON e.object_code_new = o.object_code_new
            LEFT JOIN pr_request_give r  -- pr_request 테이블 조인 추가
                ON o.land_code = r.land_code
                AND o.building_code = r.building_code
                AND o.room_code = r.room_code
            WHERE  r.give_del = %s
            AND e.ad_site = %s
            AND e.ad_end < %s
            AND o.object_status IN ('중개요청','거래완료')
            """ + (f"AND e.object_code_new IN ({', '.join(['%s'] * len(object_code_new_list))})\n" if object_code_new_list else "") + """
            ORDER BY ad_end DESC
            # LIMIT 2
        """        
        # query = """
        #     SELECT 
        #         e.object_code_new, e.admin_id, e.ad_site, e.ad_code, e.ad_start, e.ad_end, 
        #         e.ad_memo, o.object_status, o.object_ttype, o.object_tmoney1, o.object_tmoney2, o.object_mmoney 
        #     FROM pr_externalad e
        #     LEFT JOIN pr_object o 
        #         ON e.object_code_new = o.object_code_new
        #     WHERE e.ad_site = %s 
        #     AND e.ad_end < %s
        #     AND o.object_status IN ('중개요청','거래완료')
        #     ORDER BY ad_end DESC
        #     # LIMIT 2
        # """
        params = ('N', 광고사이트명, today) + (tuple(object_code_new_list) if object_code_new_list else ())
        cursor.execute(query, params)
        ad_res = cursor.fetchall() 
        ad_rows = cursor.rowcount
        # 광고 사이트별 정보를 담을 딕셔너리 초기화
        ad_info = {'한방': [], '네이버': [], '써브': [], 'KB부동산': [], '직방': [], '다방': [], '당근': []}
        # print("ad_res: ", ad_res)
        # pyautogui.alert("광고사이트명: "+광고사이트명)
        if not ad_res:
            return None  # 연장할 매물이 없으면 None 반환
        else:    
            # 광고 데이터를 딕셔너리에 저장
            for ad in ad_res:
                ad_site = ad['ad_site']
                # print("ad_code:"+ad['ad_code']+" object_code_new:"+ad['object_code_new']+" admin_id:"+ad['admin_id'])
                # continue
                if userid != ad['admin_id'] and userid != 'omnsk8': continue
                if ad_site in ad_info:
                    print("ad_site:"+ad_site)
                    print("ad:",ad)
                    ad_info[ad_site].append({
                        'admin_id': ad['admin_id'] if ad['admin_id'] is not None else '',
                        'ad_code': ad['ad_code'] if ad['ad_code'] is not None else '',
                        'ad_start': ad['ad_start'] if ad['ad_start'] != '0000-00-00' else '',
                        'ad_end': ad['ad_end'] if ad['ad_end'] != '0000-00-00' else '',
                        'ad_memo': ad['ad_memo'] if ad['ad_memo'] is not None else '',
                        #기본 네이버매물정보 외 물건정보(물건상태 등)
                        'object_code_new': ad['object_code_new'],
                        'object_status': ad['object_status'],
                        'object_rtype': ad['object_rtype'],
                        'object_ttype': ad['object_ttype'],
                        'object_tmoney1': ad['object_tmoney1'],
                        'object_tmoney2': ad['object_tmoney2'],
                        'object_mmoney': ad['object_mmoney'],
                        'master_name': ad['master_name']
                    })    
            print('ad_rows:',ad_rows)
            print("ad_info1===>", ad_info)
            # pyautogui.alert(len(ad_info['네이버']))
            # 반환 데이터에 추가
            return_data["adData"] = ad_info 
            return_data["등록방식"] = '종료매물등록'
    except Exception as e:
        print(" 오류발생:", str(e))
        pyautogui.alert(str(e),"오류발생: ")
    finally:
        #반환해줘야할 데이터: 관리자정보, 네이버매물정보, 해당 물건정보
        # pyautogui.alert(return_data)
        return return_data
    
    
    # pyautogui.alert("확인")
    # try:
    #     conn = pymysql.connect(host='obangkr.cafe24.com', user='obangkr', password='Ddhqkd!1', charset='utf8', database='obangkr')
    #     print("서버와의 연결이 정상적으로 수립되었습니다.")
    # except pymysql.err.OperationalError as e:
    #     print("서버와의 연결이 실패했습니다:", str(e))    
    # # conn = pymysql.connect(host='obangkr.cafe24.com', user='obangkr', password='Ddhqkd!1', charset='utf8')
    # cursor = conn.cursor(pymysql.cursors.DictCursor)
    # cursor.execute('USE obangkr;')    


def getData(object_code_new, userid, userpw):
    print("object_code_new: "+object_code_new)
    print("userid: "+userid)
    print("userpw: "+userpw)
    return_data = {}
    conn, cursor = DB연결후ConCursor반환()  # ✅ DB 연결 함수 호출

    adminData = getAdminData(cursor, userid)
    # pyautogui.alert(f"선택된 매물번호 object_code_new: {object_code_new}")
    # 매물번호가 없으면 네이버 연장할 데이터 조회
    if not object_code_new:
        today = datetime.date.today()
        query = """
        SELECT admin_id, ad_site, ad_code, ad_start, ad_end, ad_memo 
        FROM pr_externalad 
        WHERE ad_site = '네이버' 
        AND ad_end < %s
        LIMIT 2
        """
        cursor.execute(query, (today,))
        ad_res = cursor.fetchall() 
        ad_rows = cursor.rowcount
        # 광고 사이트별 정보를 담을 딕셔너리 초기화
        ad_info = {'한방': [], '네이버': [], '써브': [], 'KB부동산': [], '직방': [], '다방': [], '당근': []}
        # print("ad_res: ", ad_res)
        if not ad_res:
            return None  # 연장할 매물이 없으면 None 반환
        else:    
            # 광고 데이터를 딕셔너리에 저장
            for ad in ad_res:
                ad_site = ad['ad_site']
                if ad_site in ad_info:
                    print("ad_site:"+ad_site)
                    print("ad:",ad)
                    ad_info[ad_site].append({
                        'admin_id': ad['admin_id'] if ad['admin_id'] is not None else '',
                        'ad_code': ad['ad_code'] if ad['ad_code'] is not None else '',
                        'ad_start': ad['ad_start'] if ad['ad_start'] != '0000-00-00' else '',
                        'ad_end': ad['ad_end'] if ad['ad_end'] != '0000-00-00' else '',
                        'ad_memo': ad['ad_memo'] if ad['ad_memo'] is not None else ''
                    })           
    else:    
        print(f"작업중인 매물번호 object_code_new ===>{object_code_new}")
        query = 'SELECT admin_id, ad_site, ad_code, ad_start, ad_end, ad_memo FROM pr_externalad WHERE object_code_new = "%s"' % object_code_new
        cursor.execute(query)
        ad_res = cursor.fetchall() 
        ad_rows = cursor.rowcount
        # 광고 사이트별 정보를 담을 딕셔너리 초기화
        ad_info = {'한방': {}, '네이버': {}, '써브': {}, 'KB부동산': {}, '직방': [], '다방': [], '당근': []}
        print("ad_res: ", ad_res)
        # if not ad_res:
        #     return None  # 연장할 매물이 없으면 None 반환
        # else:    
        # 광고 데이터를 딕셔너리에 저장
        for ad in ad_res:
            ad_site = ad['ad_site']
            if ad_site in ad_info:
                print("ad_site:"+ad_site)
                print("ad:",ad)
                ad_info[ad_site] = {
                    'admin_id': ad['admin_id'] if ad['admin_id'] is not None else '',
                    'ad_code': ad['ad_code'] if ad['ad_code'] is not None else '',
                    'ad_start': ad['ad_start'] if ad['ad_start'] != '0000-00-00' else '',
                    'ad_end': ad['ad_end'] if ad['ad_end'] != '0000-00-00' else '',
                    # 'ad_start': ad['ad_start'].strftime('%Y-%m-%d') if ad['ad_start'] else '',
                    # 'ad_end': ad['ad_end'].strftime('%Y-%m-%d') if ad['ad_end'] else '',
                    'ad_memo': ad['ad_memo'] if ad['ad_memo'] is not None else ''
                }        
    print('ad_rows 데이터조회:',ad_rows)
    # conn.close()
    print("ad_info 데이터조회:", ad_info)
    # 반환 데이터에 추가
    return_data["adData"] = ad_info

    if not object_code_new: 
        print("return_data", return_data)
        return return_data

    adminData = getAdminData(cursor, userid)
    print('adminData 데이터조회:',adminData)
    return_data['adminData'] = adminData

    query = 'SELECT * FROM pr_object WHERE object_code_new = "%s"' % object_code_new
    cursor.execute(query)
    o_res = cursor.fetchall()
    num_rows = cursor.rowcount
    print('num_rows:',num_rows)
    if num_rows == 0:
        print(object_code_new+'는 사용되지 않는 매물번호입니다.')
        # pyautogui.alert(object_code_new+'는 사용되지 않는 매물번호입니다.')
        # cursor.close()
        # conn.close()
        return False
    else:
        # pyautogui.alert(o_res)
        for row in o_res:
            # print(row['object_address'])
            
            obang_code = row['object_code_obang']
            land_code = row['land_code']
            building_code = row['building_code']
            room_code = row['room_code']
            object_ttype = row['object_ttype'] #거래종류
            object_title = row['object_title'] #매물제목
            object_content = row['object_content'] #매물설명
            
        # object_type = o_res['object_type']
        # land_code = o_res['land_code']
        # building_code = o_res['building_code']
        # room_code = o_res['room_code']
        # print(f"{num_rows} rows returned by the query.")

        print('land_code: '+land_code)
        print('building_code: '+building_code)
        print('room_code: '+room_code)
        print('object_ttype: '+object_ttype)
        
        query = 'SELECT * FROM pr_BrentalInfo WHERE building_code = "%s"' % building_code
        cursor.execute(query)
        brental_res = cursor.fetchall()
        brData = []
        for room_info in brental_res:
            brData.append(room_info)
        return_data["brData"] = brData
        # return_data["brData"]['r_count'] = r_count  
        # print(">>>>>brData",brData)
        # pyautogui.alert('확인'+str(len(brData)))

            
        # query = 'SELECT * FROM pr_request AS p LEFT JOIN pr_request_give AS c ON p.request_code = c.request_code WHERE c.land_code = "%s" AND c.building_code = "%s" AND c.room_code = "%s"' % (land_code, building_code, room_code)
        # cursor.execute(query)
        query = 'SELECT * FROM pr_request AS p LEFT JOIN pr_request_give AS c ON p.request_code = c.request_code WHERE p.request_del="N" AND c.land_code = %s AND c.building_code = %s AND c.room_code = %s'
        params = (land_code, building_code, room_code)
        cursor.execute(query, params)
        g_res = cursor.fetchall()
        request_main = g_res[0]['request_main']
        print("g_res 데이터조회: ", g_res)
        num_rows1 = cursor.rowcount
        print("num_rows1: "+ str(num_rows1))
        if num_rows1 == 0:
            print(object_code_new+'는 의뢰가 존재하지 않는 매물번호입니다.')
            update_query = f'UPDATE pr_object SET object_del="Y" WHERE object_code_new="{object_code_new}"'
            cursor.execute(update_query)
            conn.commit()            
            return False
        # quit()        
        #거래정보
        request_code = g_res[0]['request_code'] #의뢰번호
        # print("동선확인3")  
        master_name = g_res[0]['master_name'] #임시소유자명
        master_check = g_res[0]['master_check'] #등기확인
        object_type = g_res[0]['object_type'] #물건종류
        # print("동선확인3")  
        object_type1 = g_res[0]['object_type1'] #물건분류1
        # print("동선확인4")  
        object_type2 = g_res[0]['object_type2'] #물건분류1
        # print("동선확인5")  
        tr_target = g_res[0]['tr_target'] #거래대상
        tr_range = g_res[0]['tr_range'] #거래범위
        first_trade = g_res[0]['first_trade'] #우선거래
        trading = g_res[0]['request_trading'] #매매금액
        deposit1 = g_res[0]['request_deposit1'] #보증금1
        deposit2 = g_res[0]['request_deposit2'] #보증금2
        deposit3 = g_res[0]['request_deposit3'] #보증금3
        rent1 = g_res[0]['request_rent1'] #월세1
        rent2 = g_res[0]['request_rent2'] #월세2
        rent3 = g_res[0]['request_rent3'] #월세3
        flexible_deposit = g_res[0]['flexible_deposit'] #보증금조정가능여부
        rdate = g_res[0]['request_rdate'] #거래가능시기
        surtax = g_res[0]['surtax'] #부가세별도: Y
        manager = g_res[0]['request_manager'] #관리비 미확인,있음,없음
        mmoney = g_res[0]['request_mmoney'] #관리비금액
        mlist = g_res[0]['request_mlist'] #관리비포함내역
        mmemo = g_res[0]['request_mmemo'] #관리비메모
        tr_memo = g_res[0]['tr_memo'] #거래메모
        premium_exist = g_res[0]['premium_exist'] #권리금 미확인, 있음, 없음
        premium = g_res[0]['premium'] #권리금+시설물 금액
        premium_content = g_res[0]['premium_content'] #시설물포함내역
        request_term1 = g_res[0]['request_term1'] #계약기간하한
        request_term2 = g_res[0]['request_term2'] #계약기간상한
        client_code = g_res[0]['client_code']
        
        # try:
        # except Exception as e:
        #     print("오류체크 :", str(e))

        query = 'SELECT * FROM pr_land WHERE land_code = "%s"' % land_code
        cursor.execute(query)
        l_res = cursor.fetchall()
        landCount = cursor.rowcount
        return_data["landCount"] = landCount  
        if l_res:
            # 토지정보를 저장할 빈 딕셔너리
            landData = []  # 결과 데이터를 저장할 리스트
            for row in l_res:
                # 원하는 필드들 선택
                selected_fields = ['land_do', 'land_si', 'land_dong', 'land_li', 'land_main', 'land_type', 'land_jibun', 'land_jibung',
                                   'representing_jibun','representing_jimok','representing_purpose','representing_use','land_roadsize',
                                   'land_important','land_option','land_terms','land_memo','land_purpose','land_totarea','land_adjoiningroad']
                selected_data = {field: row[field] for field in selected_fields}
                land_address = row['land_address']
                address = land_address
                pnu = row['pnu']
                sigunguCd = pnu[:5]
                bjdongCd = pnu[5:10]
                bun = pnu[-8:-4]
                ji = pnu[-4:]                
                land_do = row['land_do'] #시도
                land_si = row['land_si'] #시군구
                land_dong = row['land_dong'] #읍면동
                land_li = row['land_li'] #리
                land_main = row['land_main']
                land_type = '산' if row['land_type'] == '2' else '일반' #대장구분 일반:1 산:2
                land_jibun = row['land_jibun'] #지번(숫자)  
                land_jibung = row['land_jibung'] #지번(숫자)  
                representing_jibun = row['representing_jibun'] 
                representing_jimok = row['representing_jimok'] 
                representing_purpose = row['representing_purpose'] 
                representing_use = row['representing_use'] 
                land_roadsize = row['land_roadsize'] 
                land_purpose = row['land_purpose'] 
                land_totarea = row['land_totarea'] 
                land_memo = row['land_memo']  
                land_adjoiningroad = row['land_adjoiningroad'] 
                                            
                landData.append(selected_data)  # 선택한 데이터를 landData 리스트에 추가

            # print(landData)  # 생성된 landData 리스트 출력
            
                
            # 최종 결과로 landData 딕셔너리 반환
            return_data["landData"] = landData                               
        else:
            print("No matching records found.")
  
        query = 'SELECT * FROM pr_building WHERE building_code = "%s"' % building_code
        cursor.execute(query)
        b_res = cursor.fetchall()

        #건물정보
        if tr_target == '건물' or tr_target == '층호수' and b_res:
            building_name = '' if b_res[0]['building_name'] == '' else b_res[0]['building_name'] #건물명
            building_gate1 = b_res[0]['building_gate1'] #건물출입 구분: 미확인,개방,열쇠,비밀번호 등
            building_gate2 = b_res[0]['building_gate2'] #건물출입 세부정보
            building_parking = b_res[0]['building_parking'] #주차장유무
            building_pn = b_res[0]['building_pn'] #전체주차가능대수
            building_element = b_res[0]['building_element'] #건물거래메모
            building_trmemo = b_res[0]['building_trmemo'] #건물거래메모
            building_memo = b_res[0]['building_memo'] #건물메모
            building_important = b_res[0]['building_important'] #건물특징
            building_option = b_res[0]['building_option'] #건물옵션
            building_terms = b_res[0]['building_terms'] #건물특약
            building_grndflr = b_res[0]['building_grndflr'] #지상층수
            building_ugrndflr = b_res[0]['building_ugrndflr'] #지하층수
            building_usedate = str(b_res[0]['building_usedate']) #사용승인일
            building_archarea = str(b_res[0]['building_archarea']) #건축면적
            building_totarea = str(b_res[0]['building_totarea']) #연면적
            building_direction = b_res[0]['building_direction'] #건물방향
            building_bolt = b_res[0]['building_bolt'] #건물전력
            building_height = b_res[0]['building_height'] #건물높이
            building_pkcode = b_res[0]['building_pkcode'] 
            building_stract = b_res[0]['building_stract'] #주구조
            building_type = b_res[0]['building_type'] #건물타입 일반/집합
            building_purpose = b_res[0]['building_purpose'] #건물주용도
            building_hhld = b_res[0]['building_hhld'] #세대수
            building_fmly = b_res[0]['building_fmly'] #가구수
            building_elvcount = b_res[0]['building_elvcount'] #승강기수
            building_road = b_res[0]['building_road'] #도로명주소
            building_loan = b_res[0]['building_loan'] #대출(건물)
            building_loan_rate = b_res[0]['building_loan_rate'] #대출이자(건물)
            sum_deposit = b_res[0]['sum_deposit'] #총보증금
            sum_rent = b_res[0]['sum_rent'] #총월세
            sum_mmoney = b_res[0]['sum_mmoney'] #총관리비
            sum_etc = b_res[0]['sum_etc'] #기타비용
            sum_etc_content = b_res[0]['sum_etc_content'] #기타비용내역

            buildingData = {
            'building_name': building_name
            ,'building_gate1': building_gate1
            ,'building_gate2': building_gate2
            ,'building_parking': building_parking
            ,'building_pn': building_pn
            ,'building_element': building_element
            ,'building_trmemo': building_trmemo
            ,'building_memo': building_memo
            ,'building_important': building_important
            ,'building_option': building_option
            ,'building_terms': building_terms
            ,'building_grndflr': building_grndflr
            ,'building_ugrndflr': building_ugrndflr
            ,'building_usedate': building_usedate
            ,'building_archarea': building_archarea
            ,'building_totarea': building_totarea
            ,'building_direction': building_direction
            ,'building_bolt': building_bolt
            ,'building_height': building_height
            ,'building_stract': building_stract
            ,'building_type': building_type
            ,'building_purpose': building_purpose
            ,'building_hhld': building_hhld
            ,'building_fmly': building_fmly
            ,'building_elvcount': building_elvcount
            ,'building_road': building_road
            ,'building_loan': building_loan
            ,'building_loan_rate' :building_loan_rate
            ,'sum_deposit': sum_deposit
            ,'sum_rent': sum_rent
            ,'sum_mmoney': sum_mmoney
            ,'sum_etc': sum_etc
            ,'sum_etc_content': sum_etc_content
            }
            return_data["buildingData"] = buildingData

            query = 'SELECT * FROM pr_brflroulninfo WHERE sigunguCd = "%s" AND bjdongCd = "%s" AND bun = "%s" AND ji = "%s"' % (sigunguCd, bjdongCd, bun, ji)
            cursor.execute(query)
            flr_strct = []
            flr_mainpurps = []
            for flr_res in cursor.fetchall():
                # print(flr_res['mainPurpsCdNm'])
                flr_strct.append(flr_res['strctCdNm'])
                flr_mainpurps.append(flr_res['mainPurpsCdNm'])
            # # 중복 제거 및 문자열 변환
            # flr_strct = ','.join(set(flr_strct))
            # flr_mainpurps = ','.join(set(flr_mainpurps))
        
            # 한 종류의 값만 존재할 때 변수에 담기
            flr_strct = flr_strct[0] if len(set(flr_strct)) == 1 else '' 
            flr_mainpurps = flr_mainpurps[0] if len(set(flr_mainpurps)) == 1 else '' 
            #층정보
            flrData = {
            'flr_strct': flr_strct
            ,'flr_mainpurps': flr_mainpurps
            }
            return_data["flrData"] = flrData            
            # print(flr_strct,flr_mainpurps)
            # input("대기모드")

            query = 'SELECT * FROM pr_brtitleinfo WHERE sigunguCd="%s" AND bjdongCd="%s" AND bun="%s" AND ji="%s"' % (sigunguCd, bjdongCd, bun, ji)
            cursor.execute(query)
            # num_rows1 = cursor.rowcount
            # pyautogui.alert(f"num_rows1:{num_rows1}, sigunguCd:{sigunguCd}, bjdongCd:{bjdongCd}, bun:{bun}, ji:{ji}")
            brtit_res = cursor.fetchall()
            brtit_count = len(brtit_res)

            brtitData = []
            if brtit_res: 
                for res in brtit_res:
                    # print(res['mgmBldrgstPk']+" vs "+building_pkcode)
                    # print(res)
                    if res['mgmBldrgstPk'] == building_pkcode:
                        brtit_platPlc = res['platPlc']
                        brtit_bldNm = res['bldNm']
                        brtit_dongNm = res['dongNm']
                        add_dongNm = '' if brtit_dongNm=='' else (' '+brtit_dongNm)
                        brtit_bldNmdongNm = brtit_bldNm+add_dongNm
                        #표제부정보
                        brtitData = {
                        'brtit_count' : brtit_count
                        ,'brtit_platPlc': brtit_platPlc
                        ,'brtit_bldNm': brtit_bldNm
                        ,'brtit_dongNm': brtit_dongNm
                        ,'brtit_bldNmdongNm': brtit_bldNmdongNm
                        }
                        break        
                    # else:
                    #     print("해당 건물의 brtit_res 없음")
            # pyautogui.alert(brtitData)
            return_data["brtitData"] = brtitData

        print("층호수 데이터수집")
        query = 'SELECT * FROM pr_room WHERE room_code = "%s"' % room_code
        cursor.execute(query)
        r_res = cursor.fetchall()
        #호실정보
        if tr_target == '층호수' and r_res:
            room_num = r_res[0]['room_num'] #호실명
            room_floor = '' if r_res[0]['room_floor'] == '' else r_res[0]['room_floor'] #호실층수
            room_status = r_res[0]['room_status'] #호실상태
            room_gate1 = r_res[0]['room_gate1'] #내부출입 구분: 미확인,개방,열쇠,비밀번호 등
            room_gate2 = r_res[0]['room_gate2'] #내부출입 세부정보
            room_memo = r_res[0]['room_memo'] #호실메모
            room_trmemo = r_res[0]['room_trmemo'] #호실비밀메모
            room_rcount = r_res[0]['room_rcount'] #방개수
            room_bcount = r_res[0]['room_bcount'] #욕실수
            room_purpose = r_res[0]['room_purpose'] #주용도
            r_direction = r_res[0]['r_direction'] #호실방향기준
            room_direction = r_res[0]['room_direction'] #호실방향
            room_area1 = r_res[0]['room_area1'] #전용면적
            room_area2 = r_res[0]['room_area2'] #공급면적
            room_important = r_res[0]['room_important'] #호실특징
            room_option = r_res[0]['room_option'] #호실옵션
            room_terms = r_res[0]['room_terms'] #호실특약
            roomData = {
            'room_num': room_num
            ,'room_floor': room_floor
            ,'room_status': room_status
            ,'room_gate1': room_gate1
            ,'room_gate2': room_gate2
            ,'room_memo': room_memo
            ,'room_trmemo': room_trmemo
            ,'room_rcount': room_rcount
            ,'room_bcount': room_bcount
            ,'room_purpose': room_purpose
            ,'direction_stn': r_direction
            ,'room_direction': room_direction
            ,'room_area1': room_area1
            ,'room_area2': room_area2
            ,'room_important': room_important
            ,'room_option': room_option
            ,'room_terms': room_terms
            }
            return_data["roomData"] = roomData



        # print("동선확인1")          
        

        
        try:
            #의뢰인정보     
            query = 'SELECT client_name,client_nameset,client_phone1,client_gender,client_type,telecom FROM pr_client WHERE client_del="N" AND client_code = "%s"' % client_code
            cursor.execute(query)
            clientCount = cursor.rowcount
            # print("clientCount:"+str(clientCount))
            for cont_res in cursor.fetchall():
                client_name = cont_res['client_name']
                client_nameset = cont_res['client_nameset']
                client_phone1 = cont_res['client_phone1']
                client_gender = cont_res['client_gender']
                client_type = cont_res['client_type']
                telecom = cont_res['telecom']
                # client_code를 키로 사용하여 이름과 연락처를 딕셔너리에 저장
                clientData = {
                    'client_code': client_code,
                    'client_name': client_name,
                    'client_nameset': client_nameset,
                    'client_phone1': client_phone1,
                    'client_gender': client_gender,
                    'client_type': client_type,
                    'telecom': telecom
                }
            # print("동선확인22 client_code:"+client_code)  
            # print("clientData:",clientData)  
            return_data["clientData"] = clientData    
        except Exception as e:
            print("❌ DB 연결 실패3:", str(e))    
        # pyautogui.alert(clientData)
        # pyautogui.alert('main_master_name:'+main_master_name)
        # print("동선확인3")   
        
        #등기미확인시 본인 또는 대표자인 접촉자정보
        query = 'SELECT * FROM pr_contactor AS a INNER JOIN pr_client AS b ON a.client_code=b.client_code WHERE a.contactor_del="N" AND a.request_type="내놓기" AND a.request_code = "%s"' % request_code
        # query = 'SELECT * FROM pr_contactor AS a INNER JOIN pr_client AS b ON a.client_code=b.client_code WHERE a.contactor_del="N" AND a.contactor_type IN ("대표","본인") AND a.request_type="내놓기" AND a.request_code = "%s"' % request_code
        cursor.execute(query)
        contactor_data = {}  # client_code를 키로 하여 고객의 이름과 연락처를 저장할 딕셔너리
        for cont_res in cursor.fetchall():
            client_code = cont_res['client_code']
            contactor_type = cont_res['contactor_type']
            client_name = cont_res['client_name']
            client_phone1 = cont_res['client_phone1']
            client_gender = cont_res['client_gender']
            telecom = cont_res['telecom']
            # client_code를 키로 사용하여 이름과 연락처를 딕셔너리에 저장
            contactor_data[client_code] = {
                'contactor_type': contactor_type,
                'contactor_name': client_name,
                'contactor_phone1': client_phone1,
                'contactor_gender': client_gender,
                'telecom': telecom
            }
                
        contactorData = {
            'contactor_data': contactor_data
        }
        return_data["contactorData"] = contactorData 

        # print("동선확인4",contactorData)  

        do_path = land_do if land_do != '' else ''
        si_path = '\\'+land_si if land_si != '' else ''
        dong_path = '\\'+land_dong if land_dong != '' else ''
        li_path = '\\'+land_li if land_li != '' else ''
        type_path = '산' if land_type == '산' else ''
        jibun_path = '\\'+land_jibung if land_jibung != '' else ''
        folder_path = do_path + si_path + dong_path + li_path + jibun_path
        # folder_path = do_path + si_path + dong_path + li_path + type_path + jibun_path
        deunggi_path = '미설정'
        if tr_target == '토지':
            deunggi_path = folder_path+'\\토지장부'
        if tr_target == '건물' or tr_target == '층호수':
            building_name_path = '\\'+building_name if building_name != '' else ''
            folder_path += building_name_path
            if building_type != '집합':
                deunggi_path = folder_path+'\\건물장부'
            

        if tr_target == '층호수':
            if room_floor != '':
                room_floor = room_floor if int(room_floor) > 0 else '지하'+str(int(room_floor) * (-1))
                floor_path = '\\'+room_floor+'층' if room_floor != '' else ''
                num_path = '\\'+room_num+'' if room_num != '' else ''
                folder_path += floor_path + num_path
                if building_type == '집합':
                    deunggi_path = folder_path+'\\건물장부'
            else:
                folder_path += '\\층정보없음'
            #     pyautogui.alert(request_code+" 의뢰의 층 정보를 확인해주세요!!")
            #     conn.close()

        print(folder_path)

        writeData = {
        'request_code': request_code
        ,'object_code_new': object_code_new
        ,'obang_code': obang_code
        ,'land_code': land_code
        ,'building_code': building_code
        ,'room_code': room_code
        ,'request_main': request_main
        ,'master_name': master_name
        ,'master_check': master_check
        ,'object_type': object_type
        ,'object_type1': object_type1
        ,'object_type2': object_type2
        ,'tr_target': tr_target
        ,'object_ttype': object_ttype
        ,'object_title' : object_title
        ,'object_content' : object_content
        ,'address': address
        ,'tr_range': tr_range
        ,'trading': trading
        ,'deposit1': deposit1
        ,'deposit2': deposit2
        ,'deposit3': deposit3
        ,'rent1': rent1
        ,'rent2': rent2
        ,'rent3': rent3
        ,'flexible_deposit': flexible_deposit
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
        ,'request_term1' : request_term1
        ,'request_term2' : request_term2
        ,'first_trade' : first_trade
        
        }

        conn.close()
        print("데이터확인 adminData:", adminData)
        print("데이터확인 writeData:", writeData)
        print("데이터확인 folderPath:", folder_path)
        print("데이터확인 deunggi_path:", deunggi_path)
        print("데이터확인 type_path:", type_path)
        # return {"landData": landData, "buildingData": buildingData, "roomData": roomData, "writeData": writeData, 'folderPath': folder_path, 'type_path': type_path}
        return_data.update({ "adminData": adminData, "writeData": writeData, 'folderPath': folder_path, 'deunggiPath':deunggi_path, 'type_path': type_path})

        print(">>>>>adData",return_data["adData"])
        print(">>>>>writeData",writeData)
        print(">>>>>contactorData",contactorData)
        print(">>>>>clientData",clientData)
        print(">>>>>landCount",landCount)
        print(">>>>>landData",landData)
        if tr_target == '층호수' or tr_target == '건물':
            print(">>>>>buildingData",buildingData)
            print(">>>>>brtitData",brtitData)
            print(">>>>>flrData",flrData)
            print(">>>>>brData",brData)
        
        if tr_target == '층호수':print(">>>>>roomData",roomData)
        return_data["등록방식"] = '단일매물등록'

        return return_data


