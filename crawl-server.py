from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/places/<place_name>', methods=['GET'])
def crawlPlaces(place_name):
    print(place_name)


    return f"Received: {place_name}" 

if __name__ == '__main__':
    app.run()