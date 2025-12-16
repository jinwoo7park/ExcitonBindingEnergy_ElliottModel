# Railway 전용 배포 가이드 (권장)

이 프로젝트는 **Railway에서 프론트엔드와 백엔드를 모두 배포**합니다.

## 배포 구조

- **Railway**: 프론트엔드(React + Vite) + 백엔드(FastAPI) 모두 배포
- **단일 서비스**: 하나의 Railway 서비스에서 모든 것을 처리
- **크기 제한 없음**: Python 패키지 크기 제한 문제 없음 (Vercel의 250MB 제한 우회)

## Railway 배포 (이미 설정됨)

### 현재 설정

Railway는 이미 `nixpacks.toml`과 `railway.json`을 통해 설정되어 있습니다:

**nixpacks.toml:**
- Node.js와 Python 설치
- 프론트엔드 빌드 (`pnpm build`)
- Python 의존성 설치 (`pip install -r requirements.txt`)
- FastAPI 서버 시작 (`python3 -m api.index`)

**railway.json:**
- 빌드 명령: `pnpm install && pnpm build && pip install -r requirements.txt`
- 시작 명령: `python3 -m api.index`

### 배포 확인

Railway 배포 URL: `https://web-production-af7d7.up.railway.app`

- 프론트엔드: `https://web-production-af7d7.up.railway.app/`
- 백엔드 API: `https://web-production-af7d7.up.railway.app/api/`
- Health check: `https://web-production-af7d7.up.railway.app/api/health`

### 작동 방식

1. **빌드 단계**:
   - Node.js 설치 및 프론트엔드 의존성 설치 (`pnpm install`)
   - 프론트엔드 빌드 (`pnpm build`) → `dist/` 폴더 생성
   - Python 의존성 설치 (`pip install -r requirements.txt`)

2. **실행 단계**:
   - FastAPI 서버 시작 (`python3 -m api.index`)
   - FastAPI가 `dist/` 폴더의 정적 파일을 서빙
   - `/api/*` 경로는 FastAPI 엔드포인트로 라우팅
   - 나머지 경로는 `dist/index.html`로 라우팅 (SPA)

## 장점

✅ **단일 배포 플랫폼**: Railway 하나로 모든 것을 관리
✅ **크기 제한 없음**: Python 패키지(numpy, scipy, matplotlib) 크기 제한 문제 없음
✅ **간단한 설정**: 추가 환경 변수 설정 불필요
✅ **CORS 문제 없음**: 같은 도메인에서 서빙되므로 CORS 설정 불필요
✅ **비용 효율**: 하나의 서비스만 운영

## Vercel과의 비교

| 항목 | Railway | Vercel |
|------|---------|--------|
| Python 패키지 크기 제한 | 없음 | 250MB (초과 시 오류) |
| 배포 플랫폼 | 단일 (Railway) | 분리 (Vercel + Railway) |
| 설정 복잡도 | 낮음 | 높음 (환경 변수 등) |
| CORS 설정 | 불필요 | 필요 |
| 빌드 속도 | 중간 | 빠름 (프론트엔드만) |

## 로컬 개발

로컬 개발은 기존과 동일합니다:

```bash
# 프론트엔드 + 백엔드 동시 실행
pnpm run dev:all

# 또는 수동으로
# 터미널 1
python3 -m api.index

# 터미널 2
pnpm dev
```

## Railway 환경 변수 설정 (선택사항)

필요한 경우 Railway 대시보드에서 환경 변수를 설정할 수 있습니다:

- `PORT`: Railway가 자동으로 설정 (변경 불필요)
- `ALLOWED_ORIGINS`: CORS 허용 도메인 (기본적으로 모든 도메인 허용)

## 문제 해결

### 빌드 실패

Railway 로그에서 확인:
- `pnpm build` 실행 여부
- `dist/` 폴더 생성 여부
- Python 패키지 설치 성공 여부

### 정적 파일이 로드되지 않음

- `api/index.py`의 `dist` 폴더 경로 확인
- Railway 로그에서 "Static files mounted" 메시지 확인

## 결론

**Railway 전용 배포를 권장합니다.**

- ✅ 설정이 간단함
- ✅ 크기 제한 없음
- ✅ 추가 환경 변수 불필요
- ✅ CORS 문제 없음

Vercel을 사용하지 않으려면 Vercel 프로젝트를 비활성화하거나 삭제하면 됩니다.

