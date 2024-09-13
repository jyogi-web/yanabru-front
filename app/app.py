from flask import Flask,render_template,Response
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
mp_drawing = mp.solutions.drawing_utils

# カメラ映像を取得
def generate_frames():
    cap = cv2.VideoCapture(0)  # カメラの映像を取得（0はデフォルトカメラ）

    while True:
        success, frame = cap.read()
        if not success:
            break

        # 画像をRGBに変換
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # MediaPipeで骨格検出
        result = pose.process(rgb_frame)

        # 骨格のランドマークを描画
        if result.pose_landmarks:
            mp_drawing.draw_landmarks(
                frame, result.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        # JPEG形式でエンコード
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        # フレームを返す
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

#入力：姿勢推定から得られたランドマークのデータ
#出力：12の点(右肩)からの相対座標(numpy配列)
def landmark2np(pose_landmarks):
    detected_point = 12
    li = []
    for j in (pose_landmarks.landmark):
            li.append([j.x, j.y, j.z])
    for k in li:
        if k[0] == 0 and k[1] == 0  and k[2]==0:
            print("No detected")
            li[k] = li[detected_point]

    return np.array(li) - li[detected_point]

#入力：比較する2つの座標ランドマーク群
#出力：各ベクトルごとに比較したコサイン平均類似度
def manual_cos(A, B):
    dot = np.sum(A*B, axis=-1)
    A_norm = np.linalg.norm(A, axis=-1)
    B_norm = np.linalg.norm(B, axis=-1)
    cos = dot / (A_norm*B_norm+1e-10)

    # 検出できない場合の処理
    for i in cos:
        count = 0
        if i == 0:
            print("cos deleted")
            np.delete(cos,count)
        count = count +1
    return cos.mean()

# ルートエンドポイント
@app.route('/video')
def video():
    return render_template('video.html')

# ビデオフィードエンドポイント
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
