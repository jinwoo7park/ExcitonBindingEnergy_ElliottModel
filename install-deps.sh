#!/bin/bash

# Python 의존성 설치 스크립트
# 여러 방법을 시도하여 pip를 찾습니다

echo "🔍 Python 의존성 설치 중..."

# 방법 1: python3 -m pip
if command -v python3 &> /dev/null; then
    echo "python3 -m pip 사용 시도..."
    if python3 -m pip install -r requirements.txt; then
        echo "✅ Python 의존성 설치 완료!"
        exit 0
    fi
fi

# 방법 2: pip3
if command -v pip3 &> /dev/null; then
    echo "pip3 사용 시도..."
    if pip3 install -r requirements.txt; then
        echo "✅ Python 의존성 설치 완료!"
        exit 0
    fi
fi

# 방법 3: pip
if command -v pip &> /dev/null; then
    echo "pip 사용 시도..."
    if pip install -r requirements.txt; then
        echo "✅ Python 의존성 설치 완료!"
        exit 0
    fi
fi

echo "❌ Python 의존성 설치 실패!"
echo "다음 중 하나를 시도하세요:"
echo "  python3 -m pip install -r requirements.txt"
echo "  pip3 install -r requirements.txt"
echo "  pip install -r requirements.txt"
exit 1



