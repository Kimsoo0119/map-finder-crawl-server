from flask import Flask, request, jsonify
from flask_cors import CORS
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import requests
import os


app = Flask(__name__)
CORS(app)
load_dotenv()

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

if __name__ == '__main__':
    app.run()