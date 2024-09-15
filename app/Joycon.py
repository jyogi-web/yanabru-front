from pyjoycon import JoyCon, get_R_id
import time
from threading import Lock

score_lock = Lock()


def joycon(global_score, score_lock):
    print("joycon開始―！！！")

    try:
        # Joy-ConのIDを取得
        joycon_id = get_R_id()
        joycon = JoyCon(*joycon_id)

        # 前回の加速度データを保持する変数を用意
        prev_accel = {'x': 0, 'y': 0, 'z': 0}

        while True:
            # Joy-Conのステータスを取得
            status = joycon.get_status()
            accel = status['accel']  # 加速度データ

            # 各軸の変化量を計算
            accel_change_x = abs(accel['x'] - prev_accel['x'])
            accel_change_y = abs(accel['y'] - prev_accel['y'])
            accel_change_z = abs(accel['z'] - prev_accel['z'])

            # しきい値を設定 (ここでは7000)
            threshold = 7000

            # x, y, zのいずれかで振る動作を検知した場合に得点を加算
            if accel_change_x > threshold or accel_change_y > threshold or accel_change_z > threshold:
                with score_lock:  # スコアの更新はスレッドセーフにする
                    global_score += 10
                print(f"Joy-Conを振りました！得点: {global_score}")
            # 現在の加速度データを前回のデータとして保存
            prev_accel = accel

            # 加速度データを表示
            print("加速度:", accel)
            time.sleep(0.1)  # 0.1秒ごとにチェック

    except Exception as e:
        print(f"エラーが発生しました: {e}")