from flask import Flask, render_template, jsonify, request,url_for
import json
import subprocess
from .Joycon import joycon
import subprocess
import threading
import time
from flask_cors import CORS 
import os
import cv2
import mediapipe as mp
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)  # 全エンドポイントでCORSを有効化

# MediaPipe Poseモデルの読み込み
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# グローバル変数としてスコアを保持
global_score = [0]  # リストで初期化
score_lock = threading.Lock()

# 基本ディレクトリの取得
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ランドマークデータの保存先
LANDMARKS_FOLDER = os.path.join(BASE_DIR, 'static', 'landmarks')
os.makedirs(LANDMARKS_FOLDER, exist_ok=True)

# アップロードフォルダの設定
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ランドマークデータの保存先
landmarks_file = os.path.join(LANDMARKS_FOLDER, 'suirenka-mini_landmarks.json')

# ランドマークファイル更新
def update_landmarks(file):
    global landmarks_file
    landmarks_file=file

# 見本動画から骨格ランドマークを抽出し、保存
def extract_and_save_landmarks(video_path, save_path, target_fps=60):
    cap = cv2.VideoCapture(video_path)
    landmarks_data = []
    
    frame_interval = 1.0 / target_fps
    prev_time = time.time()

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        current_time = time.time()
        if current_time - prev_time >= frame_interval:
            # mediapipeで骨格検出
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(frame_rgb)
            
            if results.pose_landmarks:
                landmarks = []
                for landmark in results.pose_landmarks.landmark:
                    landmarks.append({
                        'x': landmark.x,
                        'y': landmark.y,
                        'z': landmark.z,
                        'visibility': landmark.visibility
                    })
                landmarks_data.append(landmarks)
            
            prev_time = current_time

    cap.release()

    with open(save_path, 'w',encoding='utf-8') as f:
        json.dump(landmarks_data, f,ensure_ascii=False, indent=4)

# ランドマークデータを提供するエンドポイント
@app.route('/get-pose-landmarks', methods=['GET'])
def get_pose_landmarks():
    with open(landmarks_file, 'r', encoding='utf-8') as file:
        landmarks_data = json.load(file)
    return jsonify(landmarks=landmarks_data)

# 新しいエンドポイントを追加して、ランドマークを抽出し保存する
@app.route('/extract_landmarks', methods=['POST'])
def extract_landmarks():
    video_path = request.json.get('video_path')
    save_path = request.json.get('save_path')
    target_fps = request.json.get('target_fps', 60)

    extract_and_save_landmarks(video_path, save_path, target_fps)
    
    return jsonify({'status': 'success', 'message': 'Landmarks extracted and saved successfully.'})


# ファイルアップロードエンドポイントの前に追加
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')  # 修正
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Flaskの設定にUPLOAD_FOLDERを追加
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ファイルアップロードエンドポイント
@app.route('/upload_video', methods=['POST'])
def upload_video():
    print("アップロードエンドポイントにリクエストが届きました")
    
    if 'video' not in request.files:
        print("動画ファイルが提供されていません")
        return jsonify({'status': 'error', 'message': 'No video file provided'}), 400
    
    video = request.files['video']
    
    if video.filename == '':
        print("空のファイル名")
        return jsonify({'status': 'error', 'message': 'No selected file'}), 400

    # ファイル名をサニタイズ
    filename = secure_filename(video.filename)
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    print(f"保存先のパス: {video_path}")
    
    try:
        video.save(video_path)
        print(f"動画ファイルを保存しました: {video_path}")
    except Exception as e:
        print(f"動画ファイルの保存中にエラーが発生しました: {e}")
        return jsonify({'status': 'error', 'message': 'Failed to save video file'}), 500
    
    # ランドマークの保存先パスを設定
    save_filename = f"{os.path.splitext(filename)[0]}_landmarks.json"
    save_path = os.path.join(LANDMARKS_FOLDER, save_filename)
    print(f"ランドマーク保存先のパス: {save_path}")
    
    try:
        extract_and_save_landmarks(video_path, save_path)
        print(f"ランドマークを抽出して保存しました: {save_path}")
    except Exception as e:
        print(f"ランドマークの抽出中にエラーが発生しました: {e}")
        return jsonify({'status': 'error', 'message': 'Failed to extract landmarks'}), 500
    
    return jsonify({'status': 'success', 'message': 'Video uploaded and landmarks extracted successfully.'})

# メインエンドポイント
@app.route('/')
def index():
    # アップロードフォルダ内の.mp4ファイルを取得
    video_files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.endswith('.mp4')]
    # 対応するゲーム名をリストアップ
    games = [os.path.splitext(f)[0] for f in video_files]
    return render_template('index.html', games=games)


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
  
@app.route('/game/<game_name>')
def game_page(game_name):
    """
    指定されたゲーム名に基づいてゲームページを表示します。
    ランドマークファイルと動画ファイルが存在するかを確認し、
    存在する場合はgame.htmlテンプレートにデータを渡します。
    """
    landmark_file = os.path.join(LANDMARKS_FOLDER, f'{game_name}_landmarks.json')
    video_file = f'uploads/{game_name}.mp4'

    # 動画ファイルのフルパス
    video_full_path = os.path.join(BASE_DIR, 'static', video_file)

    # ランドマークファイルと動画ファイルの存在チェック
    if not os.path.exists(landmark_file):
        return jsonify({'status': 'error', 'message': 'ランドマークファイルが見つかりません'}), 404
    if not os.path.exists(video_full_path):
        return jsonify({'status': 'error', 'message': '動画ファイルが見つかりません'}), 404

    # ランドマークファイルを更新
    update_landmarks(landmark_file)

    # 動画ファイルのURLを生成
    video_url = url_for('static', filename=video_file)

    return render_template('game.html', video_file=video_url, game_name=game_name)

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