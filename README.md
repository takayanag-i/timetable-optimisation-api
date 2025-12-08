# Optimisation API

時間割編成を最適化するためのREST APIです。

## ローカル開発

### サーバーの起動

```shell
PYTHONPATH=./src uv run uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

docker-composeがあるディレクトリから実行する場合
```shell
docker-compose exec fastapi sh -c "cd /workspaces/timetable/fastapi && PYTHONPATH=./src uv run uvicorn main:app --reload --host 0.0.0.0 --port 8001"
```

### OpenAPI ドキュメント

[http://localhost:8001/docs](http://localhost:8001/docs)

## Cloud Runへのデプロイ

GitHubから直接Cloud Runにデプロイします。詳細は [DEPLOY.md](./DEPLOY.md) を参照してください。

### クイックスタート

1. **GitHub Actionsを使用（推奨）**
   - `.github/workflows/deploy-cloud-run.yml` が設定済み
   - GitHub Secretsに必要な環境変数を設定
   - mainブランチにプッシュすると自動デプロイ

2. **Cloud Buildトリガーを使用**
   - `cloudbuild-github.yaml` を使用してCloud Buildトリガーを設定
   - GitHubへのプッシュで自動デプロイ

3. **ソースベースデプロイ**
   - `./deploy-github.sh` を実行してローカルからデプロイ