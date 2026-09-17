# 🤖 카카오톡 AI 챗봇 - 금융 분석 플랫폼

FastAPI, Gemini AI, pykrx를 활용한 **카카오톡 오픈빌더 챗봇**입니다.  
유튜브 영상 요약, 주식 종목 분석, 지수/환율 조회 등의 기능을 제공합니다.

## ✨ 주요 기능

### 📺 **유튜브 영상 요약**
- 유튜브 URL 입력 → 자막 추출 → Gemini AI 요약
- 한국어/영어/자동생성 자막 자동 감지

### 📈 **주식 종목 분석**
- 실시간 주가 조회 (pykrx)
- 관련 뉴스 3개 자동 수집
- Gemini AI 투심 분석
  - 📈 현재가 브리핑
  - 📰 기사 요약
  - ⚖️ 투심 분석 (긍정/부정/중립)
  - 🔗 관련주/테마주 추천

### 📊 **지수/환율 조회**
- 코스피, 코스닥, 나스닥, S&P500 등 지수 조회
- USD/KRW, EUR/USD 등 환율 실시간 조회
- finance-datareader 기반

### 📰 **뉴스 검색 및 분석**
- 네이버 뉴스 검색 API
- 본문 텍스트 자동 추출

## 🏗️ 시스템 아키텍처

```
카카오톡 (사용자)
    ↓
FastAPI 서버 (/api/chat)
    ├─ 즉시 응답: "분석 중입니다..." (5초 내)
    └─ BackgroundTasks (백그라운드 작업)
        ├─ youtube.py (영상 요약)
        ├─ stock.py (주가/지수/환율)
        ├─ news.py (뉴스 검색)
        └─ llm_helper.py (Gemini AI 분석)
            ↓
콜백 URL로 결과 POST
    ↓
카카오톡 메시지로 결과 표시
```

## 📦 프로젝트 구조

```
챗봇 버전 2/
├── main.py              # FastAPI 서버 (메인 진입점)
├── youtube.py           # 유튜브 자막 추출 + 요약
├── stock.py             # 주가/지수/환율 조회 (pykrx + finance-datareader)
├── news.py              # 뉴스 검색 + 본문 추출
├── llm_helper.py        # Gemini AI 분석 및 요약
├── requirements.txt     # 의존성 패키지
├── .env                 # 환경 변수 (API 키)
├── .gitignore           # Git 제외 파일
├── Procfile             # Render 배포 설정
├── runtime.txt          # Python 버전
└── README.md            # 이 파일
```

## 🚀 빠른 시작

### 1. 로컬 설치 및 실행

```bash
# 저장소 클론
git clone https://github.com/your-username/chatbot-v2.git
cd chatbot-v2

# 가상 환경 생성
python -m venv venv

# 가상 환경 활성화
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# .env 파일 생성 및 API 키 입력
# .env 파일 내용:
# GEMINI_API_KEY=your_gemini_api_key
# NAVER_CLIENT_ID=your_naver_client_id
# NAVER_CLIENT_SECRET=your_naver_client_secret

# 서버 실행
python main.py
# 또는
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 2. Render에 배포

#### 단계 1: GitHub에 푸시
```bash
git init
git add .
git commit -m "Initial commit: Kakao chatbot v2"
git branch -M main
git remote add origin https://github.com/your-username/chatbot-v2.git
git push -u origin main
```

#### 단계 2: Render 설정
1. [Render.com](https://render.com) 접속 및 GitHub 계정 연동
2. **"New +"** → **"Web Service"** 선택
3. GitHub 저장소 연결 (`chatbot-v2`)
4. 배포 설정:
   - **Name**: 예) `kakao-chatbot-v2`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. **Environment Variables** 설정:
   ```
   GEMINI_API_KEY = your_gemini_api_key
   NAVER_CLIENT_ID = your_naver_client_id
   NAVER_CLIENT_SECRET = your_naver_client_secret
   ```
6. **Deploy** 클릭

#### 단계 3: 카카오톡 오픈빌더 연동
1. 카카오톡 오픈빌더에서 새 스킬 생성
2. 스킬 서버 URL: `https://your-service-name.onrender.com/api/chat`
3. 테스트 및 배포

## 🔑 필수 API 키

### 1. Gemini API
- [Google AI Studio](https://aistudio.google.com/app/apikey)에서 API 키 발급

### 2. 네이버 API
- [Naver Cloud Platform](https://www.ncloud.com/)에서 API 키 발급
- Search API 활성화 필요

## 📝 사용 예시

### 예시 1: 주식 종목 분석
```
사용자: "SK하이닉스 분석해줘"
봇: [분석 중입니다...]
(잠시 후)
봇: 📊 SK하이닉스 투심 분석
   📈 현재가: 1,758,000원 (+0.06%)
   📰 기사 요약: 3개 뉴스...
   ⚖️ 투심: 긍정적
   🔗 관련주: 삼성전자, 원익IPS...
```

### 예시 2: 유튜브 영상 요약
```
사용자: "https://youtube.com/watch?v=xxx"
봇: [분석 중입니다...]
(잠시 후)
봇: 📺 유튜브 영상 요약
   1. 핵심 내용 1
   2. 핵심 내용 2
   3. 핵심 내용 3
```

### 예시 3: 지수/환율 조회
```
사용자: "코스피 환율"
봇: 📈 KOSPI: 6,742 (+0.35%)
    💱 USD/KRW: 1,379.78원
```

## 🛠️ 기술 스택

- **Backend**: FastAPI, Uvicorn
- **AI**: Google Gemini 2.0 Flash
- **금융 데이터**: pykrx, finance-datareader
- **웹 스크래핑**: BeautifulSoup4
- **영상 처리**: youtube-transcript-api
- **뉴스 API**: Naver Search API
- **배포**: Render (무료)

## 📋 주요 함수

### main.py
- `chat()`: 카카오톡 메시지 수신 및 즉시 응답
- `process_analysis_background()`: 백그라운드 분석 작업
- `analyze_youtube()`: 유튜브 분석
- `analyze_stock_full()`: 주식 분석
- `analyze_index_or_exchange()`: 지수/환율 조회

### stock.py
- `get_stock_price()`: 주가 조회 (pykrx)
- `get_stock_news()`: 관련 뉴스 조회
- `get_index_price()`: 지수 조회
- `get_exchange_rate()`: 환율 조회

### llm_helper.py
- `analyze_stock()`: 투심 분석
- `summarize_news()`: 뉴스 3줄 요약

### youtube.py
- `get_youtube_summary()`: 영상 자막 추출 + 요약

### news.py
- `search_news()`: 뉴스 검색
- `get_article_text()`: 본문 추출

## ⚙️ Render 배포 비용

- **무료 티어**: 월 750시간 무료 (항상 켜둬도 안됨)
- **$7/월**: 항상 켜짐 (권장)

> Render의 무료 서버는 15분 이상 사용이 없으면 자동 sleep됩니다.  
> 24시간 운영을 원하면 유료 플랜으로 업그레이드하세요.

## 🐛 문제 해결

### "API 키가 없다" 오류
- `.env` 파일이 프로젝트 루트에 있는지 확인
- Render Environment Variables에 올바르게 설정되었는지 확인

### "모듈을 찾을 수 없다" 오류
- `requirements.txt`에 모든 의존성이 있는지 확인
- Render 배포 로그에서 설치 오류 확인

### 5초 타임아웃 오류
- BackgroundTasks가 올바르게 작동하는지 확인
- 콜백 URL이 유효한지 확인

## 📚 참고 자료

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [Render 배포 가이드](https://render.com/docs)
- [카카오톡 오픈빌더](https://open.kakao.com/)
- [Google Gemini API](https://ai.google.dev/)

## 📄 라이선스

MIT License

## 👨‍💻 기여

버그 리포트 및 기능 제안은 GitHub Issues를 통해 주시기 바랍니다.

---

**만든이**: AI 챗봇 개발자  
**마지막 업데이트**: 2026-09-17
