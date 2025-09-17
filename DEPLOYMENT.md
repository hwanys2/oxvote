# Railway 배포 가이드

## 1. Railway 프로젝트 설정

### GitHub 연동
1. Railway 대시보드에서 프로젝트 생성
2. GitHub 저장소 연결
3. 자동 배포 활성화 (main 브랜치)

### 환경변수 설정
Railway 대시보드에서 다음 환경변수들을 설정하세요:

```
DEBUG=False
SECRET_KEY=your-secret-key-here
RAILWAY_DEPLOYMENT_ID=production
```

## 2. GitHub Actions 설정

### Repository Secrets 설정
GitHub 저장소의 Settings > Secrets and variables > Actions에서 다음 시크릿을 추가:

- `RAILWAY_TOKEN`: Railway API 토큰
- `RAILWAY_SERVICE_ID`: Railway 서비스 ID

### Railway API 토큰 생성
1. Railway 대시보드 > Account Settings > Tokens
2. "Generate Token" 클릭
3. 생성된 토큰을 GitHub Secrets에 추가

### Railway 서비스 ID 확인
1. Railway 프로젝트 > Settings > General
2. "Service ID" 복사하여 GitHub Secrets에 추가

## 3. 자동 배포 흐름

1. **코드 푸시**: main 브랜치에 코드 푸시
2. **GitHub Actions 실행**: 
   - 의존성 설치
   - 테스트 실행
   - 정적 파일 수집
   - Railway 배포
3. **Railway 배포**: 
   - 마이그레이션 실행
   - 정적 파일 수집
   - Gunicorn으로 서버 시작

## 4. 배포 확인

배포 완료 후 다음 URL에서 확인:
- `https://web-production-622a6.up.railway.app`

## 5. 문제 해결

### 일반적인 문제들:
1. **DisallowedHost 오류**: ALLOWED_HOSTS에 도메인 추가
2. **정적 파일 404**: collectstatic 실행 확인
3. **데이터베이스 오류**: 마이그레이션 실행 확인

### 로그 확인:
```bash
# Railway CLI로 로그 확인
railway logs
```
