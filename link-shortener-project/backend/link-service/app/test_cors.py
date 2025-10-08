from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # Enable CORS for the whole app

@app.route('/test')
def test_route():
    return "CORS is working!"

if __name__ == '__main__':
    app.run(debug=True)