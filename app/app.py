from flask import Flask, render_template, jsonify, request,url_for
import json
import subprocess
from .Joycon import joycon
import subprocess
import threading
import time

app = Flask(__name__)

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

# メインエンドポイント
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/eisa')
def eisa():
    link='/eisa'
    update_landmarks('app/static/landmarks/sample_landmarks(1m).json')
    #landmarks_file='app/static/landmarks/sample_landmarks(1m).json'
    # 動画ファイルのパスを動的に生成
    video_file = url_for('static', filename='video/sample_1m.mp4')
    return render_template('game.html',video_file=video_file,link=link)

@app.route('/suirenka')
def syounaxn():
    link='/suirenka'
    update_landmarks('app/static/landmarks/suirenka-mini_landmarks.json')
    #landmarks_file = 'app/static/landmarks/suirenka-mini_landmarks.json'
    # 動画ファイルのパスを動的に生成
    video_file = url_for('static', filename='video/JustDance_Suirenka_mini.mp4')
    return render_template('game.html',video_file=video_file,link=link)

@app.route('/odoloop')
def odoloop():
    link='/odoloop'
    update_landmarks('app/static/landmarks/odottezunda_landmarks.json')
    #landmarks_file = 'app/static/landmarks/suirenka-mini_landmarks.json'
    # 動画ファイルのパスを動的に生成
    video_file = url_for('static', filename='video/踊ってない夜を知らないずんだもん反転_mini.mp4')
    return render_template('game.html',video_file=video_file,link=link)

@app.route('/marumori')
def marumori():
    link='/marumori'
    update_landmarks('app/static/landmarks/marumori_landmarks.json')
    #landmarks_file = 'app/static/landmarks/suirenka-mini_landmarks.json'
    # 動画ファイルのパスを動的に生成
    video_file = url_for('static', filename='video/マル・マル・モリ・モリ_反転.mp4')
    return render_template('game.html',video_file=video_file,link=link)

@app.route('/dynamic')
def dynamic():
    link='/dynamic'
    update_landmarks('app/static/landmarks/dynamic_landmarks.json')
    #landmarks_file = 'app/static/landmarks/suirenka-mini_landmarks.json'
    # 動画ファイルのパスを動的に生成
    video_file = url_for('static', filename='video/ダイナミック琉球反転_mini.mp4')
    return render_template('game.html',video_file=video_file,link=link)

@app.route('/koi')
def koi():
    link='/koi'
    update_landmarks('app/static/landmarks/koidansu_landmarks.json')
    # 動画ファイルのパスを動的に生成
    video_file = url_for('static', filename='video/恋ダンス振り付け反転.mp4')
    return render_template('game.html',video_file=video_file,link=link)

@app.route('/harehare')
def harehare():
    link='/harehare'
    update_landmarks('app/static/landmarks/harehare_landmarks.json')
    # 動画ファイルのパスを動的に生成
    video_file = url_for('static', filename='video/ハレ晴レユカイ反転.mp4')
    return render_template('game.html',video_file=video_file,link=link)
  
@app.route('/eigadancer')
def eigadancer():
    return render_template('eigadancer.html')

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