# Vercel 배포 가이드

## 🚀 Vercel 배포 방법

### 방법 1: 정적 사이트 + 외부 API (추천)

1. **Vercel CLI 설치**:
   ```bash
   npm i -g vercel
   ```

2. **프로젝트 배포**:
   ```bash
   vercel
   ```

3. **API는 별도 서비스 사용**:
   - Railway (무료)
   - Render (무료)
   - Heroku (무료)

### 방법 2: 서버리스 함수로 변환

Vercel은 Python 서버리스 함수를 지원하므로 Flask 앱을 변환할 수 있습니다.

#### API 함수 생성:
```python
# api/restaurants.py
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/restaurants', methods=['GET'])
def get_restaurants():
    # 기존 로직
    pass

if __name__ == '__main__':
    app.run()
```

### 방법 3: Railway + Vercel (하이브리드)

1. **Railway에 API 배포**:
   ```bash
   # Railway CLI 설치
   npm install -g @railway/cli
   
   # 로그인 및 배포
   railway login
   railway init
   railway up
   ```

2. **Vercel에 프론트엔드 배포**:
   ```bash
   vercel
   ```

## 🔧 Vercel 설정 파일

### vercel.json
```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/**/*.py",
      "use": "@vercel/python"
    },
    {
      "src": "index.html",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "api/$1"
    },
    {
      "src": "/(.*)",
      "dest": "index.html"
    }
  ]
}
```

## 📁 프로젝트 구조 (Vercel용)

```
hungry-people/
├── api/                    # 서버리스 함수
│   ├── restaurants.py
│   ├── events.py
│   └── recommendations.py
├── index.html              # 메인 페이지
├── vercel.json             # Vercel 설정
└── package.json            # 프로젝트 설정
```

## 🚀 배포 명령어

```bash
# Vercel CLI 설치
npm i -g vercel

# 프로젝트 디렉토리에서
vercel

# 또는 GitHub 연동
vercel --prod
```

## 💡 추천 배포 방법

1. **Railway** (가장 간단)
   - Python Flask 직접 지원
   - 무료 티어
   - 자동 배포

2. **Render** (안정적)
   - 무료 티어
   - 자동 SSL
   - 쉬운 설정

3. **Heroku** (전통적)
   - 무료 티어 (제한적)
   - Git 기반 배포

## 🔗 배포 후 확인

- **도메인**: `https://your-app-name.vercel.app`
- **API**: `https://your-app-name.vercel.app/api/restaurants`
- **상태**: Vercel 대시보드에서 확인
