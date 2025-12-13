# Optimisation API

## Run Local Server

```shell
PYTHONPATH=./src uv run uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

docker-composeがあるディレクトリから実行する場合
```shell
docker-compose exec fastapi sh -c "cd /workspaces/timetable/fastapi && PYTHONPATH=./src uv run uvicorn main:app --reload --host 0.0.0.0 --port 8001"
```

## OpenAPI

[http://localhost:8001/docs](http://localhost:8001/docs)