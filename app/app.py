from flask import Flask,render_template,Response,request,jsonify
import mediapipe as mp
import cv2
import numpy as np

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

# MediaPipeの初期化
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# お手本動画の読み込み
video_path = '/static/video/エイサー_島人ぬ宝.mp4'
cap = cv2.VideoCapture(video_path)

def generate_frames():
    while True:
        success, frame = cap.read()
        if not success:
            break

        # 骨格検出を行う
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(frame_rgb)

        # 骨格の描画
        if results.pose_landmarks:
            mp.solutions.drawing_utils.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        # フレームをJPEG形式にエンコードして送信
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# ルートエンドポイント
@app.route('/video')
def video():
    return render_template('video.html')

# ビデオフィードエンドポイント
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# 骨格データを受信しスコアを計算
@app.route('/pose-data', methods=['POST'])
def pose_data():
    data = request.json
    joints = data.get('joints', [])

    # お手本のポーズと比較してスコアを計算
    # 仮のデータとしてお手本の骨格を定義
    reference_pose = [{'x': 0.5, 'y': 0.5}, {'x': 0.6, 'y': 0.6}]  # 例として使用

    # 類似度を計算（ユークリッド距離）
    score = calculate_similarity(reference_pose, joints)
    return jsonify(score=score)

# スコアを計算する関数
def calculate_similarity(pose1, pose2):
    if len(pose1) != len(pose2):
        return 0  # データ数が一致しない場合はスコア0

    distances = [np.linalg.norm(np.array([p1['x'], p1['y']]) - np.array([p2['x'], p2['y']])) for p1, p2 in zip(pose1, pose2)]
    return 100 - np.mean(distances) * 100  # 距離に基づいてスコアを100点満点で計算