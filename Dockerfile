# ベースイメージを指定
FROM python:3.9

# 必要なファイルをコピー
COPY requirements.txt requirements.txt
COPY app app

# 依存関係をインストール
RUN pip install -r requirements.txt

# ポート開放 (uvicornで指定したポート)
EXPOSE 8080

# アプリケーションを起動
CMD ["python", "app/app.py"]