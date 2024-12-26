
import tkinter as tk
from tkinter import messagebox
import datetime
import pyautogui 
# 메시지 박스를 호출하는 함수
def popup_message(complete_count, update_ok, end_ok):
    # messagebox.showinfo("알림", f"{complete_count}개의 매물을 업데이트 하였습니다.")
    response = messagebox.askyesno("알림", f"{complete_count}개의 매물을 업데이트 하였습니다.\n(업데이트:{update_ok} , 거래완료:{end_ok}) \n 계속진행하시겠습니까?")

    # tkinter 윈도우 생성
    root = tk.Tk()
    print('팝업생성')

    # 메시지 창 닫기
    root.destroy()
    return response
    # # 윈도우 실행
    # root.mainloop()

def process_wait(hour):
    

    # 경과될 시간 계산
    now = datetime.datetime.now()
    end_time = now + datetime.timedelta(hours=hour)

    # GUI 설정
    root = tk.Tk()
    root.title("실시간 남은 시간")
    root.geometry("500x150")

    # 남은 시간 표시 라벨
    remaining_time_label = tk.Label(root, text="", font=("Helvetica", 20))
    remaining_time_label.pack(pady=20)

    # 멈춤 버튼
    stop_button = tk.Button(root, text="멈춤", font=("Helvetica", 14), command=root.destroy)
    stop_button.pack(pady=10)

    # 실시간으로 남은 시간 업데이트
    def update_remaining_time():
        remaining_time = end_time - datetime.datetime.now()
        remaining_time_str = str(remaining_time).split('.')[0]  # 소수점 이하 제거
        remaining_time_label.configure(text=f"업데이트 개시까지 {remaining_time_str} 남았습니다.")
        if remaining_time.total_seconds() > 0:
            root.after(1000, update_remaining_time)  # 1초마다 업데이트
        else:
            # messagebox.showinfo("시간 종료", f"{hour}시간이 경과되었습니다.")
            root.destroy()
            update_start()

    # 실시간으로 남은 시간 업데이트 시작
    update_remaining_time()

    # Tkinter 루프 시작
    root.mainloop()


# pyautogui.alert("오방매물 최신등록일을 업데이트 합니다.")

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.chrome.options import Options

# import chromedriver_autoinstaller

# chromedriver_autoinstaller.install()

options = Options()
options.add_argument("--disable-blink-features=AutomationControlled") #봇으로 인식안하게 하는 옵션

# admin_id = 'test@osanbang.com'
# admin_pw = '1234'
admin_id = "nasangkwon@outlook.kr"
admin_pw = 'tkdrnjs2@'

# driver = webdriver.Chrome('/chromedriver', options=options)
driver = webdriver.Chrome(options=options)

driver.implicitly_wait(10)
# URL 열기
driver.maximize_window()
driver.get('https://osanbang.com/adminlogin/index')

# WebDriverWait(driver, 30).until(EC.presence_of_element_located(
#     By.CSS_SELECTOR, "body > div.logo > a > img"
# ))

driver.find_element(By.XPATH, '//*[@id="login_form"]/div[1]/div/input').send_keys(admin_id)
driver.find_element(By.XPATH, '//*[@id="login_form"]/div[2]/div/input').send_keys(admin_pw)
driver.find_element(By.XPATH, '//*[@id="login_form"]/div[3]/button').click()

driver.implicitly_wait(10)
driver.find_element(By.CSS_SELECTOR, 'body > div.page-container > div.page-sidebar-wrapper > div > ul > li:nth-child(3) > a > span.title').click() #사이드바 매물 클릭
driver.find_element(By.CSS_SELECTOR, '#menu-product-1 > a').click() #매물->매물관리 클릭

# driver.get('https://osanbang.com/adminproduct/index')

#obang_data에서 가져온 obang_update에 포함된 obang_code를 업데이트 할 예정임
import obang_data
complete_count = 0
update_ok = 0
end_ok = 0
def update_start():
    import datetime
    global complete_count
    global update_ok
    global end_ok
    print(str(complete_count+1) + "번째 업데이트 시작: " + str(datetime.datetime.now()))

    #최신등록일 업데이트
    obang_update = obang_data.obang_update
    for update_code in obang_update:
        try:
            # WebDriverWait(driver, 10).until(EC.element_to_be_clickable(By.CSS_SELECTOR, "#search_id")).clear() #매물번호 입력창의 입력값 초기화
            driver.implicitly_wait(10)
            driver.find_element(By.CSS_SELECTOR, "#search_id").clear() 
            print(f"{update_code} 1.검색창 초기화")
            driver.find_element(By.CSS_SELECTOR, "#search_id").send_keys(update_code) #매물번호입력창에 매물번호 입력
            print("----- 2.매물번호입력창에 매물번호 입력")
            driver.find_element(By.CSS_SELECTOR, "#admin_member_id > option:nth-child(1)").click() #담당자를 직원별로 선택
            print("----- 3.담당자를 직원별로 선택")
            driver.find_element(By.CSS_SELECTOR, "#go_keyword").click() #검색버튼(돋보기) 클릭
            print("----- 4.검색버튼(돋보기) 클릭")
            # WebDriverWait(driver, 10).until(EC.presence_of_element_located(By.CSS_SELECTOR, "#tr_20052 > td:nth-child(14) > div:nth-child(1)"))
            # time.sleep(2)
            
            # 업데이트 전 등록일
            before_target = driver.find_element(By.CSS_SELECTOR, f"#tr_{update_code} > td:nth-child(15) > div").get_attribute('title').split(' ')[0]
            before_date = datetime.datetime.strptime(before_target , '%Y-%m-%d')
            today = datetime.datetime.today()
            print(f"{update_code} before_date: ", before_date)
            # print(f"{update_code} today: ", today)
            # if before_date == today:            

            # 오늘 날짜와 비교하여 출력
            if before_target == str(datetime.date.today()):
                print("----- 5.Today! pass")
            elif before_date > today:
                print("----- 5.Future Date! pass")
            else:
                #업데이트 실행
                print("----- 5.past Date! update")
                driver.find_element(By.CSS_SELECTOR, f'#tr_{update_code} > td:nth-child(14) > div:nth-child(1)').click() #관리 클릭
                print("----- 5-1.관리 클릭")
                # time.sleep(1)
                # WebDriverWait(driver, 10).until(EC.presence_of_element_located(By.CSS_SELECTOR, f"#tr_{update_code} > td:nth-child(14) > div:nth-child(1) > a")).click() #관리 클릭
                # WebDriverWait(driver, 10).until(EC.presence_of_element_located(By.CSS_SELECTOR, f"#tr_{update_code} > td:nth-child(14) > div.dropdown.open > ul > li:nth-child(7) > a")).click() #최신등록일로갱신 클릭
                driver.find_element(By.CSS_SELECTOR, f'#tr_{update_code} > td:nth-child(14) > div.dropdown.open > ul > li:nth-child(7)').click() #최신등록일로갱신 클릭
                print("----- 5-2.최신등록일로갱신 클릭")

                # driver.find_element(By.CSS_SELECTOR, "#search_id").send_keys("12345") #매물번호입력창에 매물번호 입력

                # days_diff = (today - before_date).days
                # if days_diff == 1:
                #     print("Yesterday!")
                # else:
                #     print(f"{days_diff} days ago")
                
                #거래완료 해제
                status_span = driver.find_elements(By.XPATH, f'//*[@id="tr_{update_code}"]/td[10]/span')
                # print(status_span.text)
                span_texts = []
                for span in status_span: span_texts.append(span.text)
                if "완료" in span_texts:
                    print("----- 6.완료라벨 표시중 -> 완료라벨 제거")

                    driver.execute_script(f"change('is_finished','{update_code}','0');")
                    try:
                        alert = WebDriverWait(driver, 0.2).until(EC.alert_is_present())
                        alert.accept()
                    except Exception as e:
                        print("alert오류", str(e))
                        pass  # alert 창이 없는 경우, 그냥 넘어갑니다.  
        
                else:
                    print("----- 6.완료라벨 없음")
                    pass
                update_ok += 1  
                complete_count += 1                

        except:
            # print(update_code,"업데이트 안됨")
            print(f"{update_code}업데이트 안됨")

    #거래완료 및 비공개처리
    print("거래완료 및 비공개처리 시작")
    obang_complete = obang_data.obang_complete
    print("obang_complete:", obang_complete)
    for complete_code in obang_complete:
        try:
            # WebDriverWait(driver, 10).until(EC.element_to_be_clickable(By.CSS_SELECTOR, "#search_id")).clear() #매물번호 입력창의 입력값 초기화
            driver.implicitly_wait(10)
            driver.find_element(By.CSS_SELECTOR, "#search_id").clear() 
            print(f"{update_code} 1.검색창 초기화")
            driver.find_element(By.CSS_SELECTOR, "#search_id").send_keys(complete_code) #매물번호입력창에 매물번호 입력
            print("----- 2.매물번호입력창에 매물번호 입력")
            driver.find_element(By.CSS_SELECTOR, "#admin_member_id > option:nth-child(1)").click() #담당자를 직원별로 선택
            print("----- 3.담당자를 직원별로 선택")
            driver.find_element(By.CSS_SELECTOR, "#go_keyword").click() #검색버튼(돋보기) 클릭
            print("----- 4.검색버튼(돋보기) 클릭")

            #비공개처리
            element = driver.find_element(By.XPATH, f'//*[@id="tr_{complete_code}"]/td[3]/div/label')
            driver.execute_script("arguments[0].setAttribute('class', 'btn btn-gray lock')", element)
            print("----- 5.비공개처리")
            
            #완료처리
            status_span = driver.find_elements(By.XPATH, f'//*[@id="tr_{complete_code}"]/td[10]/span')
            # print(status_span.text)
            span_texts = []
            for span in status_span: span_texts.append(span.text)
            if "완료" not in span_texts:
                driver.execute_script(f"change('is_finished','{complete_code}','1');")
                print("----- 6.완료라벨 미표시상태 -> 완료라벨 표시")
                
                try:
                    alert = WebDriverWait(driver, 0.2).until(EC.alert_is_present())
                    alert.accept()
                except Exception as e:
                    print("alert오류", str(e))
                    pass  # alert 창이 없는 경우, 그냥 넘어갑니다.                
            else:
                print("----- 6.완료라벨 표시상태")
                pass
            end_ok += 1
            complete_count += 1
            

        except Exception as e:
            print("오류:" , str(e))
            print(f"{complete_code}거래완료 안됨")
    
        
    if popup_message(complete_count, update_ok, end_ok):
        print(" 계속진행합니다.")
        process_wait(10) # 몇 시간뒤에 재작동할지 설정
        # update_start()
    else:
        print("멈춥니다")
        # 드라이버 종료
        driver.quit()


# driver.find_element(By.CSS_SELECTOR, "#search_id").send_keys(Keys.ENTER)

update_start()




# time.sleep(10)
# input()
