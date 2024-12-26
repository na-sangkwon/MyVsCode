import requests
from bs4 import BeautifulSoup

# # 웹 페이지의 URL
# url = 'https://new.land.naver.com/offices?ms=37.1492562,127.0632774,15&a=SG:SMS&e=RETAIL'

# # HTTP GET 요청을 보내고 응답을 받음
# response = requests.get(url)

# # BeautifulSoup을 사용하여 HTML 파싱
# soup = BeautifulSoup(response.text, 'lxml')

# # XPath로 원하는 요소들 선택
# elements = soup.find_all('//*[@id="listContents1"]/div/div/div[1]/div[1]/div/div[1]/div/span[2]/a')

# # 선택된 요소들의 텍스트 출력
# for element in elements:
#     print(element['href'])

import requests
from bs4 import BeautifulSoup
# import urllib.request as req

# 크롤링할 페이지 URL
url = "https://new.land.naver.com/offices?ms=37.1495298,127.0732124,15&a=SG:SMS&e=RETAIL&h=85&i=567&u=ONEFLOOR"

# 페이지의 HTML 가져오기
response = requests.get(url)
html = response.text

# BeautifulSoup를 사용하여 HTML 파싱
soup = BeautifulSoup(html, "html.parser")
print(soup)
# 매물 목록 요소 찾기
# articles = soup.select("#listContents1 > div > div > div:nth-child(1) > div:nth-child(1) > div > div.cp_area")
offices = soup.find_all(class_="cp_area")
# print(offices)

# # 각 매물 정보 출력
# for article in articles:
#     # 매물 정보에서 필요한 데이터 추출
#     title = article.select_one(".inner_list .item_title").text.strip()
#     price = article.select_one(".inner_list .price").text.strip()
#     address = article.select_one(".inner_list .location").text.strip()

#     # 추출한 데이터 출력
#     print("매물 제목:", title)
#     print("가격:", price)
#     print("주소:", address)
#     print("-------------------")


input()