from pyjoycon import JoyCon, get_R_id
import time
from threading import Lock

score_lock = Lock()

# タイミングデータ (島人ぬ宝)
timing_data = {
    "1": {"soundTimer": 6.06},
    "2": {"soundTimer": 8.45},
    "3": {"soundTimer": 8.84},
    "4": {"soundTimer": 12.45},
    "5": {"soundTimer": 14.86},
    "6": {"soundTimer": 15.27}
}

def joycon(global_score, score_lock,start_time):
    print("joycon開始―！！！")

    try:
        # Joy-ConのIDを取得
        joycon_id = get_R_id()
        joycon = JoyCon(*joycon_id)

        # 前回の加速度データを保持する変数を用意
        prev_accel = {'x': 0, 'y': 0, 'z': 0}

        timing_keys = list(timing_data.keys())  # タイミングデータのキーリストを取得
        current_timing_index = 0  # 現在のタイミングデータのインデックス


        while True:
            # 現在の経過時間を計算
            elapsed_time = time.time() - start_time

            # Joy-Conのステータスを取得
            status = joycon.get_status()
            accel = status['accel']  # 加速度データ

            # 各軸の変化量を計算
            accel_change_x = abs(accel['x'] - prev_accel['x'])
            accel_change_y = abs(accel['y'] - prev_accel['y'])
            accel_change_z = abs(accel['z'] - prev_accel['z'])

            # しきい値を設定 (ここでは7000)
            threshold = 7000

            # 現在のタイミングデータを取得
            if current_timing_index < len(timing_keys):
                target_time = timing_data[timing_keys[current_timing_index]]["soundTimer"]

                # タイミングに基づく加点処理
                time_tolerance = 0.5  # 許容誤差 (例: 0.5秒)
                missed_time_check = 0.5  # 逃したタイミングをどのくらい後まで許容するか（秒）

                # 現在のタイミングと次のタイミングを比較
                if target_time - time_tolerance <= elapsed_time <= target_time + missed_time_check:
                    if accel_change_x > threshold or accel_change_y > threshold or accel_change_z > threshold:
                        with score_lock:  # スコアの更新はスレッドセーフにする
                            global_score += 1000
                        print(f"タイミングに合わせて振りました！得点: {global_score}")
                        current_timing_index += 1  # 次のタイミングに進む
                elif elapsed_time > target_time + missed_time_check:
                    # 次のタイミングを確認する
                    print(f"タイミング {current_timing_index} を逃しました。次へ。")
                    current_timing_index += 1
            # 現在の加速度データを前回のデータとして保存
            prev_accel = accel

            # デバッグ用: 加速度データを表示
            # print("加速度:", accel, "経過時間:", elapsed_time)
            time.sleep(0.1)  # 0.1秒ごとにチェック

    except Exception as e:
        print(f"エラーが発生しました: {e}")