# 배포 가이드

이 문서는 ExcitonBindingEnergy_ElliottModel을 프로덕션 환경에 배포하는 방법을 설명합니다.

## 아키텍처

- **프론트엔드**: Vercel에 배포 (https://elliott-model.vercel.app/)
- **백엔드**: Railway 또는 Render에 배포 (FastAPI)

## 백엔드 배포

### 방법 1: Railway 배포 (권장)

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
     ALLOWED_ORIGINS=https://elliott-model.vercel.app,http://localhost:3000
     ```

3. **배포 확인**
   - 배포가 완료되면 Railway가 자동으로 URL 생성 (예: `https://your-app.railway.app`)
   - 이 URL을 복사해두세요

### 방법 2: Render 배포

1. **Render 계정 생성 및 서비스 생성**
   - https://render.com 접속
   - GitHub 계정으로 로그인
   - "New +" > "Web Service" 선택
   - 저장소 선택

2. **설정**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python3 api.py`
   - Environment Variables:
     ```
     ALLOWED_ORIGINS=https://elliott-model.vercel.app,http://localhost:3000
     ```

3. **배포 확인**
   - 배포가 완료되면 Render가 자동으로 URL 생성 (예: `https://your-app.onrender.com`)
   - 이 URL을 복사해두세요

## 프론트엔드 배포 (Vercel)

### 환경 변수 설정

1. **Vercel 대시보드 접속**
   - https://vercel.com/dashboard
   - 프로젝트 선택

2. **환경 변수 추가**
   - Settings > Environment Variables
   - 새 환경 변수 추가:
     - Name: `VITE_API_BASE_URL`
     - Value: 백엔드 API URL (Railway 또는 Render에서 받은 URL)
     - Environment: Production, Preview, Development 모두 선택

3. **재배포**
   - Deployments 탭에서 최신 배포 선택
   - "Redeploy" 클릭

## 배포 확인

1. **백엔드 확인**
   - `https://your-backend-url/api/health` 접속
   - `{"status":"ok"}` 응답 확인

2. **프론트엔드 확인**
   - https://elliott-model.vercel.app/ 접속
   - 파일 업로드 및 분석 기능 테스트

## 문제 해결

### CORS 오류

백엔드의 `ALLOWED_ORIGINS` 환경 변수에 프론트엔드 URL이 포함되어 있는지 확인하세요.

### 404 오류

프론트엔드의 `VITE_API_BASE_URL` 환경 변수가 올바르게 설정되었는지 확인하세요.

### 백엔드 연결 실패

1. 백엔드 서버가 실행 중인지 확인
2. 백엔드 URL이 올바른지 확인
3. 브라우저 콘솔에서 네트워크 오류 확인

