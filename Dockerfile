# Python 3.8のベースイメージを使用
FROM python:3.8-slim

# 作業ディレクトリを作成
WORKDIR /app

# 依存関係をインストール
COPY /app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションファイルをコピー
COPY . .

# コンテナ起動時の実行コマンド
CMD ["flask", "run", "--host=0.0.0.0", "--port=5002", "--reload"]
