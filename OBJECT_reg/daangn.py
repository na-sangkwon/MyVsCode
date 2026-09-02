# fileName: daangn.py
import time
import re
from ai_utils import ask_openrouter, CONFIG_API_KEY, CONFIG_MODEL
import pymysql
import threading  # 👈 [AI 대기제거 패치] 백그라운드 병렬 연산을 위한 라이브러리 추가
from datetime import timedelta, datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException
import pyautogui

import os
import sys
# 🚀 상위 폴더의 패키지를 인식할 수 있도록 시스템 경로(sys.path)에 추가하는 마법의 코드
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# 이제 공용 함수를 내 파일 안에 있는 것처럼 자유롭게 불러옵니다!
from util.property_utils import (
    최상단알림창,
    건축법상건축물용도로변환,
    만원단위숫자금액을한글금액으로,
    당근매물번호_검색창_입력, 
    검색결과_목록개수_확인, 
    리액트_입력창_값_강제주입, 
    당근_매물상태_확인, 
    당근_날짜및_끌어올리기_가능여부_확인,
    당근_끌어올리기_실행,
    텍스트창_값검속_및_신규업데이트판정,
    체크박스_상태검속_및_신규업데이트판정,
    라디오버튼_선택검속_및_신규업데이트판정,
    드롭다운_선택검속_및_신규업데이트판정,
    제목기준_다중체크박스_통합검속엔진,
    로그저장,
    텍스트기준_버튼_클릭,
    최상단_예아니오_창,
    데이터베이스_다중_가격스펙_전수조회,
    당근_끌어올리기_마스터_통합엔진,
)

# pyautogui.alert(ai_utils.CONFIG_API_KEY)
def generate_ai_one_liner(address, object_type):
    """
    공용 AI 모듈(ask_openrouter)을 사용하여 기존 질문 규칙과 파라미터를 100% 동일하게 유지한 채 결과를 반환받습니다.
    """
    if not CONFIG_API_KEY or CONFIG_API_KEY.strip() == "":
        print("ℹ️  [AI 한줄평] 중앙 관제탑에 API 키가 비어있어 기본 보안 마스킹 제목을 사용합니다.")
        return None
        
    print(f"🤖 [AI 한줄평] 중앙 통합 모델 [{CONFIG_MODEL}] 실시간 생성 요청 중...")
        
    # 🔒 비주거용 보안 마스킹 규칙 적용 (기존 지침 유지)
    security_rule = f"분석대상 매물위치: {address}\n"
    if object_type != '주거용':
        security_rule = "🚨 [보안 준수]: 비주거용 물건이므로 지번(예: 640-9), 호수(예: 103호), 건물명(예: 성지빌딩)은 타 중개업소의 우회 가로채기 방지를 위해 절대로 노출금지"
        
    # 2. 마스터 주문서 조립 (소장님의 기존 프롬프트 유지)
    # =================================================================
    # 🎯 [프롬프트 대개혁] 홍보 문구/이모지/특수문자 완벽 제거 및 순수 위치 정보 한정 규칙
    # =================================================================
    system_prompt = (
        "너는 부동산의 위치 정보를 정확하고 담백하게 요약하는 데이터 전문가야. "
        "제시된 주소와 특징을 바탕으로 오직 '행정 구역, 교통, 인접 시설' 정보만 나타내는 '위치 한줄평'을 작성해줘.\n\n"
        "❌ [엄격 금지 규칙 - 위반 시 무조건 에러]\n"
        "1. 이모지(예: ✨, 🏠, 🚗)는 절대로 쓰지 마라.\n"
        "2. 느낌표(!), 물결(~), 따옴표 등 모든 특수문자와 문장부호를 일절 사용하지 마라.\n"
        "3. '경기도 오산시 궐동 640-9 부근','궐동 버거킹건물 3층'과 같이 구체적인 위치표시금지.\n"
        # "3. '추천', '강추', '대박', '최고', '클릭유도' 같은 홍보성 멘트나 카피라이팅 미사여구는 엄격히 금지한다.\n\n"
        "⭕ [필수 준수 규칙]\n"
        "1. '홍대입구역 인근 서교동 카페거리 부근', '역삼동 주민센터 인근 조용한 주택가'와 같이 주변에 대표적인 건물이나 시설물이 있다면 활용하여 오직 사실적인 위치/교통 관련 내용만 남겨라.\n"
        "2. 반드시 공백 포함 25자 이내로 간결하게 작성하고, 다른 설명 없이 알맹이 결과만 대답해라.\n"
        f"{security_rule}"
    )
    user_prompt = f"매물위치: {address}"
    
    # 3. 🌟 기존 세팅값(모델, 창의성 0.5, 100토큰) 그대로 공용 함수에게 전달
    content = ask_openrouter(system_prompt, user_prompt, api_key=CONFIG_API_KEY, model=CONFIG_MODEL)
    
    if content:
        print(f"✅ [AI 한줄평 생성 system_prompt] ➡️ {system_prompt}")
        print(f"✅ [AI 한줄평 생성 성공] 결과 문구 ➡️ {content}")
        return content
    else:
        print("⚠️  [AI 한줄평 서비스 임시 우회] 공용 모듈 반환 오류로 기존 제목을 대체 사용합니다.")
        return None

def macro(data, user):
    """
    당근부동산 자동 매물 등록 (최종 검증 및 정제 완료 완료 버전)
    """
    driver = None
    try:
        # =================================================================
        # 1. DB 연동 데이터 추출
        # =================================================================
        admin_data = data.get('adminData', {})
        write_data = data.get('writeData', {})
        land_data_list = data.get('landData', [])
        land_data = land_data_list[0] if land_data_list else {}
        building_data = data.get('buildingData', {})
        room_data = data.get('roomData', {})
        ad_data = data.get('adData', {})





        admin_id = admin_data.get('admin_id', '')
        admin_name = admin_data.get('admin_name', '')    # 담당자명 (DB에 없으면 기본값 나상권)
        admin_phone = admin_data.get('admin_phone1', '')

        당근광고정보 = ad_data['당근'] if ad_data['당근'] else []
        if len(당근광고정보) > 0 : 
            당근광고종료일 = 당근광고정보['ad_end']
            당근광고담당자 = 당근광고정보['admin_id']
            당근매물번호 = 당근광고정보['ad_code']
            if 당근광고담당자 != admin_id :
                print(f"사용자({admin_id}) VS 기등록자({당근광고담당자})")
                pyautogui.alert(f"기등록된 당근광고정보가 있습니다. 내용을 확인해주세요~\n\n\n당근광고종료일: {당근광고종료일}\n\n당근광고담당자: {당근광고담당자}")
                return
            등록방식 = '업데이트'
        else:
            등록방식 = '신규'

        # 기본 정보
        title = write_data.get('object_title', '')          
        content = write_data.get('object_content', '')      
        object_type = write_data.get('object_type', '')     
        object_type1 = write_data.get('object_type1', '')   
        object_type2 = write_data.get('object_type2', '')  
        tr_target = write_data.get('tr_target', '')   
        request_manager = write_data.get('manager', '').strip()   # 관리비 여부 ('포함', '없음', '별도', '미확인')
        request_mmoney = write_data.get('mmoney', '')            # 고정 관리비 금액 (만원 단위)
        request_mlist = write_data.get('mlist', '')              # 포함 내역 문자열 ('인터넷,수도,유선')
        flexible_deposit = write_data.get('flexible_deposit', '') # 보증금 조정 가능 여부 ('Y' / 'N')
        request_main = write_data.get('request_main', '')        # 부동산 소재지
        object_code_new = write_data.get('object_code_new', '')  # 새홈 매물번호
        
        # 가격 정보 
        trade_type = write_data.get('object_ttype', '')     
        trading_price = write_data.get('trading', '')       
        deposit = write_data.get('deposit1', '')            
        rent = write_data.get('rent1', '')    
        deposit2 = write_data.get('deposit2', '')
        rent2 = write_data.get('rent2', '')      
        deposit3 = write_data.get('deposit3', '')
        rent3 = write_data.get('rent3', '')      
        request_term1 = write_data.get('request_term1', '')       
        premium_exist = write_data.get('premium_exist', '')      # 권리금 존재유무 ('없음' / '미확인' / '있음')
        premium = write_data.get('premium', '')                  # 권리금액 (만원 단위)
        premium_content = write_data.get('premium_content', '')  # 권시물내역 (설명창 주입 데이터)      

        if request_mlist:
            mlist_list = [x.strip() for x in str(request_mlist).split(',') if x.strip()]  
        try:
            mmoney_float = float(request_mmoney) if request_mmoney else 0.0
        except ValueError:
            mmoney_float = 0.0     

        target_manage_includes = ["공용"] # 부과방식이 별도/포함일 때 당근은 기본적으로 '공용' 명찰을 상시 요구함
        if request_mlist:
            manage_mapping_rules = {
                "인터넷": "인터넷비", "수도": "수도료", "유선": "TV", "전기": "전기료", "가스": "가스비", "난방": "난방비"
            }
            for db_word, karrot_label in manage_mapping_rules.items():
                # 신규 등록과 동일하게 공용전기/공용수도를 제외한 순수 개별 항목들만 정밀 분류 수집
                if any(db_word in item and "공용" not in item for item in mlist_list):
                    target_manage_includes.append(karrot_label)


        land_main = land_data.get('land_main', '').strip()
        representing_jibun = land_data.get('representing_jibun', '').strip()
        land_memo = land_data.get('land_memo', '')
        land_important = land_data.get('land_important', '')
        land_terms = land_data.get('land_terms', '')
        # 💡 [정밀 조합] 대표지번 결합 주소 생성 (데이터가 아예 없을 경우를 대비해 기존 address를 백업 가드로 작동)
        if land_main and representing_jibun:
            address_search = f"{land_main} {representing_jibun}"
        else:
            address_search = write_data.get('address', '')
        address = address_search             

        building_purpose = building_data.get('building_purpose', '') 
        floor_top = building_data.get('building_grndflr', '') 
        approval_date = building_data.get('building_usedate', '') 
        building_direction = building_data.get('building_direction', '') 
        building_totarea = building_data.get('building_totarea', '') 
        building_parking = building_data.get('building_parking', '') 
        building_pn = building_data.get('building_pn', '')           
        building_option = building_data.get('building_option', '')   # 건물 옵션 텍스트 
        building_important = building_data.get('building_important', '') # 건물 특징 데이터 추출
        building_terms = building_data.get('building_terms', '')
        building_memo = building_data.get('building_memo', '')
        building_hhld = building_data.get('building_hhld', '')       # 세대수 데이터 추출       
        
        # 면적 및 시설 정보
        area_private = room_data.get('room_area1', '')      
        area_supply = room_data.get('room_area2', '')       
        room_cnt = room_data.get('room_rcount', '')         
        bath_cnt = room_data.get('room_bcount', '')         
        floor_current = room_data.get('room_floor', '') 
        room_option = room_data.get('room_option', '')               # 호실 옵션 텍스트
        room_important = room_data.get('room_important', '')  
        room_memo = room_data.get('room_memo', '')
        room_terms = room_data.get('room_terms', '')         # 호실 특약 데이터 추출
        room_status = room_data.get('room_status', '')       # 호실 상태 (예: 공실, 거주중)
        rdate = write_data.get('rdate', '')                  # 거래 가능 시기 (입주가능일 날짜)  
        room_direction = room_data.get('room_direction', '') # 호실 방향
        # pyautogui.alert(f"room_direction:{room_direction}")
        
        full_options_str = str(room_option) + "," + str(building_option)
        
        option_replace_map = {
            '냉방기': '에어컨',
            '가스레인지': '가스렌지',
            '전자레인지': '전자렌지',
            '승강기': '엘리베이터'
        }
        for db_word, karrot_word in option_replace_map.items():
            full_options_str = full_options_str.replace(db_word, karrot_word)
        allowed_options = ['에어컨', '냉장고', '세탁기', '가스렌지', '인덕션', '전자렌지', '침대', '엘리베이터', '복층', '옥탑']
        matched_options = [opt for opt in allowed_options if opt in full_options_str]

        # =================================================================
        # 1. DB 연동 데이터 추출 (맨 하단 short_title 정의부 바로 밑에 추가)
        # =================================================================
        room_num = room_data.get('room_num', '') 
        short_title = request_main[:50] if request_main else "추천 매물"

        # =================================================================
        # 🏢 [순서 정렬] 매물 종류(Karrot Type) 지능형 선행 연산 및 검수 홀딩 엔진
        # =================================================================
        sub_types = str(object_type1) + " " + str(object_type2)
        print(f"sub_types:{sub_types}")
        # 🎯 [소장님 지시 규칙] tr_target이 '건물'/'통임대'이거나 건물 특징에 '통임대' 단어가 식별되면 무조건 '건물' 확정
        is_full_building_condition = (
            (tr_target in ['건물', '통임대']) or 
            (building_important and '통임대' in str(building_important))
        )

        if is_full_building_condition:
            karrot_type = "건물"
            print(f"🏢 [매물 종류 판독] 거래대상({tr_target}) 또는 통임대 조건에 부합하여 '건물' 카테고리로 최우선 확정합니다.")
            
            # 🎯 [신설] 통건물 등록 시, 호실 면적이 아닌 건물 대장(building_data)의 연면적을 수급하여 전용면적 변수에 가로채기 주입합니다.
            building_totarea = building_data.get('building_totarea', building_data.get('building_area', ''))
            if building_totarea and str(building_totarea).strip() not in ["", "0", "None"]:
                area_private = building_totarea
                print(f"   .. 📐 [건물 면적 스왑] 통건물 모드이므로 건물 연면적({area_private}㎡)을 입력 타겟으로 결정했습니다.")
        else:
            # 조건에 부합하지 않는 일반 호실별 매물은 기존 분류 체계 가동
            if object_type == '주거용':
                if '아파트' in sub_types: karrot_type = "아파트"
                elif '오피스텔' in sub_types: karrot_type = "오피스텔"
                # elif any(keyword in sub_types for keyword in ['주택', '단독', '다세대', '다가구']): karrot_type = "주택"
                else:
                    try: r_cnt_float = float(str(room_cnt).replace('룸', '').strip())
                    except ValueError: r_cnt_float = 1.0
                    if r_cnt_float < 2.0:
                        if room_important and '주방오픈형' in str(room_important): karrot_type = "오픈형 원룸"
                        else: karrot_type = "분리형 원룸"
                    else: karrot_type = "빌라(투룸 이상)"
            elif object_type == '상업용':
                if '사무실' in sub_types: karrot_type = "사무실"
                else: karrot_type = "상가"
            elif object_type == '공업용' or any(keyword in sub_types for keyword in ['공장', '창고']): karrot_type = "공장/창고"
            elif object_type == '토지': karrot_type = "토지"
            else:
                karrot_type = "건물" # 예외 방어용 매칭 기본 fallback

        # # 🎯 [소장님 요청 사항] 제대로 수정되었는지 브라우저 기동 전에 잠시 멈추는 최상단 검수 알림창 작동
        # 최상단알림창(
        #     f"📊 [매물 종류 사전 판독 및 홀딩 안내창]\n\n"
        #     f"• DB 거래대상 (tr_target) : {tr_target}\n"
        #     f"• 건물 특징 메모 데이터 : {building_important if building_important else '없음'}\n"
        #     f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        #     f"📢 최종 연산된 당근 카테고리 : [{karrot_type}]\n\n"
        #     f"원하시는 대로 '건물' 또는 알맞은 매물 종류로 결정되었는지 확인해 주세요.\n"
        #     f"이 안내창의 [확인]을 누르시면 비로소 크롬 브라우저가 실행되며 매크로가 시작됩니다.",
        #     title="🔍 매물 종류 결정 수동 검수 대기"
        # )

        # 🎯 [신설] 매물종류가 '토지'로 분류된 경우, 토지대장의 총면적(land_totarea)을 면적 변수에 스왑 주입합니다.
        if karrot_type == "토지":
            land_totarea = land_data.get('land_totarea', '')
            if land_totarea and str(land_totarea).strip() not in ["", "0", "None"]:
                area_private = land_totarea
                print(f"   .. 📐 [토지 면적 스왑] 토지 모드이므로 대지면적({area_private}㎡)을 입력 타겟으로 확정했습니다.")

        # 🔒 [보안 솔루션] 비주거용 주소/제목 보안 마스킹 연산
        public_title = short_title
        room_num_target = room_num

        if object_type != '주거용':
            if floor_current:
                f_clean = str(floor_current).replace('층', '').strip()
                room_num_target = f"{f_clean}층 일부"
            else:
                room_num_target = "일부"

            # 🎯 [근본적 해결] 상호 오염 위험이 있는 request_main 대신, 행정 구역 전용 데이터인 land_main을 최우선 소스로 강제 고정합니다.
            if land_main and str(land_main).strip() not in ["", "None"]:
                public_title = str(land_main).strip()
                print(f"🔒 [보안 화이트리스트 가동] 오염 없는 순수 행정동 주소({public_title})를 베이스 타이틀로 채택했습니다.")
            else:
                # 만약 land_main이 비어있을 때를 대비한 2중 백업 방어선 (기존 블랙리스트 가드에 보완 필터 결합)
                clean_text = short_title
                clean_text = re.sub(r'\d+-\d+', '', clean_text)
                clean_text = re.sub(r'\d+호|\d+층', '', clean_text)
                clean_text = re.sub(r'\S+(빌딩|타워|빌라|하우스|오피스텔|메디컬|프라자|플라자|센터|스퀘어|바게트|커피|카페|다이소|마트)', '', clean_text)
                clean_text = re.sub(r'(동|리|읍|면)\s*\d+', r'\1', clean_text)
                public_title = clean_text.strip() if len(clean_text.strip()) >= 4 else f"추천 {karrot_type} 매물"
                
            print(f"🔒 [보안 가동] 상세주소 가공: '{room_num}' ➡️ '{room_num_target}'")
            print(f"🔒 [보안 가동] 노출형 제목 정제: '{short_title}' ➡️ '{public_title}'")
        
        # 💡 [AI 대기제거 패치] 결과를 안전하게 공유해서 보관할 빈 딕셔너리를 만듭니다.
        ai_result = {"content": None}

        # 백그라운드 보관함에서 한줄평 수거
        ai_one_liner_retrieved = ai_result.get("content")
        # pyautogui.alert(f"✅ [AI 한줄평 생성 성공] 결과 문구 ➡️ {content}")
        
        # 💡 [핵심 안전장치] AI 결과가 올바르게 존재하면 그 값을 쓰고, 비어있다면 공백을 대입합니다.
        final_one_liner = ai_one_liner_retrieved if ai_one_liner_retrieved else '오산에서 방구하기 오방 (나상권부동산)'
        
        print(f"✨ [위치 한줄평 주입] 최종 기입 문구 ➡️ {final_one_liner}")


        # # 💡 백그라운드 스레드에서 작동할 미니 작업 함수를 만듭니다.
        # def bg_ai_worker():
        #     ai_result["content"] = generate_ai_one_liner(
        #         address=address,
        #         object_type=object_type,
        #     )

        # # 💡 보조 일꾼(Thread)을 생성해 백그라운드에서 AI 통신을 조용히 지시합니다.
        # ai_thread = threading.Thread(target=bg_ai_worker)
        # ai_thread.daemon = True  # 프로그램이 꺼지면 스레드도 같이 꺼지게 안전설정
        # ai_thread.start()
        # print("🚀 [AI 백그라운드 연산 시동] AI 한줄평을 뒤편에서 생성하기 시작합니다. 크롬 브라우저는 대기 없이 바로 기동됩니다!")

        print("\n" + "="*60)
        print("📋 [디버깅 - 1단계] 필수/핵심 원본 데이터 확인")
        print("="*60)
        print(f" 📍 검색할 주소 : {address}")
        print(f" 💰 거래 유형   : {trade_type} (보증금:{deposit} / 월세:{rent} / 매매가:{trading_price})")
        print(f" 🔹 전용 면적   : {area_private}㎡")
        print(f" 🔹 사용승인일  : {approval_date}")
        print("="*60 + "\n")

        # =================================================================
        # 2. 브라우저 실행
        # =================================================================
        chrome_options = Options()
        profile_path = os.path.join(os.getcwd(), "daangn_profile")
        chrome_options.add_argument(f"--user-data-dir={profile_path}")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.maximize_window()
        wait = WebDriverWait(driver, 10) 




















        # =================================================================
        # 3. 등록 방식별(업데이트 / 신규) 폼 진입 및 검속 시퀀스 가동
        # =================================================================
        if 등록방식 == '업데이트':
            print("당근 업데이트 시작")
            driver.get("https://realty.daangn.com/ceo/home") 
            당근매물번호_검색창_입력(driver, 당근매물번호)
            검색된목록수 = 검색결과_목록개수_확인(driver)

            print(f"📊 [업데이트 모드 - {당근매물번호}] 검색 필터링 매물 수: {검색된목록수}개")
            
            if 검색된목록수 == 1:
                해당매물행 = driver.find_element(By.CSS_SELECTOR, "div.flex.w-full.cursor-pointer.items-center.border-b")
                현재매물상태 = 당근_매물상태_확인(해당매물행)
                    
                # 끌올표시날짜, 끌올가능여부 = 당근_날짜및_끌어올리기_가능여부_확인(해당매물행)
                # 최상단알림창(f"끌올표시날짜:{끌올표시날짜}")
                try:
                    row_element = driver.find_element(By.CSS_SELECTOR, "div.flex.w-full.cursor-pointer.items-center.border-b")
                    edit_btn = row_element.find_element(By.XPATH, ".//button[text()='수정']")
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", edit_btn)
                    time.sleep(0.2)
                    driver.execute_script("arguments[0].click();", edit_btn)
                    print(f"✅ [업데이트 모드 - {당근매물번호}] 기존 매물 수정 폼 진입 성공! (전 필드 실시간 동기화 스캔 개시)")
                    
                    # 🎯 [치료 핵심] 수정창 로딩 판단 기준을 유령 address 대신 확정 노출되는 salesType으로 변경합니다.
                    WebDriverWait(driver, 8).until(EC.presence_of_element_located((By.NAME, "salesType")))
                    time.sleep(1.0) 
                except Exception as e:
                    print(f"❌ [업데이트 모드] 수정 페이지 진입 실패 -> {e}")
                    return
            else:
                print(f"⚠️ [업데이트 모드] 검색 결과 개수 불일치로 매크로 홀딩 처리")
                최상단알림창(f"검색 결과가 1개가 아니므로 ({검색된목록수}개) 자동 수정을 진행할 수 없습니다.")
                return

            # 🛠️ [데이터 전치 가동] 신규 모드용 정제 변수들을 업데이트 블록 내부에 정밀 동기화 빌드합니다.
            try:
                term_months = int(re.sub(r'\D', '', str(request_term1))) if request_term1 else 12
            except:
                term_months = 12

            price_sets = []
            raw_pairs = [(deposit, rent), (deposit2, rent2), (deposit3, rent3)]
            for dep_val, rent_val in raw_pairs:
                try:
                    if dep_val is not None and rent_val is not None:
                        if float(str(dep_val).strip()) >= 0 and float(str(rent_val).strip()) >= 0:
                            price_sets.append((float(str(dep_val).strip()), float(str(rent_val).strip())))
                except: continue

            is_short_term = False
            target_deposit = float(deposit) if deposit else 0.0
            target_rent = float(rent) if rent else 0.0
            if term_months < 12:
                for d_num, r_num in price_sets:
                    if d_num < (r_num * 3):
                        is_short_term = True
                        target_deposit = d_num
                        target_rent = r_num
                        break

            target_types = [t.strip() for t in trade_type.split(',') if t.strip()]
            if "월세" in target_types and is_short_term:
                target_types = ["단기" if t == "월세" else t for t in target_types]

            # 사용승인일 포맷 정제
            app_date_str = str(approval_date).strip() if approval_date else ""
            if len(app_date_str) == 8 and "-" not in app_date_str:
                app_date_str = f"{app_date_str[:4]}-{app_date_str[4:6]}-{app_date_str[6:]}"

            # 방향 포맷 정제
            target_direction = str(room_direction).strip() if room_direction else ""
            if karrot_type == "건물" and building_direction:
                target_direction = str(building_direction).strip()
            if target_direction and not target_direction.endswith('향') and target_direction in ['남', '동', '서', '북', '남동', '남서', '북동', '북서']:
                target_direction += '향'
            elif object_type == '주거용' and not target_direction:
                target_direction = "남향"

            # 주차 및 세대수 정제
            parking_status = "가능" if (building_parking == '있음' or '주차' in str(building_option) or (building_pn and str(building_pn) != '0')) else "불가능"
            parking_per_hhld = ""
            if parking_status == "가능" and building_pn and building_hhld:
                try:
                    if int(building_hhld) > 0:
                        parking_per_hhld = str(round(int(building_pn) / int(building_hhld), 2))
                except: pass

            # 건축물 용도 정제 
            mapped_purpose = 건축법상건축물용도로변환(building_purpose, area_private)
            if not mapped_purpose: mapped_purpose = "제2종 근린생활시설"

            # 상업용 화장실 보정
            if object_type == '상업용' and (not bath_cnt or str(bath_cnt).strip() in ["", "0", "None"]):
                bath_cnt = "1" if (room_option and '화장실' in str(room_option)) else "0"

            # 비밀 메모 조립
            memo_date_str = datetime.now().strftime('%y%m%d')
            secret_memo_text = f"{request_main}\n{memo_date_str} {admin_name}등록(새홈번호: {object_code_new})"

            # =================================================================
            # 📐 [소장님 지시 반영 - 최소 추가] 실실시간 대조용 면적 반올림 정제 시퀀스
            # =================================================================
            # 화면 UI(66.12)와 DB 날것(66.1157)의 불일치로 인한 가짜 업데이트 판정을 차단합니다.
            if area_private and str(area_private).strip() not in ["", "0", "None"]:
                try: area_private = str(round(float(area_private), 2))
                except: pass
            if area_supply and str(area_supply).strip() not in ["", "0", "None"]:
                try: area_supply = str(round(float(area_supply), 2))
                except: pass

            # 📊 [마스터 동기화 팩토리 가동] - 전 필드 일괄 자동 검속 및 동적 주입 시동
            업데이트결과리포트 = {}
            업데이트결과리포트["거래유형"] = 제목기준_다중체크박스_통합검속엔진(driver, "거래 유형", target_types)
            업데이트결과리포트["매물종류"] = 드롭다운_선택검속_및_신규업데이트판정(driver, "salesType", karrot_type, "매물 종류")
            업데이트결과리포트["건축물용도"] = 드롭다운_선택검속_및_신규업데이트판정(driver, "buildingUsage", mapped_purpose, "건축물 용도")
            업데이트결과리포트["전용면적"] = 텍스트창_값검속_및_신규업데이트판정(driver, "area", area_private, "전용 면적")
            
            if karrot_type not in ["건물", "토지"]:
                업데이트결과리포트["공급면적"] = 텍스트창_값검속_및_신규업데이트판정(driver, "supplyArea", area_supply, "공급 면적")
                
            업데이트결과리포트["사용승인일"] = 텍스트창_값검속_및_신규업데이트판정(driver, "buildingApprovalDate", app_date_str, "사용승인일")
            
            if karrot_type != "토지":
                업데이트결과리포트["방개수"] = 텍스트창_값검속_및_신규업데이트판정(driver, "roomCnt", room_cnt, "방 개수")
                업데이트결과리포트["욕실개수"] = 텍스트창_값검속_및_신규업데이트판정(driver, "bathroomCnt", bath_cnt, "욕실 개수")
                업데이트결과리포트["전체층수"] = 텍스트창_값검속_및_신규업데이트판정(driver, "topFloor", floor_top, "전체 층수")
                업데이트결과리포트["해당층수"] = 텍스트창_값검속_및_신규업데이트판정(driver, "floor", str(abs(int(floor_current))) if floor_current else "", "해당 층수")
                업데이트결과리포트["방향"] = 드롭다운_선택검속_및_신규업데이트판정(driver, "buildingOrientation", target_direction, "방향")

            # 주차 라디오 및 세부 입력창 검속
            parking_container = "//span[text()='주차']/ancestor::div[contains(@class, 'flex-col') or contains(@class, 'items-start')][1]"
            업데이트결과리포트["주차여부"] = 라디오버튼_선택검속_및_신규업데이트판정(driver, parking_container, parking_status, "주차 여부")
            if parking_status == "가능":
                업데이트결과리포트["총주차대수"] = 텍스트창_값검속_및_신규업데이트판정(driver, "availableTotalParkingSpots", building_pn, "총 주차대수")
                if parking_per_hhld:
                    업데이트결과리포트["세대당주차"] = 텍스트창_값검속_및_신규업데이트판정(driver, "availableParkingSpotsV2", parking_per_hhld, "세대당 주차대수")

            if object_type == '주거용':
                업데이트결과리포트["시설옵션"] = 제목기준_다중체크박스_통합검속엔진(driver, "시설 정보", matched_options)
            
            # 관리비 부과 방식 세그먼트 및 포함 항목 검속
            if request_manager == "별도":
                target_manage_mode = "정액 관리비" if 0 < mmoney_float < 10 else "기타 부과"
            elif request_manager == "포함":
                target_manage_mode = "정액 관리비"
            else:
                target_manage_mode = "확인 불가"
            
            업데이트결과리포트["부과방식"] = 라디오버튼_선택검속_및_신규업데이트판정(driver, "//div[@aria-label='관리비 부과 방식']", target_manage_mode, "관리비 부과 방식")
            if target_manage_mode in ["정액 관리비", "기타 부과"]:
                업데이트결과리포트["총관리비"] = 텍스트창_값검속_및_신규업데이트판정(driver, "totalManageCost", request_mmoney, "총 관리비")
                if request_mlist:
                    업데이트결과리포트["관리비포함"] = 제목기준_다중체크박스_통합검속엔진(driver, "관리비에 포함", target_manage_includes)

            # 후반부 문자열 텍스트 에어리어 검속
            업데이트결과리포트["위치한줄평"] = 텍스트창_값검속_및_신규업데이트판정(driver, "addressInfo", final_one_liner, "위치 한줄평", xpath_target="//input[@name='addressDescription' or @name='addressInfo']")
            업데이트결과리포트["상세설명"] = 텍스트창_값검속_및_신규업데이트판정(driver, "content", content, "상세 설명")
            업데이트결과리포트["비밀메모"] = 텍스트창_값검속_및_신규업데이트판정(driver, "memoContent", secret_memo_text, "중개소 비밀메모")

            # =================================================================
            # 🛑 [공용 예아니오창 엔진 도입] 단 한 줄로 소장님의 의사를 여쭤봅니다!
            # =================================================================
            순수물건변동여부 = any(res.get("status") in ["업데이트", "신규입력"] for key, res in 업데이트결과리포트.items() if key != "비밀메모" and res)

            final_report_msg = "변동없음"
            if not 순수물건변동여부:
                question_msg = (
                    "물건 정보 중 실제로 변경된 내용이 전혀 없습니다.\n"
                    "(중개소 비밀메모만 최신 날짜로 자동 조합됨)\n\n"
                    "수정을 취소하고 대시보드 목록 화면으로 나갈까요?\n\n"
                    "[예] ➡️ 수정 취소 후 즉시 목록으로 복귀\n"
                    "[아니오] ➡️ 무시하고 계속 진행하여 저장 마감"
                )
                
                # # 🚀 공용 함수가 반환해 준 결과값(True/False)을 받아 즉시 조건문 가동!
                # if 최상단_예아니오_창(question_msg, title="🔍 물건정보 변동 없음 감지"):
                #     print("   [🛑 매크로 탈출] 순수 물건 변동이 없어 수정을 취소하고 메인 목록으로 복귀합니다.")
                #     driver.get("https://realty.daangn.com/ceo/home")
                #     당근매물번호_검색창_입력(driver, 당근매물번호)
                #     pass

                driver.get("https://realty.daangn.com/ceo/home")
                당근매물번호_검색창_입력(driver, 당근매물번호)
            
            # 물건정보가 변경된 경우
            else:
                print("수정화면의 물건정보가 변경된 경우")
                # 📊 시각화 알림창 마감 리포트 출력 구동
                # 📊 [대개혁 - 소장님 맞춤형 이원화 가독성 리포트 엔진]
                changed_lines = []
                unchanged_lines = []
                
                for field_key, field_res in 업데이트결과리포트.items():
                    if not field_res: 
                        continue
                    current_status = field_res.get("status", "유지(패스)")
                    val_before = field_res.get("before", "").strip()
                    val_after = field_res.get("after", "").strip()
                    
                    # 가인식 공백 명찰화 처리
                    val_before_display = f"'{val_before}'" if val_before else "공백"
                    val_after_display = f"'{val_after}'" if val_after else "공백"
                    
                    if current_status == "유지(패스)":
                        # 변경 없는 항목: 항목명과 값만 심플하게 주머니에 저장
                        unchanged_lines.append(f"  • {field_key} ({val_after_display})")
                    else:
                        # 변경 있는 항목: 불필요한 태그를 떼고 심플하게 이전 ➡️ 이후 값만 조준 저장
                        changed_lines.append(f"  • {field_key}: {val_before_display} ➡️ {val_after_display}")

                # 🚀 최종 출력용 스냅샷 리포트 본문 조립
                report_lines = [
                    f"🔎 [검속 대상] 새홈번호: {object_code_new} | 당근번호: {당근매물번호}",
                    f"📊 [화면 상태] 검색 목록: {검색된목록수}개 | 현재 상태: {현재매물상태}",
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                ]
                
                # 1구역: 변경 및 동기화 완료 항목 배치
                if changed_lines:
                    report_lines.append("🔄 [값 변동 및 업데이트 항목]")
                    report_lines.extend(changed_lines)
                else:
                    report_lines.append("🔄 [값 변동 및 업데이트 항목] ➡️ 없음 (모든 정보 완벽 일치)")
                    
                report_lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                
                # 2구역: 변동 없는 유지 항목 배치
                if unchanged_lines:
                    report_lines.append("✅ [일치 항목 (기존 값 유지)]")
                    report_lines.extend(unchanged_lines)
                    
                report_lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                report_lines.append("💡 모든 필드의 동적 대조 및 동기화 기입이 완료되었습니다.")
                report_lines.append("화면을 최종 검수하신 후, 우측 하단의 [매물 수정] 버튼을 눌러 마감해주세요.")
                
                final_report_msg = "\n".join(report_lines)

                # =================================================================
                # 🎯 [소장님 아키텍처 지침 적용] 당근마켓 전용 변동 알맹이 데이터 정제 시퀀스
                # =================================================================
                changed_history_list = []
                for field_key, field_res in 업데이트결과리포트.items():
                    if not field_res: 
                        continue
                    current_status = field_res.get("status", "유지(패스)")
                    
                    # 오직 실제로 '값의 변동'이 일어난 항목만 정밀 필터링 수집
                    if current_status in ["업데이트", "신규입력"]:
                        val_before = field_res.get("before", "").strip()
                        # val_after = field_res.get("after", "").strip()
                        val_before_display = f"'{val_before}'" if val_before else "공백"
                        # val_after_display = f"'{val_after}'" if val_after else "공백"
                        
                        changed_history_list.append(f"{field_key}: {val_before_display}")

                # 변동된 실체 내용이 1개라도 존재할 때만 완벽하게 분리된 순수 공용 로그 함수를 호출합니다!
                if changed_history_list:
                    # 불필요한 장식 다 걷어내고 순수 알맹이만 줄바꿈(\n) 문자열로 결합
                    clean_log_value = "\n".join(changed_history_list)
                    
                    # 🚀 공용 함수에 규격화된 원본 재료들만 정직하게 배달 주입!
                    로그저장(
                        log_target=object_code_new,   # 새홈 매물번호 명시
                        log_item="당근자동수정",       # 신규등록프로그램으로 기등록매물수정 
                        log_value=clean_log_value,  # 정제된 순수 변경점 텍스트 블록 주입
                        admin_id=admin_id           # 작업자 ID 주입
                    )
                else:
                    print("   [💾 시스템] UI 상태와 DB 데이터가 100% 일치하여 범용 로그 적재를 패스합니다.")

                # =================================================================
                # 🚀 [소장님 요청사항 - 최소 추가] '매물 수정' 버튼 자동 클릭 및 목록 복귀
                # =================================================================
                try:
                    # 복잡한 스크롤, 대기, 클릭 스크립트 연산을 공용 함수 하나로 압축 교체했습니다.
                    if 텍스트기준_버튼_클릭(driver, "매물 수정"):
                        # 저장 완료 후 메인 대시보드 목록(/ceo/home)으로 돌아올 때까지 정밀 대기
                        WebDriverWait(driver, 6).until(EC.url_contains("/ceo/home"))
                        time.sleep(0.5)
                except Exception as save_err:
                    print(f"   .. ❌ 자동 저장 중 지연 발생 (수동 마감 필요) -> {save_err}")

            해당매물행 = driver.find_element(By.CSS_SELECTOR, "div.flex.w-full.cursor-pointer.items-center.border-b")
            끌올표시날짜, 끌올가능여부 = 당근_날짜및_끌어올리기_가능여부_확인(해당매물행)
            print(f"끌올표시날짜:{끌올표시날짜}")
            if 끌올가능여부:
                print("끌어올리기 가능상태")
                DB_유효_가격목록 = 데이터베이스_다중_가격스펙_전수조회(object_code_new)
                # ② 🚀 [핵심 연동] 복잡한 모든 팝업 추적 처리를 공용 통합 엔진에게 배달 위임합니다!
                결과_코드명사 = 당근_끌어올리기_마스터_통합엔진(
                    driver,
                    row_element=해당매물행,
                    ad_code=당근매물번호,
                    current_status=현재매물상태,
                    price_specs=DB_유효_가격목록
                )
                print(f"결과_코드명사:{결과_코드명사}")
            else:
                최상단알림창("끌어올리기 표시안됨")


            # 마스터 종합 가독성 안내창 오픈 후 당근 매커니즘 종료
            if final_report_msg: 최상단알림창(final_report_msg, title="📊 당근마켓 업데이트 검속 완료 리포트")
            if driver:
                driver.quit()
        













        elif 등록방식 == '신규' :
            print("당근 신규등록 시작")
            # =================================================================
            # 3. 로그인 및 폼 진입 (알림창 제어 포함)
            # =================================================================
            driver.get("https://realty.daangn.com/") 
            # 최상단알림창("확인?329")        
            sidebar_btn_xpath = "//button[contains(., '매물 등록')]"
            print('매물등록 버튼 클릭시도')
            try:
                register_btn = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, sidebar_btn_xpath)))
                register_btn.click()
                # register_btn = wait.until(
                #     EC.element_to_be_clickable((By.XPATH, sidebar_btn_xpath))
                # )
                # register_btn.click()
            except TimeoutException:
                print("🔑 로그인이 필요합니다.")
                pyautogui.alert("크롬 창에서 당근 로그인을 완료 후 [확인]을 누르세요.")
                register_btn = wait.until(EC.element_to_be_clickable((By.XPATH, sidebar_btn_xpath)))
                register_btn.click()
            print("⏳ 임시저장 알림창 발생 여부 실시간 감지 중 (최대 4초 대기)...")

            try:
                # 💡 무조건 2초 쉬는 게 아니라, 알림창이 브라우저에 "출현할 때까지" 정밀 대기합니다.
                alert = WebDriverWait(driver, 4).until(EC.alert_is_present())
                alert_text = alert.text
                print(f"⚠️  [알림창 감지 완료] 팝업 문구: '{alert_text}'")
                
                # 알림창 거절 (작성 중인 글 이어 쓰지 않고 새로 쓰기 진행)
                alert.dismiss()
                print("➡️  임시저장 알림창을 거절(새로 쓰기)하여 양식을 초기화했습니다.")
                time.sleep(0.8)
            except TimeoutException:
                # 4초 동안 기다렸는데도 알림창이 안 뜨면 깨끗한 상태로 인지하고 정상 진행합니다.
                print("ℹ️  임시저장 알림창 없음 (안전 대기 종료 - 정상 진행).")
            except Exception as alert_err:
                print(f"ℹ️  알림창 처리 중 기타 예외 발생 (패스): {alert_err}")

            wait.until(EC.presence_of_element_located((By.NAME, "address")))
            print("\n" + "="*60)
            print("📝 [디버깅 - 2단계] 필수 항목 클릭 및 동적 입력 로그")
            print("="*60)

            # =================================================================
            # 4. 공통 자동화 헬퍼 함수 정의 (안전 대기 및 중복 입력 방지 통합본)
            # =================================================================
            failed_fields = [] # 👈 [신설] 매크로 입력 실패 항목을 모으는 보관함

            def inject_input(field_name, value, label):
                if value is None or str(value).strip() == "":
                    print(f"⚠️  [{label}] 건너뜀 -> 데이터 없음")
                    return
                try:
                    element = WebDriverWait(driver, 3).until(
                        EC.presence_of_element_located((By.NAME, field_name))
                    )
                    current_val = element.get_attribute('value')
                    if current_val and current_val.strip() == str(value).strip():
                        print(f"ℹ️  [{label}] 이미 올바른 값({current_val})이 자동 입력되어 있어 패스합니다.")
                        return
                    element.send_keys(Keys.CONTROL + "a")
                    element.send_keys(Keys.BACKSPACE)
                    time.sleep(0.1)
                    element.send_keys(str(value))
                    print(f"✅ [{label}] 입력 성공 -> {value}")
                except Exception as e:
                    err_msg = f"• {label} 입력 실패 (요소 누락 또는 대기 초과)" # 👈 수집용 문구 정제
                    print(f"❌ {err_msg}")
                    failed_fields.append(err_msg) # 실패 주머니에 저장

            def click_element_by_xpath(xpath, label):
                try:                                
                    # 요소 찾기
                    element = wait.until(
                        EC.presence_of_element_located((By.XPATH, xpath))
                    )
                    # 스크롤 이동
                    driver.execute_script(
                        "arguments[0].scrollIntoView({block:'center'});",
                        element
                    )
                    # 클릭 가능해질 때까지 대기
                    element = wait.until(
                        EC.element_to_be_clickable((By.XPATH, xpath))
                    )                 
                    # element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                    element.click()
                    print(f"✅ [{label}] 클릭 성공")
                    return True
                except Exception as e:
                    err_msg = f"• {label} 클릭 실패"
                    # err_msg = f"• {label} 클릭 실패 (방해 레이어로 인한 클릭 불가)" # 👈 수집용 문구 정제
                    print(f"❌ {err_msg}")
                    failed_fields.append(err_msg) # 실패 주머니에 저장
                    return False
            
            # =================================================================
            # 5. 주소 검색 및 선택 자동화 (결과 수량 자동 판단)
            # =================================================================
            if address:
                print("🔍 [주소 검색] 팝업창 제어 및 결과 분석 시작...")
                
                try:
                    main_address_btn = driver.find_element(By.XPATH, "//button[@name='address']")
                    main_address_btn.click()
                    print("   .. 메인 화면의 주소 검색 버튼 클릭 완료")
                except:
                    print("   .. 주소 팝업창이 이미 열려 있는 상태입니다.")

                try:
                    popup_input_xpath = "//div[@role='dialog']//input[contains(@placeholder, '한누리대로')]"
                    address_input = wait.until(EC.presence_of_element_located((By.XPATH, popup_input_xpath)))
                    
                    address_input.clear()
                    address_input.send_keys(str(address))
                    print(f"   .. 팝업 입력창에 '{address}' 타이핑 완료")
                    time.sleep(0.5)
                    
                    address_input.send_keys(Keys.ENTER)
                    print("   .. 주소 검색 엔터(ENTER) 실행 완료")
                    
                    # =================================================================
                    # 🌟 [오류 해결 완료] 무조건 2초 대기 제거 -> 결과 출현 OR 결과 없음 동적 감시
                    # =================================================================
                    # 💡 XPath의 '|' (OR) 연산자를 사용해 [선택] 버튼이나 [결과 없음] 문구 중 먼저 뜨는 걸 감지합니다.
                    combined_xpath = "//div[@role='dialog']//button[text()='선택'] | //span[text()='검색 결과가 없어요.']"
                    
                    try:
                        # 당근 서버가 응답을 보내 화면을 갱신할 때까지만 정밀 동적 대기 (최대 4초)
                        WebDriverWait(driver, 4).until(
                            EC.presence_of_element_located((By.XPATH, combined_xpath))
                        )
                        print("   .. ⚡ 당근부동산 검색 응답 수신 완료 (0.1초 단위 매칭 성공)")
                    except TimeoutException:
                        print("   .. ⏳ 네트워크 또는 로딩 지연으로 대기 시간 초과 (계속 진행)")

                    # 대기가 끝난 즉시 [선택] 버튼들의 개수를 수집하여 자동 분기 시동
                    select_buttons_xpath = "//div[@role='dialog']//button[text()='선택']"
                    result_buttons = driver.find_elements(By.XPATH, select_buttons_xpath)
                    result_count = len(result_buttons)
                    
                    print(f"📊 [주소 검색 결과 분석] 발견된 주소 개수: {result_count}개")
                    
                    if result_count == 1:
                        print("   .. 🎯 검색 결과가 1개이므로 자동으로 [선택] 버튼을 클릭합니다.")
                        result_buttons[0].click()
                        print("✅ [주소 선택 완료] 자동 매칭 성공")
                    elif result_count >= 2:
                        print("   .. ⚠️  검색 결과가 여러 개이므로 수동 선택 모드로 전환합니다.")
                        최상단알림창(
                            f"주소 검색 결과가 총 {result_count}개 발견되었습니다.\n\n"
                            "원하시는 정확한 주소지 우측에 있는 [선택] 버튼을 직접 클릭해 주신 뒤,\n"
                            "이 프로그램 알림창의 [확인]을 눌러 계속 진행해 주세요."
                        )
                    else:
                        print("   .. ❌ 검색 결과가 0개입니다. 수동 검색 대기.")
                        최상단알림창(
                            f"'{address}'로 검색된 주소 결과가 없습니다.\n\n"
                            "팝업창에서 검색어를 직접 수정하여 입력한 뒤 [선택]까지 완료해 주시고,\n"
                            "이 프로그램 알림창의 [확인]을 눌러주세요."
                        )
                    
                except Exception as e:
                    print(f"❌ [주소 팝업 제어 실패] -> 진행 중 오류 발생: {e}")
            else:
                print("⚠️  [주소] 건너뜀 -> DB에 주소 데이터가 없습니다.")
            
            # =================================================================
            # 5-2. [상세 주소 고도화] 호실 검색 및 자동/수동 분기 처리 (완전 교정)
            # =================================================================
            if room_num:
                print(f"🚪 [상세 주소 설정] '{room_num}' 입력 및 필터링 시작...")
                
                detail_input_xpath = "//input[contains(@placeholder, 'A-1101')]"
                detail_input = wait.until(EC.presence_of_element_located((By.XPATH, detail_input_xpath)))
                
                detail_input.click()
                detail_input.clear()
                detail_input.send_keys(str(room_num))
                print(f"   .. 상세 주소창에 '{room_num}' 입력 완료")
                time.sleep(0.8) 
                
                room_options_xpath = "//div[contains(@class, 'bg-bg-layer-default')]//p[contains(@class, 'cursor-pointer')]"
                room_options = driver.find_elements(By.XPATH, room_options_xpath)
                filtered_count = len(room_options)
                
                print(f"📊 [상세 주소 결과 분석] 필터링된 공식 호실 수: {filtered_count}개")
                
                exact_match = False
                
                # [분기 1] 검색 결과가 정확히 1개이고 공식 명칭과 완전히 일치할 때
                if filtered_count == 1:
                    target_room_text = room_options[0].text.strip()
                    if target_room_text == str(room_num).strip():
                        print(f"   .. 🎯 공식 주소록 일치 항목 발견({target_room_text}) -> 자동 선택합니다.")
                        room_options[0].click()
                        exact_match = True
                        # 최상단알림창("입력하기버튼클릭 전")
                        time.sleep(0.2)
                        # =================================================================
                        # 🚀 [소장님 피드백 반영 - 유령 클릭 완벽 차단 JS 안전핀 장착]
                        # =================================================================
                        # 입력창 포커스가 풀리며 버튼 좌표가 위로 도망치더라도,
                        # 물리 좌표와 무관하게 고유 엘리먼트를 직접 타격하는 브라우저 자바스크립트 엔진을 가동합니다.
                        submit_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='입력하기']")))
                        driver.execute_script("arguments[0].click();", submit_btn)
                        print("✅ [상세 주소 설정 완료] 공식 등록 주소 매칭 성공.")

                # [분기 2] 🎯 [소장님 지시사항 적용] 결과가 없거나 커스텀 호실명이어서 직접 입력이 필요할 때 (일반/유형별 동적 우회 패치)
                if not exact_match:
                    current_step = "준비 단계"
                    
                    try:
                        # 0) 상세주소 입력창을 다시 클릭하여 확실하게 포커스를 주고 레이아웃을 정렬합니다.
                        current_step = "1단계: 상세주소 입력창 강제 포커스 및 정렬 대기"
                        detail_input.click()
                        time.sleep(0.3)
                        
                        # 🎯 [치료 핵심] '직접 입력' 버튼이 존재하는지 0초 대기로 즉시 리스트 수집
                        direct_btn_list = driver.find_elements(By.XPATH, "//button[text()='직접 입력']") if False else driver.find_elements(By.XPATH, "//button[text()='직접 입력']")
                        
                        # ---------------------------------------------------------
                        # 상황 A: 실시간 목록이나 '직접 입력' 단추가 없는 담백한 일반 주소 규격일 때
                        # ---------------------------------------------------------
                        if not direct_btn_list:
                            print("   .. ℹ️  [주소 규격 판독] '직접 입력' 버튼이 없는 일반 주택 형태입니다. 즉시 입력을 확정합니다.")
                            current_step = "일반 주소 규격: 팝업 폐쇄를 위한 최종 하단 [입력하기] 버튼 클릭 처리"
                            
                            submit_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='입력하기']")))
                            driver.execute_script("arguments[0].click();", submit_btn)
                            print("✅ [상세 주소 입력 완료] 일반 주소 팝업창이 가림막 없이 깔끔하게 폐쇄되었습니다.")
                            time.sleep(0.4)
                            
                        # ---------------------------------------------------------
                        # 상황 B: 공식 리스트 팝업창이 열려있고 '직접 입력' 단추가 가로막고 있을 때
                        # ---------------------------------------------------------
                        else:
                            print("   .. ⚠️  공식 주소록 팝업이 감지되어 소장님 지시대로 [직접 입력] 물리 시퀀스를 가동합니다.")
                            direct_btn = direct_btn_list[0]
                            
                            # 1) '직접 입력' 단추 레이어 무력화 강제 터치
                            current_step = "2단계: [직접 입력] 버튼 마우스 풀세트 시퀀스 주입"
                            mouse_sequence_script = """
                            var el = arguments[0];
                            var e1 = new MouseEvent('mousedown', {bubbles: true, cancelable: true, view: window});
                            el.dispatchEvent(e1);
                            var e2 = new MouseEvent('mouseup', {bubbles: true, cancelable: true, view: window});
                            el.dispatchEvent(e2);
                            var e3 = new MouseEvent('click', {bubbles: true, cancelable: true, view: window});
                            el.dispatchEvent(e3);
                            """
                            driver.execute_script(mouse_sequence_script, direct_btn)
                            print("   .. ✅ [직접 입력] 버튼에 가상 마우스 물리 압착 시퀀스 조준 발사 성공")
                            time.sleep(0.5) 
                            
                            # 2) 활성화된 수동 입력란 포커싱
                            current_step = "3단계: 새로 생성된 직접 입력창 엘리먼트 정밀 추적"
                            direct_input_xpath = "//div[@role='dialog']//input[contains(@placeholder, 'A-1101')]"
                            direct_input = wait.until(EC.presence_of_element_located((By.XPATH, direct_input_xpath)))
                            
                            # 3) 호실명 문자열 정밀 재기입
                            current_step = f"4단계: 직접 입력창 클릭 및 호실 명칭({room_num_target}) 최종 타이핑"
                            direct_input.click()
                            direct_input.send_keys(Keys.CONTROL + "a")
                            direct_input.send_keys(Keys.BACKSPACE)
                            time.sleep(0.1)
                            direct_input.send_keys(str(room_num_target))
                            print(f"   .. ✍️  직접 입력창에 '{room_num_target}' 최종 타이핑 완료")
                            time.sleep(0.2)
                            
                            # 4) 최종 하단 [입력하기] 버튼을 실행하여 팝업 완벽히 닫기
                            current_step = "5단계: 팝업 폐쇄를 위한 최종 하단 [입력하기] 버튼 클릭 완료"
                            submit_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='입력하기']")))
                            driver.execute_script("arguments[0].click();", submit_btn)
                            print("✅ [상세 주소 수동 입력 완료] 주소 팝업창이 성공적으로 차단 해제 및 폐쇄되었습니다.")
                            time.sleep(0.4)
                        
                    except Exception as detail_err:
                        err_summary = f"• 상세 주소 직접 입력 실패 (지점: {current_step})"
                        print(f"❌ [상세 주소 직접 입력 제어 실패] -> 멈춘 위치: [{current_step}] / 에러 원인: {detail_err}")
                        failed_fields.append(err_summary)
                        
                        최상단알림창(
                            f"상세 주소 수동 직접 입력 처리 중 오류가 발생했습니다.\n\n"
                            f"🚨 실패 지점 : {current_step}\n"
                            f"⚙️ 에러 내용 : {detail_err}\n\n"
                            f"열려 있는 당근 창에서 직접 '{room_num_target}'을 입력하고 [입력하기]를 마우스로 클릭해 주신 뒤,\n"
                            "이 알림창의 [확인]을 눌러 다음 단계(매물 종류 선택)로 진행해 주세요.",
                            title="❌ 주소 직접 입력 에러 지점 파악"
                        )
                # 최상단알림창("주소선택완료?")
                # =================================================================
                # 5-2-B. [고도화] 중복 매물 경고창 통합 감지 및 정지 엔진 (하드 블록 추가)
                # =================================================================
                print("⏳ [중복 매물 검사] 팝업 출현 여부 동적 감시 시동 (최대 1.5초 대기)...")
                
                # 🎯 [치료 핵심] 기존 선택형 팝업과 신규 절대차단형(하드블록) 팝업 제목을 OR(|) 연산으로 동시 감시합니다.
                dup_title_xpath = "//h2[text()='중복 매물이 아닌지 확인해주세요'] | //h2[text()='중복 매물은 올릴 수 없어요']"
                
                try:
                    # 두 팝업 중 하나가 나타날 때까지 최대 1.5초 동적 대기
                    detected_el = WebDriverWait(driver, 1.5).until(
                        EC.presence_of_element_located((By.XPATH, dup_title_xpath))
                    )
                    popup_text = detected_el.text.strip()
                    print(f"⚠️  [중복 매물 경고 감지] 화면에 팝업 제동 장치 발동 완료 ➡️ 문구: '{popup_text}'")
                    
                    # ---------------------------------------------------------
                    # 상황 1: 당근마켓 정책상 완전히 업로드가 거부되는 하드 블록 팝업일 때
                    # ---------------------------------------------------------
                    if popup_text == "중복 매물은 올릴 수 없어요":
                        최상단알림창(
                            "🚨 중개소 내에 이미 등록된 동일 중복 매물이 존재합니다!\n\n"
                            "당근마켓 보안 정책상 더 이상 등록을 진행할 수 없는 락(Lock) 상태입니다.\n"
                            "당근 창에서 [확인]을 누르고 주소를 다른 곳으로 수정하시거나,\n"
                            "해당 매크로 프로그램을 종료해 주세요.",
                            title="❌ 중복 등록 절대 불가 (하드 블록)"
                        )
                    
                    # ---------------------------------------------------------
                    # 상황 2: 기존의 처리 방식을 물어보는 양방향 선택형 팝업일 때
                    # ---------------------------------------------------------
                    else:
                        최상단알림창(
                            "중복매물을 처리방식을 결정하고 확인버튼을 클릭하세요.\n\n"
                            "※ 당근마켓 화면에서 [같은 매물이에요] 또는 [다른 매물이에요] 중\n"
                            "원하시는 처리 방식을 마우스로 직접 클릭하신 뒤,\n"
                            "이 안내창의 [확인]을 눌러 계속 진행해 주세요.",
                            title="⚠️ 중복 매물 확인 필요"
                        )
                    
                    print("➡️  소장님의 수동 팝업 처리 검수가 확인되었습니다. 다음 단계 가격 입력을 진행합니다.")
                    time.sleep(0.5) # 팝업이 스르륵 닫히는 미세 애니메이션 버퍼 시간
                    
                except TimeoutException:
                    # 1.5초 동안 기다려도 어떤 중복 팝업도 안 나타나면 '깨끗한 매물'로 확정 판정
                    print("ℹ️  중복 매물 경고 없음. 깨끗한 주소이므로 지체 없이 즉시 통과합니다.")
            else:
                print("⚠️  [상세 주소] 건너뜀 -> DB에 호실(room_num) 데이터가 없습니다.")

            # =================================================================
            # 🥇 [순서 교정 - 1순위] 5-3. 매물 종류 선택 드롭다운 (시간차 방어 버전)
            # =================================================================
            # 💡 지번 미노출 체크박스를 화면에 탄생시키기 위해 매물 종류를 먼저 결정합니다.
            print(f"🏢 [매물 종류 분석] 당근 규격 조준 대상: '{karrot_type}'")
            try:
                # 🚀 [버그 해결] 주소창이 닫힌 후 메인 폼이 브라우저에 그려질 때까지 최대 3초간 실시간 동적 대기합니다.
                # 보내주신 HTML 구조에 맞춰 button 바로 옆에 붙은 div 태그를 정밀 타격합니다.
                current_value_xpath = "//button[@name='salesType']/following-sibling::div"
                current_value_el = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, current_value_xpath))
                )
                current_text = current_value_el.text.strip()
                print(f"   .. 현재 화면에 선택되어 있는 값: '{current_text}'")
                
                # DB 목표값과 현재 화면의 기본값이 이미 같다면 드롭다운을 열지 않고 패스합니다.
                if current_text == karrot_type:
                    print(f"ℹ️  [매물 종류] 이미 기본값이 '{karrot_type}'으로 일치하여 '0초'만에 통과합니다.")
                else:
                    # 값이 다를 때만 드롭다운 버튼 클릭 실행
                    dropdown_trigger = driver.find_element(By.NAME, "salesType")
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", dropdown_trigger)
                    time.sleep(0.1)
                    
                    driver.execute_script("arguments[0].click();", dropdown_trigger)
                    print("   .. 드롭다운 버튼 자바스크립트 강제 클릭 성공 (옵션 목록 활성화)")
                    time.sleep(0.4) # 애니메이션 레이어가 완전히 열릴 때까지 미세 대기
                    
                    # 팝업 박스 내부의 진짜 선택 단추만 조준 사격
                    dropdown_option_xpath = f"//div[@role='listbox' or @role='dialog' or contains(@class, 'popover')]//button[contains(., '{karrot_type}')] | //button[text()='{karrot_type}' and not(@name='salesType')]"
                    
                    option_btn = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, dropdown_option_xpath))
                    )
                    
                    driver.execute_script("arguments[0].click();", option_btn)
                    print(f"✅ [매물 종류 설정 완료] 드롭다운에서 '{karrot_type}' 최종 선택 완료")
                    
                    # 카테고리가 비주거용으로 바뀌면서 지번 미노출 체크박스가 완전히 그려질 시간 부여
                    time.sleep(0.4) 
            except Exception as e:
                print(f"❌ [매물 종류 드롭다운 제어 실패] -> 에러 원인: {e}")

            # =================================================================
            # 🥈 [순서 교정 - 2순위] 5-2-C. 비주거용 매물 지번 미노출 체크박스 제어
            # =================================================================
            # 💡 상단에서 '상가' 선택이 끝났으므로 이제 안전하게 체크박스를 저격할 수 있습니다.
            if object_type != '주거용':
                print(f"🔒 [주소 노출 제어] 매물 종류가 '{object_type}'(비주거용)이므로 지번 숨김을 진행합니다.")
                try:
                    hide_addr_xpath = "//input[@name='isHideAddress']/parent::label"
                    addr_cb_label = wait.until(EC.presence_of_element_located((By.XPATH, hide_addr_xpath)))
                    
                    if addr_cb_label.get_attribute("data-checked") is None:
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", addr_cb_label)
                        time.sleep(0.2)
                        addr_cb_label.click()
                        print("   .. ✅ [주소 설정] '지번은 미노출할게요.' 체크박스 자동 선택 성공")
                        time.sleep(0.2)
                    else:
                        print("   .. ℹ️ [주소 설정] '지번은 미노출할게요.' 이미 기본적으로 체크되어 있어 패스합니다.")
                except Exception as addr_cb_err:
                    print(f"   .. ❌ [주소 설정] 지번 미노출 체크박스 제어 실패 -> {addr_cb_err}")
                    failed_fields.append("• 지번 미노출 체크박스 선택 실패")
            else:
                print("ℹ️  [주소 노출 제어] 주거용 매므로 지번을 정상 노출합니다 (체크박스 패스).")

            # =================================================================
            # 🏢 [리팩토링] 건축물용도 자동 주입 엔진 (공용 유틸리티 함수 전면 이식)
            # =================================================================
            if building_purpose:
                try:
                    # 1) 🎯 [중앙 집중] 공용 함수를 호출하여 복잡한 건축법 면적 계산 및 키워드 매핑을 단 한 줄로 해결합니다.
                    mapped_purpose = 건축법상건축물용도로변환(building_purpose, area_private, 'true')

                    # 2) 최종 실무 안전 가드레일(Fallback) - 매칭 실패 시 기존과 동일하게 제2종 근린생활시설 지정
                    if not mapped_purpose:
                        mapped_purpose = "제2종 근린생활시설"
                        print(f"   .. ⚠️ 공용 함수 매칭 실패로 가드레일 용도({mapped_purpose})를 임시 채택합니다.")
                    else:
                        print(f"   .. 🎯 공용 함수 분석 성공 ➡️ 대장상 원본:({building_purpose}) ➡️ 최종 정제 용도: [{mapped_purpose}]")

                    # 3) 드롭다운 버튼 조준 및 클릭하여 목록 레이어 열기
                    trigger_btn = wait.until(EC.element_to_be_clickable((By.NAME, "buildingUsage")))
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", trigger_btn)
                    time.sleep(0.1)
                    trigger_btn.click()
                    print("   .. 건축물 용도 드롭다운 레이어 활성화 완료")
                    time.sleep(0.3)
                    
                    # 4) 최종 선택지 클릭 처리 (공백 무력화 내장)
                    clean_target = mapped_purpose.replace(" ", "")
                    option_xpath = f"//div[contains(@class, 'absolute')]//button[translate(text(), ' ', '')='{clean_target}']"
                    
                    try:
                        target_option = wait.until(EC.element_to_be_clickable((By.XPATH, option_xpath)))
                        target_option.click()
                        print(f"✅ [건축물용도] 최종 UI 선택 완료 ➡️ 당근 선택지:({mapped_purpose})")
                    except Exception as click_err:
                        print(f"   .. ⚠️ 화면에 [{mapped_purpose}] 버튼이 없습니다. 수동 선택 모드로 전환합니다.")
                        pyautogui.alert(
                            f"■ DB에 입력된 용도: {building_purpose}\n"
                            f"■ 시스템 추천 용도: {mapped_purpose}\n\n"
                            f"당근마켓 목록에서 알맞은 건축물 용도를 '직접 마우스로 클릭'해 주신 뒤,\n"
                            f"이 알림창의 [확인]을 눌러 계속 진행해 주세요."
                        )
                    time.sleep(0.2)
                except Exception as e:
                    print(f"❌ [건축물용도] '{building_purpose}' 제어 도중 예상치 못한 치명적 오류 발생 -> {e}")
                    failed_fields.append(f"• 건축물용도({building_purpose}) 매핑 실패")
            else:
                failed_fields.append(f"• 건축물용도(building_purpose)값 없음")

            # =================================================================
            # 7. 기존 텍스트 필드 입력 수행 (소수점 자릿수 비례 연산 고도화 패치)
            # =================================================================
            # 💡 [비율 연산 고도화] 주거용 물건인데 DB에 전용면적이 없을 경우 공식 기반 자동 분배
            if object_type == '주거용' and (not area_private or str(area_private).strip() in ["", "0", "None"]):
                
                try:
                    r_cnt_clean = str(room_cnt).replace('룸', '').strip()
                    r_cnt = float(r_cnt_clean) if r_cnt_clean else 1.0
                except ValueError:
                    r_cnt = 1.0 # 파싱 실패 시 기본 1룸 처리
                    
                # 최소 방 개수 안전선 고정 (0룸 이하 방지)
                if r_cnt < 1.0:
                    r_cnt = 1.0
                    
                # 💡 [핵심 공식] 구간별 선형 비례 연산 (Linear Interpolation)
                if r_cnt <= 3.0:
                    # 1룸(20㎡) ~ 3룸(60㎡) 구간은 0.1룸당 정확히 2㎡씩 정비례 증가
                    calc_area = r_cnt * 20
                else:
                    # 3룸(60㎡) 초과 구간은 가중치를 높여 4룸 기준인 85㎡에 수렴하도록 연산
                    calc_area = 60 + (r_cnt - 3.0) * 25
                    
                # 소수점 깔끔하게 정수형태 문자로 변환 (예: 1.1룸 -> "22")
                area_private = str(int(round(calc_area)))
                print(f"📐 [비율 면적 구제] 주거용 전용면적 누락 -> 공식 적용({r_cnt}룸) 임의 부여: {area_private}㎡")

            # 💡 [세트 연산] 공급면적도 비어있다면, 결정된 전용면적의 1.3배로 연산
            if object_type == '주거용' and (not area_supply or str(area_supply).strip() in ["", "0", "None"]) and area_private:
                try:
                    area_supply = str(round(float(area_private) * 1.3, 1))
                    print(f"📐 [비율 면적 구제] 주거용 공급면적 누락 -> 전용 기반 자동 연산(1.3배): {area_supply}㎡")
                except Exception as area_err:
                    print(f"⚠️  [면적 구제 실패] 공급면적 연산 오류 -> {area_err}")
            time.sleep(0.3)
            # [당근 폼 입력 진행]
            # [당근 폼 입력 진행]
            inject_input("area", area_private, "전용 면적")
            
            if karrot_type != "토지":
                # 🎯 [수정 핵심] 매물종류가 '건물'일 때는 공급면적 입력창이 UI에서 증발하므로, 
                # 타임아웃 에러 및 실패 리포트(failed_fields)가 누적되는 것을 방지하기 위해 분기 처리합니다.
                if karrot_type != "건물":
                    inject_input("supplyArea", area_supply, "공급 면적")
                else:
                    inject_input("supplyArea", area_private, "공급 면적")

            # =================================================================
            # 6. [최종 고도화] 당근 전용 거래유형(단기/월세) 지능형 판독 및 가격 엔진 (미만 규칙 전면 교정)
            # =================================================================
            if trade_type:
                # 1) 최소 계약기간 정수형 숫자 추출 (단위 제거 및 예외 가드)
                try:
                    term_months = int(re.sub(r'\D', '', str(request_term1))) if request_term1 else 12
                except:
                    term_months = 12

                print(f"💰 [가격 설정] DB 원본 거래유형 분석: '{trade_type}' / 검출된 최소계약기간: {term_months}개월")
                
                # 2) DB 다중 임대료 세트 수집 (보증금/월세가 모두 0 이상인 정상 세트만 필터링)
                price_sets = []
                raw_pairs = [
                    (deposit, rent, "1세트"),
                    (deposit2, rent2, "2세트"),
                    (deposit3, rent3, "3세트")
                ]
                for dep_val, rent_val, label in raw_pairs:
                    try:
                        if dep_val is not None and rent_val is not None:
                            d_num = float(str(dep_val).strip())
                            r_num = float(str(rent_val).strip())
                            if d_num >= 0 and r_num >= 0:
                                price_sets.append((d_num, r_num, label))
                    except ValueError:
                        continue

                # 3) 🎯 [교정 핵심] 당근 단기 매물 조건 충족 여부 전수 조사 (이상 ➡️ 미만으로 체질 개선)
                is_short_term = False
                target_deposit = None
                target_rent = None
                chosen_label = "없음"

                if term_months < 12:
                    for d_num, r_num, label in price_sets:
                        # 🚀 소장님 정정 반영: 단기 방은 보증금이 월세의 3배 '미만'이어야 함
                        if d_num < (r_num * 3):
                            is_short_term = True
                            target_deposit = d_num
                            target_rent = r_num
                            chosen_label = label
                            break

                # 4) 체크박스 타겟 목록 리스트 생성 (DB가 월세 세팅이고 단기조건 충족시 '단기' 명찰로 강제 치환)
                target_types = [t.strip() for t in trade_type.split(',') if t.strip()]
                
                if "월세" in target_types:
                    if is_short_term:
                        print(f"   .. 🎯 [단기 판정 성공] 최소계약기간({term_months}개월 < 12개월) 및 금액 조건(보증금 {int(target_deposit)} < 월세 {int(target_rent)} x 3) 모두 충족!")
                        print(f"   .. 당근마켓 거래 규격을 [월세] ➡️ [단기] 체크박스로 강제 우회 변경합니다. (채택: {chosen_label})")
                        target_types = ["단기" if t == "월세" else t for t in target_types]
                    else:
                        print(f"   .. ℹ️  [일반 월세 판정] 단기 조건 불충족으로 정식 월세 규격을 유지합니다.")
                        print(f"      👉 판독 이유 : 최소계약기간이 12개월 이상이거나, 보증금이 월세의 3배 이상이라 일반 장기 계약으로 분류됨.")
                        print(f"      👉 현재 데이터 : 판독된 계약기간={term_months}개월 / 입력된 보증금={deposit}만 / 월세={rent}만 (단기 상한선인 보증금 {int(float(rent)*3 if rent else 0)}만 원 이상)")
                        
                        if price_sets:
                            target_deposit = price_sets[0][0]
                            target_rent = price_sets[0][1]
                        else:
                            target_deposit = float(deposit) if deposit else 0
                            target_rent = float(rent) if rent else 0

                # 5) 쉼표(,)로 연결된 모든 최종 대상 체크박스 각각 전부 클릭 활성화
                for t_name in target_types:
                    try:
                        cb_xpath = f"//span[contains(@class, 'seed-checkbox__label') and text()='{t_name}']/parent::label"
                        cb_label = wait.until(EC.presence_of_element_located((By.XPATH, cb_xpath)))
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", cb_label)
                        time.sleep(0.1)
                        
                        if cb_label.get_attribute("data-checked") is None:
                            driver.execute_script("arguments[0].click();", cb_label)
                            print(f"   .. ✅ 거래유형 체크박스 [{t_name}] 선택 성공")
                            time.sleep(0.1)
                    except Exception as e:
                        print(f"   .. ❌ 거래유형 체크박스 [{t_name}] 클릭 실패 -> {e}")
                        failed_fields.append(f"• 거래유형 체크박스 [{t_name}] 선택 실패")

                time.sleep(0.5) # 체크박스 구동 후 하단 금액 입력 창들이 완전히 늘어날 때까지 버퍼 제공
                
                # 6) 🎯 활성화된 당근마켓 입력창에 세부 금액 정밀 기입
                if "매매" in target_types and trading_price:
                    try:
                        el = wait.until(EC.visibility_of_element_located((By.XPATH, "//span[@class='t4-bold text-fg-neutral' and text()='매매']/following::input[@type='number'][1]")))
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
                        time.sleep(0.1)
                        el.click(); el.send_keys(Keys.CONTROL + "a"); el.send_keys(Keys.BACKSPACE); el.send_keys(str(trading_price))
                        print(f"   .. ✅ [매매 - 가격] 입력 성공 -> {trading_price}")
                    except: 
                        print("   .. ❌ [매매 - 가격] 입력 실패")
                        failed_fields.append("• 매매 금액 입력 실패")

                if "전세" in target_types and deposit:
                    try:
                        el = wait.until(EC.visibility_of_element_located((By.XPATH, "//span[@class='t4-bold text-fg-neutral' and text()='전세']/following::input[@type='number'][1]")))
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
                        time.sleep(0.1)
                        el.click(); el.send_keys(Keys.CONTROL + "a"); el.send_keys(Keys.BACKSPACE); el.send_keys(str(deposit))
                        print(f"   .. ✅ [전세 - 보증금] 입력 성공 -> {deposit}")
                    except: 
                        print("   .. ❌ [전세 - 보증금] 입력 실패")
                        failed_fields.append("• 전세 보증금 입력 실패")

                # 일반 월세 창 주입
                if "월세" in target_types and target_deposit is not None:
                    try:
                        el_dep = wait.until(EC.visibility_of_element_located((By.XPATH, "//span[@class='t4-bold text-fg-neutral' and text()='월세']/following::input[@type='number'][1]")))
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el_dep)
                        time.sleep(0.1)
                        el_dep.click(); el_dep.send_keys(Keys.CONTROL + "a"); el_dep.send_keys(Keys.BACKSPACE); el_dep.send_keys(str(int(target_deposit)))
                        
                        el_rent = wait.until(EC.visibility_of_element_located((By.XPATH, "//span[@class='t4-bold text-fg-neutral' and text()='월세']/following::input[@type='number'][2]")))
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el_rent)
                        time.sleep(0.1)
                        el_rent.click(); el_rent.send_keys(Keys.CONTROL + "a"); el_rent.send_keys(Keys.BACKSPACE); el_rent.send_keys(str(int(target_rent)))
                        print(f"   .. ✅ [월세 - 보증금/임대료] 입력 성공 -> {int(target_deposit)}/{int(target_rent)}")
                        
                        if flexible_deposit == 'Y':
                            try:
                                adj_cb = driver.find_element(By.XPATH, "//span[@class='t4-bold text-fg-neutral' and text()='월세']/following::input[contains(@name, 'adjustable')]/parent::label")
                                if adj_cb.get_attribute("data-checked") is None: 
                                    driver.execute_script("arguments[0].click();", adj_cb)
                            except: pass
                    except: 
                        print("   .. ❌ [월세 - 금액] 입력 실패")
                        failed_fields.append("• 월세 보증금/임대료 입력 실패")

                # 🎯 단기 전용 입력창 주입
                if "단기" in target_types and target_deposit is not None:
                    try:
                        el_dep = wait.until(EC.visibility_of_element_located((By.XPATH, "//span[@class='t4-bold text-fg-neutral' and text()='단기']/following::input[@type='number'][1]")))
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el_dep)
                        time.sleep(0.1)
                        el_dep.click(); el_dep.send_keys(Keys.CONTROL + "a"); el_dep.send_keys(Keys.BACKSPACE); el_dep.send_keys(str(int(target_deposit)))
                        
                        el_rent = wait.until(EC.visibility_of_element_located((By.XPATH, "//span[@class='t4-bold text-fg-neutral' and text()='단기']/following::input[@type='number'][2]")))
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el_rent)
                        time.sleep(0.1)
                        el_rent.click(); el_rent.send_keys(Keys.CONTROL + "a"); el_rent.send_keys(Keys.BACKSPACE); el_rent.send_keys(str(int(target_rent)))
                        print(f"   .. ✅ [단기 - 예치금/월세] 입력 성공 -> {int(target_deposit)}/{int(target_rent)}")
                    except: 
                        print("   .. ❌ [단기 - 금액] 입력 실패")
                        failed_fields.append("• 단기 금액 입력 실패")
                    
                if "연세" in target_types and deposit:
                    try:
                        el_dep = wait.until(EC.visibility_of_element_located((By.XPATH, "//span[@class='t4-bold text-fg-neutral' and text()='연세']/following::input[@type='number'][1]")))
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el_dep)
                        time.sleep(0.1)
                        el_dep.click(); el_dep.send_keys(Keys.CONTROL + "a"); el_dep.send_keys(Keys.BACKSPACE); el_dep.send_keys(str(deposit))
                        
                        el_rent = wait.until(EC.visibility_of_element_located((By.XPATH, "//span[@class='t4-bold text-fg-neutral' and text()='연세']/following::input[@type='number'][2]")))
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el_rent)
                        time.sleep(0.1)
                        el_rent.click(); el_rent.send_keys(Keys.CONTROL + "a"); el_rent.send_keys(Keys.BACKSPACE); el_rent.send_keys(str(rent))
                        print(f"   .. ✅ [연세 - 보증금/임대료] 입력 성공 -> {deposit}/{rent}")
                    except: 
                        print("   .. ❌ [연세 - 금액] 입력 실패")
                        failed_fields.append("• 연세 보증금/임대료 입력 실패")
            else:
                print("⚠️  [거래 유형] 건너뜀 -> DB에 거래 유형 정보가 없습니다.")
            
            # =================================================================
            # 6-B. [정밀 매핑] 상업용 매물 권리금 조건별 자동 입력 엔진 (최종 보정)
            # =================================================================
            if object_type == '상업용':
                print(f"💰 [권리금 설정] 상업용 매물 분석 시동 (상태:{premium_exist} / 금액:{premium})")
                try:
                    # 0) 🎯 [핵심 패치] 금액 데이터에서 한글('협의만' 등)을 제거하고 순수 숫자만 추출하여 유효성 판별
                    premium_digits = re.sub(r'\D', '', str(premium)) if premium else ""
                    has_valid_price = premium_digits.isdigit() and int(premium_digits) > 0

                    # 1) 권리금 섹션 타이틀로 화면 스크롤 이동
                    premium_section = driver.find_element(By.XPATH, "//h2[text()='권리금']")
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", premium_section)
                    time.sleep(0.3)

                    # 2) 소장님이 지시하신 3대 조건 정밀 분기 제어 가동
                    # ---------------------------------------------------------
                    # 분기 A: 권리금이 [있음] 이고, 실제 유효한 [숫자 금액]이 존재할 때
                    # ---------------------------------------------------------
                    if premium_exist == '있음' and has_valid_price:
                        print(f"   .. ➡️ [조건 A] 정상 권리금 매물로 판단되어 금액({premium_digits}만)을 주입합니다.")
                        inject_input("premiumMoney", premium_digits, "권리금 금액창")
                        
                        if premium_content and str(premium_content).strip() not in ["", "None"]:
                            inject_input("premiumMoneyDescription", str(premium_content), "권리금 설명창")
                    
                    # ---------------------------------------------------------
                    # 분기 B: [있음인데 금액이 문자/공백] 이거나, 아예 상태가 [미확인] 일 때
                    # ➡️ 소장님 지시사항: '협의 가능' 체크 후 무조건 숫자 '0' 주입!
                    # ---------------------------------------------------------
                    elif (premium_exist == '있음' and not has_valid_price) or premium_exist == '미확인':
                        print("   .. ➡️ [조건 B] 권리금 미확인이거나 금액이 불분명하여 [협의 가능 + 0원] 강제 주입을 실행합니다.")
                        negotiable_xpath = "//span[text()='협의 가능']/parent::label"
                        negotiable_label = wait.until(EC.presence_of_element_located((By.XPATH, negotiable_xpath)))
                        
                        if negotiable_label.get_attribute("data-checked") is None:
                            negotiable_label.click()
                            print("   .. ✅ [협의 가능] 체크박스 선택 성공")
                            time.sleep(0.2)
                        else:
                            print("   .. ℹ️ [협의 가능] 이미 체크되어 있어 패스합니다.")

                        # 문자열('협의만')을 완전 소거하고 규격에 맞는 숫자 "0"을 확실하게 박아줍니다.
                        inject_input("premiumMoney", "0", "권리금 금액창 (협의가능)")
                        
                        if premium_content and str(premium_content).strip() not in ["", "None"]:
                            inject_input("premiumMoneyDescription", str(premium_content), "권리금 설명창")
                    
                    # ---------------------------------------------------------
                    # 분기 C: 권리금 상태가 명확하게 [없음] 일 때
                    # ---------------------------------------------------------
                    elif premium_exist == '없음':
                        print("   .. ➡️ [조건 C] 권리금 상태가 '없음'이므로 [권리금 없음] 체크박스를 켭니다.")
                        no_premium_xpath = "//span[text()='권리금 없음']/parent::label"
                        no_premium_label = wait.until(EC.presence_of_element_located((By.XPATH, no_premium_xpath)))
                        
                        if no_premium_label.get_attribute("data-checked") is None:
                            no_premium_label.click()
                            print("   .. ✅ [권리금 없음] 선택 성공")
                            time.sleep(0.2)
                            
                except Exception as p_err:
                    print(f"❌ [권리금 섹션 제어 실패] -> 원인: {p_err}")
            else:
                print("ℹ️  [권리금 설정] 상업용 물건이 아니므로 권리금 입력을 건너뜁니다.")
            
            if approval_date:
                app_date_str = str(approval_date).strip()
                if len(app_date_str) == 8 and "-" not in app_date_str:
                    app_date_str = f"{app_date_str[:4]}-{app_date_str[4:6]}-{app_date_str[6:]}"
                inject_input("buildingApprovalDate", app_date_str, "사용승인일")

            # =================================================================
            # 🌱 [신설] 토지 매물 전용 특수 필드 자동화 입력 엔진 (지목/용도지역)
            # =================================================================
            if karrot_type == "토지":
                print("🌱 [토지 옵션 설정] 지목 및 용도지역 자동 분석을 시작합니다.")
                
                # [1단계] 토지 종류 (지목 - landType) 매핑 및 라디오 버튼 타격
                jimok = land_data.get('representing_jimok', '').strip()
                if jimok:
                    # 당근 UI 전용 명칭 보정 매칭 ("대" ➡️ "대(垈)")
                    target_jimok = "대(垈)" if jimok == "대" else jimok
                    print(f"   .. 🌾 지목 분석 결과: DB 원본({jimok}) ➡️ 당근 선택지 명칭: [{target_jimok}]")
                    
                    try:
                        jimok_xpath = f"//span[contains(@class, 'seed-radio__label') and text()='{target_jimok}']/parent::label"
                        jimok_element = wait.until(EC.presence_of_element_located((By.XPATH, jimok_xpath)))
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", jimok_element)
                        time.sleep(0.1)
                        jimok_element.click()
                        print(f"   .. ✅ 토지종류 [{target_jimok}] 라디오 버튼 선택 성공")
                    except Exception as jimok_err:
                        print(f"   .. ❌ 토지종류 [{target_jimok}] 선택 실패 -> {jimok_err}")
                        failed_fields.append(f"• 토지종류({target_jimok}) 선택 실패")

                # [2단계] 용도지역 (landPurpose) 매핑 및 라디오 버튼 타격
                db_purpose = land_data.get('land_purpose', land_data.get('representing_purpose', '')).strip()
                if db_purpose:
                    target_purpose = ""
                    if "농림" in db_purpose:
                        target_purpose = "농림지역"
                    elif "관리" in db_purpose:
                        target_purpose = "관리지역"
                    elif "자연환경" in db_purpose:
                        target_purpose = "자연환경보전지역"
                    elif any(kw in db_purpose for kw in ["주거", "상업", "공업", "녹지", "도시"]):
                        target_purpose = "도시지역"
                    
                    if target_purpose:
                        print(f"   .. 🗺️ 용도지역 분석 결과: DB 원본({db_purpose}) ➡️ 당근 선택지 명칭: [{target_purpose}]")
                        try:
                            purpose_xpath = f"//span[contains(@class, 'seed-radio__label') and text()='{target_purpose}']/parent::label"
                            purpose_element = wait.until(EC.presence_of_element_located((By.XPATH, purpose_xpath)))
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", purpose_element)
                            time.sleep(0.1)
                            purpose_element.click()
                            print(f"   .. ✅ 용도지역 [{target_purpose}] 라디오 버튼 선택 성공")
                        except Exception as purp_err:
                            print(f"   .. ❌ 용도지역 [{target_purpose}] 선택 실패 -> {purp_err}")
                            failed_fields.append(f"• 용도지역({target_purpose}) 선택 실패")
                    else:
                        print(f"   .. ⚠️ DB 용도지역 명칭({db_purpose})이 당근마켓 4대 표준 규격에 매칭되지 않아 스킵합니다.")

            # =================================================================
            # [핵심 추가] 상업용 매물 욕실(화장실) 조건별 자동 매핑 로직
            # =================================================================
            if object_type == '상업용':
                # 1) DB에 욕실수(room_bcount) 데이터가 아예 없거나 빈 값인 경우 검사
                if not bath_cnt or str(bath_cnt).strip() in ["", "0", "None"]:
                    # 2) 호실 옵션(room_option)에 '화장실' 문구가 들어있는지 확인
                    if room_option and '화장실' in str(room_option):
                        bath_cnt = "1"
                        print("🚽 [욕실 분석] 상업용 물건 욕실수 누락 -> 옵션에 '화장실'이 포함되어 '1'을 자동 입력합니다.")
                    # 3) 그 외 아무 조건도 없다면 '0' 처리
                    else:
                        bath_cnt = "0"
                        print("🚽 [욕실 분석] 상업용 물건 욕실수 누락 및 옵션 데이터 없음 -> '0'을 자동 입력합니다.")
                else:
                    print(f"🚽 [욕실 분석] 상업용 물건 DB 본래의 욕실수 데이터를 유지합니다 -> {bath_cnt}개")
            
            # [당근 폼 주입 진행]
            inject_input("roomCnt", room_cnt, "방 개수")
            inject_input("bathroomCnt", bath_cnt, "욕실 개수") # 👈 위에서 가공된 bath_cnt가 안전하게 주입됩니다.
            inject_input("topFloor", floor_top, "전체 층수")
            
            if floor_current:
                try:
                    inject_input("floor", str(abs(int(floor_current))), "해당 층수")
                except:
                    inject_input("floor", floor_current, "해당 층수")

            # =================================================================
            # 7-A. [고도화] 호실/건물 방향 드롭다운 자동 선택 (건물 전체 방향 예외 처리)
            # =================================================================
            target_direction = ""

            # 🎯 [소장님 지시 규칙] 매물 종류가 '건물'일 경우 건물대장의 방향(building_direction)을 최우선 적용
            # pyautogui.alert(f"karrot_type:{karrot_type}")
            if karrot_type == "건물":
                b_dir = building_data.get('building_direction', '')
                if b_dir:
                    target_direction = str(b_dir).strip()
                    print(f"🧭 [방향 설정] '건물' 매물이므로 건물대장 고유 방향 데이터([{target_direction}])를 채택합니다.")
            else:
                # 일반 호실별 매물일 때는 기존대로 개별 호실 방향(room_direction) 채택
                if room_direction:
                    target_direction = str(room_direction).strip()

            # 당근마켓 규격 맞춤형 '향' 접미사 자동 보정 시스템 (예: '동' ➡️ '동향')
            # pyautogui.alert(f"target_direction:{target_direction}")
            if target_direction:
                if not target_direction.endswith('향') and target_direction in ['남', '동', '서', '북', '남동', '남서', '북동', '북서']:
                    target_direction += '향'
            elif object_type == '주거용':
                target_direction = "남향"
                print("ℹ️  [방향 설정] DB에 방향 데이터가 없으나 주거용 물건이므로 '남향'으로 기본값을 적용합니다.")

            if target_direction:
                print(f"🧭 [방향 설정] 최종 선택할 당근 규격 방향: '{target_direction}'")

                try:
                    direction_trigger = wait.until(EC.presence_of_element_located((By.NAME, "buildingOrientation")))
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", direction_trigger)
                    
                    direction_trigger.click()
                    print("   .. 방향 드롭다운 목록 활성화 성공")
                    
                    direction_option_xpath = f"//button[text()='{target_direction}']"
                    option_btn = wait.until(EC.element_to_be_clickable((By.XPATH, direction_option_xpath)))
                    option_btn.click()
                    
                    print(f"✅ [방향 설정 완료] '{target_direction}' 선택 성공")
                except Exception as e:
                    print(f"❌ [방향 드롭다운 제어 실패] -> 원인: {e}")
            else:
                print("⚠️  [방향] 건너뜀 -> DB에 방향 데이터가 없고 주거용 물건도 아닙니다.")

            # =================================================================
            # 7-A-2. [핵심 추가] 층 정보 하단 특수 체크박스 제어 (지하/반지하/건물 전체)
            # =================================================================
            try:
                is_basement = room_important and any(kw in str(room_important) for kw in ['지하층', '지하'])
                is_semi_basement = room_important and '반지하' in str(room_important)
                is_full_building = building_important and '통임대' in str(building_important)

                floor_checkboxes = []
                if is_basement: floor_checkboxes.append("지하")
                if is_semi_basement: floor_checkboxes.append("반지하")
                if is_full_building: floor_checkboxes.append("건물 전체")

                if floor_checkboxes:
                    print(f"🏢 [층 특수 조건 분석] 체크 대상 항목: {floor_checkboxes}")
                    for cb_label in floor_checkboxes:
                        cb_xpath = f"//label[contains(@class, 'seed-checkbox__root') and not(@data-checked)]//span[text()='{cb_label}']"
                        try:
                            cb_element = driver.find_element(By.XPATH, cb_xpath)
                            cb_element.click()
                            print(f"   .. ✅ 층 체크박스 [{cb_label}] 선택 성공")
                        except:
                            print(f"   .. ℹ️  층 체크박스 [{cb_label}] 이미 체크되어 있거나 찾을 수 없음")
                            
            except Exception as floor_cb_err:
                print(f"❌ [층 체크박스 제어 실패] -> 원인: {floor_cb_err}")

            # =================================================================
            # 7-B. [고도화] 주차 정보 선택 및 총/세대당 주차대수 자동 주입
            # =================================================================
            is_parking_available = False
            
            if building_parking == '있음' or '주차' in str(building_option):
                is_parking_available = True
                
            if building_pn:
                try:
                    if int(building_pn) > 0:
                        is_parking_available = True
                except ValueError:
                    if any(keyword in str(building_pn) for keyword in ['가능', '있음', '유']):
                        is_parking_available = True

            parking_status = "가능" if is_parking_available else "불가능"
            print(f"🚗 [주차 정보 분석] 주차장 유무:{building_parking} / 대수:{building_pn} -> 당근 규격: '{parking_status}'")

            try:
                parking_xpath = f"//span[text()='주차']/ancestor::div[contains(@class, 'items-start')][1]//span[text()='{parking_status}']"
                parking_radio_label = driver.find_element(By.XPATH, parking_xpath)
                
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", parking_radio_label)
                parking_radio_label.click()
                print(f"✅ [주차 정보 설정] 라디오 버튼 '{parking_status}' 클릭 성공")
                
                if parking_status == "가능":
                    inject_input("availableTotalParkingSpots", building_pn, "총 주차대수")

                    if building_pn and building_hhld:
                        try:
                            pn_int = int(building_pn)
                            hhld_int = int(building_hhld)
                            
                            if hhld_int > 0:
                                parking_per_hhld = round(pn_int / hhld_int, 2)
                                inject_input("availableParkingSpotsV2", parking_per_hhld, "세대당 주차대수")
                            else:
                                print("⚠️  [세대당 주차대수] 건너뜀 -> DB의 세대수(building_hhld)가 0입니다.")
                        except ValueError:
                            print("⚠️  [세대당 주차대수] 건너뜀 -> 주차대수나 세대수가 숫자가 아닙니다. (계산 불가)")
                    else:
                        print("⚠️  [세대당 주차대수] 건너뜀 -> DB에 세대수(building_hhld) 데이터가 없습니다.")

            except Exception as e:
                print(f"❌ [주차 정보 선택 실패] -> 원인: {e}")

            if object_type == '주거용':
                # =================================================================
                # 7-E. [핵심 추가] PHP 서버 로직 기반 시설 옵션 치환 및 자동 체크 (오타 패치)
                # =================================================================



                print(f"🛠️  [시설 옵션 분석] 매칭된 당근 옵션 목록: {matched_options}")

                try:
                    facility_section = driver.find_element(By.XPATH, "//h2[text()='시설 정보']")
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", facility_section)

                    for opt in matched_options:
                        unchecked_xpath = f"//label[contains(@class, 'seed-checkbox__root') and not(@data-checked)]//span[text()='{opt}']"
                        
                        try:
                            checkbox_label = driver.find_element(By.XPATH, unchecked_xpath)
                            checkbox_label.click()
                            print(f"   .. ✅ [{opt}] 체크박스 자동 선택 성공")
                        except:
                            print(f"   .. ℹ️  [{opt}] 이미 체크되어 있거나 건너뜀")

                    print("✅ [시설 정보 옵션 설정 완료] 모든 체크박스 반영 시도가 끝났습니다.")

                except Exception as e:
                    print(f"❌ [시설 정보 옵션 설정 실패] -> 원인: {e}")

                # =================================================================
                # 7-F. 특약 조건 기반 반려동물 및 대출 항목 자동 선택
                # =================================================================
                pet_status = "확인 필요"
                loan_status = "확인 필요"
                terms_str = str(room_terms)

                if "애완동물가능" in terms_str:
                    pet_status = "가능"
                elif "애완동물금지" in terms_str:
                    pet_status = "불가능"

                if "대출가능" in terms_str:
                    loan_status = "가능"

                print(f"🐾 [반려동물 분석] 특약 기반 -> 당근 규격: '{pet_status}'")
                print(f"💳 [대출 여부 분석] 특약 기반 -> 당근 규격: '{loan_status}'")

                try:
                    pet_xpath = f"//span[text()='반려동물']/ancestor::div[contains(@class, 'flex-col') or contains(@class, 'gap-x3')][1]//span[text()='{pet_status}']"
                    pet_radio = driver.find_element(By.XPATH, pet_xpath)
                    
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", pet_radio)
                    pet_radio.click()
                    print(f"   .. ✅ [반려동물] '{pet_status}' 라디오 버튼 클릭 성공")
                except Exception as e:
                    print(f"   .. ❌ [반려동물] 선택 실패 -> 원인: {e}")

                try:
                    loan_xpath = f"//span[text()='대출']/ancestor::div[contains(@class, 'flex-col') or contains(@class, 'gap-x3')][1]//span[text()='{loan_status}']"
                    loan_radio = driver.find_element(By.XPATH, loan_xpath)
                    
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", loan_radio)
                    loan_radio.click()
                    print(f"   .. ✅ [대출] '{loan_status}' 라디오 버튼 클릭 성공")
                except Exception as e:
                    print(f"   .. ❌ [대출] 선택 실패 -> 원인: {e}")

            # =================================================================
            # 7-G. [핵심 추가] 위반건축물 및 전입신고 불가능 체크박스 정밀 제어
            # =================================================================
            is_violation = building_important and "위반건축물" in str(building_important)
            is_no_registration = room_terms and "전입신고불가" in str(room_terms)

            print(f"⚠️  [위반건축물 분석] 건물특징 기반 -> 당근 규격: {'해당' if is_violation else '미해당'}")
            print(f"🏠 [전입신고 불가능 분석] 호실특약 기반 -> 당근 규격: {'해당' if is_no_registration else '미해당'}")

            if is_violation:
                try:
                    violation_xpath = "//span[text()='위반건축물']/ancestor::div[contains(@class, 'flex-col')][1]//label[contains(@class, 'seed-checkbox__root') and not(@data-checked)]//span[text()='해당']"
                    violation_cb = driver.find_element(By.XPATH, violation_xpath)
                    
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", violation_cb)
                    violation_cb.click()
                    print("   .. ✅ [위반건축물] '해당' 체크박스 자동 선택 성공")
                except Exception as e:
                    print(f"   .. ℹ️  [위반건축물] 이미 체크되어 있거나 선택 스킵: {e}")

            if is_no_registration:
                try:
                    no_reg_xpath = "//span[text()='전입신고 불가능']/ancestor::div[contains(@class, 'flex-col')][1]//label[contains(@class, 'seed-checkbox__root') and not(@data-checked)]//span[text()='해당']"
                    no_reg_cb = driver.find_element(By.XPATH, no_reg_xpath)
                    
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", no_reg_cb)
                    no_reg_cb.click()
                    print("   .. ✅ [전입신고 불가능] '해당' 체크박스 자동 선택 성공")
                except Exception as e:
                    print(f"   .. ℹ️  [전입신고 불가능] 이미 체크되어 있거나 선택 스킵: {e}")

            # =================================================================
            # 7-C. [순서 재정렬 - 최우선 반영] 관리비 부과 방식 분기 엔진 (최종 보정)
            # =================================================================

            print(f"💵 [관리비 분석] 여부:{request_manager} / 금액 환산:{mmoney_float}만 원 / 포함내역:{request_mlist}")

            try:
                manage_section = driver.find_element(By.XPATH, "//h2[text()='관리비']")
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", manage_section)

                # ---------------------------------------------------------
                # [분기 1] 관리비가 "별도"인 경우 (기존 유지)
                # ---------------------------------------------------------
                if request_manager == "별도":
                    if 0 < mmoney_float < 10:
                        print("   .. ➡️  부과 방식: 10만원 미만 매물이므로 [정액 관리비]를 선택합니다.")
                        click_element_by_xpath("//label[@data-value='FIXED' or contains(text(), '정액 관리비')]", "정액 관리비 탭")

                        print("   .. ➡️  [1순위 타격] '10만원 미만 혹은 의뢰인이 세부 내역 미제공' 체크박스 선택 시도...")
                        try:
                            checkbox_xpath = "//span[contains(@class, 'seed-checkbox__label') and text()='10만원 미만 혹은 의뢰인이 세부 내역 미제공']/parent::label"
                            cb_label = wait.until(EC.presence_of_element_located((By.XPATH, checkbox_xpath)))
                            
                            if cb_label.get_attribute("data-checked") is None:
                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", cb_label)
                                cb_label.click()
                                print("   .. ✅ [10만원 미만 예외 체크박스] 선(先) 체크 완료")
                            else:
                                print("   .. ℹ️  [10만원 미만 예외] 이미 기본값으로 체크되어 있습니다.")
                        except Exception as cb_err:
                            print(f"   .. ❌ [10만원 미만 예외 체크박스] 클릭 실패 -> {cb_err}")
                            failed_fields.append("• 10만원 미만 예외 체크박스 선택 실패")

                        click_element_by_xpath("//span[contains(@class, 'seed-radio__label') and text()='직전 월']", "부과기준 (직전 월)")
                        inject_input("totalManageCost", request_mmoney, "총 관리비 입력창")
                        click_element_by_xpath("//span[contains(@class, 'seed-checkbox__label') and text()='공용']", "포함항목 (공용)")
                        
                        # 🎯 [소장님 지시사항] 단순 글자 매칭을 버리고, '공용' 접두사가 붙은 공용전기/공용수도는 철저히 제외합니다.
                        if request_mlist:
                            mlist_list = [x.strip() for x in str(request_mlist).split(',') if x.strip()]
                            mapping_rules = {
                                "인터넷": "인터넷비", "수도": "수도료", "유선": "TV", "전기": "전기료", "가스": "가스비", "난방": "난방비"
                            }
                            for db_word, karrot_label in mapping_rules.items():
                                # 💡 리스트 안의 단어 중 '전기'가 포함되되, '공용'이라는 글자가 없는 정통 개별 항목일 때만 작동!
                                if any(db_word in item and "공용" not in item for item in mlist_list):
                                    cb_xpath = f"//span[contains(@class, 'seed-checkbox__label') and text()='{karrot_label}']"
                                    click_element_by_xpath(cb_xpath, f"포함항목 ({karrot_label})")
                                    time.sleep(0.1)
                    else:
                        print("   .. ➡️  부과 방식: 10만원 이상이므로 [기타 부과]를 선택합니다.")
                        click_element_by_xpath("//label[@data-value='ETC' or contains(text(), '기타 부과')]", "기타 부과 탭")

                        click_element_by_xpath("//span[contains(@class, 'seed-radio__label') and text()='직전 월']", "부과기준 (직전 월)")
                        inject_input("totalManageCost", request_mmoney, "총 관리비 입력창")
                        click_element_by_xpath("//span[contains(@class, 'seed-checkbox__label') and text()='공용']", "포함항목 (공용)")
                        
                        # 🎯 [소장님 지시사항] 10만원 이상 기타부과 섹션 내 공용전기/공용수도 차단 엔진 이식
                        if request_mlist:
                            # mlist_list = [x.strip() for x in str(request_mlist).split(',') if x.strip()]
                            mapping_rules = {
                                "인터넷": "인터넷비", "수도": "수도료", "유선": "TV", "전기": "전기료", "가스": "가스비", "난방": "난방비"
                            }
                            for db_word, karrot_label in mapping_rules.items():
                                if any(db_word in item and "공용" not in item for item in mlist_list):
                                    checkbox_xpath = f"//span[contains(@class, 'seed-checkbox__label') and text()='{karrot_label}']"
                                    click_element_by_xpath(checkbox_xpath, f"포함항목 ({karrot_label})")
                                    time.sleep(0.1)
                            # 최상단알림창("정상 클릭?")
                        try:
                            basis_radio_xpath = "//input[@value='ESTIMATED_BY_AGENT_DUE_TO_NO_OWNER_INFO']/parent::label"
                            target_radio = wait.until(EC.presence_of_element_located((By.XPATH, basis_radio_xpath)))
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", target_radio)
                            driver.execute_script("arguments[0].click();", target_radio)
                            print("✅ [세부 타입 (중개의뢰인 관리비 미제시)] 자동 선택 성공")
                        except Exception as basis_err:
                            print(f"❌ [세부 타입 선택 실패] -> 원인: {basis_err}")

                # ---------------------------------------------------------
                # 🎯 [신설 분기 2] 관리비가 월세에 "포함"된 경우 처리 시스템 (버그 수정 완료)
                # ---------------------------------------------------------
                elif request_manager == "포함":
                    print("   .. ➡️  부과 방식: 관리비가 포함된 매물이므로 [정액 관리비] 예외 세팅을 가동합니다.")
                    
                    # ① '정액 관리비' 탭 타격
                    click_element_by_xpath("//label[@data-value='FIXED' or contains(text(), '정액 관리비')]", "정액 관리비 탭")

                    # ② '10만원 미만 혹은 의뢰인이 세부 내역 미제공' 강제 체크
                    try:
                        checkbox_xpath = "//span[contains(@class, 'seed-checkbox__label') and text()='10만원 미만 혹은 의뢰인이 세부 내역 미제공']/parent::label"
                        cb_label = wait.until(EC.presence_of_element_located((By.XPATH, checkbox_xpath)))
                        if cb_label.get_attribute("data-checked") is None:
                            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", cb_label)
                            cb_label.click()
                            print("   .. ✅ [10만원 미만 예외 체크박스] 선택 성공")
                        else:
                            print("   .. ℹ️  [10만원 미만 예외] 이미 기본값으로 체크되어 있습니다.")
                    except Exception as cb_err:
                        print(f"   .. ❌ [10만원 미만 예외 체크박스] 클릭 실패 -> {cb_err}")
                        failed_fields.append("• 10만원 미만 예외 체크박스 선택 실패")

                    # ③ '직전 월' 기준 라디오 버튼 선택
                    click_element_by_xpath("//span[contains(@class, 'seed-radio__label') and text()='직전 월']", "부과기준 (직전 월)")
                    
                    # ④ '총 관리비' 입력창에 숫자 "0" 주입
                    inject_input("totalManageCost", "0", "총 관리비 입력창")
                    
                    # ⑤ 🎯 [개정] '관리비에 포함'은 줄 제목이므로 기본 '공용' 단추를 타격합니다. (기타는 체크 제외)
                    click_element_by_xpath("//span[contains(@class, 'seed-checkbox__label') and text()='공용']", "포함항목 (공용)")
                    
                    # ⑥ 🎯 의뢰서의 mlist 내역(인터넷, 수도 등)을 분석하여 해당 항목들도 함께 켜줍니다.
                    # 🎯 [소장님 지시사항] 관리비 포함 항목 내부에서도 공용전기/공용수도는 개별 체크박스를 건드리지 않게 가드를 세웁니다.
                    if request_mlist:
                        mlist_list = [x.strip() for x in str(request_mlist).split(',') if x.strip()]
                        mapping_rules = {
                            "인터넷": "인터넷비", "수도": "수도료", "유선": "TV", "전기": "전기료", "가스": "가스비", "난방": "난방비"
                        }
                        for db_word, karrot_label in mapping_rules.items():
                            if any(db_word in item and "공용" not in item for item in mlist_list):
                                cb_xpath = f"//span[contains(@class, 'seed-checkbox__label') and text()='{karrot_label}']"
                                click_element_by_xpath(cb_xpath, f"포함항목 ({karrot_label})")
                                time.sleep(0.1)

                # ---------------------------------------------------------
                # [분기 3] 그 외 '미확인', '없음' 등인 경우 -> '확인 불가' 분기 (기존 유지)
                # ---------------------------------------------------------
                else:
                    print("   .. ➡️  부과 방식: 데이터 불충분으로 [확인 불가]를 선택합니다.")
                    click_element_by_xpath("//label[@data-value='UNAVAILABLE' or contains(text(), '확인 불가')]", "확인 불가 탭")

                    combined_feats = str(building_important) + str(room_important) + str(content)
                    is_new_building = (not approval_date) or any(kw in combined_feats for kw in ['신축', '미등기', '첫입주'])

                    if object_type == '상업용' or karrot_type in ['상가', '사무실']:
                        unavailable_reason = "STORE_NOT_OFFICETEL"
                        print("   .. ➡️  확인불가사유 판정: 상업용 자산 [오피스텔 제외 상가 건물에 해당하는 경우] 도출")
                    elif karrot_type == "주택" and not is_new_building:
                        unavailable_reason = "SINGLE_HOUSE"
                        print("   .. ➡️  확인불가사유 판정: 일반 주거 주택 [단독주택] 도출")
                    else:
                        unavailable_reason = "UNREGISTERED_OR_NEW"
                        print("   .. ➡️  확인불가사유 판정: 신축/미등기 및 범용 fallback [미등기건물, 신축건물 등 관리비 내역이 확인불가한 경우] 도출")

                    try:
                        reason_xpath = f"//input[@name='manageCostUnavailableReason' and @value='{unavailable_reason}']/parent::label"
                        reason_radio = wait.until(EC.presence_of_element_located((By.XPATH, reason_xpath)))
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", reason_radio)
                        driver.execute_script("arguments[0].click();", reason_radio)
                        print(f"   .. ✅ 확인 불가 사유 [{unavailable_reason}] 최종 동 동기화 선택 성공")
                    except Exception as reason_err:
                        print(f"   .. ❌ 확인 불가 사유 라디오 버튼 조준 실패 -> 원인: {reason_err}")

                print("✅ [관리비 설정 완료] 요청하신 조건대로 매핑이 완료되었습니다.")

            except Exception as e:
                print(f"❌ [관리비 자동 입력 실패] -> 원인: {e}")

            # =================================================================
            # 7-D. PHP 서버 로직 기반 입주가능일 자동 설정
            # =================================================================
            today_str = datetime.now().strftime('%Y-%m-%d')
            print(f"📅 [입주가능일 분석] 호실상태:{room_status} / 제시일:{rdate} / 오늘:{today_str}")

            try:
                move_in_section = driver.find_element(By.XPATH, "//span[text()='입주가능일']")
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", move_in_section)

                if room_status and '공실' in str(room_status):
                    print("   .. ➡️  호실 상태가 '공실'이므로 [즉시 입주 가능] 체크박스를 클릭합니다.")
                    immediate_xpath = "//span[contains(@class, 'seed-checkbox__label') and text()='즉시 입주 가능']"
                    click_element_by_xpath(immediate_xpath, "즉시 입주 가능 체크박스")
                    
                else:
                    move_in_date_target = today_str 
                    
                    if rdate and str(rdate).strip() != '0000-00-00' and str(rdate).strip() != '':
                        rdate_str = str(rdate).strip()
                        
                        if len(rdate_str) == 8 and "-" not in rdate_str:
                            rdate_str = f"{rdate_str[:4]}-{rdate_str[4:6]}-{rdate_str[6:]}"
                        
                        if rdate_str > today_str:
                            move_in_date_target = rdate_str 
                            print(f"   .. ➡️  제시일이 미래 날짜이므로 해당 날짜를 선택합니다: {rdate_str}")
                        else:
                            print(f"   .. ➡️  제시일이 과거이거나 오늘이므로 오늘 날짜를 선택합니다: {today_str}")
                    else:
                        print(f"   .. ➡️  제시일 데이터가 없으므로 오늘 날짜로 대체합니다: {today_str}")

                    inject_input("moveInDate", move_in_date_target, "입주가능일 날짜 입력창")

                print("✅ [입주가능일 설정 완료] 성공적으로 반영되었습니다.")

            except Exception as e:
                print(f"❌ [입주가능일 자동 설정 실패] -> 원인: {e}")

            # # =================================================================
            # # 🤖 [AI 탑재] 위치 한줄평 실시간 동적 호출 및 자동 주입 (스레드 동기화)
            # # =================================================================
            # # 💡 셀레니움이 여기까지 입력하며 오느라 시간이 꽤 지났을 것입니다.
            # # 혹시 인터넷이 심각하게 느려 아직 AI가 대답을 완료하지 못했다면 최대 2초 동안만 안전하게 더 기다려줍니다.
            # if ai_thread.is_alive():
            #     print("⏳ [AI 한줄평 대기] 셀레니움이 아주 조금 빨랐네요! 한줄평 완성을 위해 최대 2초간 안전 대기합니다...")
            #     ai_thread.join(timeout=2.0) # 2.0초가 넘어가면 멈추지 않고 즉시 무시하고 진행(안전 가드)
            
            # 💡 [핵심 디버깅 패치] 'addressInfo' 뿐만 아니라 실제 당근 HTML name인 'addressDescription' 및 placeholder 기반 그물망 포커스 시도
            try:
                # 1. 입력창 찾기 (가장 높은 확률의 두 name 속성을 OR 연산으로 단번에 대기)
                one_liner_el = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@name='addressDescription' or @name='addressInfo']"))
                )
                
                # 2. 화면 중앙으로 스크롤하여 가려짐 에러 완벽 해결
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", one_liner_el)
                # time.sleep(0.2)
                
                # 3. 기존 글자 전체선택(Ctrl+A) 후 지우고 최종 AI 카피 타이핑
                one_liner_el.click()
                one_liner_el.send_keys(Keys.CONTROL + "a")
                one_liner_el.send_keys(Keys.BACKSPACE)
                time.sleep(0.1)
                one_liner_el.send_keys(str(final_one_liner))
                print(f"✅ [위치 한줄평] 입력 성공 -> {final_one_liner}")
                    
            except Exception as e:
                print(f"❌ [위치 한줄평] 입력 실패 -> {e}")

            # =================================================================
            # 7-E-2. [대개혁] 레거시 템플릿 정제 및 상세설명 지능형 조립 엔진
            # =================================================================
            # 💡 DB에 구형 서식이나 HTML 태그가 들어있어도 완벽하게 필터링하여 재가공합니다.
            db_content = str(content).strip() if content else ""
            
            # [1단계] 지저분한 HTML 태그 및 공백 문자 제거
            db_content = re.sub(r'<[^>]*>', '', db_content)
            db_content = db_content.replace('&nbsp;', ' ').replace('&amp;', '&').strip()
            
            # [2단계] 당근 규격에 맞게 단어 스왑 및 무의미한 빈 안내선(-- 보증금 등) 삭제
            db_content = db_content.replace("네이버", "당근")
            db_content = re.sub(r'--\s*(보증금|월세|관리비|전용면적).*\n?', '', db_content)
            
            # [3단계] 알맹이 데이터인 '주요특징' 구역만 영리하게 슬라이싱 추출
            if "주요특징" in db_content:
                db_content = db_content[db_content.find("주요특징"):]
            elif len(db_content) < 15:
                db_content = "" # 단순 템플릿만 있고 알맹이가 없으면 초기화
                
            # 무조건 소장님의 고도화된 스펙 시트를 베이스로 기본 빌드합니다.
            lines = []
            # 🎯 [신설] 지하층 숫자(-1, -2 등)를 '지하1층' 문구로 완벽하게 변형하는 정제 엔진
            f_clean = str(floor_current).replace('층', '').strip()
            try:
                f_int = int(f_clean)
                floor_str = f"지하{abs(f_int)}층" if f_int < 0 else f"{f_int}층"
            except ValueError:
                floor_str = f"{f_clean}층" if f_clean else ""
            desc_title = public_title
            # print(f"desc_title:{desc_title}")
            if object_type == '주거용':
                # 🎯 [소장님 지시사항] 번지수까지 완벽하게 은닉하기 위해 address 대신 순수 행정동(land_main)과 방표시를 결합합니다.
                try:
                    rc_val = float(str(room_cnt).replace('룸', '').strip())
                    room_display = str(int(rc_val)) if rc_val.is_integer() else str(rc_val)
                except:
                    room_display = str(room_cnt).replace('룸', '').strip() if room_cnt else "1"
                
                # land_main 데이터 유효성 가드레일 포함
                최종행정동 = land_main if land_main else address
                desc_title = f"{최종행정동} {room_display}룸"
            else:
                # 🎯 [상업용/비주거 보안 고도화] 비주거용 매물도 호수 앞 영문자(A, B동 등)를 깔끔하게 함께 소거합니다.
                desc_title = re.sub(r'[A-Za-z]*\d+호|\([^)]+\)', '', desc_title)
                
                # 🔒 [1차 가드] DB 상의 실제 건물명(예: 양우프라자, 모세빌딩 등)이 제목에 포함되어 있으면 직접 타격 제거
                b_name = building_data.get('building_name', '')
                if b_name and str(b_name).strip() not in ["", "None"]:
                    desc_title = desc_title.replace(str(b_name).strip(), "")
                
                # 🔒 [2차 가드] 프라자, 플라자, 센터, 스퀘어 등 실무형 상가 건물 접미사까지 패턴 차단 확장
                desc_title = re.sub(r'\S+(빌딩|타워|빌라|하우스|오피스텔|메디컬|프라자|플라자|센터|스퀘어|팩토리|몰)', '', desc_title)
                
                # 지번이나 불필요하게 떨어진 잔여 숫자 청소
                desc_title = re.sub(r'\s+\d+-\d+|\s+\d+(?!\s*층)', '', desc_title)
                
                # 🎯 [소장님 지시사항] 비주거용 지하 매물의 알파벳(B, A등) 및 '지하' 중복 글자를 원천 삭제하고 '지하층'으로 통일합니다.
                try:
                    f_val = int(str(floor_current).replace('층', '').strip())
                    is_underground = f_val < 0
                except ValueError:
                    is_underground = "지하" in str(floor_current)

                if is_underground:
                    # 🧹 제목 뒤에 외롭게 남은 호수 알파벳(B) 제거 및 기존 텍스트에 낀 '지하' 단어 청소
                    desc_title = re.sub(r'\b[A-Za-z]\b', '', desc_title) 
                    desc_title = desc_title.replace('지하', '').strip()
                    desc_title = f"{desc_title} 지하층"
                else:
                    # 지상층일 때는 기존 규칙대로 층수를 정밀 결합
                    if floor_str and floor_str not in desc_title:
                        desc_title = f"{desc_title.strip()} {floor_str}"

            # 🔒 '무명'이 포함된 단어(무명건물1, 무명호실2 등) 완전 제거
            desc_title = re.sub(r'무명\S*', '', desc_title)
            # 🧹 단어가 빠지면서 덩그러니 남은 구문 기호( , ) 정리
            desc_title = re.sub(r',\s*(?=\d+층)', '', desc_title)

            # ✨ [공백 압축] 연속된 모든 공백을 단 한 칸으로 정리
            desc_title = re.sub(r'\s+', ' ', desc_title).strip()

            lines.append(f"🌟 당근 이웃분들께 추천하는 [{desc_title}] 매물입니다! 🌟\n")
            lines.append("📌 [한눈에 보는 핵심 스펙]")

            # 동적 가격 정보 정제
            # 🎯 [신설] 공용 금액 정제 엔진을 이식하여 대형 금액을 한글 규격으로 자동 트랜스폼합니다.
            trade_details = []
            if "월세" in trade_type and deposit:
                dep_kor = 만원단위숫자금액을한글금액으로(deposit)
                rent_kor = 만원단위숫자금액을한글금액으로(rent)
                trade_details.append(f"보증금:{dep_kor} / 월세:{rent_kor}")
            elif "전세" in trade_type and deposit:
                dep_kor = 만원단위숫자금액을한글금액으로(deposit)
                trade_details.append(f"보증금:{dep_kor}")

            if "매매" in trade_type and trading_price and str(trading_price).strip() not in ["", "0", "None"]:
                price_kor = 만원단위숫자금액을한글금액으로(trading_price)
                trade_details.append(f"매매가:{price_kor}")
                
            price_summary = f"{trade_type} ({' / '.join(trade_details)})" if trade_details else trade_type

            lines.append(f"• 💰 거래 유형 : {price_summary}")
            
            # 🎯 [치료] 말뿐인 안내 단어를 지우고, 실제 0.3025를 곱해 평수를 실시간으로 계산해 붙여줍니다.
            area_details = []

            if area_private and str(area_private).strip() not in ["", "0", "None"]:
                try:
                    # 소수점이 너무 길게 늘어지는 현상을 방지하기 위해 ㎡는 둘째짜리, 평수는 첫째짜리 반올림
                    m2_priv = round(float(area_private), 2)
                    py_priv = round(m2_priv * 0.3025, 1)
                    area_details.append(f"전용 {m2_priv}㎡ ({py_priv}평)")
                except:
                    area_details.append(f"전용 {area_private}㎡")

            if area_supply and str(area_supply).strip() not in ["", "0", "None"]:
                try:
                    m2_supp = round(float(area_supply), 2)
                    py_supp = round(m2_supp * 0.3025, 1)
                    area_details.append(f"공급 {m2_supp}㎡ ({py_supp}평)")
                except:
                    area_details.append(f"공급 {area_supply}㎡")

            if area_details:
                lines.append(f"• 📐 면적 정보 : {' / '.join(area_details)}")
            
            # 🎯 [소장님 지시사항] 핵심 스펙의 방 개수는 소수점을 완전히 무력화하여 1.5룸도 정수 '1'로 표현합니다.
            if (room_cnt and str(room_cnt).strip() not in ["", "0", "None"]) or (bath_cnt and str(bath_cnt).strip() not in ["", "0", "None"]):
                try:
                    rc_val = float(str(room_cnt).replace('룸', '').strip())
                    # int()로 강제 절사하여 소수점 아래 자리를 완전히 소거합니다.
                    rc_clean = str(int(rc_val))
                except:
                    rc_clean = re.sub(r'\.\d+', '', str(room_cnt).replace('룸', '').strip())
                    
                try:
                    bc_val = float(str(bath_cnt).strip())
                    bc_clean = str(int(bc_val)) if bc_val.is_integer() else str(bc_val)
                except:
                    bc_clean = str(bath_cnt).strip()
                    
                spec_room_bath = []
                if rc_clean and rc_clean not in ["0", "None", ""]: spec_room_bath.append(f"방 {rc_clean}개")
                if bc_clean and bc_clean not in ["0", "None", ""]: spec_room_bath.append(f"욕실 {bc_clean}개")
                
                if spec_room_bath:
                    lines.append(f"• 🛌 방/욕실수 : {' / '.join(spec_room_bath)}")
            
            # 🎯 [개선] 위에서 치환된 floor_str를 재활용하여 문구 깨짐과 '층' 글자 중복을 원천 봉쇄합니다.
            f_curr = floor_str if floor_str else "문의"
            if floor_top and str(floor_top).strip() not in ["", "0", "None"]:
                lines.append(f"• 🏢 층수 위치 : 총 {floor_top}층 중 {f_curr}")
            else:
                lines.append(f"• 🏢 층수 위치 : {f_curr}")
            
            p_status = "가능" if (building_parking == '있음' or (building_pn and str(building_pn) != '0')) else "불가능"
            p_num = f"({building_pn}대 보유)" if building_pn else ""
            lines.append(f"• 🚗 주차 여부 : 주차 {p_status} {p_num}")
            
            if request_manager == "별도" and request_mmoney:
                lines.append(f"• 💵 관 리 비 : 월 {request_mmoney}만 원")
                if request_mlist: lines.append(f"  (포함 내역: {request_mlist})")
            else:
                lines.append(f"• 💵 관 리 비 : {request_manager}")
                
            lines.append(f"• 📅 입주 시기 : {room_status if room_status else '협의 입주'}\n")
            
            # 다중 조건 보증금 노출
            if (deposit2 and rent2) or (deposit3 and rent3):
                lines.append("   [※ 다양한 보증금 조건 선택 가능]")
                lines.append(f"   • 조건 A : 보증금 {deposit}만 원 / 월세 {rent}만 원 (기본)")
                if deposit2 and rent2: lines.append(f"   • 조건 B : 보증금 {deposit2}만 원 / 월세 {rent2}만 원")
                if deposit3 and rent3: lines.append(f"   • 조건 C : 보증금 {deposit3}만 원 / 월세 {rent3}만 원")
                lines.append("")

            # 🎯 [신설] DB에 건물옵션 데이터가 존재할 경우 상세설명에 동적 바인딩
            if building_option and str(building_option).strip() not in ["", "None"]:
                lines.append("🏢 [건물 공동 옵션]")
                lines.append(f"• {building_option}\n")

            if room_option and str(room_option).strip() not in ["", "None"]:
                lines.append("🛠️ [제공되는 시설 옵션]")
                lines.append(f"• {room_option}\n")

            # =================================================================
            # 🎯 [대개혁] 거래대상(tr_target)별 고유 메모/특징/특약 동적 매핑 및 라인 가공 엔진
            # =================================================================
            target_memo_raw = ""
            target_important_raw = ""
            target_terms_raw = ""
            target_name_ko = "호실"

            # 현재 실제 매킹된 거래대상 가중치 판독 분기
            current_target = tr_target if tr_target in ["층호수", "건물", "토지"] else ("토지" if karrot_type == "토지" else ("건물" if karrot_type == "건물" else "층호수"))

            if current_target == "층호수":
                target_name_ko = "호실"
                target_memo_raw = room_memo
                target_important_raw = room_important
                target_terms_raw = room_terms
            elif current_target == "건물":
                target_name_ko = "건물 전체"
                target_memo_raw = building_memo
                target_important_raw = building_important
                target_terms_raw = building_terms
            elif current_target == "토지":
                target_name_ko = "토지"
                target_memo_raw = land_memo
                target_important_raw = land_important
                target_terms_raw = land_terms

            # 지저분한 특수기호(--, ·) 및 빈 구절을 가독성 좋게 인라인 정제해주는 서브 팩토리 함수
            def clean_target_text(raw_text):
                if not raw_text or str(raw_text).strip() in ["", "0", "None"]:
                    return ""
                text_lines = [f"• {line.strip().lstrip('-').lstrip('·').strip()}" for line in str(raw_text).split('\n') if line.strip()]
                return "\n".join(text_lines)

            clean_target_important = clean_target_text(target_important_raw)
            clean_target_terms = clean_target_text(target_terms_raw)
            clean_target_memo = clean_target_text(target_memo_raw)

            # 정제 완료된 항목만 상세설명 본문 주머니에 순차적으로 바인딩
            if clean_target_important:
                lines.append(f"✨ [{target_name_ko} 주요 특징]")
                lines.append(clean_target_important + "\n")

            if clean_target_terms:
                lines.append(f"📜 [{target_name_ko} 특별 특약/규칙]")
                lines.append(clean_target_terms + "\n")

            if clean_target_memo:
                lines.append(f"📝 [{target_name_ko} 참고 메모]")
                lines.append(clean_target_memo + "\n")

            # 🎯 [핵심 주입] 정제된 DB의 알맹이 '주요특징' 메모가 있다면 중단에 매끄럽게 병합합니다.
            if db_content:
                lines.append("📝 [매물 주요 특징]")
                lines.append(db_content + "\n")
                    
            # =================================================================
            # 📞 [신설] 담당자 성별/직급별 직통 프로필 자동 생성 엔진
            # =================================================================
            pos = str(admin_data.get('admin_position', '')).strip()
            gen = str(admin_data.get('admin_gender', '')).strip() # '여'/'남' 또는 'F'/'M' 판별
            last_name = admin_name[0] if admin_name else ""
            
            # 1) 지정하신 규칙에 따른 성+직함 매칭 알고리즘 가동
            if pos in ['팀장', '팀원']:
                if gen in ['여', '여성', 'F', 'f']:
                    manager_title = f"{last_name}실장"
                else:
                    manager_title = f"{last_name}부장"
            elif pos:
                manager_title = f"{last_name}{pos}" # 소장, 대표 등 기타 직급 예외 처리
            else:
                manager_title = f"{admin_name}"
                
            # 2) 연락처 가독성을 높이기 위한 하이픈(-) 하이라이트 정제
            clean_p = re.sub(r'\D', '', str(admin_phone))
            formatted_phone = f"{clean_p[:3]}-{clean_p[3:7]}-{clean_p[7:]}" if len(clean_p) == 11 else admin_phone

            # 3) 상세설명 본문 주머니에 직통 유도 안내장 바인딩
            lines.append("📞 [담당자 직통 문의]")
            lines.append(f"• 직통 번호 : {formatted_phone} ({manager_title})")
            lines.append("• 구경하고 싶으시거나 궁금한 점이 있다면 언제든지 편하게 전화나 문자 남겨주세요! 부담 없이 친절하고 자세하게 안내해 드리겠습니다. 😊\n")
            # =================================================================

            lines.append("💡 [안내 사항]")
            lines.append("• 100% 실매물만 엄선하여 이웃분들께 소개해 드리고 있습니다.")
            lines.append("• 상세한 문의나 방문 예약은 채팅 또는 전화 주시면 친절히 안내해 드릴게요! ☺️")
            
            content = "\n".join(lines)
            print("✅ [상세설명 생성 완료] 데이터 기반 맞춤형 문장이 조립되었습니다.")

            try:
                content_header = driver.find_element(By.XPATH, "//span[text()='상세 설명']")
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", content_header)
                print("   .. 🛞 상세 설명 섹션으로 뷰포트 스크롤 이동 완료")
            except Exception as scroll_err:
                print(f"   .. ⚠️ 상세 설명 섹션 헤더 스크롤 실패 (계속 진행) -> {scroll_err}")

            # =================================================================
            # 7-E-3. [완벽 패치] 리액트 내부 가상돔(State) 강제 동기화 엔진
            # =================================================================
            try:
                print("✍️  [상세설명 주입] React 내부 메모리 상태(State) 강제 동기화를 실행합니다.")
                
                textarea_xpath = "//textarea[@name='content']"
                textarea_el = wait.until(EC.presence_of_element_located((By.XPATH, textarea_xpath)))
                
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", textarea_el)
                textarea_el.click()
                
                react_sync_script = """
                var element = arguments[0];
                var full_text = arguments[1];
                
                var valueSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value").set;
                valueSetter.call(element, full_text);
                
                element.dispatchEvent(new Event('input', { bubbles: true }));
                element.dispatchEvent(new Event('change', { bubbles: true }));
                """
                driver.execute_script(react_sync_script, textarea_el, content)
                print("✅ [상세 설명] 리액트 메모리 동기화 및 주입 최종 성공!")
                
            except Exception as content_err:
                print(f"❌ [상세 설명] 리액트 동기화 주입 실패 -> 원인: {content_err}")

            

            # =================================================================
            # 7-E-4. [완전 저격] 3단계 추적 알고리즘이 적용된 비밀메모 주입 엔진
            # =================================================================
            try:
                print("✍️  [중개소 비밀메모] 주입 및 3단계 그물망 추적을 시작합니다.")
                
                memo_xpaths = [
                    "//textarea[contains(@name, 'memo') or contains(@name, 'Memo') or contains(@placeholder, '메모')]",
                    "//span[contains(text(), '메모') or contains(text(), '비밀')]/ancestor::div[contains(@class, 'flex')][1]//textarea",
                    "//textarea[@name!='content']"
                ]
                
                memo_el = None
                for i, xpath in enumerate(memo_xpaths, 1):
                    try:
                        memo_el = WebDriverWait(driver, 1.5).until(
                            EC.presence_of_element_located((By.XPATH, xpath))
                        )
                        print(f"   .. 🎯 [{i}단계 추적망] 매칭 성공! (XPath: {xpath})")
                        break
                    except:
                        continue
                
                if memo_el is None:
                    raise Exception("화면에서 비밀메모 textarea 요소를 도저히 찾을 수 없습니다.")

                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", memo_el)
                # time.sleep(0.3)
                memo_el.click()
                # time.sleep(0.2)

                memo_date_str = datetime.now().strftime('%y%m%d') # 📅 '260524' 포맷 추출 (선행 선언)          
                secret_memo_text = f"{request_main}\n{memo_date_str} {admin_name}등록(새홈번호: {object_code_new})"
                
                react_memo_script = """
                var element = arguments[0];
                var full_text = arguments[1];
                
                var valueSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value").set;
                valueSetter.call(element, full_text);
                
                element.dispatchEvent(new Event('input', { bubbles: true }));
                element.dispatchEvent(new Event('change', { bubbles: true }));
                """
                driver.execute_script(react_memo_script, memo_el, secret_memo_text)
                print("✅ [중개소 비밀메모] 가공문구 자동 입력 최종 성공!")
                # time.sleep(0.5)
                
            except Exception as memo_err:
                print(f"⚠️  [중개소 비밀메모] 자동 입력 실패 (수동 입력 필요) -> 원인: {memo_err}")

            # =================================================================
            # 📞 [신설] 전화문의 받기 담당자 연락처 자동 변경 엔진
            # =================================================================
            if admin_phone:
                # 특수기호나 하이픈 완벽 제거 및 정제 (예: '010-1234-5678' -> '01012345678')
                admin_phone_clean = re.sub(r'\D', '', str(admin_phone))
                print(f"📞 [연락처 설정] 담당자 연락처({admin_phone_clean}) 세팅 여부 판별을 시작합니다.")
                try:
                    # 0) [추가] 현재 화면에 등록되어 노출 중인 연락처 글자 추출
                    # '전화문의 받기' 텍스트 바로 다음에 나오는 첫 번째 span 태그(번호 영역)를 타겟팅합니다.
                    current_phone_xpath = "//span[text()='전화문의 받기']/following::span[1]"
                    current_phone_el = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, current_phone_xpath))
                    )
                    current_phone = re.sub(r'\D', '', current_phone_el.text.strip())
                    print(f"   .. 📱 현재 등록된 연락처 추출 성공: {current_phone}")

                    # 💡 [스마트 스킵] 현재 등록된 번호와 담당자 번호가 이미 일치한다면 변경 생략!
                    if current_phone == admin_phone_clean:
                        print(f"   .. ℹ️  현재 번호와 담당자 번호가 이미 동일합니다. 불필요한 번호 변경을 건너뜁니다.")
                    else:
                        print(f"   .. 🔄 현재 번호({current_phone})와 담당자 번호({admin_phone_clean})가 다릅니다. 변경을 진행합니다.")
                        
                        # 1) '전화문의 받기' 섹션 뒤편에 위치한 '번호 수정하기' 버튼 찾아 클릭
                        edit_btn_xpath = "//span[text()='전화문의 받기']/following::button[text()='번호 수정하기'][1]"
                        edit_btn = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, edit_btn_xpath))
                        )
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", edit_btn)
                        time.sleep(0.2)
                        edit_btn.click()
                        print("   .. ✅ [번호 수정하기] 버튼 클릭 성공 (입력 폼 활성화)")
                        time.sleep(0.4) # 폼 전환 애니메이션 대기
                        
                        # 2) 번호 입력창 찾기 (가장 확실한 placeholder="01000000000" 속성 조준)
                        phone_input_xpath = "//form//input[@placeholder='01000000000']"
                        phone_input = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, phone_input_xpath))
                        )
                        
                        # 기존 입력값 지우고 담당자 번호 주입
                        phone_input.click()
                        phone_input.send_keys(Keys.CONTROL + "a")
                        phone_input.send_keys(Keys.BACKSPACE)
                        time.sleep(0.1)
                        phone_input.send_keys(admin_phone_clean)
                        print(f"   .. ✅ 담당자 번호({admin_phone_clean}) 입력 완료")
                        time.sleep(0.2)
                        
                        # 3) '번호 변경' 완료 버튼 찾아 클릭하여 저장
                        submit_btn_xpath = "//form//button[text()='번호 변경']"
                        submit_btn = driver.find_element(By.XPATH, submit_btn_xpath)
                        submit_btn.click()
                        print("   .. ✅ [번호 변경] 반영 완료!")
                        # time.sleep(0.5)
                    
                except Exception as phone_err:
                    print(f"⚠️  [연락처 설정] 변경 도중 건너뜀 (이미 설정되어 있거나 요소를 찾을 수 없음) -> {phone_err}")
            else:
                print("ℹ️  [연락처 설정] DB에 담당자 연락처 데이터가 없어 기본 번호 상태를 유지합니다.")


            # =================================================================
            # 7-H. [디버깅 패치] 매물 사진 저장 폴더 자동 열기 및 경로 추적
            # =================================================================
            # 🔍 실시간 수신 데이터 분석 출력 (터미널에서 확인용)
            print("\n================== 📂 [사진 폴더 정밀 수사관] ==================")
            print(f"📄 write_data 내 'img_path' 값   : {write_data.get('img_path')}")
            print(f"📄 data 내 'folderPath' 값       : {data.get('folderPath')}")
            print(f"🔑 write_data 전체 키 목록       : {list(write_data.keys())}")
            print(f"🔑 data 전체 키 목록             : {list(data.keys())}")
            print("==============================================================\n")

            # 물건사진 폴더열기
            main_dir = 'Z:\\업무자료\\4사진자료&이미지자료(외부유출금지)\\1주거용물건, 상업용물건\\'
            path_dir = main_dir + data['folderPath'] #'경기도\\오산시\\궐동\\654-9\\썬플라워\\1층\\1층'
            print("기본 매물 경로:", path_dir)
            
            # 1) 🎯 [개선] 'output' 단어가 포함된 모든 폴더 스캔 및 최신순 정밀 추적 가동
            if os.path.exists(path_dir):
                try:
                    # 폴더 내 모든 하위 항목 중 이름에 'output'이 들어간 디렉토리만 자석처럼 수집
                    all_items = os.listdir(path_dir)
                    output_dirs = [
                        os.path.join(path_dir, item) 
                        for item in all_items 
                        if 'output' in item and os.path.isdir(os.path.join(path_dir, item))
                    ]
                    
                    # 소장님이 출력창에서 즉시 원인을 파악하실 수 있도록 검색 내역 투명하게 오픈
                    print(f"   .. 📂 [폴더 스캔 결과] 현재 매물 경로 내부에서 발견된 output 계열 폴더: {output_dirs}")
                    
                    if output_dirs:
                        # 🎯 [치료 핵심] 윈도우 수정 날짜에 속지 않고, 폴더명 뒤의 숫자(YYMMDD) 순서대로 완벽하게 정렬하여 가장 최신 폴더를 수확합니다.
                        chosen_output_dir = max(output_dirs, key=lambda x: os.path.basename(x))
                        print(f"   .. 🎯 [최신 폴더 타겟팅] 문자열 날짜순(YYMMDD) 가장 최신 폴더를 자동 결합했습니다: {chosen_output_dir}")
                        
                        # 선택된 폴더 내부에 존재하는 진짜 하위 서브 디렉토리 목록 수집
                        sub_dirs = [
                            os.path.join(chosen_output_dir, d) 
                            for d in os.listdir(chosen_output_dir) 
                            if os.path.isdir(os.path.join(chosen_output_dir, d))
                        ]
                        if sub_dirs:
                            path_dir = max(sub_dirs, key=os.path.getmtime)
                            print(f"   .. 🎯 [하위 서브작업 폴더 발견] 최종 기입된 최신 하위 폴더를 엽니다: {path_dir}")
                        else:
                            path_dir = chosen_output_dir
                            print(f"   .. 🎯 [하위 폴더 없음] 내부가 비어있어 선택된 output 폴더 자체를 오픈 경로로 지정합니다.")
                    else:
                        print(f"   .. ℹ️  [추적 패스] 해당 매물 폴더 리스트 내부에 'output' 단어가 포함된 폴더가 전혀 발견되지 않았습니다. 기본 경로를 유지합니다.")
                        
                except Exception as track_err:
                    print(f"   .. ⚠️ [하위 폴더 정밀 추적 중 연산 에러 발생] -> 원인: {track_err} (기본 경로 우회)")

            # 2) 🎯 [버그 수정] 미정의된 '원본사진들' 변수 대신, 최종 타겟 경로가 존재하는지 여부로 가드레일 교체
            if path_dir and os.path.exists(path_dir): 
                try:
                    os.startfile(path_dir)
                    print('📂 폴더열기 성공') 
                except:
                    try:
                        # os.startfile 거부 반응 발생 시 서브 프로세스 핸들러로 2차 우회 오픈
                        import subprocess
                        subprocess.Popen(f'explorer "{path_dir}"')
                        print('📂 서브 프로세스로 폴더열기 성공')
                    except Exception as sub_err:
                        print(f'❌ 폴더열기 최종 에러 -> {sub_err}')   
            else:
                print("⚠️ [사진 폴더] 경로가 올바르지 않거나 컴퓨터에 존재하지 않아 열기를 패스합니다.")
                failed_fields.append("• [사진 폴더] 경로찾기실패 / 열기 패스")

            # 🎯 [버그 수정] 당근마켓에 존재하지 않는 오방용 급매(is_speed) 강제 조작 스크립트 라인 전면 영구 삭제완료

            # =================================================================
            # 8. 최종 입력 확인 및 당근 매물번호 자동 추출/DB 저장 엔진
            # =================================================================
            print("="*60 + "\n")
            print("🎉 필수 및 주차 정보까지 모든 필드 고도화 입력 시도가 완료되었습니다.")
            
            # 🎯 [동적 리포트 합성 시스템 개혁]
            base_msg = (
                "[입력 결과 확인후 매물번호 추출용] 대기 창입니다.\n\n"
                "오입력된 내용이 없는지 최종 주차 정보까지 검수하신 뒤,\n"
                "브라우저 화면 맨 아래에서 [작성 완료] 혹은 [등록하기]를 진행해 주세요.\n\n"
            )
            
            # 만약 실패 주머니에 에러 명단이 하나라도 담겨있다면, 문장 사이에 경고 안내장 긴급 합성
            if failed_fields:
                base_msg += "⚠️ [자동 입력 실패/누락 항목 발생!]\n"
                base_msg += "당근마켓 내부 팝업 화면이 요소를 가려 아래 항목이 정상 기입되지 못했습니다.\n"
                base_msg += "등록 완료 버튼을 누르기 전, 화면에서 꼭 '수동 확인 및 수정'을 해주세요!\n\n"
                base_msg += "\n\n".join(failed_fields) + "\n\n"
                
            base_msg += "※ '등록 완료!' 화면으로 전환되면 이 알림창의 [확인]을 누르세요."

            # 최상단 강제 고정 알림창 가동
            최상단알림창(base_msg, title="🔍 매물 등록 최종 검수 대기")
            
            try:
                print("⏳ [매물번호 추출] 완료 화면에서 당근 매물 번호 추적을 시작합니다 (최대 20초 대기)...")
                
                daangn_label_xpath = "//span[text()='매물 번호']"
                WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, daangn_label_xpath)))
                
                daangn_code_el = driver.find_element(By.XPATH, "//span[text()='매물 번호']/following-sibling::span[1]")
                daangn_code = daangn_code_el.text.strip()
                print(f"🎯 [추출 성공] 당근마켓 새 매물 번호 수거 완료 ➡️ {daangn_code}")
                
                # =================================================================
                # 💾 4) [신설] naver.py 동기화 규격 맞춤형 DB 주입/수정 엔진 (안전 가드 작동)
                # =================================================================
                print(f"💾 [DB 연동 시작] 새홈 매물번호 [{object_code_new}] 당근 광고 데이터 동기화 중...")
                
                current_date = datetime.now().strftime("%Y-%m-%d")
                current_time = datetime.now().strftime("%H:%M:%S")
                ad_start = current_date
                ad_end = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
                manager_id = admin_data.get('ad_id', '')
                new_ad_memo = f"{admin_name} 등록, 당근:{daangn_code}"

                conn = None
                try:
                    conn = pymysql.connect(
                        host='obangkr.cafe24.com', user='obangkr', password='Ddhqkd!1', database='obangkr', charset='utf8'
                    )
                    cursor = conn.cursor()
                    
                    check_query = "SELECT * FROM pr_externalad WHERE object_code_new = %s AND ad_site = '당근'"
                    cursor.execute(check_query, (object_code_new,))
                    existing_record = cursor.fetchone()
                    
                    if existing_record:
                        update_query = """
                            UPDATE pr_externalad 
                            SET ad_code = %s, ad_udate = %s, ad_utime = %s, ad_memo = %s, ad_start = %s, ad_end = %s
                            WHERE object_code_new = %s AND ad_site = '당근'
                        """
                        cursor.execute(update_query, (daangn_code, current_date, current_time, new_ad_memo, ad_start, ad_end, object_code_new))
                        db_action_text = "기존 매물 정보 업데이트(UPDATE) 성공"
                    else:
                        insert_query = """
                            INSERT INTO pr_externalad (
                                admin_id, object_code_new, ad_start, ad_end, ad_site, ad_code, 
                                ad_manager, ad_manager_id, ad_udate, ad_utime, ad_memo, ad_wdate, ad_wtime
                            ) VALUES (%s, %s, %s, %s, '당근', %s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        cursor.execute(insert_query, (
                            manager_id, object_code_new, ad_start, ad_end, daangn_code, 
                            admin_name, manager_id, current_date, current_time, new_ad_memo, current_date, current_time
                        ))
                        db_action_text = "신규 매물 데이터 삽입(INSERT) 성공"
                    
                    conn.commit()
                    print(f"   .. ✅ DB 동기화 최종 승인 완료! ({db_action_text})")
                    
                    # 5) 🎯 [리팩토링] 최종 등록 완료 안내창 치환
                    최상단알림창(
                        f"🎉 당근 매물 등록 및 DB 저장 성공!\n\n"
                        f"• 새홈 매물번호 : {object_code_new}\n"
                        f"• 당근 등록번호 : {daangn_code}\n"
                        f"• 실시간 DB 조치 : {db_action_text}\n\n"
                        f"오방 데이터베이스에 매핑 정보가 정상 반영되었습니다.\n"
                        f"[확인]을 누르면 매크로 프로그램이 종료됩니다.",
                        title="✅ 당근 등록 완료"
                    )
                    
                except Exception as db_err:
                    if conn: conn.rollback()
                    print(f"❌ [DB 동기화 실패] 트랜잭션 오류로 인해 롤백되었습니다 -> {db_err}")
                    # 🎯 [리팩토링] DB 저장 에러창 치환
                    최상단알림창(f"⚠️ 매물은 등록되었으나 DB 저장에 실패했습니다.\n\n오류 내용: {db_err}", title="❌ DB 동기화 오류")
                finally:
                    if conn: conn.close()
                
            except Exception as extract_err:
                print(f"❌ [매물번호 추출 실패] 완료 화면을 찾지 못했거나 타임아웃 발생 -> {extract_err}")
                # 🎯 [리팩토링] 번호 추출 실패 에러창 치환
                최상단알림창(
                    "완료 페이지에서 당근 매물번호를 추출하는 데 실패했습니다.\n\n"
                    "인터넷 지연 등으로 화면이 미처 다 켜지지 않았을 수 있으니,\n"
                    "브라우저 우측에 생성된 번호를 메모하신 후 수동 저장해 주세요.",
                    title="⚠️ 추출 타임아웃"
                )

            print("="*60 + "\n")

    except Exception as e:
        print(f"\n❌ 당근 매크로 치명적 오류 발생: {e}")
        pyautogui.alert(f"오류가 발생했습니다:\n{str(e)}")
        
    finally:
        if driver:
            driver.quit()