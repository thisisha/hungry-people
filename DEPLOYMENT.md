# 배포 가이드

## 🚀 배포 옵션

### 1. 로컬 네트워크 배포 (즉시 가능)

#### 현재 상황에서 바로 사용 가능한 방법:

1. **백엔드 서버 실행**:
   ```bash
   cd backend
   python app.py
   ```

2. **웹 서버 실행**:
   ```bash
   python -m http.server 8080
   ```

3. **네트워크 접속**:
   - 같은 네트워크의 다른 기기에서 접속 가능
   - IP 주소 확인: `ipconfig` (Windows) 또는 `ifconfig` (Mac/Linux)

### 2. 클라우드 배포 (무료)

#### A. Heroku 배포

1. **Heroku CLI 설치**:
   ```bash
   # Windows
   winget install Heroku.HerokuCLI
   
   # 또는 공식 사이트에서 다운로드
   # https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Heroku 앱 생성**:
   ```bash
   heroku login
   heroku create hungry-people-app
   ```

3. **Procfile 생성**:
   ```
   web: python backend/app.py
   ```

4. **배포**:
   ```bash
   git add .
   git commit -m "Initial deployment"
   git push heroku main
   ```

#### B. Railway 배포

1. **Railway 계정 생성**: https://railway.app
2. **GitHub 연동**
3. **프로젝트 연결**
4. **자동 배포**

#### C. Render 배포

1. **Render 계정 생성**: https://render.com
2. **Web Service 생성**
3. **GitHub 저장소 연결**
4. **자동 배포**

### 3. Docker 배포

#### Dockerfile 생성:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5001

CMD ["python", "backend/app.py"]
```

#### Docker 실행:
```bash
docker build -t hungry-people .
docker run -p 5001:5001 hungry-people
```

### 4. VPS 배포

#### DigitalOcean, AWS EC2, Google Cloud 등

1. **서버 생성**
2. **도메인 연결**
3. **SSL 인증서 설정**
4. **자동 배포 설정**

## 🔧 배포 전 준비사항

### 1. 환경 변수 설정
```python
# .env 파일
FLASK_ENV=production
DATABASE_URL=sqlite:///hungry_people.db
```

### 2. 프로덕션 설정
```python
# app.py 수정
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)
```

### 3. 정적 파일 최적화
- CSS/JS 압축
- 이미지 최적화
- CDN 사용

## 📊 추천 배포 순서

1. **로컬 네트워크** (즉시 테스트)
2. **Heroku** (무료, 간단)
3. **Railway** (현대적)
4. **VPS** (완전한 제어)

## 💡 배포 팁

- **무료 티어 제한**: 월 사용량 제한 있음
- **데이터베이스**: SQLite → PostgreSQL (클라우드)
- **정적 파일**: CDN 사용 권장
- **모니터링**: 로그 확인 필수
