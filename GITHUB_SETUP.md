# GitHub 프로젝트 설정 가이드

## 1. GitHub 저장소 생성

1. GitHub에 로그인하고 https://github.com/new 에서 새 저장소 생성
2. 저장소 이름: `elliot-fitting` (또는 원하는 이름)
3. Public 또는 Private 선택
4. **README, .gitignore, LICENSE는 추가하지 않음** (이미 프로젝트에 포함되어 있음)

## 2. 로컬 Git 저장소 초기화 및 업로드

현재 프로젝트 디렉토리에서 다음 명령어 실행:

```bash
# Git 저장소 초기화
git init

# 모든 파일 추가
git add .

# 첫 커밋
git commit -m "Initial commit: Python port of MATLAB Elliot fitting code"

# GitHub 저장소 연결
git remote add origin https://github.com/jinwoo7park/Eliot-model.git

# 기본 브랜치를 main으로 설정
git branch -M main

# GitHub에 푸시
git push -u origin main
```

## 3. README.md 업데이트

`README.md` 파일에서 다음 부분을 실제 정보로 수정:
- 저장소 URL
- 작성자 정보
- 라이선스 정보 (필요시)

## 4. 추가 설정 (선택사항)

### GitHub Pages 설정
- Settings > Pages에서 문서 사이트 호스팅 가능

### Issues 및 Projects 활성화
- Settings에서 Issues와 Projects 활성화

### 브랜치 보호 규칙
- Settings > Branches에서 main 브랜치 보호 규칙 설정 가능

## 5. 릴리스 생성

버전을 배포할 때:
```bash
# 태그 생성
git tag -a v0.1.0 -m "Initial release"

# 태그 푸시
git push origin v0.1.0
```

GitHub에서 Releases 섹션에서 릴리스 노트 작성 가능

## 6. 협업 설정

### Collaborators 추가
- Settings > Collaborators에서 협업자 추가

### Pull Request 템플릿 (선택사항)
`.github/pull_request_template.md` 파일 생성 가능

## 7. CI/CD 확인

`.github/workflows/python-package.yml` 파일이 포함되어 있어서:
- 코드 푸시 시 자동으로 테스트 실행
- Actions 탭에서 실행 상태 확인 가능

## 유용한 명령어

```bash
# 변경사항 확인
git status

# 변경사항 커밋
git add .
git commit -m "커밋 메시지"

# GitHub에 푸시
git push

# 최신 변경사항 가져오기
git pull

# 브랜치 생성 및 전환
git checkout -b feature/new-feature
```

