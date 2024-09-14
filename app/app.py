from flask import Flask, render_template, Response, request, jsonify
import mediapipe as mp
import cv2
import numpy as np
import threading
from .Joycon import joycon  # Joycon関数をインポート
from .scoring_logic import check_acceleration_and_score  # スコア計算ロジックをインポート]
from .ButtonGetInfo import JoyconInfo, latest_data  # Joyconデータとグローバル変数をインポート

app = Flask(__name__)

# グローバル変数でタイマースレッドを管理
timer_thread = None
stop_timer_event = threading.Event()

@app.route('/')
def index():
    return render_template("index.html")

# MediaPipeの初期化
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# お手本動画の読み込み
video_path = '/static/video/sample_15s.mp4'
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

@app.route('/video')
def video():
    return render_template('video.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/pose-data', methods=['POST'])
def pose_data():
    data = request.json
    joints = data.get('joints', [])
    print(joints)
    
    reference_pose = [{'x': 0.5, 'y': 0.5}, {'x': 0.6, 'y': 0.6}]  # 例として使用
    score = calculate_similarity(reference_pose, joints)
    return jsonify(score=score)

def calculate_similarity(pose1, pose2):
    if len(pose1) != len(pose2):
        return 0

    distances = [np.linalg.norm(np.array([p1['x'], p1['y']]) - np.array([p2['x'], p2['y']])) for p1, p2 in zip(pose1, pose2)]
    return 100 - np.mean(distances) * 100

# グローバル変数でタイマースレッドを管理
timer_thread = None
stop_timer_event = threading.Event()

# タイマーを開始するエンドポイント
@app.route('/start-timer', methods=['POST'])
def start_timer():
    global timer_thread

    if timer_thread is None or not timer_thread.is_alive():
        # クライアントから BPM を取得
        bpm = request.json.get('bpm', 72)  # デフォルト値として 72 を使用
        # 新しいスレッドでJoyconタイマーを実行
        timer_thread = threading.Thread(target=JoyconInfo, args=(bpm,))  # 引数bpmを渡す
        timer_thread.start()
        return jsonify({'message': 'タイマーを開始しました'}), 200
    else:
        return jsonify({'message': 'タイマーはすでに実行中です'}), 400


@app.route('/check-score', methods=['POST'])
def check_score():
    global score

    # Joy-Con から取得したデータを使用
    accel_data = latest_data['accel']
    joycon_time = latest_data['timestamp']  # Joy-Con のタイムスタンプを取得

    # 動画の現在の再生時間をクライアントから取得
    data = request.json
    video_time = data.get('video_time', 0)

    # Joy-Conのデータがあるか確認
    if accel_data is not None:
        # 再生時間と加速度データに基づいて得点を計算
        score = check_acceleration_and_score(accel_data, video_time, score)

    return jsonify({"score": score})

# タイマーを停止するエンドポイント
@app.route('/stop-timer', methods=['POST'])
def stop_timer():
    global stop_timer_event
    stop_timer_event.set()
    return jsonify({'message': 'タイマーを停止しました'}), 200

if __name__ == '__main__':
    app.run(debug=True)
