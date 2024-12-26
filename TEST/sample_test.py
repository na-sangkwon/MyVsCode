from selenium import webdriver
from selenium.webdriver import ActionChains

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options

import pyautogui 
import pymysql
from datetime import datetime, timedelta

options = Options()

options.add_argument("--disable-blink-features=AutomationControlled")
# ChromeDriver 경로 설정
driver = webdriver.Chrome(options=options)



# URL 열기
driver.maximize_window()
driver.get('https://www.serve.co.kr/member/login')
driver.find_element(By.XPATH, '//*[@id="input-1"]').send_keys("osanbang6666")
driver.find_element(By.XPATH, '//*[@id="input-3"]').send_keys("dhqkd5555%")
driver.find_element(By.XPATH, '//*[@id="app"]/div/div/div/div/div[2]/div[4]/button').click()


WebDriverWait(driver, 10).until(
    EC.text_to_be_present_in_element(
        (By.XPATH, '//*[@id="app"]/div/div/header/div/div[2]/button[1]/span[3]/span[2]'), 
        "나상권공인중개사사무소"
    )
)

# driver.get('https://ma.serve.co.kr/good/articleRegistManage/') #신규등록페이지

# try:
#     label_xpath = '//label[text()="확인 매물 등록 시 주의사항을 확인하였습니다."]'
    
#     # 라벨 클릭 대기
#     label_element = WebDriverWait(driver, 20).until(
#         EC.presence_of_element_located((By.XPATH, label_xpath))
#     )
#     label_element.click()
#     print("라벨을 클릭하여 체크박스를 선택했습니다.")
# except Exception as e:
#     print(f"라벨 클릭 중 오류 발생: {e}")
  

# pyautogui.alert("계속 하시겠습니까?")

admin_id = "상가팀원"
object_code_new = "523482"
써브매물번호 = "317868453"
광고상태 = "광고종료"
ad_memo = ""
현재날짜시간 = datetime.now()
현재날짜 = 현재날짜시간.date()
# 문자형으로 변환
current_date = 현재날짜시간.strftime("%Y-%m-%d")  # 'YYYY-MM-DD' 형식
current_time = 현재날짜시간.strftime("%H:%M:%S")  # 'HH:MM:SS' 형식    

driver.get(f'https://ma.serve.co.kr/good/articleTrsmDetail?atclNo={써브매물번호}') #등록완료페이지


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

    # 매물번호를 저장할 변수 초기화
    네이버매물번호 = ""
    써브매물번호 = ""
    # KB매물번호 = ""
    alert_message = ""

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

    # pyautogui.alert("계속 하시겠습니까?")

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
        pyautogui.alert(f"existing_record:\n{existing_record}")
        # pyautogui.alert(f"실행될 쿼리문(check_query):\n{check_query}")
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
                pyautogui.alert(f"실행될 쿼리문:\n{query_preview}")
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
                    # conn.commit()
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


pyautogui.alert(f"작업완료")



driver.get('https://ma.serve.co.kr/good/articleTrsmDetail?atclNo=317711995') #등록완료페이지

# 매물번호를 저장할 변수 초기화
네이버매물번호 = ""
써브매물번호 = ""
KB매물번호 = ""
alert_message = ""
광고상태 = "광고중"

try:


    # XPath 지정
    sources = {
        "써브": '//div[@class="t-btn-item" and @title="써브"]//span[@data-v-2e0e3870 and text()]',
        "네이버": '//div[@class="t-btn-item" and @title="네이버"]//span[@class="v-btn__content"]/span',
        "KB부동산": '//div[@class="t-btn-item" and @title="KB부동산"]//span[@class="v-btn__content"]/span',
    }

    # 각 매물번호를 찾아서 변수에 저장
    for source_name, xpath in sources.items():
        try:
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            if source_name == "네이버":
                네이버매물번호 = element.text
            elif source_name == "써브":
                써브매물번호 = element.text
            elif source_name == "KB부동산":
                KB매물번호 = element.text
        except Exception as e:
            # 매물번호를 찾을 수 없는 경우 변수에 기본값 저장
            if source_name == "네이버":
                네이버매물번호 = "찾을 수 없음"
            elif source_name == "써브":
                써브매물번호 = "찾을 수 없음"
            elif source_name == "KB부동산":
                KB매물번호 = "찾을 수 없음"


    # 결과 출력 (확인을 위해)
    print(f"네이버매물번호: {네이버매물번호}")
    print(f"써브매물번호: {써브매물번호}")
    print(f"KB매물번호: {KB매물번호}")


    # DB 연결
    conn = pymysql.connect(host='obangkr.cafe24.com', user='obangkr', password='Ddhqkd!1', charset='utf8')

    # 현재 날짜와 시간 가져오기
    current_date = datetime.now().strftime("%Y-%m-%d")  # 'YYYY-MM-DD' 형식
    current_time = datetime.now().strftime("%H:%M:%S")  # 'HH:MM:SS' 형식
    # 광고 시작일과 종료일 계산
    ad_start, ad_end = get_ad_dates()   

    # 변수 확인
    print(f"INSERT 쿼리에 사용될 변수:")
    print(f"담당자 아이디 (admin_id): {admin_id}")
    print(f"새홈 매물번호 (object_code_new): {object_code_new}")
    print(f"광고 사이트 (ad_site): 네이버")
    print(f"네이버 매물번호 (ad_code): {네이버매물번호}")
    print(f"날짜 (ad_udate): {current_date}")
    print(f"시간 (ad_utime): {current_time}")
    print(f"숨김 코드 (hidden_code): {써브매물번호}")

    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
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
            # 기존 매물번호와 새 매물번호 비교
            current_ad_code = existing_record['ad_code']
            print(f"기존 매물번호 (ad_code): {current_ad_code}")
            print(f"새 매물번호 (네이버매물번호): {네이버매물번호}")    
            # ad_memo 값 처리
            existing_ad_memo = existing_record.get('ad_memo', '')  # 기존 ad_memo 값 가져오기
            new_ad_memo_part = f"써브:{써브매물번호}, KB부동산:{KB매물번호}"  # 추가할 값
            if existing_ad_memo:
                # 기존 값이 있으면 쉼표로 연결
                new_ad_memo = f"{existing_ad_memo}, {new_ad_memo_part}"
            else:
                # 기존 값이 없으면 새 값만 추가
                new_ad_memo = new_ad_memo_part                
            # 변수 확인
            print(f"UPDATE 쿼리에 사용될 변수:")
            print(f"ad_memo 업데이트 값: {new_ad_memo}") 

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
                query_params = [네이버매물번호, current_date, current_time, new_ad_memo]

                # 광고중이 아닌 경우 시작일과 종료일 파라미터 추가
                if 광고상태 != "광고중":
                    query_params.extend([ad_start, ad_end])
                # WHERE 절에 사용할 파라미터 추가
                query_params.extend([admin_id, object_code_new])
                


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
                pyautogui.alert(f"실행될 쿼리문:\n{query_preview}")
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
            # 광고 정보가 없는 경우 추가 작업 수행
            insert_query = """
                INSERT INTO pr_externalad (
                    admin_id, object_code_new, ad_start, ad_end, ad_site, ad_code, ad_udate, ad_utime, ad_memo, ad_wdate, ad_wtime
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """


            # ad_memo 구성
            ad_memo = f"써브:{써브매물번호}, KB부동산:{KB매물번호}"

            print(f"ad_memo 업데이트 값: {ad_memo}")

            # 알림창으로 쿼리 확인
            query_preview = f"""
            INSERT INTO pr_externalad (
                admin_id, object_code_new, ad_start, ad_end, ad_site, ad_code, ad_udate, ad_utime, ad_memo
            ) VALUES (
                '{admin_id}', '{object_code_new}', '{ad_start}', '{ad_end}', '네이버', '{네이버매물번호}', '{current_date}', '{current_time}', '{ad_memo}'
            );
            """
            pyautogui.alert(f"실행될 쿼리문:\n{query_preview}")

            try:
                # 쿼리 실행
                cursor.execute(insert_query, (
                    admin_id, object_code_new, ad_start, ad_end, '네이버', 네이버매물번호, current_date, current_time, ad_memo, current_date, current_time
                ))
                if admin_id and object_code_new and 네이버매물번호 and 써브매물번호 :
                    conn.commit()
                    alert_message = f"새 네이버 광고 매물이 추가되었습니다.\n\n부동산써브: {써브매물번호}\n네이버부동산: {네이버매물번호}\nKB부동산: {KB매물번호}"
            except Exception as e:
                alert_message = f"추가 작업 중 오류가 발생했습니다: {e}"

        # 알림창으로 결과 표시
        if alert_message : 
            print(alert_message)
            pyautogui.alert(alert_message)

    except Exception as e:
        pyautogui.alert(f"오류 발생: {e}")
    finally:
        conn.close()
except Exception as e:
    pyautogui.alert(f"오류 발생: {e}", "오류")

finally:
    driver.quit()

# driver.find_element(By.XPATH, '//*[@id="login_form"]/div[1]/div/input').send_keys("nasangkwon@outlook.kr")
# driver.find_element(By.XPATH, '//*[@id="login_form"]/div[2]/div/input').send_keys("tkdrnjs2@")
# driver.find_element(By.XPATH, '//*[@id="login_form"]/div[3]/button').click()

# # 로그인확인겸 첫 파란등록버튼 기다리기(관리자로 로그인시)
# driver.implicitly_wait(10)
# WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/div[1]/div/ul/li[3]/a'))).click()
# driver.find_element(By.XPATH, '//*[@id="menu-product-1"]/a').click()

# # 확인후 이동
# driver.get('https://osanbang.com/adminproduct/add?category_id')

# driver.find_element(By.ID, 'category_16').click() #매물 종류
# # 거래종류
# for a in driver.find_elements(By.XPATH, '//*[@id="product_form"]/div[1]/div[2]/div[2]/div[3]/div[2]/div/div'):
#     print(a.text) 
#     if a.text == '전세': 
#         a.click()

# if driver.find_element(By.XPATH, '//*[@id="full_price_area"]').is_displayed():
#     print("참입니다.")
# else:
#     print("거짓입니다.")


input()
# time.sleep(20)




