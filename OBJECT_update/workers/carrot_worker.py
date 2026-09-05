# D:\241103_nsk98\Documents\repos_python\OBJECT_update\workers\carrot_worker.py

import os
import time
import datetime
import json   # 끌올관측 기록을 한 줄 JSON으로 남길 때 사용
import sys
import pyautogui
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# 🚀 상위 폴더의 패키지를 인식할 수 있도록 시스템 경로(sys.path)에 추가하는 마법의 코드
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from util.property_utils import (
    확인창클릭,
    최상단알림창,

    당근매물번호_검색창_입력, 
    검색결과_목록개수_확인, 
    리액트_입력창_값_강제주입, 
    당근_매물상태_확인, 
    당근_날짜및_끌어올리기_가능여부_확인,
    텍스트창_값검속_및_신규업데이트판정,
    체크박스_상태검속_및_신규업데이트판정,
    라디오버튼_선택검속_및_신규업데이트판정,
    드롭다운_선택검속_및_신규업데이트판정,
    로그저장,
    텍스트기준_버튼_클릭,
    최상단_예아니오_창,
    당근_끌어올리기_마스터_통합엔진,
    데이터베이스_다중_가격스펙_전수조회,
)

class CarrotAutomationWorker:
    """ 당근부동산 비즈니스 센터 제어 및 매물 끌올/수정/완료 처리를 전담하는 클래스 """

    def __init__(self, 브라우저_객체, 수집된_데이터, 작업_모드, progress_callback=None, unattended=False):
        self.브라우저 = 브라우저_객체
        self.데이터 = 수집된_데이터
        self.모드 = 작업_모드

        # 🔥 외부 호출 이름(progress_callback)은 맞추고, 내부 변수는 직관적인 한글명을 유지합니다!
        self.진행상황_알림함수 = progress_callback
        # 나스 무인 실행처럼 사람이 화면 앞에 없는 경우 True — 로그인 세션 만료 시 QR/문자인증을
        # 대신 해줄 사람이 없으므로, 무한정 기다리는 대신 즉시 중단하고 원인을 로그에 남긴다.
        self.unattended = unattended
        
        # 내부 성과 지표 한글 변수 초기화
        self.최종완료_개수 = 0
        self.끌어올리기_성공_개수 = 0
        self.수정업데이트_성공_개수 = 0
        self.비공개완료_성공_개수 = 0
        self.건너뜀_개수 = 0
        self.숨김해제_성공_개수 = 0

    # =================================================================
    # 🔒 [신설] 로그인 세션 자동 검증 및 페이지 로드 안정화 모듈 (daangn.py 이식)
    # =================================================================
    def 로그인확인_및_페이지로드_안정화(self):
        """ 당근 Realty CEO 홈 페이지 진입 후 로그인 상태를 검수하고 화면이 완벽히 켜질 때까지 동적 대기 """
        초기_제한시간_대기기구 = WebDriverWait(self.브라우저, 4)
        
        print("\n[🔎 디버그] 1단계: 당근 비즈니스 센터 매물 관리 홈 주소로 브라우저 이동을 명령합니다.")
        self.브라우저.get('https://realty.daangn.com/ceo/home')
        
        try:
            print("[🔎 디버그] 2단계: 기존 로그인 세션(쿠키) 유효성을 판별하기 위해 대시보드 핵심 요소(통합 검색창)를 탐색합니다...")
            # 대시보드 내 검색 필터 input 요소가 4초 안에 발견되는지 실시간 감시
            초기_제한시간_대기기구.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "form input[placeholder*='지번']"))
            )
            print("[✅ 로그인 검증 성공] 기존 세션이 안전하게 유지되어 있어 수동 인증 없이 즉시 통과합니다.")
            
        except TimeoutException:
            print("🔑 [로그인 세션 만료] 대시보드 진입이 차단되어 사용자 인증 대기 제동 장치를 발동합니다.")

            if self.unattended:
                # 무인 모드에서는 QR/문자인증을 대신 해줄 사람이 없다 — 기다려봐야 영원히 풀리지
                # 않으므로 팝업을 띄우는 대신 즉시 예외를 던져 이번 사이클을 중단시키고 로그로 남긴다.
                raise RuntimeError("당근 로그인 세션 만료 — 무인 모드에서는 자동 재로그인이 불가능하여 실행을 중단합니다.")

            # daangn.py와 동일하게 사용자가 인증을 마칠 때까지 매크로 엔진의 흐름을 임시 정지시킵니다.
            pyautogui.alert(
                "당근마켓 로그인 세션이 유효하지 않습니다!\n\n"
                "크롬 창에서 휴대폰 번호 인증 또는 QR 코드 스캔 로그인을 완료하신 뒤,\n"
                "대표 중개소 매물 목록 대시보드가 화면에 완벽히 로드되면\n"
                "이 프로그램 안내창의 [확인]을 눌러 계속 진행해 주세요."
            )
            
            print("[🔎 디버그] 사용자 수동 로그인 완료 신호를 수신했습니다. 화면 재검증 시퀀스를 가동합니다...")
            # 로그인 완료 후 대시보드가 완전히 그려질 때까지 넉넉하게 스캔 대기 (최대 60초 제한)
            WebDriverWait(self.브라우저, 60).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "form input[placeholder*='지번']"))
            )
            print("[✅ 로그인 검증 성공] 사용자가 로그인을 성공적으로 마쳤음을 감지했습니다.")
            
        print("[🔎 디버그] 3단계: 비동기 AJAX 데이터 그리드 테이블이 완전히 안착할 수 있도록 물리적 버퍼 시간을 부여합니다.")
        time.sleep(2.0)
        print("[🔎 디버그] 당근 비즈니스 센터 화면 초기화 및 페이지 로드 안정화 작업 완료!\n")

    # =================================================================
    # 🔍 기능별 독립 검증 함수 (순수 한글화 및 디버깅 강화)
    # =================================================================

    def 검색결과_목록개수_확인(self, 당근매물번호):
        """ 현재 화면에 노출된 검색 결과 매물 행(Row)의 개수를 반환 (공용 유틸 이식 버전) """
        개수 = 검색결과_목록개수_확인(self.브라우저)
        print(f"   [🔎 디버그 - {당근매물번호}] 현재 화면에 감지된 매물 카드 개수: {개수}개")
        return 개수

    def 매물상태_확인(self, 매물_행_객체, 당근매물번호):
        """ 해당 매물의 현재 상태 값('숨김', '판매중' 등)을 추출하여 반환 (공용 유틸 이식 버전) """
        status_text = 당근_매물상태_확인(매물_행_객체)
        print(f"   [🔎 디버그 - {당근매물번호}] 매물의 현재 화면 표시 상태값: '{status_text}'")
        return status_text

    def 날짜및_끌어올리기_가능여부_확인(self, 매물_행_객체, 당근매물번호):
        """ 날짜 필드의 텍스트와 [끌어올리기] 버튼 존재 여부를 판별하여 반환 (공용 유틸 이식 버전) """
        date_text, can_up = 당근_날짜및_끌어올리기_가능여부_확인(매물_행_객체)
        print(f"   [🔎 디버그 - {당근매물번호}] 표시된 날짜: '{date_text}' | 끌어올리기 버튼 활성화 여부: {can_up}")
        return date_text, can_up

    def 팝업_제목_텍스트_추출(self, driver, timeout=3):
        """
        현재 열려 있는 가격 조정 팝업창의 H2 타이틀 영역 텍스트를 100% 수거하는 당근 전속 함수
        """
        try:
            h2_요소 = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, "//div[@role='dialog' and @data-state='open']//h2"))
            )
            팝업제목 = h2_요소.get_attribute("textContent").strip()
            # pyautogui.alert(f"팝업제목:{팝업제목}")
            # span 태그 등으로 쪼개져 있어도 한눈에 합쳐서 문자열로 반환합니다.
            return 팝업제목
        except:
            return ""

    # =================================================================
    # 🎯 [신설 함수] 가격 최신화/신설/소거 공정을 완전히 전담하는 하부 모듈
    # =================================================================
    def 팝업창_가격_동기화_처리(self, 팝업창, 당근매물번호, DB_유효_가격목록):
        """ 팝업창 내부의 카드들을 DB 스펙에 맞춰 조율하고 변동 여부 리포트를 반환합니다. """
        DB_요구_유형들 = [x['종류'] for x in DB_유효_가격목록]
        처리완료_목표_유형들 = set()
        실제_변경_발생함 = False
        변경_리포트_목록 = []

        # 🔄 [1단계]: 기존 카드 재사용 및 실시간 금액 최신화 (덮어쓰기)
        현재_팝업창_카드들 = 팝업창.find_elements(By.XPATH, ".//span[contains(@class, 't5-bold')]/ancestor::div[contains(@class, 'rounded-r3')]")
        print(f"   [🔎 1단계: 기존카드 검속 - {당근매물번호}] 팝업창 내 기존 생성 카드 {len(현재_팝업창_카드들)}개 감지")
        
        for 카드 in 현재_팝업창_카드들:
            카드_텍스트 = 카드.find_element(By.XPATH, ".//span[contains(@class, 't5-bold')]").get_attribute("textContent").strip()
            정제_종류 = "월세" if "월세" in 카드_텍스트 else "전세" if "전세" in 카드_텍스트 else "매매" if "매매" in 카드_텍스트 else "단기" if "단기" in 카드_텍스트 else ""
            
            if 정제_종류 in DB_요구_유형들:
                DB_아이템 = next(x for x in DB_유효_가격목록 if x['종류'] == 정제_종류)
                카드_수치_변경됨 = False
                
                if 정제_종류 == "월세" or 정제_종류 == "단기":
                    현재_보증금 = 카드.find_element(By.NAME, "deposit").get_attribute("value")
                    현재_월세 = 카드.find_element(By.NAME, "monthlyPay").get_attribute("value")
                    if 현재_보증금 != str(DB_아이템["보증금"]) or 현재_월세 != str(DB_아이템["월세"]):
                        변경_리포트_목록.append(f" 🔄 [{정제_종류} 수정] 기존: {현재_보증금}/{현재_월세} ➡️ 완료: {DB_아이템['보증금']}/{DB_아이템['월세']}")
                        self.리액트_입력창_값_강제주입(카드.find_element(By.NAME, "deposit"), str(DB_아이템["보증금"]))
                        self.리액트_입력창_값_강제주입(카드.find_element(By.NAME, "monthlyPay"), str(DB_아이템["월세"]))
                        카드_수치_변경됨 = True
                        
                elif 정제_종류 == "전세":
                    현재_보증금 = 카드.find_element(By.NAME, "deposit").get_attribute("value")
                    if 현재_보증금 != str(DB_아이템["보증금"]):
                        변경_리포트_목록.append(f" 🔄 [{정제_종류} 수정] 기존: {현재_보증금} ➡️ 완료: {DB_아이템['보증금']}")
                        self.리액트_입력창_값_강제주입(카드.find_element(By.NAME, "deposit"), str(DB_아이템["보증금"]))
                        카드_수치_변경됨 = True
                        
                elif 정제_종류 == "매매":
                    try: 매매_인풋 = 카드.find_element(By.NAME, "price")
                    except: 매매_인풋 = 카드.find_element(By.XPATH, ".//input[@type='number']")
                    현재_매매가 = 매매_인풋.get_attribute("value")
                    if 현재_매매가 != str(DB_아이템["매매가"]):
                        변경_리포트_목록.append(f" 🔄 [{정제_종류} 수정] 기존: {현재_매매가} ➡️ 완료: {DB_아이템['매매가']}")
                        self.리액트_입력창_값_강제주입(매매_인풋, str(DB_아이템["매매가"]))
                        카드_수치_변경됨 = True
                
                if 카드_수치_변경됨:
                    print(f"   [✍️ 금액 업데이트 - {당근매물번호}] 구형 [{정제_종류}] 카드 가격 변동 검지 ➡️ 최신 금액 덮어쓰기 완수")
                    실제_변경_발생함 = True
                else:
                    print(f"   [ 동결 - {당근매물번호}] 구형 [{정제_종류}] 카드 데이터 완전 일치 ➡️ 수정 스킵")
                    
                처리완료_목표_유형들.add(정제_종류)

        # 🔄 [2단계]: 누락된 거래 종류 스마트 신설 (정밀 추적 트랩 탑재)
        for DB_아이템 in DB_유효_가격목록:
            목표_유형 = DB_아이템["종류"]
            if 목표_유형 in 처리완료_목표_유형들:
                continue

            체크_카드들 = 팝업창.find_elements(By.XPATH, ".//span[contains(@class, 't5-bold')]/ancestor::div[contains(@class, 'rounded-r3')]")
            
            if len(체크_카드들) == 0:
                print(f"   [➕ 방식 직통신설 - {당근매물번호}] 청정 공실 상태 확인 ➡️ 대형 직통 [{목표_유형}] 단추 직접 클릭")
                try:
                    직통_단추 = 팝업창.find_element(By.XPATH, f".//div[contains(@class, 'gap-x2_5')]/button[text()='{목표_유형}']")
                    self.브라우저.execute_script("arguments[0].click();", 직통_단추)
                    time.sleep(0.8)
                except Exception as 단추오류:
                    print(f"   [❌ 단계 실패] 빈 화면 직통 [{목표_유형}] 단추를 클릭하지 못했습니다: {단추오류}")
                    raise 단추오류
            else:
                print(f"   [➕ 방식 레이어신설 - {당근매물번호}] 팝업창 내 [{목표_유형}] 누락 확인 ➡️ 다른 거래 방식 메뉴 가동")
                
                try:
                    스크롤_컨테이너 = 팝업창.find_element(By.XPATH, ".//div[contains(@class, 'overflow-y-auto')]")
                    self.브라우저.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", 스크롤_컨테이너)
                    time.sleep(0.5)
                    
                    추가_버튼 = 팝업창.find_element(By.XPATH, ".//span[contains(text(), '다른 거래 방식 추가')]/ancestor::button")
                    동적_메뉴_ID = 추가_버튼.get_attribute("aria-controls")
                    
                    self.브라우저.implicitly_wait(0) 
                    드롭다운_옵션들 = self.브라우저.find_elements(By.XPATH, "//div[@role='menuitem'] | //div[contains(@class, 'menu')]//button")
                    메뉴_실제_보임 = any(옵션.is_displayed() for 옵션 in 드롭다운_옵션들)
                    self.브라우저.implicitly_wait(5) 
                    
                    if not 메뉴_실제_보임:
                        print(f"   [🔎 디버그 - {당근매물번호}] 추가 메뉴가 물리적으로 열려있지 않으므로 무조건 클릭 탈환!")
                        try: 추가_버튼.click()
                        except: self.브라우저.execute_script("arguments[0].click();", 추가_버튼)
                        time.sleep(0.6)
                except Exception as 버튼오류:
                    print(f"   [❌ 단계 실패] '다른 거래 방식 추가' 버튼 및 스크롤바 제어 실패: {버튼오류}")
                    raise 버튼오류
                    
                try:
                    제어_레이어_ID = 동적_메뉴_ID if 동적_메뉴_ID else "radix-_r_53_"
                    정밀_옵션_XPATH = (
                        f"//*[@id='{제어_레이어_ID}']//*[contains(text(), '{목표_유형}') or contains(., '{목표_유형}')] | "
                        f"//div[@role='menuitem' and contains(., '{목표_유형}')] | "
                        f"//div[contains(@id, 'radix-')]//span[text()='{목표_유형}'] | "
                        f"//button[contains(., '{목표_유형}') and not(ancestor::div[@role='dialog'])]"
                    )
                    옵션_타겟 = WebDriverWait(self.브라우저, 4).until(EC.presence_of_element_located((By.XPATH, 정밀_옵션_XPATH)))
                    self.브라우저.execute_script("arguments[0].click();", 옵션_타겟)
                    time.sleep(0.8)
                except Exception as 옵션오류:
                    raise 옵션오류
                
            최종_타겟_카드 = 팝업창.find_element(By.XPATH, f".//span[contains(@class, 't5-bold') and contains(text(), '{목표_유형}')]/ancestor::div[contains(@class, 'rounded-r3')]") if False else 팝업창.find_element(By.XPATH, f".//span[contains(@class, 't5-bold') and contains(text(), '{목표_유형}')]/ancestor::div[contains(@class, 'rounded-r3')]")
            if 목표_유형 == "월세" or 목표_유형 == "단기":
                self.리액트_입력창_값_강제주입(최종_타겟_카드.find_element(By.NAME, "deposit"), str(DB_아이템["보증금"]))
                self.리액트_입력창_값_강제주입(최종_타겟_카드.find_element(By.NAME, "monthlyPay"), str(DB_아이템["월세"]))
            elif 목표_유형 == "전세":
                self.리액트_입력창_값_강제주입(최종_타겟_카드.find_element(By.NAME, "deposit"), str(DB_아이템["보증금"]))
            elif 목표_유형 == "매매":
                try: 매매_인풋 = 최종_타겟_카드.find_element(By.NAME, "price")
                except: 매매_인풋 = 최종_타겟_카드.find_element(By.XPATH, ".//input[@type='number']")
                self.리액트_입력창_값_강제주입(매매_인풋, str(DB_아이템["매매가"]))
                
            print(f"   [✍️ 금액 신설완료 - {당근매물번호}] 신설 배치된 [{목표_유형}] 카드에 타겟 금액 기입 완료")
            신설_금액 = f"{DB_아이템['보증금']}/{DB_아이템['월세']}" if 목표_유형 in ["월세", "단기"] else f"{DB_아이템['보증금']}" if 목표_유형 == "전세" else f"{DB_아이템['매매가']}"
            변경_리포트_목록.append(f" ➕ [{목표_유형} 신설] ➡️ 입력금액: {신설_금액}")
            실제_변경_발생함 = True

        # 🗑️ [3단계]: DB 요구사항 스펙에 전혀 없는 껍데기 구형 카드 최종 철거
        while True:
            마무리_카드들 = 팝업창.find_elements(By.XPATH, ".//span[contains(@class, 't5-bold')]/ancestor::div[contains(@class, 'rounded-r3')]")
            최종_삭제_실행됨 = False
            
            for 카드 in 마무리_카드들:
                카드_텍스트 = 카드.find_element(By.XPATH, ".//span[contains(@class, 't5-bold')]").get_attribute("textContent").strip()
                정제_종류 = "월세" if "월세" in 카드_텍스트 else "전세" if "전세" in 카드_텍스트 else "매매" if "매매" in 카드_텍스트 else "단기" if "단기" in 카드_텍스트 else ""
                
                if 정제_종류 not in DB_요구_유형들:
                    print(f"   [🗑️ 최종 소거 - {당근매물번호}] DB에 없는 불필요 카드 완전 박멸 ➡️ 유형:[{카드_텍스트}] 휴지통 격파")
                    try:
                        이전_값 = 카드.find_element(By.NAME, "price").get_attribute("value") if 정제_종류 == "매매" else f"{카드.find_element(By.NAME, 'deposit').get_attribute('value')}/{카드.find_element(By.NAME, 'monthlyPay').get_attribute('value') if 정제_종류 in ['월세','단기'] else ''}".rstrip('/')
                    except: 이전_값 = "확인불가"
                    변경_리포트_목록.append(f" 🗑️ [{정제_종류} 삭제] 기존에 적혀있던 금액: {이전_값}")
                    
                    삭제_단추 = 카드.find_element(By.XPATH, ".//button[@aria-label='삭제']")
                    self.브라우저.execute_script("arguments[0].click();", 삭제_단추)
                    time.sleep(0.8) 
                    최종_삭제_실행됨 = True
                    실제_변경_발생함 = True
                    break 
                    
            if not 최종_삭제_실행됨:
                break 

        return 실제_변경_발생함, 변경_리포트_목록

    # 🔥 [신설] 사장님 검속용 DB 전체 데이터 가로 한 줄 출력 엔진
    def 데이터베이스_전체_정보_출력(self, 당근매물번호):
        """ 당근 매물 번호에 매핑된 DB 원본 레코드 전체 필드를 가로로 컴팩트하게 출력 """
        import pymysql
        try:
            연결고리 = pymysql.connect(host='obangkr.cafe24.com', user='obangkr', password='Ddhqkd!1', database='obangkr', charset='utf8')
            명령조수 = 연결고리.cursor(pymysql.cursors.DictCursor)
            조회쿼리 = """
                SELECT * FROM pr_externalad AS e
                JOIN pr_object AS o ON e.object_code_new = o.object_code_new
                JOIN pr_request_give AS c ON o.land_code = c.land_code AND o.building_code = c.building_code AND o.room_code = c.room_code
                WHERE e.ad_code = %s AND e.ad_site = '당근' LIMIT 1
            """
            명령조수.execute(조회쿼리, (str(당근매물번호),))
            원본행 = 명령조수.fetchone()
            if 원본행:
                # pprint를 쓰지 않고 내장 dict 출력으로 가로 정렬 강제 유지
                print(f"   [🔎 DB 원본 전수조사 - {당근매물번호}] {dict(원본행)}")
            명령조수.close(); 연결고리.close()
        except Exception as 오류:
            print(f"   [❌ 오류 - {당근매물번호}] 원본 데이터 출력 중 실패: {오류}")

    # =================================================================
    # 💾 [신설] 끌올 성공 매물 광고시작일(ad_start) 오늘 날짜 동기화 엔진
    # =================================================================
    def 데이터베이스_광고시작종료일_최신화(self, 당근매물번호):
        """ 숨김 해제 성공 시 광고 시작일을 오늘로, 종료일을 30일 뒤로 전격 연장 동기화 """
        import pymysql
        try:
            연결고리 = pymysql.connect(host='obangkr.cafe24.com', user='obangkr', password='Ddhqkd!1', database='obangkr', charset='utf8')
            명령조수 = 연결고리.cursor()
            
            # 🎯 [종료일 30일 연장 이식] 시작일(오늘), 업데이트일(오늘), 종료일(오늘+30일) 삼각 편대를 동시에 리셋합니다.
            업데이트쿼리 = """
                UPDATE pr_externalad 
                SET ad_start = CURRENT_DATE, 
                    ad_end = DATE_ADD(CURRENT_DATE, INTERVAL 30 DAY), 
                    ad_udate = CURRENT_DATE 
                WHERE ad_code = %s AND ad_site = '당근' AND ad_del = 'N'
            """
            명령조수.execute(업데이트쿼리, (str(당근매물번호),))
            연결고리.commit()
            명령조수.close(); 연결고리.close()
            print(f"   [💾 DB 부활 동기화 - {당근매물번호}] 광고시작일(오늘) 및 종료일(30일 뒤) 패키지 갱신 완료")
        except Exception as 오류:
            print(f"   [❌ DB 업데이트 실패 - {당근매물번호}] 광고 정보 연장 업데이트 중 실패: {오류}")

    def 리액트_입력창_값_강제주입(self, 엘리먼트, 주입할_텍스트):
        """ 리액트 가상돔(State)의 압착을 무력화하고 값을 완벽하게 동기화 주입 (공용 유틸 이식 버전) """
        return 리액트_입력창_값_강제주입(self.브라우저, 엘리먼트, 주입할_텍스트)

    def 끌어올리기_실행(self, 매물_행_객체, 당근매물번호, 현재_상태):
        """ 
        [소장님 아키텍처 연동 완수] 내부 비즈니스 로직 연산을 공용 마스터 통합 엔진에 일임하고,
        반환된 결과 코드 명사에 맞추어 인스턴스 성과 카운터 지표만 정밀 누적 처리합니다.
        """
        # ① 공용 엔진에 대조하기 위해 선행 조회한 DB 다중 가격 스펙 주머니를 먼저 빌드합니다.
        DB_유효_가격목록 = 데이터베이스_다중_가격스펙_전수조회(당근매물번호, "당근")
        
        # ② 🚀 [핵심 연동] 복잡한 모든 팝업 추적 처리를 공용 통합 엔진에게 배달 위임합니다!
        # 팝업에서 읽히는 쿨타임 문구를 받아올 그릇 — 총괄 루프가 이걸 관측기록으로 남긴다.
        관측 = {}
        결과_코드명사 = 당근_끌어올리기_마스터_통합엔진(
            driver=self.브라우저,
            row_element=매물_행_객체,
            ad_code=당근매물번호,
            current_status=현재_상태,
            price_specs=DB_유효_가격목록,
            unattended=self.unattended,
            끌올관측_수집함=관측
        )
        # 총괄 루프에서 꺼내 쓴다(여기서 바로 적재하지 않는 이유: 상태·날짜표시는 루프가 들고 있어서
        #  한 줄로 합치려면 그쪽에서 써야 한다. 여기서 따로 적재하면 관측이 두 줄로 쪼개진다).
        self.최근_끌올관측 = {**관측, '결과코드': 결과_코드명사}
        
        # ③ 공용 엔진이 리턴해준 코드에 따라 이 파일 고유의 카운터 지표 가드레일을 밟습니다.
        if 결과_코드명사 == "BUMP_SUCCESS":
            print(f"   [✅ 성공 - {당근매물번호}] 다차원 가격 조율 및 정통 끌어올리기 최종 마감 완료 V")
            self.끌어올리기_성공_개수 += 1
            return True
            
        elif 결과_코드명사 == "PRICE_UPDATE_SUCCESS":
            print(f"   [✅ 성공 - {당근매물번호}] 쿨타임 제한 매물 가격만 변경 처리 최종 완료 V")
            self.수정업데이트_성공_개수 += 1
            return True
        
        elif 결과_코드명사 == "RESCUE_BUMP_SUCCESS":
            # 🚀 [대통합 치료 완료] 이제 쿨타임 중 구출이든 정통 끌올 중 구출이든 누락 없이 완벽히 이쪽으로 모입니다!
            print(f"   [✅ 성공 - {당근매물번호}] '숨김' 유령 상태 해제 및 활성 트랙 구출 완수 V")
            self.숨김해제_성공_개수 += 1
            self.데이터베이스_광고시작종료일_최신화(당근매물번호) # 🛑 가로채기 당해 씹히던 30일 수명 연장 쿼리 완벽 결속!
            return True       
            
        elif 결과_코드명사 == "NO_CHANGE_SKIP":
            print(f"   [  동결 - {당근매물번호}] 쿨타임 제한 매물 일치 확인 ➡️ 가격 변동 없음 스킵 V")
            return True
            
        else:
            # FAIL인 경우
            return False

    # =================================================================
    # 🔓 [독립 신설] 수정 방식 사후 검속용 DB 상태 단독 조회기
    # =================================================================
    def 새홈매물번호_조회(self, 당근매물번호):
        """ 당근 매물번호에 매핑된 새홈매물번호(우리 기본키)를 조회한다 """
        import pymysql
        try:
            연결고리 = pymysql.connect(host='obangkr.cafe24.com', user='obangkr', password='Ddhqkd!1', database='obangkr', charset='utf8')
            명령조수 = 연결고리.cursor(pymysql.cursors.DictCursor)
            명령조수.execute("SELECT object_code_new FROM pr_externalad WHERE ad_code = %s AND ad_site = '당근' AND ad_del = 'N' LIMIT 1", (str(당근매물번호),))
            행 = 명령조수.fetchone()
            명령조수.close(); 연결고리.close()
            return 행['object_code_new'] if 행 else ''
        except Exception as 오류:
            print(f"   [❌ 오류 - {당근매물번호}] 새홈매물번호 조회 실패: {오류}")
            return ''

    def 끌올관측_기록(self, 당근매물번호, 현재_상태, 날짜_텍스트):
        """
        이 매물을 오늘 본 그대로 pr_log에 한 줄 남긴다(log_item='당근끌올관측').

        [왜 남기는가 — 2026-09-05 사용자 지시]
        당근의 두 규칙을 우리가 모른다: ① 끌올 쿨타임이 언제 몇 일로 바뀌는지
        (실측 14일이지만 과거 5일이던 시기가 있었다 — 고정값이 아니다) ② 끌올하지 않고 방치하면
        언제 노출이 끊기는지(= 실질 광고종료일). 둘 다 한 시점을 아무리 정밀하게 재도 알 수 없고,
        매일 같은 값을 찍어 시계열로 쌓아야만 보인다. 그래서 관측을 남긴다.

        [결과코드를 반드시 함께 남기는 이유]
        '숨김'에는 당근이 자동으로 내린 것과 우리가 내린 것이 섞여 있다(2026-09-05 확인: 판매중인데
        16일 방치된 매물과 숨김인데 20시간밖에 안 된 매물이 공존). 결과코드가 있어야 나중에
        '우리가 손대지 않은 매물'만 골라 자연 전이를 계산할 수 있다 —
        RESCUE_BUMP_SUCCESS(우리가 숨김해제) / NO_CHANGE_SKIP(손 안 댐)이 그 구분자다.
        """
        관측 = getattr(self, '최근_끌올관측', {}) or {}
        새홈매물번호 = self.새홈매물번호_조회(당근매물번호)
        기록 = {
            '당근번호': str(당근매물번호),
            '상태': 현재_상태,
            '날짜표시': 날짜_텍스트,
            '팝업제목': 관측.get('팝업제목', ''),      # 당근이 알려준 남은 쿨타임 원문
            '쿨타임여부': 관측.get('쿨타임여부', None),
            '결과코드': 관측.get('결과코드', ''),
        }
        try:
            로그저장(
                log_target=(새홈매물번호 or str(당근매물번호)),   # 새홈번호로 통일(사용자 확정) — 못 찾으면 당근번호로 대체
                log_item='당근끌올관측',
                log_value=json.dumps(기록, ensure_ascii=False),
                admin_id='SYSTEM'
            )
        except Exception as 오류:
            # 관측 실패가 본작업을 막지 않게 한다 — 기록은 부수적인 일이다
            print(f"   [⚠️ 관측기록 실패 - {당근매물번호}] {오류}")
        finally:
            self.최근_끌올관측 = {}   # 다음 매물에 이전 값이 새어나가지 않게 비운다
    def 데이터베이스_매물상태_조회(self, 당근매물번호):
        """ 당근 매물 번호에 매핑된 새홈 원본 매물의 현재 노출 상태(object_status)를 직통 조회 """
        import pymysql
        try:
            연결고리 = pymysql.connect(host='obangkr.cafe24.com', user='obangkr', password='Ddhqkd!1', database='obangkr', charset='utf8')
            명령조수 = 연결고리.cursor(pymysql.cursors.DictCursor)
            조회쿼리 = """
                SELECT o.object_status 
                FROM pr_externalad AS e
                JOIN pr_object AS o ON e.object_code_new = o.object_code_new
                WHERE e.ad_code = %s AND e.ad_site = '당근' LIMIT 1
            """
            명령조수.execute(조회쿼리, (str(당근매물번호),))
            행 = 명령조수.fetchone()
            명령조수.close(); 연결고리.close()
            return 행['object_status'] if 행 else ""
        except:
            return ""

    # =================================================================
    # 🛠️ [정상 구조 안착] 사장님 특명 반영 가격 수정 및 상태 반전 제어 엔진
    # =================================================================
    def 수정방식_업데이트_실행(self, 매물_행_객체, 당근매물번호):
        """ [수정] 버튼 진입 후 DB 스펙에 맞춘 금액 동기화 처리 및 메인 복귀 후 상태 반전 마킹 최종 완수 """
        try:
            # 1단계: 수정 폼 페이지 진입
            print(f"   [🔎 디버그 - {당근매물번호}] 1단계: 수정 버튼 클릭 및 수정 페이지 진입 시도...")
            수정_버튼 = 매물_행_객체.find_element(By.XPATH, ".//button[text()='수정']")
            수정_버튼.click()
            time.sleep(2.5) # 양식 폼 렌더링 안정화 대기 마진
            
            # 2단계: DB 실시간 다중 가격 스펙 수집 및 양식 동기화 토글
            DB_유효_가격목록 = 데이터베이스_다중_가격스펙_전수조회(당근매물번호, "당근")
            if not DB_유효_가격목록:
                print(f"   [⚠️ 경고 - {당근매물번호}] 유효한 DB 가격 스펙이 없어 양식 수정을 캔슬하고 백업 복귀합니다.")
                self.브라우저.back()
                return False

            target_types = [x['종류'] for x in DB_유효_가격목록]
            print(f"   [🔎 가격 동기화 - {당근매물번호}] 2단계: 수정 페이지 내 거래방식 가격셋({target_types}) 매핑 시작...")
            
            # daangn.py 가격 입력 알고리즘을 이식하여 기존 체크박스 유무에 따른 동적 가상 토글 제어 가동
            전체_유형 = ["매매", "전세", "월세", "단기"]
            for t_name in 전체_유형:
                try:
                    cb_xpath = f"//span[contains(@class, 'seed-checkbox__label') and text()='{t_name}']/parent::label"
                    cb_label = self.브라우저.find_element(By.XPATH, cb_xpath)
                    is_checked = cb_label.get_attribute("data-checked") is not None
                    should_be_checked = t_name in target_types
                    
                    if should_be_checked != is_checked:
                        self.브라우저.execute_script("arguments[0].click();", cb_label)
                        time.sleep(0.2)
                except:
                    pass

            time.sleep(0.4) # 입력창 가로 확장 버퍼 마진

            # 활성화된 입력창 영역에 리액트 가상돔 강제 주입 엔진으로 정밀 숫자 기입
            for item in DB_유효_가격목록:
                t_name = item["종류"]
                try:
                    if t_name == "매매":
                        el = self.브라우저.find_element(By.XPATH, "//span[@class='t4-bold text-fg-neutral' and text()='매매']/following::input[@type='number'][1]")
                        self.리액트_입력창_값_강제주입(el, str(item["매매가"]))
                    elif t_name == "전세":
                        el = self.브라우저.find_element(By.XPATH, "//span[@class='t4-bold text-fg-neutral' and text()='전세']/following::input[@type='number'][1]")
                        self.리액트_입력창_값_강제주입(el, str(item["보증금"]))
                    elif t_name == "월세" or t_name == "단기":
                        el_dep = self.브라우저.find_element(By.XPATH, f"//span[@class='t4-bold text-fg-neutral' and text()='{t_name}']/following::input[@type='number'][1]")
                        el_rent = self.브라우저.find_element(By.XPATH, f"//span[@class='t4-bold text-fg-neutral' and text()='{t_name}']/following::input[@type='number'][2]")
                        self.리액트_입력창_값_강제주입(el_dep, str(item["보증금"]))
                        self.리액트_입력창_값_강제주입(el_rent, str(item["월세"]))
                    print(f"   [✍️ 양식 수정수행 - {당근매물번호}] [{t_name}] 가격 세부 수치 금액 동기화 주입 완료")
                except Exception as 가격오류:
                    print(f"   [❌ 가격 입력 누락 - {당근매물번호}] {t_name} 금액창 컴포넌트 타격 실패: {가격오류}")

            # 3단계: 매물 수정 완료 버튼 최종 제출
            print(f"   [🔎 디버그 - {당근매물번호}] 3단계: [매물 수정] 폼 저장 승인 단추 터치...")
            try:
                수정완료_버튼 = self.브라우저.find_element(By.XPATH, "//button[text()='매물 수정' or contains(text(), '수정 완료') or text()='수정']")
                self.브라우저.execute_script("arguments[0].click();", 수정완료_버튼)
            except:
                print(f"   [⚠️ 버튼 유실 - {당근매물번호}] 수정 완료 저장 단추 가닥을 잡지 못해 백업 뒤로가기 우회")
                self.브라우저.back()
                return False

            # 비동기 저장 통신 및 메인 대시보드 리스트 목록 조회 화면 복귀 대기
            WebDriverWait(self.브라우저, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "form input[placeholder*='지번']"))
            )
            time.sleep(1.5)

            # 4단계: 재조회 및 상태값 정밀 상호 교차 사후 검속 보정 벨트 가동
            print(f"   [🔎 디버그 - {당근매물번호}] 4단계: 매물 락 해제 및 반전 제어를 위한 검색어 재입력...")
            당근매물번호_검색창_입력(self.브라우저, 당근매물번호)
            
            if self.검색결과_목록개수_확인(당근매물번호) == 1:
                새_매물_행 = self.브라우저.find_element(By.CSS_SELECTOR, "div.flex.w-full.cursor-pointer.items-center.border-b")
                현재_상태 = self.매물상태_확인(새_매물_행, 당근매물번호)
                DB_상태 = self.데이터베이스_매물상태_조회(당근매물번호)
                
                print(f"   [🔎 상태 교차 분석 - {당근매물번호}] 당근화면표시: '{현재_상태}' ↔️ DB원본진행: '{DB_상태}'")
                
                # 🔄 [시나리오 A] DB는 활성 중개요청인데 당근은 완료 수면 상태일 때 ➡️ 판매중 구출 작전
                if DB_상태 == "중개요청" and 현재_상태 == "거래완료":
                    print(f"   [🔓 상태반전 활성화 - {당근매물번호}] '거래완료' 수면 상태 포착 ➡️ 표준 명찰 더보기 클릭")
                    더보기_버튼 = 새_매물_행.find_element(By.XPATH, ".//button[@aria-haspopup='menu']")
                    try: 더보기_버튼.click()
                    except: self.브라우저.execute_script("arguments[0].click();", 더보기_버튼)
                    time.sleep(0.8)
                    
                    변경_옵션 = WebDriverWait(self.브라우저, 3).until(
                        EC.element_to_be_clickable((By.XPATH, "//div[@role='menu' and @data-state='open']//*[text()='판매중으로 변경']"))
                    )
                    self.브라우저.execute_script("arguments[0].click();", 변경_옵션)
                    time.sleep(0.5)
                    # 확인창클릭(self.브라우저, 선택='확인', timeout=1)
                    print(f"   [✅ 상태부활 마감 - {당근매물번호}] '판매중으로 변경' 락 격파 및 활성 트랙 복귀 완수 V")
                    time.sleep(1.0)
                    
                # 🔒 [시나리오 B] DB는 이미 완료/종결인데 당근은 살아 숨 쉴 때 ➡️ 숨기기 예방 가드 작전
                elif DB_상태 != "중개요청" and 현재_상태 == "판매중":
                    print(f"   [🔒 상태반전 은닉 - {당근매물번호}] DB 종결 매물 당근 과노출 포착 ➡️ 표준 명찰 더보기 클릭")
                    더보기_버튼 = 새_매물_행.find_element(By.XPATH, ".//button[@aria-haspopup='menu']")
                    try: 더보기_버튼.click()
                    except: self.브라우저.execute_script("arguments[0].click();", 더보기_버튼)
                    time.sleep(0.8)
                    
                    변경_옵션 = WebDriverWait(self.브라우저, 3).until(
                        EC.element_to_be_clickable((By.XPATH, "//div[@role='menu' and @data-state='open']//*[text()='숨기기']"))
                    )
                    self.브라우저.execute_script("arguments[0].click();", 변경_옵션)
                    time.sleep(0.5)
                    확인창클릭(self.브라우저, 선택='확인', timeout=1, unattended=self.unattended)
                    print(f"   [✅ 상태은닉 마감 - {당근매물번호}] '숨기기' 락 격파 및 은닉 트랙 전송 완수 V")
                    time.sleep(1.0)

            print(f"   [✅ 성공 - {당근매물번호}] 수정방식 데이터 동기화 및 상태 교정 대마감")
            self.수정업데이트_성공_개수 += 1
            return True
        except Exception as 오류:
            print(f"   [❌ 오류 - {당근매물번호}] 수정방식 업데이트 고도화 시퀀스 도중 최종 실패: {오류}")
            return False

    def 비공개_완료처리_실행(self, 매물_행_객체, 당근매물번호):
        """ 점 세개(...) 메뉴를 클릭하여 해당 매물을 비공개(광고 종료/숨기기) 처리 """
        try:
            print(f"   [🔎 디버그 - {당근매물번호}] 우측 관리탭 점 세개(...) 제어 버튼 탐색 중...")
            더보기_버튼 = 매물_행_객체.find_element(By.XPATH, ".//button[contains(@id, 'radix-') and .//*[local-name()='svg']]")
            더보기_버튼.click()
            time.sleep(0.6)
            
            print(f"   [🔎 디버그 - {당근매물번호}] 하부 레이어 팝업 메뉴 노출 감지. 종료/숨기기 탭 저격 중...")
            비공개_메뉴_선택 = WebDriverWait(self.브라우저, 3).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@role='menuitem' or @class='seed-context-menu']//*[contains(text(),'종료') or contains(text(),'숨기기')]"))
            )
            비공개_메뉴_선택.click()
            time.sleep(1.2)
            
            print(f"   [✅ 성공 - {당근매물번호}] 거래완료 비공개 전환 마감")
            return True
        except Exception as 오류:
            print(f"   [❌ 오류 - {당근매물번호}] 점 세개 레이어 팝업 제어 중 비공개 실패: {오류}")
            return False


    def 업데이트_프로세스_총괄(self):
        """ 당근 매물 최신화 프로세스 총괄 컨트롤러 """
        당근_업데이트_목록 = self.데이터.get('당근_업데이트목록', []) 
        총_작업량 = len(당근_업데이트_목록)
        
        print(f"[🔎 디버그] 당근 업데이트 대상 데이터셋 목록: {당근_업데이트_목록}")
        if 총_작업량 == 0:
            print("[🔎 디버그] 당근부동산 최신화 업데이트 대상 매물이 없어 프로세스를 스킵합니다.")
            return

        for 현재_인덱스, 당근매물번호 in enumerate(당근_업데이트_목록, 1):
            print(f"\n👉 [당근업데이트 사이클 {현재_인덱스}/{총_작업량}] 당근매물번호 {당근매물번호} 처리 시작")
            # 최상단알림창(f"\n👉 [당근업데이트 사이클 {현재_인덱스}/{총_작업량}] 당근매물번호 {당근매물번호} 처리 시작")

            # 🔥 [가로채기 출력 실행] 번호를 잡자마자 크롬 제어 전에 DB 전체 레코드를 가로 한 줄로 먼저 뿜어냅니다.
            self.데이터베이스_전체_정보_출력(당근매물번호)
            
            if self.진행상황_알림함수:
                # 🎯 [수치 교정] 현재 작업 중인 녀석을 제외한 '진짜 완료된 개수'만 프로그레스바에 반영하고 문구를 '처리 중'으로 변경합니다.
                self.진행상황_알림함수(현재_인덱스 - 1, 총_작업량, f"🔄 당근 업데이트 진행 중... ({현재_인덱스}/{총_작업량}번째 매물 처리 중) | 건너뜀: {self.건너뜀_개수}개")
            
            당근매물번호_검색창_입력(self.브라우저, 당근매물번호)
            
            if self.검색결과_목록개수_확인(당근매물번호) != 1:
                print(f"   [⚠️ 경고 - {당근매물번호}] 검색된 행이 고정 1개가 아니므로 안전을 위해 스킵합니다.")
                self.건너뜀_개수 += 1
                continue
                
            매물_행 = self.브라우저.find_element(By.CSS_SELECTOR, "div.flex.w-full.cursor-pointer.items-center.border-b")
            
            # 🎯 [순서 교체] 상태를 체크하기 전에 날짜와 끌올 버튼 활성화 여부를 먼저 계측합니다.
            날짜_텍스트, 끌올_버튼_존재여부 = self.날짜및_끌어올리기_가능여부_확인(매물_행, 당근매물번호)
            현재_상태 = self.매물상태_확인(매물_행, 당근매물번호)
            
            # 🔥 [가드 확장 완료] 사장님 지침 반영: '거래완료' 명찰을 단 매물도 스킵 대상에서 전격 제외시켜 통과시킵니다!
            if 현재_상태 not in ["숨김", "미노출", "판매중", "거래완료"] or (현재_상태 == "판매중" and not 끌올_버튼_존재여부):
                print(f"   [⚠️ 경고 - {당근매물번호}] 수집 대상 외 상태이거나 끌올 쿨타임이 안 지난 매물('{현재_상태}')이므로 스킵합니다.")
                self.건너뜀_개수 += 1
                continue
            
            작업_성공_여부 = False
            if 끌올_버튼_존재여부:
                print("끌올버튼 있음")
                # 🎯 [전달 파이프 연동] 목록에서 수집한 '현재_상태' 인자값을 마스터 일꾼 함수에 함께 주입합니다.
                작업_성공_여부 = self.끌어올리기_실행(매물_행, 당근매물번호, 현재_상태)
            else:
                print("끌올버튼 없음")
                작업_성공_여부 = self.수정방식_업데이트_실행(매물_행, 당근매물번호)

            # 오늘 본 그대로 한 줄 남긴다 — 쿨타임이 언제 바뀌는지, 방치 시 언제 노출이 끊기는지는
            # 매일 쌓아야만 알 수 있다(끌올관측_기록 주석 참고). 기록 실패는 본작업을 막지 않는다.
            self.끌올관측_기록(당근매물번호, 현재_상태, 날짜_텍스트)

            # pyautogui.alert("이상유무확인")  
            if 작업_성공_여부:
                self.최종완료_개수 += 1

    def 거래완료_비공개_프로세스_총괄(self):
        """ 당근 완료 매물 비공개 처리 총괄 컨트롤러 """
        당근_완료_목록 = self.데이터.get('당근_거래완료목록', [])
        총_작업량 = len(당근_완료_목록)
        
        print(f"[🔎 디버그] 당근 비공개 처리 대상 데이터셋 목록: {당근_완료_목록}")
        if 총_작업량 == 0:
            print("[🔎 디버그] 당근부동산 비공개 처리 대상 매물이 없어 프로세스를 스킵합니다.")
            return

        for 현재_인덱스, 당근매물번호 in enumerate(당근_완료_목록, 1):
            print(f"\n👉 [당근비공개 사이클 {현재_인덱스}/{총_작업량}] 당근매물번호 {당근매물번호} 처리 시작")
            
            if self.진행상황_알림함수:
                # 🎯 텍스트 가독성을 현재 처리 중인 순번으로 명확하게 일치시킵니다.
                self.진행상황_알림함수(현재_인덱스 - 1, 총_작업량, f"🔒 당근 완료 매물 비공개 전환 중... ({현재_인덱스}/{총_작업량}번째 처리 중)", mode='indeterminate')
                
            당근매물번호_검색창_입력(self.브라우저, 당근매물번호)
            
            if self.검색결과_목록개수_확인(당근매물번호) == 1:
                매물_행 = self.브라우저.find_element(By.CSS_SELECTOR, "div.flex.w-full.cursor-pointer.items-center.border-b")
                if self.비공개_완료처리_실행(매물_행, 당근매물번호):
                    self.비공개완료_성공_개수 += 1
            else:
                print(f"   [⚠️ 경고 - {당근매물번호}] 비공개 처리 대상 매물이 화면에 검색되지 않아 스킵합니다.")
                self.건너뜀_개수 += 1

    def run(self):
        """ 당근 일꾼 엔진 구동 제어 허브 """
        print("\n==================================================")
        print("▶ [당근부동산 일꾼] 자동화 제어 기동")
        print("==================================================")
        
        # 🔥 이식 완료: daangn.py의 주소 로드 및 실시간 세션 검증 프로세스 가동
        self.로그인확인_및_페이지로드_안정화()
        
        if self.모드 in ['all', 'update_only']:
            print("[🔎 디버그] 1단계: 당근 최신화 업데이트 프로세스 가동")
            self.업데이트_프로세스_총괄()
        # pyautogui.alert("비공개 프로세스 시작?")    
        if self.모드 in ['all', 'close_only']:
            print("\n[🔎 디버그] 2단계: 당근 거래완료 매물 비공개 일괄 처리 가동")
            self.거래완료_비공개_프로세스_총괄()
            
        print("\n[🔎 디버그] 당근부동산 일꾼 할당 작업 최종 마감 완료.")
        return self.최종완료_개수, self.끌어올리기_성공_개수, self.수정업데이트_성공_개수, self.비공개완료_성공_개수, self.건너뜀_개수, self.숨김해제_성공_개수