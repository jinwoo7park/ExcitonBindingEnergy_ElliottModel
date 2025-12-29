# Fly.io 404 오류 해결 가이드

배포는 성공했지만 404 오류가 발생하는 경우의 해결 방법입니다.

## 문제 원인

`Dockerfile`에서 `python3 -m api.index`로 실행하면 `api/index.py`의 `if __name__ == "__main__":` 블록이 실행되지 않아 uvicorn 서버가 시작되지 않습니다.

## 해결 방법

### 1. Dockerfile 수정

`Dockerfile`의 CMD를 다음과 같이 수정하세요:

```dockerfile
# 기본 명령어
# PORT 환경 변수를 사용하여 uvicorn 실행
CMD ["sh", "-c", "uvicorn api.index:app --host 0.0.0.0 --port ${PORT:-8080}"]
```

### 2. 변경사항 배포

```bash
fly deploy
```

### 3. 로그 확인

배포 후 로그를 확인하여 서버가 정상적으로 시작되었는지 확인:

```bash
fly logs
```

정상적으로 시작되면 다음과 같은 로그가 보입니다:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8080
```

### 4. 상태 확인

```bash
fly status
fly checks list
```

### 5. 브라우저에서 확인

- https://your-app-name.fly.dev/api/health
- https://your-app-name.fly.dev/api

정상적으로 작동하면:
- `/api/health` → `{"status": "ok", "mode": "serverless"}`
- `/api` → `{"message": "Exciton Binding Energy Calculator API", "version": "1.0.0"}`

