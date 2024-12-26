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
import re
import os
import pymysql
from datetime import datetime, timedelta

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

    def run(self): #run 함수는 QThread 클래스의 핵심 메서드로, 스레드가 시작될 때 즉,start()를 호출하면 자동으로 실행
        print("네이버 매물 등록 작업 시작")
#함수설정     
        def 그룹별명칭변환(그룹, 대상명칭):
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
                    "벽걸이에어컨": ["에어컨"],
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
                }
            elif 그룹 == '매물분류2차':
                변환사전 = {
                    "단독": ["단독주택"],
                }

            # 대상명칭이 변환 사전의 값 리스트에 포함되는지 확인
            for 변환된명칭, 명칭리스트 in 변환사전.items():
                if 대상명칭 in 명칭리스트:
                    return 변환된명칭

            # 매핑되지 않으면 원래 값을 반환
            return 대상명칭
   
        # def 그룹별명칭변환(그룹, 대상명칭):
        #     # 변환 매핑
        #     변환사전 = {}
        #     if 그룹 == '건축물용도':
        #         변환사전 = {
        #             "다가구주택": "단독주택",
        #             "단독주택외": "단독주택",
        #             "근린생활시설": "제1종 근린생활시설",
        #             "소매점": "제1종 근린생활시설",
        #             "제1종근린생활시설": "제1종 근린생활시설",
        #             "제2종근린생활시설": "제2종 근린생활시설",
        #             "노유자시설": "노유자(老幼者: 노인 및 어린이)시설",
        #             "여관": "위락시설",
        #             "교정군사시설": "교정(矯正) 및 군사 시설",
        #             "자동차관련시설": "자동차 관련 시설",
        #             "다세대주택": "공동주택",
        #             "제조업소": "공장",
        #             # 추가 매핑
        #         }
        #     elif 그룹 == '시설정보':
        #         변환사전 = {
        #             "공터": "마당",
        #             "에어컨": "벽걸이에어컨",
        #             "가스렌지": "가스레인지",
        #             "인덕션": "인덕션레인지",
        #             "전자렌지": "전자레인지",
        #             # "에어컨": "에어컨",
        #             # 추가 매핑
        #         }
        #     elif 그룹 == '관리비포함내역':
        #         변환사전 = {
        #             "공용전기": "공용관리비",
        #             "공용수도": "기타관리비",
        #             "개별전기": "전기료",
        #             "개별수도": "수도료",
        #             "TV": "TV사용료",
        #             # 추가 매핑
        #         }
        #     elif 그룹 == '주용도':
        #         변환사전 = {
        #             "상가점포": "상가전용",
        #             "사무실": "사무실전용",
        #             # 추가 매핑
        #         }
        #     elif 그룹 == '지역(시/도)':
        #         변환사전 = {
        #             "전라북도": "전북특별자치도",
        #             # 추가 매핑
        #         }
        #     elif 그룹 == '전문분야':
        #         변환사전 = {
        #             "주거용": "원/투룸",
        #             "상업용": "상가/사무실",
        #             "공업용": "공장/창고",
        #             # 추가 매핑
        #         }
        #     elif 그룹 == '방특징':
        #         변환사전 = {
        #             "중로접": "큰길가",
        #             "대로접": "큰길가",
        #             # 추가 매핑
        #         }
        #     elif 그룹 == '건축구조':
        #         변환사전 = {
        #             "일반철골구조": "철골조",
        #             # 추가 매핑
        #         }
        #     elif 그룹 == '매물분류2차':
        #         변환사전 = {
        #             "단독주택": "단독",
        #             # 추가 매핑
        #         }

        #     # 매핑된 값 반환, 매핑되지 않았으면 원래 값을 반환
        #     return 변환사전.get(대상명칭, 대상명칭)
        
        def 목록_변환(그룹, 항목들):
            변환된_항목들 = []
            for 항목 in 항목들.split(','):
                변환된_항목들.append(그룹별명칭변환(그룹, 항목.strip()))
            return ','.join(변환된_항목들)    

        def 제곱미터_평_변환(제곱미터):
            평 = float(제곱미터) / 3.3058
            return str(round(평, 1))  # 소수점 둘째 자리까지 반올림

        def 한글금액(금액):
            단위 = ["만원", "억", "조"]
            단위_금액 = []
            i = 0
            if 금액.isdigit():
                금액 = int(금액)
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
                return 결과 if 결과 else "0만원"  # 결과가 비어있으면 "0만원" 반환
        
        def 다시보지않기확인():
            try:
                # "다시 보지 않기" 텍스트가 있는 요소가 나타날 때까지 대기
                다시보지않기_요소 = WebDriverWait(driver, 1).until(
                    EC.presence_of_element_located((By.XPATH, '//*[text()="다시 보지 않기"]'))
                )
                
                # 요소가 화면에 보이는지 확인
                if 다시보지않기_요소.is_displayed():
                    다시보지않기_요소.click()
                    print("알림: '다시 보지 않기' 텍스트가 화면에 표시되었습니다.")
                    # pyautogui.alert("알림: '다시 보지 않기' 텍스트가 화면에 표시되었습니다.")
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
                print(f"'{strong태그의텍스트}' 텍스트를 가진 strong 태그의 개수: {len(strong_elements)}")
                
                # 각 strong 태그의 부모 tr 요소 찾기
                for strong in strong_elements:
                    # HTML에서 텍스트 추출 후 모든 공백 및 줄바꿈 제거
                    strong_text = strong.get_attribute('textContent').replace('\n', '').replace('\r', '').replace(' ', '')
                    print(f"공백과 줄바꿈을 제거한 strong_text vs 요청strong_text: {strong_text} vs {요청strong_text}")
                    # print(f"찾은 {strong.text} strong요소: {strong.get_attribute('outerHTML')}")
                    # strong 태그의 상위 th 태그를 거쳐 상위 tr 태그 찾기
                    # tr_element = strong.find_element(By.XPATH, './ancestor::tr')
                    # print(f"찾은 {strong.text} tr요소: {tr_element.get_attribute('outerHTML')}")
                    # return tr_element

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
                                elements = td.find_elements(By.XPATH, f'./div/div/div/div[3]/{tag_name}')
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
                                # print(f"{몇번째}번째 보이는 {tag_name} 태그를 찾았습니다.")
                                return v_elem
                        break

                print(f"{몇번째}번째 보이는 {tag_name} 태그를 찾을 수 없습니다.")
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
                                # print("target_div 클릭완료!!")
                                # 선택된 div 내부에서 선택할 항목에 해당하는 요소를 찾아 클릭                   
                                # time.sleep(1)
                                선택항목요소 = WebDriverWait(driver, 10).until(
                                    EC.element_to_be_clickable((By.XPATH, f"//div[@class='v-overlay-container']//div[contains(text(), '{선택할항목}')]"))
                                    # EC.element_to_be_clickable((By.XPATH, f"//div[@class='v-overlay-container']//div[text()='{선택할항목}']"))
                                )
                                # print(f"Found target_div태그: {선택항목요소.get_attribute('outerHTML')}")
                                if 선택항목요소:
                                    선택항목요소.click()
                                    time.sleep(0.5)
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

        def 홍보확인서선택및의뢰인정보입력(fail_msg):   
            print("홍보확인서선택및의뢰인정보입력() 시작")
            소유자명 = ''
            소유자연락처 = ''        
            소유자유형 = '본인'  
            선택할검증방식 = '홍보확인서 확인'
            print("등기부확인여부:"+등기부확인여부+" 등록된 소유자수:"+str(len(등록된소유자들_arr)))
            if 등기부확인여부=='Y' and len(등록된소유자들_arr) > 0: #등기확인된 소유주
                print("등록된소유자들:",등록된소유자들)
                print("master_info:",master_info)
                if master_info and 'master_name' in master_info: #본인 또는 대표인 접촉자정보존재
                    print("1")
                    if master_info['master_name'] in 등록된소유자들 and master_info['master_type'] == '본인': #소유주정보에 등기확인된 소유주 존재
                        print("3")
                        소유자명 = master_info['master_name'] if '이름미확인' not in master_info['master_name'] else ''
                    elif master_info['master_name'] not in 등록된소유자들:
                        print("5")
                        
                        if len(등록된소유자들_arr) == 1 :
                            소유자명 = 등록된소유자들 
                            if master_info['master_type'] == '대표':
                                소유자유형 = master_info['master_type']
                            else:
                                소유자유형 = '직원'
                        else :
                            등록된소유자들_arr[0]
                            소유자유형 = master_info[0]['master_type']

                    else:
                        pyautogui.alert(f"- 등기부상 소유자:  {등록된소유자들}\n\n- 의뢰인:  {master_info['master_name']} ({master_info['master_type']})", "※소유자정보 불일치")
                    소유자연락처 = master_info['master_phone1']
                    소유자유형 = master_info['master_type']
                    소유자통신사 = master_info['telecom']
                    fail_msg += "\n- 휴대폰통신사 미확인" if 소유자통신사 == '미확인' else ''
                    print(f"소유자:{소유자명}\n연락처(통신사:{소유자통신사}):{소유자연락처}")
                    if 소유자연락처 and 소유자통신사 != '미확인':
                        선택할검증방식 = '모바일확인V2 (집주인)'
                else:
                    소유자명 = 등록된소유자들 
                    소유자유형 = '대리인'
            else:
                fail_msg += '\n- 소유자이름 입력 실패'
            # pyautogui.alert("소유자명:"+소유자명)
            #검증방식  
            try:
                적용대상h2 = driver.find_elements(By.XPATH, f'//h2[@class="t-h2"]')
                print(f"'t-h2'의 class를 가진 h2 태그의 개수: {len(적용대상h2)}")
                # 적용대상h2 = driver.find_elements(By.XPATH, f'//h2[contains(text(), "검증방식")]')
                # print(f"'검증방식' 텍스트를 가진 h2 태그의 개수: {len(적용대상h2)}")
                
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
                #네이버등록권
                특정위치의x번째입력태그찾기('네이버 등록권', 'radio', 1).click()
                # pyautogui.alert("정상?")
            except:
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
                특정위치의x번째입력태그찾기('의뢰인과 등기부상 소유자와의 관계', 'text', 1).send_keys(소유자유형) 
                특정위치의x번째입력태그찾기('소유자 연락처 (홍보확인서2)', 'radio', 2).click()
                # pyautogui.alert("정상?")   
                연락처입력대상stong_text = '소유자 연락처 (홍보확인서2)'      
            elif 선택할검증방식 == '모바일확인V2 (집주인)':
                if master_info['master_gender']: 
                    print(f"소유자성별:{master_info['master_gender']}")
                    # pyautogui.alert(f"소유자성별:{master_info['master_gender']}")
                    선택할성별위치 = 1 if master_info['master_gender'] == '남성' else 2
                    특정위치의x번째입력태그찾기('등기부상 소유자 성별', 'radio', 선택할성별위치).click()
                if master_info['telecom']:
                    if master_info['telecom'] == 'SKT': 선택할통신사위치 = 1
                    if master_info['telecom'] == 'KT': 선택할통신사위치 = 2
                    if master_info['telecom'] == 'LGU+': 선택할통신사위치 = 3
                    if master_info['telecom'] == '알)SKT': 선택할통신사위치 = 4
                    if master_info['telecom'] == '알)KT': 선택할통신사위치 = 5
                    if master_info['telecom'] == '알)LGU+': 선택할통신사위치 = 6
                    연락처입력대상stong_text = '등기부상 소유자 휴대폰번호'     
                    특정위치의x번째입력태그찾기('등기부상 소유자 휴대폰번호', 'radio', 선택할통신사위치).click() 
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
#변수설정
        print("=== 변수 설정")
        # 현재 날짜와 시간 가져오기
        현재날짜시간 = datetime.now()
        현재날짜 = 현재날짜시간.date()
        # 문자형으로 변환
        current_date = 현재날짜시간.strftime("%Y-%m-%d")  # 'YYYY-MM-DD' 형식
        current_time = 현재날짜시간.strftime("%H:%M:%S")  # 'HH:MM:SS' 형식    
        # current_date = datetime.date.today()
        # formatted_date = current_date.strftime("%Y-%m-%d")
        
        admin_id = self.data['adminData']['ad_id']
        admin_name = self.data['adminData']['admin_name']
        # naver_id = self.data['adminData']['naver_id']
        # naver_pw = self.data['adminData']['naver_pw']
        naver_id = "osanbang6666"
        naver_pw = "dhqkd5555%"
        
        errarr = []
        fail_msg = ''

        client_code = self.data['clientData']['client_code']
        master_data = self.data['masterData']['master_data']
        print("client_code:"+client_code)
        print("master_data:",master_data)
        master_keys_list = list(master_data.keys())
        master_info = None  # 초기화
        # 리스트에 요소가 있는지 확인하고 첫 번째 요소에 접근합니다.
        # 조건에 따라 데이터를 필터링하고 첫 번째 항목 선택
        if master_keys_list:  # 키가 비어있지 않은 경우
            print("master_keys_list:", master_keys_list)
            
            # '본인' 또는 '대표'이고 'master_phone1'이 있는 데이터 탐색
            for key in master_keys_list:
                data = master_data[key]
                if (data.get('master_type') in ['본인', '대표']) and data.get('master_phone1'):
                    master_info = data
                    break

            # 조건에 맞는 데이터가 없는 경우 최근의뢰인의 데이터를 탐색
            if master_info is None:
                for key in master_keys_list:
                    if key == client_code:
                        master_info = master_data[key]
                        break

            # 최종 master_info 출력
            if master_info:
                print("Selected master_info:", master_info)
            else:
                print("No matching data found.")
        else:
            # 키 리스트가 비어있는 경우 처리
            print("master_keys_list: No data available")
            
        # pyautogui.alert("소유자 목록확인")
        등록된소유자들 = self.data['writeData']['master_name']
        등록된소유자들_arr = []
        등록된소유자들_arr = 등록된소유자들.split(',')
        if len(등록된소유자들_arr) > 0:
            master_name = 등록된소유자들_arr[0]
        else:
            master_name = ''
        등기부확인여부 = self.data['writeData']['master_check']
        
        client_name = self.data['clientData']['client_name']
        client_phone1 = self.data['clientData']['client_phone1']
        # client_gender = self.data['clientData']['client_gender']
        client_phone = f"{client_phone1[:3]}-{client_phone1[3:7]}-{client_phone1[7:]}"
        client_info = client_name + ' ' + client_phone
        # client_telecom = self.data['clientData']['telecom']
        
        tr_target = self.data['writeData']['tr_target']
        tr_range = self.data['writeData']['tr_range']
        representing_purpose = self.data['landData'][0]['representing_purpose']
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
        
        request_code = self.data['writeData']['request_code'] #의뢰번호
        object_code_new = self.data['writeData']['object_code_new'] #새홈매물번호
        obang_code = self.data['writeData']['obang_code'] #오방매물번호
        optionImportant = ''
        object_type = self.data['writeData']['object_type']
        obinfo_type = ''
        obinfo_type1 = self.data['writeData']['object_type1']
        obinfo_type2 = self.data['writeData']['object_type2']
        if obinfo_type1 == '상가건물':
            obinfo_type1 = '빌딩건물'
            if obinfo_type2 == '상업용건물':
                obinfo_type2 = '상가건물'

        # if self.data['writeData']['object_type'] == '주거용' and tr_target == '층호수':
        #     if self.data['roomData']['room_rcount'] == '1':
        #         obinfo_type = '원룸'
        #     elif self.data['roomData']['room_rcount'] >= '2':
        #         obinfo_type = '투룸/쓰리룸+'
        # elif self.data['writeData']['object_type'] == '상업용':
        #     obinfo_type = '상가/사무실'
        obinfo_trading = self.data['writeData']['trading'] #매매금액    
        obinfo_deposit1 = self.data['writeData']['deposit1'] #보증금1
        obinfo_deposit2 = self.data['writeData']['deposit2'] #보증금2
        obinfo_deposit3 = self.data['writeData']['deposit3'] #보증금3
        obinfo_rent1 = self.data['writeData']['rent1'] #월세1
        obinfo_rent2 = self.data['writeData']['rent2'] #월세2
        obinfo_rent3 = self.data['writeData']['rent3'] #월세3
        obinfo_ttype = self.data['writeData']['object_ttype'] #거래종류
        obinfo_title = self.data['writeData']['object_title'] #매물제목
        obinfo_content = remove_html_and_entities(self.data['writeData']['object_content']) #매물설명

        premium = self.data['writeData']['premium']
        premium_exist = self.data['writeData']['premium_exist']
        premium_content = self.data['writeData']['premium_content']
        basic_manager = self.data['writeData']['manager'] #관리비 별도/포함/미확인
        basic_mmoney = '' if self.data['writeData']['mmoney']=='' else float(self.data['writeData']['mmoney'])*10000 #관리비
        basic_mlist = self.data['writeData']['mlist'] #관리비포함내역
        # 관리비항목들 = 그룹별명칭변환('관리비포함내역', basic_mlist)
        관리비항목들 = 목록_변환('관리비포함내역', basic_mlist)
        basic_mmemo = self.data['writeData']['mmemo'] #관리비메모
        add_warmer = '' #data['writeData']['add_warmer'] 난방
        add_rdate = str(self.data['writeData']['rdate']) #입주일
        secret_1 = '' if self.data['writeData']['tr_memo'] == '' else self.data['writeData']['tr_memo'] + "\n"
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
            location_detail += ' 제'+basic_floor+'층'
            #집합건물일 경우 호실명 추가, 일반건물이면 '일부' 추가
            if building_type == '집합':
                location_detail += location_room
            else:
                location_detail += ' 일부'
            room_important = self.data['roomData']['room_important'] #호실특징
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
        if tr_target == '층호수':
            I_memo += ("\n"+room_memo) if (I_memo != '' and room_memo) else room_memo
        if tr_target == '건물' or tr_target == '층호수':
            I_memo += ("\n"+building_memo) if (I_memo != '' and building_memo) else building_memo
        I_memo += ("\n"+land_memo) if (I_memo != '' and land_memo) else land_memo
        premium_memo = ''
        r_add_memo = ''
        # pyautogui.alert("I_memo:\n"+I_memo)
#webdriver 열기
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
                "나상권공인중개사사무소"
            )
        )
        # 로그인확인겸 첫 파란등록버튼 기다리기(관리자로 로그인시)
        driver.implicitly_wait(10)





        # 기등록 네이버매물번호가 존재여부확인
        네이버매물번호 = self.data.get('adData', {}).get('네이버', {}).get('ad_code', '')  # 키가 존재하지 않을 경우 기본값 반환
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
                print(f"라벨 클릭 중 오류 발생: {e}")
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
                # pyautogui.alert("매물분류1차:"+매물분류1차+"\n"+"매물분류2차:"+매물분류2차)
                obinfo_type1 = 매물분류1차
                obinfo_type2 = 매물분류2차
            else:
                try:
                    #소분류
                    특정위치X번째셀렉트에서선택('매물 분류', 1, obinfo_type1)
                    # 다시보지않기확인()  
                    if obinfo_type1 == '상가점포': 다시보지않기확인()
                    #대분류 
                    특정위치X번째셀렉트에서선택('매물 분류', 2, 그룹별명칭변환('매물분류2차', obinfo_type2))
                    # pyautogui.alert(f"{obinfo_type1} {obinfo_type2} 클릭 완료!")
                    
                except Exception as e:
                    print(f"An error occurred: {e}")
                    pyautogui.alert("요소를 찾을 수 없습니다.")        
        
            # pyautogui.alert("테스트중입니다.") 
            #거래종류 obinfo_ttype 
            if ',' in obinfo_ttype: #쉼표가 있다면 쉼표로 분리후 첫번째 항목을 값으로 지정
                obinfo_ttype = obinfo_ttype.split(',')[0]
            라디오버튼선택('거래 종류', obinfo_ttype)  


            # 특정위치X번째셀렉트에서선택('건축물용도', 1, 그룹별명칭변환('건축물용도', '제2종 근린생활시설'))
            # pyautogui.alert("테스트중입니다.") 
        #매물소재지
            print(location_do, location_si, location_dong, location_li, jibun)
            리입력칸수 = 1
            #소재지
            특정위치X번째셀렉트에서선택('소재지', 1, 그룹별명칭변환('지역(시/도)', location_do))
            특정위치X번째셀렉트에서선택('소재지', 2, location_si)
            특정위치X번째셀렉트에서선택('소재지', 3, location_dong)
            if location_li != '': 
                특정위치의x번째입력태그찾기('소재지', 'text', 리입력칸수).send_keys(location_li)
                # WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="input-1137"]'))).send_keys(location_li)
                # time.sleep(0.5); print("li ok:", self.data['landData'][0]['land_li'])
            
            # time.sleep(0.5); print("type_path ok:", self.data['type_path'])
            # pyautogui.alert("go?"+"\n"+"brtit_bldNm:"+brtit_bldNm)
            if obinfo_type1 in ['아파트','오피스텔']:
                #단지선택
                if obinfo_type1 == '아파트':
                    단지선택항목 = brtit_bldNm
                    # 특정위치X번째셀렉트에서선택('단지', 3, brtit_bldNm)
                elif obinfo_type1 == '오피스텔':
                    단지선택항목 = building_name
                    # 특정위치X번째셀렉트에서선택('단지', 1, 단지선택항목)
                pyautogui.alert("단지 선택후 확인을 클릭하여 주십시오."+"\n\n"+"※예상단지명: "+단지선택항목, "단지선택")
                
                #평형선택(전용면적이 포함되어 있는 항목 선택)
                try:
                    if obinfo_type1 == '아파트':
                        특정위치X번째셀렉트에서선택('단지', 2, basic_area1)
                        # driver.find_element(By.XPATH, f'//*[@id="app"]/div/div/div[3]/div/div[1]/div[5]/table/tbody/tr[2]/td/div[1]/div[2]').click()
                        # 평형선택항목 = WebDriverWait(driver, 10).until(
                        #     EC.element_to_be_clickable((By.XPATH, f"//div[@class='v-overlay-container']//div[contains(text(), '{basic_area1}')]"))
                        # )
                        # 평형선택항목.click()
                        # print(f"선택완료:{basic_area1}")
                    elif obinfo_type1 == '오피스텔':
                        특정위치X번째셀렉트에서선택('단지', 2, basic_area1)
                        # driver.find_element(By.XPATH, f'//*[@id="app"]/div/div/div[3]/div/div[1]/div[5]/table/tbody/tr[2]/td/div[1]/div[2]').click()
                        # 평형선택항목 = WebDriverWait(driver, 10).until(
                        #     EC.element_to_be_clickable((By.XPATH, f"//div[@class='v-overlay-container']//div[contains(text(), '{basic_area1}')]"))
                        # )
                        # 평형선택항목.click()
                        
                except Exception as e:
                    print(f"An error occurred: {e}")
            else:
                리입력칸수 = 1
                if self.data['type_path']=='산':
                    # driver.find_element(By.XPATH, '//*[@id="ismount2"]').click()
                    라디오버튼선택('소재지', '산')
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
                상세주소값 = ''
                상세주소입력파트 = 특정위치의x번째입력태그찾기('상세주소', 'text', 1)
                if tr_target == '토지':
                    상세주소값 = location_detail.strip()
                else:
                    if '무명건물' not in building_name:
                        특정위치의x번째입력태그찾기('건물명', 'text', building_name)
                    # if tr_target == '건물':
                    #     상세주소값 = location_building.strip()
                    # elif tr_target == '층호수':
                    #     상세주소값 = location_room.strip()
                    상세주소값 = location_detail
                # print("상세주소값:"+상세주소값)
                # pyautogui.alert("상세주소값:"+상세주소값)
                라디오버튼선택('상세주소', '상세주소 없음') if 상세주소값 == '' else  상세주소입력파트.send_keys(상세주소값)

                #지도
                if object_type == '주거용':
                    라디오버튼선택('지도', '지도 표시')
                else:
                    라디오버튼선택('지도', '지도 표시안함')
                
            # pyautogui.alert("go?"+brtit_bldNm)
        #가격정보
            print('obinfo_ttype:'+str(obinfo_ttype)+' obinfo_trading:'+str(obinfo_trading)+' obinfo_deposit1:'+str(obinfo_deposit1)+' obinfo_rent1:'+str(obinfo_rent1))
            if obinfo_ttype=='매매':
                print("매매가: ",obinfo_trading)
                if obinfo_trading:
                    if obinfo_type1 == '원룸':
                        pyautogui.alert("매물분류 '원룸'은 매매로 등록이 불가합니다.\n\n프로중개인에서 매물분류 변경후 다시 시도하세요!!")
                        driver.quit()
                    특정위치의x번째입력태그찾기('매매가', 'Number', 1).send_keys(obinfo_trading) #매매가
                    trading_memo += "\n"+"-- 거래종류 : "+obinfo_ttype
                    trading_memo += "\n"+"-- 거래금액 : "+한글금액(obinfo_trading)
            # pyautogui.alert("go?")
            if (obinfo_ttype=='전세' or obinfo_ttype=='월세') and obinfo_deposit1:
                print("보증금: ",obinfo_deposit1)
                보증금카테고리명 = '전세가' if obinfo_ttype=='전세' else '보증금'
                보증금입력파트 = 특정위치의x번째입력태그찾기(보증금카테고리명, 'Number', 1)
                보증금입력파트.send_keys(obinfo_deposit1)
                rent_memo += "\n"+"-- 거래종류 : "+obinfo_ttype
                rent_memo += "\n"+"-- 보증금 : "+한글금액(obinfo_deposit1)
                if obinfo_ttype=='월세' and obinfo_rent1:
                    print("월세: ",obinfo_rent1)
                    월세입력파트 = 특정위치의x번째입력태그찾기('월세', 'number', 1)
                    월세입력파트.send_keys(obinfo_rent1)
                    rent_memo += "\n"+"-- 월세 : "+한글금액(obinfo_rent1)
                    if obinfo_deposit2:
                        rent_memo += "\n※보증금조정가능(문의)"
                # pyautogui.alert("go?")
            if obinfo_type1 in ['상가점포','사무실']:
                if premium_exist == '있음':
                    if premium.isdigit():
                        특정위치의x번째입력태그찾기('권리금', 'number', 1).send_keys(premium)
                    premium_memo = "\n"+"-- 권리금(시설비) : " + (한글금액(premium) if premium.isdigit() else premium)
                    premium_memo += "\n"+"-- 권시물내역 : " + premium_content + " 등" if premium_content else "\n"+"-- 권시물내역 : 확인필요"

        #관리비 부과정보
            
            if tr_target != '토지': 
                if basic_manager == '별도':
                    print("관리비:"+str(float(basic_mmoney))+" , 관리비항목들:"+관리비항목들)
                    if obinfo_type1 in ['원룸','주택']:
                        if float(basic_mmoney) < 100000:
                            # 라디오버튼선택('부과방식', '정액관리비')
                            라디오버튼선택('부과방식', '기타부과')
                            라디오버튼선택('부과기준', '직전 월 관리비')
                            #관리비세부내역
                            특정위치X번째셀렉트에서선택('관리비 타입',1,'정액관리비가 10만원 미만인 경우')
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
                    elif obinfo_type1 in ['사무실','상가점포']:
                        특정위치의x번째입력태그찾기('월 관리비', 'number', 1).send_keys(int(basic_mmoney))
                        # 라벨들로체크박스클릭('월 관리비', 관리비항목들)
                        # pyautogui.alert("go?")
                else:   
                    print("basic_manager:" + basic_manager)
                    if obinfo_type1 in ['오피스텔','주택']:
                        라디오버튼선택('부과방식', '정액관리비 (세부내역 미고지한 경우)')
                        라디오버튼선택('부과기준', '직전 월 관리비')
                        특정위치X번째셀렉트에서선택('관리비 타입',1,'정액관리비이지만 중개의뢰인이 세부내역 미고지한 경우')
                        특정위치의x번째입력태그찾기('관리비', 'number', 1).send_keys(0)
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

                    elif obinfo_type1 in ['아파트']:
                        라디오버튼선택('부과방식', '기타부과')
                        라디오버튼선택('부과기준', '직전 월 관리비')
                        특정위치X번째셀렉트에서선택('관리비 타입',1,'관리규약 등에 따라부과')
                        # 셀렉트항목선택('관리규약 등에 따라부과', '//*[@id="app"]/div/div/div[3]/div/div[1]/div[9]/table/tbody/tr[1]/td/div[1]/div[1]')
                        라벨들로체크박스클릭('포함항목', 관리비항목들)     

                    elif obinfo_type1 in ['공장창고']:
                        특정위치의x번째입력태그찾기('월 관리비', 'checkbox', 1).click() 

                    elif obinfo_type1 in ['원룸','상가점포','사무실']:    
                        if obinfo_ttype=='매매':
                            try:
                                관리비없음체크박스 = 특정위치의x번째입력태그찾기('월 관리비', 'checkbox', 1)
                                관리비없음체크박스.click()
                            except:
                                fail_msg += '\n- 관리비없음 체크실패'
                        else:
                            if basic_manager == '없음':
                                if obinfo_type1 in ['상가점포','사무실']:
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
                                if obinfo_type1 in ['원룸']:
                                    라디오버튼선택('부과방식', '정액관리비 (세부내역 미고지한 경우)')
                                    라디오버튼선택('부과기준', '직전 월 관리비')
                                    특정위치X번째셀렉트에서선택('관리비 타입',1,'정액관리비이지만 중개의뢰인이 세부내역 미고지한 경우')
                                    # 셀렉트항목선택('정액관리비이지만 중개의뢰인이 세부내역 미고지한 경우', '//*[@id="app"]/div/div/div[3]/div/div[1]/div[9]/table/tbody/tr[1]/td/div[1]/div[3]')
                                    특정위치의x번째입력태그찾기('관리비', 'number', 1).send_keys(0)
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
                if obinfo_type1 in ['원룸','주택']:
                    라디오버튼선택('건물유형', '건물 일부 (방 또는 일부)')
            elif tr_target == '건물':
                B_memo += "\n"+"\n"+"□■ 건물정보"
                if obinfo_type1 in ['원룸','주택']:
                    라디오버튼선택('건물유형', '건물 전체')
            elif tr_target == '토지' or tr_target == '건물':
                L_memo += "\n"+"\n"+"□■ 토지정보" 
            # pyautogui.alert("go?")    
            if obinfo_type1 in ['아파트', '오피스텔']:
                # 문자열의 마지막 글자가 '동'인지 확인
                # 마지막 '동' 제거
                brtit_dongNm = brtit_dongNm[:-1] if brtit_dongNm.endswith('동') else ''
                if room_num.endswith('호'):
                    room_num = room_num[:-1]
                #해당 동/호
                특정위치의x번째입력태그찾기('해당 동/호', 'text', 1).send_keys(brtit_dongNm)
                특정위치의x번째입력태그찾기('해당 동/호', 'text', 2).send_keys(room_num)
            # pyautogui.alert("정상?") 
            
            #연면적
            if tr_target == '건물':
                if obinfo_type1 in ['주택', '공장창고', '빌딩건물']:
                    # pyautogui.alert(f"tr_target:{tr_target},tr_target:{tr_target}") 
                    print('building_totarea:'+str(building_totarea))
                    if building_totarea : 특정위치의x번째입력태그찾기('연면적', 'text', 1).send_keys(building_totarea)   
                    if building_totarea: B_memo += "\n"+"-- 연면적: "+building_totarea+f"㎡ (약{제곱미터_평_변환(building_totarea)}평)"
            #건축면적
                    if building_archarea : 특정위치의x번째입력태그찾기('건축면적', 'text', 1).send_keys(building_archarea)   
                    if building_archarea: B_memo += "\n"+"-- 건축면적: "+building_archarea+f"㎡ (약{제곱미터_평_변환(building_archarea)}평)"
            
            #대지면적
            if tr_target in ['토지', '건물']:
                print('land_totarea:'+str(land_totarea))
                if land_totarea : 특정위치의x번째입력태그찾기('대지면적', 'text', 1).send_keys(land_totarea)   
                if land_totarea: L_memo += "\n"+"-- 대지면적: "+land_totarea+f"㎡ (약{제곱미터_평_변환(land_totarea)}평)"
            #계약면적
            if obinfo_type1 in ['상가점포','사무실']:
                print('basic_area2:'+str(basic_area2))
                basic_area2 = basic_area1 if (basic_area2 == '' or basic_area2 == '') else basic_area2
                # pyautogui.alert("정상?") 
                if obinfo_type2 in ['지식산업센터']:
                    특정위치의x번째입력태그찾기('공급면적', 'text', 1).send_keys(str(basic_area2))
                else:
                    특정위치의x번째입력태그찾기('임대(계약)면적', 'text', 1).send_keys(str(basic_area2))
                if basic_area2: R_memo += "\n"+"-- 계약면적: "+basic_area2+f"㎡ (약{제곱미터_평_변환(basic_area2)}평)"
            #전용면적
            if obinfo_type1 in ['원룸','주택','상가점포','사무실']:
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
                    
                if building_type != '집합':
                    r_add_memo = "\n"+"※ 일반건물의 전용면적은 실측면적과 다를 수 있습니다."
                try:
                    특정위치의x번째입력태그찾기('전용면적', 'text', 1).send_keys(str(basic_area1))
                except:
                    fail_msg += '\n- 전용면적 입력실패'
                if basic_area1: R_memo += "\n"+"-- 전용면적: "+str(basic_area1)+f"㎡ (약{제곱미터_평_변환(basic_area1)}평)"
            #공급면적
            if obinfo_type1 in ['원룸','주택']:
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
                print('basic_floor:'+str(basic_floor)+' basic_totflr:'+str(basic_totflr))
                #해당층 #해당동 총층
                if obinfo_type1 in ['아파트', '오피스텔']:
                    특정위치의x번째입력태그찾기('해당층 / 해당동 총층', 'text', 1).send_keys(basic_floor)
                    # 특정위치의x번째입력태그찾기('해당층 / 해당동 총층', 'number', 1).send_keys(basic_totflr)
                elif obinfo_type1 in ['상가점포','사무실','주택','원룸']:
                    특정위치의x번째입력태그찾기('해당층 / (해당동) 총층', 'text', 1).send_keys(basic_floor)
                    특정위치의x번째입력태그찾기('해당층 / (해당동) 총층', 'number', 1).send_keys(basic_totflr) 
                    if basic_floor: R_memo += "\n"+"-- 해당층: "+basic_floor+"층"
                basic_totflr += "\n"+"-- 총층: "+basic_totflr+"층"
                # pyautogui.alert("정상?")   
                #층노출동의여부
                if obinfo_type1 in ['원룸','주택']:
                    if object_type != '주거용':
                        라디오버튼선택('층노출 동의여부', '동의 (층 노출)')
                    else:
                        라디오버튼선택('층노출 동의여부', '동의안함 (고/중/저 노출)')
                elif obinfo_type1 in ['아파트']:
                    특정위치의x번째입력태그찾기('층노출 동의여부', 'radio', 2).click()
            #방수/욕실수
            if obinfo_type1 in ['원룸','주택']:
                if obinfo_type1 == '원룸':
                    라디오버튼선택('방수 / 욕실수', '1개')
                    특정위치의x번째입력태그찾기('방수 / 욕실수', 'number', 1).send_keys(basic_bcount)
                elif obinfo_type1 == '주택':
                    if tr_target == '층호수':
                        if basic_rcount: R_memo += "\n"+"-- 방수: "+basic_rcount
                        if basic_bcount: R_memo += " / 욕실수: "+basic_bcount                        
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
                        if basic_rcount: B_memo += "\n"+"-- 건물구성(호실): "+basic_rcount
                    특정위치의x번째입력태그찾기('방수 / 욕실수', 'number', 1).send_keys(basic_rcount)
                    특정위치의x번째입력태그찾기('방수 / 욕실수', 'number', 2).send_keys(basic_bcount)
            #방향
            # print('r_direction:'+r_direction+" room_direction:"+room_direction)
            if tr_target == '층호수':
                print('room_direction:'+str(room_direction))
                room_direction = '남' if room_direction == '' else room_direction
                if obinfo_type1 in ['상가점포','사무실']:
                    특정위치X번째셀렉트에서선택('방향', 1, room_direction)
                    # 셀렉트항목선택(room_direction, '//*[@id="app"]/div/div/div[3]/div/div[1]/div[11]/table/tbody/tr[13]/td/div[1]/div')
            elif tr_target == '건물':
                print('building_direction:'+str(building_direction))
                if building_direction == '':
                    fail_msg += '\n- 건물방향 입력실패'
                else:
                    if obinfo_type1 in ['주택']:
                        특정위치X번째셀렉트에서선택('방향기준 / 방향', 2, building_direction)
                    else:
                        특정위치X번째셀렉트에서선택('방향', 1, building_direction)
                    print("건물방향 선택완료: " + building_direction)
                
            #방향기준/방향
            if obinfo_type1 in ['원룸','주택','아파트','오피스텔']:
                특정위치X번째셀렉트에서선택('방향기준 / 방향', 1, '안방')
                if room_direction: 특정위치X번째셀렉트에서선택('방향기준 / 방향', 2, room_direction)
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
                if obinfo_type1 in ['원룸','주택']:
                    특정위치의x번째입력태그찾기('세대(가구수)', 'number', 1).send_keys(세대가구수)
            # pyautogui.alert("세대(가구수) 확인")
            #방거실형태
            if obinfo_type1 in ['주택']:
                라디오버튼선택('방거실형태', '분리형')
            # pyautogui.alert("방거실형태 확인")
            #복층여부
            if obinfo_type1 in ['원룸','주택']:
                if '복층형' in room_important:
                    라디오버튼선택('복층여부', '복층')
                else:
                    라디오버튼선택('복층여부', '단층')
            # pyautogui.alert("복층여부 확인")
            #주차가능여부
            if obinfo_type1 in ['원룸','주택','아파트','상가점포','사무실','오피스텔']:
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
                if obinfo_type1 in ['아파트', '오피스텔']:
                    print('세대당주차대수값:'+str(세대당주차대수값)+" building_pn:"+str(building_pn))
                    #세대당 
                    특정위치의x번째입력태그찾기('세대당 / 총 주차대수', 'text', 1).send_keys(str(세대당주차대수값))
                    #총
                    특정위치의x번째입력태그찾기('세대당 / 총 주차대수', 'number', 1).send_keys(str(building_pn))
                else:
                    특정위치의x번째입력태그찾기('총 주차대수', 'number', 1).send_keys(str(building_pn))
            
            #건축구조
            if tr_target == '건물':
                if obinfo_type1 in ['공장창고']:
                    try:
                        if building_stract: 특정위치X번째셀렉트에서선택('건축구조', 1, 그룹별명칭변환('건축구조', building_stract))
                    except:
                        fail_msg += '\n- 건축구조 선택실패'
            #용도지역
            if tr_target == '건물' or tr_target == '토지':
                    try:
                        if representing_purpose: 특정위치X번째셀렉트에서선택('용도지역', 1, representing_purpose)
                    except:
                        fail_msg += '\n- 용도지역 선택실패'
            #사용전력
                    try:
                        if building_bolt: 
                            if building_bolt <= 25:
                                전력범위값 = "25Kw 이하"
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
                            특정위치X번째셀렉트에서선택('사용전력', 1, 전력범위값)
                    except:
                        fail_msg += '\n- 사용전력 선택실패'
                
            #건축물용도
            if tr_target != '토지' : 
                print('building_purpose:'+str(building_purpose))
                if obinfo_type1 in ['아파트', '오피스텔']:
                    공동주택키워드s = ['공동주택', '다세대', '연립', '업무시설']
                    # 공동주택키워드s = ['공동주택', '다세대', '연립']
                    # building_purpose에 키워드 중 하나라도 포함되어 있는지 확인
                    if any(keyword in building_purpose for keyword in 공동주택키워드s):
                        건축물용도선택값 = 2
                    elif '숙박시설' in building_purpose:
                        건축물용도선택값 = 15
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
                    # 구분자 목록
                    delimiters = ['(', ',', '.', ' 및 ', '/', '또한', ' ']        
                    # 구분자들을 이스케이프 처리하고 정규 표현식 패턴을 만듭니다.
                    pattern = '|'.join(re.escape(delimiter) for delimiter in delimiters)
                    # 주어진 패턴으로 문자열을 분할합니다.
                    parts = re.split(pattern, building_purpose)
                    # 첫 번째 부분을 반환합니다. 공백 제거를 포함
                    building_purpose = parts[0].strip() 
                    # if ',' in building_purpose:
                    #     building_purpose = building_purpose.split(',')[0]
                    # elif '.' in building_purpose:
                    #     building_purpose = building_purpose.split('.')[0]
                    # elif ' 및 ' in building_purpose:
                    #     building_purpose = building_purpose.split(' 및 ')[0]
                    
                    특정위치X번째셀렉트에서선택('건축물용도', 1, 그룹별명칭변환('건축물용도', building_purpose))
                    # 셀렉트항목선택(그룹별명칭변환('건축물용도', building_purpose), '//*[@id="app"]/div/div/div[3]/div/div[1]/div[11]/table/tbody/tr[30]/td/div[1]/div/div[1]')
                    if building_purpose: B_memo += "\n"+"-- 건축물 주용도: "+그룹별명칭변환('건축물용도', building_purpose)
                if obinfo_type1 in ['원룸','주택','상가점포','사무실','공장창고']:
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
                if obinfo_type1 in ['원룸','주택']:
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
                    if '에어컨' in optionImportant:
                        냉방시설항목들 = []
                        #호실 메모에 구체적인 에어컨이 기록되어있으면 그것을 선택
                        if '벽걸이에어컨' in room_memo :
                            냉방시설항목들.append('벽걸이에어컨')
                        if '스텐드에어컨' in room_memo :
                            냉방시설항목들.append('스텐드에어컨')
                        if '천정에어컨' in room_memo or '천정형에어컨' in room_memo or '시스템에어컨' in room_memo :
                            냉방시설항목들.append('천정에어컨')
                        if len(냉방시설항목들) > 0 : 
                            라벨들로체크박스클릭('냉방시설', 냉방시설항목들)
                        else:
                            fail_msg += '\n- 시설정보(냉방시설) 에어컨 종류 선택실패'
                if obinfo_type1 not in ['오피스텔', '아파트','주택'] :
                    #난방시설
                    특정위치X번째셀렉트에서선택('난방시설', 1, '개별난방')
                    #난방연료
                    특정위치X번째셀렉트에서선택('난방연료', 1, '도시가스')
                # #냉방시설
                # if obinfo_type1 not in ['아파트']:
                #     라벨들로체크박스클릭('냉방시설', 시설정보항목들)
                #생활시설
                if obinfo_type1 in ['원룸','주택','오피스텔']:
                    라벨들로체크박스클릭('생활시설', 시설정보항목들)
                #보안시설
                라벨들로체크박스클릭('보안시설', 시설정보항목들)
                #기타시설
                라벨들로체크박스클릭('기타시설', 시설정보항목들)
            else:
                if land_important: L_memo += "\n"+"-- 토지특징: "+land_important
        #매물상세정보
            print('매물상세정보 시작')
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
            description += "\n"+" "
            description += f"□■ 신속한 상담을 위해 '네이버부동산에서 매물번호[ {object_code_new} ]를 보고 문의드립니다.'라고 말씀해주세요~"
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
            description += "\n"+""" "원하시는 매물을 찾을 때까지 끝까지 최선을 다하겠습니다." """   
            description += "\n"+""
            description += "\n"+""" "매물에 관한 자세한 상담을 원하시면 지금 바로 전화주세요!!" """   
            description += "\n"+""
            description += "\n"+""" "문의주시면 더 많은 비공개 매물까지도 안내받으실 수 있습니다." """   
            description += "\n"+""
            description += "\n"+""" "오산/화성/평택/용인 최대 빅데이터 보유!! 오산에서방구하기 오방!!" """   
            description += "\n"+""
            description += "\n"+""" "차별화된 중개시스템으로 원하는 매물을 쉽게!! 빠르게!! 정확하게!!" """   
            # 태그별개수출력('상세정보')
            # 상세정보script = "arguments[0].value = arguments[1];"
            상세정보script = """
            var textarea = arguments[0];
            var value = arguments[1];
            textarea.value = value;
            var event = new Event('input', { bubbles: true });
            textarea.dispatchEvent(event);
            """
            driver.execute_script(상세정보script, 특정위치의x번째입력태그찾기('상세정보', 'textarea', 1), description)
            # 특정위치의x번째입력태그찾기('상세정보', 'textarea', 1).send_keys(description) #느림 description
            print('매물상세정보 종료')
            # pyautogui.alert("정상?")   
            # 비공개script = "arguments[0].value = arguments[1];"
            비공개script = """
            var textarea = arguments[0];
            var value = arguments[1];
            textarea.value = value;
            var event = new Event('input', { bubbles: true });
            textarea.dispatchEvent(event);
            """
            driver.execute_script(비공개script, 특정위치의x번째입력태그찾기('관리자 메모(비공개 정보)', 'textarea', 1), basic_secret+obinfo_content)
            fail_msg = 홍보확인서선택및의뢰인정보입력(fail_msg)    

















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
                else:
                    광고상태 = "광고중"
                    print("광고가 아직 유효합니다. '등록리스트'로 이동")
                    driver.get('https://ma.serve.co.kr/good/articleRegistList')

            else:
                print("광고 종료일이 설정되지 않았습니다.")   
                # driver.get('https://ma.serve.co.kr/good/articleRegistList')
            time.sleep(3)

            
            # pyautogui.alert("네이버 선택확인")
            if 써브매물번호:
                매물번호입력요소 = 특정위치의x번째입력태그찾기('매물번호', 'text', 1)
                매물번호입력요소.send_keys(써브매물번호)
            else:
                특정위치X번째셀렉트에서선택('매물번호', 1, '네이버')
                매물번호입력요소 = 특정위치의x번째입력태그찾기('매물번호', 'text', 1)
                매물번호입력요소.send_keys(네이버매물번호)
                
            # 매물번호입력요소.send_keys(네이버매물번호)
            매물번호입력요소.send_keys(Keys.ENTER)

            # 최대 5초 동안 대기
            # time.sleep(1)
            # pyautogui.alert("검색결과건수 확인")

            # if not self.wait_for_confirmation("2단계 작업이 완료되었습니다. 계속 진행할까요?"):
            #     self.finished.emit(False)
            #     return

            try:
                # span 태그를 찾고 값이 '1'일 때까지 대기
                element = WebDriverWait(driver, 10).until(
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
                    pyautogui.alert(f"span 태그의 값이 10초 안에 1이 되지 않았습니다. 현재 값: {검색결과건수}", "알림")
                except Exception as e:
                    pyautogui.alert(f"span 태그를 찾을 수 없습니다. 오류: {e}", "오류")        
            
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
                    # driver.find_element(By.XPATH, f'//*[@id="printArea"]/div/table/tbody/tr/td[7]/div/div[2]/button').click() 
                    time.sleep(2)
                    다시보지않기확인()  
                elif 광고상태 == '광고실패':
                    driver.find_element(By.XPATH, f'//*[@id="printArea"]/div/table/tbody/tr/td[7]/div/div[1]/button').click() 
                    time.sleep(2)
                    다시보지않기확인()  
                    # #네이버등록권
                    # 특정위치의x번째입력태그찾기('네이버등록권', 'radio', 1).click()  
                    fail_msg = 홍보확인서선택및의뢰인정보입력(fail_msg)    
                elif 광고상태 == '광고종료':
                    driver.find_element(By.XPATH, f'//*[@id="printArea"]/div/table/tbody/tr/td[7]/div/div[1]/button').click() 
                    time.sleep(2)
                    다시보지않기확인()  
                    # #네이버등록권
                    # 특정위치의x번째입력태그찾기('네이버등록권', 'radio', 1).click()  
                    fail_msg = 홍보확인서선택및의뢰인정보입력(fail_msg)    

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
                    except Exception as e:
                        print(f"Failed to click the checkbox through label: {e}")            
                else:
                    print("No checkbox ID found for the label.")
            else:
                print("Label with text '모두동의 (필수)' not found.")
            # pyautogui.alert("정상?") 
        #물건사진 폴더열기
            main_dir = 'Z:\\업무자료\\4사진자료&이미지자료(외부유출금지)\\1주거용물건, 상업용물건\\'
            path_dir = main_dir + self.data['folderPath'] #'경기도\\오산시\\궐동\\654-9\\썬플라워\\1층\\1층'
            print(path_dir)
            try:
                os.startfile(path_dir)
                print('폴더열기 성공') 
            except:
                print('폴더열기 에러(해당폴더 없음)')             
        except Exception as e:
            print(f"약관동의 에러: {e}")
    

        print("확인메세지 표시전")
        if not self.wait_for_confirmation(address_info+"\n"+fail_msg+"\n\n매물번호를 추출하여 저장합니다.\n\n수정내용 저장후\n써브/네이버/KB부동산 매물번호가 보이는 페이지에서\n'확인'버튼을 눌러주세요"):
            self.finished.emit(False)
            return
        # pyautogui.alert(address_info+"\n"+fail_msg+"\n\n매물번호를 추출하여 저장합니다.\n\n수정내용 저장후\n써브/네이버/KB부동산 매물번호가 보이는 페이지에서\n'확인'버튼을 눌러주세요", "[네이버부동산]")
        print("확인메세지 표시후")




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
            # alert_message = ""

            # XPath 지정
            sources = {
                "써브": '//div[@class="t-btn-item" and @title="써브"]//span[@data-v-2e0e3870 and text()]',
                "네이버": '//div[@class="t-btn-item" and @title="네이버"]//span[@class="v-btn__content"]/span',
                # "KB부동산": '//div[@class="t-btn-item" and @title="KB부동산"]//span[@class="v-btn__content"]/span',
            }

            # 각 매물번호를 찾아서 변수에 저장
            for source_name, xpath in sources.items():
                try:
                    element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, xpath)))
                    매물번호[source_name] = element.text
                except Exception as e:
                    print(f"{source_name} 매물번호를 찾을 수 없습니다. 오류: {e}")
                    매물번호[source_name] = "찾을 수 없음"      
                    # 네이버매물번호, 써브매물번호, KB매물번호를 매물번호 딕셔너리에서 가져옴
                네이버매물번호 = 매물번호.get("네이버", "")
                써브매물번호 = 매물번호.get("써브", "")
                # KB매물번호 = 매물번호.get("KB부동산", "")     

            # 결과 출력 (확인을 위해)
            print(f"네이버매물번호: {네이버매물번호}")
            print(f"써브매물번호: {써브매물번호}")
            # print(f"KB매물번호: {KB매물번호}")


            # DB 연결
            conn = pymysql.connect(host='obangkr.cafe24.com', user='obangkr', password='Ddhqkd!1', charset='utf8')

            # 광고 시작일과 종료일 계산
            ad_start, ad_end = get_ad_dates()   

            # # 변수 확인
            # print(f"INSERT 쿼리에 사용될 변수:")
            # print(f"담당자 아이디 (admin_id): {admin_id}")
            # print(f"새홈 매물번호 (object_code_new): {object_code_new}")
            # print(f"광고 사이트 (ad_site): 네이버")
            # print(f"네이버 매물번호 (ad_code): {네이버매물번호}")
            # print(f"날짜 (ad_udate): {current_date}")
            # print(f"시간 (ad_utime): {current_time}")
            # print(f"써브매물번호: {써브매물번호}")

            try:
                # DictCursor 대신 기본 커서 사용
                cursor = conn.cursor()
                # cursor = conn.cursor(pymysql.cursors.DictCursor)
                cursor.execute('USE obangkr;')

                # 네이버 광고 여부 확인 쿼리
                check_query = """
                    SELECT *
                    FROM pr_externalad
                    WHERE admin_id = %s AND object_code_new = %s AND ad_site = '네이버'
                """
                cursor.execute(check_query, (admin_id, object_code_new))
                existing_record = cursor.fetchone()

                if existing_record:
                    # 기본 커서 결과를 컬럼별로 매핑
                    columns = [desc[0] for desc in cursor.description]
                    existing_record = dict(zip(columns, existing_record))                    
                    print('광고 정보가 있는 경우 - 수정 작업 수행')
                    # 기존 매물번호와 새 매물번호 비교
                    current_ad_code = existing_record['ad_code']
                    print(f"기존 매물번호 (ad_code): {current_ad_code}")
                    print(f"새 매물번호 (네이버매물번호): {네이버매물번호}")  
                    if current_ad_code == 네이버매물번호:
                        alert_message = "담당자가 이미 동일한 네이버 광고 매물번호를 사용하고 있습니다."
                    else:
                    
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
                        query_params = [네이버매물번호, current_date, current_time, ad_memo]

                        # 광고중이 아닌 경우 시작일과 종료일 파라미터 추가
                        if 광고상태 != "광고중":
                            query_params.extend([ad_start, ad_end])
                        # WHERE 절에 사용할 파라미터 추가
                        query_params.extend([admin_id, object_code_new])
                        
                        # ad_memo 값 처리
                        existing_ad_memo = existing_record.get('ad_memo', '')  # 기존 ad_memo 값 가져오기
                        new_ad_memo_part = f"써브:{써브매물번호}"
                        # new_ad_memo_part = f"써브:{써브매물번호}, KB부동산:{KB매물번호}"  # 추가할 값
                        new_ad_memo = f"{existing_ad_memo}, {new_ad_memo_part}".strip(', ') if existing_ad_memo else new_ad_memo_part
           
                        # 변수 확인
                        print(f"UPDATE 쿼리에 사용될 변수:")
                        print(f"ad_memo 업데이트 값: {new_ad_memo}")   

                        # # 알림창을 띄우고 테스트를 위해 중단
                        # pyautogui.alert(f"""
                        # 변수 값 확인:
                        # - 새 매물번호: {네이버매물번호}
                        # - 기존 매물번호: {current_ad_code}
                        # - 담당자 아이디: {admin_id}
                        # - 새홈 매물번호: {object_code_new}
                        # 쿼리를 실행하지 않고 중단합니다. 확인 후 진행해주세요.
                        # """)    
                        #  
                        query_preview = f"""
                        UPDATE pr_externalad
                        SET ad_code = '{네이버매물번호}', ad_start = '{ad_start}', ad_end = '{ad_end}', ad_udate = '{current_date}', ad_utime = '{current_time}', 
                            ad_memo = '{new_ad_memo}'
                        WHERE admin_id = '{admin_id}' AND object_code_new = '{object_code_new}' AND ad_site = '네이버';
                        """
                        # pyautogui.alert(f"실행될 쿼리문:\n{query_preview}")
                        try:
                            # 쿼리 실행
                            cursor.execute(update_query, tuple(query_params))
                            
                            # 영향을 받은 행의 수 확인
                            affected_rows = cursor.rowcount

                            if affected_rows > 0:
                                if admin_id and object_code_new and 네이버매물번호 and 써브매물번호 : 
                                    conn.commit()     
                                    alert_message = f"업데이트를 완료하였습니다. {affected_rows}개의 행이 변경되었습니다."
                            else:                      
                                alert_message = "업데이트할 내용이 없습니다. 기존 매물번호와 동일한 매물번호일 수 있습니다."

                        except Exception as e:
                            alert_message = f"쿼리 실행 중 오류가 발생했습니다: {e}"
                
                
                else:
                    print('광고 정보가 없는 경우 - 추가 작업 수행')
                    insert_query = """
                        INSERT INTO pr_externalad (
                            admin_id, object_code_new, ad_start, ad_end, ad_site, ad_code, ad_udate, ad_utime, ad_memo, ad_wdate, ad_wtime
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """

                    # ad_memo 구성
                    ad_memo = f"써브:{써브매물번호}"
                    # ad_memo = f"써브:{써브매물번호}, KB부동산:{KB매물번호}"
                    print(f"ad_memo 업데이트 값: {ad_memo}")

                    # 알림창으로 쿼리 확인
                    query_preview = f"""
                    INSERT INTO pr_externalad (
                        admin_id, object_code_new, ad_start, ad_end, ad_site, ad_code, ad_udate, ad_utime, ad_memo
                    ) VALUES (
                        '{admin_id}', '{object_code_new}', '{ad_start}', '{ad_end}', '네이버', '{네이버매물번호}', '{current_date}', '{current_time}', '{ad_memo}'
                    );
                    """
                    # pyautogui.alert(f"실행될 쿼리문:\n{query_preview}")

                    try:
                        # 쿼리 실행
                        conn.begin()  # 트랜잭션 시작
                        cursor.execute(insert_query, (
                            admin_id, object_code_new, ad_start, ad_end, '네이버', 네이버매물번호, current_date, current_time, ad_memo, current_date, current_time
                        ))
                        if admin_id and object_code_new and 네이버매물번호 and 써브매물번호 :
                            conn.commit()
                            alert_message = f"새 네이버 광고 매물이 추가되었습니다.\n\n부동산써브: {써브매물번호}\n네이버부동산: {네이버매물번호}\n\n작업을 종료합니다."
                            # alert_message = f"새 네이버 광고 매물이 추가되었습니다.\n\n부동산써브: {써브매물번호}\n네이버부동산: {네이버매물번호}\nKB부동산: {KB매물번호}\n\n작업을 종료합니다."
                    except Exception as e:
                        alert_message = f"추가 작업 중 오류가 발생했습니다: {e}"

                # 알림창으로 결과 표시
                if alert_message : 
                    print(alert_message)
                    pyautogui.alert(alert_message)

            except Exception as e:
                conn.rollback()  # 오류 시 롤백
                pyautogui.alert(f"오류 발생: {e}")
            finally:
                conn.close()
        except Exception as e:
            pyautogui.alert(f"오류 발생: {e}", "오류")

        # if not self.wait_for_confirmation("1단계 작업이 완료되었습니다. 계속 진행할까요?"):
        #     self.finished.emit(False)
        #     return

        # # 다른 단계에서도 활용
        # if not self.wait_for_confirmation("2단계 작업을 진행할까요?"):
        #     self.finished.emit(False)
        #     return



        print("모든 작업 완료")
        self.finished.emit(True)
        # finally:
        #     pyautogui.alert(address_info+"\n"+fail_msg+"\n\n매물등록창을 닫으시겠습니까?", "[네이버부동산]")
        # driver.quit()
        driver.close()
        # return errarr   
        
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
