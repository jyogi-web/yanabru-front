## 仮想環境(venv)
### 仮想環境作成
以下のコマンドを実行して仮想環境を作成する
```bash
python -m venv [仮想環境名]
```
### 仮想環境のアクティベート
#### Linux,Macの場合
```bash
 .\[仮想環境名]/bin/activate
```
#### Windowsの場合
```bash
.\[仮想環境名]\Scripts\activate
```

### 依存関係書き出し
```bash
pip freeze > requirements.txt
```

## 実行
```bash
python run.py
```

参考：(https://qiita.com/shun_sakamoto/items/7944d0ac4d30edf91fde)