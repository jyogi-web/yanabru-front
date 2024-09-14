from pyjoycon import JoyCon, get_R_id
import time
from datetime import datetime
import json

# グローバル変数で最新の加速度データとタイムスタンプを保持
latest_data = {"accel": None, "timestamp": None}

def JoyconInfo(BPM):
    global latest_data  # グローバル変数を参照

    # 初期化
    scoreJoy = 0
    result = {}
    count = 0
    dlapsedtime = 0
    soundTimer = 0
    countsecond = 1
    try:
        # Joy-ConのIDを取得
        joycon_id = get_R_id()
        joycon = JoyCon(*joycon_id)

        # 前回の加速度データを保持する変数を用意
        prev_accel = {'x': 0, 'y': 0, 'z': 0}

        # 開始タイム取得
        start_time = datetime.now()
        print(f"ゲームスタート {start_time} 秒")

        while True:
            # Joy-Conのステータスを取得
            status = joycon.get_status()
            accel = status['accel']  # 加速度データ
            button_right = status['buttons']['right']
            
            # 各軸の変化量を計算
            accel_change_x = abs(accel['x'] - prev_accel['x'])
            accel_change_y = abs(accel['y'] - prev_accel['y'])
            accel_change_z = abs(accel['z'] - prev_accel['z'])

            # グローバル変数に加速度データとタイムスタンプを更新
            latest_data = {"accel": accel, "timestamp": time.time()}

            # しきい値を超えた場合に振ったとみなす
            threshold = 7000
            if accel_change_x > threshold or accel_change_y > threshold or accel_change_z > threshold:
                scoreJoy += 10  # 得点を加算
                print(f"Joy-Conを振りました！得点: {scoreJoy}")

            # 特定のボタンを押しているときにデータを取得
            if button_right['b'] == 1:
                count += 1
                elapsed_time = (datetime.now() - start_time).total_seconds()  # 経過秒数
                data = {
                    'soundTimer': soundTimer  # 経過時間
                }
                print(f"データ {count}: {data}")
                result[count] = data

            # ZRボタンで終了
            if button_right['zr'] == 1:
                with open('joycon_result.json', 'w') as f:
                    json.dump(result, f)
                print("ゲーム終了、データ保存しました")
                break

            # 現在の加速度データを前回のデータとして保存
            prev_accel = accel

            # タイマー計算 (BPMに基づいて)
            soundTimer += (BPM / 60) * 0.1
            print(f"タイマー: {soundTimer}")
            if soundTimer >= countsecond * BPM:
                print(f"{countsecond}秒経過しました")
                countsecond += 1

            # 0.1秒ごとにループ
            time.sleep(0.1)

    except Exception as e:
        print(f"エラーが発生しました: {e}")
