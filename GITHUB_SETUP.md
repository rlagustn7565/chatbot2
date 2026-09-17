# GitHub Repository 생성 완벽 가이드

## 📝 저장소명: chatbot2

---

## 🚀 단계별 설정

### 1단계: GitHub 로그인
```
1. https://github.com/ 접속
2. 우상단 프로필 아이콘 클릭
3. "Sign in" (아직 로그인 안 했으면)
```

### 2단계: 새 Repository 생성

#### 방법 1: "New" 버튼으로 (추천)
```
1. GitHub 홈페이지 우상단 "+" 아이콘 클릭
2. "New repository" 선택
```

#### 방법 2: 프로필에서
```
1. 프로필 → "Repositories" 탭
2. "New" 버튼 클릭
```

---

## ⚙️ Repository 설정

### 기본 정보

| 항목 | 값 | 설명 |
|------|-----|------|
| **Repository name** | `chatbot2` | ✓ 저장소 이름 |
| **Description** | `Kakao Chatbot with AI Analysis` | 저장소 설명 (선택) |

### 공개 범위

```
◉ Public  (추천 - Render에서 접근 가능)
○ Private (유료 플랜 필요)
```

**선택: Public**

### 초기화 옵션

#### ✓ 체크할 항목
```
☑ Add a README file
  (저장소에 대한 설명)

☑ Add .gitignore
  - Python 선택
  (Git에서 제외할 파일)

☑ Choose a license
  - MIT License 선택
  (오픈소스 라이선스)
```

#### 최종 설정 화면

```
Repository name*
├─ chatbot2

Description
└─ Kakao Chatbot with AI Analysis

Public / Private
└─ ◉ Public

Initialize this repository with:
├─ ☑ Add a README file
├─ ☑ Add .gitignore
│  └─ Python
└─ ☑ Choose a license
   └─ MIT License
```

---

## 📸 설정 상세

### 1. Repository Name
- **이름**: `chatbot2`
- ✓ 소문자만 사용
- ✓ 하이픈(-) 또는 언더스코어(_) 사용 가능
- ✓ 공백 없음

### 2. Description (선택사항)
```
Kakao Chatbot with AI Analysis using FastAPI and Gemini
```

### 3. Public vs Private

| 항목 | Public | Private |
|------|--------|---------|
| 공개 | ✓ 누구나 볼 수 있음 | ✗ 초대한 사람만 |
| Render 연동 | ✓ 가능 | ✗ 불가 (무료) |
| 비용 | 무료 | 무료 (1개) |
| 추천 | ✓ | ✗ |

**선택: Public**

### 4. .gitignore (자동 생성)
- **"Python" 선택** - Python 프로젝트용 자동 설정
- .env, __pycache__, venv 등 자동 제외

### 5. License (자동 생성)
- **"MIT License" 선택** - 가장 개방적인 라이선스
- 자신의 프로젝트를 타인이 자유롭게 사용 가능

---

## 🎯 최종 설정 예시

```
Repository name:     chatbot2
Description:         Kakao Chatbot with AI Analysis
Public/Private:      ◉ Public
README file:         ☑ Yes
.gitignore:          ☑ Yes (Python)
License:             ☑ MIT License
```

---

## ✅ Repository 생성 후

### 생성되는 파일
```
chatbot2/
├── .gitignore       (자동 생성)
├── LICENSE          (MIT 라이선스)
└── README.md        (기본 README)
```

### 저장소 URL
```
https://github.com/your-username/chatbot2
```

### Clone 명령어 (나중에 필요)
```bash
git clone https://github.com/your-username/chatbot2.git
cd chatbot2
```

---

## 🔗 다음 단계: 로컬 저장소와 연동

### 옵션 1: 빈 저장소를 로컬에서 초기화

```bash
# 프로젝트 폴더로 이동
cd "C:\챗봇 버전 2"

# 기존 git 초기화 (있으면 제거)
# rm -r .git  (또는 del .git in Windows)

# git 초기화
git init

# GitHub 저장소와 연결
git remote add origin https://github.com/your-username/chatbot2.git

# 모든 파일 추가
git add .

# 초기 커밋
git commit -m "🚀 Initial commit: Kakao Chatbot with AI Analysis"

# GitHub에 푸시
git branch -M main
git push -u origin main
```

### 옵션 2: GitHub 웹 UI에서 직접 파일 추가

1. GitHub 저장소 페이지 접속
2. **"Add file"** → **"Upload files"** 클릭
3. 파일들을 드래그 & 드롭
4. **"Commit changes"** 클릭

---

## ⚠️ 주의사항

### .env 파일 보안
```
❌ 절대 업로드하면 안 됨!
   - GEMINI_API_KEY
   - NAVER_CLIENT_ID
   - NAVER_CLIENT_SECRET

✓ .gitignore에서 자동 제외됨
```

### 파일 확인
```bash
# 로컬에서 확인
git status
# 결과: .env는 나타나지 않음 (무시됨)
```

---

## 📋 빠른 체크리스트

- [ ] GitHub.com 로그인
- [ ] "New repository" 클릭
- [ ] 저장소 이름: `chatbot2`
- [ ] 설명: `Kakao Chatbot with AI Analysis`
- [ ] **Public** 선택
- [ ] ☑ Add a README file
- [ ] ☑ Add .gitignore (Python)
- [ ] ☑ Choose a license (MIT)
- [ ] **"Create repository"** 클릭
- [ ] 저장소 생성 완료!

---

## 🎉 생성 완료 후

### 저장소 주소
```
https://github.com/your-username/chatbot2
```

### 다음 작업
```
1. 로컬에서 파일 추가 & 커밋
2. GitHub에 푸시
3. Render에 배포
4. 카카오톡에서 테스트
```

---

## 💡 팁

### 1. Repository 이름 변경 (나중에 가능)
```
Settings → General → Repository name 변경 가능
```

### 2. 설명 수정
```
저장소 상단의 "About" 섹션에서 수정 가능
```

### 3. 공개 범위 변경 (나중에 가능)
```
Settings → Danger zone → Make private/public
```

---

**이제 준비 완료! GitHub에서 chatbot2 저장소를 만들고 파일을 추가하세요!** 🚀
