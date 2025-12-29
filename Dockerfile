FROM python:3.11-slim

# Node.js 및 pnpm 설치
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Node.js 설치 (LTS 버전)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs

# pnpm 설치
RUN npm install -g pnpm

# 작업 디렉토리 설정
WORKDIR /workspace

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Node.js 의존성 설치를 위한 package.json 복사
COPY package.json pnpm-lock.yaml* ./
RUN pnpm install || pnpm install --no-frozen-lockfile

# 나머지 파일 복사 (프론트엔드 소스 포함)
COPY . .

# 프론트엔드 빌드
RUN pnpm build

# 포트 노출 (Fly.io는 8080 사용, 환경 변수로 제어)
EXPOSE 8080

# 기본 명령어
# PORT 환경 변수를 사용하여 uvicorn 실행
CMD ["sh", "-c", "uvicorn api.index:app --host 0.0.0.0 --port ${PORT:-8080}"]
