# Python 3.12.9ベースイメージ
FROM python:3.12.9-slim

# 作業ディレクトリを設定
WORKDIR /app

# システムパッケージのインストール
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    build-essential \
    coinor-cbc \
    coinor-libcbc-dev \
    && rm -rf /var/lib/apt/lists/*

# uvのインストール
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Gurobiのインストール（x86_64版）
RUN wget https://packages.gurobi.com/12.0/gurobi12.0.3_linux64.tar.gz -O /tmp/gurobi12.0.3_linux64.tar.gz \
    && mkdir -p /opt \
    && tar xvfz /tmp/gurobi12.0.3_linux64.tar.gz -C /opt \
    && rm /tmp/gurobi12.0.3_linux64.tar.gz

# Gurobi環境変数の設定
ENV GUROBI_HOME=/opt/gurobi1000/linux64
ENV PATH=$PATH:$GUROBI_HOME/bin
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$GUROBI_HOME/lib

# CBCソルバーのパス設定（aptでインストールしたCBCを使用）
ENV CBC_PATH=/usr/bin/cbc

# プロジェクトファイルのコピー
COPY pyproject.toml uv.lock ./

# 依存関係のインストール
RUN uv sync --frozen --no-dev

# アプリケーションコードのコピー
COPY . .

# Cloud RunのPORT環境変数に対応（デフォルトは8080）
ENV PORT=8080

# アプリケーションの起動
# Cloud RunはPORT環境変数を自動的に設定するため、それを使用
CMD sh -c "PYTHONPATH=./src uv run uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"
