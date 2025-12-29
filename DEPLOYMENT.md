# 배포 가이드

이 문서는 ExcitonBindingEnergy_ElliottModel을 배포하는 다양한 방법을 설명합니다.

## 배포 옵션 비교

| 방법 | 플랫폼 | 장점 | 단점 | 추천도 |
|------|--------|------|------|--------|
| **Fly.io 단일 배포** | Fly.io | 무료 티어 제공, 전 세계 CDN, 빠른 배포, 추천 | 무료 티어 제한 (3 VM), 설정 필요 | ⭐⭐⭐⭐⭐ |
| **Railway 단일 배포** | Railway | 크기 제한 없음, CORS 불필요, 설정 간단 | 월 $5 크레딧 (소규모는 무료) | ⭐⭐⭐⭐ |
| **Render 단일 배포** | Render | 완전 무료 | 15분 비활성 시 sleep | ⭐⭐⭐ |

## 방법 1: Fly.io 단일 배포 (추천) ⭐⭐⭐⭐⭐

Fly.io에서 프론트엔드와 백엔드를 모두 배포하는 방법입니다.

**상세한 단계별 가이드는 [FLY_IO_DEPLOYMENT.md](./FLY_IO_DEPLOYMENT.md)를 참고하세요.**

### 장점
- ✅ 무료 티어 제공 (월 3개 VM, 3GB 전송량)
- ✅ 전 세계 CDN, 빠른 응답 속도
- ✅ CORS 설정 불필요 (같은 도메인에서 서빙)
- ✅ Docker 기반 배포 (표준 호환성)
- ✅ 자동 HTTPS

### 빠른 시작

1. **Fly.io CLI 설치 및 로그인**
   ```bash
   curl -L https://fly.io/install.sh | sh
   fly auth login
   ```

2. **fly.toml 설정**
   - `app = "your-app-name"` 고유한 이름으로 변경

3. **배포**
   ```bash
   fly launch  # 처음 배포 시
   # 또는
   fly deploy  # 이후 배포
   ```

4. **확인**
   - 기본 URL: `https://your-app-name.fly.dev`
   - `fly status`로 상태 확인

## 방법 1-1: Railway 단일 배포 ⭐⭐⭐⭐

Railway에서 프론트엔드와 백엔드를 모두 배포하는 방법입니다.

### 장점
- ✅ 크기 제한 없음 (Python 패키지 크기 제한 문제 없음)
- ✅ CORS 설정 불필요 (같은 도메인에서 서빙)
- ✅ 설정 간단 (하나의 서비스로 관리)
- ✅ 월 $5 무료 크레딧 (소규모 프로젝트는 무료로 충분)

### 배포 방법

1. **Railway 계정 생성**
   - https://railway.app 접속
   - GitHub 계정으로 로그인

2. **프로젝트 생성**
   - "New Project" 클릭
   - "Deploy from GitHub repo" 선택
   - 저장소 선택
   - "Deploy Now" 클릭

3. **자동 설정 확인**
   - Railway는 `nixpacks.toml`과 `railway.json`을 자동으로 인식합니다
   - 빌드: `pnpm install && pnpm build && pip install -r requirements.txt`
   - 시작: `python3 -m api.index`

4. **도메인 확인**
   - Settings > Networking 탭
   - "Generate Domain" 클릭
   - 생성된 URL 복사 (예: `https://your-app.up.railway.app`)

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

### 환경 변수 설정 (선택사항)

Railway 대시보드에서:
- `PORT`: Railway가 자동으로 설정 (변경 불필요)
- `ALLOWED_ORIGINS`: CORS 허용 도메인 (기본적으로 모든 도메인 허용)


### 작동 방식

1. **빌드 단계** (Dockerfile 기반):
   - Python 3.11 및 Node.js 설치
   - Python 의존성 설치 (`pip install -r requirements.txt`)
   - Node.js 의존성 설치 (`pnpm install`)
   - 프론트엔드 빌드 (`pnpm build`) → `dist/` 폴더 생성

2. **실행 단계**:
   - FastAPI 서버 시작 (`python3 -m api.index`)
   - PORT 환경 변수는 자동으로 8080으로 설정됨
   - FastAPI가 `dist/` 폴더의 정적 파일을 서빙
   - `/api/*` 경로는 FastAPI 엔드포인트로 라우팅
   - 나머지 경로는 `dist/index.html`로 라우팅 (SPA)

### 환경 변수 설정 (선택사항)

Fly.io 단일 배포 시 CORS 설정은 필요 없습니다 (같은 도메인).

로컬 개발을 위한 환경 변수만 필요한 경우:
```bash
# 환경 변수 확인
fly secrets list

# 환경 변수 설정 (필요 시)
fly secrets set YOUR_VAR=value
```

### 무료 티어 제한

- **3개 VM**: 최대 3개의 가상 머신
- **3GB 전송량**: 월 3GB의 아웃바운드 트래픽
- **1GB 스토리지**: 볼륨 스토리지 1GB
- 소규모 프로젝트에는 충분합니다

### 주의사항

- Fly.io는 기본적으로 포트 8080을 사용합니다 (fly.toml에서 설정됨)
- `api/index.py`는 PORT 환경 변수를 읽으므로 자동으로 8080을 사용합니다
- 리전 선택: `icn` (서울), `nrt` (도쿄), `sin` (싱가포르) 등

## 방법 2: 분리 배포 (선택사항 - 복잡함)

프론트엔드와 백엔드를 별도로 배포하는 방법입니다. **단일 배포를 권장합니다.**

**참고**: 이 방법은 복잡하고 CORS 설정이 필요합니다. 가능하면 방법 1 (Fly.io 단일 배포)을 사용하세요.

### 백엔드 배포

#### 옵션 A: Railway (권장)

1. **Railway 계정 생성 및 프로젝트 생성**
   - https://railway.app 접속
   - GitHub 계정으로 로그인
   - "New Project" 클릭
   - "Deploy from GitHub repo" 선택
   - 저장소 선택

2. **환경 변수 설정**
   - Railway 대시보드에서 프로젝트 선택
   - Variables 탭에서 다음 환경 변수 추가:
     ```
     ALLOWED_ORIGINS=https://your-vercel-app.vercel.app,http://localhost:3000
     ```

3. **배포 확인**
   - 배포가 완료되면 Railway가 자동으로 URL 생성
   - 이 URL을 복사해두세요 (예: `https://your-app.railway.app`)

#### 옵션 B: Render (완전 무료)

1. **Render 계정 생성**
   - https://render.com 접속
   - GitHub 계정으로 로그인

2. **Web Service 생성**
   - "New +" > "Web Service" 클릭
   - GitHub 저장소 연결

3. **설정 입력**
   ```
   Name: exciton-binding-energy-api
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: python3 -m api.index
   ```

4. **환경 변수 추가**
   ```
   ALLOWED_ORIGINS=https://your-frontend-domain.com,http://localhost:3000
   ```

5. **배포 확인**
   - 배포가 완료되면 Render가 자동으로 URL 생성 (예: `https://your-app.onrender.com`)

### 프론트엔드 배포

프론트엔드는 Vercel, Netlify, 또는 다른 정적 호스팅 서비스에 배포할 수 있습니다.

1. **환경 변수 설정**
   - `VITE_API_BASE_URL`: 백엔드 API URL (예: `https://your-backend.onrender.com`)

2. **CORS 설정**
   - 백엔드의 `ALLOWED_ORIGINS` 환경 변수에 프론트엔드 도메인 추가

## 방법 3: Render 단일 배포 ⭐⭐⭐

Render에서 프론트엔드와 백엔드를 모두 배포하는 방법입니다.

### 장점
- ✅ 완전 무료 (제한 없음)
- ✅ 자동 HTTPS
- ✅ GitHub 연동

### 단점
- ⚠️ 15분 비활성 시 sleep (첫 요청이 느림)

### 배포 방법

1. **Render 계정 생성**
   - https://render.com 접속
   - GitHub 계정으로 로그인

2. **Web Service 생성**
   - "New +" > "Web Service" 클릭
   - GitHub 저장소 연결

3. **설정 입력**
   ```
   Name: exciton-binding-energy
   Environment: Python 3
   Build Command: pnpm install && pnpm build && pip install -r requirements.txt
   Start Command: python3 -m api.index
   ```

4. **환경 변수 추가**
   ```
   ALLOWED_ORIGINS=https://your-app.onrender.com,http://localhost:3000
   ```

5. **배포 확인**
   - 배포가 완료되면 Render가 자동으로 URL 생성

## 배포 확인

### Fly.io 단일 배포
- 프론트엔드: `https://your-app-name.fly.dev/`
- 백엔드 API: `https://your-app-name.fly.dev/api/`
- Health check: `https://your-app-name.fly.dev/api/health`

### Railway 단일 배포
- 프론트엔드: `https://your-app.up.railway.app/`
- 백엔드 API: `https://your-app.up.railway.app/api/`
- Health check: `https://your-app.up.railway.app/api/health`

### 분리 배포
- 백엔드: `https://your-backend-url/api/health` → `{"status":"ok"}` 응답 확인
- 프론트엔드: `https://your-frontend-domain.com/` → 파일 업로드 및 분석 기능 테스트

## 문제 해결

### CORS 오류
- **Fly.io/Railway 단일 배포**: CORS 문제 없음 (같은 도메인)
- **분리 배포**: 백엔드의 `ALLOWED_ORIGINS` 환경 변수에 프론트엔드 URL이 포함되어 있는지 확인

### 404 오류
- 단일 배포: 서버가 정상적으로 시작되었는지 확인 (`fly logs` 또는 배포 플랫폼 로그)
- 분리 배포: 프론트엔드의 `VITE_API_BASE_URL` 환경 변수가 올바르게 설정되었는지 확인
- 백엔드 URL이 올바른지 확인

### 백엔드 연결 실패
1. 백엔드 서버가 실행 중인지 확인 (`/api/health` 엔드포인트 확인)
2. 백엔드 URL이 올바른지 확인
3. 브라우저 콘솔에서 네트워크 오류 확인

### Render가 느린 경우
- 첫 요청은 sleep에서 깨어나느라 느릴 수 있음 (정상)
- UptimeRobot 같은 무료 서비스로 주기적 ping 설정 가능

### Railway 크레딧 부족
- Render 또는 Fly.io로 전환 고려
- 또는 사용량 확인 후 필요시 업그레이드

### Fly.io 배포 오류
- `fly.toml`의 앱 이름이 고유한지 확인
- Docker 빌드 로그 확인: `fly logs`
- 포트 설정 확인 (기본 8080)

### 빌드 실패
- Railway/Render 로그에서 확인:
  - `pnpm build` 실행 여부
  - `dist/` 폴더 생성 여부
  - Python 패키지 설치 성공 여부

### 정적 파일이 로드되지 않음
- `api/index.py`의 `dist` 폴더 경로 확인
- Railway/Render 로그에서 "Static files mounted" 메시지 확인

## 로컬 개발

로컬 개발은 모든 배포 방법과 동일합니다:

```bash
# 프론트엔드 + 백엔드 동시 실행
pnpm run dev:all

# 또는 수동으로
# 터미널 1
python3 -m api.index

# 터미널 2
pnpm dev
```

## 추천 구성

**가장 추천**: Fly.io 단일 배포
- ✅ 무료 티어 제공
- ✅ 전 세계 CDN, 빠른 속도
- ✅ CORS 문제 없음
- ✅ 설정 간단

**다른 옵션**: Railway 단일 배포
- ✅ 크기 제한 없음
- ✅ 월 $5 무료 크레딧 (소규모는 무료)
- ✅ 설정 간단

**완전 무료**: Render 단일 배포
- ✅ 완전 무료
- ⚠️ Sleep 있지만 무료

**고성능 필요**: Fly.io 단일 배포
- ✅ 전 세계 CDN
- ✅ 빠른 응답 속도
- ✅ 설정 간단
