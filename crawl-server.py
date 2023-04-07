import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os


app = Flask(__name__)
CORS(app)
load_dotenv()

# 네이버 검색 API 사용을 위한 API key
client_id = os.environ.get('CLIENT_ID')
client_secret = os.environ.get('CLIENT_SECRET')
naver_search_url = os.environ.get('NAVER_SEARCH_URL')

# Selenium으로 크롬 브라우저 열기
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')  # 화면 출력 안 함
chrome_options.add_argument('--disable-gpu')  # GPU 사용 안 함
chrome_options.add_argument('lang=ko_KR')  # 언어 설정, 안 하면 네이버 지도 검색이 안 될 수도 있음
driver = webdriver.Chrome(service_log_path=os.path.devnull, options=chrome_options)
driver.get("https://www.google.co.kr/?hl=ko")
    
@app.route('/<place_name>', methods=['GET'])
def search_map(place_name):
    try:
        # place_name을 url에서 사용할 수 있도록 인코딩
        encoded_place_name = requests.utils.quote(place_name)
        url = f"{naver_search_url}?query={encoded_place_name}&sm=hty&style=v5"
        # 검색 결과 페이지로 이동하고 로딩 기다리기
        # 로드가 완료될 때까지 기다림 (10초)
        driver.get(url)
        first_item = driver.find_element(By.XPATH, '//*[@id="ct"]/div[2]/ul/li[1]/div[1]/a/div')
        first_item.click()

        wait = WebDriverWait(driver, 5)
        # 현재 url이 변경될때까지 대기 최대 2초
        wait.until(EC.url_changes(driver.current_url))
        url = driver.current_url
        
        # 변경된 url을 통해 html 파싱
        placePage = requests.get(url)
        place_page_soup = BeautifulSoup(placePage.text, 'html.parser')
        # 평균 별점
        star_rating_element = place_page_soup.select_one('span.PXMot.LXIwF em')
        star_rating = star_rating_element.text if star_rating_element else None
        # 총 리뷰 수
        review_count_element = place_page_soup.select_one('a.place_bluelink em')
        review_count = review_count_element.text if review_count_element else None
        
        # 위에서 나온 url을 통해서 리뷰 url로 변경
        review_url = url.replace('/home', '/review/visitor')
        review_page = requests.get(review_url)
        review_page.encoding = 'utf-8' # 인코딩 설정
        review_page_soup = BeautifulSoup(review_page.text, 'html.parser')
        selected_reviews = review_page_soup.select('li.YeINN')
    
        reviews = []
        for review in selected_reviews:
            # writer_element = review.select_one('div.sBWyy')
            # writer = writer_element.text.strip() if writer_element else None
            
            description_element = review.select_one('span.zPfVt')
            description = description_element.text.strip() if description_element else None
            
            # reviews.append({'writer': writer, 'description': description})
            reviews.append({'description': description})
        
        result = {'naverStars': star_rating,'naverReviewerCounts': review_count,'reviews': reviews, }
        
        return jsonify(result)
    
    except TimeoutException as e:
        print(e)
        return jsonify({'error': '페이지 로딩이 제대로 되지 않았습니다.'})
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run()