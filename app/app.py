from flask import Flask, render_template, jsonify, request,url_for
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
global_score = [0]  # リストで初期化
score_lock = threading.Lock()

# ランドマークデータの保存先
landmarks_file = 'app/static/landmarks/suirenka-mini_landmarks.json'
# ランドマークファイル更新
def update_landmarks(file):
    global landmarks_file
    landmarks_file=file

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


@app.route('/eisa')
def eisa():
    song_name = request.args.get('song', 'eisa')  # デフォルトは島人ぬ宝
    link = '/eisa'
    update_landmarks('app/static/landmarks/sample_landmarks(1m).json')
    #landmarks_file='app/static/landmarks/sample_landmarks(1m).json'

    # 曲名に基づいてタイミングデータを取得する
    timing_data_file = f'app/static/timing_data/{song_name}.json'
    update_landmarks(timing_data_file)
    
    # 動画ファイルのパスを動的に生成
    video_file = url_for('static', filename='video/sample_1m.mp4',link=link)
    
    return render_template('game.html',video_file=video_file,link=link)

@app.route('/syounaxn')
def syounaxn():
    song_name = request.args.get('song', 'suirenka')  # デフォルトは湘南乃風
    link='/syounaxn'
    update_landmarks('app/static/landmarks/suirenka-mini_landmarks.json')
    #landmarks_file = 'app/static/landmarks/suirenka-mini_landmarks.json'
    # 曲名に基づいてタイミングデータを取得する
    timing_data_file = f'app/static/timing_data/{song_name}.json'
    update_landmarks(timing_data_file)
    
    # 動画ファイルのパスを動的に生成
    video_file = url_for('static', filename='video/JustDance_Suirenka_mini.mp4')

    return render_template('game.html',video_file=video_file,link=link)

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
    data = request.json  # フロントエンドからのデータを取得
    song_name = data.get('song_name')  # 'song_name'が存在するか確認
    print(f"Received song name: {song_name}")  # ログに出力して確認
    
    if song_name:
        timing_data_file = f'app/static/timing_data/{song_name}.json'
        start_time = time.time()
        threading.Thread(target=joycon, args=(global_score, score_lock, start_time, timing_data_file)).start()
        return jsonify({'status': 'Joy-Con processing started'}), 200
    else:
        return jsonify({'status': 'Error', 'message': 'No song name provided'}), 400

@app.route('/get-score', methods=['GET'])
def get_score():
    global global_score
    with score_lock:
        print(f"Returning global score: {global_score[0]}")  # デバッグ用に返されるスコアを出力
        return jsonify({'score': global_score[0]})

@app.route('/reset-score', methods=['POST'])
def reset_score():
    global global_score
    with score_lock:
        global_score = [0]  # スコアを初期化
        print("スコアがリセットされました")
    return jsonify({'status': 'Score reset'})

if __name__ == '__main__':
    app.run(debug=True)