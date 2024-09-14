from pyjoycon import JoyCon,    get_R_id
import time
from datetime import datetime
import json

def Joycon(BPM):
    # 初期化
    scoreJoy = 0
    result = {}
    count = 0
    dlapsedtime=0
    soundTimer=0
    countsecond=1
    try:
        # Joy-ConのIDを取得
        joycon_id = get_R_id()
        joycon = JoyCon(*joycon_id)

        # 前回の加速度データを保持する変数を用意
        prev_accel = {'x': 0, 'y': 0, 'z': 0}

        # 開始タイム取得
        start_time = datetime.now()

        print(f"ゲームスタート{start_time}秒")

        while True:
            # Joy-Conのステータスを取得
            status = joycon.get_status()
            accel = status['accel']  # 加速度データ
            button_right = status['buttons']['right']
            
            # 振る動作を検知 (軸方向の変化量が一定以上のとき)
            # 各軸の変化量を計算
            accel_change_x = abs(accel['x'] - prev_accel['x'])
            accel_change_y = abs(accel['y'] - prev_accel['y'])
            accel_change_z = abs(accel['z'] - prev_accel['z'])

            # print(buttons['right'])

            # しきい値を超えた場合に振ったとみなす
            threshold = 3000

            if accel_change_x > threshold or accel_change_y > threshold or accel_change_z > threshold:
                scoreJoy += 10  # 得点を加算
                print(f"Joy-Conを振りました！得点: {scoreJoy}")

            # 特定のボタンを押しているときに加速度・座標・時間を取得
            if button_right['r']==1:
                count+=1
                data = {
                    'accel_change_x':accel_change_x,
                    'accel_change_y':accel_change_y,
                    'accel_change_z':accel_change_z,
                    'gyro_x':status['gyro']['x'],
                    'gyro_y':status['gyro']['y'],
                    'gyro_z':status['gyro']['z'],
                    'microseconds':dlapsedtime.microseconds
                }
                print(status['gyro'])
                result[count] = data
                

            # zrで終了
            if button_right['zr']==1:
                json.dumps(result)
                print(result)
                # break




            # 現在の加速度データを前回のデータとして保存
            prev_accel = accel

            # ジャイロと加速度データを表示
            # print("加速度:", accel)
            # time.sleep(0.1)  # 0.1秒ごとにチェック
            # BPM/60秒/0.1（←上のやつ）
            soundTimer += (BPM/60)*0.1
            print(soundTimer)
            if (soundTimer/countsecond)>=BPM:
                print(f"{soundTimer/countsecond}秒経過しました")
                countsecond+=1
            endtime = datetime.now()
            dlapsedtime = endtime-start_time # 経過時間
            # print("経過時間：",dlapsedtime)
    except Exception as e:
        print(f"エラーが発生しました: {e}")

Joycon(72)
