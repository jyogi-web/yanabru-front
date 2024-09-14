# scoring_logic.py
import numpy as np

# お手本データ
reference_times = {
    1: {"soundTimer": 6.96},
    2: {"soundTimer": 9.86},
    3: {"soundTimer": 10.2},
    4: {"soundTimer": 14.52},
    5: {"soundTimer": 17.4},
    6: {"soundTimer": 17.88}
}

# お手本データの時間と一致しているかどうかを判定し、得点を付与する関数
def check_acceleration_and_score(acceleration, video_time, score):
    for key, ref_data in reference_times.items():
        ref_time = ref_data["soundTimer"]

        # 動画の現在の時間がリファレンス時間±0.3秒以内かどうかを確認
        if ref_time - 0.3 <= video_time <= ref_time + 0.3:
            # 加速度が7000を超えた場合に得点を付与
            if acceleration > 7000:
                score += 1
                print(f"Score! Time: {video_time}, Acceleration: {acceleration}, Score: {score}")
    return score
