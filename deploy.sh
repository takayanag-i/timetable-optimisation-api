#!/bin/bash

# Cloud Runデプロイスクリプト
# 使用方法: ./deploy.sh [PROJECT_ID] [SERVICE_NAME] [REGION]

set -e

# デフォルト値
PROJECT_ID=${1:-"your-project-id"}
SERVICE_NAME=${2:-"timetable-api"}
REGION=${3:-"asia-northeast1"}

# 環境変数の確認
if [ -z "$WLSACCESSID" ] || [ -z "$WLSSECRET" ] || [ -z "$LICENSEID" ]; then
    echo "警告: Gurobiライセンス環境変数が設定されていません"
    echo "WLSACCESSID, WLSSECRET, LICENSEID を設定してください"
    read -p "続行しますか? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "プロジェクトID: $PROJECT_ID"
echo "サービス名: $SERVICE_NAME"
echo "リージョン: $REGION"

# gcloud認証の確認
echo "gcloud認証を確認しています..."
gcloud config set project $PROJECT_ID

# Artifact Registryリポジトリの作成（存在しない場合）
REPOSITORY="timetable-api"
echo "Artifact Registryリポジトリを確認しています..."
if ! gcloud artifacts repositories describe $REPOSITORY --location=$REGION --format="value(name)" 2>/dev/null; then
    echo "Artifact Registryリポジトリを作成しています..."
    gcloud artifacts repositories create $REPOSITORY \
        --repository-format=docker \
        --location=$REGION \
        --description="Timetable API Docker images"
fi

# Dockerイメージのビルド
IMAGE_TAG="$REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$SERVICE_NAME:latest"
echo "Dockerイメージをビルドしています: $IMAGE_TAG"
docker build -t $IMAGE_TAG .

# Dockerイメージのプッシュ
echo "Dockerイメージをプッシュしています..."
docker push $IMAGE_TAG

# Cloud Runへのデプロイ
echo "Cloud Runにデプロイしています..."
gcloud run deploy $SERVICE_NAME \
    --image $IMAGE_TAG \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --port 8080 \
    --memory 2Gi \
    --cpu 2 \
    --timeout 3600 \
    --max-instances 10 \
    --set-env-vars "WLSACCESSID=$WLSACCESSID,WLSSECRET=$WLSSECRET,LICENSEID=$LICENSEID,CBC_PATH=/usr/bin/cbc"

echo "デプロイが完了しました！"
echo "サービスURLを取得中..."
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)")
echo "サービスURL: $SERVICE_URL"
