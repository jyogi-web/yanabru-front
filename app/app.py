from flask import Flask, render_template, jsonify, request,url_for
import json

app = Flask(__name__)

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
    link='/eisa'
    update_landmarks('app/static/landmarks/sample_landmarks(1m).json')
    #landmarks_file='app/static/landmarks/sample_landmarks(1m).json'
    # 動画ファイルのパスを動的に生成
    video_file = url_for('static', filename='video/sample_1m.mp4')
    return render_template('game.html',video_file=video_file,link=link)

@app.route('/syounaxn')
def syounaxn():
    link='/syounaxn'
    update_landmarks('app/static/landmarks/suirenka-mini_landmarks.json')
    #landmarks_file = 'app/static/landmarks/suirenka-mini_landmarks.json'
    # 動画ファイルのパスを動的に生成
    video_file = url_for('static', filename='video/JustDance_Suirenka_mini.mp4')
    return render_template('game.html',video_file=video_file,link=link)

@app.route('/landtest')
def landtest():
    return render_template('landtest.html')

if __name__ == '__main__':
    app.run(debug=True)