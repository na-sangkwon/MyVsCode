import numpy as np
import pyautogui 

def getData(object_code_new, userid, userpw):
    print("object_code_new: "+object_code_new)
    print("userid: "+userid)
    print("userpw: "+userpw)
    return_data = {}
    import pymysql
    # pyautogui.alert("확인")
    conn = pymysql.connect(host='obangkr.cafe24.com', user='obangkr', password='Ddhqkd!1', charset='utf8')

    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute('USE obangkr;')

    try:
        conn = pymysql.connect(host='obangkr.cafe24.com', user='obangkr', password='Ddhqkd!1', charset='utf8', database='obangkr')
        print("서버와의 연결이 정상적으로 수립되었습니다.")
    except pymysql.err.OperationalError as e:
        print("서버와의 연결이 실패했습니다:", str(e))    
    # is_connected = conn.ping()
    # if is_connected:
    #     print("서버와의 연결이 정상적으로 수립되었습니다.")
    # else:
    #     print("서버와의 연결이 실패했습니다.")
    # print("object_data연결상태", conn.ping())

    query = 'SELECT * FROM pr_admin WHERE admin_del="N" AND admin_id = "%s"' % userid
    # params = (userid, userpw)
    cursor.execute(query)
    admin_res = cursor.fetchall() 
    # admin_name = admin_res[0]['admin_name'].decode('utf8')   
    print('admin_res:',admin_res)
    
    query = 'SELECT * FROM pr_object WHERE object_code_new = "%s"' % object_code_new
    cursor.execute(query)
    o_res = cursor.fetchall()
    num_rows = cursor.rowcount
    print('num_rows:',num_rows)
    if num_rows == 0:
        print(object_code_new+'는 사용되지 않는 매물번호입니다.')
        pyautogui.alert(object_code_new+'는 사용되지 않는 매물번호입니다.')
        cursor.close()
        conn.close()
        return
    else:
        for row in o_res:
            # print(row['object_address'].decode('utf8'))
            
            obang_code = row['object_code_obang'].decode('utf8')
            land_code = row['land_code'].decode('utf8')
            building_code = row['building_code'].decode('utf8')
            room_code = row['room_code'].decode('utf8')
            object_ttype = row['object_ttype'].decode('utf8') #거래종류
            object_title = row['object_title'].decode('utf8') #매물제목
            object_content = row['object_content'].decode('utf8') #매물설명
            
        # object_type = o_res['object_type'].decode('utf8')
        # land_code = o_res['land_code'].decode('utf8')
        # building_code = o_res['building_code'].decode('utf8')
        # room_code = o_res['room_code'].decode('utf8')
        # print(f"{num_rows} rows returned by the query.")

        print('land_code: '+land_code)
        print('building_code: '+building_code)
        print('room_code: '+room_code)
        
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
        
        query = 'SELECT ad_site,ad_code FROM pr_externalad WHERE object_code_new = "%s"' % object_code_new
        cursor.execute(query)
        ad_res = cursor.fetchall()
        # for ad in ad_res:
        #     if ad['ad_site'].decode('utf8') == '한방':
        #         hanbang_code = '' if ad['ad_code'].decode('utf8') is None else ad['ad_code'].decode('utf8')
        #     elif ad['ad_site'].decode('utf8') == '네이버':
        #         naver_code = '' if ad['ad_code'].decode('utf8') is None else ad['ad_code'].decode('utf8')
        # adData = {
        # 'hanbang_code': hanbang_code
        # ,'naver_code': naver_code
        # }
        # return_data["adData"] = adData   
        
        # 광고 사이트와 코드를 매핑하는 딕셔너리 초기화
        ad_codes = {'한방': '', '네이버': ''}
        for ad in ad_res:
            ad_site = ad['ad_site'].decode('utf8')
            ad_code = ad['ad_code'].decode('utf8') if ad['ad_code'] is not None else ''
            
            if ad_site in ad_codes:
                ad_codes[ad_site] = ad_code
        # return_data = {"adData": ad_codes}
        return_data["adData"] = ad_codes   
            
        # query = 'SELECT * FROM pr_request AS p LEFT JOIN pr_request_give AS c ON p.request_code = c.request_code WHERE c.land_code = "%s" AND c.building_code = "%s" AND c.room_code = "%s"' % (land_code, building_code, room_code)
        # cursor.execute(query)
        query = 'SELECT * FROM pr_request AS p LEFT JOIN pr_request_give AS c ON p.request_code = c.request_code WHERE p.request_del="N" AND c.land_code = %s AND c.building_code = %s AND c.room_code = %s'
        params = (land_code, building_code, room_code)
        cursor.execute(query, params)
        g_res = cursor.fetchall()
        # request_main = g_res[0]['request_main'].decode('utf8')
        print("g_res: ", g_res)
        num_rows1 = cursor.rowcount
        print("num_rows1: "+ str(num_rows1))
        # quit()        
        #거래정보
        request_code = g_res[0]['request_code'].decode('utf8') #의뢰번호
        # print("동선확인3")  
        master_name = g_res[0]['master_name'].decode('utf8')
        master_check = g_res[0]['master_check'].decode('utf8')
        object_type = g_res[0]['object_type'].decode('utf8') #물건종류
        # print("동선확인3")  
        object_type1 = g_res[0]['object_type1'].decode('utf8') #물건분류1
        # print("동선확인4")  
        object_type2 = g_res[0]['object_type2'].decode('utf8') #물건분류1
        # print("동선확인5")  
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
        request_term1 = g_res[0]['request_term1'].decode('utf8') #계약기간하한
        request_term2 = g_res[0]['request_term2'].decode('utf8') #계약기간상한
        client_code = g_res[0]['client_code'].decode('utf8')
        
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
                selected_fields = ['land_do', 'land_si', 'land_dong', 'land_li', 'land_type', 'land_jibun',
                                   'land_jibung','representing_jimok','representing_purpose','representing_use','land_roadsize',
                                   'land_important','land_option','land_memo','land_purpose','land_totarea']
                selected_data = {field: row[field].decode('utf8') for field in selected_fields}
                land_address = row['land_address']
                address = land_address
                pnu = row['pnu'].decode('utf8')
                sigunguCd = pnu[:5]
                bjdongCd = pnu[5:10]
                bun = pnu[-8:-4]
                ji = pnu[-4:]                
                land_do = row['land_do'].decode('utf8') #시도
                land_si = row['land_si'].decode('utf8') #시군구
                land_dong = row['land_dong'].decode('utf8') #읍면동
                land_li = row['land_li'].decode('utf8') #리
                land_type = '산' if row['land_type'].decode('utf8') == '2' else '일반' #대장구분 일반:1 산:2
                land_jibun = row['land_jibun'].decode('utf8') #지번(숫자)  
                land_jibung = row['land_jibung'].decode('utf8') #지번(숫자)  
                representing_jimok = row['representing_jimok'].decode('utf8') 
                representing_purpose = row['representing_purpose'].decode('utf8') 
                representing_use = row['representing_use'].decode('utf8') 
                land_roadsize = row['land_roadsize'].decode('utf8') 
                land_purpose = row['land_purpose'].decode('utf8') 
                land_totarea = row['land_totarea'].decode('utf8') 
                land_memo = row['land_memo'].decode('utf8') 
                                            
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
            building_name = '' if b_res[0]['building_name'].decode('utf8') == '' else b_res[0]['building_name'].decode('utf8') #건물명
            building_gate1 = b_res[0]['building_gate1'].decode('utf8') #건물출입 구분: 미확인,개방,열쇠,비밀번호 등
            building_gate2 = b_res[0]['building_gate2'].decode('utf8') #건물출입 세부정보
            building_parking = b_res[0]['building_parking'].decode('utf8') #주차장유무
            building_pn = b_res[0]['building_pn'].decode('utf8') #전체주차가능대수
            building_trmemo = b_res[0]['building_trmemo'].decode('utf8') #건물거래메모
            building_memo = b_res[0]['building_memo'].decode('utf8') #건물메모
            building_important = b_res[0]['building_important'].decode('utf8') #건물특징
            building_option = b_res[0]['building_option'].decode('utf8') #건물옵션
            building_grndflr = b_res[0]['building_grndflr'] #지상층수
            building_ugrndflr = b_res[0]['building_ugrndflr'] #지하층수
            building_usedate = str(b_res[0]['building_usedate']) #사용승인일
            building_archarea = str(b_res[0]['building_archarea'].decode('utf8')) #건축면적
            building_totarea = str(b_res[0]['building_totarea'].decode('utf8')) #연면적
            building_direction = b_res[0]['building_direction'].decode('utf8') #건물방향
            building_pkcode = b_res[0]['building_pkcode'].decode('utf8') 
            building_type = b_res[0]['building_type'].decode('utf8') #건물타입 일반/집합
            building_purpose = b_res[0]['building_purpose'].decode('utf8') #건물주용도
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
            ,'building_trmemo': building_trmemo
            ,'building_memo': building_memo
            ,'building_important': building_important
            ,'building_option': building_option
            ,'building_grndflr': building_grndflr
            ,'building_ugrndflr': building_ugrndflr
            ,'building_usedate': building_usedate
            ,'building_archarea': building_archarea
            ,'building_totarea': building_totarea
            ,'building_direction': building_direction
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
                # print(flr_res['mainPurpsCdNm'].decode('utf8'))
                flr_strct.append(flr_res['strctCdNm'].decode('utf8'))
                flr_mainpurps.append(flr_res['mainPurpsCdNm'].decode('utf8'))
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

            query = 'SELECT * FROM pr_brtitleinfo WHERE sigunguCd="%s" AND bjdongCd="%s" AND bun="%s" AND ji="%s" AND mgmBldrgstPk="%s"' % (sigunguCd, bjdongCd, bun, ji, building_pkcode)
            cursor.execute(query)
            # num_rows1 = cursor.rowcount
            # pyautogui.alert(f"num_rows1:{num_rows1}, sigunguCd:{sigunguCd}, bjdongCd:{bjdongCd}, bun:{bun}, ji:{ji}")
            brtit_res = cursor.fetchall()
            brtitData = []
            if brtit_res: 
                print(brtit_res)
                brtit_bldNm = brtit_res[0]['bldNm'].decode('utf8')
                brtit_dongNm = brtit_res[0]['dongNm'].decode('utf8')
                add_dongNm = '' if brtit_dongNm=='' else (' '+brtit_dongNm)
                brtit_bldNmdongNm = brtit_bldNm+add_dongNm
                #표제부정보
                brtitData = {
                'brtit_bldNm': brtit_bldNm
                ,'brtit_dongNm': brtit_dongNm
                ,'brtit_bldNmdongNm': brtit_bldNmdongNm
                }            
            else:
                print("brtit_res 없음")
            # pyautogui.alert(brtit_res)
            return_data["brtitData"] = brtitData


        query = 'SELECT * FROM pr_room WHERE room_code = "%s"' % room_code
        cursor.execute(query)
        r_res = cursor.fetchall()
        #호실정보
        if tr_target == '층호수' and r_res:
            room_num = r_res[0]['room_num'].decode('utf8') #호실명
            room_floor = '' if r_res[0]['room_floor'].decode('utf8') == '' else r_res[0]['room_floor'].decode('utf8') #호실층수
            room_status = r_res[0]['room_status'].decode('utf8') #호실상태
            room_gate1 = r_res[0]['room_gate1'].decode('utf8') #내부출입 구분: 미확인,개방,열쇠,비밀번호 등
            room_gate2 = r_res[0]['room_gate2'].decode('utf8') #내부출입 세부정보
            room_memo = r_res[0]['room_memo'].decode('utf8') #호실메모
            room_rcount = r_res[0]['room_rcount'].decode('utf8') #방개수
            room_bcount = r_res[0]['room_bcount'].decode('utf8') #욕실수
            r_direction = r_res[0]['r_direction'].decode('utf8') #호실방향기준
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
            ,'direction_stn': r_direction
            ,'room_direction': room_direction
            ,'room_area1': room_area1
            ,'room_area2': room_area2
            ,'room_important': room_important
            ,'room_option': room_option
            }
            return_data["roomData"] = roomData



        # print("동선확인1")          
        # 사용자정보
        admin_name = admin_res[0]['admin_name'].decode('utf8')
        ad_id = admin_res[0]['admin_id'].decode('utf8')
        # admin_email = admin_res[0]['admin_email'].decode('utf8')
        # admin_pw = admin_res[0]['admin_pw'].decode('utf8')
        ad_email = admin_res[0]['ad_email'].decode('utf8')
        ad_pw = admin_res[0]['ad_pw'].decode('utf8')
        zigbang_tag = admin_res[0]['zigbang_tag'].decode('utf8')
        obang_id = admin_res[0]['obang_id'].decode('utf8')
        obang_pw = admin_res[0]['obang_pw'].decode('utf8')
        zigbang_id = admin_res[0]['zigbang_id'].decode('utf8')
        zigbang_pw = admin_res[0]['zigbang_pw'].decode('utf8')
        obs_id = admin_res[0]['obs_id'].decode('utf8')
        obs_pw = admin_res[0]['obs_pw'].decode('utf8')
        naver_id = admin_res[0]['naver_id'].decode('utf8')
        naver_pw = admin_res[0]['naver_pw'].decode('utf8')
        hanbang_id = admin_res[0]['hanbang_id'].decode('utf8')
        hanbang_pw = admin_res[0]['hanbang_pw'].decode('utf8')
        adminData = {
            'admin_name': admin_name,
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
            'hanbang_pw': hanbang_pw
        }

        # print("동선확인22")  
        
        #의뢰인정보
        query = 'SELECT client_name,client_nameset,client_phone1,client_gender,telecom FROM pr_client WHERE client_del="N" AND client_code = "%s"' % client_code
        cursor.execute(query)
        for cont_res in cursor.fetchall():
            client_name = cont_res['client_name'].decode('utf8')
            client_nameset = cont_res['client_nameset'].decode('utf8')
            client_phone1 = cont_res['client_phone1'].decode('utf8')
            client_gender = cont_res['client_gender'].decode('utf8')
            telecom = cont_res['telecom'].decode('utf8')
            # client_code를 키로 사용하여 이름과 연락처를 딕셔너리에 저장
            clientData = {
                'client_name': client_name,
                'client_nameset': client_nameset,
                'client_phone1': client_phone1,
                'client_gender': client_gender,
                'telecom': telecom
            }
        return_data["clientData"] = clientData        
        # pyautogui.alert('master_names', master_names)
        # pyautogui.alert('main_master_name:'+main_master_name)

        
        #본인 또는 대표자 정보
        query = 'SELECT * FROM pr_contactor AS a INNER JOIN pr_client AS b ON a.client_code=b.client_code WHERE a.contactor_del="N" AND a.contactor_type IN ("대표","본인") AND a.request_type="내놓기" AND a.request_code = "%s"' % request_code
        cursor.execute(query)
        contactor_data = {}  # client_code를 키로 하여 고객의 이름과 연락처를 저장할 딕셔너리
        for cont_res in cursor.fetchall():
            client_code = cont_res['client_code']
            contactor_type = cont_res['contactor_type'].decode('utf8')
            client_name = cont_res['client_name'].decode('utf8')
            client_phone1 = cont_res['client_phone1'].decode('utf8')
            # client_code를 키로 사용하여 이름과 연락처를 딕셔너리에 저장
            contactor_data[client_code] = {
                'contactor_type': contactor_type,
                'contactor_name': client_name,
                'contactor_phone1': client_phone1
            }
                
        contactorData = {
            'contactor_data': contactor_data
        }
        return_data["contactorData"] = contactorData 

        # print("동선확인4")  

        do_path = land_do if land_do != '' else ''
        si_path = '\\'+land_si if land_si != '' else ''
        dong_path = '\\'+land_dong if land_dong != '' else ''
        li_path = '\\'+land_li if land_li != '' else ''
        type_path = '산' if land_type == '산' else ''
        jibun_path = '\\'+land_jibung if land_jibung != '' else ''
        folder_path = do_path + si_path + dong_path + li_path + type_path + jibun_path
        if tr_target == '건물' or tr_target == '층호수':
            building_name_path = '\\'+building_name if building_name != '' else ''
            folder_path += building_name_path
        if tr_target == '층호수':
            if room_floor != '':
                room_floor = room_floor if int(room_floor) > 0 else '지하'+str(int(room_floor) * (-1))
                floor_path = '\\'+room_floor+'층' if room_floor != '' else ''
                num_path = '\\'+room_num+'' if room_num != '' else ''
                folder_path += floor_path + num_path
            else:
                folder_path += '\\층정보없음'
            #     pyautogui.alert(request_code+" 의뢰의 층 정보를 확인해주세요!!")
            #     conn.close()

        print (folder_path)

        writeData = {
        'request_code': request_code
        ,'object_code_new': object_code_new
        ,'obang_code': obang_code
        ,'land_code': land_code
        ,'building_code': building_code
        ,'room_code': room_code
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
        }

        conn.close()
        # return {"landData": landData, "buildingData": buildingData, "roomData": roomData, "writeData": writeData, 'folderPath': folder_path, 'type_path': type_path}
        return_data.update({"adminData": adminData, "writeData": writeData, 'folderPath': folder_path, 'type_path': type_path})
  
        print(">>>>>adminData",adminData)
        print(">>>>>adData",return_data['adData'])
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

        return return_data


