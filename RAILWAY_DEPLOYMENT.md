# Railway 배포 가이드 (추천)

## 🚀 Railway로 배포하기

### 1. Railway 계정 생성
- https://railway.app 접속
- GitHub 계정으로 로그인

### 2. 프로젝트 연결
1. Railway 대시보드에서 "New Project" 클릭
2. "Deploy from GitHub repo" 선택
3. GitHub 저장소 연결

### 3. 자동 배포 설정
Railway가 자동으로 감지:
- `requirements.txt` → Python 의존성 설치
- `Procfile` → 실행 명령어
- `backend/app.py` → 메인 애플리케이션

### 4. 환경 변수 설정 (선택사항)
Railway 대시보드에서:
- `FLASK_ENV=production`
- `PORT=5000` (자동 설정됨)

### 5. 도메인 설정
- Railway가 자동으로 도메인 제공
- 커스텀 도메인 설정 가능

## 🔧 Railway용 설정 파일

### railway.json (선택사항)
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python backend/app.py",
    "healthcheckPath": "/api/health"
  }
}
```

## 📊 배포 후 확인

1. **Railway 대시보드**에서 배포 상태 확인
2. **로그** 확인: `railway logs`
3. **도메인** 접속 테스트
4. **API 엔드포인트** 테스트

## 🚀 배포 명령어 (CLI 사용 시)

```bash
# Railway CLI 설치
npm install -g @railway/cli

# 로그인
railway login

# 프로젝트 초기화
railway init

# 배포
railway up

# 로그 확인
railway logs

# 도메인 확인
railway domain
```

## 💡 Railway 장점

- ✅ Python Flask 직접 지원
- ✅ 무료 티어 제공
- ✅ 자동 HTTPS
- ✅ Git 기반 자동 배포
- ✅ 쉬운 설정
- ✅ 실시간 로그

## 🔗 배포 후 URL

- **웹사이트**: `https://your-app-name.railway.app`
- **API**: `https://your-app-name.railway.app/api/restaurants`
- **상태 확인**: `https://your-app-name.railway.app/api/health`
