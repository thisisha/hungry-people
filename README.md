# Hungry People - 식사 장소 추천 서비스

## 🍽️ 서비스 소개

**Hungry People**은 소상공인시장진흥공단의 전국 백년가게 현황 데이터와 연구개발특구진흥재단 행사일정 데이터를 연계하여 사용자가 지역 내에서 신뢰할 수 있는 점심/저녁 식사 장소를 쉽고 빠르게 탐색할 수 있도록 돕는 웹 기반 서비스입니다.

### 🎯 주요 기능
- **전국 백년가게 검색**: 신뢰할 수 있는 음식점 정보 제공
- **행사 장소 근처 추천**: 회의나 행사 장소 근처 백년가게 추천
- **지역별 필터링**: 지역별로 음식점 필터링 및 검색
- **스마트 추천**: 사용자 쿼리 분석을 통한 맞춤형 추천
- **통합 검색**: 백년가게와 행사일정을 한 번에 검색

### 📊 활용 데이터
1. **소상공인시장진흥공단 전국 백년가게 현황** (1,407개 업체)
   - 업체명, 주소, 연락처, 지역 정보
2. **연구개발특구진흥재단 행사일정** (1,243개 행사)
   - 행사명, 장소, 날짜, 지역, 기술 분류
3. **연구개발특구진흥재단 유관기관 일정** (1,739개 일정)
   - 일정 제목, 날짜, 작성일

## 🛠️ 기술 스택

### Backend
- **Python Flask**: RESTful API 서버
- **SQLite**: 데이터베이스
- **Pandas**: 데이터 처리
- **Flask-CORS**: CORS 처리

### Frontend
- **React.js**: 사용자 인터페이스
- **Material-UI**: UI 컴포넌트
- **Axios**: HTTP 클라이언트

## 🚀 설치 및 실행

### 1. 프로젝트 클론 및 의존성 설치

```bash
# Python 의존성 설치
pip install Flask Flask-CORS pandas

# Node.js 의존성 설치 (프론트엔드 디렉토리에서)
cd frontend
npm install
```

### 2. 백엔드 서버 실행

```bash
cd backend
python app.py
```

백엔드 서버가 `http://localhost:5000`에서 실행됩니다.

### 3. 프론트엔드 서버 실행

```bash
cd frontend
npm start
```

프론트엔드 서버가 `http://localhost:3000`에서 실행됩니다.

## 📡 API 엔드포인트

### 기본 API
- `GET /api/health` - 서버 상태 확인
- `GET /api/stats` - 통계 정보

### 백년가게 API
- `GET /api/restaurants` - 백년가게 목록
- `GET /api/restaurants/<id>` - 백년가게 상세 정보

### 행사일정 API
- `GET /api/events` - 행사일정 목록

### 추천 API
- `GET /api/recommendations` - 추천 서비스
- `GET /api/smart-recommendations` - 스마트 추천

### 검색 API
- `GET /api/search` - 통합 검색
- `GET /api/regions` - 지역 목록

## 🔍 사용 예시

### 1. 지역별 백년가게 검색
```
GET /api/restaurants?region=서울&limit=10
```

### 2. 행사 장소 근처 백년가게 추천
```
GET /api/recommendations?location=대전 DCC&limit=5
```

### 3. 스마트 추천
```
GET /api/smart-recommendations?q=대덕특구&limit=10
```

### 4. 통합 검색
```
GET /api/search?q=컨퍼런스&type=all&limit=20
```

## 📁 프로젝트 구조

```
hungry-people/
├── backend/                 # Flask 백엔드
│   ├── app.py              # 메인 애플리케이션
│   ├── models/             # 데이터 모델
│   │   └── database.py     # 데이터베이스 관리
│   ├── services/           # 비즈니스 로직
│   │   ├── data_processor.py      # CSV 데이터 처리
│   │   └── recommendation_engine.py # 추천 엔진
│   └── data/               # CSV 데이터 파일
├── frontend/               # React 프론트엔드
│   ├── src/
│   │   └── App.js          # 메인 컴포넌트
│   └── public/
├── requirements.txt        # Python 의존성
└── README.md              # 프로젝트 문서
```

## 🎨 주요 기능 설명

### 1. 백년가게 검색
- 전국 1,407개 백년가게 정보 제공
- 지역별, 키워드별 검색 가능
- 신뢰할 수 있는 음식점 정보

### 2. 행사 장소 근처 추천
- 행사/회의 장소 근처 백년가게 자동 추천
- 지역 키워드 매칭을 통한 정확한 추천
- 가중치 기반 정렬로 최적의 결과 제공

### 3. 스마트 추천 시스템
- 사용자 쿼리 자동 분석
- 지역, 행사, 장소 타입별 맞춤 추천
- 추천 제안 및 관련 정보 제공

### 4. 반응형 웹 인터페이스
- Material-UI 기반 모던한 디자인
- 모바일/데스크톱 반응형 지원
- 직관적인 사용자 경험

## 🔧 개발 환경

- **Python**: 3.8+
- **Node.js**: 14+
- **npm**: 6+

## 📝 라이선스

이 프로젝트는 교육 및 연구 목적으로 개발되었습니다.

## 🤝 기여하기

1. 프로젝트 포크
2. 기능 브랜치 생성 (`git checkout -b feature/AmazingFeature`)
3. 변경사항 커밋 (`git commit -m 'Add some AmazingFeature'`)
4. 브랜치에 푸시 (`git push origin feature/AmazingFeature`)
5. Pull Request 생성

## 📞 문의

프로젝트에 대한 문의사항이 있으시면 이슈를 생성해 주세요.