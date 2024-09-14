import cv2
import mediapipe as mp
import json
import os

# 保存先ディレクトリを確認し、存在しない場合は作成
save_dir = 'app/static/landmarks'
os.makedirs(save_dir, exist_ok=True)

# Mediapipeのポーズモジュールを初期化
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# 見本動画から骨格ランドマークを抽出し、保存
def extract_and_save_landmarks(video_path, save_path):
    cap = cv2.VideoCapture(video_path)
    landmarks_data = []
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # mediapipeで骨格検出
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(frame_rgb)
        
        if results.pose_landmarks:
            frame_landmarks = []
            for landmark in results.pose_landmarks.landmark:
                frame_landmarks.append({
                    'x': landmark.x,
                    'y': landmark.y,
                    'z': landmark.z,
                    'visibility': landmark.visibility
                })
            landmarks_data.append(frame_landmarks)
    
    cap.release()
    
    # JSONファイルとして保存
    with open(save_path, 'w') as f:
        json.dump(landmarks_data, f)

# 見本動画の骨格ランドマークを抽出して保存
extract_and_save_landmarks('app/static/video/sample_15s.mp4', 'app/static/landmarks/sample_landmarks.json')