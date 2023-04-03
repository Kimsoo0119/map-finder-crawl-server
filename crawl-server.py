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
        first_item = driver.find_element(By.XPATH, '//*[@id="ct"]/div[2]/ul/li[1]/div[1]/a/div/em')
        first_item.click()

        wait = WebDriverWait(driver, 2)
        wait.until(EC.url_changes(driver.current_url))
        url = driver.current_url
        
        print(url)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        star_rating_element = soup.select_one('span.PXMot.LXIwF em')
        star_rating = star_rating_element.text if star_rating_element else None

        review_url = url.replace('/home', '/review/visitor')
        driver.get(review_url)
        

        # 결과 반환
        result = {'place_name': place_name, 'star_rating': star_rating}
        return jsonify(result)
    
    except TimeoutException as e:
        print(e)
        return jsonify({'error': '페이지 로딩이 제대로 되지 않았습니다.'})
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run()