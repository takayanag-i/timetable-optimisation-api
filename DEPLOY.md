# Cloud Run デプロイ手順（GitHub直接デプロイ）

このドキュメントでは、GitHubから直接Google Cloud Runにデプロイする手順を説明します。

## 前提条件

1. Google Cloud SDK (gcloud) がインストールされていること
2. GitHubリポジトリが作成されていること
3. Google Cloudプロジェクトが作成されていること
4. 必要な権限（Cloud Run Admin、Cloud Build Editor等）があること
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

# Cloud Build API
gcloud services enable cloudbuild.googleapis.com

# Container Registry API（一時的なイメージ保存用）
gcloud services enable containerregistry.googleapis.com
```

### 3. Cloud Buildサービスアカウントに権限を付与

```bash
PROJECT_ID="your-project-id"
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

# Cloud Run Admin権限を付与
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
    --role="roles/run.admin"

# Service Account User権限を付与
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"
```

### 4. 環境変数の設定（Secret Managerを使用 - 推奨）

```bash
# Secretを作成
echo -n "your-wlsaccessid" | gcloud secrets create wlsaccessid --data-file=-
echo -n "your-wlssecret" | gcloud secrets create wlssecret --data-file=-
echo -n "your-licenseid" | gcloud secrets create licenseid --data-file=-

# Cloud BuildサービスアカウントにSecretへのアクセス権限を付与
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
gcloud secrets add-iam-policy-binding wlsaccessid \
    --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
gcloud secrets add-iam-policy-binding wlssecret \
    --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
gcloud secrets add-iam-policy-binding licenseid \
    --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

## デプロイ方法

### 方法1: GitHub Actionsを使用（推奨）

GitHub Actionsで自動デプロイする方法です。最もシンプルで推奨される方法です。

#### セットアップ

1. **サービスアカウントの作成と権限付与**

```bash
PROJECT_ID="your-project-id"

# サービスアカウントを作成
gcloud iam service-accounts create github-actions \
    --display-name="GitHub Actions Service Account"

# 権限を付与
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-actions@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"

# JSONキーを生成
gcloud iam service-accounts keys create key.json \
    --iam-account=github-actions@${PROJECT_ID}.iam.gserviceaccount.com
```

2. **GitHub Secretsの設定**

GitHubリポジトリの Settings → Secrets and variables → Actions で以下を設定：

- `GCP_PROJECT_ID`: Google CloudプロジェクトID
- `GCP_SA_KEY`: 上記で作成したkey.jsonの内容
- `WLSACCESSID`: GurobiライセンスID
- `WLSSECRET`: Gurobiライセンスシークレット
- `LICENSEID`: GurobiライセンスID

3. **ワークフローファイルの確認**

`.github/workflows/deploy-cloud-run.yml` が既に作成されています。必要に応じて環境変数を調整してください。

#### デプロイの実行

mainブランチにプッシュすると自動的にデプロイが開始されます：

```bash
git add .
git commit -m "Deploy to Cloud Run"
git push origin main
```

---

### 方法2: Cloud Buildトリガーを使用

GitHubへのプッシュをトリガーにCloud Buildで自動デプロイする方法です。

#### セットアップ

1. **GitHubリポジトリとの接続**

```bash
# GitHub接続を作成（初回のみ）
gcloud builds triggers create github \
    --name="deploy-timetable-api" \
    --repo-name="your-repo-name" \
    --repo-owner="your-github-username" \
    --branch-pattern="^main$" \
    --build-config="cloudbuild-github.yaml" \
    --region="asia-northeast1"
```

または、[Cloud Console](https://console.cloud.google.com/cloud-build/triggers) からUIで設定：
1. 「トリガーを接続」をクリック
2. GitHubを選択し、認証を行う
3. リポジトリを選択
4. 設定を完了

2. **cloudbuild-github.yamlの設定**

`cloudbuild-github.yaml` のsubstitutionsに環境変数を設定するか、Cloud Buildトリガーの設定で環境変数を指定します。

#### デプロイの実行

GitHubのmainブランチにプッシュすると、自動的にデプロイが開始されます：

```bash
git add .
git commit -m "Deploy to Cloud Run"
git push origin main
```

#### デプロイの確認

```bash
# Cloud Buildの履歴を確認
gcloud builds list --limit=5

# 最新のビルドログを確認
gcloud builds log $(gcloud builds list --limit=1 --format="value(id)")

# Cloud Runサービスの状態を確認
gcloud run services describe timetable-api --region asia-northeast1
```

---

### 方法3: ソースベースデプロイ（gcloudコマンド）

ローカルからソースコードを直接デプロイする方法です。

#### セットアップ

```bash
# プロジェクトIDを設定
PROJECT_ID="your-project-id"
SERVICE_NAME="timetable-api"
REGION="asia-northeast1"

# 環境変数を設定
export WLSACCESSID="your-wlsaccessid"
export WLSSECRET="your-wlssecret"
export LICENSEID="your-licenseid"
```

#### デプロイの実行

```bash
# デプロイスクリプトを使用
./deploy-github.sh $PROJECT_ID $SERVICE_NAME $REGION

# または、直接gcloudコマンドを使用
gcloud run deploy $SERVICE_NAME \
    --source . \
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

#### 注意点

- ソースベースデプロイは、Cloud Buildを使用して自動的にビルドします
- ビルド時間は通常5-10分かかります
- ビルドログはCloud Buildで確認できます

---

## 環境変数の更新

Cloud Runサービスに環境変数を更新するには：

```bash
gcloud run services update timetable-api \
    --region asia-northeast1 \
    --update-env-vars "WLSACCESSID=your-wlsaccessid,WLSSECRET=your-wlssecret,LICENSEID=your-licenseid,CBC_PATH=/usr/bin/cbc"
```

### Secret Managerを使用する場合（推奨）

より安全に環境変数を管理するには、Secret Managerを使用します：

```bash
# Secretを作成（既に作成済みの場合はスキップ）
echo -n "your-wlsaccessid" | gcloud secrets create wlsaccessid --data-file=-
echo -n "your-wlssecret" | gcloud secrets create wlssecret --data-file=-
echo -n "your-licenseid" | gcloud secrets create licenseid --data-file=-

# Cloud RunサービスにSecretをマウント
gcloud run services update timetable-api \
    --region asia-northeast1 \
    --update-secrets WLSACCESSID=wlsaccessid:latest,WLSSECRET=wlssecret:latest,LICENSEID=licenseid:latest
```

---

## リソース設定

デフォルトのリソース設定：
- **メモリ**: 2Gi
- **CPU**: 2
- **タイムアウト**: 3600秒（1時間）
- **最大インスタンス数**: 10

必要に応じて調整：

```bash
gcloud run services update timetable-api \
    --region asia-northeast1 \
    --memory 4Gi \
    --cpu 4 \
    --timeout 7200 \
    --max-instances 20
```

---

## デプロイの確認

### サービスURLの取得

```bash
gcloud run services describe timetable-api \
    --region asia-northeast1 \
    --format="value(status.url)"
```

### ヘルスチェック

```bash
SERVICE_URL=$(gcloud run services describe timetable-api --region asia-northeast1 --format="value(status.url)")
curl $SERVICE_URL/docs
```

### ログの確認

```bash
gcloud run services logs read timetable-api --region asia-northeast1
```

---

## トラブルシューティング

### 1. ビルドエラー

- Dockerfileの構文を確認
- 依存関係が正しくインストールされているか確認
- Cloud Buildのログを確認: `gcloud builds log BUILD_ID`

### 2. 起動エラー

- 環境変数が正しく設定されているか確認
- ポート設定（Cloud RunはPORT環境変数を使用）を確認
- ログを確認: `gcloud run services logs read timetable-api --region asia-northeast1`

### 3. Gurobiライセンスエラー

- WLSACCESSID、WLSSECRET、LICENSEIDが正しく設定されているか確認
- Gurobiライセンスが有効であることを確認
- ネットワーク接続を確認（Webライセンスサーバーを使用する場合）

### 4. CBCソルバーエラー

- CBC_PATH環境変数が正しく設定されているか確認（デフォルト: /usr/bin/cbc）
- CBCが正しくインストールされているか確認

### 5. 権限エラー

- Cloud Buildサービスアカウントに適切な権限が付与されているか確認
- IAMポリシーを確認: `gcloud projects get-iam-policy $PROJECT_ID`

### 6. デプロイタイムアウト

- ビルド時間が長い場合は、Cloud Buildのタイムアウト設定を調整
- `cloudbuild-github.yaml` の `machineType` を変更: `machineType: 'E2_HIGHCPU_8'`

---

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

---

## 更新デプロイ

コードを更新した後、再度デプロイ：

### GitHub Actionsの場合
mainブランチにプッシュするだけで自動デプロイされます。

### Cloud Buildトリガーの場合
mainブランチにプッシュするだけで自動デプロイされます。

### ソースベースデプロイの場合
```bash
./deploy-github.sh $PROJECT_ID $SERVICE_NAME $REGION
```

---

## 参考リンク

- [Cloud Run ドキュメント](https://cloud.google.com/run/docs)
- [Cloud Build ドキュメント](https://cloud.google.com/build/docs)
- [Cloud Run ソースベースデプロイ](https://cloud.google.com/run/docs/deploying/source-code)
- [GitHub Actions for Google Cloud](https://github.com/google-github-actions)
- [Gurobi ドキュメント](https://www.gurobi.com/documentation/)
- [CBC ソルバー](https://github.com/coin-or/Cbc)
