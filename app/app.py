from flask import Flask, render_template, jsonify, request
import json
import subprocess
from .Joycon import joycon
from flask_cors import CORS
import subprocess
import threading
import time

app = Flask(__name__)
CORS(app)

# グローバル変数としてスコアを保持
global_score = 0
score_lock = threading.Lock()

# ランドマークデータの保存先
landmarks_file = 'app/static/landmarks/sample_landmarks(30fps).json'

# ランドマークデータを提供するエンドポイント
@app.route('/get-pose-landmarks', methods=['GET'])
def get_pose_landmarks():
    with open(landmarks_file, 'r') as file:
        landmarks_data = json.load(file)
    return jsonify(landmarks=landmarks_data)

# # Poseデータを受け取るエンドポイント
# @app.route('/pose-data', methods=['POST'])
# def pose_data():
#     data = request.json
#     # ここで受け取ったポーズデータを処理する
#     print("Received pose data:", data)
#     # 例としてスコアを固定値で返す
#     return jsonify(score=100)

# メインエンドポイント
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/landtest')
def landtest():
    return render_template('landtest.html')

# Joycon.pyを実行するためのAPI
@app.route('/run-joycon', methods=['POST'])
def run_joycon():
    print("runrunrun")
    try:
        # Joycon.pyをバックグラウンドで実行
        process = subprocess.Popen(['python', '../Joycon.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if stderr:
            return jsonify({'status': 'Joycon.py failed', 'error': stderr.decode()}), 500
        return jsonify({'status': 'Joycon.py started'}), 200
    except Exception as e:
        return jsonify({'status': 'Error', 'error': str(e)}), 500


# Joy-Conの処理をバックグラウンドで実行するエンドポイント
@app.route('/start-joycon', methods=['POST'])
def start_joycon():
    print("start_joycon!!")
    start_time = time.time()  # スタートボタンが押された時の時間を記録
    # Joyconの処理をバックグラウンドで実行
    threading.Thread(target=joycon, args=(global_score, score_lock, start_time)).start()
    return jsonify({'status': 'Joy-Con processing started'}), 200

# スコアを取得するエンドポイント
@app.route('/get-score', methods=['GET'])
def get_score():
    # print("getscore!")
    with score_lock:
        return jsonify({'score': global_score}), 200

if __name__ == '__main__':
    app.run(debug=True)