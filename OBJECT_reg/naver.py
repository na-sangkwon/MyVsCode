from selenium import webdriver
from selenium.webdriver import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait

from selenium.webdriver.chrome.options import Options

import pyautogui
import time
import traceback
import register
import re
import pymysql
import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta

import os
import sys
# 🚀 상위 폴더의 패키지를 인식할 수 있도록 시스템 경로(sys.path)에 추가하는 마법의 코드
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# 이제 공용 함수를 내 파일 안에 있는 것처럼 자유롭게 불러옵니다!
from util.property_utils import 건축법상건축물용도로변환

options = Options()

options.add_argument("--disable-blink-features=AutomationControlled")



from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QMessageBox
class NaverThread(QThread):
    ask_confirmation = pyqtSignal(str)  # 확인 메시지 요청 시그널
    finished = pyqtSignal(bool)        # 작업 완료 신호 (True: 성공, False: 실패)

    def __init__(self, data, user):
        super().__init__()
        self.data = data
        self.user = user
        self.continue_work = True      # 작업을 계속할지 여부
        # [2026-09-03 추가] 웹 버튼 → 로컬도우미로 헤드리스 실행될 때 True로 설정된다(local_helper.py
        # run_naver_extend_headless() 참고). 원래 이 매크로는 데스크톱(test.exe)에서 사람이 화면을
        # 보며 쓰던 것이라 최상단알림창()이 전부 사람이 눌러줘야 넘어가는 모달 팝업인데, 헤드리스
        # 실행에선 아무도 클릭해줄 사람이 없어 그대로 무한정 멈춰버리는 문제가 실사용 중 발견됐다
        # (기간만료매물확인 종료알림 팝업에서 멈춤). 데스크톱 사용자 경험은 그대로 두고 싶어서
        # 팝업 자체를 없애지 않고, headless일 때만 최상단알림창()이 화면에 띄우지 않도록 분기한다.
        self.headless = False
        self.headless_notes = []  # headless일 때 최상단알림창() 대신 여기에 메시지를 쌓아둔다
        # [2026-09-03 추가 — 사용자 요청] "연장등록이 실제로 어느 코드 경로를 탔는지" 진단하려면
        # 이 프로세스가 어디에도 print()를 못 남기는 상황(local_helper/main.py가 DETACHED_PROCESS로
        # 표준출력을 안 연결함)에서도 확인할 방법이 필요했다. headless_notes(→ pr_log의 "중간 알림")는
        # 담당자가 보는 연장등록 이력 화면에 그대로 노출되므로, 개발 진단용 문구를 거기 섞으면 안 된다
        # — 대신 이미 있는 일반 오류로그(pr_error_log, main.py::report_error_to_server()가 API로
        # 보고) 채널을 재사용한다. run_naver_extend_headless()가 이 콜백을 채워준다 — 데스크톱
        # (test.exe) 실행처럼 안 채워지면 진단_기록()은 조용히 아무 것도 하지 않는다.
        self.report_error = None

    # [2026-09-05 신규 — 사용자 요청] 예상 못 한 예외를 개발자용 오류로그(pr_error_log)에 보고한다.
    # 원래 run()의 catch-all들은 예외를 pyautogui.alert/최상단알림창으로만 알렸는데, headless
    # 실행에선 그게 headless_notes(→ 담당자가 보는 연장등록 이력 pr_log)에만 쌓이고 개발자용
    # 오류로그에는 아무것도 안 남아, 크롬드라이버 확보 실패(Unable to obtain driver for chrome,
    # 2026-09-05 매물 920585)의 원인을 오류로그 화면에서 전혀 확인할 수 없었다.
    #
    # run() 안의 중첩함수 진단_기록()을 쓰지 않고 클래스 메서드로 둔 이유가 둘 있다. (1) run()의
    # 바깥쪽 catch-all은 그 중첩함수가 정의되기 전 단계의 예외(예: 서두 데이터 검증)도 잡기 때문에,
    # 거기서 중첩함수를 부르면 오히려 "이름 없음" 2차 예외가 난다. (2) 진단_기록()은 정상 경로를
    # 추적하는 용도(severity='diag')라, 실제 실패(Exception)와 오류로그에서 섞이면 안 된다.
    def report_unexpected_exception(self, exc, 발생지점):
        # report_error는 headless 실행일 때만 채워지는 콜백이라(local_helper/main.py의
        # run_naver_extend_headless() 참고) 데스크톱(test.exe) 실행에선 None이다 — 그때는 조용히 넘어간다.
        보고 = getattr(self, 'report_error', None)
        if not 보고:
            return
        # 예외가 실제로 터진 가장 안쪽 프레임의 파일/줄번호 — 스택트레이스를 다 읽지 않아도
        # 오류로그 목록에서 바로 발생 위치가 보이게 함께 넘긴다.
        발생파일, 발생줄 = None, None
        프레임들 = traceback.extract_tb(exc.__traceback__)
        if 프레임들:
            발생파일, 발생줄 = 프레임들[-1].filename, 프레임들[-1].lineno
        # 이 콜백은 보고에 실패해도 절대 예외를 올리지 않게 설계돼 있어
        # (main.py::report_error_to_server() 참고) 호출부에서 따로 try/except로 감싸지 않는다.
        보고(f"[연장등록 예상밖오류] {발생지점}: {exc}",
           file=발생파일, line=발생줄, stack=traceback.format_exc(), severity='Exception')

    def run(self): #run 함수는 QThread 클래스의 핵심 메서드로, 스레드가 시작될 때 즉,start()를 호출하면 자동으로 실행
        # [2026-09-03 추가] 이 파일 곳곳에서 pyautogui.alert()를 직접 호출하는 곳이 최상단알림창()
        # 말고도 20곳 넘게 있다(오류 상황 알림 등) — 전부 개별적으로 고치는 대신, headless일 때
        # pyautogui.alert 자체를 이 스레드 안에서만 가로채서 화면에 띄우지 않고 headless_notes에
        # 기록하도록 한다. pyautogui는 모듈 전역이라 이렇게 덮어쓰면 이 스레드가 실행되는 동안 이
        # 프로세스 안의 모든 pyautogui.alert 호출에 적용된다 — 이 프로세스는 애초에 매물 하나(또는
        # 배치)의 연장등록 하나만 전담하고 끝나는 프로세스라(local_helper.py run_naver_extend_headless
        # 참고) 다른 스레드와 충돌할 일이 없다. 반환값(버튼 텍스트)을 쓰는 호출부는 없는 것으로
        # 확인했지만, 혹시 몰라 실제 pyautogui.alert의 기본 반환값인 'OK'를 그대로 돌려준다.
        if self.headless:
            def _headless_alert(text='', title='', button='OK', **kwargs):
                # [2026-09-03 추가 — 진단용] 이 alert가 except 블록 안에서 호출된 것이라면(예:
                # "오류 발생: {e}") sys.exc_info()에 그 예외가 아직 걸려있으므로, 어느 줄에서
                # 무슨 예외가 났는지 전체 스택트레이스를 함께 남긴다 — str(e) 한 줄만으로는 원인
                # 위치를 알 수 없어서(getAttribute.js 관련 오류의 정확한 발생 지점을 못 찾음).
                tb = traceback.format_exc()
                note = text if tb.strip() == 'NoneType: None' else f"{text}\n[스택트레이스]\n{tb}"
                self.headless_notes.append(note)
                print(f"[headless — pyautogui.alert 대신 기록됨] {title}: {note}")
                return button
            pyautogui.alert = _headless_alert
        try:
            if not self.data:
                pyautogui.alert(f"사용되지 않는 매물번호이거나 매물데이터가 없습니다.\n\n data:\n{self.data}")
                self.finished.emit(False)
                return                
            # adData = self.data.get('adData', {}).get('네이버', {})
            # pyautogui.alert(f"데이터 테스트중...\n\n adData:\n{adData}")
            ad_naver_list = self.data.get('adData', {}).get('네이버', [])
            if isinstance(ad_naver_list, list):  # 여러 개의 만료 광고 처리
                if len(ad_naver_list) == 0:
                    pyautogui.alert(f"더이상 업데이트할 매물이 존재하지 않습니다.")
                    return  
                else:
                    if not self.wait_for_confirmation(f"광고가 종료된 매물들(총 {str(len(ad_naver_list))}건)을 모두 업데이트하시겠습니까?\n\n확인: 네이버부동산 매물업데이트\n취소: 대상 매물번호들 클립보드 복사후 종료"):
                        import pyperclip
                        object_code_list = [ad.get('object_code_new', '') for ad in ad_naver_list if ad.get('object_code_new')]
                        object_codes_str = ','.join(object_code_list) # 쉼표로 연결된 문자열 생성
                        pyperclip.copy(object_codes_str) # 쉼표로 연결된 문자열 생성
                        # QMessageBox.information(None, "복사 완료", f"매물번호가 복사되었습니다.\n{object_codes_str}")
                        pyautogui.alert(f"해당 매물번호들을 클립보드에 복사하였습니다.\n\n복사된 매물번호:\n{object_codes_str}")
                        # self.finished.emit(False)
                        return                        
                
                print("네이버 매물 등록 작업 시작")
    #함수설정     
            def 그룹별명칭변환(그룹, 대상명칭):
                # print("그룹별명칭변환 그룹:",그룹,", 대상명칭:",대상명칭)
                # 그룹별 변환 매핑
                변환사전 = {}

                if 그룹 == '건축물용도':
                    변환사전 = {
                        "단독주택": ["다가구주택", "단독주택외"],
                        "제1종 근린생활시설": ["근린생활시설", "소매점", "제1종근린생활시설"],
                        "제2종 근린생활시설": ["제2종근린생활시설"],
                        "노유자(老幼者: 노인 및 어린이)시설": ["노유자시설"],
                        "위락시설": ["여관"],
                        "교정(矯正) 및 군사 시설": ["교정군사시설"],
                        "자동차 관련 시설": ["자동차관련시설"],
                        "공동주택": ["다세대주택"],
                        "공장": ["제조업소"],
                    }
                elif 그룹 == '시설정보':
                    변환사전 = {
                        "마당": ["공터"],
                        "벽걸이에어컨": ["냉방기"],
                        "가스레인지": ["가스렌지"],
                        "인덕션레인지": ["인덕션"],
                        "전자레인지": ["전자렌지"],
                    }
                elif 그룹 == '관리비포함내역':
                    변환사전 = {
                        "공용관리비": ["공용전기"],
                        "기타관리비": ["공용수도"],
                        "전기료": ["개별전기"],
                        "수도료": ["개별수도"],
                        "TV사용료": ["TV"],
                    }
                elif 그룹 == '주용도':
                    변환사전 = {
                        "상가전용": ["상가점포"],
                        "사무실전용": ["사무실"],
                    }
                elif 그룹 == '지역(시/도)':
                    변환사전 = {
                        "전북특별자치도": ["전라북도"],
                    }
                elif 그룹 == '전문분야':
                    변환사전 = {
                        "원/투룸": ["주거용"],
                        "상가/사무실": ["상업용"],
                        "공장/창고": ["공업용"],
                    }
                elif 그룹 == '방특징':
                    변환사전 = {
                        "큰길가": ["중로접", "대로접"],
                    }
                elif 그룹 == '건축구조':
                    변환사전 = {
                        "철골조": ["일반철골구조"],
                        "철근콘크리트": ["철근콘크리트구조"],
                        "벽돌조": ["벽돌조"],
                    }
                elif 그룹 == '매물분류1차': #object_type1값으로 매물분류1차 선별
                    변환사전 = {
                        "원룸": ["원룸/오피"],
                        "주택": ["단독/전원"],
                        "상가점포": ["상가/점포"],
                        "빌딩건물": ["상가건물"],
                    }
                elif 그룹 == '매물분류2차':
                    변환사전 = {
                        "단독": ["단독주택"],
                        "주거용": ["주거용오피스텔"],
                        "다가구": ["다가구주택"],
                        "일반상가": ["무권리상가", "프랜차이즈"],
                        "상가건물": ["올근생(소형)", "올근생(대형)"],
                        "빌라": ["빌라/연립"],
                    }

                # 대상명칭이 변환 사전의 값 리스트에 포함되는지 확인
                for 변환된명칭, 명칭리스트 in 변환사전.items():
                    if 대상명칭 in 명칭리스트:
                        return 변환된명칭
                print("반환되는 대상명칭:",대상명칭)
                # 매핑되지 않으면 원래 값을 반환
                return 대상명칭
            
            def 목록_변환(그룹, 항목들):
                변환된_항목들 = []
                for 항목 in 항목들.split(','):
                    변환된_항목들.append(그룹별명칭변환(그룹, 항목.strip()))
                return ','.join(변환된_항목들)    

            def 제곱미터_평_변환(제곱미터):
                평 = float(제곱미터) / 3.3058
                return str(round(평, 1))  # 소수점 둘째 자리까지 반올림

            def 최상단알림창(message, title="알림"):
                # [2026-09-03 수정] headless(웹 트리거) 실행 중에는 이 팝업을 아무도 클릭해줄 사람이
                # 없어 그대로 멈춰버리는 문제가 실사용 중 발견됐다("기간만료매물확인 종료알림",
                # "비밀메모 채우기" 등에서 재현) — 이 함수는 어디서도 반환값을 쓰지 않는 단순 알림이라
                # (호출부 코드는 팝업을 누르든 안 누르든 뒤 로직이 똑같이 진행됨, 직접 확인함), 화면에
                # 띄우는 대신 메시지를 기억해뒀다가 최종 결과 보고에 함께 남기는 쪽이 안전하다(사용자
                # 요청). 데스크톱(test.exe) 사용자 경험은 그대로 유지하기 위해 headless일 때만 이렇게
                # 분기한다.
                if self.headless:
                    # [2026-09-03 추가 — 진단용] pyautogui.alert 쪽과 동일하게, except 블록 안에서
                    # 호출된 것이라면 스택트레이스도 함께 남긴다.
                    tb = traceback.format_exc()
                    note = message if tb.strip() == 'NoneType: None' else f"{message}\n[스택트레이스]\n{tb}"
                    self.headless_notes.append(note)
                    print(f"[headless — 알림창 대신 기록됨] {title}: {note}")
                    return
                root = tk.Tk()
                root.withdraw()  # 창 숨기기
                root.attributes("-topmost", True)  # 항상 위에 있도록 설정
                messagebox.showinfo(title, message)
                root.destroy()

            # [2026-09-03 신규 — 사용자 요청] "연장등록이 실제로 어느 코드 경로를 탔는지"(중복매물
            # 조기반환 vs 정상 등록 흐름 등) 진단하려던 중, 이 파일의 print()는 headless 실행 시
            # 어디에도 남지 않는다는 게 확인됐다(위 __init__의 self.report_error 설명 참고). 화면에는
            # 절대 안 띄우고(데스크톱 사용자 방해 안 함), self.report_error가 채워져 있을 때만
            # 일반 오류로그(pr_error_log)에 낮은 심각도로 남긴다 — 담당자가 보는 연장등록 이력에는
            # 안 섞이고, 다음 문제 발생 시 개발자가 오류로그 화면에서 추측 없이 바로 확인할 수 있다.
            def 진단_기록(message):
                if self.report_error:
                    self.report_error(f"[연장등록 진단] {message}", severity='diag')

            def 한글금액(금액):
                단위 = ["만원", "억", "조"]
                단위_금액 = []
                i = 0

                # 문자열일 때만 isdigit() 검사
                if isinstance(금액, str):
                    if 금액.isdigit():
                        금액 = int(금액)
                    else:
                        # 숫자가 아닌 문자열이면 예외 처리 또는 0 반환
                        return "0만원"
                elif not isinstance(금액, int):
                    # int도 아니면서 str도 아닌 경우, 예외 처리
                    return "0만원"
                # 만원 단위로 주어진 금액을 억, 조 등으로 나누어 변환
                while 금액 > 0:
                    금액, 나머지 = divmod(금액, 10000)  # 10000으로 나누어 몫과 나머지를 구함
                    if 나머지 > 0:
                        단위_금액.append(f"{나머지}{단위[i]}")
                    i += 1

                # 단위_금액 리스트를 거꾸로 뒤집어서 큰 단위가 먼저 오도록 함
                단위_금액 = 단위_금액[::-1]
                # 결과 문자열 생성
                결과 = ''.join(단위_금액)
                return 결과 if 결과 else "0만원" # 결과가 비어있으면 "0만원" 반환
            
            def 다시보지않기확인():      
                try:
                    # el = WebDriverWait(driver, 1, poll_frequency=0.1).until(
                    #     EC.visibility_of_element_located(
                    #         (By.XPATH, '//div[@class="v-overlay-container"]//span[text()="다시 보지 않기"]')
                    #     )
                    # )
                    # el.click()
                    # print("✅ '다시 보지 않기' 클릭 완료")   
                    driver.implicitly_wait(0)             

                    # 팝업 컨테이너가 나타날 때까지 최대 1초 대기
                    popup_xpath = '/html/body/div[2]/div'
                    popup = WebDriverWait(driver, 0.5, poll_frequency=0.1).until(
                        EC.presence_of_element_located((By.XPATH, popup_xpath))
                    )

                    # 팝업 내에서 "다시 보지 않기" 버튼 span 찾기
                    다시보지않기_버튼 = popup.find_element(By.XPATH, './/span[text()="다시 보지 않기"]')


                    # 요소가 보이면 클릭
                    if 다시보지않기_버튼.is_displayed():
                        driver.execute_script("arguments[0].click();", 다시보지않기_버튼)
                        print("✅ '다시 보지 않기' 클릭 성공")
                    else:
                        print("⚠️ '다시 보지 않기'는 존재하지만 표시되지 않았습니다.")
                    # # 클릭 (JS 사용해도 안전)
                    # driver.execute_script("arguments[0].click();", 다시보지않기_버튼)
                    # print("✅ '다시 보지 않기' 클릭 성공")

                    driver.implicitly_wait(10)

                except Exception as e:
                    print("알림: '다시 보지 않기' 텍스트가 화면에 나타나지 않았습니다.")

            def 확인메세지창승인():
                try:
                    # 확인 메시지 창이 생성될 때까지 대기 (10초로 설정)
                    alert = WebDriverWait(driver, 10).until(EC.alert_is_present())
                    # 확인 메시지 창 승인
                    alert.accept()
                except:
                    # 대기 시간 초과 또는 확인 메시지 창이 없는 경우 예외 처리
                    print("확인 메시지 창이 없습니다.")        
            
            def 특정tr요소(strong태그의텍스트):
                print(f"특정tr요소({strong태그의텍스트})")
                요청strong_text = strong태그의텍스트.replace(' ', '')
                try:
                    strong_elements = driver.find_elements(By.XPATH, f"//th/strong")
                    # print(f"'{strong태그의텍스트}' 텍스트를 가진 strong 태그의 개수: {len(strong_elements)}")
                    
                    # 각 strong 태그의 부모 tr 요소 찾기
                    for strong in strong_elements:
                        # HTML에서 텍스트 추출 후 모든 공백 및 줄바꿈 제거
                        strong_text = strong.get_attribute('textContent').replace('\n', '').replace('\r', '').replace(' ', '')
                        # print(f"공백과 줄바꿈을 제거한 strong_text vs 요청strong_text: {strong_text} vs {요청strong_text}")
                        # print(f"찾은 {strong.text} strong요소: {strong.get_attribute('outerHTML')}")
                        # strong 태그의 상위 th 태그를 거쳐 상위 tr 태그 찾기
                        tr_element = strong.find_element(By.XPATH, './ancestor::tr')
                        # print(f"찾은 {strong.text} tr요소: {tr_element.get_attribute('outerHTML')}")
                        return tr_element

                except Exception as e:
                    print(f"An error occurred: {e}")    
            
            def 특정위치의x번째입력태그찾기(strong태그의텍스트, tag_name, 몇번째):
                print(f"특정위치의x번째태그찾기({strong태그의텍스트}, {tag_name}, {몇번째})")
                try:      
                    요청strong_text = strong태그의텍스트.replace(' ', '')
                    # print("요청strong_text:"+요청strong_text)
                    # 모든 strong 요소를 찾아낸 후에 보이는 요소만 필터링
                    all_strong_elements = driver.find_elements(By.XPATH, "//th/strong")
                    visible_strong_elements = [elem for elem in all_strong_elements if elem.is_displayed()]
                    # print(f"보이는 strong태그 개수: {len(visible_strong_elements)}개")
                    # 각 strong 태그의 부모 tr 요소 찾기
                    for strong in visible_strong_elements:
                        # HTML에서 텍스트 추출 후 모든 공백 및 줄바꿈 제거
                        strong_text = strong.get_attribute('textContent').replace('\n', '').replace('\r', '').replace(' ', '')
                        # print("strong_text:"+strong_text)
                        # print(f"Found strong태그: {strong태그의텍스트} {strong.get_attribute('outerHTML')}")
                        if 요청strong_text == strong_text:
                            # strong 태그의 상위 th 태그를 거쳐 상위 tr 태그 찾기
                            # tr_element = strong.find_element(By.XPATH, './parent::tr')
                            tr_element = strong.find_element(By.XPATH, './ancestor::tr')
                            # print(f"Found tr_element 태그: {tr_element.get_attribute('outerHTML')}")
                            # 해당 tr 내의 td 요소들 찾기
                            td_elements = tr_element.find_elements(By.XPATH, './td')
                            # print(f"찾은 td태그 개수: {len(td_elements)}개")
                            visible_elements = []
                            # 원하는 태그만 찾기
                            for td in td_elements:
                                # print(f"Found td태그: {td.get_attribute('outerHTML')}")
                                
                                if tag_name == 'textarea':
                                    # elements = td.find_elements(By.XPATH, f'./div/div/div/div[3]/{tag_name}')
                                    # print("tag_name이 textarea입니다.")
                                    elements = td.find_elements(By.XPATH, f'.//textarea[contains(@class, "v-field__input")]')
                                else:
                                    elements = td.find_elements(By.XPATH, f'.//input[@type="{tag_name}"]')
                                # print(f"elements 개수: {len(elements)}개")
                                limit_count = 1
                                for elem in elements:
                                    # print(f"Found {tag_name} all element: {elem.get_attribute('outerHTML')}")
                                    if tag_name in ['checkbox', 'radio']:
                                        # print(f"Found {tag_name} element: {elem.get_attribute('outerHTML')}")
                                        visible_elements.append(elem)
                                    else:
                                        if elem.is_displayed():
                                            visible_elements.append(elem)
                                        #     print("요소가 보임")
                                        #     # print(f"Found {tag_name} element: {elem.get_attribute('outerHTML')}")
                                        # else:
                                        #     print("요소가 안보임")
                                        #     # print(f"{tag_name} element is not displayed: {elem.get_attribute('outerHTML')}")
                                if len(visible_elements) > 0: break
                            # print(f"visible_elements 개수: {len(visible_elements)}개")
                            # 원하는 태그 찾기
                            visible_tag_count = 0
                            for v_elem in visible_elements:
                                visible_tag_count += 1
                                if visible_tag_count == 몇번째:
                                    # print(f"{몇번째}번째 보이는 {tag_name} 태그를 찾았습니다.\n {td.get_attribute('outerHTML')}")
                                    return v_elem
                            break

                    # print(f"{몇번째}번째 보이는 {tag_name} 태그를 찾을 수 없습니다.")
                    return None

                except Exception as e:
                    print(f"An error occurred: {e}")
                    return None   
            
            def 라벨들로체크박스클릭(strong태그의텍스트, 체크박스_라벨들):
                print(f"라벨들로체크박스클릭({strong태그의텍스트}, [{체크박스_라벨들}])")
                """
                주어진 strong 텍스트를 포함하는 tr 요소 내의 체크박스들 중 주어진 라벨 텍스트와 일치하는 체크박스를 클릭하는 함수.

                Args:
                - driver: Selenium WebDriver 객체
                - strong태그의텍스트: 찾고자 하는 strong 태그의 텍스트
                - 체크박스_라벨들: 클릭하고자 하는 체크박스의 라벨 텍스트 목록 (리스트 형태)
                """
                try:
                    # 주어진 텍스트를 포함하는 strong 태그 찾기
                    # strong_elements = driver.find_elements(By.XPATH, f'//th//strong[contains(text(), "{strong태그의텍스트}")]')
                    strong_elements = driver.find_elements(By.XPATH, f'//th//strong[contains(normalize-space(.), "{strong태그의텍스트}")]')
                    # all_strong_elements = driver.find_elements(By.XPATH, '//th/strong')
                    if not strong_elements:
                        print(f"'{strong태그의텍스트}' 텍스트를 가진 strong 태그를 찾을 수 없습니다.")
                        return

                    # 각 strong 태그의 부모 tr 요소 찾기
                    print(f"strong_elements 개수:{str(len(strong_elements))}")
                    for strong in strong_elements:
                        # strong 태그의 상위 th 태그를 거쳐 상위 tr 태그 찾기
                        tr_element = strong.find_element(By.XPATH, './ancestor::tr')
                        # 이후의 모든 tr 요소를 검색하되 다음 strong을 가진 th가 나타날 때까지
                        following_trs = tr_element.find_elements(By.XPATH, './following-sibling::tr[not(.//th/strong)] | .//following-sibling::tr[.//th/strong and not(.//th/strong[normalize-space(.)="{strong태그의텍스트}"])]')
                        
                        print(f"tr 개수:{str(len([tr_element] + following_trs))}")
                        for tr in [tr_element] + following_trs:
                            # 해당 tr 내의 체크박스들 찾기
                            checkboxes = tr.find_elements(By.XPATH, './/input[@type="checkbox"]')
                            labels = tr.find_elements(By.XPATH, './/label')

                            # 체크박스와 라벨 매칭하여 클릭하기
                            for label in labels:
                                label_text = label.text.strip()
                                # print("label_text:"+label_text)
                                if label_text in 체크박스_라벨들:
                                    for checkbox in checkboxes:
                                        if checkbox.get_attribute("id") == label.get_attribute("for"):
                                            if not checkbox.is_selected():
                                                label.click()
                                            #     print(f"Clicked checkbox with label: {label_text}")
                                            # else:
                                            #     print(f"Checkbox with label '{label_text}' is already selected")

                except Exception as e:
                    print(f"An error occurred: {e}")    
                
            def 태그별개수출력(strong태그의텍스트):
                """
                주어진 strong 텍스트를 포함하는 tr 요소 내의 태그별 보이는 개수를 출력하는 함수.

                Args:
                - driver: Selenium WebDriver 객체
                - strong태그의텍스트: 찾고자 하는 strong 태그의 텍스트

                Returns:
                - 태그별 보이는 개수 (딕셔너리 형태)
                """
                try:
                    # 주어진 텍스트를 포함하는 strong 태그 찾기
                    # strong_elements = driver.find_elements(By.XPATH, f'//th//strong[contains(text(), "{strong태그의텍스트}")]')
                    strong_elements = driver.find_elements(By.XPATH, f'//th//strong[contains(normalize-space(.), "{strong태그의텍스트}")]')
                    
                    if not strong_elements:
                        print(f"'{strong태그의텍스트}' 텍스트를 가진 strong 태그를 찾을 수 없습니다.")
                        return None

                    # 각 strong 태그의 부모 tr 요소 찾기
                    for strong in strong_elements:
                        # strong 태그의 상위 th 태그를 거쳐 상위 tr 태그 찾기
                        tr_element = strong.find_element(By.XPATH, './ancestor::tr')
                        
                        # 해당 tr 내의 td 요소들 찾기
                        td_elements = tr_element.find_elements(By.XPATH, './/td')
                        visible_elements = []
                        
                        tag_types = ['input', 'select', 'textarea', 'button']
                        
                        for td in td_elements:
                            for tag in tag_types:
                                if tag == 'input':
                                    elements = td.find_elements(By.XPATH, f'.//{tag}[not(@type="radio")]')
                                    radio_elements = td.find_elements(By.XPATH, f'.//{tag}[@type="radio"]')
                                    elements.extend(radio_elements)
                                else:
                                    elements = td.find_elements(By.XPATH, f'.//{tag}')                        

                                for elem in elements:
                                    print(f"Found {tag} element: {elem.get_attribute('outerHTML')}")  # 디버깅 출력
                                    if elem.get_attribute('style') != 'display: none' and elem.get_attribute('style') != 'visibility: hidden':
                                        visible_elements.append(elem)
                                    # if elem.is_displayed():
                                    #     visible_elements.append(elem)

                        # 태그 별 개수 계산
                        input_count = len([elem for elem in visible_elements if elem.tag_name == 'input' and elem.get_attribute('type') != 'radio'])
                        select_count = len([elem for elem in visible_elements if elem.tag_name == 'select'])
                        radio_count = len([elem for elem in visible_elements if elem.get_attribute('type') == 'radio'])
                        button_count = len([elem for elem in visible_elements if elem.tag_name == 'button'])
                        textarea_count = len([elem for elem in visible_elements if elem.tag_name == 'textarea'])
                        
                        counts = {
                            'input': input_count,
                            'select': select_count,
                            'radio': radio_count,
                            'button': button_count,
                            'textarea': textarea_count
                        }

                        print(f"보이는 input 태그 개수: {input_count}")
                        print(f"보이는 select 태그 개수: {select_count}")
                        print(f"보이는 radio 태그 개수: {radio_count}")
                        print(f"보이는 button 태그 개수: {button_count}")
                        print(f"보이는 textarea 태그 개수: {textarea_count}")

                        return counts

                    return None

                except Exception as e:
                    print(f"An error occurred: {e}")
                    return None
                
            def 특정위치X번째셀렉트에서선택(strong태그명, X번째, 선택할항목):
                print(f"특정위치X번째셀렉트에서선택({strong태그명}, {X번째}, {선택할항목})")
                try:
                    strong태그명 = strong태그명.replace(' ', '')
                    strong_elements = driver.find_elements(By.XPATH, f"//th/strong")
                    # print(f"'{strong태그명}' 텍스트를 가진 strong 태그의 개수: {len(strong_elements)}")
                    # print(f"찾은 strong태그 개수: {len(strong_elements)}개")
                    # 각 strong 태그의 부모 tr 요소 찾기
                    for strong in strong_elements:
                        # HTML에서 텍스트 추출 후 모든 공백 및 줄바꿈 제거
                        strong_text = strong.get_attribute('textContent').replace('\n', '').replace('\r', '').replace(' ', '')

                        # print(f"Found strong태그: {strong태그명} {strong.get_attribute('outerHTML')}")
                        if strong태그명 == strong_text:
                            # strong 태그의 상위 th 태그를 거쳐 상위 tr 태그 찾기
                            tr_elements = strong.find_elements(By.XPATH, './ancestor::tr')

                            # 화면에 표시된 tr 요소 필터링
                            visible_tr_elements = [tr for tr in tr_elements if tr.is_displayed()]
                            # print(f"표시된 tr 요소 개수: {len(visible_tr_elements)}개")  

                            if not visible_tr_elements:
                                print("화면에 표시된 tr 요소가 없습니다.")
                                continue

                            # 첫 번째 표시된 tr 요소 선택
                            tr_element = visible_tr_elements[0]
                    
                            # 해당 tr 내의 td 요소들 찾기
                            td_elements = tr_element.find_elements(By.XPATH, './td')
                            # print(f"찾은 td 태그 개수: {len(td_elements)}개")

                            # 원하는 태그만 찾기
                            for td in td_elements:
                                # pyautogui.alert("check!!")
                                # print(f"Found td태그: {td.get_attribute('outerHTML')}")
                                # td 태그 내에서 t-select-area-group 또는 t-select-item 클래스를 가진 div 찾기
                                # target_divs = td.find_elements(By.XPATH, f".//div[@aria-haspopup='menu']//div[contains(@class, 'v-field__append-inner')]")
                                target_divs = td.find_elements(By.XPATH, f".//div[contains(@class, 't-select-area-group') or contains(@class, 't-select-item')]//div[@aria-haspopup='menu']")      
                                # print(f"target_divs 개수: {len(target_divs)}개")
                                # pyautogui.alert("check!!")
                                # 화면에 표시된 tr 요소 필터링
                                visible_target_divs = [div for div in target_divs if div.is_displayed()]
                                # print(f"표시된 div 요소 개수: {len(visible_target_divs)}개")  
                                if not visible_target_divs:
                                    print("화면에 표시된 div 요소가 없습니다.")
                                    continue                  
                                if X번째 <= len(visible_target_divs):
                                    target_div = visible_target_divs[X번째 - 1]  # X번째 요소 선택 (0부터 시작하므로 -1)
                                    # print(f"Found target_div태그: {target_div.get_attribute('outerHTML')}")
                                    # pyautogui.alert("check!!")
                                    # target_div 요소가 보일 때까지 대기
                                    # WebDriverWait(driver, 5).until(EC.visibility_of(target_div))
                                    # WebDriverWait(driver, 5).until(EC.element_to_be_clickable(target_div))         
                                    target_div.click()
                                    print("target_div 클릭완료!!")
                                    # 선택된 div 내부에서 선택할 항목에 해당하는 요소를 찾아 클릭                   
                                    # time.sleep(1)
                                    선택항목요소 = WebDriverWait(driver, 5).until(
                                        EC.element_to_be_clickable((By.XPATH, f"//div[@class='v-overlay-container']//div[contains(text(), '{선택할항목}')]"))
                                        # EC.element_to_be_clickable((By.XPATH, f"//div[@class='v-overlay-container']//div[text()='{선택할항목}']"))
                                    )
                                    # print(f"Found target_div태그: {선택항목요소.get_attribute('outerHTML')}")
                                    if 선택항목요소:
                                        선택항목요소.click()
                                        time.sleep(0.2)
                                        print(f"'{strong태그명}'필드의 '{X번째}'번째 셀렉트항목 '{선택할항목}'을 클릭했습니다.")
                                        break
                                    else:
                                        print(f"'{선택할항목}' 항목을 찾을 수 없습니다.")
                                else:
                                    print(f"주어진 위치에 {X번째}번째 셀렉트 박스가 존재하지 않습니다.")
                            # print(f"{X번째}번째 보이는 SELECT 태그를 찾을 수 없습니다.")        
                            break
                    
                    return None
                except Exception as e:
                    print(f"An error occurred: {e}")
                    
            def 라디오버튼선택(대상strong텍스트, 선택할텍스트):
                print(f"라디오버튼선택({대상strong텍스트}, {선택할텍스트})")
                try:
                    적용대상strong = driver.find_elements(By.XPATH, f'//th//strong[contains(text(), "{대상strong텍스트}")]')
                    # print(f"'{대상strong텍스트}' 텍스트를 가진 strong 태그의 개수: {len(적용대상strong)}")
                    
                    # 해당 strong 태그들이 속한 tr 태그 내에서 td 태그의 첫 번째 div 내에 있는 label의 텍스트 출력
                    for strong in 적용대상strong:
                        # strong 태그가 속한 tr 태그 찾기
                        tr_element = strong.find_element(By.XPATH, './ancestor::tr')
                        # 해당 tr 내의 td의 첫 번째 div 내에 있는 label 태그 찾기
                        label_elements = tr_element.find_elements(By.XPATH, './/td[1]//div//label')
                        # 각 label 태그의 텍스트 출력
                        for label in label_elements:
                            # print(f"Label 텍스트: {label.text}") 
                            if label.text==선택할텍스트:
                                label.click()     
                                # print(f"{대상strong텍스트}({label.text}) 클릭완료")   
                except Exception as e:
                    print(f"An error occurred: {e}")    

            def 선택된라디오버튼텍스트가져오기(대상strong텍스트):
                print(f"선택된라디오버튼텍스트가져오기({대상strong텍스트})")
                try:
                    # 1. 대상 strong 텍스트를 가진 strong 태그 찾기
                    적용대상strong_elements = driver.find_elements(By.XPATH, f'//th//strong[contains(text(), "{대상strong텍스트}")]')

                    if not 적용대상strong_elements:
                        print(f"'{대상strong텍스트}' 텍스트를 가진 strong 태그를 찾을 수 없습니다.")
                        return None

                    for strong_element in 적용대상strong_elements:
                        # 2. strong 태그가 속한 tr 태그 찾기
                        tr_element = strong_element.find_element(By.XPATH, './ancestor::tr')

                        # 3. 해당 tr 내에서 선택된 라디오 버튼의 부모 div.v-selection-control 찾기
                        #    선택된 라디오 버튼은 'v-selection-control--dirty' 클래스와 'mdi-radiobox-marked' 아이콘을 가집니다.
                        try:
                            # 'v-selection-control--dirty' 클래스를 가지는 v-selection-control div 찾기
                            selected_control_div = tr_element.find_element(By.XPATH, './/div[contains(@class, "v-selection-control") and contains(@class, "v-selection-control--dirty")]')

                            # 찾은 div 내에서 label 태그 찾기
                            selected_label = selected_control_div.find_element(By.TAG_NAME, 'label')
                            
                            print(f"'{대상strong텍스트}' 그룹에서 선택된 라디오 버튼: {selected_label.text}")
                            return selected_label.text

                        except Exception as inner_e:
                            # 해당 tr 내에 선택된 라디오 버튼이 없거나 찾기 실패 (다른 strong 태그에 대한 처리)
                            # print(f"경고: '{대상strong텍스트}' 그룹의 tr 내에서 선택된 라디오 버튼을 찾을 수 없습니다. ({inner_e})")
                            continue # 다음 strong 태그가 있다면 계속 시도

                    print(f"'{대상strong텍스트}' 그룹 내에서 선택된 라디오 버튼을 찾지 못했습니다.")
                    return None

                except Exception as e:
                    print(f"오류 발생: {e}")
                    return None
                

            def 숫자만_int(text):
                m = re.search(r'[\d,]+', text)
                return int(m.group(0).replace(',', '')) if m else 0


            def 네이버등록권_자동선택(driver, 최소충전금액=1580):
                wait = WebDriverWait(driver, 10)

                네이버등록권영역 = wait.until(EC.presence_of_element_located((
                    By.XPATH,
                    "//tr[.//th/strong[translate(normalize-space(), ' ', '')='네이버등록권']]"
                )))

                def radio_클릭(radio):
                    driver.execute_script(
                        "arguments[0].scrollIntoView({block: 'center'});",
                        radio
                    )
                    driver.execute_script("arguments[0].click();", radio)

                # 1순위: 등록권 사용 영역에서 잔여수량 있는 등록권 선택
                등록권사용테이블 = 네이버등록권영역.find_element(
                    By.XPATH,
                    ".//strong[normalize-space()='등록권 사용']"
                    "/ancestor::div[contains(@class,'wrap-title')]"
                    "/following-sibling::div[contains(@class,'t-table-column-det-group')][1]"
                    "//table"
                )

                for 행 in 등록권사용테이블.find_elements(By.XPATH, ".//tbody/tr"):
                    칸목록 = 행.find_elements(By.XPATH, "./td")
                    if len(칸목록) < 3:
                        continue

                    등록권명 = 칸목록[1].text.strip()
                    잔여수량 = 숫자만_int(칸목록[2].text.strip())

                    if 잔여수량 <= 0:
                        continue

                    radio = 행.find_element(By.XPATH, ".//input[@type='radio']")
                    if radio.get_attribute("disabled") is not None:
                        continue

                    radio_클릭(radio)
                    print(f"등록권 사용 선택완료: {등록권명}, 잔여수량={잔여수량}")
                    return "등록권사용"

                # 2순위: 등록권이 없으면 현재보유금액 확인 후 충전금 사용
                현재보유금액영역 = 네이버등록권영역.find_element(
                    By.XPATH,
                    ".//strong[normalize-space()='충전금 사용']"
                    "/ancestor::div[contains(@class,'wrap-title')]"
                )

                현재보유금액텍스트 = 현재보유금액영역.text
                현재보유금액 = 숫자만_int(현재보유금액텍스트)

                if 현재보유금액 >= 최소충전금액:
                    충전금사용테이블 = 네이버등록권영역.find_element(
                        By.XPATH,
                        ".//strong[normalize-space()='충전금 사용']"
                        "/ancestor::div[contains(@class,'wrap-title')]"
                        "/following-sibling::div[contains(@class,'t-table-column-det-group')][1]"
                        "//table"
                    )

                    충전금행 = 충전금사용테이블.find_element(
                        By.XPATH,
                        ".//tbody/tr[td[2][normalize-space()='써브N 일반 단건']]"
                    )

                    radio = 충전금행.find_element(By.XPATH, ".//input[@type='radio']")
                    if radio.get_attribute("disabled") is not None:
                        raise Exception("써브N 일반 단건 radio가 비활성화 상태입니다.")

                    radio_클릭(radio)
                    print(f"충전금 사용 선택완료: 써브N 일반 단건, 현재보유금액={현재보유금액}")
                    return "충전금사용"

                # 3순위: 둘 다 불가
                pyautogui.alert("사용가능한 등록권이 없습니다")
                return False
     

            def 팝업창으로전환():
                main_page = driver.current_window_handle #팝업창 생성전의 창
                # print("메인창:",driver.title, main_page)

                handles = driver.window_handles #팝업창을 닫기 전
                # print(handles)
                driver.switch_to.window(handles[-1])
                # print("현재창 활성화된 창" ,driver.title, driver.current_window_handle) 

                # # 원래 창 핸들 저장
                # original_window = driver.current_window_handle
                # # 새 창이 열릴 때까지 대기
                # WebDriverWait.until(EC.number_of_windows_to_be(2))
                # # 새 창으로 전환
                # for window_handle in driver.window_handles:
                #     if window_handle != original_window:
                #         driver.switch_to.window(window_handle)
                #         break   

            # def 원래창으로전환():
            #     driver.switch_to.window(handles[0])   

            def 개인정보수집및이용동의체크():
                try:
                    print("📌 개인정보 수집 동의 체크 시작")
                    canvas1_xpath = '//div[@class="content-area"]/div[2]//canvas'

                    # 1) 캔버스 요소 찾기
                    canvas1 = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, canvas1_xpath))
                    )

                    # 캔버스의 실제 크기와 스타일 확인
                    canvas1_info = driver.execute_script("""
                        const canvas = arguments[0];
                        return {
                            width: canvas.width,
                            height: canvas.height,
                            styleWidth: canvas.style.width,
                            styleHeight: canvas.style.height,
                            offsetWidth: canvas.offsetWidth,
                            offsetHeight: canvas.offsetHeight
                        };
                    """, canvas1)
                    # print(f"Canvas 정보: {canvas1_info}")

                    # 2) 캔버스 위치/크기 가져오기
                    rect = driver.execute_script("""
                        const c = arguments[0].getBoundingClientRect();
                        return {left: c.left, top: c.top, width: c.width, height: c.height};
                    """, canvas1)


                    # w, h = rect['width'], rect['height']
                    # print(f"canvas w:{w}, h:{h}")
                    # # V자 좌표 (캔버스 내 상대좌표)
                    # sx, sy = w * 0.2, h * 0.2        # p1: 좌측 상단
                    # mx, my = w * 0.4, h * 0.6        # p2: 하단 중간
                    # ex, ey = w * 0.6, h * 0.2        # p3: 우측 상단        

                    left, top, w, h = rect['left'], rect['top'], rect['width'], rect['height']
                    # V 모양의 첫 번째 선용 포인트 계산
                    sx, sy = left + w * 0.4, top + h * 0.2        # p1: 좌측 상단
                    mx, my = left + w * 0.6, top + h * 1.0        # p2: 하단 중간
                    ex, ey = left + w * 0.8, top + h * 0.2        # p3: 우측 상단
                    # print(f"left={left}, top={top}, w={w}, h={h}, sx={sx}, sy={sy}, mx={mx}, my={my}, ex={ex}, ey={ey}")
                    
                    # actions = ActionChains(driver)
                    # actions.move_to_element_with_offset(canvas, int(sx), int(sy))
                    # actions.click_and_hold()
                    # actions.move_to_element_with_offset(canvas, int(mx), int(my))
                    # actions.release()
                    # actions.perform()

                    # actions = ActionChains(driver)
                    # actions.move_to_element_with_offset(canvas, int(mx), int(my))
                    # actions.click_and_hold()
                    # actions.move_to_element_with_offset(canvas, int(ex), int(ey))
                    # actions.release()
                    # actions.perform()

                    # 중간 드래그 보강용 포인트 (시작↔끝 중간)
                    segx12, segy12 = (sx + mx) / 2, (sy + my) / 2
                    segx23, segy23 = (mx + ex) / 2, (my + ey) / 2
          
                    actions = ActionChains(driver)
                    # print(f"x:{sx}, y:{sy} - p2좌표 ")
                    actions.w3c_actions.pointer_action.move_to_location(576, 280)
                    # actions.w3c_actions.pointer_action.move_to_location(sx, sy)
                    actions.w3c_actions.pointer_action.pointer_down()
                    # (3) 중간점으로 천천히 이동
                    # print(f"x:{segx12}, y:{segy12} - p1-p2중간좌표 ")
                    actions.w3c_actions.pointer_action.pause(0.05)
                    actions.w3c_actions.pointer_action.move_to_location(586, 314)

                    # actions.w3c_actions.pointer_action.pause(0.05)
                    # actions.w3c_actions.pointer_action.pointer_up()
                    # actions.perform()
                    # time.sleep(5)
                    # pyautogui.alert("'\'그리기 완료, '/'그리기 시작?")
                    # actions.w3c_actions.pointer_action.move_to_location(segx12, segy12)
                    # actions.w3c_actions.pointer_action.pointer_down()

                    # (4) 끝점(하단 중간)까지 계속 이동
                    # print(f"x:{mx}, y:{my} - p2좌표 ")
                    # actions.w3c_actions.pointer_action.pause(0.05)
                    actions.w3c_actions.pointer_action.move_to_location(636, 368)
                    
                    # actions.w3c_actions.pointer_action.pause(0.05)
                    actions.w3c_actions.pointer_action.move_to_location(666, 442)
                    
                    
                    # actions.w3c_actions.pointer_action.pause(0.05)
                    actions.w3c_actions.pointer_action.pointer_up()
                    actions.perform()

                    # # time.sleep(1)
                    # pyautogui.alert("'\'그리기 완료, '/'그리기 시작?")

                    actions = ActionChains(driver)
                    actions.w3c_actions.pointer_action.move_to_location(636, 368)
                    # actions.w3c_actions.pointer_action.move_to_location(mx, my)
                    actions.w3c_actions.pointer_action.pointer_down()
                    # print(f"x:{segx23}, y:{segy23} - p2-p3중간좌표 ")
                    # actions.w3c_actions.pointer_action.pause(0.05)
                    actions.w3c_actions.pointer_action.move_to_location(696, 284)
                    # actions.w3c_actions.pointer_action.move_to_location(segx23, segy23)
                    # print(f"x:{ex}, y:{ey} - p3좌표 ")
                    # actions.w3c_actions.pointer_action.pause(0.05)
                    actions.w3c_actions.pointer_action.move_to_location(726, 264)
                    # actions.w3c_actions.pointer_action.move_to_location(segx23, segy23)
                    # actions.w3c_actions.pointer_action.pause(0.05)
                    actions.w3c_actions.pointer_action.move_to_location(746, 244)
                    # actions.w3c_actions.pointer_action.move_to_location(ex, ey)
                    actions.w3c_actions.pointer_action.pointer_up()
                    actions.perform()

                    print("✅ 개인정보 수집 동의 체크 완료")

                except Exception as e:
                    print(f"Canvas 서명 오류: {e}")

            def 의뢰인이름쓰기(의뢰인명):
                try:
                    driver.find_element(By.XPATH, f'//input[@class="input-sign"]').send_keys(의뢰인명)
                except Exception as e:
                    print(f"의뢰인이름쓰기 오류: {e}")                    

            def 매물의뢰인서명날인():
                try:
                    print("📌 매물의뢰인서명날인 시작")
                    canvas1_xpath = '//*[@id="app"]/div/div/div/div[2]/div[2]/div[2]/div[1]/canvas'

                    # 1) 캔버스 요소 찾기
                    canvas1 = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, canvas1_xpath))
                    )

                    # 캔버스의 실제 크기와 스타일 확인
                    canvas1_info = driver.execute_script("""
                        const canvas = arguments[0];
                        return {
                            width: canvas.width,
                            height: canvas.height,
                            styleWidth: canvas.style.width,
                            styleHeight: canvas.style.height,
                            offsetWidth: canvas.offsetWidth,
                            offsetHeight: canvas.offsetHeight
                        };
                    """, canvas1)
                    rect1 = driver.execute_script("""
                        const c = arguments[0].getBoundingClientRect();
                        return {left: c.left, top: c.top, width: c.width, height: c.height};
                    """, canvas1)    
                    left, top, w, h = rect1['left'], rect1['top'], rect1['width'], rect1['height']
                    # V 모양의 첫 번째 선용 포인트 계산
                    sx, sy = left + w * 0.4, top + h * 0.2        # p1: 좌측 상단
                    mx, my = left + w * 0.6, top + h * 1.0        # p2: 하단 중간
                    ex, ey = left + w * 0.8, top + h * 0.2        # p3: 우측 상단                
                    # print(f"Canvas1 정보: {canvas1_info}")
                    # print(f"left={left}, top={top}, w={w}, h={h}, sx={sx}, sy={sy}, mx={mx}, my={my}, ex={ex}, ey={ey}")

                    canvas2_xpath = '//*[@id="app"]/div/div/div/div[2]/div[4]/div[2]/div[1]/canvas'
                    # canvas_xpath = '//div[@class="content-area"]/div[4]//canvas'
                    
                    # 1) 캔버스 요소 찾기
                    canvas2 = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, canvas2_xpath))
                    )

                    # 캔버스의 실제 크기와 스타일 확인
                    canvas2_info = driver.execute_script("""
                        const canvas = arguments[0];
                        return {
                            width: canvas.width,
                            height: canvas.height,
                            styleWidth: canvas.style.width,
                            styleHeight: canvas.style.height,
                            offsetWidth: canvas.offsetWidth,
                            offsetHeight: canvas.offsetHeight
                        };
                    """, canvas2)

                    # 2) 캔버스 위치/크기 가져오기
                    rect = driver.execute_script("""
                        const c = arguments[0].getBoundingClientRect();
                        return {left: c.left, top: c.top, width: c.width, height: c.height};
                    """, canvas2)


                    left, top, w, h = rect['left'], rect['top'], rect['width'], rect['height']
                    # V 모양의 첫 번째 선용 포인트 계산
                    sx, sy = left + w * 0.4, top + h * 0.2        # p1: 좌측 상단
                    mx, my = left + w * 0.6, top + h * 1.0        # p2: 하단 중간
                    ex, ey = left + w * 0.8, top + h * 0.2        # p3: 우측 상단
                    # print(f"Canvas2 정보: {canvas2_info}")
                    # print(f"left={left}, top={top}, w={w}, h={h}, sx={sx}, sy={sy}, mx={mx}, my={my}, ex={ex}, ey={ey}")
                    # print(f"lt=[{left},{top}], lb=[{left},{top+h}], rt=[{left+w},{top}], rb=[{left+w},{top+h}]")
                    


                    # 중간 드래그 보강용 포인트 (시작↔끝 중간)
                    segx12, segy12 = (sx + mx) / 2, (sy + my) / 2
                    segx23, segy23 = (mx + ex) / 2, (my + ey) / 2
          
                    actions = ActionChains(driver)
                    # print(f"x:{sx}, y:{sy} - p2좌표 ")
                    actions.w3c_actions.pointer_action.move_to_location(756, 720) #-240
                    # actions.w3c_actions.pointer_action.move_to_location(sx, sy)
                    actions.w3c_actions.pointer_action.pointer_down()
                    # (3) 중간점으로 천천히 이동
                    # print(f"x:{segx12}, y:{segy12} - p1-p2중간좌표 ")
                    actions.w3c_actions.pointer_action.pause(0.05)
                    actions.w3c_actions.pointer_action.move_to_location(666, 614)

                    # actions.w3c_actions.pointer_action.pause(0.05)
                    actions.w3c_actions.pointer_action.move_to_location(606, 638)
                    # actions.w3c_actions.pointer_action.pause(0.05)
                    actions.w3c_actions.pointer_action.move_to_location(616, 648)


                    # (4) 끝점(하단 중간)까지 계속 이동
                    # print(f"x:{mx}, y:{my} - p2좌표 ")
                    # actions.w3c_actions.pointer_action.pause(0.05)
                    actions.w3c_actions.pointer_action.move_to_location(636, 668)
                    
                    # actions.w3c_actions.pointer_action.pause(0.05)
                    actions.w3c_actions.pointer_action.move_to_location(666, 666)
                    
                    
                    # actions.w3c_actions.pointer_action.pause(0.05)
                    actions.w3c_actions.pointer_action.pointer_up()
                    actions.perform()

                    # # time.sleep(1)
                    # pyautogui.alert("'\'그리기 완료, '/'그리기 시작?")

                    actions = ActionChains(driver)
                    actions.w3c_actions.pointer_action.move_to_location(636, 668)
                    # actions.w3c_actions.pointer_action.move_to_location(mx, my)
                    actions.w3c_actions.pointer_action.pointer_down()
                    # print(f"x:{segx23}, y:{segy23} - p2-p3중간좌표 ")
                    # actions.w3c_actions.pointer_action.pause(0.05)
                    actions.w3c_actions.pointer_action.move_to_location(696, 614)
                    # actions.w3c_actions.pointer_action.move_to_location(segx23, segy23)
                    # print(f"x:{ex}, y:{ey} - p3좌표 ")
                    # actions.w3c_actions.pointer_action.pause(0.05)
                    actions.w3c_actions.pointer_action.move_to_location(726, 580)
                    # actions.w3c_actions.pointer_action.move_to_location(segx23, segy23)
                    # actions.w3c_actions.pointer_action.pause(0.05)
                    actions.w3c_actions.pointer_action.move_to_location(546, 740)
                    # actions.w3c_actions.pointer_action.move_to_location(ex, ey)
                    actions.w3c_actions.pointer_action.pointer_up()
                    actions.perform()

                    print("✅ 개인정보 수집 동의 체크 완료")

                except Exception as e:
                    print(f"Canvas 서명 오류: {e}")


            def 홍보확인서작성(의뢰인명, 관계):
                if 관계=='직원' or 관계 == '대표':
                    의뢰인명 = '이은선' 
                print(f"홍보확인서작성(의뢰인명, 관계) => 관계:{관계},의뢰인명:{의뢰인명}")   
                try:
                    #홍보확인서 작성버튼 클릭
                    홍보확인서작성버튼 = driver.find_element(By.XPATH, '//*[@id="app"]//button//span/span[text()="홍보확인서 작성"]')
                    홍보확인서작성버튼.click()
                    #홍보확인서 작성 팝업창내의 서명하기 버튼 클릭

                    # 원래 창 핸들 저장
                    original_window = driver.current_window_handle
                    print("메인창:",driver.title, original_window)
                    handles = driver.window_handles #팝업창을 닫기 전
                    print(handles)
                    driver.switch_to.window(handles[-1])
                    print("현재창 활성화된 창" ,driver.title, driver.current_window_handle)
                    # 서명하기 버튼 찾아서 클릭
                    서명하기xpath = '//a[@id="reg_button" and text()=" 서명하기 "]'
                    서명하기요소 = WebDriverWait(driver, 15).until( # 대기 시간을 좀 더 여유있게 15초로 늘려봅니다.
                        EC.element_to_be_clickable((By.XPATH, 서명하기xpath))
                    )
                    print(f"클릭하려는 요소의 텍스트: {서명하기요소.text}")
                    서명하기요소.click()   
                    print("성공적으로 '서명하기' 버튼을 클릭했습니다.")    
                    개인정보수집및이용동의체크() 
                    if 관계 != '본인':
                        의뢰인이름쓰기(의뢰인명)
                    완료버튼요소 = driver.find_element(By.XPATH, '//*[@id="app"]//button/span[3]/span[text()="완료"]')
                    driver.execute_script("arguments[0].scrollIntoView();", 완료버튼요소)
                    매물의뢰인서명날인()
                    완료버튼요소.click()
                    이미지첨부xpath = '//a[@id="reg_button" and text()=" 이미지 첨부 "]'
                    이미지첨부요소 = WebDriverWait(driver, 5).until( # 대기 시간을 좀 더 여유있게 15초로 늘려봅니다.
                        EC.element_to_be_clickable((By.XPATH, 이미지첨부xpath))
                    )
                    이미지첨부요소.click()
                    print("성공적으로 '이미지첨부요소' 버튼을 클릭했습니다.")              
                    driver.switch_to.window(handles[0])
                    홍보확인서작성tr요소 = 특정tr요소('홍보확인서 작성')
                    if 홍보확인서작성tr요소: print("홍보확인서작성tr요소 찾음")
                    미리보기요소 =  WebDriverWait(홍보확인서작성tr요소, 10).until( # 대기 시간을 좀 더 여유있게 15초로 늘려봅니다.
                        EC.element_to_be_clickable((By.XPATH, '//span/span[text()="미리보기"]'))
                    )     
                    if 미리보기요소:print('미리보기 요소찾음')  

                except Exception as e:
                    print(f"홍보확인서작성 오류: {e}")                    

            def 검증방식선택및의뢰인정보입력(fail_msg):   
                print("검증방식선택및의뢰인정보입력() 시작")
                소유자명 = ''
                소유자연락처 = ''        
                소유자유형 = '본인'
                선택할검증방식 = '홍보확인서 확인'
                소유자통신사 = ''

                #소유자정보 결정
                print("등기부확인여부:"+등기부확인여부+" 등록된 소유자수:"+str(len(등록된소유자들_arr)))
                #입력된 소유자들이 있는 경우
                if len(등록된소유자들_arr) > 0: 

                    print("등록된소유자들:",등록된소유자들)
                    print("contactor_info:",contactor_info)
                    # 필수값이므로 소유자명 결정        
                    if len(등록된소유자들_arr) == 1 :
                        print("1")
                        소유자명 = 등록된소유자들 
                    else :
                        print("2")
                        # print("등록된소유자들_arr:",등록된소유자들_arr)
                        소유자명 = 등록된소유자들_arr[0]
                        # 소유자유형 = contactor_info[0]['contactor_type']
                    if 등기부확인여부 == 'Y':
                        if '(주)' in 소유자명 or '주식회사' in 소유자명 or '법인' in 소유자명:
                            print("a")
                            소유자유형 = '직원'
                        elif '종중' in 소유자명 or '신탁' in 소유자명:
                            print("b")
                            소유자유형 = '직원'
                        else:
                            print("c")
                            소유자유형 = '본인'
                    else:
                        print("d")
                        소유자유형 = '본인' 

                    if 소유자유형 == '본인':
                        의뢰인명 = 소유자명
                    else:
                        의뢰인명 = '이은선'  

                    if contactor_info and 'contactor_name' in contactor_info: #본인 또는 대표인 접촉자정보존재
                        print("3")
                        if '미확인' not in contactor_info['contactor_name'] and contactor_info['contactor_name'] in 등록된소유자들 and contactor_info['contactor_type'] == '본인': #소유주정보에 등기확인된 소유주(개인) 존재
                            print("4")
                            소유자명 = contactor_info['contactor_name']
                            소유자연락처 = contactor_info['contactor_phone1']
                            소유자통신사 = contactor_info['telecom']
                        elif contactor_info['contactor_name'] not in 등록된소유자들 and contactor_info['contactor_type'] == '대리인-법인': #법인일 경우?
                            print("5")
                            소유자유형 = '직원'
                            # corporation_group = ['종중', '단체', '법인', '관리인']
                            # if any(corporation in contactor_info['contactor_type'] for corporation in corporation_group):
                            #     소유자유형 = '직원'
                            # elif contactor_info['contactor_type'].startswith('임차대리인') or contactor_info['contactor_type'] == '임차인':
                            #     소유자유형 = '세입자'
                            # elif contactor_info['contactor_type'] == '본인':
                            #     소유자유형 = '본인'
                            # else:
                            #     소유자유형 = '본인' 

                        else:
                            최상단알림창(f"- 등기부상 소유자:  {등록된소유자들}\n\n- 의뢰인:  {contactor_info['contactor_name']} ({contactor_info['contactor_type']})", "※소유자정보 불일치")
                        print("8")
                        
                        # 소유자유형 = contactor_info['contactor_type']
                        
                        fail_msg += "\n- 휴대폰통신사 미확인" if 소유자통신사 == '미확인' else ''
                        print(f"소유자:{소유자명}\n연락처(통신사:{소유자통신사}):{소유자연락처}")
                        if 소유자유형 == '본인' and 소유자연락처 and 소유자통신사 != '미확인':
                            선택할검증방식 = '모바일확인V2 (집주인)'
                    else:
                        # 소유자명 = 등록된소유자들 
                        # 소유자유형 = '대리인'
                        최상단알림창("접촉자정보 없음")
                else:
                    소유자명 = contactor_info['contactor_name']
                    소유자유형 = '본인'
                    # if tr_target == '토지':

                    # else:
                    #     if '미등기' in building_important:
                    #         소유자명 = contactor_info['contactor_name']
                    #         소유자유형 = '본인'
                    #     else:
                    #         fail_msg += '\n- 소유자이름 입력 실패'
                # pyautogui.alert("소유자명:"+소유자명)
                #검증방식  
                try:
                    print("선택할검증방식:",선택할검증방식)
                    if 선택할검증방식 != '홍보확인서 확인':
                        적용대상h2 = driver.find_elements(By.XPATH, f'//h2[@class="t-h2"]')
                        print(f"'t-h2'의 class를 가진 h2 태그의 개수: {len(적용대상h2)}")
                        # 적용대상h2 = driver.find_elements(By.XPATH, f'//h2[contains(text(), "검증방식")]')
                        # print(f"'검증방식' 텍스트를 가진 h2 태그의 개수: {len(적용대상h2)}")
                        time.sleep(0.2)
                        # 해당 h2 태그들이 속한 div 태그 내에서 td 태그의 첫 번째 div 내에 있는 label의 텍스트 출력
                        for h2 in 적용대상h2:
                            # h2 태그가 속한 div 태그 찾기
                            div_element = h2.find_element(By.XPATH, './parent::div')
                            # 해당 div 내의 td의 첫 번째 div 내에 있는 label 태그 찾기
                            label_elements = div_element.find_elements(By.XPATH, './/div/div/label')
                            # 각 label 태그의 텍스트 출력
                            for label in label_elements:
                                # print(f"Label 텍스트: {label.text}") 
                                if label.text==선택할검증방식:
                                    label.click()     
                                    # print(f"{대상h2텍스트}({label.text}) 클릭완료")    
                    # pyautogui.alert("'써브N 일반 패키지' 요소찾기")
                    # 잔여수량요소 = driver.find_element(By.XPATH, f'//table//tr[td[text()="써브N 일반 패키지"]]/td[3]/div[1]/span')
                    잔여수량요소 = driver.find_element(By.XPATH, f'//table//tr[td[text()="써브N 일반 패키지"]]/td[3]')
                    잔여수량텍스트 = 잔여수량요소.text.strip()
                    # '/' 기준으로 나누고 첫 번째 값만 가져오기
                    잔여수량 = 잔여수량텍스트.split('/')[0].strip()
                    # pyautogui.alert(f"잔여수량텍스트{잔여수량텍스트}\n잔여수량:{잔여수량}개")
                    #사용 가능한 등록권이 없습니다. 상품 구매 후 이용해주세요.
                    print(f"등록권 잔여수량:{잔여수량}")
                    네이버등록권_자동선택(driver)
                    # pyautogui.alert("정상?")
                except Exception as e:
                    pyautogui.alert(f"등록권선택 실패: {e}")
                    fail_msg += '\n- 네이버등록권 선택실패'
                    
                #의뢰인정보
                print(f"소유자명:{소유자명}")
                # pyautogui.alert("정상?"+소유자명)
                소유자명입력창 = 특정위치의x번째입력태그찾기('등기부상 소유자 이름', 'text', 1)
                if 소유자명입력창: 
                    소유자명입력창.send_keys(Keys.CONTROL + 'a')  # 모든 텍스트 선택
                    소유자명입력창.send_keys(Keys.DELETE)  # 선택된 텍스트 삭제
                    소유자명입력창.send_keys(소유자명) 
                else:
                    print("소유자명입력창을 찾을 수 없습니다.")            
                print(f"선택할검증방식:{선택할검증방식}")
                # pyautogui.alert("정상?")  
                if 선택할검증방식 == '홍보확인서 확인':
                    관계입력창 = 특정위치의x번째입력태그찾기('의뢰인과 등기부상 소유자와의 관계', 'text', 1)
                    관계입력창.send_keys(Keys.CONTROL + 'a')  # 모든 텍스트 선택
                    관계입력창.send_keys(Keys.DELETE)  # 선택된 텍스트 삭제
                    관계입력창.send_keys(소유자유형) 
                    특정위치의x번째입력태그찾기('소유자 연락처 (홍보확인서2)', 'radio', 2).click()
                    홍보확인서작성(소유자명, 소유자유형)
                    # time.sleep(3)
                    # main_page = driver.current_window_handle
                    # pyautogui.alert("정상?"+main_page)   
                    연락처입력대상stong_text = '소유자 연락처 (홍보확인서2)'      
                elif 선택할검증방식 == '모바일확인V2 (집주인)':
                    if contactor_info['contactor_gender']: 
                        print(f"소유자성별:{contactor_info['contactor_gender']}")
                        # pyautogui.alert(f"소유자성별:{contactor_info['contactor_gender']}")
                        선택할성별위치 = 1 if contactor_info['contactor_gender'] == '남성' else 2
                        특정위치의x번째입력태그찾기('등기부상 소유자 성별', 'radio', 선택할성별위치).click()
                        print(f"소유자성별 완료 {contactor_info['contactor_gender']}")
                    if contactor_info['telecom']:
                        if contactor_info['telecom'] == 'SKT': 선택할통신사위치 = 1
                        if contactor_info['telecom'] == 'KT': 선택할통신사위치 = 2
                        if contactor_info['telecom'] == 'LGU+': 선택할통신사위치 = 3
                        if contactor_info['telecom'] == '알)SKT': 선택할통신사위치 = 4
                        if contactor_info['telecom'] == '알)KT': 선택할통신사위치 = 5
                        if contactor_info['telecom'] == '알)LGU+': 선택할통신사위치 = 6
                        연락처입력대상stong_text = '등기부상 소유자 휴대폰번호'     
                        특정위치의x번째입력태그찾기('등기부상 소유자 휴대폰번호', 'radio', 선택할통신사위치).click() 
                        print(f"통신사선택 완료 {contactor_info['telecom']}")
                    if len(소유자연락처) > 0 :print(f"소유자연락처 {소유자연락처}")
                    if len(소유자연락처) == 11:
                        # pyautogui.alert("정상?") 
                        특정위치X번째셀렉트에서선택(연락처입력대상stong_text, 1, '010')  
                        # 셀렉트항목선택('010', '//*[@id="app"]/div/div/div[3]/div/div[1]/div[16]/table/tbody/tr[3]/td/div[2]/div[1]') #느림
                        # pyautogui.alert("정상?") 
                        가운데4자리 = 소유자연락처[3:7]  # 예: '01012345678'에서 '1234' 추출
                        마지막4자리 = 소유자연락처[7:11]  # 예: '01012345678'에서 '5678' 추출  
                        특정위치의x번째입력태그찾기(연락처입력대상stong_text, 'number', 1).send_keys(가운데4자리)  #느림
                        # pyautogui.alert("정상?")   
                        특정위치의x번째입력태그찾기(연락처입력대상stong_text, 'number', 2).send_keys(마지막4자리)  #느림
                # pyautogui.alert("정상?") 
                # pyautogui.alert("정상?")  
                try:
                    if not 네이버매물번호:
                        # 등기부등본 파일첨부 라디오버튼 클릭
                        if object_type != '상업용':
                            특정위치의x번째입력태그찾기('등기부등본 첨부', 'radio', 2).click()
                except:
                    print("등기부등본 첨부에서 두번째 라디오버튼 클릭불가")
                    
                return fail_msg
            
            def 빠른이동(이동위치):
                try:
                    의뢰인정보버튼 = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, f'//*[@id="app"]/div/div/div[2]/div/div[2]/ol/li//button/span[3]/span[text()="{이동위치}"]'))
                    )
                    의뢰인정보버튼.click()
                    print(f"🔍 '{이동위치}' 버튼을 클릭했습니다.")
                except Exception as e:
                    print(f"⚠️ '{이동위치}' 버튼을 찾을 수 없습니다: {e}")                






            
    #변수설정
            try:
                print("=== 변수 설정")
                print("self.data:", self.data)
                # 현재 날짜와 시간 가져오기
                현재날짜시간 = datetime.now()
                현재날짜 = 현재날짜시간.date()
                # 문자형으로 변환
                current_date = 현재날짜시간.strftime("%Y-%m-%d")  # 'YYYY-MM-DD' 형식
                current_time = 현재날짜시간.strftime("%H:%M:%S")  # 'HH:MM:SS' 형식    
                # current_date = datetime.date.today()
                # formatted_date = current_date.strftime("%Y-%m-%d")
                
                manager_id = self.data['adminData']['ad_id']
                admin_name = self.data['adminData']['admin_name']
                naver_id = self.data['adminData']['naver_id']
                naver_pw = self.data['adminData']['naver_pw']
                # naver_id = "osanbang6666"
                # naver_pw = "dhqkd5555%"
                부동산상호명 = "나상권공인중개사사무소"
                # naver_id = "osanon"
                # naver_pw = "osanon12!@"
                # 부동산상호명 = "큐브공인중개사사무소"
                
                errarr = []
                fail_msg = ''

                # 데이터 종류에 따른 분기 처리
                if 'landData' not in self.data:    
                    print("📢 landData 없음 - 연장 등록 모드입니다. 상세 변수 설정을 건너뜁니다.")            
                else:
                    client_code = self.data['clientData']['client_code']
                    contactor_data = self.data['contactorData']['contactor_data']
                    print("client_code:"+client_code)
                    print("contactor_data:",contactor_data)
                    contactor_keys_list = list(contactor_data.keys())
                    contactor_info = None  # 초기화
                    # 리스트에 요소가 있는지 확인하고 첫 번째 요소에 접근합니다.
                    # 조건에 따라 데이터를 필터링하고 첫 번째 항목 선택
                    if contactor_keys_list:  # 키가 비어있지 않은 경우
                        print("contactor_keys_list:", contactor_keys_list)
                        
                        # '본인' 또는 '대표'이고 'contactor_phone1'이 있는 데이터 탐색
                        for key in contactor_keys_list:
                            keyData = contactor_data[key]
                            if (keyData.get('contactor_type') in ['본인', '대표']) and keyData.get('contactor_phone1'):
                                if keyData.get('telecom') != '미확인':
                                    contactor_info = keyData
                                    break
                                else:
                                    contactor_info = keyData

                        # 조건에 맞는 데이터가 없는 경우 최근의뢰인의 데이터를 탐색
                        if contactor_info is None:
                            for key in contactor_keys_list:
                                if key == client_code:
                                    contactor_info = contactor_data[key]
                                    break

                        # 최종 contactor_info 출력
                        if contactor_info:
                            print("Selected contactor_info:", contactor_info)
                        else:
                            print("No matching data found.")
                    else:
                        # 키 리스트가 비어있는 경우 처리
                        print("contactor_keys_list: No data available")
                        
                    # pyautogui.alert("소유자 목록확인")
                    등록된소유자들 = self.data['writeData']['master_name']
                    등록된소유자들_arr = []
                    # 쉼표로 나눈 뒤, strip() 후 빈값이 아닌 것만 필터
                    등록된소유자들_arr = [s.strip() for s in 등록된소유자들.split(',') if s.strip()]
                    if len(등록된소유자들_arr) > 0:
                        master_name = 등록된소유자들_arr[0]
                    else:
                        master_name = ''
                    
                    
                    client_name = self.data['clientData']['client_name']
                    client_phone1 = self.data['clientData']['client_phone1']
                    # client_gender = self.data['clientData']['client_gender']
                    client_type = self.data['clientData']['client_type']
                    client_phone = f"{client_phone1[:3]}-{client_phone1[3:7]}-{client_phone1[7:]}"
                    client_info = client_name + ' ' + client_phone
                    # client_telecom = self.data['clientData']['telecom']
                    
                    if self.data['writeData']:
                        등기부확인여부 = self.data['writeData']['master_check']
                        tr_target = self.data['writeData']['tr_target']
                        tr_range = self.data['writeData']['tr_range']
                        request_code = self.data['writeData']['request_code'] #의뢰번호
                        object_code_new = self.data['writeData']['object_code_new'] #새홈매물번호
                        obang_code = self.data['writeData']['obang_code'] #오방매물번호
                        object_type = self.data['writeData']['object_type']
                        obinfo_type = ''
                        obinfo_type1 = self.data['writeData']['object_type1']
                        obinfo_type2 = self.data['writeData']['object_type2']
                        if obinfo_type1 == '상가건물':
                            obinfo_type1 = '상가건물'
                            if obinfo_type2 == '상업용건물':
                                obinfo_type2 = '상가건물'

                        # if self.data['writeData']['object_type'] == '주거용' and tr_target == '층호수':
                        #     if self.data['roomData']['room_rcount'] == '1':
                        #         obinfo_type = '원룸'
                        #     elif self.data['roomData']['room_rcount'] >= '2':
                        #         obinfo_type = '투룸/쓰리룸+'
                        # elif self.data['writeData']['object_type'] == '상업용':
                        #     obinfo_type = '상가/사무실'
                        first_trade = self.data['writeData']['first_trade'] #우선거래
                        obinfo_trading = self.data['writeData']['trading'] #매매금액    
                        obinfo_deposit1 = self.data['writeData']['deposit1'] #보증금1
                        obinfo_deposit2 = self.data['writeData']['deposit2'] #보증금2
                        obinfo_deposit3 = self.data['writeData']['deposit3'] #보증금3
                        obinfo_rent1 = self.data['writeData']['rent1'] #월세1
                        obinfo_rent2 = self.data['writeData']['rent2'] #월세2
                        obinfo_rent3 = self.data['writeData']['rent3'] #월세3
                        flexible_deposit = self.data['writeData']['flexible_deposit'] #보증금조정가능여부
                        obinfo_ttype = self.data['writeData']['object_ttype'] #거래종류
                        obinfo_title = self.data['writeData']['object_title'] #매물제목
                        obinfo_content = remove_html_and_entities(self.data['writeData']['object_content']) #매물설명

                        premium = self.data['writeData']['premium']
                        premium_exist = self.data['writeData']['premium_exist']
                        premium_content = self.data['writeData']['premium_content']
                        basic_manager = self.data['writeData']['manager'] #관리비 별도/포함/미확인
                        # basic_mmoney = '' if self.data['writeData']['mmoney']=='' else float(self.data['writeData']['mmoney'])*10000 #관리비
                        mmoney_raw = self.data['writeData'].get('mmoney', '').strip() #관리비
                        try:
                            # 빈 문자열이거나 숫자가 아닌 경우 float()에서 ValueError가 터짐
                            basic_mmoney = float(mmoney_raw) * 10000
                        except (ValueError, TypeError):
                            # 예외가 발생하면 공백으로 처리
                            basic_mmoney = ''                    
                        basic_mlist = self.data['writeData']['mlist'] #관리비포함내역
                        # 관리비항목들 = 그룹별명칭변환('관리비포함내역', basic_mlist)
                        관리비항목들 = 목록_변환('관리비포함내역', basic_mlist)
                        basic_mmemo = self.data['writeData']['mmemo'] #관리비메모
                        add_warmer = '' #data['writeData']['add_warmer'] 난방
                        add_rdate = str(self.data['writeData']['rdate']) #입주일
                        secret_1 = '' if self.data['writeData']['tr_memo'] == '' else self.data['writeData']['tr_memo'] + "\n"
                    else:
                        print("writeData 데이터없음")
                    representing_purpose = self.data['landData'][0]['representing_purpose']
                    representing_jimok = self.data['landData'][0]['representing_jimok']
                    location_do = self.data['landData'][0]['land_do']
                    location_si = self.data['landData'][0]['land_si']
                    location_dong = self.data['landData'][0]['land_dong']
                    location_li = self.data['landData'][0]['land_li']
                    # jibun = self.data['landData'][0]['land_jibun']
                    jibung = self.data['landData'][0]['land_jibung'] #지번그룹
                    jibung_arr = jibung.split(',')
                    jibung_len = len(jibung_arr) #지번의 개수
                    jibun = jibung_arr[0] if jibung_len > 1 else jibung
                    
                    location_lijibun = (self.data['type_path'] + self.data['landData'][0]['land_jibun']) if self.data['landData'][0]['land_li'] == '' else (self.data['landData'][0]['land_li'] + self.data['type_path'] + self.data['landData'][0]['land_jibun'])
                    location_dongli = (self.data['landData'][0]['land_dong'] + self.data['type_path'] + self.data['landData'][0]['land_jibun']) if self.data['landData'][0]['land_li'] == '' else location_lijibun
                    
                    
                    optionImportant = ''
                    
                    
                    secret_2 = '' if self.data['landData'][0]['land_memo'] == '' else self.data['landData'][0]['land_memo'] + "\n"
                    address_info = location_dongli 
                    address_info += " 외"+str(jibung_len-1) if jibung_len > 1 else ""
                    land_memo = self.data['landData'][0]['land_memo']#토지메모
                    land_option = self.data['landData'][0]['land_option']#토지옵션
                    location_detail = f'외 {jibung_len-1}필지' if jibung_len > 1 else '' #다중필지일 경우 '외 ㅇㅇ필지'로 표시
                    

                    if tr_target == '토지' or tr_target == '건물':
                        land_totarea = self.data['landData'][0]['land_totarea'] #대지면적
                        if tr_target == '토지' :
                            land_purpose = self.data['landData'][0]['land_purpose'] #용도지역
                            land_important = self.data['landData'][0]['land_important'] #토지특징
                            land_option = self.data['landData'][0]['land_option'] #토지옵션
                            

                    if tr_target == '건물' or tr_target == '층호수':
                        if 'brtitData' in self.data and isinstance(self.data['brtitData'], dict):
                            # brtitData가 딕셔너리일 경우
                            brtit_platPlc = self.data['brtitData'].get('brtit_platPlc', '')
                            brtit_bldNm = self.data['brtitData'].get('brtit_bldNm', '')
                            brtit_dongNm = self.data['brtitData'].get('brtit_dongNm', '')
                            brtit_bldNmdongNm = self.data['brtitData'].get('brtit_bldNmdongNm', '')
                            
                            #brtit_platPlc문자열을 ' '으로 분리한 마지막 요소에서 마지막 '번지'를 제외하고 저장
                            # 1. brtit_platPlc를 공백으로 분리하고 마지막 요소 가져오기
                            address_parts = brtit_platPlc.split()  # 공백으로 분리하여 리스트로 변환
                            if address_parts:  # address_parts가 비어 있지 않은 경우에만 실행
                                last_part = address_parts[-1]  # 마지막 요소 선택
                                # 2. 마지막 요소에서 '번지' 제거
                                if '번지' in last_part:
                                    jibun = last_part.replace('번지', '').strip()  # '번지'를 제거하고, 앞뒤 공백 제거
                                else:
                                    jibun = last_part  # '번지'가 없으면 그대로 사용
                            else:
                                jibun = ''  # address_parts가 비어 있을 경우 기본값 설정
                        else:
                            # brtitData가 비어있거나 딕셔너리가 아닐 경우 빈 문자열 할당
                            brtit_bldNm = ''
                            brtit_dongNm = ''
                            brtit_bldNmdongNm = ''
                        
                        location_building = '' if brtit_bldNmdongNm == '' else ' ' + brtit_bldNmdongNm
                        location_detail += location_building
                        building_name = self.data['buildingData']['building_name'] #건물명
                        building_gate1 = self.data['buildingData']['building_gate1'] #건물출입방법
                        building_gate2 = self.data['buildingData']['building_gate2'] #건물출입내용
                        building_info = ('' if location_dongli == '' else ' ') + building_name + (("("+building_gate2+")") if building_gate1 == '비밀번호' else "")
                        building_archarea = self.data['buildingData']['building_archarea'] #건축면적
                        building_totarea = self.data['buildingData']['building_totarea'] #연면적
                        building_direction = self.data['buildingData']['building_direction'] #방향
                        building_bolt = self.data['buildingData']['building_bolt'] #건물전력
                        building_type = self.data['buildingData']['building_type'] #대장구분
                        building_purpose = self.data['buildingData']['building_purpose'] #주용도
                        building_stract = self.data['buildingData']['building_stract'] #주구조
                        building_usedate = str(self.data['buildingData']['building_usedate']) #사용승인일
                        basic_totflr = str(int(self.data['buildingData']['building_grndflr']) + int(self.data['buildingData']['building_ugrndflr'])) #전체층
                        building_ugrndflr = str(self.data['buildingData']['building_ugrndflr']) if self.data['buildingData']['building_ugrndflr']!='' else 0 #지하총층
                        building_grndflr = str(self.data['buildingData']['building_grndflr']) #지상총층
                        building_important = self.data['buildingData']['building_important'] #건물특징
                        if building_important != '':
                            optionImportant += ','+building_important if optionImportant != '' else building_important
                        # if building_important != '': optionImportant = building_important
                        print("building_important: ", optionImportant)
                        building_element = self.data['buildingData']['building_element'] #건물구성
                        building_memo = self.data['buildingData']['building_memo'] #건물메모
                        building_option = self.data['buildingData']['building_option'] #건물옵션
                        if building_option != '':
                            optionImportant += ','+building_option if optionImportant != '' else building_option
                        # if building_option != '': optionImportant = optionImportant+','+building_option
                        print("building_option: ", optionImportant)
                        building_pn = int(self.data['buildingData']['building_pn']) if self.data['buildingData']['building_pn'] != '' else 0 #주차대수
                        building_hhld = self.data['buildingData']['building_hhld'] #세대수
                        세대당주차대수값 = (int(building_pn)/int(building_hhld)) if int(building_pn)>0 and int(building_hhld)>0 else 0
                        building_fmly = self.data['buildingData']['building_fmly'] #가구수
                        secret_3 = '' if self.data['buildingData']['building_memo'] == '' else self.data['buildingData']['building_memo'] + "\n"
                        address_info += building_info


                    basic_floor = ''
                    basic_rcount=''
                    basic_bcount=''
                    r_direction=''
                    room_direction=''
                    basic_area1 = ''
                    basic_area2 = ''
                    room_important = ''
                    if tr_target == '층호수':
                        room_num = self.data['roomData']['room_num']
                        location_room = '' if room_num == '' else ' ' + room_num
                        room_status = ' '+self.data['roomData']['room_status'] if self.data['roomData']['room_status']!='미확인' else ' 상태미확인' #호실상태
                        room_gate1 = ' '+self.data['roomData']['room_gate1'] #내부출입1
                        room_gate2 = ':'+self.data['roomData']['room_gate2'] if self.data['roomData']['room_gate2'] != '' else '' #내부출입2  
                        room_gate = room_status+room_gate1+room_gate2 if room_gate1 != ' 미확인' else ' 미확인'
                        room_info = location_room + room_gate
                        basic_area1 = self.data['roomData']['room_area1'] #전용면적(호실)
                        basic_area2 = self.data['roomData']['room_area2'] #공급면적
                        basic_rcount = self.data['roomData']['room_rcount'] #방수
                        basic_bcount = self.data['roomData']['room_bcount'] #욕실수
                        basic_floor = self.data['roomData']['room_floor'] #해당층
                        room_important = self.data['roomData']['room_important'] #호실특징
                        # location_detail += ' 제'+basic_floor+'층'
                        #집합건물일 경우 호실명 추가, 일반건물이면 '일부' 추가
                        if building_type == '집합':
                            location_detail += ' 제'+basic_floor+'층 '+location_room
                        else:
                            if '층전체' in room_important:
                                if "층" in location_room: #location_room에 '층'이 존재할 경우 '층'이후 문자열 제거
                                    print("'층'이 존재하는 호실명 location_room:"+location_room)  # 출력: "2층"     
                                    location_room = location_room.split("층")[0] + "층"
                                    print("'층'이후 문자열을 제거한 호실명 location_room:"+location_room)  # 출력: "2층"                    
                                location_detail += location_room+' 전체'+' 제'+basic_floor+'층'+' 전체'
                            else:
                                if location_room.endswith('층'): #location_room값이 '층'로 끝나는 경우
                                    location_detail += location_room+' 일부'+' 제'+basic_floor+'층'+' 일부'
                                else:
                                    location_detail += location_room+' 전체'+' 제'+basic_floor+'층'+' 일부'
                        
                        print("상세주소 location_detail:"+location_detail)
                        required_기본인테리어 = {"천정마감", "벽마감", "바닥마감"}  # 기본인테리어 특징들
                        room_features = set(room_important.split(','))  # 쉼표로 분리하여 set으로 변환
                        # 조건 확인 및 특징 추가/제거
                        if required_기본인테리어.issubset(room_features):  # 3개의 특징이 모두 포함되어 있는지 확인
                            room_features -= required_기본인테리어  # 기존 특징 제거
                            room_features.add("기본인테리어")  # '기본인테리어' 추가
                        # 결과를 쉼표로 연결
                        room_important = ','.join(room_features)        
                        if room_important != '':
                            optionImportant += ','+room_important if optionImportant != '' else room_important
                        print("room_important: ", optionImportant)
                        room_option = self.data['roomData']['room_option'] #호실옵션
                        if room_option != '':
                            optionImportant += ','+room_option if optionImportant != '' else room_option
                        print("room_option: ", optionImportant)
                        r_direction = self.data['roomData']['direction_stn'] #방향기준
                        room_direction = self.data['roomData']['room_direction'] #방향
                        room_memo = '' if self.data['roomData']['room_memo'] == '' else self.data['roomData']['room_memo'] + "\n"
                        address_info += room_info
                    상세주소값 = location_detail
                    basic_secret = f"새홈[{object_code_new}] " + current_date+" "+admin_name #오류발생하면 formatted_date 사용
                    basic_secret += "\n" + address_info +" " + client_info
                    basic_secret += "\n" +" https://obangkr.cafe24.com/web/request/request_view/view_give_request_detail.php?request_code="+request_code
                    fail_msg = ''
                    trading_memo = ''
                    rent_memo = ''
                    L_memo = ''
                    B_memo = ''
                    R_memo = ''
                    I_memo = ''

                    def 메모에마크추가(메모, 마크='-- '):
                        if not 메모:  # 메모가 None 또는 빈 문자열인 경우 예외 처리
                            return ""            
                        # 줄 단위로 나누고, 각 줄에 '-- ' 추가
                        return "\n".join([f"{마크}{line}" for line in 메모.split("\n") if line.strip()])
                    # room_memo 처리
                    if tr_target == '층호수':
                        room_memo_formatted = 메모에마크추가(room_memo , '· ')
                        if room_memo_formatted:
                            I_memo += ("\n" if I_memo else "") + room_memo_formatted

                    # building_memo 처리
                    if tr_target in ["건물", "층호수"]:
                        
                        building_memo_formatted = 메모에마크추가(building_memo , '· ')
                        if building_memo_formatted:
                            I_memo += ("\n" if I_memo else "") + building_memo_formatted
                    # land_memo 처리
                    land_memo_formatted = 메모에마크추가(land_memo , '· ')
                    if land_memo_formatted:
                        I_memo += ("\n" if I_memo else "") + land_memo_formatted
                        
                    # if tr_target == '층호수':
                    #     I_memo += ("\n"+room_memo) if (I_memo != '' and room_memo) else room_memo
                    # if tr_target == '건물' or tr_target == '층호수':
                    #     I_memo += ("\n"+building_memo) if (I_memo != '' and building_memo) else building_memo
                    # I_memo += ("\n"+land_memo) if (I_memo != '' and land_memo) else land_memo
                    premium_memo = ''
                    r_add_memo = ''
                    # pyautogui.alert("I_memo:\n"+I_memo)

                    print("=== 유효성검사")
                    #미등기건물 매매등록불가
                    if tr_target=='건물' and first_trade=='sell' and '미등기' in building_important:
                        최상단알림창("미등기 건물은 매매등록하실 수 없습니다.")
                        print("=== 등록취소")
                        # self.finished.emit(False)
                        return
                    # else:
                    #     최상단알림창("미등기 건물이 아닙니다.")

            except Exception as e:
                print(f"변수설정 에러확인:{e}") 
                # [2026-09-05 추가 — 사용자 요청] 원래 print만 하고 그대로 다음 단계로 넘어가던 자리다.
                # headless 실행에선 이 print가 어디에도 안 남아 예외가 통째로 사라졌고, 이후 단계가
                # 여기서 못 만든 변수를 참조해 NameError로 터지면 오류로그에는 "name 'xxx' is not
                # defined"만 찍혀 진짜 원인을 알 수 없었다.
                #
                # 진행 흐름은 일부러 그대로 둔다(즉시 return 하지 않음) — 로그인용 변수는 이 블록
                # 앞부분에서 만들어져서, 뒷부분에서 난 예외는 지금도 등록이 진행되는 경우가 있을 수
                # 있고, 그걸 새로 실패로 바꾸면 안 되기 때문이다(사용자와 확인 후 "보고만 추가"로 결정).
                self.report_unexpected_exception(e, '변수설정 중')


            
            
            




    #webdriver 열기
            try:
                print("=== webdriver 열기")
                # ChromeDriver 경로 설정
                driver = webdriver.Chrome(options=options)
                # driver = webdriver.Chrome('/chromedriver', options=options)
                # driver = webdriver.Chrome(ChromeDriverManager().install())                
                # URL 열기
                driver.maximize_window()
                
                driver.get('https://www.serve.co.kr/member/login')
                driver.find_element(By.XPATH, '//*[@id="input-1"]').send_keys(naver_id)
                driver.find_element(By.XPATH, '//*[@id="input-3"]').send_keys(naver_pw)
                driver.find_element(By.XPATH, '//*[@id="app"]/div/div/div/div/div[2]/div[4]/button').click()

                #정상적으로 로그인된 상태가 될 때까지 대기
                WebDriverWait(driver, 10).until(
                    EC.text_to_be_present_in_element(
                        (By.XPATH, '//*[@id="app"]/div/div/header/div/div[2]/button[1]/span[3]/span[2]'), 
                        부동산상호명
                    )
                )
                # 로그인확인겸 첫 파란등록버튼 기다리기(관리자로 로그인시)
                driver.implicitly_wait(10)






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
                        print("❌ DB 연결 실패:", str(e))
                        return None, None  # 연결 실패 시 (None, None) 반환


                def 등록종료리스트검색결과건수():
                    # 검색결과요소 = WebDriverWait(driver, 5).until(
                    #     EC.presence_of_element_located((By.XPATH, '//div[@class="t-position-group"]//div[@class="total-area"]/span'))
                    # )
                    # 검색결과건수 = 검색결과요소.text
                    # # 알림창으로 값 표시
                    # pyautogui.alert(f"span 태그의 값이 10초 안에 1이 되지 않았습니다. 현재 값: {검색결과건수}", "알림")
                    try:
                        검색결과건수 = None
                        # span 태그를 찾고 값이 '1'일 때까지 대기
                        element = WebDriverWait(driver,2).until(
                            lambda d: d.find_element(By.XPATH, '//div[@class="t-position-group"]//div[@class="total-area"]/span').text == "1"
                        )
                        print("span 태그의 값이 1입니다.")
                        검색결과건수 = "1"
                        # pyautogui.alert("span 태그의 값이 1입니다.")
                    except Exception:
                        # 10초 안에 값이 1이 되지 않았을 경우
                        try:
                            # span 태그의 현재 값 가져오기
                            검색결과요소 = driver.find_element(By.XPATH, '//div[@class="t-position-group"]//div[@class="total-area"]/span')
                            검색결과건수 = 검색결과요소.text
                            # 알림창으로 값 표시
                            # print(f"span 태그의 값이 10초 안에 1이 되지 않았습니다. 현재 값: {검색결과건수}")
                            # pyautogui.alert(f"span 태그의 값이 10초 안에 1이 되지 않았습니다. 현재 값: {검색결과건수}", "알림")
                            
                        except Exception as e:
                            pyautogui.alert(f"span 태그를 찾을 수 없습니다. 오류: {e}", "오류")     
                        
                    return 검색결과건수   



                def 등록종료리스트에서검색(네이버매물번호):
                    # print("등록종료리스트에서검색: "+네이버매물번호)      
                    네이버매물번호입력요소 =  WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, '//*[@placeholder="매물번호를 입력해 주세요"]')
                        )
                    )
                    네이버매물번호입력요소.send_keys(네이버매물번호)    
                    네이버매물번호입력요소.send_keys(Keys.ENTER)   
                    driver.implicitly_wait(10)  
                    # time.sleep(1)
                    # print(f"검색완료 - 네이버매물번호: {네이버매물번호} ")                   


                def 연장등록(네이버매물정보, 검증방식, 실패_msg):
                    print(f"네이버매물정보:{네이버매물정보}")  
                    # pyautogui.alert(네이버매물정보, "네이버매물정보")

                    연장결과_msg = ""
                    새홈매물번호 = 네이버매물정보.get('object_code_new', '')
                    네이버매물번호 = 네이버매물정보.get('ad_code', '')
                    등록된메모 = 네이버매물정보.get('ad_memo', '')
                    object_rtype = 네이버매물정보.get('object_rtype', '')
                    object_ttype = 네이버매물정보.get('object_ttype', '')
                    object_tmoney1 = 네이버매물정보.get('object_tmoney1', '')
                    object_tmoney2 = 네이버매물정보.get('object_tmoney2', '')
                    object_mmoney = 네이버매물정보.get('object_mmoney', '')
                    print(f"연장등록:{네이버매물번호}, 검증방식:{검증방식}")  
                    #첫번째 리스트의 재등록버튼 클릭
                    driver.find_element(By.XPATH, f'//*[@id="printArea"]/div/table/tbody/tr/td[4]/div[2]/div[1]/button').click() 
                    # time.sleep(1) 

                    # 🌟 [신설] 기등록 중복 매물 알림 팝업창 실시간 감지 및 넘버 추출 엔진
                    try:
                        duplicate_code = "확인불가"
                        # 중복 안내 문구가 출력되는지 최대 2초간 동적 감시 실행
                        dup_msg_el = WebDriverWait(driver, 2).until(
                            EC.presence_of_element_located((By.XPATH, '//p[@class="alert-message" and contains(text(), "동일한 매물")]'))
                        )
                        popup_text = dup_msg_el.text
                        print(f"⚠️ [중복 매물 경고 발생] {popup_text}")
                        
                        # 정규식 패턴을 사용해 문장 속 기등록된 매물 번호 숫자 조각만 정밀 추출
                        match = re.search(r'\d+', popup_text)
                        if match:
                            duplicate_code = match.group(0)
                            print(f"🚨 [콘솔출력] 이미 다른 번호로 등록된 매물번호 포착 완료 ➡️ {duplicate_code}")
                            
                        # 팝업 컨테이너 내부의 [확인] 버튼을 자바스크립트로 강제 타격하여 차단 해제 및 폐쇄
                        confirm_btn = driver.find_element(By.XPATH, '//div[contains(@class, "modal-popup")]//button[.//span[text()="확인"]]')
                        driver.execute_script("arguments[0].click();", confirm_btn)
                        print("✅ 중복 매물 차단 알림창을 정상적으로 닫았습니다.")
                        
                        # 중복 매물이 있으면 더 이상 진행서식 입력이 불가능하므로 사유를 반환하고 즉시 함수를 안전하게 탈출시킵니다.
                        print(f"\n- 이미 동일한 매물번호({duplicate_code})가 노출 중이어서 연장 등록이 제한되었습니다.")
                        진단_기록(f"중복매물 팝업 감지 — duplicate_code={duplicate_code}로 조기 반환")

                    except Exception:
                        # 2초간 지켜봤는데 중복 팝업이 뜨지 않는다면 정상 클린 매물이므로 기존 로직대로 자연스럽게 무혈 통과합니다.
                        print("ℹ️ 중복 매물 팝업 없음 - 정상 연장 등록 양식 단계 진입")
                        진단_기록("중복매물 팝업 없음 — 정상 등록 흐름으로 진행")

                    # pyautogui.alert("다시보지않기 진입 시도") 
                    print("다시보지않기 진입 시도")
                    다시보지않기확인()          

                    if duplicate_code != '확인불가' : return duplicate_code


                    # pyautogui.alert(basic_secret, "basic_secret")
                    # 비밀메모요소 = 특정위치의x번째입력태그찾기('관리자 메모 (비공개 정보)', 'textarea', 1)
                    # pyautogui.alert(비밀메모요소.get_attribute('value'), "비밀메모요소")



                    def 기존값변경(입력란, 기존입력값, 신규입력값):
                        입력값글자수 = len(기존입력값)
                        입력란.send_keys(Keys.BACK_SPACE * 입력값글자수)   
                        입력란.send_keys(신규입력값)      

                    #기존에 등록된 거래정보
                    구거래종류 = 선택된라디오버튼텍스트가져오기('거래 종류')
                    print(f"구거래종류:{구거래종류}")  
                    if 구거래종류 == object_ttype:            
                        if 구거래종류 == '매매':
                            매매금액입력란 = 특정위치의x번째입력태그찾기('매매가', 'number', 1)
                            기존매매금액 = 매매금액입력란.get_attribute('value')
                            # print(f"기존매매금액:{기존매매금액}")
                            if int(object_tmoney1) != int(기존매매금액):
                                print(f"매매금액 수정:{기존매매금액} => {object_tmoney1}")
                                기존값변경(매매금액입력란,기존매매금액,object_tmoney1)
                                
                        elif 구거래종류  == '전세':
                            전세가입력란 = 특정위치의x번째입력태그찾기('전세가', 'number', 1)
                            기존전세가 = 전세가입력란.get_attribute('value')
                            # print(f"기존전세가:{기존전세가}")
                            if int(object_tmoney1) != int(기존전세가):
                                print(f"전세가 수정:{기존전세가} => {object_tmoney1}")
                                기존값변경(전세가입력란,기존전세가,object_tmoney1)
                        elif 구거래종류  == '월세':
                            보증금입력란 = 특정위치의x번째입력태그찾기('보증금', 'number', 1)
                            기존보증금 = 보증금입력란.get_attribute('value')
                            # pyautogui.alert(f"기존보증금:{기존보증금}")
                            월세입력란 = 특정위치의x번째입력태그찾기('월세', 'number', 1)
                            기존월세 = 월세입력란.get_attribute('value')
                            # pyautogui.alert(f"기존월세:{기존월세}")
                            if int(object_tmoney1) != int(기존보증금):
                                print(f"보증금 수정:{기존보증금} => {object_tmoney1}")
                                time.sleep(0.1)
                                기존값변경(보증금입력란,기존보증금,object_tmoney1)
                            if int(object_tmoney2) != int(기존월세):
                                print(f"월세 수정:{기존월세} => {object_tmoney2}")
                                기존값변경(월세입력란,기존월세,object_tmoney2)
                        
                        # 선택된부과방식이 '정액관리비 (세부내역 미고지한 경우)'인 경우에만 수정
                        선택된부과방식 = 선택된라디오버튼텍스트가져오기('부과방식')
                        #관리비별도이고 값이 변경된 경우
                        if object_mmoney and int(object_mmoney)>0 and 선택된부과방식 == '정액관리비 (세부내역 미고지한 경우)':
                            if object_rtype in ['원룸','투룸','쓰리룸 이상']: #주거용?
                                관리비입력란 = 특정위치의x번째입력태그찾기('관리비', 'number', 1)
                            else: #비주거용?
                                관리비입력란 = 특정위치의x번째입력태그찾기('월 관리비', 'number', 1)
                            기존관리비 = 관리비입력란.get_attribute('value')
                            if 기존관리비:
                                if int(object_mmoney*10000) != int(기존관리비):
                                    print(f"관리비 수정:{기존관리비} => {object_mmoney*10000}")
                                    기존값변경(관리비입력란,기존관리비,object_mmoney*10000)
                    #거래종류가 변경된 경우
                    else:
                        최상단알림창(f"[새홈]{새홈매물번호}\n\n등록된 거래종류와 다릅니다.\n확인시 거래종류와 금액이 수정됩니다.\n\n{구거래종류} => {object_ttype}")
                        def 가격정보삭제확인():
                            try:
                                # pyautogui.alert(f"확정버튼요소 확인")
                                가격정보삭제확인버튼요소 =  WebDriverWait(driver, 10).until(
                                    EC.element_to_be_clickable(
                                        (By.XPATH, '/html/body/div[2]/div/div[2]/div[1]/div[2]/div/div[2]/button')
                                    )
                                )   
                                가격정보삭제확인버튼요소.click()
                            except Exception as e:
                                print(f"가격정보삭제확인버튼 클릭 에러: {e}")
                                최상단알림창(f"가격정보삭제확인버튼 클릭 에러: {e}\n\n매물번호를 수동으로 추출해야합니다.")
                                # 연장결과_msg = '404'                        
                        # 연장결과_msg += f"{새홈매물번호} - 등록된 거래종류와 달라 거래금액이 수정되지 않음"

                        #임대에서 매매로 변경된 경우
                        if object_ttype == '매매':
                            라디오버튼선택('거래 종류', '매매')  
                            가격정보삭제확인()
                            매매금액입력란 = 특정위치의x번째입력태그찾기('매매가', 'number', 1)
                            매매금액입력란.send_keys(object_tmoney1)
                        elif object_ttype == '전세':
                            라디오버튼선택('거래 종류', '전세')  
                            가격정보삭제확인()
                            전세가입력란 = 특정위치의x번째입력태그찾기('전세가', 'number', 1)
                            전세가입력란.send_keys(object_tmoney1)
                        elif object_ttype == '월세':
                            라디오버튼선택('거래 종류', '월세')  
                            가격정보삭제확인()
                            보증금입력란 = 특정위치의x번째입력태그찾기('보증금', 'number', 1)
                            보증금입력란.send_keys(object_tmoney1)
                            월세입력란 = 특정위치의x번째입력태그찾기('월세', 'number', 1)
                            월세입력란.send_keys(object_tmoney2)
                        #매매에서 임대로 변경된 경우
                        #'월 관리비'항목중 '관리비 표시안함' 체크
                        try:
                            관리비표시안함체크박스 = 특정위치의x번째입력태그찾기('월 관리비', 'checkbox', 1)
                            관리비표시안함체크박스.click()
                        except:
                            fail_msg += '\n- 관리비표시안함 체크실패'  
                        #상세설명내용수정
                        pyautogui.alert(f"값수정 완료, 상세설명의 가격정보 표시부 확인필요!!")        
                    
                    
                    비밀메모요소 = 특정위치의x번째입력태그찾기('관리자 메모 (비공개 정보)', 'textarea', 1)
                    비밀메모 = 비밀메모요소.get_attribute('value')
                    if 비밀메모:
                        print("비밀메모 존재")
                    else:
                        print("비밀메모 내용없음")
                        최상단알림창("새홈:"+새홈매물번호+" ==> 비밀메모 채우기")

                    # pyautogui.alert(비밀메모요소.get_attribute('value'), "비밀메모요소")
                    
                    빠른이동("검증방식")

                    #네이버등록권
                    # pyautogui.alert("'써브N 일반 패키지' 요소찾기")
                    잔여수량요소 = driver.find_element(By.XPATH, f'//table//tr[td[text()="써브N 일반 패키지"]]/td[3]//span')
                    # pyautogui.alert("테스트결과:"+잔여수량요소.text)
                    print(f"잔여수량:{잔여수량요소.text}")
                    네이버등록권_자동선택(driver)
                    
                    동의결과_msg = 약관동의체크()
                    #의뢰인정보 위치 클릭
                    빠른이동("의뢰인 정보")
                    
                    #홍보확인서 작성
                    if 검증방식 != "모바일확인2": 
                        관계입력창 = 특정위치의x번째입력태그찾기('의뢰인과 등기부상 소유자와의 관계', 'text', 1)
                        입력된관계 = 관계입력창.get_attribute("value")
                        소유자명입력창 = 특정위치의x번째입력태그찾기('등기부상 소유자 이름', 'text', 1)
                        입력된소유자명 = 소유자명입력창.get_attribute("value")
                        if 입력된관계 != '':
                            홍보확인서작성(입력된소유자명, 입력된관계)
                        else:
                            pyautogui.alert(f"입력된관계:{입력된관계}, 입력된소유자명:{입력된소유자명}")
                        # pyautogui.alert(f"테스트중. 홍보확인서작성:\n")                             
                        # 최상단알림창(f"새홈번호:{object_code_new}\n\n홍보확인서 이미지 추가후 확인을 클릭하세요")
                        # pyautogui.alert(f"새홈번호:{object_code_new}\n\n홍보확인서 작성후 확인을 클릭하세요")

                    else:
                        print(f"메모에 '모바일확인V2'가 포함되어있습니다.\n등록된 메모:{등록된메모}")
                        # pyautogui.alert(f"메모에 '모바일확인V2'가 포함되어있습니다.\n\n등록된 메모:{등록된메모}")
                    if 동의결과_msg != "200": 
                        연장결과_msg += 동의결과_msg
                        pyautogui.alert(f"동의결과_msg: {동의결과_msg}")
                    #등록권선택
                    time.sleep(0.2)
                    #매물등록 버튼 클릭
                    try:
                        # [2026-09-02 수정] 기존 XPath(li[3] 인덱스 기반)가 실제로는 "임시저장" 버튼을
                        # 가리키고 있었다 — 라이브 재현으로 확인함(클릭 직후 "임시저장 하시겠습니까?"
                        # 확인창이 뜨는 걸 스크린샷으로 확인). 화면 우측 버튼 순서(예약등록/목록/
                        # 임시저장/매물등록)가 바뀌면 인덱스 기반 XPath는 계속 깨질 수 있으므로,
                        # 버튼 텍스트("매물등록")로 직접 찾도록 바꿔 순서 변화에 영향받지 않게 한다.
                        # pyautogui.alert(f"매물등록 확인")
                        # [2026-09-02 재수정] text()는 버튼의 "직접" 텍스트만 찾는데, 실제로는 이
                        # 버튼 텍스트가 자식 요소(span 등) 안에 있어서 못 찾았다(라이브 재현으로
                        # 확인 — "등록버튼 클릭 에러" 발생). contains(., ...)는 자손 요소를 포함한
                        # 전체 텍스트를 보므로 이런 구조에서도 찾는다.
                        매물등록버튼요소 =  WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable(
                                (By.XPATH, '//button[contains(., "매물등록")]')
                            )
                        )
                        매물등록버튼요소.click()
                        진단_기록("매물등록 버튼 클릭 성공")
                    except Exception as e:
                        print(f"등록버튼 클릭 에러: {e}")
                        최상단알림창(f"등록버튼 클릭 에러: {e}\n\n매물번호를 수동으로 추출해야합니다.")
                        연장결과_msg = '404'

                    # driver.find_element(By.XPATH, f'//*[@id="app"]/div/div/div[2]/div/div[2]/ul/li[3]/div/button').click()
                    #등록 확정버튼 클릭
                    # [2026-09-03 수정 — 실사용 중 재현된 버그] 두 버튼 다 절대경로 XPath(/html/body/div[2]/...)로
                    # 찾고 있었는데, 이 사이트는 Vue(Vuetify) SPA라 body의 실제 두번째 div는 페이지 콘텐츠가
                    # 아니라 모든 모달이 공유하는 렌더링 컨테이너(class="v-overlay-container")다 — 그 안의
                    # 몇 번째 자식을 가리키느냐는 "그 순간 모달이 몇 겹 떠 있는지"에 따라 완전히 달라진다.
                    # 실제로 2026-09-03에 네이버 무료 등록권(써브N 일반 패키지)이 0/300으로 소진돼 충전금
                    # 결제 경로(써브N 일반 단건)로 자동 전환됐는데, 이 결제 경로에서는 모달 겹수/구조가
                    # 달라져 절대경로가 엉뚱한 요소를 가리키면서 두 버튼 다 타임아웃났다(pr_log id=17176로
                    # 확인, 담당자 PC 재현은 결제 발생 문제로 아직 못 함 — 아래는 이 파일의 확인된 다른
                    # 모달 처리 방식(연장등록() 위쪽 "중복 매물 확인" 팝업, By.XPATH
                    # '//div[contains(@class,"modal-popup")]//button[.//span[text()="확인"]]')과 동일한
                    # 패턴으로 바꾼 것 — 실제 버튼 문구가 "확인"이 맞는지는 라이브 재현으로 아직 확정 못했다,
                    # 다음에 문제가 생기면 결제 후 실제 화면을 보고 문구를 확정할 것).
                    try:
                        # pyautogui.alert(f"확정버튼요소 확인")
                        time.sleep(0.2)
                        확정버튼요소 =  WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable(
                                (By.XPATH, '//div[contains(@class, "modal-popup")]//button[.//span[text()="확인"]]')
                            )
                        )
                        확정버튼요소.click()
                        진단_기록("확정버튼 클릭 성공 (modal-popup 셀렉터로 찾음)")
                    except Exception as e:
                        print(f"확정버튼 클릭 에러: {e}")
                        최상단알림창(f"확정버튼 클릭 에러: {e}\n\n매물번호를 수동으로 추출해야합니다.")
                        연장결과_msg = '404'

                    try:
                        # pyautogui.alert(f"확정버튼요소 확인")
                        완료확인버튼요소 =  WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable(
                                (By.XPATH, '//div[contains(@class, "modal-popup")]//button[.//span[text()="확인"]]')
                            )
                        )
                        완료확인버튼요소.click()
                        진단_기록("완료확인버튼 클릭 성공 (modal-popup 셀렉터로 찾음)")
                    except Exception as e:
                        print(f"완료확인버튼 클릭 에러: {e}")
                        최상단알림창(f"완료확인버튼 클릭 에러: {e}\n\n매물번호를 수동으로 추출해야합니다.")
                        연장결과_msg = '404'

                    
                    if 연장결과_msg == '404' : 
                        print("404 오류발생")         
                    else:
                        # if 연장결과_msg != '' : 최상단알림창(f"연장결과_msg:{연장결과_msg}\n\n") 
                        연장결과_msg = '200'                   
                    return 연장결과_msg

                def 약관동의체크():
                    동의실패_msg = ""
                    try:
                        # pyautogui.alert("1742 약관동의 시작")
                        # '모두동의 (필수)' 텍스트를 가진 label 태그 찾기
                        agreement_label = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, "//label[normalize-space(.)='모두동의 (필수)']"))
                        )
                        # pyautogui.alert("테스트 종료\n")
                        # label 태그와 연관된 checkbox 클릭
                        if agreement_label:
                            # label 태그의 for 속성을 사용하여 연관된 input 요소를 찾아 클릭
                            checkbox_id = agreement_label.get_attribute('for')
                            if checkbox_id:
                                print("checkbox_id:"+checkbox_id)
                                checkbox_element = driver.find_element(By.ID, checkbox_id)
                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox_element)
                                time.sleep(1) #대기시간필요
                                try:
                                    # 레이블 클릭 시도
                                    label_element = driver.find_element(By.CSS_SELECTOR, f'label[for="{checkbox_id}"]')
                                    label_element.click()
                                    print("Checkbox has been clicked through label.")
                                    return "200"
                                except Exception as e:
                                    print(f"Failed to click the checkbox through label: {e}")  
                                    동의실패_msg += f"약관동의 에러: {e}"          
                            else:
                                print("No checkbox ID found for the label.")
                                동의실패_msg += f"약관동의 에러: {e}"
                        else:
                            print("Label with text '모두동의 (필수)' not found.")
                            동의실패_msg += f"약관동의 에러: {e}"
                        # pyautogui.alert("정상?") 
        
                    except Exception as e:
                        print(f"약관동의 에러: {e}")
                        동의실패_msg += f"약관동의 에러: {e}"
                    
                    if 동의실패_msg: pyautogui.alert(f"동의실패_msg: {동의실패_msg}")
                    return 동의실패_msg                

                def 네이버매물번호제거(object_code_new, 실패_msg):
                    # print("네이버매물번호제거: 새홈"+object_code_new)  
                    제거실패_msg = 실패_msg
                    try:
                        # DELETE 쿼리 실행
                        query = """
                        DELETE FROM pr_externalad
                        WHERE object_code_new = %s AND ad_site = '네이버'
                        """
                        cursor.execute(query, (object_code_new,))  # 안전한 쿼리 실행
                        # pyautogui.alert(f"✅ DB에서 매물({object_code_new})의 네이버 매물번호가 삭제될 예정입니다.")
                        # 변경 사항 적용
                        conn.commit()

                        # 삭제된 행 개수 확인
                        if cursor.rowcount > 0:
                            print(f"✅ DB에서 매물({object_code_new})의 네이버 매물번호가 삭제되었습니다.")
                            # print(f"✅ DB에서 매물({object_code_new})의 네이버 매물번호가 삭제되었습니다. commit비활성")
                            # 제거실패_msg += f"\n- ✅ DB에서 매물({object_code_new})의 네이버 매물번호가 삭제되었습니다."
                            # pyautogui.alert(f"✅ DB에서 매물({object_code_new})의 네이버 매물번호가 삭제되었습니다.")
                            return "200"
                        else:
                            # print(f"⚠️ DB에서 매물({object_code_new})을 찾을 수 없거나 이미 삭제됨.")
                            제거실패_msg += f"\n- ⚠️ DB에서 매물({object_code_new})을 찾을 수 없거나 이미 삭제됨."
                    except Exception as e:
                        # print(f"❌ 네이버매물번호 삭제 중 오류 발생: {str(e)}")
                        제거실패_msg += f"\n- ❌ 새홈매물({object_code_new})의 네이버광고 삭제 중 오류 발생: {str(e)}"
                    
                    return 제거실패_msg
                    # finally:
                    #     cursor.close()
                    #     conn.close()                

                def 등록된매물번호추출(네이버매물정보):
                    print("등록된매물번호추출(네이버매물정보)")
                    print(f"네이버매물정보:{네이버매물정보}")
                    
                    object_code_new = 네이버매물정보.get('object_code_new', '')
                    네이버종료일 = 네이버매물정보.get('ad_end', '')
                    ad_memo = 네이버매물정보.get('ad_memo', '')
                    master_name = 네이버매물정보.get('master_name', '')
                    등록방식 = self.data.get('등록방식', {})
                    print(f"등록방식:{등록방식}")
                    if object_code_new == '':
                        object_code_new = self.data.get('writeData', {}).get('object_code_new', '')
                    # if isinstance(네이버매물정보, list):
                    #     object_code_new = self.data.get('adData', {}).get('네이버', {}).get('object_code_new', '')
                    # else:
                    #     object_code_new = self.data.get('writeData', {}).get('object_code_new', '')
                    # 네이버종료일 = self.data.get('adData', {}).get('네이버', {}).get('ad_end', '')
                    # 네이버종료일_date = datetime.strptime(네이버종료일, "%Y-%m-%d").date()
                    # pyautogui.alert(f"등록된매물번호추출{object_code_new}")
                    def get_ad_dates():
                        """
                        광고 시작일과 종료일을 반환합니다.
                        시작일은 오늘 날짜, 종료일은 30일 후 날짜입니다.
                        """
                        start_date = datetime.now().strftime("%Y-%m-%d")  # 오늘 날짜
                        end_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")  # 30일 후 날짜
                        return start_date, end_date

                    try:
                        # 매물번호 저장 딕셔너리 초기화
                        매물번호 = {"네이버": "", "써브": ""}
                        # 매물번호 = {"네이버": "", "써브": "", "KB부동산": ""}

                        # # 매물번호를 저장할 변수 초기화
                        # 네이버매물번호 = ""
                        # 써브매물번호 = ""
                        # KB매물번호 = ""
                        alert_message = ""
                        time.sleep(1)
                        # 테스트요소 = driver.find_element(By.XPATH, "//div[contains(@class, 't-content-registration')]/table[2]/tbody/tr[not(contains(@style, 'display: none'))]/td[1]")
                        # print(테스트요소.get_attribute('outerHTML'))
                        # pyautogui.alert(f"테스트값: {테스트요소.text}")
                        # XPath 지정
                        sources = {
                            "써브": '//div[@class="t-btn-item" and @title="써브"]//span[@data-v-2e0e3870 and text()]',
                            "네이버": '//div[@class="t-btn-item" and @title="네이버"]//span[@class="v-btn__content"]/span',
                            # "KB부동산": '//div[@class="t-btn-item" and @title="KB부동산"]//span[@class="v-btn__content"]/span',
                            "소유자이름": "//div[contains(@class, 't-content-registration')]/table[2]/tbody/tr[not(contains(@style, 'display: none'))]/td[1]"
                        }

                        try:
                            # 각 매물번호를 찾아서 변수에 저장
                            for source_name, xpath in sources.items():
                                try:
                                    element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, xpath)))
                                    매물번호[source_name] = element.text
                                except Exception as e:
                                    print(f"{source_name} 매물번호를 찾을 수 없습니다. 오류: {e}")
                                    alert_message = f"{source_name} 매물번호를 찾을 수 없습니다. 오류: {e}"
                                    매물번호[source_name] = "찾을 수 없음"
                                    # 네이버매물번호, 써브매물번호, KB매물번호를 매물번호 딕셔너리에서 가져옴
                                네이버매물번호 = 매물번호.get("네이버", "")
                                써브매물번호 = 매물번호.get("써브", "")
                                소유자이름 = 매물번호.get("소유자이름", "")
                                # KB매물번호 = 매물번호.get("KB부동산", "")     
                            if 네이버매물번호=='' or 써브매물번호=='':
                                최상단알림창(f"❌ 추출된 매물번호가 없습니다. \n\n네이버매물번호:{네이버매물번호}\써브매물번호:{써브매물번호}")
                            else:
                                # 결과 출력 (확인을 위해)
                                print(f"네이버매물번호: {네이버매물번호}")
                                print(f"써브매물번호: {써브매물번호}")
                                # print(f"KB매물번호: {KB매물번호}")
                                print(f"소유자이름: {소유자이름}")
                                print(f"master_name: {master_name}")
                        except  Exception as e:
                            최상단알림창(f"❌ 등록된 매물번호 추출 중 오류 발생: {str(e)}")
                        if master_name != '' :
                            if 소유자이름 in master_name:
                                print("소유자 존재")
                            else:
                                최상단알림창(f"소유자불일치\n\n기존소유자들:{master_name}\n현매물 소유자:{소유자이름}")
                        # pyautogui.alert(f"소유자이름{소유자이름}")
                        # DB 연결
                        conn = pymysql.connect(host='obangkr.cafe24.com', user='obangkr', password='Ddhqkd!1', charset='utf8')

                        # 광고 시작일과 종료일 계산
                        ad_start, ad_end = get_ad_dates()   

                        # 변수 확인
                        print(f"INSERT 쿼리에 사용될 변수:")
                        print(f"광고 담당자 아이디 (manager_id): {manager_id}")
                        print(f"새홈 매물번호 (object_code_new): {object_code_new}")
                        if 네이버매물정보:
                            print(f"광고 사이트 (ad_site): 네이버")
                            print(f"네이버 매물번호 (ad_code): {네이버매물번호}")
                            print(f"ad_memo: {ad_memo}")
                            print(f"날짜 (ad_udate): {current_date}")
                            print(f"시간 (ad_utime): {current_time}")
                            print(f"써브매물번호: {써브매물번호}")
                            print(f"네이버종료일: {네이버종료일},{type(네이버종료일)}")
                        
                        # pyautogui.alert(f"등록된매물번호추출{object_code_new}")
                        if 네이버종료일 and 네이버종료일 > 현재날짜:
                            광고상태 = "광고중"
                        else:
                            광고상태 = "광고종료"
                        # pyautogui.alert(f"광고상태:{광고상태}")   
                        if 네이버매물번호 != '찾을 수 없음':  
                            try:
                                # DictCursor 대신 기본 커서 사용
                                cursor = conn.cursor()
                                # cursor = conn.cursor(pymysql.cursors.DictCursor)
                                cursor.execute('USE obangkr;')

                                # 네이버 광고 여부 확인 쿼리
                                check_query = """
                                    SELECT *
                                    FROM pr_externalad
                                    WHERE object_code_new = %s AND ad_site = '네이버'
                                """
                                cursor.execute(check_query, (object_code_new))
                                # check_query = """
                                #     SELECT *
                                #     FROM pr_externalad
                                #     WHERE admin_id = %s AND object_code_new = %s AND ad_site = '네이버'
                                # """
                                # cursor.execute(check_query, (admin_id, object_code_new))
                                existing_record = cursor.fetchone()

                                if existing_record:

                                    # 기본 커서 결과를 컬럼별로 매핑
                                    columns = [desc[0] for desc in cursor.description]
                                    existing_record = dict(zip(columns, existing_record))                    
                                    print('광고 정보가 있는 경우 - 수정 작업 수행')
                                    # 기존 매물번호와 새 매물번호 비교
                                    current_ad_code = existing_record['ad_code']
                                                                        
                                    # ad_memo 값 처리
                                    existing_ad_memo = existing_record.get('ad_memo', '')  # 기존 ad_memo 값 가져오기
                                    new_ad_memo_part = f"써브:{써브매물번호}"
                                    if existing_ad_memo:
                                        # "써브:숫자9자리" 패턴이 이미 있는지 정규표현식으로 확인
                                        if re.search(r'써브:\d{9}', existing_ad_memo):
                                            # 기존 써브 매물번호를 새 값으로 교체
                                            new_ad_memo = re.sub(r'써브:\d{9}', new_ad_memo_part, existing_ad_memo)
                                        else:
                                            # 기존 ad_memo 뒤에 새 써브매물번호 추가
                                            new_ad_memo = f"{existing_ad_memo}, {new_ad_memo_part}"
                                    else:
                                        # 기존 ad_memo가 비어있으면 새 값만 사용
                                        new_ad_memo = new_ad_memo_part
                                    # new_ad_memo = f"{existing_ad_memo}, {new_ad_memo_part}".strip(', ') if existing_ad_memo else new_ad_memo_part
                    
                                    # # 변수 확인
                                    # print(f"UPDATE 쿼리에 사용될 변수:")
                                    # print(f"ad_memo 업데이트 값: {new_ad_memo}")   

                                    # # 알림창을 띄우고 테스트를 위해 중단
                                    # pyautogui.alert(f"""
                                    # 변수 값 확인:
                                    # - 새 매물번호: {네이버매물번호}
                                    # - 기존 매물번호: {current_ad_code}
                                    # - existing_ad_memo: {existing_ad_memo}
                                    # - new_ad_memo: {new_ad_memo}
                                    # - 담당자 아이디: {manager_id}
                                    # - 새홈 매물번호: {object_code_new}
                                    # 쿼리를 실행하지 않고 중단합니다. 확인 후 진행해주세요.
                                    # """)    

                                    print(f"기존 매물번호 (ad_code): {current_ad_code}")
                                    print(f"새 매물번호 (네이버매물번호): {네이버매물번호}")  

                                    # if current_ad_code == 네이버매물번호:
                                    #     alert_message = "담당자가 이미 동일한 네이버 광고 매물번호를 사용하고 있습니다."
                                    # else:
                                    
                                    # 기본 UPDATE 쿼리 구성
                                    update_query = """
                                        UPDATE pr_externalad
                                        SET ad_code = %s, ad_udate = %s, ad_utime = %s, ad_memo = %s
                                    """
                                    # 광고중이 아닌 경우 시작일과 종료일 추가
                                    if 광고상태 != "광고중":
                                        update_query += ", ad_start = %s, ad_end = %s"
                                    # WHERE 절 추가
                                    update_query += """
                                        WHERE admin_id = %s AND object_code_new = %s AND ad_site = '네이버'
                                    """

                                    # 쿼리에 사용할 변수 생성
                                    query_params = [네이버매물번호, current_date, current_time, new_ad_memo]
                                    # 광고중이 아닌 경우 시작일과 종료일 파라미터 추가
                                    if 광고상태 != "광고중":
                                        query_params.extend([ad_start, ad_end])
                                    # WHERE 절에 사용할 파라미터 추가
                                    query_params.extend([manager_id, object_code_new])

                                    # query_preview = f"""
                                    # UPDATE pr_externalad
                                    # SET ad_code = '{네이버매물번호}', ad_start = '{ad_start}', ad_end = '{ad_end}', ad_udate = '{current_date}', ad_utime = '{current_time}', 
                                    #     ad_memo = '{new_ad_memo}'
                                    # WHERE admin_id = '{manager_id}' AND object_code_new = '{object_code_new}' AND ad_site = '네이버';
                                    # """
                                    # pyautogui.alert(f"실행될 쿼리문:\n{query_preview}")

                                    try:
                                        # 쿼리 실행
                                        cursor.execute(update_query, tuple(query_params))
                                        
                                        # 영향을 받은 행의 수 확인
                                        affected_rows = cursor.rowcount

                                        if affected_rows > 0:
                                            if manager_id and object_code_new and 네이버매물번호 and 써브매물번호 : 
                                                conn.commit()    
                                                print(f"✅ DB에서 매물({object_code_new})의 네이버 매물번호를 업데이트 하였습니다.") 
                                                if 등록방식 == '단일매물등록':
                                                    alert_message = f"업데이트를 완료하였습니다. {affected_rows}개의 행이 변경되었습니다."
                                        else:                      
                                            alert_message = "업데이트할 내용이 없습니다. 기존 매물번호와 동일한 매물번호일 수 있습니다."

                                    except Exception as e:
                                        alert_message = f"쿼리 실행 중 오류가 발생했습니다: {e}"
                                
                                
                                else:
                                    print('광고 정보가 없는 경우 - 추가 작업 수행')
                                    insert_query = """
                                        INSERT INTO pr_externalad (
                                            admin_id, object_code_new, ad_start, ad_end, ad_site, ad_code, ad_manager, ad_manager_id, ad_udate, ad_utime, ad_memo, ad_wdate, ad_wtime
                                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                    """

                                    # ad_memo 구성
                                    ad_memo = f"{admin_name} 등록, 써브:{써브매물번호}"
                                    # ad_memo = f"써브:{써브매물번호}, KB부동산:{KB매물번호}"
                                    print(f"ad_memo 업데이트 값: {ad_memo}")

                                    # 알림창으로 쿼리 확인
                                    query_preview = f"""
                                    INSERT INTO pr_externalad (
                                        admin_id, object_code_new, ad_start, ad_end, ad_site, ad_code, ad_manager, ad_manager_id, ad_udate, ad_utime, ad_memo
                                    ) VALUES (
                                        '{manager_id}', '{object_code_new}', '{ad_start}', '{ad_end}', '네이버', '{네이버매물번호}', '{admin_name}', '{manager_id}', '{current_date}', '{current_time}', '{ad_memo}'
                                    );
                                    """
                                    # pyautogui.alert(f"실행될 쿼리문:\n{query_preview}")

                                    try:
                                        # 쿼리 실행
                                        conn.begin()  # 트랜잭션 시작
                                        cursor.execute(insert_query, (
                                            manager_id, object_code_new, ad_start, ad_end, '네이버', 네이버매물번호, admin_name, manager_id, current_date, current_time, ad_memo, current_date, current_time
                                        ))
                                        if manager_id and object_code_new and 네이버매물번호 and 써브매물번호 :
                                            conn.commit()
                                            print(f"✅ DB에 매물({object_code_new})의 네이버 매물번호를 추가 하였습니다.") 
                                            alert_message = f"새 네이버 광고 매물이 추가되었습니다.\n\n부동산써브: {써브매물번호}\n네이버부동산: {네이버매물번호}\n\n작업을 종료합니다."
                                        else:
                                            alert_message = f"DB에 등록하기 위한 필수정보가 확인되지 않습니다.\n\manager_id: {manager_id}\nobject_code_new: {object_code_new}\n네이버매물번호: {네이버매물번호}\써브매물번호: {써브매물번호}\n\n작업을 종료합니다."
                                    except Exception as e:
                                        alert_message = f"추가 작업 중 오류가 발생했습니다: {e}"

                                # if not self.wait_for_confirmation("1단계 작업이 완료되었습니다. 계속 진행할까요?"):
                                #     self.finished.emit(False)
                                #     return

                                # # 다른 단계에서도 활용
                                # if not self.wait_for_confirmation("2단계 작업을 진행할까요?"):
                                #     self.finished.emit(False)
                                #     return

                                print("모든 작업 완료")
                                # self.finished.emit(True)
                            except Exception as e:
                                conn.rollback()  # 오류 시 롤백
                                pyautogui.alert(f"오류 발생: {e}")
 
                            # 알림창으로 결과 표시
                            if alert_message : 
                                print(alert_message)
                                # pyautogui.alert(alert_message)      
                                최상단알림창(alert_message)                         
                    except Exception as e:
                        pyautogui.alert(f"오류 발생: {e}", "오류")  
                        driver.close()          

                def 기간만료매물확인(네이버매물정보, 실패_msg, 연장_count, 종료_count, check_set):
                    # object_code_new = 네이버매물정보.get('object_code_new', '')


                    # print(f"네이버 매물번호 추출테스트 진행 중...{object_code_new}")
                    # driver.get('https://ma.serve.co.kr/good/articleTrsmDetail?atclNo=323888355')
                    # 등록된매물번호추출(네이버매물정보)
                    # pyautogui.alert(f"네이버 매물번호 추출테스트 완료")

                    print(f"새홈[{object_code_new}] 네이버 매물번호 {등록된매물번호} 기간만료매물확인 진행 중..................................................")
                    # 부동산써브 등록종료 리스트 접속
                    driver.get('https://ma.serve.co.kr/good/articleRegistEndList')
                    
                    검색전_결과건수 = 등록종료리스트검색결과건수()
                    print("검색전_결과건수:"+str(검색전_결과건수))
                    검색전_결과건수 = str(검색전_결과건수).replace(',', '')  # 쉼표 제거

                    #등록된 매물번호로 네이버종료리스트에서 조회
                    if int(검색전_결과건수) > 0:
                        등록종료리스트에서검색(등록된매물번호)
                        검색결과건수 = 등록종료리스트검색결과건수()
                        print(f"매물상태:{매물상태}, 검색후 검색결과건수:{str(검색결과건수)}")
                        # pyautogui.alert(f"네이버매물번호: {네이버매물정보}")

                        #등록된 네이버매물번호로 1개가 검색되고 해당 매물의 매물상태가 '중개요청'이면 연장등록
                        if int(검색결과건수) == 1 and  매물상태 == '중개요청':
                            print(f"기존 네이버매물({등록된매물번호}) 연장등록")
                            검증방식 = driver.find_element(By.XPATH, '//*[@id="printArea"]/div/table/tbody/tr/td[4]/p[1]').text
                            연장등록결과 = 연장등록(네이버매물정보, 검증방식, 실패_msg)
                            if 연장등록결과 != "200" : 
                                실패_msg += 연장등록결과
                                pyautogui.alert(f"이미등록된 매물입니다. 써브매물번호: {연장등록결과}")
                            else:
                                연장_count = 연장_count + 1
                                #매물등록버튼 클릭
                                # pyautogui.alert(f"연장등록결과: {연장등록결과}")
                                
                                등록된매물번호추출(네이버매물정보)

                                
                        #등록된 매물번호로 조회되지 않거나 중개요청상태가 거래완료일 경우
                        else:
                            #등록된 매물번호의 매물 거래상태가 '거래완료'이거나 조회되지 않으면서 광고종료일이 1개월이상 경과된 경우 네이버부동산에서 매물삭제
                            광고종료일_기한초과 = 네이버종료일 + timedelta(days=30) < 현재날짜 #광고종료 30일이상 경과
                            if 매물상태 == '거래완료' or (int(검색결과건수) == 0 and 광고종료일_기한초과):
                                # pyautogui.alert(f"네이버매물번호제거 대기")
                                print(f"DB에서 매물({object_code_new})의 기존 네이버매물번호({등록된매물번호}) 제거")
                                제거결과 = 네이버매물번호제거(object_code_new, 실패_msg)
                                if 제거결과 == "200" : 
                                    종료_count = 종료_count + 1
                                else:
                                    실패_msg += 제거결과
                            else:
                                # pyautogui.alert(f"실패 대기")
                                if 매물상태 == '중개요청' and not 광고종료일_기한초과:
                                    print("등록종료리스트에 없으나 광고기간이 종료후 30일이내 중개요청상태 매물")
                                    check_set.append(object_code_new)
                                실패_msg += f"\n- 매물({object_code_new})의 기존 네이버매물번호({등록된매물번호})로 조회된 결과가 이상합니다."
                                print(f"매물({object_code_new})의 기존 네이버매물번호({등록된매물번호})로 조회된 결과가 이상합니다.")
                    
                    # pyautogui.alert(f"네이버매물번호: {네이버매물정보}")

                    return 실패_msg, 연장_count, 종료_count, check_set

                    
                def 미확인매물광고제거(object_code_new):
                    print("미확인매물광고제거: 새홈"+object_code_new)  
                    제거실패_msg = 실패_msg
                    try:
                        # DELETE 쿼리 실행
                        query = """
                        DELETE FROM pr_externalad
                        WHERE object_code_new = %s
                        """
                        cursor.execute(query, (object_code_new,))  # 안전한 쿼리 실행
                        # pyautogui.alert(f"✅ DB에서 매물({object_code_new})의 네이버 매물번호가 삭제될 예정입니다.")
                        # 변경 사항 적용
                        conn.commit()

                        # 삭제된 행 개수 확인
                        if cursor.rowcount > 0:
                            print(f"✅ DB에서 미확인 매물({object_code_new}) {str(cursor.rowcount)}개를 제거하였습니다.")
                            # print(f"✅ DB에서 매물({object_code_new})의 네이버 매물번호가 삭제되었습니다. commit비활성")
                            # 제거실패_msg += f"\n- ✅ DB에서 매물({object_code_new})의 네이버 매물번호가 삭제되었습니다."
                            # pyautogui.alert(f"✅ DB에서 매물({object_code_new})의 네이버 매물번호가 삭제되었습니다.")
                        else:
                            print(f"⚠️ DB에서 매물({object_code_new})을 찾을 수 없거나 이미 삭제됨.")
                            # 제거실패_msg += f"\n- ⚠️ DB에서 매물({object_code_new})을 찾을 수 없거나 이미 삭제됨."
                    except Exception as e:
                        print(f"\n- ❌ 새홈매물({object_code_new})의 외부광고 삭제 중 오류 발생: {str(e)}")
                        # 제거실패_msg += f"\n- ❌ 새홈매물({object_code_new})의 외부광고 삭제 중 오류 발생: {str(e)}"
                    
                    # return 제거실패_msg

                #필수항목체크(소재지,금액)


                        
                        
                    
                # #기능테스트 위치
                # driver.get('https://ma.serve.co.kr/good/articleTrsmDetail?atclNo=320884158')
                # print("추출창 열기 성공")
                # # 네이버매물정보 = self.data.get('adData', {}).get('네이버', {})[0]
                # # pyautogui.alert(f"테스트중.\n\nad_naver_list:\n{ad_naver_list}")
                # # pyautogui.alert(f"테스트중.\n\nad_naver_list:\n{ad_naver_list}")
                # if isinstance(ad_naver_list, list):
                #     네이버매물정보 = self.data.get('adData', {}).get('네이버', {})[0]
                # else:
                #     네이버매물정보 = ad_naver_list
                # print(f"네이버매물정보:{네이버매물정보}")
                # 등록된매물번호추출(네이버매물정보)
                # pyautogui.alert(f"테스트중.\n\n복사된 매물번호:\n{네이버매물정보}")
















                # 기등록 네이버매물번호가 존재여부확인
                # ad_naver_list = self.data.get('adData', {}).get('네이버', [])
                if isinstance(ad_naver_list, list):  # 여러 개의 만료 광고 처리
                    conn,cursor = DB연결후ConCursor반환()
                    확인결과_msg = ""
                    실패_msg = ""        
                    기간만료_count = 0   
                    연장_count = 0   
                    종료_count = 0   
                    미확인_count = 0 
                    check_set = []      
                    for 네이버매물정보 in ad_naver_list: 
                        manager_id = 네이버매물정보.get('admin_id', '')
                        object_code_new = 네이버매물정보.get('object_code_new', '')
                        등록된매물번호 = 네이버매물정보.get('ad_code', '')
                        매물상태 = 네이버매물정보.get('object_status', '')
                        네이버종료일 = 네이버매물정보.get('ad_end', '')
                        # pyautogui.alert(f"ad_memo:{ad_memo}")
                        if 매물상태:
                            기간만료_count = 기간만료_count + 1
                            확인결과_msg,연장_count,종료_count,check_set = 기간만료매물확인(네이버매물정보, 실패_msg, 연장_count, 종료_count, check_set)  # 

                        else:
                            미확인_count = 미확인_count + 1
                            # pyautogui.alert(f"존재하지 않는 매물번호({object_code_new})로 외부광고가 존재함. 매물상태:{매물상태}")
                            미확인매물광고제거(object_code_new)
                        # 네이버매물번호 = 네이버매물정보.get('ad_code', '')
                    print(f"확인결과_msg", 확인결과_msg)
                    check_list = ','.join(check_set)
                    최상단알림창(f"기간만료매물확인 종료알림\n\n총 처리건수:{str(len(ad_naver_list))}\n\n기간만료매물확인 - {기간만료_count}건(연장 {연장_count}건, 종료 {종료_count}건)\n미확인매물 - {미확인_count}건\n종료일 확인이 필요한 매물list - {check_list}\n"+확인결과_msg)

                else:  # 기존 방식 유지
                    네이버매물번호 = ad_naver_list.get('ad_code', '')
                    # 단일매물처리(네이버매물번호)            
                    # 네이버매물번호 = self.data.get('adData', {}).get('네이버', {}).get('ad_code', '')  # 키가 존재하지 않을 경우 기본값 반환

                    print(f"네이버매물번호: {네이버매물번호}")
                    ad_memo = self.data.get('adData', {}).get('네이버', {}).get('ad_memo', '')
                    print(f"네이버메모: {ad_memo}")

                    # "써브:" 뒤의 숫자 추출
                    써브뒤숫자 = re.search(r'써브:(\d+)', ad_memo)
                    print(f"써브뒤숫자: {써브뒤숫자}")

                    써브매물번호 = 써브뒤숫자.group(1) if 써브뒤숫자 else ''  # 숫자를 추출하거나 빈 문자열 반환
                    print(f"써브매물번호: {써브매물번호}")

                    네이버종료일 = self.data.get('adData', {}).get('네이버', {}).get('ad_end', '')
                    if not 네이버종료일:
                        print("네이버종료일 키가 존재하지 않거나 값이 비어 있습니다.")
                    else:
                        print(f"네이버종료일: {네이버종료일},{type(네이버종료일)}")
                    # 네이버종료일이 유효한 날짜인지 확인
                    if 네이버매물번호:
                        if 네이버종료일:
                            print(f"현재날짜: {현재날짜}")
                            try:
                                # 종료일_날짜 = datetime.combine(네이버종료일, datetime.min.time())  # date -> datetime 변환            
                                # # 종료일_날짜 = datetime.strptime(네이버종료일, '%Y-%m-%d')  # 종료일이 문자열인 경우 datetime 객체로 변환
                                try:
                                    # print(f"[DEBUG] 종료일_날짜: {종료일_날짜} (타입: {type(종료일_날짜)})")
                                    # print(f"[DEBUG] 현재날짜시간: {현재날짜시간} (타입: {type(현재날짜시간)})")
                                    # 날짜 단위로 비교
                                    if 네이버종료일 < 현재날짜 - timedelta(days=365):
                                        print(f"네이버종료일({네이버종료일})이 1년이 경과되었습니다.")
                                        네이버매물번호 = ''  # 1년이 지났으면 네이버매물번호를 공백으로 설정
                                    else:
                                        print("네이버종료일이 1년 이내입니다.")
                                except Exception as e:
                                    print(f"에러확인:{e}") 
                            except ValueError as e:
                                print(f"네이버종료일이 유효한 날짜 형식이 아닙니다. (형식: YYYY-MM-DD){e}")
                                네이버매물번호 = ''
                        else:
                            print("네이버종료일이 존재하지 않습니다.")
                            네이버매물번호 = ''
                    # pyautogui.alert("네이버매물번호:"+네이버매물번호)




















                    #신규등록
                    if 네이버매물번호 == '':
                        print("신규등록 함수시작")
                        if '외국인' in client_type:
                            print("client_type:"+client_type)
                            pyautogui.alert(f"등기확인여부:{등기부확인여부}, 등기부상소유자:{등록된소유자들}\n\n- 외국인일 경우\n1.본인명의 휴대폰통신사에 가입된 영문이름\n2.영문이름이 등기수상 한글이름과 발음이 동일(써브문의:02-2087-7300-1-0)","네이버 매물등록 전 주의사항")
                        
                        # 확인후 매물등록페이지로 이동
                        driver.get('https://ma.serve.co.kr/good/articleRegistManage/')
                        
                        #확인매물등록시 주의사항 체크
                        try:
                            label_xpath = '//label[text()="확인 매물 등록 시 주의사항을 확인하였습니다."]'
                            # 라벨 클릭 대기
                            label_element = WebDriverWait(driver, 20).until(
                                EC.presence_of_element_located((By.XPATH, label_xpath))
                            )
                            label_element.click()
                            print("라벨을 클릭하여 체크박스를 선택했습니다.")
                        except Exception as e:
                            pyautogui.alert(f"라벨 클릭 중 오류 발생: {e}")
                        # WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//label[text()="확인 매물 등록 시 주의사항을 확인하였습니다."]'))).click()
                        # time.sleep(0.5) 

                        # if not self.wait_for_confirmation("1단계 작업이 완료되었습니다. 계속 진행할까요?"):
                        #     self.finished.emit(False)
                        #     return

                    #기본정보
                        #매물분류
                        #주거용&방개수1 => 원룸, 상업용
                        print("obinfo_type1:", obinfo_type1, "obinfo_type2:", obinfo_type2)
                        if obinfo_type1 == '':
                            # objectCheckTime()
                            pyautogui.alert("매물분류 선택후 확인을 눌러주세요!!")
                            매물분류1차 = driver.find_element(By.XPATH, '//*[@id="app"]/div/div/div[3]/div/div[1]/div[4]/table/tbody/tr[1]/td/div[1]/div[1]/div/div[1]/div/div[3]/div/div/span').text
                            매물분류2차 = driver.find_element(By.XPATH, '//*[@id="app"]/div/div/div[3]/div/div[1]/div[4]/table/tbody/tr[1]/td/div[1]/div[1]/div/div[1]/div/div[3]/div/div/span').text
                            # 
                            # obinfo_type1 = 매물분류1차
                            # obinfo_type2 = 매물분류2차
                        else:
                            try:
                                time.sleep(0.3)
                                if tr_target == '토지':
                                    매물분류1차 = '토지'
                                    매물분류2차 = representing_jimok
                                else:
                                    # 🚀 roomData 장부에서 실제 건축물대장상 호실 주용도를 추출합니다.
                                    room_purpose = self.data.get('roomData', {}).get('room_purpose', '')

                                    # 🎯 대장상 주용도에 '오피스텔'이 포함되어 있다면 최우선 오피스텔 규격 가동
                                    if '오피스텔' in room_purpose:
                                        매물분류1차 = '오피스텔'
                                        if object_type == '주거용':
                                            매물분류2차 = '주거용'
                                        elif object_type == '상업용':
                                            매물분류2차 = '업무용'
                                        else:
                                            매물분류2차 = 그룹별명칭변환('매물분류2차', obinfo_type2)

                                    # 오피스텔이 아닌 일반 건물들은 소장님의 기존 매핑 규칙을 안전하게 유지합니다.
                                    else:
                                        if obinfo_type1 == '아파트/빌라':
                                            if obinfo_type2 in ['아파트']:
                                                매물분류1차 = obinfo_type2
                                            else:
                                                매물분류1차 = '주택'    
                                        else:
                                            print("obinfo_type1값이 '아파트/빌라'가 아닙니다. obinfo_type1:",obinfo_type1)
                                            매물분류1차 = 그룹별명칭변환('매물분류1차', obinfo_type1)
                                        매물분류2차 = 그룹별명칭변환('매물분류2차', obinfo_type2)

                                print("매물분류1차:", 매물분류1차, "매물분류2차:", 매물분류2차)
                                # pyautogui.alert("매물분류1차:"+매물분류1차+", 매물분류2차:"+매물분류2차)
                                #소분류
                                특정위치X번째셀렉트에서선택('매물 분류', 1, 매물분류1차)
                                # 다시보지않기확인()  
                                if obinfo_type1 == '상가/점포': 다시보지않기확인()
                                #대분류 
                                특정위치X번째셀렉트에서선택('매물 분류', 2, 매물분류2차)
                                # pyautogui.alert(f"{obinfo_type1} {obinfo_type2} 클릭 완료!")
                                
                            except Exception as e:
                                print(f"An error occurred: {e}")
                                pyautogui.alert("요소를 찾을 수 없습니다.")        
                    
                        # pyautogui.alert("테스트중입니다.") 

                        #거래종류 obinfo_ttype 
                        print("1754 first_trade:"+first_trade)
                        if first_trade == 'sell':
                            거래종류선택값 = '매매'
                        else:
                            if first_trade == 'lease1':
                                거래종류선택값 = '월세' if float(obinfo_rent1) > 0 else '전세'
                            elif first_trade == 'lease2':
                                거래종류선택값 = '월세' if float(obinfo_rent2) > 0 else '전세'
                            elif first_trade == 'lease3':
                                거래종류선택값 = '월세' if float(obinfo_rent3) > 0 else '전세'
                            else:
                                if ',' in obinfo_ttype: #쉼표가 있다면 쉼표로 분리후 첫번째 항목을 값으로 지정
                                    obinfo_ttype = obinfo_ttype.split(',')[0]
                                거래종류선택값 = obinfo_ttype     
                        라디오버튼선택('거래 종류', 거래종류선택값)  
                        # if ',' in obinfo_ttype: #쉼표가 있다면 쉼표로 분리후 첫번째 항목을 값으로 지정
                        #     obinfo_ttype = obinfo_ttype.split(',')[0]
                        # pyautogui.alert(f"테스트중입니다.")
                        # 라디오버튼선택('소재지', '산')  

                        # 변환된용도 = 그룹별명칭변환('건축물용도', '제1종 근린생활시설')
                        # 특정위치X번째셀렉트에서선택('건축물용도', 1, 변환된용도)
                        # pyautogui.alert(f"테스트중입니다.") 
                        # 검증방식선택및의뢰인정보입력(fail_msg) #테스트용

                    #매물소재지
                        print(location_do, location_si, location_dong, location_li, jibun)
                        리입력칸수 = 1
                        #소재지
                        특정위치X번째셀렉트에서선택('소재지', 1, 그룹별명칭변환('지역(시/도)', location_do))
                        특정위치X번째셀렉트에서선택('소재지', 2, location_si)
                        특정위치X번째셀렉트에서선택('소재지', 3, location_dong)
                        if location_li != '' and 매물분류2차 not in ['아파트','주거용'] : 
                            리입력창 = 특정위치의x번째입력태그찾기('소재지', 'text', 리입력칸수)
                            리입력창.send_keys(location_li)
                            리입력창.send_keys(Keys.ENTER) 
                            # time.sleep(0.3)
                        
                        # time.sleep(0.5); print("type_path ok:", self.data['type_path'])
                        # pyautogui.alert("go?"+"\n"+"매물분류2차:"+매물분류2차)
                        if 매물분류2차 in ['아파트','주거용']:
                            #단지선택
                            if 매물분류2차 == '아파트':
                                단지선택항목 = brtit_bldNm
                                # 특정위치X번째셀렉트에서선택('단지', 3, brtit_bldNm)
                            elif 매물분류2차 == '주거용':
                                단지선택항목 = building_name
                                # 특정위치X번째셀렉트에서선택('단지', 1, 단지선택항목)
                            최상단알림창(f"단지 선택후 확인을 클릭하여 주십시오.\n\n※예상단지명: {단지선택항목}(동:{brtit_dongNm}, 호수:{room_num}), 공급면적:{basic_area2}", "단지선택")
                            # pyautogui.alert(f"단지 선택후 확인을 클릭하여 주십시오.\n\n※예상단지명: {단지선택항목}(동:{brtit_dongNm}, 호수:{room_num}), 공급면적:{basic_area2}", "단지선택")
                            
                            #평형선택(전용면적이 포함되어 있는 항목 선택)
                            try:
                                if 매물분류2차 in ['아파트','주거용']:
                                    # 문자열의 마지막 글자가 '동'인지 확인
                                    # 마지막 '동' 제거
                                    brtit_dongNm = brtit_dongNm[:-1] if brtit_dongNm.endswith('동') else '1'
                                    # brtit_dongNm = brtit_dongNm[:-1] if brtit_dongNm.endswith('동') else ''
                                    if room_num.endswith('호'):
                                        room_num = room_num[:-1]

                                    if 매물분류1차 == '아파트':
                                        #'동/호 선택'라디오 박스 활성화상태 확인
                                        동호선택요소 = 특정위치의x번째입력태그찾기('단지', 'radio', 1)
                                        if 동호선택요소.is_enabled() :
                                            동호선택요소.click()
                                            특정위치X번째셀렉트에서선택('단지', 2, brtit_dongNm)
                                            특정위치X번째셀렉트에서선택('단지', 3, room_num)
                                            # pyautogui.alert("1동호선택요소를 클릭가능합니다.")
                                        else:
                                            특정위치X번째셀렉트에서선택('단지', 2, basic_area2)
                                            # pyautogui.alert("1동호선택요소를 클릭할 수 없습니다.")

                                    elif 매물분류1차 == '오피스텔':
                                        특정위치X번째셀렉트에서선택('단지', 2, basic_area2)
                                    
                            except Exception as e:
                                print(f"An error occurred: {e}")
                                최상단알림창(f"단지선택 실패\n\n※예상단지명: {단지선택항목}(동:{brtit_dongNm}, 호수:{room_num}), 공급면적:{basic_area2}")
                        else:
                            리입력칸수 = 1
                            if self.data['type_path']=='산':
                                # driver.find_element(By.XPATH, '//*[@id="ismount2"]').click()
                                # time.sleep(0.5)
                                라디오버튼선택('소재지', '산')
                                # pyautogui.alert("'산'선택확인 go??")
                                if location_li == '':
                                    지번입력파트 = 특정위치의x번째입력태그찾기('소재지', 'text', 리입력칸수+1)
                                else:
                                    지번입력파트 = 특정위치의x번째입력태그찾기('소재지', 'text', 리입력칸수+2)
                                jibun = jibun[1:]
                            else:
                                라디오버튼선택('소재지', '일반')
                                if location_li == '':
                                    지번입력파트 = 특정위치의x번째입력태그찾기('소재지', 'text', 리입력칸수)
                                else:
                                    지번입력파트 = 특정위치의x번째입력태그찾기('소재지', 'text', 리입력칸수+1)
                            # pyautogui.alert("지번입력파트 go??")
                            지번입력파트.send_keys(jibun)
                                
                                # driver.find_element(By.XPATH, 일반지번입력파트).send_keys(self.data['landData'][0]['land_jibun'])
                            
                            #건물명,상세주소
                            # 상세주소값 = ''
                            상세주소입력파트 = 특정위치의x번째입력태그찾기('상세주소', 'text', 1)
                            if tr_target == '토지':
                                # 상세주소값 = location_detail.strip()
                                print("상세주소값:"+상세주소값)
                            else:
                                print("building_name:"+building_name)
                                if '무명건물' not in building_name:
                                    if 매물분류1차 not in ['상가점포','사무실']:
                                        특정위치의x번째입력태그찾기('건물명', 'text', building_name)
                                # if tr_target == '건물':
                                #     상세주소값 = location_building.strip()
                                # elif tr_target == '층호수':
                                #     상세주소값 = location_room.strip()
                                
                                # print("상세주소값:"+상세주소값)
                            # pyautogui.alert("상세주소값:"+상세주소값)
                            라디오버튼선택('상세주소', '상세주소 없음') if 상세주소값.strip() == '' else  상세주소입력파트.send_keys(상세주소값)
                            if '일부부' in 상세주소값: pyautogui.alert("'일부부'가 포함된 상세주소값:"+상세주소값)
                            # 표시용상세주소값 = 상세주소값.split(',')[0].strip()# 쉼표 기준으로 분리하고 첫 번째 요소만 가져옴(대표 호실의 등기부만 사용하기 위함)
                            # 라디오버튼선택('상세주소', '상세주소 없음') if 표시용상세주소값.strip() == '' else  상세주소입력파트.send_keys(표시용상세주소값)

                            #기타 참고 주소
                            if tr_target == '토지':
                                if '미등기' in land_important:
                                    라디오버튼선택('기타 참고 주소', '미등기')
                                    I_memo += ("\n" if I_memo else "") + 메모에마크추가("미등기토지로 자세한 토지정보는 문의바랍니다." , '· ')
                            else:
                                if '미등기' in building_important:
                                    라디오버튼선택('기타 참고 주소', '미등기')
                                    I_memo += ("\n" if I_memo else "") + 메모에마크추가("미등기건물로 자세한 건물정보는 문의바랍니다." , '· ')
                            # pyautogui.alert("building_important:"+building_important)
                            #지도
                            if object_type == '주거용':
                                라디오버튼선택('지도', '지도 표시')
                            else:
                                라디오버튼선택('지도', '지도 표시안함')
                            
                        # pyautogui.alert("go?"+brtit_bldNm)
                    #가격정보
                        print('first_trade:'+first_trade+'obinfo_ttype:'+str(obinfo_ttype)+' obinfo_trading:'+str(obinfo_trading)+' obinfo_deposit1:'+str(obinfo_deposit1)+' obinfo_rent1:'+str(obinfo_rent1))
                        if first_trade == 'sell':
                            print("매매가: ",obinfo_trading)
                            if obinfo_trading:
                                if 매물분류1차 == '원룸':
                                    pyautogui.alert("매물분류 '원룸'은 매매로 등록이 불가합니다.\n\n프로중개인에서 매물분류 변경후 다시 시도하세요!!")
                                    driver.quit()
                                특정위치의x번째입력태그찾기('매매가', 'number', 1).send_keys(obinfo_trading) #매매가
                                trading_memo += "\n"+"-- 거래종류 : "+obinfo_ttype
                                trading_memo += "\n"+"-- 거래금액 : "+한글금액(obinfo_trading)
                        # pyautogui.alert("go?")
                        else:
                            
                            # pyautogui.alert("go?")
                            if first_trade == 'lease1':
                                보증금값 = obinfo_deposit1
                                월세값 = round(float(obinfo_rent1))
                            elif first_trade == 'lease2':
                                보증금값 = obinfo_deposit2
                                월세값 = round(float(obinfo_rent2))
                            elif first_trade == 'lease3':
                                보증금값 = obinfo_deposit3
                                월세값 = round(float(obinfo_rent3))
                            else:
                                보증금값 = obinfo_deposit1
                                월세값 = round(float(obinfo_rent1))
                            보증금카테고리명 = '전세가' if (월세값=='' or int(월세값)==0) else '보증금'
                            print(f"first_trade:{first_trade} 보증금값:{보증금값}, 월세값:{월세값}, 보증금카테고리명:{보증금카테고리명}")
                            # pyautogui.alert("go?")
                            보증금입력파트 = 특정위치의x번째입력태그찾기(보증금카테고리명, 'number', 1)
                                
                            보증금입력파트.send_keys(보증금값)
                            rent_memo += "\n"+"-- 거래종류 : "+obinfo_ttype
                            rent_memo += "\n"+"-- 보증금 : "+한글금액(보증금값)

                            if 월세값 > 0:
                                print("월세: ",월세값)
                                월세입력파트 = 특정위치의x번째입력태그찾기('월세', 'number', 1)
                                월세입력파트.send_keys(월세값)
                                rent_memo += "\n"+"-- 월세 : "+한글금액(월세값)
                                if flexible_deposit == 'Y':
                                    rent_memo += "\n※보증금조정가능(문의)"
                            else:
                                print("월세값 없음")

                        # if obinfo_ttype == '매매':
                        #     print("매매가: ",obinfo_trading)
                        #     if obinfo_trading:
                        #         if obinfo_type1 == '원룸':
                        #             pyautogui.alert("매물분류 '원룸'은 매매로 등록이 불가합니다.\n\n프로중개인에서 매물분류 변경후 다시 시도하세요!!")
                        #             driver.quit()
                        #         특정위치의x번째입력태그찾기('매매가', 'Number', 1).send_keys(obinfo_trading) #매매가
                        #         trading_memo += "\n"+"-- 거래종류 : "+obinfo_ttype
                        #         trading_memo += "\n"+"-- 거래금액 : "+한글금액(obinfo_trading)
                        # # pyautogui.alert("go?")
                        # if (obinfo_ttype=='전세' or obinfo_ttype=='월세') and obinfo_deposit1:
                        #     print("보증금: ",obinfo_deposit1)
                        #     보증금카테고리명 = '전세가' if obinfo_ttype=='전세' else '보증금'
                        #     보증금입력파트 = 특정위치의x번째입력태그찾기(보증금카테고리명, 'Number', 1)
                        #     보증금입력파트.send_keys(obinfo_deposit1)
                        #     rent_memo += "\n"+"-- 거래종류 : "+obinfo_ttype
                        #     rent_memo += "\n"+"-- 보증금 : "+한글금액(obinfo_deposit1)
                        #     if obinfo_ttype=='월세' and obinfo_rent1:
                        #         print("월세: ",obinfo_rent1)
                        #         월세입력파트 = 특정위치의x번째입력태그찾기('월세', 'number', 1)
                        #         월세입력파트.send_keys(obinfo_rent1)
                        #         rent_memo += "\n"+"-- 월세 : "+한글금액(obinfo_rent1)
                        #         if obinfo_deposit2:
                        #             rent_memo += "\n※보증금조정가능(문의)"
                        #     # pyautogui.alert("go?")
                        if 매물분류1차 in ['상가점포','사무실']:
                            if premium_exist == '있음':
                                if premium.isdigit():
                                    특정위치의x번째입력태그찾기('권리금', 'number', 1).send_keys(premium)
                                premium_memo = "\n"+"-- 권리금(시설비) : " + (한글금액(premium) if premium.isdigit() else premium)
                                premium_memo += "\n"+"-- 권시물내역 : " + premium_content + " 등" if premium_content else "\n"+"-- 권시물내역 : 확인필요"

                    #관리비 부과정보
                        
                        if tr_target != '토지': 
                            if tr_target == '건물':
                                if 매물분류1차 in ['주택']:
                                    라디오버튼선택('부과방식', '확인불가')
                                    라디오버튼선택('부과기준', '직전 월 관리비')
                                    특정위치X번째셀렉트에서선택('확인불가 사유',1,'건축법 시행령 발표1의 제1호 가목의 단독주택') #확인불가 사유
                                else:
                                    try:
                                        관리비표시안함체크박스 = 특정위치의x번째입력태그찾기('월 관리비', 'checkbox', 1)
                                        관리비표시안함체크박스.click()
                                    except:
                                        fail_msg += '\n- 관리비표시안함 체크실패'     
                            elif tr_target == '층호수':               
                                if basic_manager == '별도':
                                    if basic_mmoney == '': 
                                        basic_mmoney = 999999
                                        rent_memo += "\n"+"-- 관리비 확인필요"
                                    print("관리비:"+str(float(basic_mmoney))+" , 관리비항목들:"+관리비항목들)
                                    if 매물분류1차 in ['원룸','오피스텔','아파트','주택']:
                                        if float(basic_mmoney) < 100000:
                                            # 라디오버튼선택('부과방식', '정액관리비')
                                            라디오버튼선택('부과방식', '기타부과')
                                            라디오버튼선택('부과기준', '직전 월 관리비')
                                            #관리비세부내역
                                            특정위치X번째셀렉트에서선택('관리비 타입',1,'정액관리비가 10만원 미만인 경우')
                                            # pyautogui.alert("2686 go?")
                                            # 셀렉트항목선택('정액관리비가 10만원 미만인 경우', '//*[@id="app"]/div/div/div[3]/div/div[1]/div[9]/table/tbody/tr[1]/td/div[1]/div[1]')
                                            # 셀렉트항목선택('정액관리비이지만 중개의뢰인이 세부내역 미고지한 경우', '//*[@id="app"]/div/div/div[3]/div/div[1]/div[9]/table/tbody/tr[1]/td/div[1]/div[3]')
                                            특정위치의x번째입력태그찾기('관리비', 'number', 1).send_keys(int(basic_mmoney))
                                            라벨들로체크박스클릭('포함항목', 관리비항목들)
                                        elif float(basic_mmoney) >= 100000:
                                            라디오버튼선택('부과방식', '정액관리비 (세부내역 미고지한 경우)')
                                            라디오버튼선택('부과기준', '직전 월 관리비')
                                            #관리비세부내역
                                            특정위치X번째셀렉트에서선택('관리비 타입',1,'정액관리비이지만 중개의뢰인이 세부내역 미고지한 경우')
                                            # 셀렉트항목선택('정액관리비이지만 중개의뢰인이 세부내역 미고지한 경우', '//*[@id="app"]/div/div/div[3]/div/div[1]/div[9]/table/tbody/tr[1]/td/div[1]/div[3]')
                                            특정위치의x번째입력태그찾기('관리비', 'number', 1).send_keys(int(basic_mmoney))
                                            라벨들로체크박스클릭('포함항목', 관리비항목들)
                                    elif 매물분류1차 in ['사무실','상가점포']:
                                        특정위치의x번째입력태그찾기('월 관리비', 'number', 1).send_keys(int(basic_mmoney))
                                        # 라벨들로체크박스클릭('월 관리비', 관리비항목들)
                                        # pyautogui.alert("go?")
                                    else :
                                        라디오버튼선택('부과방식', '정액관리비 (세부내역 미고지한 경우)')
                                        라디오버튼선택('부과기준', '직전 월 관리비')
                                        특정위치X번째셀렉트에서선택('관리비 타입',1,'정액관리비이지만 중개의뢰인이 세부내역 미고지한 경우')
                                        특정위치의x번째입력태그찾기('월 관리비', 'number', 1).send_keys(int(basic_mmoney))
                                        라벨들로체크박스클릭('포함항목', 관리비항목들)
                                else:   
                                    print("basic_manager:" + basic_manager)
                                    if 매물분류1차 in ['아파트','주택','원룸','오피스텔']:
                                        if 매물분류2차 in ['아파트']:
                                            라디오버튼선택('부과방식', '기타부과')
                                            라디오버튼선택('부과기준', '직전 월 관리비')
                                            특정위치X번째셀렉트에서선택('관리비 타입',1,'관리규약 등에 따라부과')

                                        else:                                         
                                            라디오버튼선택('부과방식', '정액관리비 (세부내역 미고지한 경우)')
                                            라디오버튼선택('부과기준', '직전 월 관리비')
                                            특정위치X번째셀렉트에서선택('관리비 타입',1,'정액관리비이지만 중개의뢰인이 세부내역 미고지한 경우')
                                        특정위치의x번째입력태그찾기('관리비', 'number', 1).send_keys(100)
                                        rent_memo += "\n"+"-- 구체적인 관리비내역 별도문의"
                                        try:
                                            # 관리비없음체크박스 = 특정위치의x번째입력태그찾기('포함항목', 'checkbox', 1)
                                            # 관리비없음체크박스.click()
                                            print('"관리비 포함항목 없음" 체크전')
                                            라벨들로체크박스클릭('포함항목', '관리비 포함항목 없음')
                                            # 특정위치의x번째입력태그찾기('포함항목', 'checkbox', 9).click() # 관리비 포함항목 없음 체크
                                            print('"관리비 포함항목 없음" 체크후')
                                            # pyautogui.alert("1119 go? 체크박스 찾는데 너무 오래걸림ㅠ")
                                        except:
                                            fail_msg += '\n- 관리비없음 체크실패'

                                    # elif obinfo_type1 in ['아파트']:
                                    #     라디오버튼선택('부과방식', '기타부과')
                                    #     라디오버튼선택('부과기준', '직전 월 관리비')
                                    #     특정위치X번째셀렉트에서선택('관리비 타입',1,'관리규약 등에 따라부과')
                                    #     특정위치의x번째입력태그찾기('관리비', 'number', 1).send_keys(0)
                                    #     # 셀렉트항목선택('관리규약 등에 따라부과', '//*[@id="app"]/div/div/div[3]/div/div[1]/div[9]/table/tbody/tr[1]/td/div[1]/div[1]')
                                    #     라벨들로체크박스클릭('포함항목', 관리비항목들)     

                                    elif 매물분류1차 in ['공장창고']:
                                        특정위치의x번째입력태그찾기('월 관리비', 'checkbox', 1).click() 

                                    elif 매물분류1차 in ['원룸','상가점포','사무실']:    
                                        if obinfo_ttype=='매매':
                                            try:
                                                관리비없음체크박스 = 특정위치의x번째입력태그찾기('월 관리비', 'checkbox', 1)
                                                관리비없음체크박스.click()
                                            except:
                                                fail_msg += '\n- 관리비없음 체크실패'
                                        else:
                                            if basic_manager == '없음':
                                                if 매물분류1차 in ['상가점포','사무실']:
                                                    try:
                                                        관리비표시안함체크박스 = 특정위치의x번째입력태그찾기('월 관리비', 'checkbox', 1)
                                                        관리비표시안함체크박스.click()
                                                    except:
                                                        fail_msg += '\n- 관리비표시안함 체크실패'
                                                else:
                                                    특정위치의x번째입력태그찾기('확인불가 사유', 'text', 1).send_keys('실사용한만큼 납부') #확인불가 사유
                                                rent_memo += "\n"+"-- 관리비 별도 없음"
                                            else:
                                                print("obinfo_type:" + obinfo_type)
                                                if 매물분류1차 in ['원룸']:
                                                    라디오버튼선택('부과방식', '정액관리비 (세부내역 미고지한 경우)')
                                                    라디오버튼선택('부과기준', '직전 월 관리비')
                                                    특정위치X번째셀렉트에서선택('관리비 타입',1,'정액관리비이지만 중개의뢰인이 세부내역 미고지한 경우')
                                                    # 셀렉트항목선택('정액관리비이지만 중개의뢰인이 세부내역 미고지한 경우', '//*[@id="app"]/div/div/div[3]/div/div[1]/div[9]/table/tbody/tr[1]/td/div[1]/div[3]')
                                                    특정위치의x번째입력태그찾기('관리비', 'number', 1).send_keys(100)
                                                    특정위치의x번째입력태그찾기('포함항목', 'checkbox', 9).click() # 관리비 포함항목 없음 체크
                                                else:
                                                    관리비없음체크박스 = 특정위치의x번째입력태그찾기('월 관리비', 'checkbox', 1)
                                                    관리비없음체크박스.click()

                                        if basic_manager == '포함':
                                            rent_memo += "\n"+"-- 관리비 포함(문의)"
                                        elif basic_manager == '미확인':
                                            rent_memo += "\n"+"-- 관리비 내역 미확인 (문의)"
                                        


                                    # print("관리비 확인불가")
                                    # 라디오버튼선택('부과방식', '확인불가')
                                    # #확인불가사유
                                    # 셀렉트항목선택('미등기건물 신축건물 등 관리비 내역이 확인불가한 경우', '//*[@id="app"]/div/div/div[3]/div/div[1]/div[10]/table/tbody/tr/td/div')
                        
                        # pyautogui.alert("go?")

                    #매물정보
                        # pyautogui.alert("go?")
                        #건물유형
                        
                        if tr_target == '층호수':
                            B_memo += "\n"+"\n"+"□■ 건물정보"
                            R_memo += "\n"+"\n"+"□■ 호실정보"
                            if 매물분류1차 in ['원룸','주택']:
                                라디오버튼선택('건물유형', '건물 일부 (방 또는 일부)')
                        if tr_target == '건물':
                            B_memo += "\n"+"\n"+"□■ 건물정보"
                            if 매물분류1차 in ['원룸','주택']:
                                라디오버튼선택('건물유형', '건물 전체')
                        if tr_target == '토지' or tr_target == '건물':
                            L_memo += "\n"+"\n"+"□■ 토지정보" 
                        # pyautogui.alert("go?")    
                        if 매물분류1차 in ['오피스텔']:
                            #해당 동/호
                            특정위치의x번째입력태그찾기('해당 동/호', 'text', 1).send_keys(brtit_dongNm)
                            특정위치의x번째입력태그찾기('해당 동/호', 'text', 2).send_keys(room_num)
                        # pyautogui.alert("정상?") 
                        
                        #연면적
                        if 매물분류1차 in ['주택', '공장창고', '빌딩건물']:
                            # pyautogui.alert(f"tr_target:{tr_target},tr_target:{tr_target}") 
                            print('building_totarea:'+str(building_totarea))
                            if tr_target == '건물' or 매물분류1차 in ['공장창고', '빌딩건물']:
                                if building_totarea : 특정위치의x번째입력태그찾기('연면적', 'text', 1).send_keys(building_totarea)   
                                if building_totarea: B_memo += "\n"+"-- 연면적: "+building_totarea+f"㎡ (약{제곱미터_평_변환(building_totarea)}평)"
                        #건축면적
                                if building_archarea : 특정위치의x번째입력태그찾기('건축면적', 'text', 1).send_keys(building_archarea)   
                                if building_archarea: B_memo += "\n"+"-- 건축면적: "+building_archarea+f"㎡ (약{제곱미터_평_변환(building_archarea)}평)"
                        
                        #대지면적
                        if 매물분류1차 in ['토지', '공장창고', '빌딩건물','주택']:
                            if tr_target in ['토지', '건물'] or 매물분류1차 in ['공장창고', '빌딩건물']:
                                print('land_totarea:'+str(land_totarea))
                                if land_totarea : 특정위치의x번째입력태그찾기('대지면적', 'text', 1).send_keys(land_totarea)   
                                # pyautogui.alert("L_memo:"+L_memo)
                                if land_totarea: L_memo += "\n"+"-- 대지면적: "+land_totarea+f"㎡ (약{제곱미터_평_변환(land_totarea)}평)"
                        #계약면적
                        if 매물분류1차 in ['상가점포','사무실']:
                            print('basic_area2:'+str(basic_area2))
                            basic_area2 = basic_area1 if (basic_area2 == '' or basic_area2 == '') else basic_area2
                            # pyautogui.alert("정상?") 
                            if 매물분류2차 in ['지식산업센터']:
                                특정위치의x번째입력태그찾기('공급면적', 'text', 1).send_keys(str(basic_area2))
                            else:
                                특정위치의x번째입력태그찾기('임대(계약)면적', 'text', 1).send_keys(str(basic_area2))
                            if basic_area2: R_memo += "\n"+"-- 계약면적: "+basic_area2+f"㎡ (약{제곱미터_평_변환(basic_area2)}평)"
                        #전용면적
                        if 매물분류1차 in ['원룸','주택','상가점포','사무실']:
                            print('basic_area1:'+str(basic_area1)+' basic_rcount:'+str(basic_rcount))
                            if object_type == '주거용' and (basic_area1=='' or basic_area1==''):
                                if basic_rcount == '1':
                                    basic_area1 = '20'
                                elif basic_rcount == '1.5':
                                    basic_rcount = '1'
                                    basic_area1 = '25' 
                                elif basic_rcount == '1.8':
                                    basic_rcount = '1'
                                    basic_area1 = '30' 
                                elif basic_rcount == '2':
                                    basic_area1 = '50' 
                                else:
                                    basic_area1
                                
                            if building_type != '집합' and tr_target == '층호수':
                                r_add_memo = "\n"+"※ 일반건물의 전용면적은 실측면적과 다를 수 있습니다."
                            try:
                                특정위치의x번째입력태그찾기('전용면적', 'text', 1).send_keys(str(basic_area1))
                            except:
                                fail_msg += '\n- 전용면적 입력실패'
                            if basic_area1: R_memo += "\n"+"-- 전용면적: "+str(basic_area1)+f"㎡ (약{제곱미터_평_변환(basic_area1)}평)"
                        #공급면적
                        if 매물분류1차 in ['원룸','오피스텔','주택']:
                            print('basic_area2:'+str(basic_area2))
                            if basic_area1:
                                basic_area2 = basic_area1 if (basic_area2=='' or basic_area2=='') else basic_area2
                                try:
                                    특정위치의x번째입력태그찾기('공급면적', 'text', 1).send_keys(str(basic_area2))
                                except:
                                    fail_msg += '\n- 공급면적 입력실패'     
                                if basic_area2: R_memo += "\n"+"-- 공급면적: "+str(basic_area2)+f"㎡ (약{제곱미터_평_변환(basic_area2)}평)"

                        if tr_target=='건물':
                                #해당층
                                print('building_grndflr:'+str(building_grndflr))
                                특정위치의x번째입력태그찾기('지상 / 지하 총층', 'number', 1).send_keys(str(building_grndflr))
                                if building_grndflr: R_memo += "\n"+"-- 지상층: "+str(building_grndflr)+"층"
                            # pyautogui.alert("정상?")   
                            #총층
                                print('building_ugrndflr:'+str(building_ugrndflr))
                                특정위치의x번째입력태그찾기('지상 / 지하 총층', 'number', 2).send_keys(str(building_ugrndflr))
                                if building_ugrndflr: R_memo += "/지하층: "+str(building_ugrndflr)+"층"
                        elif tr_target=='층호수':
                            print('basic_floor:'+basic_floor+' basic_totflr:'+basic_totflr)
                            #해당층 #해당동 총층
                            if 매물분류2차 in ['주거용','아파트']:
                                if 매물분류2차 in ['주거용']: #아파트일 경우 동/호수 선택시 해당층 값이 자동입력되어 수동으로 입력할 필요없음
                                    특정위치의x번째입력태그찾기('해당층 / 해당동 총층', 'text', 1).send_keys(basic_floor)
                                # 특정위치의x번째입력태그찾기('해당층 / 해당동 총층', 'number', 1).send_keys(str(building_grndflr))
                            else:
                                특정위치의x번째입력태그찾기('해당층 / (해당동) 총층', 'text', 1).send_keys(basic_floor)
                                특정위치의x번째입력태그찾기('해당층 / (해당동) 총층', 'number', 1).send_keys(basic_totflr) 
                                if basic_floor: R_memo += "\n"+"-- 해당층: "+basic_floor+"층"
                            basic_totflr += "\n"+"-- 총층: "+basic_totflr+"층"
                            # pyautogui.alert("정상?")   
                            #층노출동의여부
                            if 매물분류2차 in ['일반원룸','주택','주거용']:
                                if object_type == '주거용':
                                    라디오버튼선택('층노출 동의여부', '동의안함 (고/중/저 노출)')
                                else:
                                    라디오버튼선택('층노출 동의여부', '동의 (층 노출)')
                            elif 매물분류2차 in ['아파트']:
                                특정위치의x번째입력태그찾기('층노출 동의여부', 'radio', 2).click()
                        #방수/욕실수
                        if 매물분류1차 in ['원룸','주택', '상가점포']:
                            if tr_target == '층호수':                               
                                # if basic_bcount: R_memo += " / 욕실수: "+basic_bcount      
                                if 매물분류1차 in ['원룸', '주택']:
                                    if  매물분류2차 == '일반원룸':
                                        라디오버튼선택('방수 / 욕실수', '1개')
                                        특정위치의x번째입력태그찾기('방수 / 욕실수', 'number', 1).send_keys(basic_bcount)
                                    else:
                                        특정위치의x번째입력태그찾기('방수 / 욕실수', 'number', 1).send_keys(basic_rcount)
                                        특정위치의x번째입력태그찾기('방수 / 욕실수', 'number', 2).send_keys(basic_bcount)
                                        R_memo += ("\n"+"-- 방수: "+basic_rcount) if basic_rcount and float(basic_rcount) > 0 else ("\n"+"-- 방없음")
                                        R_memo += ("\n"+"-- 욕실수: "+basic_bcount) if basic_bcount and int(basic_bcount) > 0 else ("\n"+"-- 욕실없음")   

                            elif tr_target == '건물':
                                print("1344 building_element:"+building_element)
                                basic_rcount = '0'
                                basic_bcount = '0'
                                # 숫자 추출 및 합산
                                if building_element:
                                    # 숫자 추출 및 합산
                                    basic_rcount = str(sum(map(int, re.findall(r'[+-]?\d+', building_element))))
                                    # pyautogui.alert(basic_rcount)
                                else:
                                    fail_msg += '\n- 건물 구성 확인필요'
                                print("1354 건물구성 개수:"+basic_rcount)
                                if float(basic_rcount) > 1 : B_memo += "\n"+"-- 건물구성(호실): "+basic_rcount   


                        #방향
                        # print('r_direction:'+r_direction+" room_direction:"+room_direction)
                        if tr_target == '층호수':
                            print('room_direction:'+str(room_direction))
                            room_direction = '남' if room_direction == '' else room_direction
                            if 매물분류1차 in ['상가점포','사무실']:
                                특정위치X번째셀렉트에서선택('방향', 1, room_direction)
                                # 셀렉트항목선택(room_direction, '//*[@id="app"]/div/div/div[3]/div/div[1]/div[11]/table/tbody/tr[13]/td/div[1]/div')
                            #방향기준/방향
                            elif 매물분류1차 in ['아파트','원룸','오피스텔','주택']:
                                방향기준값=r_direction if r_direction != '' else '안방'
                                특정위치X번째셀렉트에서선택('방향기준 / 방향', 1, 방향기준값)
                                if room_direction: 특정위치X번째셀렉트에서선택('방향기준 / 방향', 2, room_direction)                                
                        elif tr_target == '건물':
                            print('building_direction:'+str(building_direction))
                            if building_direction == '':
                                fail_msg += '\n- 건물방향 입력실패'
                            else:
                                if 매물분류1차 in ['아파트','주택']:
                                    특정위치X번째셀렉트에서선택('방향기준 / 방향', 2, building_direction)
                                else:
                                    특정위치X번째셀렉트에서선택('방향', 1, building_direction)
                                print("건물방향 선택완료: " + building_direction)
                            

                        # pyautogui.alert("방향기준/방향 확인") 
                        #세대(가구수)
                        if tr_target != '토지':
                            print("세대(가구수) building_type:" + building_type )
                            if building_type == '집합':
                                print("세대(가구수) building_hhld:" + str(building_hhld) )
                                세대가구수 = building_hhld
                            else:
                                print("세대(가구수) building_fmly:" + str(building_fmly) )
                                세대가구수 = building_fmly
                            if 매물분류1차 in ['원룸','주택']:
                                특정위치의x번째입력태그찾기('세대(가구수)', 'number', 1).send_keys(세대가구수)
                        # pyautogui.alert("세대(가구수) 확인")
                        #방거실형태
                        if 매물분류1차 in ['주택']:
                            라디오버튼선택('방거실형태', '분리형')
                        # pyautogui.alert("방거실형태 확인")
                        #복층여부
                        if 매물분류1차 in ['원룸','오피스텔','주택']:
                            if '복층형' in room_important:
                                라디오버튼선택('복층여부', '복층')
                            else:
                                라디오버튼선택('복층여부', '단층')
                        # pyautogui.alert("복층여부 확인")
                        #주차가능여부
                        if 매물분류1차 in ['원룸','오피스텔','주택','아파트','상가점포','사무실']:
                            print('building_pn:'+str(building_pn)+' building_option:'+building_option)
                            if building_pn=='0' and '주차장' not in building_option:
                                라디오버튼선택('주차가능여부', '주차 불가능')
                                # 특정위치의x번째태그찾기('주차가능여부', 'radio', 2).click()
                            else:
                                라디오버튼선택('주차가능여부', '주차 가능')
                                # 주차가능여부파트 = 특정위치의x번째태그찾기('주차가능여부', 'radio', 2)
                                # 주차가능여부파트.click()
                            # pyautogui.alert("총주차대수 확인")  
                            
                        #총주차대수
                        if tr_target != '토지' : 
                            print('building_pn:'+str(building_pn))
                            if 매물분류2차 in ['아파트','주거용']:
                                print('세대당주차대수값:'+str(세대당주차대수값)+" building_pn:"+str(building_pn))
                                #세대당 
                                특정위치의x번째입력태그찾기('세대당 / 총 주차대수', 'text', 1).send_keys(str(세대당주차대수값))
                                #총
                                특정위치의x번째입력태그찾기('세대당 / 총 주차대수', 'number', 1).send_keys(str(building_pn))
                            else:
                                특정위치의x번째입력태그찾기('총 주차대수', 'number', 1).send_keys(str(building_pn))
                        
                        #건축구조
                        if tr_target == '건물':
                            if 매물분류1차 in ['공장창고', '상가건물']:
                                if building_stract: B_memo += "\n"+"-- 건물구조: "+building_stract
                                try:
                                    if building_stract: 특정위치X번째셀렉트에서선택('건축구조', 1, 그룹별명칭변환('건축구조', building_stract))
                                except:
                                    fail_msg += '\n- 건축구조 선택실패'
                        #용도지역
                        if tr_target == '건물' or tr_target == '토지':
                                if land_totarea: L_memo += "\n"+"-- 주용도지역: "+representing_purpose
                                try:
                                    if representing_purpose: 특정위치X번째셀렉트에서선택('용도지역', 1, representing_purpose)
                                except:
                                    fail_msg += '\n- 용도지역 선택실패'
                        #사용전력
                                try:
                                    if building_bolt: 
                                        if building_bolt: B_memo += "\n"+"-- 사용전력: "+building_bolt+" KW"
                                        if building_bolt <= 25:
                                            전력범위값 = "25Kw이하"
                                        elif 25 < building_bolt <= 50:
                                            전력범위값 = "25~50"
                                        elif 50 < building_bolt <= 100:
                                            전력범위값 = "50~100"
                                        elif 100 < building_bolt <= 1000:
                                            전력범위값 = "100~1000"
                                        elif 1000 < building_bolt <= 10000:
                                            전력범위값 = "1000~10000"
                                        else:
                                            전력범위값 = "10000Kw 이상"
                                        print("전력범위값:"+전력범위값)
                                        특정위치X번째셀렉트에서선택('사용전력', 1, 전력범위값)
                                except:
                                    fail_msg += '\n- 사용전력 선택실패'
                        #위반건축물여부
                        특정위치X번째셀렉트에서선택('위반건축물여부', 1, '표시안함')
                        특정위치X번째셀렉트에서선택('위반건축물여부', 1, '표시안함')
                        # if tr_target != '토지':
                        #     위반건축물여부 = '예' if '위반건축물' in building_important else '아니오'
                        #     print("위반건축물여부:"+위반건축물여부)
                        #     특정위치X번째셀렉트에서선택('위반건축물여부', 1, 위반건축물여부)  
                        # pyautogui.alert("위반건축물여부 확인")  

                        #건축물용도
                        if tr_target != '토지' : 
                            print('building_purpose:'+str(building_purpose))
                            if 매물분류2차 in ['아파트','주거용']:
                                공동주택키워드s = ['공동주택', '다세대', '연립', '업무시설']
                                # 공동주택키워드s = ['공동주택', '다세대', '연립']
                                # building_purpose에 키워드 중 하나라도 포함되어 있는지 확인
                                if any(keyword in building_purpose for keyword in 공동주택키워드s):
                                    건축물용도선택값 = 2
                                elif '숙박시설' in building_purpose:
                                    건축물용도선택값 = 3
                                elif '2종' in building_purpose:
                                    건축물용도선택값 = 4
                                elif '근린생활' in building_purpose:
                                    건축물용도선택값 = 3
                                elif '업무시설' in building_purpose:
                                    건축물용도선택값 = 4
                                else:
                                    건축물용도선택값 = 1
                                특정위치의x번째입력태그찾기('건축물용도', 'radio', 건축물용도선택값).click()
                            else:
                                # 💡 상위 폴더에 구축한 공용 유틸리티 함수에게 [원본 용도, 전용면적]을 매개변수로 전달합니다.
                                mapped_purpose = 건축법상건축물용도로변환(building_purpose, basic_area1)

                                # 🛞 최종 반환된 결과에 따른 네이버 부동산 폼 제어 및 예외 처리
                                if mapped_purpose:
                                    # 공용 함수가 성공적으로 값을 찾아 반환해 준 경우
                                    특정위치X번째셀렉트에서선택('건축물용도', 1, mapped_purpose)
                                    print(f"✅ [공용 유틸 자동매핑 성공] {building_purpose} ➡️ {mapped_purpose}")
                                else:
                                    # "근생" 등 애매한 단어로 인해 공용 함수가 None을 반환한 경우 (안전 수동 우회 메커니즘)
                                    print(f"⚠️ [공용 유틸 자동매핑 실패] 수동 선택 유도 (DB값: {building_purpose})")
                                    try:
                                        strong_elements = driver.find_elements(By.XPATH, "//th/strong")
                                        for strong in strong_elements:
                                            if '건축물용도' in strong.get_attribute('textContent').replace(' ', ''):
                                                tr_elem = strong.find_element(By.XPATH, './ancestor::tr')
                                                target_div = tr_elem.find_element(By.XPATH, ".//div[contains(@class, 't-select-area-group') or contains(@class, 't-select-item')]//div[@aria-haspopup='menu']")
                                                target_div.click()
                                                break
                                    except Exception as click_err:
                                        print(f"드롭다운 미리 열기 실패 (수동 선택은 가능): {click_err}")

                                    # 최상단 고정 알림창으로 안전하게 검수 요청
                                    최상단알림창(
                                        f"🚨 건축물 용도 자동 매핑 실패\n\n"
                                        f"• DB에 저장된 원래 용도: [ {building_purpose} ]\n\n"
                                        f"공용 매칭 사전에 정의되지 않은 특이 용도입니다.\n"
                                        f"브라우저 화면에서 알맞은 건축물 용도를 '직접 선택'해 주신 뒤,\n"
                                        f"이 알림창의 [확인]을 눌러 계속 진행해 주세요.",
                                        "건축물 용도 수동 선택"
                                    )

                                # 📌 [데이터 누적] 소장님의 소중한 B_memo 주용도 텍스트 결합 로직은 완벽 유지!
                                B_memo += "\n"+"-- 건축물 주용도: "+building_purpose
                            if 매물분류1차 in ['원룸','오피스텔','주택','상가점포','사무실','공장창고','빌딩건물']:
                                #건축물일자
                                # 셀렉트항목선택('사용승인일', '//*[@id="app"]/div/div/div[3]/div/div[1]/div[11]/table/tbody/tr[31]/td/div[1]/div[1]/div/div[1]')
                                # pyautogui.alert("사용승인일선택 확인")
                                print('building_usedate:'+str(building_usedate))
                                usedate = building_usedate.split("-")
                                if building_usedate == '0000-00-00':
                                    특정위치X번째셀렉트에서선택('건축물일자', 1, '준공인가일')
                                    특정위치X번째셀렉트에서선택('건축물일자',2,'2010')
                                    특정위치X번째셀렉트에서선택('건축물일자',3,'없음')
                                    # 셀렉트항목선택('준공인가일', '//*[@id="app"]/div/div/div[3]/div/div[1]/div[11]/table/tbody/tr[31]/td/div[1]/div[1]')
                                    # 셀렉트항목선택('2010', '//*[@id="app"]/div/div/div[3]/div/div[1]/div[11]/table/tbody/tr[31]/td/div[1]/div[1]/div/div[2]')
                                    # 셀렉트항목선택('없음', '//*[@id="app"]/div/div/div[3]/div/div[1]/div[11]/table/tbody/tr[31]/td/div[1]/div[1]/div/div[3]')
                                else:
                                    특정위치X번째셀렉트에서선택('건축물일자', 1, '사용승인일')
                                    특정위치X번째셀렉트에서선택('건축물일자', 2, usedate[0])
                                    특정위치X번째셀렉트에서선택('건축물일자', 3, usedate[1])
                                    특정위치X번째셀렉트에서선택('건축물일자', 4, usedate[2])
                    #원룸/투룸 방찾기
                            #방구조(타입)
                            if 매물분류1차 in ['원룸','오피스텔','주택']:
                                if tr_target == '층호수':
                                    if '오픈형' in room_important:
                                        라디오버튼선택('방 구조(타입)', '오픈형')
                                    # elif '분리형' in room_important:
                                    else:
                                        라디오버튼선택('방 구조(타입)', '분리형')
                            #방특징
                                print('optionImportant: '+optionImportant)
                                optionImportant_list = optionImportant.split(',')
                                #방특징 목록생성
                                #신축: 준공일5년이내
                                
                                # current_date = datetime.now() #오류가 발생할 수 있음
                                if not building_usedate == '0000-00-00':
                                    usedate = datetime.strptime(building_usedate, '%Y-%m-%d')
                                    print(f'현재날짜:{현재날짜}, {type(현재날짜)}')
                                    print(f'현재날짜시간:{현재날짜시간}, {type(현재날짜시간)}')
                                    print(f'usedate:{usedate}, {type(usedate)}')
                                    # pyautogui.alert(len(optionImportant_list))
                                    years_difference = (현재날짜시간 - usedate).days / 365.25    
                                    if years_difference <= 5:
                                        if '신축' not in optionImportant_list:
                                            optionImportant_list.append('신축')                           
                                #풀옵션: 냉장고,세탁기,싱크대,가스렌지,에어컨 포함
                                required_fulloptions = {'냉장고', '세탁기', '싱크대', '가스렌지', '에어컨'}
                                if required_fulloptions.issubset(optionImportant_list): #optionImportant_list에 풀옵션 항목들이 있으면 '풀옵션'을 optionImportant_list배열에 추가
                                    if '풀옵션' not in optionImportant_list:
                                        optionImportant_list.append('풀옵션')
                                #큰길가: 중로이상 접
                                road_conditions = {'중로접', '광대로접', '대로접'}
                                if any(condition in optionImportant_list for condition in road_conditions):
                                    if '큰길가' not in optionImportant_list:
                                        optionImportant_list.append('큰길가')               
                                #엘리베이터: 건물옵션에 포함
                                #애완동물: 호실옵션에 포함
                                #옥탑: 해당층이 지상층이상

                                # optionImportant_list.append('큰길가') 
                                # pyautogui.alert(optionImportant_list,"optionImportant:")
                                # 변환된optionImportant = ','.join(optionImportant)
                                # pyautogui.alert("optionImportant:",변환된optionImportant)
                                방특징항목들 = 목록_변환('방특징', ','.join(optionImportant_list))
                                if 방특징항목들: 라벨들로체크박스클릭('방 특징', 방특징항목들)
                    #시설정보
                            # 💡 [냉방시설 고도화] DB의 두루뭉술한 에어컨 옵션을 메모 분석을 통해 정밀화합니다.
                            if '냉방기' in optionImportant or '냉난방기' in optionImportant:
                                # 호실메모(room_memo)와 비밀메모(tr_memo) 원본을 하나로 통합 스캔
                                trmemo_raw = self.data.get('writeData', {}).get('tr_memo', '')
                                combined_memos = str(room_memo) + " " + str(trmemo_raw)
                                
                                if any(kw in combined_memos for kw in ['시스템에어컨', '천정에어컨', '천장에어컨', '시스템']):
                                    정밀화된에어컨 = '천장에어컨'
                                elif any(kw in combined_memos for kw in ['스텐드형에어컨', '스텐드에어컨', '스탠드형에어컨', '스탠드에어컨', '스텐드']):
                                    # ⚠️ 웹사이트 HTML 표기 규격인 '스탠드'로 변환 유도
                                    정밀화된에어컨 = '스탠드에어컨'
                                else:
                                    # 기본 메모가 없거나 매칭되지 않는 경우 가드레일 작동
                                    정밀화된에어컨 = '벽걸이에어컨'
                                
                                # 데이터 주머니(optionImportant) 내부의 명칭을 정밀 단어로 전격 치환합니다.
                                optionImportant = optionImportant.replace('냉방기', 정밀화된에어컨).replace('냉난방기', 정밀화된에어컨)
                                print(f"❄️ [에어컨 정밀 분석 성공] 메모 기반 매핑 결과 ➡️ {정밀화된에어컨}")

                            print("optionImportant:"+optionImportant)
                            시설정보항목들 = 목록_변환('시설정보', optionImportant)
                            print("시설정보항목들:"+시설정보항목들)
                            if tr_target == '건물':
                                if building_important: B_memo += "\n"+"-- 건물특징: "+building_important
                                if building_option: B_memo += "\n"+"-- 건물옵션: "+building_option
                                # B_memo += "\n"+"-- 건물메모: "+building_memo
                            if tr_target == '층호수':
                                if room_important: R_memo += "\n"+"-- 호실특징: "+room_important
                                if room_option: R_memo += "\n"+"-- 호실옵션: "+room_option
                                
                                # 🚀 전처리 단계에서 이미 완벽하게 가공되었으므로, 단 한 줄로 깔끔하게 타격합니다!
                                if any(ac in 시설정보항목들 for ac in ['벽걸이에어컨', '스탠드에어컨', '천장에어컨']):
                                    라벨들로체크박스클릭('냉방시설', 시설정보항목들)

                            if 매물분류2차 not in ['주거용', '아파트'] :
                                #난방시설
                                특정위치X번째셀렉트에서선택('난방시설', 1, '개별난방')
                                #난방연료
                                특정위치X번째셀렉트에서선택('난방연료', 1, '도시가스')
                            # #냉방시설
                            # if 매물분류1차 not in ['아파트']:
                            #     라벨들로체크박스클릭('냉방시설', 시설정보항목들)
                            #생활시설
                            if 매물분류1차 in ['원룸','오피스텔','주택']:
                                라벨들로체크박스클릭('생활시설', 시설정보항목들)
                            #보안시설
                            라벨들로체크박스클릭('보안시설', 시설정보항목들)
                            #기타시설
                            라벨들로체크박스클릭('기타시설', 시설정보항목들)
                        else:
                            if land_important: L_memo += "\n"+"-- 토지특징: "+land_important
                    #매물상세정보
                        print('-------------------- 매물상세정보 시작')
                        #매물특징
                        title_location = location_dong if obinfo_ttype != '매매' else location_si
                        title_trade = obinfo_ttype if obinfo_ttype == '매매' else '임대'
                        title = "오산에서방구하기_" if object_type == '주거용' else ''
                        title += title_location  + " " + obinfo_type1 + " " + title_trade
                        특정위치의x번째입력태그찾기('매물특징', 'text', 1).send_keys(title)
                        #상세정보
                        description = ""
                        description += "\n"+" ━━━━━━━━━━━━━━━━━━━━━━"
                        description += "\n"+" 【 오산 " + 그룹별명칭변환('전문분야', object_type) + " 전문 『 나상권공인중개사사무소 』】"
                        description += "\n"
                        description += "\n"+"   ▷ 상호 : 나상권공인중개사사무소  대표 : 나상권 "
                        description += "\n"+"   ▶ 등록번호 : 제41370-2015-00046호 "
                        description += "\n"+"   ▷ 소재지 : 오산시 궐동 640-9 성지빌딩 102호"
                        description += "\n"+"   ▶ 대표번호 : 031) 375 - 5555 "
                        description += "\n"
                        description += "\n"+"   오산에서방구하기 오방  https://osanbang.com/ "
                        description += "\n"+" ━━━━━━━━━━━━━━━━━━━━━━"
                        description += "\n"+""
                        description += "\n"+""
                        description += f"□■ 네이버 매물번호나 자체관리번호[ {object_code_new} ]를 알려주시면 신속한 상담이 가능합니다."
                        # description += f"□■ 의뢰인으로부터 전속중개요청 받은 물건으로 공동중개가능합니다."
                        description += "\n"
                        description += "\n"+"□■ 거래정보"
                        description += trading_memo
                        description += rent_memo
                        description += premium_memo
                        description += "" if ((R_memo + r_add_memo).strip()) == "□■ 호실정보" else (R_memo + r_add_memo)
                        description += "" if B_memo.strip() == "□■ 건물정보" else B_memo
                        description += "" if L_memo.strip() == "□■ 토지정보" else L_memo
                        description += "" if I_memo.strip() == "" else "\n\n□■ 주요특징\n"+I_memo
                        # pyautogui.alert(f">>{(R_memo + r_add_memo).strip()}<<\n>>{building_memo.strip()}<<\n>>{L_memo.strip()}<<")  
                        
                        # description += "\n"+" "
                        # description += "\n"+" □■ 위치"
                        # description += "\n"+"--"
                        # description += "\n"+"--"
                        # description += "\n"+"--"
                        # description += "\n"+" "
                        # description += "\n"+" □■ 특징"
                        # description += "\n"+"--"
                        description += "\n"+""
                        description += "\n"+""
                        description += "\n"+""
                        description += "\n"+""" "매물에 관한 자세한 상담을 원하시면 지금 바로 전화주세요!!" """   
                        description += "\n"+""
                        description += "\n"+""" "원하시는 매물을 찾을 때까지 끝까지 최선을 다하겠습니다." """   
                        description += "\n"+""
                        description += "\n"+""" "문의주시면 더 많은 비공개 매물까지도 안내받으실 수 있습니다." """   
                        description += "\n"+""
                        description += "\n"+""" "오산/화성/평택/용인 최대 빅데이터 보유!! 오산에서방구하기 오방!!" """   
                        description += "\n"+""
                        description += "\n"+""" "차별화된 중개시스템으로 원하는 매물을 쉽게!! 빠르게!! 정확하게!!" """   
                        # 태그별개수출력('상세정보')
                        
                        # 요소를 먼저 찾습니다.
                        상세정보요소 = 특정위치의x번째입력태그찾기('상세정보', 'textarea', 1)
                        # 1. 강제로 클릭하여 포커스를 줍니다.
                        상세정보요소.click() 
                        # 2. JS로 값을 빠르게 집어넣습니다.
                        driver.execute_script("arguments[0].value = arguments[1];", 상세정보요소, description)
                        # 3. [핵심] 프레임워크가 감지하도록 '의미 없는 키 입력'을 수행합니다.
                        # (스페이스바 입력 후 백스페이스로 지움 -> 데이터 변화 감지 트리거)
                        상세정보요소.send_keys(" ") 
                        상세정보요소.send_keys(Keys.BACK_SPACE)
                        # 4. 포커스 해제 (Blur 효과) - 다른 곳을 클릭하거나 blur JS 실행
                        # (보통 3번까지만 해도 저장되지만 확실하게 하기 위함)
                        driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", 상세정보요소)                        
                        # 상세정보script = """
                        # var textarea = arguments[0];
                        # var value = arguments[1];
                        # textarea.value = value;
                        # var event = new Event('input', { bubbles: true });
                        # textarea.dispatchEvent(event);
                        # """
                        # driver.execute_script(상세정보script, 특정위치의x번째입력태그찾기('상세정보', 'textarea', 1), description)
                        time.sleep(0.3)
                        # 상세설명 글자수제한 1000자
                        if len(description) > 1000: 
                            fail_msg += '\n- 상세설명 글자수1000자이상'
                            pyautogui.alert(f"상세설명 내용이 너무 깁니다. 글자수 {str(len(description))}자")
                        # 특정위치의x번째입력태그찾기('상세정보', 'textarea', 1).send_keys(description) #느림 description
                        print('매물상세정보 종료')
                        # pyautogui.alert("정상?")   

                        try:
                            # 1. 요소 찾기 (띄어쓰기 주의: '관리자 메모 (비공개 정보)' 인지 '관리자 메모(비공개 정보)'인지 사이트 실제 텍스트 확인 필요)
                            # 기존 코드의 텍스트를 그대로 사용합니다.
                            비공개메모요소 = 특정위치의x번째입력태그찾기('관리자 메모(비공개 정보)', 'textarea', 1) 
                            if not 비공개메모요소:
                                # 만약 못 찾았다면 띄어쓰기가 있는 버전으로 재시도 (사이트마다 다를 수 있음)
                                비공개메모요소 = 특정위치의x번째입력태그찾기('관리자 메모 (비공개 정보)', 'textarea', 1)
                            if 비공개메모요소:
                                # 2. 입력할 내용 생성
                                비공개메모내용 = '신규 ' + basic_secret + obinfo_content
                                # 3. 강제 클릭 (Focus)
                                비공개메모요소.click()
                                time.sleep(0.1)
                                # 4. JS로 값 넣기 (속도 빠름 & 특수문자 처리 용이)
                                driver.execute_script("arguments[0].value = arguments[1];", 비공개메모요소, 비공개메모내용)
                                # 5. [핵심] 키보드 입력 시늉을 내서 저장 트리거 발동 (Space -> Backspace)
                                비공개메모요소.send_keys(" ")
                                비공개메모요소.send_keys(Keys.BACK_SPACE)
                                # 6. 저장 확실시하기 (Blur 이벤트)
                                driver.execute_script("arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));", 비공개메모요소)
                                print(f"관리자 메모 추가 완료 (길이: {len(비공개메모내용)})")
                                time.sleep(0.3)
                            else:
                                print("❌ 비공개 메모 요소를 찾을 수 없어 입력을 건너뜁니다.")
                                fail_msg += '\n- 비공개 메모 입력 실패 (요소 못찾음)'

                        except Exception as e:
                            print(f"비공개 메모 입력 중 오류 발생: {e}")
                            fail_msg += f'\n- 비공개 메모 입력 에러: {e}'
                        # 비공개script = """
                        # var textarea = arguments[0];
                        # var value = arguments[1];
                        # textarea.value = value;
                        # var event = new Event('input', { bubbles: true });
                        # textarea.dispatchEvent(event);
                        # textarea.dispatchEvent(new Event('change', { bubbles: true }));
                        # textarea.blur();
                        # """
                        # driver.execute_script(비공개script, 특정위치의x번째입력태그찾기('관리자 메모(비공개 정보)', 'textarea', 1), '신규 '+basic_secret+obinfo_content)
                        time.sleep(0.3)
                        print("관리자 메모 추가, 내용:"+'신규 '+basic_secret+obinfo_content)
                        fail_msg = 검증방식선택및의뢰인정보입력(fail_msg) 
                        


















                    # 기등록 네이버매물번호 존재
                    else:
                        print(" 네이버종료일:",네이버종료일.strftime('%Y-%m-%d'))
                        #광고 종료일이 경과된 상태인지 확     
                        print("써브매물번호:"+써브매물번호)
                        # 종료일 경과 여부 확인
                        if 네이버종료일:
                            # # 종료일을 datetime 객체로 변환
                            # 종료일_date = datetime.strptime(네이버종료일, "%Y-%m-%d")
                            광고상태 = ""
                            if 네이버종료일 < 현재날짜:
                                광고상태 = "광고종료"
                                print("광고 종료일이 경과되었습니다. '등록종료리스트'로 이동")
                                driver.get('https://ma.serve.co.kr/good/articleRegistEndList')
                                # print("통합매물관리페이지로 이동:"+네이버매물번호) 
                                # 네이버매물번호입력요소 =  WebDriverWait(driver, 10).until(
                                #     EC.element_to_be_clickable(
                                #         (By.XPATH, '//*[@id="input-35"]')
                                #     )
                                # )  

                                # 관리자메모입력요소 = 특정위치의x번째입력태그찾기('소유자정보/관리자메모', 'text', 1)
                                # 관리자메모입력요소.send_keys(object_code_new)    
                                # 관리자메모입력요소.send_keys(Keys.ENTER)      
                            else:
                                광고상태 = "광고중"
                                print("광고가 아직 유효합니다. '등록리스트'로 이동")
                                driver.get('https://ma.serve.co.kr/good/articleRegistList')
                            print("네이버매물번호 입력요소 찾기")
                            네이버매물번호입력요소 =  WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable(
                                    (By.XPATH, '//*[@placeholder="매물번호를 입력해 주세요"]')
                                )
                            )
                            time.sleep(0.1)
                            네이버매물번호입력요소.send_keys(네이버매물번호)    
                            print("네이버매물번호 입력")
                            time.sleep(0.1)
                            네이버매물번호입력요소.send_keys(Keys.ENTER)                                      

                        else:
                            print("광고 종료일이 설정되지 않았습니다.")   
                            # driver.get('https://ma.serve.co.kr/good/articleRegistList')
                        time.sleep(3)

                        try:
                            # span 태그를 찾고 값이 '1'일 때까지 대기
                            element = WebDriverWait(driver, 13).until(
                                lambda d: d.find_element(By.XPATH, '//div[@class="t-position-group"]//div[@class="total-area"]/span').text == "1"
                            )
                            검색결과건수 = 1
                            print("span 태그의 값이 1입니다.")
                            # pyautogui.alert("span 태그의 값이 1입니다.")
                        except Exception:
                            # 10초 안에 값이 1이 되지 않았을 경우
                            try:
                                # span 태그의 현재 값 가져오기
                                검색결과요소 = driver.find_element(By.XPATH, '//div[@class="t-position-group"]//div[@class="total-area"]/span')
                                검색결과건수 = 검색결과요소.text
                                # 알림창으로 값 표시
                                최상단알림창(f"span 태그의 값이 10초 안에 1이 되지 않았습니다. 현재 값: {검색결과건수}", "알림")
                            except Exception as e:
                                최상단알림창(f"span 태그를 찾을 수 없습니다. 오류: {e}", "오류")        
                        
                        if 검색결과건수 == 1:
                            print("검색결과건수가 1입니다!")
                            if 광고상태 == '광고중':

                                try:
                                    # 진행상태가 '등록(서비스중)' 상태인지 확인하여 맞으면 '전송 상세보기'클릭, 틀리면 '재전송(검증) 신청'클릭 시도
                                    # 첫 번째 span에서 '등록' 텍스트가 있는지 바로 확인
                                    등록상태 = WebDriverWait(driver, 10).until(
                                        EC.presence_of_element_located(
                                            (By.XPATH, '//div[@id="printArea"]//tbody//td[6]//div[1]//span[1]')
                                        )
                                    )
                                    등록상태_text = 등록상태.text
                                    print("등록상태_text:"+등록상태_text)
                                    # pyautogui.alert(""등록상태_text:"+등록상태_text)
                                    if 등록상태_text == '등록': 
                                        # '전송 상세보기' 버튼 클릭 시도
                                        전송상세보기_버튼 = WebDriverWait(driver, 10).until(
                                            EC.element_to_be_clickable(
                                                (By.XPATH, '//div[@id="printArea"]//div[contains(@class, "t-btn-item")]//button[.//span[normalize-space(.)="전송 상세보기"]]')
                                            )
                                        )
                                        전송상세보기_버튼.click()  
                                        등록된매물번호추출(ad_naver_list)
                                        return;   
                                    else:
                                        # '재전송(검증) 신청' 버튼 클릭 시도
                                        재전송신청_버튼 = WebDriverWait(driver, 10).until(
                                            EC.element_to_be_clickable(
                                                (By.XPATH, '//div[@id="printArea"]//div[contains(@class, "t-btn-item")]//button[.//span[normalize-space(.)="재전송(검증) 신청"]]')
                                            )
                                        )
                                        재전송신청_버튼.click() 
                                    print("버튼 클릭 성공!")
                                except Exception as e:
                                    print(f"등록상태 확인실패 오류 발생: {e}") 
                                    최상단알림창(
                                        f"⚠️ 매물 상태 확인 실패\n\n"
                                        f"이미 등록된 매물이거나 매물 상태를 가져올 수 없습니다.\n"
                                        f"중복 등록 방지를 위해 프로그램을 종료합니다.", 
                                        "알림"
                                    )
                                    try:
                                        driver.quit()
                                    except:
                                        pass
                                    self.finished.emit(False)
                                    return # 스레드 및 함수 안전 종료                   
                                # driver.find_element(By.XPATH, f'//*[@id="printArea"]/div/table/tbody/tr/td[7]/div/div[2]/button').click() 
                                time.sleep(2)
                                다시보지않기확인()  
                            elif 광고상태 == '광고실패':
                                driver.find_element(By.XPATH, f'//*[@id="printArea"]/div/table/tbody/tr/td[4]/div[2]/div[1]/button').click() 
                                time.sleep(2)
                                다시보지않기확인()  
                                fail_msg = 검증방식선택및의뢰인정보입력(fail_msg)    
                            elif 광고상태 == '광고종료':
                                driver.find_element(By.XPATH, f'//*[@id="printArea"]/div/table/tbody/tr/td[4]/div[2]/div[1]/button').click() 
                                time.sleep(2)
                                다시보지않기확인()  
                                fail_msg = 검증방식선택및의뢰인정보입력(fail_msg)    

                        elif 검색결과건수 == 0:
                            print("검색결과건수가 0입니다!")
                            # pyautogui.alert("등록된 정보가 없습니다.")
                            driver.quit()
                            print("작동 종료")
                            return errarr
                                        
                        else:
                            print(f"예상치 못한 검색결과건수 값: {검색결과건수}")
                            
            #공통
                    

                #약관동의
                    약관동의체크()
                
                    #물건사진 폴더열기
                    main_dir = 'Z:\\업무자료\\4사진자료&이미지자료(외부유출금지)\\1주거용물건, 상업용물건\\'
                    path_dir = main_dir + self.data['folderPath'] #'경기도\\오산시\\궐동\\654-9\\썬플라워\\1층\\1층'
                    print(path_dir)
                    try:
                        os.startfile(path_dir)
                        print('폴더열기 성공') 
                    except:
                        print('폴더열기 에러(해당폴더 없음)')         

                    print("확인메세지 표시전 ad_naver_list:",ad_naver_list)
                    if not self.wait_for_confirmation("상세주소값: "+상세주소값+"\n"+address_info+"\n"+fail_msg+"\n\n매물번호를 추출하여 저장합니다.\n\n수정내용 저장후\n써브/네이버/KB부동산 매물번호가 보이는 페이지에서\n'확인'버튼을 눌러주세요"):
                        self.finished.emit(False)
                        return
                    # pyautogui.alert(address_info+"\n"+fail_msg+"\n\n매물번호를 추출하여 저장합니다.\n\n수정내용 저장후\n써브/네이버/KB부동산 매물번호가 보이는 페이지에서\n'확인'버튼을 눌러주세요", "[네이버부동산]")
                    print("확인메세지 표시후")

                    등록된매물번호추출(ad_naver_list)

            except Exception as e:
                print(f"등록중 오류:{e}")
                # [2026-09-05 추가 — 사용자 요청] 예상 못 한 예외를 개발자용 오류로그에도 남긴다
                # (아래 바깥쪽 catch-all 주석 참고). 이 try는 webdriver 생성부터 등록 완료까지를
                # 통째로 감싸고 있어, 크롬드라이버 확보 실패도 여기로 떨어진다.
                self.report_unexpected_exception(e, '네이버 등록 진행 중')
                pyautogui.alert(f"오류 발생: {e}", "오류")  
            finally:
                # [2026-09-05 수정] webdriver.Chrome() 자체가 실패하면(크롬 버전에 맞는 chromedriver를
                # 못 받아오는 경우 등) driver가 아예 만들어지지 않는데, 그때도 무조건 close()를
                # 부르는 바람에 "driver 참조 불가" 2차 예외가 나서 진짜 원인 위에 덮여쓰였다
                # (2026-09-05 매물 920585 사례). driver가 실제로 만들어졌을 때만 닫는다.
                if 'driver' in locals():
                    driver.close() 
        except Exception as e:
            print(f"[❌예외] 네이버 매물 등록 중 오류 발생: {e}")
            # [2026-09-05 추가] 아래 alert는 headless일 때 화면 대신 headless_notes(→ 담당자가 보는
            # 연장등록 이력 pr_log)에만 남는다 — 개발자용 오류로그(pr_error_log)에도 남겨야 원인 진단이
            # 된다. 여기와 위의 등록 catch-all 두 곳에만 넣는다: 나머지 except 16곳은 "등록버튼 클릭
            # 실패"처럼 이미 알려진 개별 단계 실패라, 그것들로 오류로그가 덮이면 정작 예상 못 한
            # 오류를 못 찾는다.
            self.report_unexpected_exception(e, '연장등록 실행 중(최상위)')
            pyautogui.alert(str(e), "에러 발생")
            self.finished.emit(False)            






        # # finally:
        # #     pyautogui.alert(address_info+"\n"+fail_msg+"\n\n매물등록창을 닫으시겠습니까?", "[네이버부동산]")
        # # driver.quit()
        # driver.close()
        # # return errarr   
        
    def wait_for_confirmation(self, message):
        """
        확인 메시지를 띄우고 사용자 응답을 대기합니다.
        :param message: 사용자에게 표시할 메시지
        :return: 작업을 계속할지 여부 (True: 계속, False: 중단)
        """
        QThread.sleep(1)  # 작업 시뮬레이션 (필요시 제거)
        self.ask_confirmation.emit(message)  # 메인 스레드에 확인 요청
        self.exec_()  # 사용자 응답 대기
        return self.continue_work
    
    def send_response(self, response):
        self.continue_work = response  # 응답 결과 저장
        self.quit()  # 이벤트 루프 종료


# # ChromeDriver 경로 설정
# driver = webdriver.Chrome('/chromedriver')
def objectCheckTime():
    import sys
    from PyQt5.QtWidgets import QApplication, QMessageBox
    app = QApplication(sys.argv)

    # 메시지 창 생성
    msgBox = QMessageBox()
    msgBox.setText("매물종류를 선택해주세요~5초후 작업이 시작됩니다.")
    msgBox.setStandardButtons(QMessageBox.Ok)
    msgBox.setWindowModality(2)  # 모달 창으로 설정 (다른 작업을 막음)
    msgBox.show()

    sys.exit(app.exec_())

from bs4 import BeautifulSoup  
def remove_html_and_entities(text):
    soup = BeautifulSoup(text, 'html.parser')
    return soup.get_text()

















# ☺ 카톡아이디 : cjwcan
# -------------------------------
# ♣ 추천매물

# ◈강남 무권리 매장
# 1.역삼역대(실75평) 보증금2억/월1000만/관200만
#   역삼역대로변 특A급매장
# 2.강남구청역(실62평) 보증금1억5천/월990만/관90만
#    대로변 코너건물
# 3.역삼동(실45평) 보증금5천/월400만/관50만
#    코너건물

# ◈강남상권 카페(강남역메인상권)
# 1. (실20평)보증금5천/월400만/관50만/권리금5천(협의가능)/합1억

# ◈강남상권 음식점
# 1. (실17평) 보증금7천 / 월350만 / 관15만 / 권리금4천 / 합1억천만
# 2. (실9평) 보증금3천 / 월180만/권리금7백/ 합3천7백만

# -------------------------------------------------------

# ✿매물소개

# ✦ 위치 : 강남구 논현동 먹자라인

# ✦ 임대면적 : 실34평

# ✦ 해당층 : 3층

# ✦ 임대내역 : 보증금 3천 / 월세 310만  / 관리비30만

# ✦ 권리금 : 최저가로 진행중 - 전화문의

# ✦ 기타 : 1인룸4개 / 2인룸2개 /샤워실 및 대기실등 인테리어 A급유지


# ✪ 매물특징

# √ 논현동 먹자라인에 위치 입지가 좋아 고객 유치하기 좋음

# √ 인테리어 모던한 스타일로 깔끔하게 유지중

# √ 권리금 강남에서 최저가로 진행중이니 24시간 언제든 연락주세요

# ---------------------------------

# ☺ 고객님이 필요한 매물을 최단시간내 A급으로 찾아드리겠습니다


# ☎ 대표번호 : 02-554-4550

# description += "\n"+"-- 🔴 임차 전속 물건 입니다 / 전화주시면 공동중개 가능합니다.🔴"

# description += "\n"+"-- 1️⃣ 층 수 : 3층 (총 5층 건물)"
# description += "\n"+"-- 2️⃣ 면 적 : 약 40평"
# description += "\n"+"-- 3️⃣ 주 차 : 1대 제공"
# description += "\n"+"-- 4️⃣ 보 증 금 : 3,000만원"
# description += "\n"+"-- 5️⃣ 임 대 료 : 360만원 / 관리비 : 실비정산"
# description += "\n"+"-- 6️⃣ 입주시기 : 항시 가능"
# description += "\n"+"-- 7️⃣ 권 리 금 : 적정한 인테리어 비용 있습니다! 자세한 사항은 부동산으로 연락 부탁 드립니다. "

# description += "\n"+"--  💥 매물 참고 사항 💥"
# description += "\n"+"-- 🔴 학동역 도보 4분 거리 위치"
# description += "\n"+"-- 🟠 직사각형 구조로 활용성 좋음"
# description += "\n"+"-- 🟡 역세권 인접하여 접근성 용이"
# description += "\n"+"-- 🟢 인근 거리 편의점 대형 마트 인접 "
# description += "\n"+"-- 🔵 좋은 위치로 인해 다양한 활용 가능"
# description += "\n"+"-- 🟣 확장성 높은 매물"

# -------------📝직접 눈으로 본 매물정보📝--------------
# ☑️️ 논현동 인테리어 및 시설 갖춘 다이닝

# ☑️️ 전용평수 :　44평

# ☑️️ 메인 업무 홀 + 룸1 + 창고1 + 주방 구조

# ☑️ 소방시설 + 대형 냉난방 + 환기시설 완비

# ☑️ 권리금 : 협의

# ☑️ 고급 다이닝 적극 추천

# ☑️ 무료 주차 1대

# 🚨🚨 날짜, 금액, 렌트프리 조율 해드립니다 🚨🚨
# 🚨🚨 위치, 조건 등에 맞춰 성심껏 찾아드립니다 🚨🚨


# ■ 수(秀)부동산중개법인은 실사진 실매물 광고가 원칙입니다.
# ■ 사진으로만 판단하시기보다 사무실의 컨디션을 직접 눈으로 확인하시는게 좋습니다.
# ■ 고객님께서 마음에 드신다면 보증금,임대료,입주시기 최대한 협의 봐드립니다.


# 🟧 리얼리부동산은?

# 다양한 분야의 책임있는 전문가가 모인 중개사무소 입니다.
# 저희는 협력하고, 공유합니다. 좋은매물소개와 좋은손님소개 하는것에 집중합니다.

# ✅ 고객이 원하는것에 집중합니다.
# 1) 빠르고 정확한 정보를 전달 합니다.
# 2) 구성원 모두가 신속하고 빠릿하게 움직입니다.
# 3) 계약보다는 안전에 우선합니다.

# ✅ 물건접수
# 1) 매물 광고를 아끼지 않습니다.(퀄리티 있는 광고를 지향합니다.)
# 2) 고객이 원할시 보안으로 진행 됩니다.(사내+중개사협력망)

# 📍 물건데이터 多 / 손님데이터 多
# 📍 분양, 분양대행, 건물(호실) 관리

# ❌본 광고 형식은 시작부동산의 창작물로써 무단 사용 금지합니다❌

# ❌임차인 전속(친척입니다) / 오토 운영으로 찾아가셔도 제 번호 알려줍니다❌
# ❌네이버 광고 금지(신고합니다)❌

# 📌 매물정보 📌  
# ✅【 금 액 】 : 보증금 3억원 / 월세 1,100만원(관리비 포함)
# ✅【 권 리 】 : 유선문의 
# ✅【 면 적 】 : 1층(약 20평) + 2층(약 80평)
# ✅【 층 수 】 : 1층 일부 + 2층 전체

# 📌상세정보 📌
# ✅【 위   치 】 : 언주역 도보1분, 차병원사거리 코너 위치
# ✅【 주   차 】 : 협의
# ✅【 입주일 】 : 협의
# ✅【 현업종 】 : 카페
# ✅【 화장실 】 : 외부 남녀 분리 화장실 
# ✅【 간   판 】 : 가능(세부사항 협의) 
# ✅【 냉난방기 】 : 천장형 에어컨
# ✅【 특   징 】 : 
# ➡카페 최적화, 2층 외부 통유리
# ➡내부 연결 계단
# ➡넓은 간판 사용 가능
# ➡이전 업종 투썸플레이스로 10년 넘게 운영
# ➡면적대비 합리적인 임대료
# ➡업종 문의 언제든지 연락 주세요
# ➡렌트프리/금액/세부사항 조율 최대한 신경써드리겠습니다

# 📌시작부동산만의 장점 📌
# 👍【 조율 】 - 렌트프리 / 금액 / 세부사항 / 조건  적극적 협의
# 👍【 순발력 】 빠르고 신속한 응대
# 👍【 젊음 】 - 넘치는 에너지의 기동력
# 👍【 센스 】 - 원스톱 브리핑 및 투어 후 매물 요점 자료 안내
# 👍【 정직 】 - 거짓 없이 정확하고 확실한 정보 전달
# 👍【 신뢰 】 - 계약 후에도 지속적인 관리
# 👍【 픽업 서비스 】
