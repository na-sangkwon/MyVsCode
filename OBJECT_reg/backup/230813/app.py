#테스트용파일

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options

import pyautogui 
import time

options = Options()

options.add_argument("--disable-blink-features=AutomationControlled")

# ChromeDriver 경로 설정
driver = webdriver.Chrome('/chromedriver', options=options)

driver.maximize_window()

# driver.get('https://mobile.karhanbang.com/kren/mamul/list')
driver.get('https://osan-bns.com/admin_item/insert') #오부사 신규등록페이지

# driver.get('https://mobile.karhanbang.com/snsLogin/login')
driver.execute_script('return document.getElementById("realtorYn").click()') #개업공인중개사여부 체크
driver.find_element(By.XPATH, '//*[@id="userId"]').send_keys('bsleemanse')
driver.find_element(By.XPATH, '//*[@id="userPw"]').send_keys('tkdrnjs1001')
driver.find_element(By.XPATH, '//*[@id="loginBtn"]/a/span').click()

WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="in_search_so"]'))).click()
한방번호 = ''
options = driver.find_elements(By.XPATH, '//*[@id="in_search_so"]/option')
if 한방번호 != '':
    print('한방번호가 존재할때')
    choice = '한방매물번호'
else:
    print('한방번호가 존재하지 않을 때')
    choice = '본번-부번'
for opt in options:
    print(opt.text)
    if opt.text == choice: 
        opt.click()
        driver.find_element(By.XPATH, '//*[@id="in_keyword"]').send_keys('640-9')
        driver.find_element(By.XPATH, '//*[@id="mainSearchBtn"]').click()
        break

result = pyautogui.confirm('\n\n 매물등록을 진행하시겠습니까?', buttons=['예', '아니오'])    
if result == '예':
    driver.get('https://mobile.karhanbang.com/kren/mamul/regist')
    
pyautogui.alert("이상없습니까?") 
driver.quit()