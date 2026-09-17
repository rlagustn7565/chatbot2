# 🚀 Render 배포 완벽 가이드

이 문서는 카카오톡 AI 챗봇을 **Render 무료 서버**에 배포하는 방법을 단계별로 설명합니다.

---

## 📋 사전 준비

1. **Git 설치**
   - [Git 공식 사이트](https://git-scm.com/download/win)에서 설치
   - 설치 후 PC 재부팅

2. **GitHub 계정**
   - [GitHub](https://github.com) 가입 (없으면 회원가입)

3. **Render 계정**
   - [Render](https://render.com) 가입 (GitHub로 로그인 권장)

4. **API 키 준비**
   - Gemini API 키
   - Naver API 키 (ID, Secret)

---

## 📝 단계별 가이드

### 1️⃣ GitHub 저장소 생성

#### 방법 A: 웹 UI로 생성 (추천)

1. GitHub 홈페이지 접속
2. 우상단 **"+"** → **"New repository"** 클릭
3. 저장소 설정:
   - **Repository name**: `kakao-chatbot-v2`
   - **Description**: Kakao Chatbot with AI Analysis
   - **Public** 선택 (Render에서 접근하려면 필수)
   - **"Create repository"** 클릭

4. 생성 후 표시되는 명령어 복사

#### 방법 B: 로컬 터미널에서 생성

```bash
cd "C:\챗봇 버전 2"

# Git 초기화
git init

# 기본 설정
git config user.name "Your Name"
git config user.email "your-email@example.com"

# 모든 파일 추가
git add .

# 초기 커밋
git commit -m "🚀 Initial commit: Kakao Chatbot v2"

# 원격 저장소 추가 (GitHub에서 복사한 URL 사용)
git remote add origin https://github.com/your-username/kakao-chatbot-v2.git

# 브랜치 이름 변경 (GitHub 기본값이 main일 경우)
git branch -M main

# GitHub에 푸시
git push -u origin main
```

---

### 2️⃣ Render에 배포

#### 단계 1: Render 로그인

1. [Render.com](https://render.com) 접속
2. **"Sign up with GitHub"** 클릭 (GitHub 계정으로 로그인)
3. GitHub 연동 권한 승인

#### 단계 2: 새 웹 서비스 생성

1. 대시보드에서 **"New +"** 클릭
2. **"Web Service"** 선택
3. GitHub 저장소 연결:
   - **"Connect"** 버튼으로 저장소 검색
   - `kakao-chatbot-v2` 선택
   - **"Connect"** 클릭

#### 단계 3: 배포 설정

다음 항목들을 설정합니다:

| 항목 | 값 | 설명 |
|------|-----|------|
| **Name** | `kakao-chatbot-v2` | 서비스 이름 (URL에 사용됨) |
| **Runtime** | `Python 3` | 런타임 환경 |
| **Build Command** | `pip install -r requirements.txt` | 빌드 명령어 |
| **Start Command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` | 시작 명령어 |
| **Plan** | `Free` | 무료 플랜 (또는 $7/월 유료) |

#### 단계 4: 환경 변수 설정

1. **"Environment"** 탭 클릭
2. **"Add Environment Variable"** 클릭
3. 다음 환경 변수 추가:

```
GEMINI_API_KEY = your_gemini_api_key_here
NAVER_CLIENT_ID = your_naver_client_id_here
NAVER_CLIENT_SECRET = your_naver_client_secret_here
```

> ⚠️ 주의: GitHub에 .env 파일이 업로드되지 않도록 주의!  
> .gitignore에 `.env`가 포함되어 있으므로 자동 제외됩니다.

#### 단계 5: 배포 시작

1. 모든 설정 확인
2. **"Deploy"** 버튼 클릭
3. 배포 진행 상황 확인 (3-5분 소요)

```
✅ Service Live ✓ - 배포 완료!
```

#### 단계 6: 배포 URL 확인

배포 완료 후:
- 서비스 URL: `https://kakao-chatbot-v2.onrender.com`
- 헬스 체크: `https://kakao-chatbot-v2.onrender.com/health`
- **API 엔드포인트**: `https://kakao-chatbot-v2.onrender.com/api/chat`

---

### 3️⃣ 카카오톡 오픈빌더 연동

1. **카카오톡 오픈빌더** 접속: https://open.kakao.com/
2. **"내 봇"** → **"스킬 관리"** 클릭
3. 새 스킬 생성:
   - **스킬 이름**: 예) "금융 분석 봇"
   - **스킬 서버 URL**: `https://kakao-chatbot-v2.onrender.com/api/chat`
   - 저장

4. **테스트**:
   ```
   "SK하이닉스 분석해줘"
   → 봇이 응답 (5초 내)
   → 분석 결과 수신 (1-2분)
   ```

5. **배포**: 테스트 완료 후 배포 신청

---

## 🔧 설정 변경 방법

### Render에서 환경 변수 변경

1. Render 대시보드 → 서비스 선택
2. **"Environment"** 탭
3. 변수 수정 후 **"Save Changes"**
4. 자동 재배포 진행

### GitHub에서 코드 업데이트

```bash
cd "C:\챗봇 버전 2"

# 코드 수정 후
git add .
git commit -m "Fix: 버그 수정 또는 기능 추가"
git push origin main

# Render가 자동으로 감지하여 재배포 (1-2분)
```

---

## 📊 무료 플랜 vs 유료 플랜

### 무료 플랜 ($0/월)
- ✅ 월 750시간 무료
- ❌ 15분 미사용 시 자동 sleep
- ❌ 24시간 운영 불가
- 개발/테스트용 추천

### 유료 플랜 ($7/월)
- ✅ 항상 켜짐 (24/7)
- ✅ 더 빠른 성능
- ✅ 우선 지원
- 프로덕션용 추천

---

## 🐛 배포 후 문제 해결

### 1. "Build failed" 오류

**로그 확인**:
1. Render 대시보드 → 서비스 선택
2. **"Logs"** 탭 → 오류 메시지 확인

**일반적인 원인**:
- `requirements.txt` 문법 오류
- 패키지 설치 실패
- Python 버전 호환성 문제

**해결**:
```bash
# 로컬에서 테스트
pip install -r requirements.txt

# 오류 해결 후 커밋
git commit -am "Fix requirements.txt"
git push origin main
```

### 2. "API 오류" 또는 "500 Internal Server Error"

**확인 사항**:
- ✓ 환경 변수가 올바르게 설정되었는가?
- ✓ API 키가 유효한가?
- ✓ Render 로그에 오류가 있는가?

**로그 확인**:
```bash
Render 대시보드 → "Logs" 탭 → 오류 메시지 검색
```

### 3. 5초 타임아웃

**원인**: 백그라운드 작업이 완료되지 않음

**확인**:
- ✓ 콜백 URL이 유효한가?
- ✓ 네트워크 지연이 있는가?
- ✓ Gemini API 응답 시간이 긴가?

**해결**:
- Render 유료 플랜 업그레이드 (더 빠른 서버)
- API 요청 최적화

### 4. "모듈을 찾을 수 없음"

**해결**:
```bash
# requirements.txt에 패키지 추가
pip freeze > requirements.txt

# 커밋 및 푸시
git add requirements.txt
git commit -m "Add missing dependencies"
git push origin main
```

---

## 📈 배포 후 모니터링

### Render 대시보드 확인

- **Status**: 서비스 상태 (Live/Build/Crashed)
- **Logs**: 실시간 로그
- **Metrics**: CPU, 메모리 사용량
- **Deployments**: 배포 이력

### 로그 모니터링

```bash
# Render 대시보드의 "Logs" 탭에서 실시간 확인
# 또는 CLI:
# render logs --service-id <service-id>
```

### 서비스 재시작

Render 대시브드 → **"Manual Deploy"** → **"Latest"** 클릭

---

## 💡 팁 및 모범 사례

### 1. 일일 업데이트

```bash
# 새로운 기능 추가
git add .
git commit -m "Feature: 새로운 기능 설명"
git push origin main

# Render가 자동 배포
```

### 2. 로그 분석

```
common patterns:
- "ERROR: Module not found" → requirements.txt 확인
- "Connection refused" → 콜백 URL 확인
- "Timeout" → 성능 개선 필요
```

### 3. 성능 최적화

- API 요청 병렬화
- 캐싱 활용
- 불필요한 로깅 제거

---

## ✅ 배포 체크리스트

- [ ] Git 설치 완료
- [ ] GitHub 계정 생성
- [ ] 저장소 생성 및 코드 푸시
- [ ] Render 계정 생성
- [ ] 환경 변수 설정
- [ ] 배포 시작
- [ ] 헬스 체크 확인 (200 OK)
- [ ] 카카오톡 오픈빌더 연동
- [ ] 테스트 메시지 전송
- [ ] 배포 완료! 🎉

---

## 📞 문제 발생 시

1. **Render 로그 확인**: 대시보드 → "Logs" 탭
2. **GitHub 커밋 확인**: 코드가 올바르게 푸시되었는가?
3. **API 키 확인**: 환경 변수가 올바른가?
4. **로컬 테스트**: `python main.py`로 로컬 실행 테스트

---

## 📚 참고 자료

- [Render 공식 가이드](https://render.com/docs)
- [FastAPI 배포](https://fastapi.tiangolo.com/deployment/)
- [GitHub 기초](https://guides.github.com/)
- [카카오톡 오픈빌더](https://open.kakao.com/guide/oapiinfo)

---

## 🎯 다음 단계

배포 완료 후:
1. 로그 모니터링 시작
2. 사용자 피드백 수집
3. 기능 개선 (새 커밋)
4. 성능 최적화
5. 사용 분석 및 업데이트

---

**작성**: AI 챗봇 개발팀  
**마지막 업데이트**: 2026-09-17  
**버전**: 1.0
