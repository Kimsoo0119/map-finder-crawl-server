import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import os


app = Flask(__name__)
CORS(app)
load_dotenv()

chrome_options = Options()
chrome_options.add_argument('--headless')  # 화면 출력 안 함
chrome_options.add_argument('--disable-gpu')  # GPU 사용 안 함
chrome_options.add_argument('lang=ko_KR')  # 언어 설정, 안 하면 네이버 지도 검색이 안 될 수도 있음
@app.route('/places/<place_name>', methods=['GET'])
def search_places(place_name):
    try:
        # 네이버 검색 API 사용을 위한 API key
        client_id = os.environ.get('CLIENT_ID')
        client_secret = os.environ.get('CLIENT_SECRET')

        # 검색 결과 중 10개씩 페이지네이션 기능을 사용하기 위한 파라미터
        display = 10
        start = request.args.get('start', 1)
        start = int(start)

        # 네이버 검색 API 호출을 위한 URL과 파라미터 설정
        url = 'https://openapi.naver.com/v1/search/local.json'
        headers = {'X-Naver-Client-Id': client_id, 'X-Naver-Client-Secret': client_secret}
        params = {'query': place_name, 'display': display, 'start': start}

        # 네이버 검색 API 호출
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        # 검색 결과 중 필요한 정보만 추출하여 반환
        result = []
        for item in response.json()['items']:
            soup = BeautifulSoup(item['title'], 'html.parser')
            title = soup.get_text()
            result.append({
                'title': title,
                'category': item['category'],
                'address': item['address'],
                'telephone': item['telephone'],
                'mapX': item['mapx'],
                'mapY': item['mapy']
                
            })

        return jsonify({'result': result}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/<place_name>', methods=['GET'])
def search_map(place_name):
    try:
        # place_name을 url에서 사용할 수 있도록 인코딩
        encoded_place_name = requests.utils.quote(place_name)
        url = f"https://m.map.naver.com/search2/search.naver?query={encoded_place_name}&sm=hty&style=v5"
        
        # Selenium으로 크롬 브라우저 열기
        options = webdriver.ChromeOptions()
        # options.add_argument('headless')  # 크롬 브라우저를 헤드리스 모드로 실행

        driver = webdriver.Chrome(service_log_path=os.path.devnull, options=options)
        # 검색 결과 페이지로 이동하고 로딩 기다리기
        driver.get(url)
        time.sleep(1)
        driver.find_element(By.XPATH,'/html/body/div[4]/div[2]/ul/li/div[1]/a[2]/div').click()
        
        # 페이지 소스코드 가져오기
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        star_element = soup.find('span', {'class': 'PXMot LXIwF'})

        # 별점 값 가져오기
        star_rating = star_element.em.text
        print(star_rating)
        # 제목 크롤링
        # title = soup.select_one('strong.name.ng-tns-c119-9').text
        # title = soup.select('.C6RjW').text
        # print(element)
        # 브라우저 종료
        # driver.quit()

        # 결과 반환
        result = {'place_name': place_name, }
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run()