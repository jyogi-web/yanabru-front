import cv2
import mediapipe as mp
import json
import os
import time

# Mediapipeのポーズモジュールを初期化
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
# 左右反転（鏡合わせ）になってるか
reverse=True

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
                frame_landmarks = []
                for landmark in results.pose_landmarks.landmark:
                    frame_landmarks.append({
                        'x': landmark.x,
                        'y': landmark.y,
                        'z': landmark.z,
                        'visibility': landmark.visibility
                    })
                landmarks_data.append(frame_landmarks)

            prev_time = current_time
    
    cap.release()
    
    # JSONファイルとして保存
    with open(save_path, 'w') as f:
        json.dump(landmarks_data, f)

# 見本動画の骨格ランドマークを抽出して保存
extract_and_save_landmarks('app/static/video/ダイナミック琉球反転_mini.mp4', 'app/static/landmarks/dynamic_landmarks.json')