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
from datetime import datetime, date
import time
import os

options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
        
def macro(data, user):
    
    def change_window(target: str):
        if target == 'parent':
            # child window close
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        elif target == 'child':
            driver.switch_to.window(driver.window_handles[1])
        else:
            print("Wrong target!")

    def 테마별명칭재정의(theme, names_arr):
        # 테마에 따른 이름을 바꿀 매핑 딕셔너리 생성
        theme_mappings = {
            '관리비포함내역': {
                '개별전기': '전기료',
                '개별가스': '가스사용료',
                '개별수도': '수도료',
                '인터넷': '인터넷사용료',
                '유선': 'TV사용료',
                '일반': '일반(공용)관리비',
                '기타': '기타관리비'
            },
            '옵션': {
                '벽걸이에어컨': '에어컨',
                '가스렌지': '가스레인지',
                '전자렌지': '전자레인지',
                '붙박이장': '옷장'
            }
        }
        # 주어진 테마에 대한 매핑 딕셔너리 가져오기
        mapping = theme_mappings.get(theme, {})
        # 이름을 매핑된 이름으로 변경
        new_names_arr = [mapping.get(name.strip(), name.strip()) for name in names_arr]
        print(theme+'명칭재정의:', new_names_arr)
        return new_names_arr     
    
    def selectOption(select_xpath, value):
        time.sleep(0.3)
        driver.find_element(By.XPATH, f'{select_xpath}').click() #선택 클릭
        
        select_element = driver.find_element(By.XPATH, f'{select_xpath}')
        
        # Select 객체를 생성하고 select 엘리먼트를 래핑합니다.
        select = Select(select_element)
        try:
            select.select_by_visible_text(value) #일치하는 텍스트 선택하기
        except Exception as e:
            print("선택 오류:", str(e))
    
    def clickLabel(div_selector, item_list): 
        print("item_list:", item_list)       
        # CSS_SELECTOR 사용하여 해당 div 태그를 찾습니다.
        div_element = driver.find_element(By.CSS_SELECTOR, f'{div_selector}')
        # div 태그 내의 모든 label 태그를 찾습니다.
        label_elements = div_element.find_elements(By.TAG_NAME, 'label')
        # 텍스트가 item 값인 label 태그를 찾아 클릭합니다.
        items = item_list.split(',')
        for item in items:
            try:
                for label in label_elements:
                    span_element = label.find_element(By.TAG_NAME, 'span')
                    # print(span_element.text, item)
                    if span_element.text == item:
                        label.click()
                        break  # 원하는 label을 찾았으므로 반복문을 종료합니다.
            except Exception as e:
                print("라벨선택 오류:", str(e))   
                 
    # def 배열값체크하기(driver, 기준div텍스트, 체크할항목들의배열):
    #     try:
    #         # 기준이 되는 요소를 텍스트로 가지는 요소 찾기
    #         base_element = driver.find_element(By.XPATH, f"//*[contains(text(), '{기준div텍스트}')]")
            
    #         # 기준이 되는 요소와 관련된 체크박스들 찾기
    #         checkboxes = base_element.find_elements(By.XPATH, ".//input[@type='checkbox']")
            
    #         # 체크할 항목들을 반복하면서 체크
    #         for item in 체크할항목들의배열:
    #             try:
    #                 # 체크할 항목을 가지는 체크박스 찾기
    #                 checkbox = base_element.find_element(By.XPATH, f".//span[text()='{item}']/preceding-sibling::input[@type='checkbox']")
    #                 if not checkbox.is_selected():
    #                     checkbox.click()
    #                     print(f"{item} 체크 완료")
    #                 else:
    #                     print(f"{item} 이미 체크되어 있습니다.")
    #             except Exception as e:
    #                 print(f"{item} 항목을 찾을 수 없습니다: {e}")
    #     except Exception as e:
    #         print(f"기준이 되는 요소를 찾을 수 없습니다: {e}")

    def 라디오박스_선택하기(driver, 기준div텍스트, 선택할텍스트):
        try:
            # 인자(기준div텍스트)를 텍스트로 가지는 div요소 찾기
            기준div = driver.find_element(By.XPATH, f"//*[contains(text(), '{기준div텍스트}')]")
            print("기준div 통과")
            # '기준div'요소의 상위div를 기준으로 봤을 때 '기준div'가 안에 있는 첫번째 div라고 하면 두번째 div요소 안에 라디오 버튼 요소들을 찾음
            # (주의: 이 코드는 모든 경우에 적합하지 않을 수 있습니다. HTML 구조에 따라 조정이 필요할 수 있습니다.)
            부모_div = 기준div.find_element(By.XPATH, "./..")
            print("부모_div 통과")
            sibling_divs = 부모_div.find_elements(By.XPATH, ".//div")
            # print("sibling_divs 개수:"+len(sibling_divs))
            if 기준div in sibling_divs:
                # '기준div'가 안에 있는 첫번째 div라면, 두번째 div요소 안에 라디오 버튼 요소들을 찾음
                두번째_div = sibling_divs[1]
                radio_elements = 두번째_div.find_elements(By.XPATH, ".//input[@type='radio']")
                print(기준div텍스트 + ' 개수: ' + str(len(radio_elements)))
                # 라디오 버튼 요소들을 반복하며 선택할 텍스트와 일치하는 것을 찾음
                for radio in radio_elements:
                    radio_text = radio.find_element(By.XPATH, "./following-sibling::span").text
                    print("radio_text:"+radio_text)
                    if radio_text == 선택할텍스트:
                        # 클릭 가능한 상태가 될 때까지 기다림
                        # 선택할요소 = 기준div.find_element(By.XPATH, f"./preceding-sibling::input[contains(@type, 'radio') and following-sibling::span[contains(text(), '{선택할텍스트}')]]")
                        # 선택할요소 = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{선택할텍스트}')]/preceding-sibling::input")))
                        선택할요소 = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{선택할텍스트}')]")))
                        print("선택할텍스트:"+선택할텍스트)
                        # print(" 선택할요소 개수:"+len(선택할요소))
                        # 선택할요소.click()
                        if not 선택할요소.is_selected():
                            선택할요소.click()
                            print(f"'{선택할텍스트}' 항목을 선택했습니다.")
                        else:
                            print(f"'{선택할텍스트}' 항목이 이미 선택되어 있습니다.")
                        break
                else:
                    print(f"'{선택할텍스트}' 항목을 찾을 수 없습니다.")
        except Exception as e:
            print(f"기준이 되는 요소를 찾을 수 없습니다: {e}")
            pyautogui.alert(f"기준이 되는 요소를 찾을 수 없습니다: {e}")
    
    def 닫기_버튼_클릭():
        print("닫기_버튼_클릭()")
        try:
            # 공지 레이어 div가 보이는지 확인
            notice_layer = WebDriverWait(driver, 2).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "div.notice_layer[style*='display: block']"))
            )
            if notice_layer:
                # 이 div 내에서 닫기 버튼 찾아 클릭
                close_button = notice_layer.find_element(By.XPATH, ".//button[contains(text(), '닫기')]")
                close_button.click()
                print("공지창이 성공적으로 닫혔습니다.")
            return True

        except Exception as e:
            print("공지창 닫기 시도 중 오류 발생:", e)
            return False   
    
    def 지정선택(대분류, 소분류, 몇번째, 옵션text):
        print(f"지정선택({대분류}, {소분류}, {몇번째}, {옵션text})")
        try: 
            대분류_text = 대분류.replace(' ', '')
            소분류_text = 소분류.replace(' ', '')
            # 모든 strong 요소를 찾아낸 후에 보이는 요소만 필터링
            all_h3_elements = driver.find_elements(By.XPATH, "//section/header/h3")
            visible_h3_elements = [elem for elem in all_h3_elements if elem.is_displayed()]
            # print(f"보이는 h3태그 개수: {len(visible_h3_elements)}개")
            # 각 strong 태그의 부모 tr 요소 찾기
            for h3 in visible_h3_elements:
                # HTML에서 텍스트 추출 후 모든 공백 및 줄바꿈 제거
                h3_text = h3.get_attribute('textContent').replace('\n', '').replace('\r', '').replace(' ', '')   
                if 대분류_text == h3_text:
                    대분류div = h3.find_element(By.XPATH, './ancestor::section[1]/div')
                    all_소분류div_elements = 대분류div.find_elements(By.XPATH, ".//div/div[1]")
                    for 소분류div in all_소분류div_elements: 
                        소분류div_text = 소분류div.get_attribute('textContent').replace('\n', '').replace('\r', '').replace(' ', '')
                        if 소분류_text == 소분류div_text:
                            조회대상div = 소분류div.find_element(By.XPATH, './parent::div')
                            elements = 조회대상div.find_elements(By.XPATH, f'.//select')
                            print(f"elements 개수: {len(elements)}개")
                            # pyautogui.alert("함수 확인")
                            visible_elements = []
                            limit_count = 1  
                            for elem in elements:   
                                if elem.is_displayed(): visible_elements.append(elem)    
                            print(f"visible_elements 개수: {len(visible_elements)}개")
                            # pyautogui.alert("함수 확인")   
                            visible_tag_count = 0
                            for v_elem in visible_elements:
                                visible_tag_count += 1
                                if visible_tag_count == 몇번째:
                                    options = v_elem.find_elements(By.XPATH, f'./option')
                                    for opt in options:
                                        if opt.text == 옵션text:
                                            opt.click()  # opt 요소 선택
                                            print(f"{opt.text} 선택완료")
                                            return  # 옵션을 선택한 후 함수 종료
                                    
                            break                                                                                                           
                                    
            print(f"{몇번째}번째 보이는 {옵션text} 태그를 찾을 수 없습니다.")
            return None

        except Exception as e:
            print(f"An error occurred: {e}")
            return None                        
        
    def 지정태그(대분류, 소분류, tag_type, 몇번째):
        print(f"지정태그({대분류}, {소분류}, {tag_type}, {몇번째})")
        try: 
            대분류_text = 대분류.replace(' ', '')
            소분류_text = 소분류.replace(' ', '')
            # 모든 strong 요소를 찾아낸 후에 보이는 요소만 필터링
            all_h3_elements = driver.find_elements(By.XPATH, "//section/header/h3")
            visible_h3_elements = [elem for elem in all_h3_elements if elem.is_displayed()]
            # print(f"보이는 h3태그 개수: {len(visible_h3_elements)}개")
            # 각 strong 태그의 부모 tr 요소 찾기
            for h3 in visible_h3_elements:
                # HTML에서 텍스트 추출 후 모든 공백 및 줄바꿈 제거
                h3_text = h3.get_attribute('textContent').replace('\n', '').replace('\r', '').replace(' ', '')
                # print("h3_text:"+h3_text)
                # pyautogui.alert("함수 확인")
                # print(f"Found h3태그: {h3태그의텍스트} {h3.get_attribute('outerHTML')}")
                if 대분류_text == h3_text:
                    # section_element = h3.find_element(By.XPATH, './parent::section')
                    대분류div = h3.find_element(By.XPATH, './ancestor::section[1]/div')
                    # print(f"Found 대분류div 태그: {대분류div.get_attribute('outerHTML')}")
                    # 모든 소분류
                    all_소분류div_elements = 대분류div.find_elements(By.XPATH, ".//div/div[1]")  #대분류div 내에서 모든 하위 div 중 첫 번째 자식 div 요소들을 찾기
                    # //*[@id="item_form"]/section[2]/div/div[1]/div[1]
                    # //*[@id="item_form"]/section[2]/div/div[2]/div[1]
                    # //*[@id="item_form"]/section[2]/div/div[3]/div/div[1]
                    # //*[@id="item_form"]/section[2]/div/div[4]/div[1]/div[1]
                    # //*[@id="item_form"]/section[2]/div/div[5]/div[1]
                    # //*[@id="item_form"]/section[2]/div/div[6]/div[1]
                    # //*[@id="item_form"]/section[2]/div/div[7]/div[1]
                    # //*[@id="item_form"]/section[2]/div/div[8]/div[1]
                    
                    # visible_소분류div_elements = [소분류div for 소분류div in all_소분류div_elements if 소분류div.is_displayed()]
                    # print(f"all_소분류div_elements 개수: {len(all_소분류div_elements)}개")
                    for 소분류div in all_소분류div_elements: 
                        소분류div_text = 소분류div.get_attribute('textContent').replace('\n', '').replace('\r', '').replace(' ', '')
                        # print(f"소분류div_text:{소분류div_text}")
                        if 소분류_text == 소분류div_text:
                            조회대상div = 소분류div.find_element(By.XPATH, './parent::div')
                            # print(f"Found td태그: {조회대상div.get_attribute('outerHTML')}")
                            if tag_type in ['textarea', 'a']:
                                elements = 조회대상div.find_elements(By.XPATH, f'.//{tag_type}')
                            else:
                                elements = 조회대상div.find_elements(By.XPATH, f'.//input[@type="{tag_type}"]')
                            # print(f"elements 개수: {len(elements)}개")
                            # pyautogui.alert("함수 확인")
                            visible_elements = []
                            limit_count = 1
                            for elem in elements:
                                # print(f"Found {tag_type} all element: {elem.get_attribute('outerHTML')}")
                                if tag_type in ['checkbox', 'radio']:
                                    # print(f"Found {tag_type} element: {elem.get_attribute('outerHTML')}")
                                    # if elem.is_displayed() and elem.is_enabled():
                                    #     print("클릭가능")
                                    # else:
                                    #     print("클릭불가능")
                                    #     if elem.is_displayed:
                                    #         print("비활성화상태")
                                    #     else:
                                    #         print("안보임")
                                    상위요소 = elem.find_element(By.XPATH, '..')
                                    # print(f"Found {tag_type} 상위요소: {상위요소.get_attribute('outerHTML')}")
                                    # if 상위요소.is_displayed() and 상위요소.is_enabled():
                                    #     print("상위요소 클릭가능")
                                    # else:
                                    #     print("상위요소 클릭불가능")
                                    #     if 상위요소.is_displayed:
                                    #         print("상위요소 비활성화상태")
                                    #     else:
                                    #         print("상위요소 안보임")
                                    visible_elements.append(상위요소)
                                else:
                                    if elem.is_displayed():
                                        visible_elements.append(elem)
                                        # print("요소가 보임")
                                        # print(f"Found {tag_type} element: {elem.get_attribute('outerHTML')}")
                                    # else:
                                    #     print("요소가 안보임")
                                    #     # print(f"{tag_type} element is not displayed: {elem.get_attribute('outerHTML')}")     
                                                           

                            
                            # //*[@id="item_form"]/section[2]/div/div[1]/div[2]/div/div[1]/div/label[1]/input
                            # //*[@id="item_form"]/section[2]/div/div[1]/div[2]/div/div[1]/div/label[2]/input
                            # //*[@id="item_form"]/section[2]/div/div[2]/div[2]/div[1]/div[1]/div/label[1]/input
                            # //*[@id="item_form"]/section[2]/div/div[2]/div[2]/div[1]/div[1]/div/label[2]/input
                            # //*[@id="item_form"]/section[2]/div/div[3]/div/div[2]/div[1]/div[1]/div/div/input
                            # //*[@id="item_form"]/section[2]/div/div[3]/div/div[2]/div[1]/div[2]/div/div/input
                            # //*[@id="item_form"]/section[2]/div/div[3]/div/div[2]/label/input
                            # //*[@id="item_form"]/section[2]/div/div[4]/div[1]/div[2]/div[1]/div[1]/div/div/div/select
                            # //*[@id="item_form"]/section[2]/div/div[4]/div[1]/div[2]/div[1]/div[2]/div/div/div/select
                            # //*[@id="item_form"]/section[2]/div/div[4]/div[2]/div/div[1]/div/div/div/div/select
                            # //*[@id="item_form"]/section[2]/div/div[5]/div[2]/div[1]/div[1]/div/div/input
                            # //*[@id="item_form"]/section[2]/div/div[5]/div[2]/div[1]/div[2]/div/div/input
                            # //*[@id="item_form"]/section[2]/div/div[6]/div[2]/div[1]/div[1]/div/label[1]/input
                            # //*[@id="item_form"]/section[2]/div/div[6]/div[2]/div[1]/div[1]/div/label[2]/input
                            # //*[@id="item_form"]/section[2]/div/div[6]/div[2]/div[1]/div[2]/div/select
                            # //*[@id="item_form"]/section[2]/div/div[7]/div[2]/div[1]/select
                            # //*[@id="item_form"]/section[2]/div/div[8]/div[2]/div[1]/div/input

                            print(f"visible_elements 개수: {len(visible_elements)}개")
                            # pyautogui.alert("함수 확인")
                            # 원하는 태그 찾기
                            visible_tag_count = 0
                            for v_elem in visible_elements:
                                visible_tag_count += 1
                                if visible_tag_count == 몇번째:
                                    return v_elem
                            break                            
                    # pyautogui.alert("함수 확인")


            print(f"{몇번째}번째 보이는 {tag_type} 태그를 찾을 수 없습니다.")
            return None

        except Exception as e:
            print(f"An error occurred: {e}")
            return None   
        
    def 관리비상세지정태그(대분류, 소분류, tag_type, 몇번째):
        print(f"관리비상세지정태그({대분류}, {소분류}, {tag_type}, {몇번째})")
        try: 
            대분류_text = 대분류.replace(' ', '')
            소분류_text = 소분류.replace(' ', '')
            # 모든 strong 요소를 찾아낸 후에 보이는 요소만 필터링
            대분류_elements = driver.find_elements(By.XPATH, '//*[@id="react-modal"]/div/div/div[1]')
            print(f"대분류_elements 개수: {len(대분류_elements)}개")
            pyautogui.alert("확인")
            visible_h3_elements = [elem for elem in 대분류_elements if elem.is_displayed()]
            # print(f"보이는 h3태그 개수: {len(visible_h3_elements)}개")
            # 각 strong 태그의 부모 tr 요소 찾기
            for h3 in visible_h3_elements:
                # HTML에서 텍스트 추출 후 모든 공백 및 줄바꿈 제거
                h3_text = h3.get_attribute('textContent').replace('\n', '').replace('\r', '').replace(' ', '')
                # print("h3_text:"+h3_text)
                # pyautogui.alert("함수 확인")
                # print(f"Found h3태그: {h3태그의텍스트} {h3.get_attribute('outerHTML')}")
                if 대분류_text == h3_text:
                    # section_element = h3.find_element(By.XPATH, './parent::section')
                    대분류div = h3.find_element(By.XPATH, './ancestor::section[1]/div')
                    # print(f"Found 대분류div 태그: {대분류div.get_attribute('outerHTML')}")
                    # 모든 소분류
                    all_소분류div_elements = 대분류div.find_elements(By.XPATH, ".//div/div[1]")  #대분류div 내에서 모든 하위 div 중 첫 번째 자식 div 요소들을 찾기
                    # //*[@id="item_form"]/section[2]/div/div[1]/div[1]
                    # //*[@id="item_form"]/section[2]/div/div[2]/div[1]
                    # //*[@id="item_form"]/section[2]/div/div[3]/div/div[1]
                    # //*[@id="item_form"]/section[2]/div/div[4]/div[1]/div[1]
                    # //*[@id="item_form"]/section[2]/div/div[5]/div[1]
                    # //*[@id="item_form"]/section[2]/div/div[6]/div[1]
                    # //*[@id="item_form"]/section[2]/div/div[7]/div[1]
                    # //*[@id="item_form"]/section[2]/div/div[8]/div[1]
                    
                    # visible_소분류div_elements = [소분류div for 소분류div in all_소분류div_elements if 소분류div.is_displayed()]
                    # print(f"all_소분류div_elements 개수: {len(all_소분류div_elements)}개")
                    for 소분류div in all_소분류div_elements: 
                        소분류div_text = 소분류div.get_attribute('textContent').replace('\n', '').replace('\r', '').replace(' ', '')
                        # print(f"소분류div_text:{소분류div_text}")
                        if 소분류_text == 소분류div_text:
                            조회대상div = 소분류div.find_element(By.XPATH, './parent::div')
                            # print(f"Found td태그: {조회대상div.get_attribute('outerHTML')}")
                            if tag_type in ['textarea', 'a']:
                                elements = 조회대상div.find_elements(By.XPATH, f'.//{tag_type}')
                            else:
                                elements = 조회대상div.find_elements(By.XPATH, f'.//input[@type="{tag_type}"]')
                            # print(f"elements 개수: {len(elements)}개")
                            # pyautogui.alert("함수 확인")
                            visible_elements = []
                            limit_count = 1
                            for elem in elements:
                                # print(f"Found {tag_type} all element: {elem.get_attribute('outerHTML')}")
                                if tag_type in ['checkbox', 'radio']:
                                    # print(f"Found {tag_type} element: {elem.get_attribute('outerHTML')}")
                                    # if elem.is_displayed() and elem.is_enabled():
                                    #     print("클릭가능")
                                    # else:
                                    #     print("클릭불가능")
                                    #     if elem.is_displayed:
                                    #         print("비활성화상태")
                                    #     else:
                                    #         print("안보임")
                                    상위요소 = elem.find_element(By.XPATH, '..')
                                    # print(f"Found {tag_type} 상위요소: {상위요소.get_attribute('outerHTML')}")
                                    # if 상위요소.is_displayed() and 상위요소.is_enabled():
                                    #     print("상위요소 클릭가능")
                                    # else:
                                    #     print("상위요소 클릭불가능")
                                    #     if 상위요소.is_displayed:
                                    #         print("상위요소 비활성화상태")
                                    #     else:
                                    #         print("상위요소 안보임")
                                    visible_elements.append(상위요소)
                                else:
                                    if elem.is_displayed():
                                        visible_elements.append(elem)
                                        # print("요소가 보임")
                                        # print(f"Found {tag_type} element: {elem.get_attribute('outerHTML')}")
                                    # else:
                                    #     print("요소가 안보임")
                                    #     # print(f"{tag_type} element is not displayed: {elem.get_attribute('outerHTML')}")     
                                                           

                            
                            # //*[@id="item_form"]/section[2]/div/div[1]/div[2]/div/div[1]/div/label[1]/input
                            # //*[@id="item_form"]/section[2]/div/div[1]/div[2]/div/div[1]/div/label[2]/input
                            # //*[@id="item_form"]/section[2]/div/div[2]/div[2]/div[1]/div[1]/div/label[1]/input
                            # //*[@id="item_form"]/section[2]/div/div[2]/div[2]/div[1]/div[1]/div/label[2]/input
                            # //*[@id="item_form"]/section[2]/div/div[3]/div/div[2]/div[1]/div[1]/div/div/input
                            # //*[@id="item_form"]/section[2]/div/div[3]/div/div[2]/div[1]/div[2]/div/div/input
                            # //*[@id="item_form"]/section[2]/div/div[3]/div/div[2]/label/input
                            # //*[@id="item_form"]/section[2]/div/div[4]/div[1]/div[2]/div[1]/div[1]/div/div/div/select
                            # //*[@id="item_form"]/section[2]/div/div[4]/div[1]/div[2]/div[1]/div[2]/div/div/div/select
                            # //*[@id="item_form"]/section[2]/div/div[4]/div[2]/div/div[1]/div/div/div/div/select
                            # //*[@id="item_form"]/section[2]/div/div[5]/div[2]/div[1]/div[1]/div/div/input
                            # //*[@id="item_form"]/section[2]/div/div[5]/div[2]/div[1]/div[2]/div/div/input
                            # //*[@id="item_form"]/section[2]/div/div[6]/div[2]/div[1]/div[1]/div/label[1]/input
                            # //*[@id="item_form"]/section[2]/div/div[6]/div[2]/div[1]/div[1]/div/label[2]/input
                            # //*[@id="item_form"]/section[2]/div/div[6]/div[2]/div[1]/div[2]/div/select
                            # //*[@id="item_form"]/section[2]/div/div[7]/div[2]/div[1]/select
                            # //*[@id="item_form"]/section[2]/div/div[8]/div[2]/div[1]/div/input

                            print(f"visible_elements 개수: {len(visible_elements)}개")
                            # pyautogui.alert("함수 확인")
                            # 원하는 태그 찾기
                            visible_tag_count = 0
                            for v_elem in visible_elements:
                                visible_tag_count += 1
                                if visible_tag_count == 몇번째:
                                    return v_elem
                            break                            
                    # pyautogui.alert("함수 확인")


            print(f"{몇번째}번째 보이는 {tag_type} 태그를 찾을 수 없습니다.")
            return None

        except Exception as e:
            print(f"An error occurred: {e}")
            return None   

    
    # 현재 날짜 출력
    current_date = date.today()
    formatted_date = current_date.strftime("%Y-%m-%d")
    
    admin_name = data['adminData']['admin_name']
    zigbang_tag = data['adminData']['zigbang_tag']
    request_code = data['writeData']['request_code'] #의뢰번호
    object_type = data['writeData']['object_type']
    
    location_do = data['landData'][0]['land_do']
    location_si = data['landData'][0]['land_si']
    location_dong = data['landData'][0]['land_dong']

    location_lijibun = (data['type_path'] + data['landData'][0]['land_jibun']) if data['landData'][0]['land_li'] == '' else (data['landData'][0]['land_li'] + data['type_path'] + data['landData'][0]['land_jibun'])
    location_dongli = (data['landData'][0]['land_dong'] + data['type_path'] + data['landData'][0]['land_jibun']) if data['landData'][0]['land_li'] == '' else location_lijibun
    location_detail = location_dongli
    total_location = location_do+" "+location_si+" "+location_detail
    print('주소(total_location):',total_location)
    
    building_purpose = data['buildingData']['building_purpose']
    building_usedate = data['buildingData']['building_usedate'] #사용승인일
    building_parking = data['buildingData']['building_parking'] #주차장유무
    building_pn = data['buildingData']['building_pn']
    building_option = data['buildingData']['building_option'] #건물옵션
    
    brtit_dongNm = data['brtitData']['brtit_dongNm']
    
    # obinfo_trading = data['writeData']['trading'] #매매금액    
    obinfo_deposit1 = data['writeData']['deposit1'] #보증금1
    # obinfo_deposit2 = data['writeData']['deposit2'] #보증금2
    # obinfo_deposit3 = data['writeData']['deposit3'] #보증금3
    obinfo_rent1 = data['writeData']['rent1'] #월세1
    # obinfo_rent2 = data['writeData']['rent2'] #월세2
    # obinfo_rent3 = data['writeData']['rent3'] #월세3
    
    total_floor = str(int(data['buildingData']['building_grndflr']) + int(data['buildingData']['building_ugrndflr']))+"층" #전체층
    room_floor = "반지하" if data['roomData']['room_floor'] == '-1' else str(int(data['roomData']['room_floor']))+"층" #해당층
    room_num = data['roomData']['room_num'] #호실명
    request_term1 = data['writeData']['request_term1'] #계약기간하한
    request_term2 = data['writeData']['request_term2'] #계약기간상한
    room_area1 = data['roomData']['room_area1'] #실면적
    room_rcount = data['roomData']['room_rcount'] #방개수
    room_bcount = data['roomData']['room_bcount']+"개" if data['roomData']['room_bcount'] != '' and data['roomData']['room_bcount'] != '0' else '선택' #욕실수
    r_direction = data['roomData']['direction_stn'] if data['roomData']['direction_stn']!='' else '안방' #호실방향기준
    room_direction = data['roomData']['room_direction'] if data['roomData']['room_direction']!='' else '남' #호실방향
    mmoney = data['writeData']['mmoney'] #관리비
    manager = data['writeData']['manager'] #관리비 별도/포함/미확인
    mlist = data['writeData']['mlist'] #관리비포함내역
    print(f"관리비 (mlist):{mlist}") #관리비 포함 항목
    mlist_arr = mlist.split(",")   
    if len(mlist_arr) > 0 : 재정의된mlist_arr = 테마별명칭재정의('관리비포함내역', mlist_arr) 
    room_important = data['roomData']['room_important'] #호실특징
    room_option = data['roomData']['room_option'] #호실옵션
    room_option = room_option.replace('가스렌지','가스레인지')
    room_option = room_option.replace('벽걸이에어컨','에어컨')
    rdate = str(data['writeData']['rdate']) #입주일
    secret_memo = "https://obangkr.cafe24.com/web/request/request_view/view_give_request_detail.php?request_code="+request_code
    

    print("데이터확인:", building_purpose)
    
    
    
    # ChromeDriver 경로 설정
    driver = webdriver.Chrome(options=options)
    # driver = webdriver.Chrome('/chromedriver', options=options)
    # driver = webdriver.Chrome(ChromeDriverManager().install())

    # URL 열기
    driver.maximize_window()
    driver.get('https://ceo.zigbang.com/?was_slept=False&agree=True')

    driver.find_element(By.XPATH, '/html/body/div[1]/section/div[1]/div[2]/div[2]/div[1]/form/input[2]').send_keys("nasangkwon@outlook.kr")
    driver.find_element(By.XPATH, '/html/body/div[1]/section/div[1]/div[2]/div[2]/div[1]/form/input[3]').send_keys("dhqkd5555%")
    driver.find_element(By.XPATH, '/html/body/div[1]/section/div[1]/div[2]/div[2]/div[1]/form/div[2]/button').click()
    
    driver.implicitly_wait(10)   
    
    # 확인후 이동
    driver.get('https://ceo.zigbang.com/items/list/oneroom')
    

    # #활성화된 모든 팝업창 닫기
    # window_handles = driver.window_handles # 현재 열린 모든 창의 핸들을 가져옴
    # print("활성화된 창의 개수: "+str(len(window_handles)))
    # for handle in window_handles: # 메인 창을 제외한 모든 팝업 창을 닫음
    #     if handle != driver.current_window_handle:
    #         pyautogui.alert("popup go??")
    #         driver.switch_to.window(handle)
    #         driver.close()
    # driver.switch_to.window(driver.window_handles[0]) # 다시 메인 창으로 전환
    
    # pyautogui.alert("1go??") 
    # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/div[2]/button'))).click() #어떤요소를 클릭하는가?
    
    # pyautogui.alert("1go??")   
    # # '오늘하루보이지않음'을 기다림
    # waitbox = WebDriverWait(driver, 10).until(
    #     EC.presence_of_element_located((By.CSS_SELECTOR, "body > div.notice_layer.common_layer.on > div.item_check.has_link > label"))
    # )
    # # '오늘하루보이지않음' 체크
    # waitbox.click()
    # # '닫기버튼'을 기다림
    # closebtn = WebDriverWait(driver, 10).until(
    #     EC.presence_of_element_located((By.CSS_SELECTOR, "body > div.notice_layer.common_layer.on > div.item_check.has_link > button"))
    # )
    # # '닫기버튼' 클릭
    # closebtn.click()

    # pyautogui.alert("go??")
    # 닫기_버튼_클릭()
    
    # pyautogui.alert("2go??")
    
    print('담당자:', admin_name)
    # pyautogui.alert("담당자:"+admin_name)
    # selectOption('//*[@id="react-root"]/article/div[1]/div[1]/div/select', '이은선') #테스트용 담당자 선택
    selectOption('//*[@id="react-root"]/article/div[1]/div[1]/div/select', zigbang_tag) #  담당자 태그선택
    # driver.find_element(By.XPATH, '//*[@id="react-root"]/article/div[1]/div[1]/div/select').click() #담당자 선택
    # select_element = driver.find_element(By.XPATH, '//*[@id="react-root"]/article/div[1]/div[1]/div/select')
    # # Select 객체를 생성하고 select 엘리먼트를 래핑합니다.
    # select = Select(select_element)
    # try:
    #     select.select_by_visible_text('이은선') #담당자로 본인을 선택하기
    # except Exception as e:
    #     print("담당자선택 오류:", str(e))
    
    #방개수2개이상 빌라선택
    if int(room_rcount) >= 2:
        # pyautogui.alert("go??")
        driver.find_element(By.XPATH, '/html/body/div[1]/section/div[1]/a[2]').click()
        
    driver.find_element(By.XPATH, '//*[@id="react-root"]/article/div[2]/div/button').click() # 배너등록하기 버튼 클릭
    # pyautogui.alert("go??")
    # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[4]/div[2]/button'))).click() #어떤요소를 클릭하는가?
    
    # 닫기_버튼_클릭()
    # pyautogui.alert("go??")
    #건물형태
    if int(room_rcount) < 2:
        driver.find_element(By.XPATH, '//*[@id="react-root"]/article/section/div[2]/div/div[2]/div[2]/a[1]').click() # 원룸형 선택
    
    
    
    time.sleep(0.5)  
    # '주소찾기' 버튼 클릭
    button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="item_form"]/section[1]/div/div/div[2]/div[1]/button'))
    )
    button.click()

    # # iframe으로 전환
    # iframe = WebDriverWait(driver, 10).until(
    #     EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//*[@id="__daum__viewerFrame_1"]'))
    # )
    main_page = driver.current_window_handle #팝업창 생성전의 창
    print("메인창:",driver.title, main_page)
    # #주소찾기 버튼클릭
    # driver.find_element(By.XPATH, '//*[@id="item_form"]/section[1]/div/div/div[2]/div[1]/button').click() 
    handles = driver.window_handles #팝업창을 닫기 전
    print(handles)
    driver.switch_to.window(handles[-1])
    print("현재창 활성화된 창" ,driver.title, driver.current_window_handle)
    # region_name = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="region_name"]')))
    # region_name.send_keys("나상권공인중개사사무소")
    # driver.find_element(By.XPATH, '//*[@id="region_name"]"]').send_keys("ENTER")

    # iframe 내부로 전환
    driver.switch_to.frame('__daum__viewerFrame_1')
    # iframe = WebDriverWait(driver, 10).until(
    #     EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//*[@id="__daum__viewerFrame_1"]'))
    # )
    
    # 텍스트 입력
    input_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="region_name"]')))
    input_box.send_keys(total_location)
    input_box.send_keys(Keys.ENTER)
    
    driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/ul/li/dl/dd[2]/span/button[1]/span[1]').click() #검색된 첫번째 지번주소 클릭
    driver.switch_to.window(handles[0])
    
    print("팝업창 닫히고 활성화된 창" ,driver.title, driver.current_window_handle)
    
    

    # # iframe에서 기본 상태로 전환
    # driver.switch_to.default_content()


    # if 지정태그('기본정보', '동 / 호', 'text', 2): 지정태그('기본정보', '동 / 호', 'text', 2).send_keys('4392')
    # if 지정태그('기본정보', '거래유형 / 가격', 'radio', 1): 지정태그('기본정보', '거래유형 / 가격', 'radio', 1).click()
    # if 지정태그('기본정보', '동 / 호', 'checkbox', 1): 지정태그('기본정보', '동 / 호', 'checkbox', 1).click()
    # if 지정태그('기본정보', '주실 방향', 'radio', 2): 지정태그('기본정보', '주실 방향', 'radio', 2).click()
    # if 지정태그('기본정보', '동 / 호', 'checkbox', 1): 지정태그('기본정보', '주실 방향', 'select', 1).click()
    # 지정선택('기본정보', '주실 방향', 1, '남서')
    # 상세설정하기 = 지정태그('추가정보', '관리비 부과 방식', 'a', 1)
    # if 상세설정하기:
    #     상세설정하기.click()

    #     main_page = driver.current_window_handle #팝업창 생성전의 창
    #     print("메인창:",driver.title, main_page)

    #     handles = driver.window_handles #팝업창을 닫기 전
    #     print(handles)
    #     driver.switch_to.window(handles[-1])
    #     print("현재창 활성화된 창" ,driver.title, driver.current_window_handle)

    #     #일반(공용) 관리비 의뢰인미제공 선택
    #     driver.find_element(By.XPATH, '//*[@id="react-modal"]/div[3]/div/div[2]/div[3]/div/div[2]/div/div[1]/label[3]/span/text()').click()
    #     print("재정의된mlist_arr:", 재정의된mlist_arr)
    #     관리비상세지정태그('정액관리비', '사용료', tag_type, 몇번째)
        
    #     pyautogui.alert("저장시작!!")
    #     #관리비 상세 설정하기 저장하기
    #     driver.find_element(By.XPATH, '//*[@id="react-modal"]/div[3]/div/div[2]/div[8]/div/button').click()
    #     pyautogui.alert("저장종료!!")

    #     # iframe 내부로 전환
    #     driver.switch_to.frame('__daum__viewerFrame_1')
    #     # iframe = WebDriverWait(driver, 10).until(
    #     #     EC.frame_to_be_available_and_switch_to_it((By.XPATH, '//*[@id="__daum__viewerFrame_1"]'))
    #     # )
    # pyautogui.alert("함수종료!!")

    time.sleep(1) 
    print(f"건물종류:{building_purpose}") #건물종류
    if '단독주택' in building_purpose:
        if 지정태그('기본정보', '건물 종류', 'radio', 1): 지정태그('기본정보', '건물 종류', 'radio', 1).click()
        # driver.find_element(By.XPATH, '//*[@id="item_form"]/section[2]/div/div[1]/div[2]/div/div[1]/div/label[1]/span').click() #단독주택 클릭
    else:
        if 지정태그('기본정보', '건물 종류', 'radio', 2): 지정태그('기본정보', '건물 종류', 'radio', 2).click()
        # driver.find_element(By.XPATH, '//*[@id="item_form"]/section[2]/div/div[1]/div[2]/div/div[1]/div/label[2]/span').click() #그외 클릭
        driver.find_element(By.XPATH, '//*[@id="item_form"]/section[2]/div/div[1]/div[2]/div/div[2]/div/input').send_keys(building_purpose) # 건축물용도 직접입력
    
    print(f"거래유형/가격:보증금{building_purpose}, 월세{obinfo_rent1}, 관리비({manager})") #거래유형/가격
    # pyautogui.alert("obinfo_deposit1:"+obinfo_deposit1+" obinfo_rent1:"+obinfo_rent1)
    if obinfo_deposit1 != '' :
        if obinfo_rent1 != '' and obinfo_rent1 != '0':
            if int(room_rcount) < 2:
                if 지정태그('기본정보', '거래유형 / 가격', 'radio', 2): 지정태그('기본정보', '거래유형 / 가격', 'radio', 2).click()
            else:
                if 지정태그('기본정보', '거래유형 / 가격', 'radio', 2): 지정태그('기본정보', '거래유형 / 가격', 'radio', 3).click()        
            # driver.find_element(By.XPATH, '//*[@id="item_form"]/section[2]/div/div[2]/div[2]/div[1]/div[1]/div/label[2]/span').click() #월세 클릭
            if 지정태그('기본정보', '거래유형 / 가격', 'text', 1): 지정태그('기본정보', '거래유형 / 가격', 'text', 1).send_keys(obinfo_deposit1)
            # driver.find_element(By.XPATH, '//*[@id="item_form"]/section[2]/div/div[2]/div[2]/div[1]/div[2]/div/div[1]/div/input').send_keys(obinfo_deposit1) #보증금 입력
            
            #관리비별도이고 관리비가 10만원이상일 경우 관리비를 9만원으로 맞추고 나머지를 월세로 입력
            # pyautogui.alert("manager:"+manager+" mmoney:"+mmoney)
            if manager == '별도' and float(mmoney) >= 10:
                obinfo_rent1 = int(obinfo_rent1) + int(mmoney) -9
                mmoney = '9'
                # pyautogui.alert("관리비가 10만원이상 별도입니다. manager:"+manager+" mmoney:"+mmoney+" obinfo_rent1:"+str(obinfo_rent1))
            driver.find_element(By.XPATH, '//*[@id="item_form"]/section[2]/div/div[2]/div[2]/div[1]/div[3]/div/div[1]/div/input').send_keys(obinfo_rent1) #월세 입력
            if int(request_term1) < 12:
                driver.find_element(By.XPATH, '//*[@id="item_form"]/section[2]/div/div[2]/div[2]/div[3]/label/input').click() #단기매물 체크박스 클릭
                print("계약기간 "+request_term1+"개월의 단기매물입니다.")
        else:
            if int(room_rcount) < 2:
                if 지정태그('기본정보', '거래유형 / 가격', 'radio', 2): 지정태그('기본정보', '거래유형 / 가격', 'radio', 1).click()
            else:
                if 지정태그('기본정보', '거래유형 / 가격', 'radio', 2): 지정태그('기본정보', '거래유형 / 가격', 'radio', 2).click()              
            # driver.find_element(By.XPATH, '//*[@id="item_form"]/section[2]/div/div[2]/div[2]/div[1]/div[1]/div/label[1]/span').click() #전세 클릭
            if 지정태그('기본정보', '거래유형 / 가격', 'text', 1): 지정태그('기본정보', '거래유형 / 가격', 'text', 1).send_keys(obinfo_deposit1)
            # driver.find_element(By.XPATH, '//*[@id="item_form"]/section[2]/div/div[2]/div[2]/div[1]/div[2]/div/div[1]/div/input').send_keys(obinfo_deposit1) #보증금 입력
                
    print(f"동 / 호 (brtit_dongNm:{brtit_dongNm} room_num:{room_num})") #동/호
    # pyautogui.alert("go??")
    #brtit_dongNm 값이 '동'으로 끝나지 않으면 '동구분이 없음'체크
    if brtit_dongNm == '' or not brtit_dongNm.endswith('동'):
        지정태그('기본정보', '동 / 호', 'checkbox', 1).click()
    #room_num 값이 '호'로 끝나면 '호'를 제외한 나머지글자 입력
    if room_num != '' and room_num.endswith('호'):
        room_num_value = room_num.replace('호','')
        if 지정태그('기본정보', '동 / 호', 'text', 2): 지정태그('기본정보', '동 / 호', 'text', 2).send_keys(room_num_value)
        # driver.find_element(By.XPATH, '//*[@id="item_form"]/section[2]/div/div[3]/div/div[2]/div[1]/div[2]/div/div/input').send_keys(room_num_value)
    
    # pyautogui.alert("go??")
    print(f"층 / 구조 (total_floor:{total_floor}, room_floor:{room_floor})") #층/구조
    selectOption('//*[@id="item_form"]/section[2]/div/div[4]/div[1]/div[2]/div[1]/div[1]/div/div/div/select', total_floor) #전체층 선택
    selectOption('//*[@id="item_form"]/section[2]/div/div[4]/div[1]/div[2]/div[1]/div[2]/div/div/div/select', room_floor) #해당층 선택
    if float(room_rcount) >= 1 and float(room_rcount) < 2:
        print('원룸매물 room_rcount:' + room_rcount)
        if '오픈형' in room_important:
            선택할원룸층구조 = '오픈형 원룸(방1)'
        elif '복층형' in room_important:
            선택할원룸층구조 = '복층형 원룸'
        else:
            선택할원룸층구조 = '분리형 원룸(방1, 거실1)'
        print('선택할원룸층구조:' + 선택할원룸층구조)
        selectOption('//*[@id="item_form"]/section[2]/div/div[4]/div[2]/div/div[1]/div/div/div/div/select', 선택할원룸층구조) #층구조 선택
        
    print(f"전용면적 (room_area1:{room_area1})") #전용면적
    if room_area1 != '' : 
        room_area = room_area1
        # driver.find_element(By.XPATH, '//*[@id="item_form"]/section[2]/div/div[5]/div[2]/div[1]/div[2]/div/div/input').send_keys(room_area1)
    else:
        #방개수에 따른 초기값
        if float(room_rcount) == 1:
            room_area = 20
        elif float(room_rcount) < 2:
            room_area = 30
        elif float(room_rcount) >= 2 and float(room_rcount) < 3:
            room_area = 45
        else:
            room_area = 60
    # driver.find_element(By.XPATH, '//*[@id="item_form"]/section[2]/div/div[5]/div[2]/div[1]/div[1]/div/div/input').send_keys(room_area)
    지정태그('기본정보', '전용면적', 'text', 2).send_keys(room_area)
    print(f"주실 방향 (r_direction:{r_direction}, room_direction:{room_direction})") #주실방향
    # pyautogui.alert("test ㄱㄱ")
    선택할주실방향기준 = (r_direction+' 기준') if r_direction != '주출입문' else r_direction
    라디오박스_선택하기(driver, '주실 방향', 선택할주실방향기준)
    지정선택('기본정보', '주실 방향', 1, room_direction)
    
    # if room_direction != '선택' : selectOption('//*[@id="item_form"]/section[2]/div/div[6]/div[2]/div/div[1]/div/select', room_direction)
    print(f"화장실 수 (room_bcount:{room_bcount})") #화장실수
    if room_bcount != '' : 지정선택('기본정보', '화장실 수', 1, room_bcount)
    print(f"사용승인일 (building_usedate:{str(building_usedate)})") #사용승인일
    지정태그('기본정보', '사용승인일', 'text', 1).send_keys(building_usedate)
    #사진

    # class_element = driver.find_element(By.CSS_SELECTOR, '#item_form > section:nth-child(10) > div > div:nth-child(2) > div:nth-child(2)')
    # class_name = class_element.get_attribute("class") #item_form > section:nth-child(10) > div > div:nth-child(2) > div.sc-csuQGl.hdlHHX
    # pyautogui.alert('경로확인?'+f'#item_form > section:nth-child(10) > div > div:nth-child(2) > div.{class_name} > div > div:nth-child(1) > div')
    
    print(f"주차 (building_parking:{building_parking})") #주차
    print(f"주차대수 (building_pn:{building_pn})")
    
    if building_parking == '있음' : 
        지정태그('추가정보', '주차', 'radio', 1).click()
        지정태그('추가정보', '주차', 'text', 1).send_keys(building_pn)
        # if building_purpose == '단독주택':
        #     #일반건물 #item_form > section:nth-child(10) > div > div:nth-child(2) > div.sc-csuQGl.hdlHHX > div > div:nth-child(1) > div
        #     clickLabel('#item_form > section:nth-child(10) > div > div:nth-child(2) > div:nth-child(2) > div > div:nth-child(1) > div', '가능')
        #     # clickLabel(f'#item_form > section:nth-child(10) > div > div:nth-child(2) > div.{class_name} > div > div:nth-child(1) > div', '가능')
        # else:  
        #     #집합건물
        #     clickLabel('#item_form > section:nth-child(10) > div > div:nth-child(1) > div:nth-child(2) > div > div:nth-child(1) > div', '가능')
    else:
        print(f"주차대수 (building_pn:{building_pn})")
    # pyautogui.alert('주차 확인?')        


    print(f"엘리베이터") #엘리베이터
    if '엘리베이터' in building_option:
        print("건물옵션에 엘리베이터 포함, building_option:"+building_option)
        # 라디오박스_선택하기(driver, '엘리베이터', '있음')
        if 지정태그('추가정보', '엘리베이터', 'radio', 1): 지정태그('추가정보', '엘리베이터', 'radio', 1).click()
        # driver.find_element(By.CSS_SELECTOR, '#item_form > section:nth-child(10) > div > div:nth-child(n) > div.sc-csuQGl.hdlHHX > div > label:nth-child(1)').click()
    else:
        # 라디오박스_선택하기(driver, '엘리베이터', '없음')
        if 지정태그('추가정보', '엘리베이터', 'radio', 2): 지정태그('추가정보', '엘리베이터', 'radio', 2).click()
        # driver.find_element(By.CSS_SELECTOR, '#item_form > section:nth-child(10) > div > div:nth-child(n) > div.sc-csuQGl.hdlHHX > div > label:nth-child(2)').click()
 
    print(f"관리비(manager):{mmoney}") #관리비
    # pyautogui.alert('manager:'+manager+' mmoney:'+mmoney)
    if manager == '별도': #item_form > section:nth-child(10) > div > div:nth-child(4) > div.sc-csuQGl.hdlHHX > div:nth-child(1) > div.sc-jTzLTM.kPElNT > div > input
        if 지정태그('추가정보', '관리비', 'text', 1): 지정태그('추가정보', '관리비', 'text', 1).send_keys(mmoney)
        # driver.find_element(By.CSS_SELECTOR, '#item_form > section:nth-child(10) > div > div:nth-child(n) > div.sc-csuQGl.hdlHHX > div.sc-kEYyzF.gjnHms > div > input').send_keys(mmoney)
        # #주거용이면서 관리비 10만원이상일 경우 관리비상세설정
        # if object_type =='주거용' and  float(mmoney) > 10:
        #     지정태그('추가정보', '관리비 부과 방식', 'a', 1).click()
                  
    elif manager == '없음':
        print("관리비없음 체크")
        if 지정태그('추가정보', '관리비', 'checkbox', 1): 지정태그('추가정보', '관리비', 'checkbox', 1).click()
        # driver.find_element(By.CSS_SELECTOR, '#item_form > section:nth-child(10) > div > div:nth-child(n) > div.sc-csuQGl.hdlHHX > label:nth-child(2) > input[type=checkbox]').click()
    elif manager == '': 
        print("관리비확인불가 체크")  
        if 지정태그('추가정보', '관리비', 'checkbox', 1): 지정태그('추가정보', '관리비', 'checkbox', 1).click()
        # driver.find_element(By.CSS_SELECTOR, '#item_form > section:nth-child(10) > div > div:nth-child(n) > div.sc-csuQGl.hdlHHX > label:nth-child(3) > input[type=checkbox]').click()  
    
    
    def 배열값체크하기(driver, 기준div텍스트, 체크할항목들의배열):
        try:
            # 인자(기준div텍스트)를 텍스트로 가지는 div요소 찾기
            기준div = driver.find_element(By.XPATH, f"//*[contains(text(), '{기준div텍스트}')]")
            
            # '기준div'요소의 상위div를 기준으로 봤을 때 '기준div'가 안에 있는 첫번째 div라고 하면 두번째 div요소 안에 label요소들을 찾아서 갯수를 확인
            # '기준div'요소의 상위div를 기준으로 봤을 때 '기준div'가 안에 있는 첫번째 div인지 확인
            # (주의: 이 코드는 모든 경우에 적합하지 않을 수 있습니다. HTML 구조에 따라 조정이 필요할 수 있습니다.)
            부모_div = 기준div.find_element(By.XPATH, "./..")
            sibling_divs = 부모_div.find_elements(By.XPATH, ".//div")
            if 기준div in sibling_divs:
                # '기준div'가 안에 있는 첫번째 div라면, 두번째 div요소 안에 label요소들을 찾아서 갯수를 확인
                두번째_div = sibling_divs[1]
                label_elements = 두번째_div.find_elements(By.TAG_NAME, "label")
                #라벨요소 안에 있는 span태그들의 텍스트 확인
                for label in label_elements:
                    span = label.find_element(By.TAG_NAME, "span")
                    label_text = span.text
                    if label_text in 체크할항목들의배열:
                        print(f"'{label_text}' 항목은 포함내역입니다.")
                        label.click()     
                    else:
                        print(f"'{label_text}' 항목을 포함내역이 아닙니다.")                      
        except Exception as e:
            print(f"기준이 되는 요소를 찾을 수 없습니다: {e}")
            pyautogui.alert(f"기준이 되는 요소를 찾을 수 없습니다: {e}")

    배열값체크하기(driver, "관리비", 재정의된mlist_arr)
    
    if float(room_rcount) < 2:
        print("room_option:", room_option)
        print(f"옵션 (room_option):{room_option}") #옵션
        # pyautogui.alert('room_option:'+room_option)
        room_option_arr = room_option.split(",")
        배열값체크하기(driver, "옵션", room_option_arr)
    

    
    today = date.today() # 현재 날짜 얻기
    rdate_day = datetime.strptime(rdate, "%Y-%m-%d").date()
    # pyautogui.alert(rdate)
    
    print(f"입주가능일:{str(rdate_day)}") #입주가능일
    if building_purpose == '단독주택':
        if  manager == '별도': #월세일 경우
            # rdate와 오늘 날짜 비교
            if rdate_day > today:
                print("rdate는 오늘 이후의 날짜입니다.")
                # driver.find_element(By.CSS_SELECTOR, '#item_form > section:nth-child(10) > div > div:nth-child(7) > div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > div > div > div > label > span').click() #날짜선택클릭
                # # 변수 rdate_day의 값을 가져와서 input 태그의 value 속성으로 설정
                # change_day = "2023. 06. 06 이후"  # 임의의 날짜 값
                # input_element = driver.find_element(By.CSS_SELECTOR, '#item_form > section:nth-child(10) > div > div:nth-child(7) > div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > div.react-datepicker-wrapper > div > div > label > input[type=radio]')
                # driver.execute_script("arguments[0].value = arguments[1];", input_element, change_day)        
            else:
                print("rdate는 오늘 이전의 날짜입니다.")   
                driver.find_element(By.CSS_SELECTOR, '#item_form > section:nth-child(10) > div > div:nth-child(n) > div.sc-csuQGl.hdlHHX > div.sc-bXGyLb.bbxnlt.sc-fBuWsC.kZkbqL > div:nth-child(1) > div > label').click() #즉시입주 클릭
        else:
            if rdate_day > today:
                print("rdate는 오늘 이후의 날짜입니다.")    
            else:
                print("rdate는 오늘 이전의 날짜입니다.")   
                driver.find_element(By.CSS_SELECTOR, '#item_form > section:nth-child(10) > div > div:nth-child(n) > div.sc-csuQGl.hdlHHX > div.sc-bXGyLb.bbxnlt.sc-fBuWsC.kZkbqL > div:nth-child(1) > div > label').click() #즉시입주 클릭
            
            
    else:   
        if  manager == '별도':
            if rdate_day > today:
                print("rdate는 오늘 이후의 날짜입니다.")    
            else:
                print("rdate는 오늘 이전의 날짜입니다.")
                #JavaScript를 사용한 클릭
                element = driver.find_element(By.CSS_SELECTOR, 'div:nth-child(2) label input[value="즉시 입주"]')
                driver.execute_script("arguments[0].click();", element)
        else:
            if rdate_day > today:
                print("rdate는 오늘 이후의 날짜입니다.")    
            else:
                print("관리비별도 아닐때 rdate는 오늘 이전의 날짜입니다.")
                #JavaScript를 사용한 클릭
                element = driver.find_element(By.CSS_SELECTOR, 'div:nth-child(2) label input[value="즉시 입주"]')
                driver.execute_script("arguments[0].click();", element)
              
        
    
    
    
    #설명
    
    #상세설명
    
    print(f"비밀메모(선택입력):{room_num}") #비밀메모
    driver.find_element(By.XPATH, '//*[@id="item_form"]/section[5]/div/div[3]/div[2]/div/textarea').send_keys(secret_memo)
    
    print(f"관심태그:{room_num}") #관심태그
    지정선택('등록정보', '관심 태그', 1, zigbang_tag)
    # selectOption('//*[@id="item_form"]/section[6]/div[1]/div[1]/div[2]/div[1]/div/div/select', zigbang_tag) #  담당자 태그선택
    
    #중개의뢰를 받은 방법
    driver.find_element(By.XPATH, '//*[@id="item_form"]/section[6]/div[2]/div[1]/div[1]/div[1]/div/label[1]/span').click()
    
    #동의체크
    driver.find_element(By.XPATH, '//*[@id="item_form"]/section[6]/div[3]/label/input').click()
    
    
    #물건사진 폴더열기
    main_dir = 'Z:\\업무자료\\4사진자료&이미지자료(외부유출금지)\\1주거용물건, 상업용물건\\'
    path_dir = main_dir + data['folderPath'] #'경기도\\오산시\\궐동\\654-9\\썬플라워\\1층\\1층'
    print(path_dir)
    try:
        os.startfile(path_dir)
    except Exception as e:
        print('폴더열기 에러', str(e))
  
    pyautogui.alert('직방 매물등록을 마치셨습니까?')
    driver.quit()