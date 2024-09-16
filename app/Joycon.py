from pyjoycon import JoyCon, get_R_id
import time
from threading import Lock

score_lock = Lock()
global_score = [0]

# タイミングデータ (島人ぬ宝)
timing_data = {
    "1" : {"soundTimer": 5.93},
    "2" : {"soundTimer": 8.29},
    "3" : {"soundTimer": 8.75},
    "4" : {"soundTimer": 12.03},
    "5" : {"soundTimer": 14.75},
    "6" : {"soundTimer": 15.15},
    "7" : {"soundTimer": 16.39},
    "8" : {"soundTimer": 17.95},
    "9" : {"soundTimer": 19.56},
    "10": {"soundTimer": 21.12},
    "11": {"soundTimer": 22.68},
    "12": {"soundTimer": 24.39},
    "13": {"soundTimer": 25.97},
    "14": {"soundTimer": 27.62},
    "15": {"soundTimer": 28.7},
    "16": {"soundTimer": 29.43},
    "17": {"soundTimer": 30.14},
    "18": {"soundTimer": 31.69},
    "19": {"soundTimer": 32.47},
    "20": {"soundTimer": 33.25},
    "21": {"soundTimer": 34.91},
    "22": {"soundTimer": 36.42},
    "23": {"soundTimer": 38.18},
    "24": {"soundTimer": 38.99},
    "25": {"soundTimer": 39.77},
    "26": {"soundTimer": 41.45},
    "27": {"soundTimer": 42.86},
    "28": {"soundTimer": 44.57},
    "29": {"soundTimer": 47.78},
    "30": {"soundTimer": 49.46},
    "31": {"soundTimer": 51.16},
    "32": {"soundTimer": 52.02},
    "33": {"soundTimer": 52.68},
    "34": {"soundTimer": 53.51},
    "35": {"soundTimer": 54.32},
    "36": {"soundTimer": 55.12},
    "37": {"soundTimer": 55.9},
    "38": {"soundTimer": 56.7},
    "39": {"soundTimer": 57.55},
    "40": {"soundTimer": 59.6},
    "41": {"soundTimer": 60.75},
    "42": {"soundTimer": 62.33},
    "43": {"soundTimer": 64.01},
    "44": {"soundTimer": 65.52},
    "45": {"soundTimer": 69.22},
    "46": {"soundTimer": 69.7},
    "47": {"soundTimer": 70.46},
    "48": {"soundTimer": 71.39},
    "49": {"soundTimer": 72.12},
    "50": {"soundTimer": 73.73}
}

def joycon(global_score, score_lock, start_time):
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
                            global_score[0] += 1000  # リストの値を更新
                        print(f"タイミングに合わせて振りました！得点: {global_score[0]}")
                        current_timing_index += 1  # 次のタイミングに進む
                elif elapsed_time > target_time + missed_time_check:
                    # 次のタイミングを確認する
                    print(f"タイミング {current_timing_index} を逃しました。次へ。")
                    current_timing_index += 1

            # 現在の加速度データを前回のデータとして保存
            prev_accel = accel

            print("グローバルスコア：", global_score[0])
            time.sleep(0.1)  # 0.1秒ごとにチェック

    except Exception as e:
        print(f"エラーが発生しました: {e}")