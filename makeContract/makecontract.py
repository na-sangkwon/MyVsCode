import pyautogui
import pyperclip
import object_data
import pymysql
import traceback
import time
import tkinter as tk
from tkinter import simpledialog

# pyautogui.mouseInfo()
# exit()

# 현재 화면 해상도 가져오기
현재화면폭, 현재화면높이 = pyautogui.size()

# 원래 스크립트가 최적화된 해상도
표준폭 = 1920  # 예: 1920
표준높이 = 1080  # 예: 1080

pyautogui.FAILSAFE = True  # 기본값 True, 마우스가 (0, 0)으로 이동하면 종료


def 동적좌표변환(표준X좌표, 표준Y좌표):
    """
    원래 스크립트의 좌표를 현재 모니터 해상도에 맞게 조정합니다.
    """
    변환X좌표 = (표준X좌표 / 표준폭) * 현재화면폭
    변환Y좌표 = (표준Y좌표 / 표준높이) * 현재화면높이
    return int(변환X좌표), int(변환Y좌표)

# 좌표 변수 정의
계약관리_좌표 = (212, 69)
조회조건_좌표 = (523,152)
조회조건_소재지_좌표 = (526,185)
조회조건_입력_좌표 = (667,152)
계약서작성_좌표 = (50, 253)
계약서종류_드롭다운_좌표 = (923, 128)
부동산_선택_좌표 = (849, 475)
중앙표시알림_확인_좌표 = (961, 568)
거래종류_드롭다운_좌표 = (963, 128)
월세_선택_좌표 = (964, 183)
확인_버튼_좌표 = (1028, 129)
소재지_버튼_좌표 = (1193, 329)
호수_좌표 = (1323,330)
토지면적_좌표 = (856,357)
구조_좌표 = (743,389)
용도_좌표 = (982,388)
건물면적_좌표 = (1298,389)
임대할부분_좌표 = (1153,417)
임대할면적_좌표 = (1300,417)
보증금_좌표 = (809,496)
계약금_좌표 = (813,524)
잔금일_좌표 = (1043,607)
차임_좌표 = (775,635)
차임지급일_좌표 = (1011,635)
선불후불_좌표 = (1085,635)
후불_좌표 = (1092,692)
부가세별도_좌표 = (1327,636)

특약사항_좌표 = (1000,636)

기준Y = 532 #임대인주소의 y좌표값
임대인주소_좌표 = (1017,443) #1017,532
임대인앞주민번호_좌표 = (823,기준Y+31)
임대인뒤주민번호_좌표 = (925,기준Y+31)
임대인연락처_좌표 = (1054,기준Y+31)
임대인성명_좌표 = (1270,기준Y+31)

임차인주소_좌표 = (1017,기준Y+154)
임차인앞주민번호_좌표 = (823,기준Y+183)
임차인뒤주민번호_좌표 = (925,기준Y+183)
임차인연락처_좌표 = (1054,기준Y+183)
임차인성명_좌표 = (1270,기준Y+183)
계약서저장_좌표 = (1248,197)



확인설명서_좌표 = (1277,87)
주거용_좌표 = (1063,272)
비주거용_좌표 = (1158,271)
토지용_좌표 = (1256,276)
확인설명서확인_좌표 = (1151,379)

업무용_좌표 = (743,160)
상업용_좌표 = (835,160)
공업용_좌표 = (922,159)
매매교환_좌표 = (1031,160)
임대_좌표 = (1128,161)

등기권리증_좌표 = (817,250)
등기사항증명서_좌표 = (934,251)
토지대장_좌표 = (1088,251)
건축물대장_좌표 = (1192,250)
지적도_좌표 = (1292,250)
임야도_좌표 = (805,273)
토지이용계획_좌표 = (953,272)
그밖의자료_좌표 = (1100,272)
그밖의자료입력_좌표 = (1370,269)

실제이용상태_좌표 = (1379,579)
대지지분_좌표 = (1377,608)
준공년도_좌표 = (910,652)
실제용도_좌표 = (1379,666)
방향선택_좌표 = (1214,651)
방향입력_좌표 = (1370,649)
내진설계적용여부입력_좌표 = (950,678)
내진능력입력_좌표 = (1301,678)
위반_좌표 = (883,765)
적법_좌표 = (947,763)
계약서내용으로가져오기_좌표 = (645,802)
계약갱신요구권행사여부미확인_좌표 = (914,594) #스크롤 최대한 내린후 좌표
적용확인_좌표 = (920,577)

확인설명서2쪽_좌표 = (766,91)
도로와의관계2_좌표 = (850,320)
주차장없음_좌표 = (765,280)
전용주차시설_좌표 = (855,279)
경비실없음_좌표 = (850,320)
자체관리_좌표 = (1222,319)
실제권리관계입력_좌표 = (1222,319)
소화전없음_좌표 = (935,709)
비상벨없음_좌표 = (935,736)
승강기없음_좌표 = (1063,845)
그밖의시설물_좌표 = (1093,903)
바닥면보통임_좌표 = (936,998)

확인설명서3쪽_좌표 = (907,90)
실비입력_좌표 = (1183,385)
지급시기_좌표 = (831,449)
저장_좌표 = (1366,54)
# _좌표 = ()
# _좌표 = ()

def 이동_후_클릭(좌표, wait=0):
    print(f"이동_후_클릭(좌표={좌표}, wait={wait})")
    # dynamic_x, dynamic_y = 동적좌표변환(좌표[0], 좌표[1])
    # pyautogui.moveTo(dynamic_x, dynamic_y, duration=wait)
    pyautogui.moveTo(좌표[0], 좌표[1], duration=wait)
    # pyautogui.alert("여기 맞니?")
    # pyautogui.click()

def 순서대로_좌표_클릭(좌표리스트, wait_between=0.5):
    """
    좌표 리스트를 순서대로 클릭합니다.
    :param 좌표리스트: [(x1, y1), (x2, y2), ...] 형태의 좌표 리스트
    :param wait_between: 각 클릭 사이의 대기 시간 (초)
    """
    for index, 좌표 in enumerate(좌표리스트, start=1):
        print(f"{index}번째 좌표로 이동 후 클릭 중: {좌표}")
        이동_후_클릭(좌표, 0.5)
        pyautogui.alert(f"{index}번째 좌표로 이동 후 클릭 중: {좌표}")
        time.sleep(wait_between)

# 좌표 리스트 정의

계약서작업목록 = [
    확인설명서_좌표,         # 확인설명서 좌표
    주거용_좌표,             # 주거용 좌표
    비주거용_좌표,           # 비주거용 좌표
    토지용_좌표,             # 토지용 좌표
    확인설명서확인_좌표,     # 확인 설명서 확인 좌표
]

주거용실행목록 = [

]

비주거용실행목록 = [

]

토지용실행목록 = [
    
]

# 동적 액션 수행 함수
def 수행(명령):
    """
    명령에 따라 좌표를 클릭하거나 값을 입력합니다.
    :param 명령: {"명칭": "지적도", "액션": "입력", "값": "테스트 데이터", "이동시간": 0.5} 형태
    """
    명칭 = 명령["명칭"]
    액션 = 명령["액션"]
    값 = 명령.get("값")
    이동시간 = 명령.get("이동시간", 0.5)  # 이동시간 기본값 0.5초

    # 좌표 동적 확인
    좌표명 = 명칭 + "_좌표"
    if 좌표명 not in globals():
        raise ValueError(f"{좌표명}이(가) 정의되지 않았습니다.")
    
    좌표 = globals()[좌표명]  # 좌표 가져오기
    print(f"{명칭}({좌표})에서 {액션} 실행 중...{값}")

    #특정 명칭에서 스크롤 사용
    if 명칭 in ['계약갱신요구권행사여부미확인']:
        스크롤다운(-1600)

    pyautogui.moveTo(좌표[0], 좌표[1], duration=이동시간)
    pyautogui.click()
    # 액션 처리
    if 액션 == "붙여넣기" and 값 is not None:
        pyperclip.copy(값)
        pyautogui.hotkey('ctrl', 'a')  # 전체선택
        pyautogui.hotkey('ctrl', 'v')  # 클립보드 내용 붙여넣기
    elif 액션 == "입력":
        # pyautogui.moveTo(좌표[0], 좌표[1], duration=이동시간)
        # pyautogui.alert(f"{명칭}({좌표})에서 {액션} 실행 중...{값}")
        # pyautogui.click()
        pyautogui.typewrite(값, interval=0.2) #한글 입력안됨
    elif 액션 == "선택":
        print("only 클릭!")
        # pyautogui.moveTo(좌표[0], 좌표[1], duration=이동시간)
        # pyautogui.click()
    else:
        raise ValueError(f"알 수 없는 액션: {액션}")
    if 명칭 == '그밖의시설물':
        pyautogui.alert(f"{명칭}({좌표})에서 {액션} 실행 중...{값}")

    
# 실행 목록 처리 함수
def 실행목록_처리(작업목록, 실행목록):
    """
    실행 목록을 기반으로 작업 목록에서 해당 작업을 찾아 실행합니다.
    :param 작업목록: 전체 작업 정의 리스트
    :param 실행목록: 실행할 작업 명칭 리스트
    """
    for 실행명칭 in 실행목록:
        # 작업목록에서 실행명칭을 가진 작업 찾기
        작업 = next((작업 for 작업 in 작업목록 if 작업["명칭"] == 실행명칭), None)
        if 작업:
            수행(작업)  # 작업 수행
        else:
            print(f"[실행 스킵] 작업목록에 '{실행명칭}'이(가) 없습니다.")

def 실행목록의특정명령뒤추가(실행목록, 추가명령, 기준명령=None):
    """
    실행 목록에서 기준 명령 뒤에 새로운 명령을 추가하거나,
    기준 명령이 없으면 목록의 마지막에 추가합니다.
    
    :param 실행목록: 기존 실행 목록 (리스트)
    :param 추가명령: 추가할 명령 (문자열)
    :param 기준명령: 실행 목록에서 기준이 되는 명령 (문자열, 기본값 None)
    :return: 수정된 실행 목록
    """
    if 기준명령 is None:
        # 기준 명령이 없으면 목록의 마지막에 추가
        실행목록.append(추가명령)
        print(f"기준 명령이 없어서 '{추가명령}'을 목록의 마지막에 추가.")
    else:
        try:
            # 기준 명령의 인덱스를 찾고 뒤에 추가
            index = 실행목록.index(기준명령) + 1
            실행목록.insert(index, 추가명령)
            print(f"기준 명령 '{기준명령}' 뒤에 '{추가명령}' 추가.")
        except ValueError:
            # 기준 명령이 목록에 없는 경우, 목록의 앞에 추가
            실행목록.insert(0, 추가명령)
            print(f"기준 명령 '{기준명령}'이 실행 목록에 없어서 '{추가명령}'을 목록의 앞에 추가.")
    return 실행목록


# pyautogui.alert("테스트준비")
# # 순서대로_좌표_클릭(좌표리스트, wait_between=1)  # 순서대로 좌표 클릭 실행
# pyautogui.alert("테스트완료")



def 스크롤다운(scroll_val):
    pyautogui.moveTo(1411,546)
    # pyautogui.click()            
    pyautogui.scroll(scroll_val)
    # pyautogui.alert("스크롤값 확인:",str(scroll_val))

def 이동_후_텍스트_붙여넣기(좌표, 텍스트, wait=0):
    print(f"이동_후_텍스트_붙여넣기(좌표={좌표}, 텍스트={텍스트}, wait={wait})")
    dynamic_x, dynamic_y = 동적좌표변환(좌표[0], 좌표[1])
    pyperclip.copy(텍스트)
    pyautogui.moveTo(dynamic_x, dynamic_y, duration=wait)
    pyautogui.click()
    pyautogui.hotkey('ctrl', 'a')  # 전체선택
    pyautogui.hotkey('ctrl', 'v')  # 클립보드 내용 붙여넣기

def 이동_후_텍스트_입력(좌표, 텍스트, wait=0): 
    print(f"이동_후_텍스트_입력(좌표={좌표}, 텍스트={텍스트}, wait={wait})")
    dynamic_x, dynamic_y = 동적좌표변환(좌표[0], 좌표[1])
    pyautogui.moveTo(dynamic_x, dynamic_y, duration=wait)
    pyautogui.click()
    pyautogui.typewrite(텍스트, interval=wait) #한글 입력안됨

# 데이터베이스 연결 및 기타 초기 설정
def 데이터베이스_연결_초기화():
    return pymysql.connect(host='obangkr.cafe24.com', user='obangkr', password='Ddhqkd!1', charset='utf8')

def 계약자_데이터_가져오기(cursor, contract_code):
    query = f'SELECT * FROM pr_contractor WHERE contractor_del="N" AND contract_code="{contract_code}"'
    # query += ' ORDER BY object_udate DESC, object_utime DESC'
    # query += ' LIMIT 1000'
    cursor.execute(query)
    return cursor.fetchall()

def 내놓기의뢰_데이터_가져오기(cursor, give_code):
    query = f'SELECT * FROM pr_request AS p'
    query += f' LEFT JOIN pr_request_give AS c ON p.request_code=c.request_code'
    query += f' WHERE p.request_del="N" AND c.give_del="N" AND p.request_code="{give_code}"'
    cursor.execute(query)
    return cursor.fetchall()

def 물건_데이터_가져오기(cursor, type, code):
    query = f'SELECT * FROM pr_{type} WHERE {type}_del="N" AND {type}_code="{code}"'
    # query += ' ORDER BY object_udate DESC, object_utime DESC'
    # query += ' LIMIT 1000'
    cursor.execute(query)
    return cursor.fetchall()

def 계약_데이터_가져오기(cursor, contract_code):
    query = f'SELECT * FROM pr_contract WHERE contract_del="N" AND contract_code="{contract_code}"'
    # query += ' ORDER BY object_udate DESC, object_utime DESC'
    # query += ' LIMIT 1000'
    cursor.execute(query)
    return cursor.fetchall()

# 가져온 데이터를 처리하는 함수
def 데이터_처리(cursor, row):
    try:
        contract_code = row['contract_code']
        give_code = row['give_code']
        print("contract_code:", contract_code)
        contract_type = row['contract_type']
        보증금 = row['contract_deposit']
        계약금 = row['contract_money']
        잔금일 = row['balance_date']   
        if 잔금일 != '0000-00-00':
            잔금일 = 잔금일.replace('-', '')         
        차임 = row['contract_rent']
        차임지급일 = row['movein_date']
        선불후불 = row['rent_preafter']
        부가세별도 = row['contract_surtax']
        print("잔금일:",잔금일)
        print("차임:",차임)
        print("차임지급일:",차임지급일)
        print("선불후불:",선불후불)

        pay_type = row['pay_type']
        pay_target = row['pay_target']
        contract_mtype = row['contract_mtype']
        contract_mmoney = row['contract_mmoney']
        contract_mcontent = row['contract_mcontent']
        contract_term = row['contract_term']
        
        # 데이터베이스에서 계약자 데이터를 가져옵니다.
        계약자데이터 = 계약자_데이터_가져오기(cursor, contract_code)
        print("계약자데이터:", 계약자데이터)
        for contractor_data in 계약자데이터:
            request_type = contractor_data['request_type']
            print("request_type:",request_type)
            if request_type=='내놓기':
                임대인주소 = contractor_data['contractor_reg_addr']
                임대인주민번호 = contractor_data['contractor_reg_num']
                임대인앞주민번호 = 임대인주민번호[:6] # 앞 6자리
                임대인뒤주민번호 = 임대인주민번호[-7:] # 뒤에서 7자리
                임대인연락처 = contractor_data['contractor_phone1']
                임대인성명 = contractor_data['contractor_name']
                print("임대인주소:",임대인주소)
                print("임대인주민번호:",임대인주민번호)
                print("임대인연락처:",임대인연락처)
                print("임대인성명:",임대인성명)
            elif request_type=='구하기':
                임차인주소 = contractor_data['contractor_reg_addr']
                임차인주민번호 = contractor_data['contractor_reg_num']
                임차인앞주민번호 = 임차인주민번호[:6] # 앞 6자리
                임차인뒤주민번호 = 임차인주민번호[-7:] # 뒤에서 7자리
                임차인연락처 = contractor_data['contractor_phone1']
                임차인성명 = contractor_data['contractor_name'] 
                print("임차인주소:",임차인주소)
                print("임차인주민번호:",임차인주민번호)
                print("임차인연락처:",임차인연락처)
                print("임차인성명:",임차인성명)
        
        # 데이터베이스에서 내놓기의뢰 데이터를 가져옵니다.
        내놓기의뢰데이터 = 내놓기의뢰_데이터_가져오기(cursor, give_code)
        print("내놓기의뢰데이터:", 내놓기의뢰데이터)
        for give_data in 내놓기의뢰데이터:
            land_code = give_data['land_code']
            building_code = give_data['building_code']
            room_code = give_data['room_code']
            object_type = give_data['object_type']
            object_type1 = give_data['object_type1']
            object_type2 = give_data['object_type2']
            print("land_code:",land_code)
            print("building_code:",building_code)
            print("room_code:",room_code)
            print("object_type:",object_type)
        
        실제이용상태 = ''
        실제용도 = ''
        실제권리관계입력 = '해당없음'
        # 데이터베이스에서 물건 데이터를 가져옵니다.
        토지데이터 = 물건_데이터_가져오기(cursor, 'land', land_code)
        print("토지데이터:", 토지데이터)
        for land_data in 토지데이터:
            land_main = land_data['land_main']
            land_jibung = land_data['land_jibung']
            토지면적 = land_data['land_totarea']
            land_dong = land_data['land_dong']
            land_li = land_data['land_li']
            land_jibung = land_data['land_jibung']
            동리번지수 = (land_dong+' '+land_jibung) if land_li == '' else (land_li+' '+land_jibung)
            실제이용상태 = land_data['representing_jimok']
            
        건물데이터 = 물건_데이터_가져오기(cursor, 'building', building_code)
        print("건물데이터:", 건물데이터)
        for building_data in 건물데이터:
            # building_main = building_data['building_main']
            building_name = building_data['building_name']
            구조 = building_data['building_stract']
            용도 = building_data['building_purpose']
            건물면적 = building_data['building_archarea']
            건물명까지주소 = land_main+' '+land_jibung+((' '+building_name) if building_name!='' and '무명건물' not in building_name else '')
            준공년도 = building_data['building_usedate']
            실제이용상태 = land_data['representing_jimok']
            
        호실데이터 = 물건_데이터_가져오기(cursor, 'room', room_code)
        print("호실데이터:", 호실데이터)
        for room_data in 호실데이터:
            # room_main = room_data['room_main']
            # room_jibung = room_data['room_jibung']
            # 호수 = room_data['room_num']
            임대할부분 = room_data['room_num']
            전용면적 = room_data['room_area1'] 
            room_option = room_data['room_option'] 

        #변동좌표
        # #계약서종류
        # object_type2 = '부동산'
        # if object_type2 in ['아파트']: #10 원룸
        #     부동산_선택_좌표 = (849, 150)
        # elif object_type2 in ['다세대']: #4
        #     부동산_선택_좌표 = (849, 200)
        #     토지면적_좌표 = (882,357)
        # elif object_type2 in ['다가구']: #5
        #     부동산_선택_좌표 = (849, 217)
        # elif object_type2 in ['일반원룸']: #10 원룸
        #     부동산_선택_좌표 = (849, 302)
        #     토지면적_좌표 = (1270,357)
        # elif object_type2 in ['상가점포']: #11 상가
        #     부동산_선택_좌표 = (849, 319)
        #     토지면적_좌표 = (882,357)
        # elif object_type2 in ['부동산']: #19 부동산
        #     부동산_선택_좌표 = (849, 456) 


        
        특약사항 = '- 현시설물 상태에서의 계약이며 퇴거시 원상복구하기로 한다.'
        # 특약사항 += '\n'+''
        특약사항 += '\n'+'- 옵션 : ' + room_option
        if contract_mtype == '없음':
            특약사항 += '\n'+f'- 관리비 없음. (개별 전기/수도/가스 요금별도)'
        else:
            if contract_mmoney != '' and contract_mmoney != '0':
                특약사항 += '\n'+f'- 관리비 {contract_mmoney}만원 {contract_mtype}.'
            if contract_mcontent != '': 
                특약사항 += f'(포함내역: {contract_mcontent})'
        
        if int(contract_term) < 12: 
            특약사항 += '\n'+'- 만기퇴실 희망시에는 만기 1주전에 임대인 혹은 관리인에게 통보하기로 한다.(미통보시 자동연장계약됨.)'
        else:
            특약사항 += '\n'+'- 만기퇴실 희망시에는 만기 1개월전에 임대인 혹은 관리인에게 통보하기로 한다.(미통보시 자동연장계약됨.)'
            특약사항 += '\n'+'- 임차인은 확정일자부여기관에 임대차정보제공을 요청할 수 있고 임대인이 납부하지 아니한 국세 및 지방세의 열람을 신청할 수 있음을 고지함.'
            특약사항 += '\n'+'- 임대인/임차인은 계약체결일로부터 30일이내 오산시청에 신고를 하기로 한다.(보증금6천만원 또는 월세30만원 초과시)'
        
        if object_type=='주거용':
            특약사항 += '\n'+'- 임차인은 퇴실시 청소비 5만원(상태에따라 증액될수있음),정화조비 월1천원씩 공제한다.'
            특약사항 += '\n'+'- 애완동물사육금지(위반시 강제퇴실조치하며 남은 기간의 월차임,중개수수료,부대비용등도 임차인이 부담하기로 한다.)'
            특약사항 += '\n'+'- 쓰레기 배출시 철저히 분리 배출하여야 하고 음식물 및 폐기쓰레기는 반드시 종량제봉투를 사용하여야 한다.'
            특약사항 += '\n'+'- 기타 그밖에 정하여지지 않은 사항은 주택임대차보호법 및 관례에 따른다.'
        elif object_type == '상업용':
            특약사항 += '\n'+'- 현 사용공간의 계약으로 공부상면적과 실측면적의 차이가 발생하더라도 본 계약관련 당사자 모두에게 이의를 제기 하지 않는다.'
            특약사항 += '\n'+'- 퇴거시 영업권 및 사업자등록 말소 확인후 보증금을 반환해주기로 한다.'
            특약사항 += '\n'+'- 기타 그밖에 정하여지지 않은 사항은 상가임대차보호법 및 관례에 따른다.'
        if pay_type == '이체':
            특약사항 += '\n'+'- 월세및 관리비 입금계좌 : ' + pay_target
        
        기본이동시간 = 0.3
        계약서작업목록 = [
            {"명칭": "계약관리", "액션": "선택", "값": None, "이동시간": 기본이동시간},
            {"명칭": "조회조건", "액션": "선택", "값": None, "이동시간": 기본이동시간},
            {"명칭": "조회조건_소재지", "액션": "선택", "값": None, "이동시간": 기본이동시간},
            {"명칭": "조회조건_입력", "액션": "붙여넣기", "값": 동리번지수, "이동시간": 기본이동시간},

            {"명칭": "계약서작성", "액션": "선택", "값": None, "이동시간": 기본이동시간},
            {"명칭": "계약서종류_드롭다운", "액션": "선택", None: "부동산", "이동시간": 2},
            {"명칭": "부동산_선택", "액션": "선택", "값": None, "이동시간": 0.3},
            {"명칭": "중앙표시알림_확인", "액션": "선택", "값": None, "이동시간": 0.3},
            {"명칭": "거래종류_드롭다운", "액션": "선택", "값": None, "이동시간": 기본이동시간},
            {"명칭": "월세_선택", "액션": "선택", "값": None, "이동시간": 0.3},
            {"명칭": "확인_버튼", "액션": "선택", "값": None, "이동시간": 기본이동시간},
            {"명칭": "소재지_버튼", "액션": "붙여넣기", "값": 건물명까지주소, "이동시간": 1.5},

            {"명칭": "토지면적", "액션": "붙여넣기", "값": 토지면적, "이동시간": 기본이동시간},
            {"명칭": "구조", "액션": "붙여넣기", "값": 구조, "이동시간": 기본이동시간},
            {"명칭": "용도", "액션": "붙여넣기", "값": 용도, "이동시간": 기본이동시간},
            {"명칭": "건물면적", "액션": "붙여넣기", "값": 건물면적, "이동시간": 기본이동시간},
            {"명칭": "임대할부분", "액션": "붙여넣기", "값": 임대할부분, "이동시간": 기본이동시간},
            {"명칭": "임대할면적", "액션": "붙여넣기", "값": 전용면적, "이동시간": 기본이동시간},
            {"명칭": "보증금", "액션": "붙여넣기", "값": 보증금, "이동시간": 기본이동시간},
            {"명칭": "계약금", "액션": "붙여넣기", "값": 계약금, "이동시간": 기본이동시간},
            {"명칭": "잔금일", "액션": "입력", "값": 잔금일, "이동시간": 기본이동시간},
            {"명칭": "차임", "액션": "붙여넣기", "값": 차임, "이동시간": 기본이동시간},
            {"명칭": "선불후불", "액션": "선택", "값": None, "이동시간": 0.2},
            {"명칭": "후불", "액션": "선택", "값": None, "이동시간": 0.2},
            {"명칭": "부가세별도", "액션": "선택", "값": None, "이동시간": 기본이동시간},

            {"명칭": "특약사항", "액션": "붙여넣기", "값": 특약사항, "이동시간": 기본이동시간},

            {"명칭": "임대인주소", "액션": "붙여넣기", "값": 임대인주소, "이동시간": 기본이동시간},
            {"명칭": "임대인앞주민번호", "액션": "붙여넣기", "값": 임대인앞주민번호, "이동시간": 기본이동시간},
            {"명칭": "임대인뒤주민번호", "액션": "붙여넣기", "값": 임대인뒤주민번호, "이동시간": 기본이동시간},
            {"명칭": "임대인연락처", "액션": "붙여넣기", "값": 임대인연락처, "이동시간": 기본이동시간},
            {"명칭": "임대인성명", "액션": "붙여넣기", "값": 임대인성명, "이동시간": 기본이동시간},
            {"명칭": "임차인주소", "액션": "붙여넣기", "값": 임차인주소, "이동시간": 기본이동시간},
            {"명칭": "임차인주민번호", "액션": "붙여넣기", "값": 임차인주민번호, "이동시간": 기본이동시간},
            {"명칭": "임차인연락처", "액션": "붙여넣기", "값": 임차인연락처, "이동시간": 기본이동시간},
            {"명칭": "임차인성명", "액션": "붙여넣기", "값": 임차인성명, "이동시간": 기본이동시간},
            {"명칭": "계약서저장", "액션": "선택", "값": None, "이동시간": 기본이동시간},
            {"명칭": "확인설명서", "액션": "선택", "값": None, "이동시간": 2},
            {"명칭": "주거용", "액션": "선택", "값": None, "이동시간": 1},
            {"명칭": "비주거용", "액션": "선택", "값": None, "이동시간": 1},
            {"명칭": "토지용", "액션": "선택", "값": None, "이동시간": 1},
            {"명칭": "확인설명서확인", "액션": "선택", "값": None, "이동시간": 기본이동시간},

            {"명칭": "단독주택", "액션": "선택", "값": None, "이동시간": 1},
            {"명칭": "공동주택", "액션": "선택", "값": None, "이동시간": 1},
            {"명칭": "주거용오피스텔", "액션": "선택", "값": None, "이동시간": 1},
            {"명칭": "업무용", "액션": "선택", "값": None, "이동시간": 1},
            {"명칭": "상업용", "액션": "선택", "값": None, "이동시간": 1},
            {"명칭": "공업용", "액션": "선택", "값": None, "이동시간": 1},
            {"명칭": "매매교환", "액션": "선택", "값": None, "이동시간": 0.3},
            {"명칭": "임대", "액션": "선택", "값": None, "이동시간": 0.3},

            {"명칭": "등기사항증명서", "액션": "선택", "값": None, "이동시간": 기본이동시간},
            {"명칭": "건축물대장", "액션": "선택", "값": None, "이동시간": 기본이동시간},
            {"명칭": "지적도", "액션": "선택", "값": None, "이동시간": 기본이동시간},
            {"명칭": "임야도", "액션": "선택", "값": None, "이동시간": 기본이동시간},
            {"명칭": "토지이용계획", "액션": "선택", "값": None, "이동시간": 기본이동시간},
            {"명칭": "그밖의자료", "액션": "선택", "값": None, "이동시간": 기본이동시간},
            {"명칭": "그밖의자료입력", "액션": "붙여넣기", "값": "현장답사, 공제증서, 신분증", "이동시간": 기본이동시간},
            {"명칭": "토지면적", "액션": "붙여넣기", "값": 토지면적, "이동시간": 기본이동시간},
            {"명칭": "전용면적", "액션": "붙여넣기", "값": 전용면적, "이동시간": 기본이동시간},
            {"명칭": "실제이용상태", "액션": "붙여넣기", "값": 실제이용상태, "이동시간": 기본이동시간},
            {"명칭": "대지지분", "액션": "선택", "값": None, "이동시간": 기본이동시간},
            {"명칭": "준공년도", "액션": "붙여넣기", "값": 준공년도, "이동시간": 기본이동시간},
            {"명칭": "실제용도", "액션": "붙여넣기", "값": 실제용도, "이동시간": 기본이동시간},
            {"명칭": "방향기준", "액션": "붙여넣기", "값": "주출입문", "이동시간": 기본이동시간},
            {"명칭": "위반", "액션": "선택", "값": None, "이동시간": 기본이동시간},
            {"명칭": "적법", "액션": "선택", "값": None, "이동시간": 기본이동시간},
            {"명칭": "위반내용입력", "액션": "붙여넣기", "값": "", "이동시간": 기본이동시간},
            {"명칭": "계약서내용으로가져오기", "액션": "선택", "값": None, "이동시간": 기본이동시간},
            {"명칭": "적용확인", "액션": "선택", "값": None, "이동시간": 1},

            {"명칭": "확인설명서2쪽", "액션": "선택", "값": None, "이동시간": 기본이동시간},
            {"명칭": "도로와의관계2", "액션": "붙여넣기", "값": "0", "이동시간": 기본이동시간},
            {"명칭": "주차장없음", "액션": "선택", "값": None, "이동시간": 기본이동시간},
            {"명칭": "전용주차시설", "액션": "선택", "값": None, "이동시간": 기본이동시간},
            {"명칭": "경비실없음", "액션": "선택", "값": None, "이동시간": 기본이동시간},
            {"명칭": "자체관리", "액션": "선택", "값": None, "이동시간": 기본이동시간},
            {"명칭": "실제권리관계입력", "액션": "붙여넣기", "값": 실제권리관계입력, "이동시간": 기본이동시간},
            {"명칭": "소화전없음", "액션": "선택", "값": None, "이동시간": 기본이동시간},
            {"명칭": "비상벨없음", "액션": "선택", "값": None, "이동시간": 기본이동시간},
            {"명칭": "승강기없음", "액션": "선택", "값": None, "이동시간": 기본이동시간},
            {"명칭": "그밖의시설물", "액션": "붙여넣기", "값": "해당없음", "이동시간": 기본이동시간},
            {"명칭": "바닥면보통임", "액션": "선택", "값": None, "이동시간": 기본이동시간},
            {"명칭": "확인설명서3쪽", "액션": "선택", "값": None, "이동시간": 기본이동시간},
            
            {"명칭": "지급시기", "액션": "붙여넣기", "값": "잔금시", "이동시간": 기본이동시간},
            {"명칭": "실비입력", "액션": "붙여넣기", "값": "등기사항전부증명서 발급 외", "이동시간": 기본이동시간},
            {"명칭": "저장", "액션": "선택", "값": None, "이동시간": 기본이동시간}
        ]


        계약서준비 = ["계약관리", "조회조건", "조회조건_소재지", "조회조건_입력"]
        
        실행목록_계약조회 = ["계약서작성", "계약서종류_드롭다운", "부동산_선택", "중앙표시알림_확인", "거래종류_드롭다운", "월세_선택", "확인_버튼", "소재지_버튼"]

        
        실행목록_계약서작성_상 = [
            "토지면적", 
            "구조", 
            "용도", 
            "건물면적", 
            "임대할부분", 
            "임대할면적", 
            "보증금", 
            "계약금", 
            "차임"
        ]
        if 잔금일 != '0000-00-00':
            실행목록_계약서작성_상 = 실행목록의특정명령뒤추가(실행목록_계약서작성_상, "잔금일", "계약금")   
        if 선불후불 == "후불":
            실행목록_계약서작성_상 = 실행목록의특정명령뒤추가(실행목록_계약서작성_상, "선불후불", "차임") 
            실행목록_계약서작성_상 = 실행목록의특정명령뒤추가(실행목록_계약서작성_상, "후불", "선불후불")   
        if 부가세별도 == 'Y': 
            실행목록_계약서작성_상 = 실행목록의특정명령뒤추가(실행목록_계약서작성_상, "부가세별도")                


        실행목록_인적사항항작성 = [
            "임대인주소", 
            "임대인앞주민번호", 
            "임대인뒤주민번호", 
            "임대인연락처", 
            "임대인성명", 
            "임차인주소", 
            "임차인앞주민번호", 
            "임차인뒤주민번호", 
            "임차인연락처", 
            "임차인성명", 
            "계약서저장", 
            "확인설명서", 
        ]
        실행목록_확인설명서1쪽 = [
            "등기사항증명서",     # 등기사항증명서 좌표
            "그밖의자료",     # 그 밖의 자료  좌표
            "그밖의자료입력",     # 그 밖의 자료 입력 좌표

            "실제이용상태",       # 실제 이용 상태 좌표
            "준공년도",           # 준공년도 좌표
            "실제용도",           # 실제 용도 좌표
            "계약서내용으로가져오기",  # 계약서 내용으로 가져오기 좌표
            "적용확인",
            "계약갱신요구권행사여부미확인"
        ]
        if object_type == '주거용':
            실행목록_인적사항항작성 = 실행목록의특정명령뒤추가(실행목록_인적사항항작성, "주거용")   
            실행목록_인적사항항작성 = 실행목록의특정명령뒤추가(실행목록_인적사항항작성, "확인설명서확인") 

            실행목록_확인설명서1쪽 = 실행목록의특정명령뒤추가(실행목록_확인설명서1쪽, "건축물대장") 
            time.sleep(1)

        elif object_type == '토지':
            실행목록_인적사항항작성 = 실행목록의특정명령뒤추가(실행목록_인적사항항작성, "토지용")   
            실행목록_인적사항항작성 = 실행목록의특정명령뒤추가(실행목록_인적사항항작성, "확인설명서확인") 

            실행목록_확인설명서1쪽 = 실행목록의특정명령뒤추가(실행목록_확인설명서1쪽, "토지대장") 
            실행목록_확인설명서1쪽 = 실행목록의특정명령뒤추가(실행목록_확인설명서1쪽, "지적도") 
            time.sleep(1)
        else:
            실행목록_인적사항항작성 = 실행목록의특정명령뒤추가(실행목록_인적사항항작성, "비주거용") 
            실행목록_인적사항항작성 = 실행목록의특정명령뒤추가(실행목록_인적사항항작성, "확인설명서확인")   
            time.sleep(1)
            if object_type == '상업용':
                if object_type1 == '사무실':
                    실행목록_확인설명서1쪽 = 실행목록의특정명령뒤추가(실행목록_확인설명서1쪽, "업무용", "최우선") 
                elif object_type1 == '상가점포':
                    실행목록_확인설명서1쪽 = 실행목록의특정명령뒤추가(실행목록_확인설명서1쪽, "상업용", "최우선") 
            elif object_type == '공업용':
                실행목록_확인설명서1쪽 = 실행목록의특정명령뒤추가(실행목록_확인설명서1쪽, "공업용", "최우선") 

            실행목록_확인설명서1쪽 = 실행목록의특정명령뒤추가(실행목록_확인설명서1쪽, "건축물대장") 

        if contract_type == 'sale':
            실행목록_확인설명서1쪽 = 실행목록의특정명령뒤추가(실행목록_확인설명서1쪽, "매매교환", "최우선") 
            실행목록_확인설명서1쪽 = 실행목록의특정명령뒤추가(실행목록_확인설명서1쪽, "등기권리증") 
            실행목록_확인설명서1쪽 = 실행목록의특정명령뒤추가(실행목록_확인설명서1쪽, "토지이용계획확인서", "등기권리증") 
        elif contract_type == 'lease':
            실행목록_확인설명서1쪽 = 실행목록의특정명령뒤추가(실행목록_확인설명서1쪽, "임대", "최우선") 



        실행목록_확인설명서2쪽 = [
            "확인설명서2쪽",
            "도로와의관계2",
            "주차장없음",
            "경비실없음",
            "자체관리",
            "실제권리관계입력",
            "소화전없음",
            "비상벨없음",
            "승강기없음",
            "그밖의시설물",
            "바닥면보통임"
        ]
        

        실행목록_확인설명서3쪽 = [
            "확인설명서3쪽",
            "지급시기",
            "실비입력",
            "저장"
        ]

        
        # 스크롤다운
        scroll_val1 = -1600
        scroll_val2 = -1600

        실행목록_처리(계약서작업목록, 계약서준비)
        time.sleep(0.5)
        pyautogui.hotkey('ENTER')
        time.sleep(0.5)
        pyautogui.hotkey('ENTER')
        # pyautogui.alert("계속 진행하시겠습니까?")

        실행목록_처리(계약서작업목록, 실행목록_계약조회)
        실행목록_처리(계약서작업목록, 실행목록_계약서작성_상)
        스크롤다운(scroll_val1)
        실행목록_처리(계약서작업목록, ["특약사항"])
        스크롤다운(scroll_val2)
        실행목록_처리(계약서작업목록, 실행목록_인적사항항작성)
        실행목록_처리(계약서작업목록, 실행목록_확인설명서1쪽)
        실행목록_처리(계약서작업목록, 실행목록_확인설명서2쪽)
        실행목록_처리(계약서작업목록, 실행목록_확인설명서3쪽)
        pyautogui.alert("테스트완료")

        
        exit()        
    except Exception as e:
        print("데이터처리 오류:", str(e))
        traceback.print_exc()

    
def 메인():
    
    try:
        # 데이터베이스 연결을 초기화합니다.
        #ftp서버에 DB연결
        conn = 데이터베이스_연결_초기화()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('USE obangkr;')     

        while True:
            # tkinter 윈도우 생성
            root = tk.Tk()
            root.withdraw()  # 메인 윈도우 숨기기

            # 사용자에게 입력 받기
            contract_code = simpledialog.askstring("입력", "계약 코드를 입력하세요:", initialvalue="241213_C02", parent=root)

            if contract_code:
                계약데이터 = 계약_데이터_가져오기(cursor, contract_code)
                if 계약데이터:
                    pyautogui.alert("한방 계약관리화면을 우측 모니터에 전체화면으로 열어주세요")
                    print("계약데이터:", 계약데이터)
                    for row in 계약데이터:
                        데이터_처리(cursor, row)
                    break  # 유효한 데이터를 처리했으므로 루프를 빠져나옵니다.
                else:
                    pyautogui.alert("데이터가 존재하지 않습니다. 다시 입력해주세요.")
            else:
                # pyautogui.alert("계약 코드를 입력해주세요.")
                break


    except Exception as 예외:
        # 오류가 발생했을 경우, 오류 메시지를 출력합니다.
        print("메인 오류:", str(예외))
    finally:
        print("작업완료")
        # 작업이 완료되면 cursor와 conn을 닫습니다.
        root.destroy()  # tkinter 종료
        cursor.close()
        conn.close()
        pyautogui.alert("계약서작성이 완료되었습니다.")

# 파이썬 스크립트가 직접 실행될 때만 메인 함수를 호출합니다.
if __name__ == "__main__":
    메인()