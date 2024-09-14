from flask import Flask, render_template, jsonify
import mediapipe as mp
import cv2

app = Flask(__name__)

# MediaPipeの初期化
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
landmarks_data = []

# お手本動画の読み込み
video_path = './static/video/sample_15s.mp4'
cap = cv2.VideoCapture(video_path)

def analyze_sample_video():
    global landmarks_data
    while True:
        success, frame = cap.read()
        if not success:
            break  # 動画の最後まで処理したら終了

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(frame_rgb)

        frame_landmarks = []
        if results.pose_landmarks:
            for landmark in results.pose_landmarks.landmark:
                frame_landmarks.append({'x': landmark.x, 'y': landmark.y})

        landmarks_data.append(frame_landmarks)

# ランドマークデータを提供するエンドポイント
@app.route('/get-pose-landmarks', methods=['GET'])
def get_pose_landmarks():
    return jsonify(landmarks=landmarks_data)

# メインエンドポイント
@app.route('/')
def index():
    return render_template('index.html')

# アプリケーション開始時に動画解析を行う
analyze_sample_video()

if __name__ == '__main__':
    app.run(debug=True)
