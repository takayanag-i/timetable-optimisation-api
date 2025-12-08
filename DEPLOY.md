# Cloud Run デプロイ手順

このドキュメントでは、FastAPIアプリケーションをGoogle Cloud Runにデプロイする手順を説明します。

## 前提条件

1. Google Cloud SDK (gcloud) がインストールされていること
2. Dockerがインストールされていること
3. Google Cloudプロジェクトが作成されていること
4. 必要な権限（Cloud Run Admin、Artifact Registry Writer等）があること
5. Gurobiライセンス情報（WLSACCESSID、WLSSECRET、LICENSEID）があること

## 事前準備

### 1. gcloud認証とプロジェクト設定

```bash
# Google Cloudにログイン
gcloud auth login

# プロジェクトを設定
gcloud config set project YOUR_PROJECT_ID

# アプリケーションのデフォルト認証情報を設定
gcloud auth application-default login
```

### 2. 必要なAPIの有効化

```bash
# Cloud Run API
gcloud services enable run.googleapis.com

# Artifact Registry API
gcloud services enable artifactregistry.googleapis.com

# Cloud Build API（Cloud Buildを使用する場合）
gcloud services enable cloudbuild.googleapis.com
```

### 3. 環境変数の設定

Gurobiライセンス情報を環境変数に設定します：

```bash
export WLSACCESSID="your-wlsaccessid"
export WLSSECRET="your-wlssecret"
export LICENSEID="your-licenseid"
```

## デプロイ方法

### 方法1: デプロイスクリプトを使用（推奨）

```bash
# 環境変数を設定
export WLSACCESSID="your-wlsaccessid"
export WLSSECRET="your-wlssecret"
export LICENSEID="your-licenseid"

# デプロイスクリプトを実行
./deploy.sh PROJECT_ID SERVICE_NAME REGION

# 例:
./deploy.sh my-project-id timetable-api asia-northeast1
```

### 方法2: gcloudコマンドを直接使用

```bash
# プロジェクトIDとサービス名を設定
PROJECT_ID="your-project-id"
SERVICE_NAME="timetable-api"
REGION="asia-northeast1"
REPOSITORY="timetable-api"

# Artifact Registryリポジトリを作成（初回のみ）
gcloud artifacts repositories create $REPOSITORY \
    --repository-format=docker \
    --location=$REGION \
    --description="Timetable API Docker images"

# Dockerイメージをビルド
IMAGE_TAG="$REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$SERVICE_NAME:latest"
docker build -t $IMAGE_TAG .

# Dockerイメージをプッシュ
docker push $IMAGE_TAG

# Cloud Runにデプロイ
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
```

### 方法3: Cloud Buildを使用

```bash
# cloudbuild.yamlのsubstitutionsを更新
# 必要な環境変数をSecret Managerに保存（推奨）またはsubstitutionsに設定

# Cloud Buildを実行
gcloud builds submit --config=cloudbuild.yaml \
    --substitutions=_WLSACCESSID="your-wlsaccessid",_WLSSECRET="your-wlssecret",_LICENSEID="your-licenseid"
```

## 環境変数の設定

Cloud Runサービスに環境変数を設定するには：

```bash
gcloud run services update $SERVICE_NAME \
    --region $REGION \
    --update-env-vars "WLSACCESSID=your-wlsaccessid,WLSSECRET=your-wlssecret,LICENSEID=your-licenseid,CBC_PATH=/usr/bin/cbc"
```

### Secret Managerを使用する場合（推奨）

より安全に環境変数を管理するには、Secret Managerを使用します：

```bash
# Secretを作成
echo -n "your-wlsaccessid" | gcloud secrets create wlsaccessid --data-file=-
echo -n "your-wlssecret" | gcloud secrets create wlssecret --data-file=-
echo -n "your-licenseid" | gcloud secrets create licenseid --data-file=-

# Cloud RunサービスにSecretをマウント
gcloud run services update $SERVICE_NAME \
    --region $REGION \
    --update-secrets WLSACCESSID=wlsaccessid:latest,WLSSECRET=wlssecret:latest,LICENSEID=licenseid:latest
```

## リソース設定

デフォルトのリソース設定：
- **メモリ**: 2Gi
- **CPU**: 2
- **タイムアウト**: 3600秒（1時間）
- **最大インスタンス数**: 10

必要に応じて調整：

```bash
gcloud run services update $SERVICE_NAME \
    --region $REGION \
    --memory 4Gi \
    --cpu 4 \
    --timeout 7200 \
    --max-instances 20
```

## デプロイの確認

### サービスURLの取得

```bash
gcloud run services describe $SERVICE_NAME \
    --region $REGION \
    --format="value(status.url)"
```

### ヘルスチェック

```bash
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format="value(status.url)")
curl $SERVICE_URL/docs
```

### ログの確認

```bash
gcloud run services logs read $SERVICE_NAME --region $REGION
```

## トラブルシューティング

### 1. ビルドエラー

- Dockerfileの構文を確認
- 依存関係が正しくインストールされているか確認
- ログを確認: `docker build -t test-image .`

### 2. 起動エラー

- 環境変数が正しく設定されているか確認
- ポート設定（Cloud RunはPORT環境変数を使用）を確認
- ログを確認: `gcloud run services logs read $SERVICE_NAME --region $REGION`

### 3. Gurobiライセンスエラー

- WLSACCESSID、WLSSECRET、LICENSEIDが正しく設定されているか確認
- Gurobiライセンスが有効であることを確認
- ネットワーク接続を確認（Webライセンスサーバーを使用する場合）

### 4. CBCソルバーエラー

- CBC_PATH環境変数が正しく設定されているか確認（デフォルト: /usr/bin/cbc）
- CBCが正しくインストールされているか確認

## ローカルでのテスト

デプロイ前にローカルでDockerイメージをテスト：

```bash
# イメージをビルド
docker build -t timetable-api:local .

# 環境変数を設定して実行
docker run -p 8080:8080 \
    -e WLSACCESSID="your-wlsaccessid" \
    -e WLSSECRET="your-wlssecret" \
    -e LICENSEID="your-licenseid" \
    -e CBC_PATH="/usr/bin/cbc" \
    timetable-api:local

# ブラウザで http://localhost:8080/docs にアクセス
```

## 更新デプロイ

コードを更新した後、再度デプロイ：

```bash
# 方法1: デプロイスクリプトを使用
./deploy.sh PROJECT_ID SERVICE_NAME REGION

# 方法2: gcloudコマンドを使用
IMAGE_TAG="$REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$SERVICE_NAME:latest"
docker build -t $IMAGE_TAG .
docker push $IMAGE_TAG
gcloud run deploy $SERVICE_NAME --image $IMAGE_TAG --region $REGION
```

## 参考リンク

- [Cloud Run ドキュメント](https://cloud.google.com/run/docs)
- [Artifact Registry ドキュメント](https://cloud.google.com/artifact-registry/docs)
- [Gurobi ドキュメント](https://www.gurobi.com/documentation/)
- [CBC ソルバー](https://github.com/coin-or/Cbc)
