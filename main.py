import os
from flask import Flask, request, jsonify, render_template
from trends import trends_result
from analysis import analysis_result
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    # return "Hello, Duniaa!"
    return render_template('base.html')

@app.route('/trends')
def trends_get():
    return render_template('trends.html')

@app.route('/trends-result', methods=['POST'])
def trends_post():
    data = request.get_json()
    response_data = trends_result(data)
    response = jsonify(response_data)
    return response

@app.route('/analysis')
def analysis_get():
    return render_template('analysis.html')

# @app.route('/analysis-result', methods=['POST'])
@app.route('/analysis-result', methods=['POST'])
def analysis_post():
    data = request.get_json()
    print(data)
    response_data = analysis_result(data)
    response = jsonify(response_data)
    return response_data

def main():
    app.run(port=int(os.environ.get('PORT', 80)))
