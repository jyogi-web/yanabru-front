## Dockerコンテナのビルドと実行
Docker Composeを使用して、コンテナをビルドしてバックグラウンドで実行します：
```
docker-compose up -d --build

```

`http://localhost:5002/`にアクセス

コンテナを停止するには、次のコマンドを使用します：
```
docker-compose down
```

## 必要なライブラリの追加
追加のPythonライブラリをインストールする場合は、`requirements.txt`ファイルにライブラリ名を追加します。
