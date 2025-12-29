# Fly.io 배포 상세 가이드

이 문서는 Elliott Model 프로젝트를 Fly.io에 배포하는 **단계별 상세 가이드**입니다.

## 📋 목차

1. [사전 준비](#1-사전-준비)
2. [Fly.io CLI 설치](#2-flyio-cli-설치)
3. [Fly.io 계정 생성 및 로그인](#3-flyio-계정-생성-및-로그인)
4. [프로젝트 설정](#4-프로젝트-설정)
5. [배포 실행](#5-배포-실행)
6. [배포 확인](#6-배포-확인)
7. [환경 변수 설정](#7-환경-변수-설정)
8. [문제 해결](#8-문제-해결)

---

## 1. 사전 준비

배포 전에 확인해야 할 사항:

### ✅ 필요한 파일 확인

프로젝트 루트에 다음 파일들이 있어야 합니다:
- `Dockerfile` ✅ (이미 생성됨)
- `fly.toml` ✅ (이미 생성됨)
- `requirements.txt` ✅
- `package.json` ✅
- `api/index.py` ✅

### ✅ Git 저장소 확인

Fly.io는 Git 저장소에서 직접 배포할 수도 있지만, 여기서는 CLI를 통한 배포를 진행합니다.

```bash
# 현재 디렉토리 확인
pwd

# Git 상태 확인 (선택사항)
git status
```

---

## 2. Fly.io CLI 설치

### macOS

**방법 1: 공식 설치 스크립트 (추천)**

```bash
curl -L https://fly.io/install.sh | sh
```

설치 후 PATH에 추가 (터미널 재시작 또는 다음 명령 실행):

```bash
# zsh 사용 시
echo 'export FLYCTL_INSTALL="$HOME/.fly"' >> ~/.zshrc
echo 'export PATH="$FLYCTL_INSTALL/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# bash 사용 시
echo 'export FLYCTL_INSTALL="$HOME/.fly"' >> ~/.bashrc
echo 'export PATH="$FLYCTL_INSTALL/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

**방법 2: Homebrew**

```bash
brew install flyctl
```

**방법 3: 직접 다운로드**

```bash
# 최신 버전 확인 및 다운로드
# https://github.com/superfly/flyctl/releases
```

### Linux

```bash
curl -L https://fly.io/install.sh | sh
```

### Windows

**PowerShell 사용:**

```powershell
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

또는 **Winget 사용:**

```powershell
winget install -e --id Superfly.Flyctl
```

### 설치 확인

```bash
fly version
```

다음과 같은 출력이 나오면 성공:
```
flyctl v0.x.x windows/amd64
```

---

## 3. Fly.io 계정 생성 및 로그인

### 계정 생성

**처음 사용하는 경우:**

```bash
fly auth signup
```

브라우저가 자동으로 열리며 계정 생성 페이지로 이동합니다:
- 이메일 주소 입력
- 비밀번호 설정
- 이메일 인증 완료

**이미 계정이 있는 경우:**

```bash
fly auth login
```

브라우저가 열리며 로그인 페이지로 이동합니다.

### 로그인 확인

```bash
fly auth whoami
```

출력 예시:
```
you are logged in as your-email@example.com
```

---

## 4. 프로젝트 설정

### 4.1 fly.toml 파일 수정

프로젝트 루트의 `fly.toml` 파일을 엽니다:

```bash
# 파일 열기 (에디터 사용)
code fly.toml  # VS Code
# 또는
nano fly.toml  # nano
# 또는
vim fly.toml   # vim
```

**수정해야 할 부분:**

```toml
app = "your-app-name"  # 👈 이 부분을 고유한 앱 이름으로 변경
```

**앱 이름 규칙:**
- 소문자만 사용 (a-z)
- 숫자 사용 가능 (0-9)
- 하이픈(-) 사용 가능
- 공백이나 대문자 사용 불가
- 전 세계적으로 고유해야 함

**좋은 예:**
```toml
app = "elliott-model-jinwoo"
app = "exciton-binding-energy"
app = "my-elliott-app-2024"
```

**나쁜 예:**
```toml
app = "Elliott Model"  # 공백, 대문자 사용 불가
app = "elliott_model"  # 언더스코어 사용 불가 (하이픈 사용)
app = "elliott.model"  # 점 사용 불가
```

**리전 설정 (선택사항):**

```toml
primary_region = "icn"  # 서울 리전
```

사용 가능한 리전:
- `icn` - 서울 (추천)
- `nrt` - 도쿄
- `sin` - 싱가포르
- `hkg` - 홍콩
- `iad` - 버지니아 (미국)
- `lhr` - 런던 (영국)
- 기타: [Fly.io 리전 목록](https://fly.io/docs/reference/regions/)

### 4.2 설정 확인

```bash
# fly.toml 파일 내용 확인
cat fly.toml
```

---

## 5. 배포 실행

### 5.1 첫 번째 배포 (앱 생성 + 배포)

**방법 1: fly launch 사용 (추천)**

```bash
fly launch
```

이 명령은 다음을 수행합니다:
1. 앱 이름 확인/생성
2. 리전 선택 (대화형 프롬프트)
3. PostgreSQL 등 추가 서비스 선택 (선택사항 - 여기서는 No)
4. Docker 빌드 시작
5. 배포 시작

**프롬프트 예시:**

```
? App Name (leave blank to use an auto-generated name): elliott-model-jinwoo
? Select region: icn (Seoul, South Korea)
? Would you like to set up a Postgresql database now? No
? Would you like to set up an Upstash Redis database now? No
? Create .dockerignore from .gitignore? Yes
? Would you like to deploy now? Yes
```

**방법 2: 수동으로 앱 생성 후 배포**

```bash
# 1. 앱 생성
fly apps create your-app-name

# 2. 배포
fly deploy
```

### 5.2 배포 과정

배포 중 다음 단계가 진행됩니다:

```
==> Building image
Remote builder fly-builder-xxx ready
==> Creating build context
==> Building image with Docker
...
[1/7] FROM docker.io/library/python:3.11-slim
[2/7] RUN apt-get update && apt-get install -y...
[3/7] RUN curl -fsSL https://deb.nodesource.com/setup_20.x...
...
==> Pushing image to fly
...
==> Creating release
...
==> Monitoring deployment
...
```

**빌드 시간:**
- 처음 빌드: 5-10분 (Docker 이미지 다운로드 + 빌드)
- 이후 빌드: 3-5분 (변경사항만 빌드)

### 5.3 배포 성공 확인

배포가 성공하면 다음과 같은 메시지가 출력됩니다:

```
✓ Deployment complete!
✓ App is available at https://your-app-name.fly.dev
```

---

## 6. 배포 확인

### 6.1 기본 확인

**앱 상태 확인:**

```bash
fly status
```

출력 예시:
```
App
  Name     = elliott-model-jinwoo
  Owner    = personal
  Hostname = elliott-model-jinwoo.fly.dev
  Region   = icn
  Image    = elliott-model-jinwoo:deployment-xxx
  Platform = machines

Machines
PROCESS ID              VERSION REGION  STATE   ROLE    CHECKS  LAST UPDATED
app     xxxxxxx         1       icn     started         1/1     2024-01-01T12:00:00Z
```

**헬스 체크 확인:**

```bash
fly checks list
```

**로그 확인:**

```bash
# 실시간 로그
fly logs

# 최근 로그만 보기
fly logs --limit 50
```

### 6.2 웹 브라우저에서 확인

1. **메인 페이지:**
   ```
   https://your-app-name.fly.dev
   ```
   - 프론트엔드가 정상적으로 로드되는지 확인

2. **API 헬스 체크:**
   ```
   https://your-app-name.fly.dev/api/health
   ```
   - 다음 응답이 나와야 함:
   ```json
   {"status": "ok", "mode": "serverless"}
   ```

3. **API 루트:**
   ```
   https://your-app-name.fly.dev/api
   ```
   - 다음 응답이 나와야 함:
   ```json
   {"message": "Exciton Binding Energy Calculator API", "version": "1.0.0"}
   ```

### 6.3 기능 테스트

1. 파일 업로드 기능 테스트
2. 분석 기능 테스트
3. 결과 다운로드 기능 테스트

---

## 7. 환경 변수 설정

### 7.1 환경 변수 확인

현재 설정된 환경 변수 확인:

```bash
fly secrets list
```

### 7.2 환경 변수 설정

**CORS 설정 (분리 배포 시 필요):**

```bash
fly secrets set ALLOWED_ORIGINS=https://your-frontend.vercel.app,http://localhost:3000
```

**여러 환경 변수 한 번에 설정:**

```bash
fly secrets set \
  ALLOWED_ORIGINS=https://your-frontend.vercel.app \
  ANOTHER_VAR=value
```

### 7.3 환경 변수 삭제

```bash
fly secrets unset ALLOWED_ORIGINS
```

### 7.4 환경 변수 변경 후 재배포

환경 변수를 변경하면 자동으로 재배포됩니다. 로그 확인:

```bash
fly logs
```

---

## 8. 문제 해결

### 8.1 배포 실패

**문제: 빌드 실패**

```bash
# 자세한 로그 확인
fly logs

# 또는 빌드 로그만 확인
fly deploy --verbose
```

**일반적인 원인:**
- Dockerfile 오류
- 의존성 설치 실패
- 메모리 부족

**해결:**
- 로그에서 오류 메시지 확인
- Dockerfile 수정 후 재배포

**문제: 포트 오류**

확인 사항:
- `fly.toml`의 `internal_port`가 8080인지 확인
- `api/index.py`가 `PORT` 환경 변수를 읽는지 확인

```bash
# 포트 확인
cat fly.toml | grep internal_port
```

### 8.2 앱이 시작되지 않음

**로그 확인:**

```bash
fly logs
```

**일반적인 원인:**
- 포트 미스매치
- Python 모듈 경로 오류
- 의존성 누락

**해결:**
```bash
# 로컬에서 테스트
python3 -m api.index

# 포트 설정 확인
echo $PORT  # 로컬에서는 비어있음 (정상)
```

### 8.3 정적 파일이 로드되지 않음

**확인:**
```bash
# dist 폴더가 빌드되었는지 확인
fly ssh console -C "ls -la /workspace/dist"
```

**해결:**
- Dockerfile에서 `pnpm build`가 실행되는지 확인
- 빌드 로그에서 dist 폴더 생성 확인

### 8.4 앱 이름 중복 오류

**오류 메시지:**
```
Error: App name already taken
```

**해결:**
```bash
# 다른 이름으로 변경
# fly.toml 파일에서 app 이름 변경
fly launch  # 새로운 이름으로 재시도
```

### 8.5 메모리 부족 오류

**증상:**
- 배포는 성공하지만 앱이 계속 재시작됨

**해결:**
```toml
# fly.toml에서 메모리 증가
[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 1024  # 512에서 1024로 증가
```

**주의:** 메모리 증가 시 무료 티어 제한에 영향

### 8.6 SSH 접속 (디버깅용)

```bash
# 앱에 SSH 접속
fly ssh console

# 또는 명령 실행
fly ssh console -C "ls -la"
fly ssh console -C "python3 --version"
```

### 8.7 앱 재시작

```bash
# 앱 재시작
fly apps restart your-app-name

# 또는 특정 머신 재시작
fly machine restart <machine-id>
```

### 8.8 앱 삭제

```bash
# 주의: 이 작업은 되돌릴 수 없습니다!
fly apps destroy your-app-name
```

---

## 9. 추가 명령어

### 9.1 유용한 명령어

```bash
# 앱 목록 확인
fly apps list

# 앱 정보 확인
fly info

# 앱 로그 실시간 보기
fly logs -a your-app-name

# 배포 히스토리
fly releases

# 스케일링 (무료 티어에서는 제한적)
fly scale count 1
fly scale vm shared-cpu-1x --memory 512

# 모니터링
fly dashboard
```

### 9.2 배포 업데이트

코드 변경 후 재배포:

```bash
# 변경사항 커밋 (선택사항)
git add .
git commit -m "Update code"

# 배포
fly deploy
```

### 9.3 롤백

이전 버전으로 되돌리기:

```bash
# 배포 히스토리 확인
fly releases

# 특정 버전으로 롤백
fly releases rollback <release-id>
```

---

## 10. 무료 티어 제한

Fly.io 무료 티어 제한:

| 항목 | 제한 |
|------|------|
| VM 개수 | 3개 |
| 아웃바운드 트래픽 | 월 3GB |
| 스토리지 (볼륨) | 1GB |
| CPU | Shared CPU |

**주의사항:**
- 제한을 초과하면 요금이 부과될 수 있습니다
- 사용량은 Fly.io 대시보드에서 확인 가능
- 소규모 프로젝트에는 충분합니다

**사용량 확인:**

```bash
fly dashboard
# 또는 웹 브라우저에서
# https://fly.io/dashboard
```

---

## 11. 성능 최적화

### 11.1 이미지 크기 최적화

Dockerfile에서 불필요한 파일 제외 (`.dockerignore` 확인)

### 11.2 빌드 시간 단소화

- 의존성 캐싱 활용
- 멀티스테이지 빌드 고려 (필요 시)

### 11.3 자동 스케일링

```toml
# fly.toml
[http_service]
  auto_stop_machines = true   # 비활성 시 자동 중지
  auto_start_machines = true  # 요청 시 자동 시작
  min_machines_running = 0    # 최소 실행 머신 수
```

---

## 12. 다음 단계

배포가 성공한 후:

1. **도메인 연결** (선택사항)
   - 커스텀 도메인 연결 가능
   - `fly certs add yourdomain.com`

2. **모니터링 설정**
   - Fly.io 대시보드에서 메트릭 확인
   - 알림 설정 (필요 시)

3. **백업 전략**
   - 데이터 백업 (필요 시)
   - 설정 파일 버전 관리

---

## 요약 체크리스트

배포 전 확인:

- [ ] Fly.io CLI 설치 완료 (`fly version` 확인)
- [ ] Fly.io 계정 생성 및 로그인 완료 (`fly auth whoami` 확인)
- [ ] `fly.toml` 파일에서 앱 이름 변경 완료
- [ ] `Dockerfile`에 프론트엔드 빌드 단계 포함 확인
- [ ] 프로젝트가 Git에 커밋되어 있음 (선택사항)

배포 후 확인:

- [ ] `fly status`로 앱 상태 확인
- [ ] 웹 브라우저에서 앱 접속 확인
- [ ] `/api/health` 엔드포인트 확인
- [ ] 파일 업로드 기능 테스트
- [ ] 분석 기능 테스트

---

## 참고 자료

- [Fly.io 공식 문서](https://fly.io/docs/)
- [Fly.io CLI 참조](https://fly.io/docs/flyctl/)
- [Dockerfile 베스트 프랙티스](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [프로젝트 README.md](../README.md)
- [배포 가이드 전체](./DEPLOYMENT.md)

---

**문제가 발생하면:**
1. 이 가이드의 "문제 해결" 섹션 확인
2. `fly logs`로 로그 확인
3. Fly.io 대시보드에서 확인
4. [Fly.io 커뮤니티](https://community.fly.io/)에서 도움 요청

