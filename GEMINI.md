# GEMINI.md - BizTone Converter 프로젝트 컨텍스트

## 프로젝트 개요
**BizTone Converter**는 사회초년생이나 신입사원이 일상적인 말투를 전문적인 비즈니스 말투로 변환할 수 있도록 돕는 AI 기반 웹 애플리케이션입니다. **상사 (Upward)**, **동료 (Lateral)**, **고객 (External)** 등 세 가지 주요 수신 대상에 맞춘 최적화된 변환 기능을 제공합니다.

### 주요 기술 스택
- **프론트엔드**: HTML5, Tailwind CSS (CDN), Vanilla JavaScript.
- **백엔드**: Python 3.11+, Flask, Flask-CORS, python-dotenv.
- **AI 엔진**: Groq API (`moonshotai/kimi-k2-instruct-0905` 모델 사용).
- **배포**: Vercel (프론트엔드 + 서버리스 함수).

### 아키텍처
본 프로젝트는 클라이언트와 서버가 분리된 구조를 따릅니다:
- **클라이언트**: 사용자 입력을 받고 AI 생성 결과를 표시하는 반응형 단일 페이지 애플리케이션(SPA).
- **서버**: 프롬프트 엔지니어링을 수행하고 Groq AI 서비스와 통신을 중개하는 Flask 기반 REST API.

---

## 빌드 및 실행 방법

### 사전 요구사항
- Python 3.11 이상.
- 유효한 Groq API 키.

### 백엔드 설정
1. **프로젝트 루트 디렉토리로 이동합니다.**
2. **가상 환경 생성 및 활성화**:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   ```
3. **의존성 설치**:
   ```bash
   pip install -r backend/requirements.txt
   ```
4. **환경 변수 설정**:
   루트 디렉토리에 `.env` 파일을 생성하고 Groq API 키를 추가합니다:
   ```env
   GROQ_API_KEY=your_actual_api_key_here
   ```
5. **애플리케이션 실행**:
   ```bash
   python backend/app.py
   ```
   서버는 `http://127.0.0.1:5001`에서 시작됩니다.

### 접속 방법
백엔드가 실행되면 브라우저에서 `http://127.0.0.1:5001`에 접속합니다. Flask 서버가 루트 경로에서 `frontend/index.html` 파일을 서빙합니다.

---

## 프로젝트 구조
- `backend/`: Flask 서버(`app.py`) 및 의존성 목록(`requirements.txt`) 포함.
- `frontend/`: 정적 웹 파일(`index.html`, `js/script.js`) 포함.
- `PRD.md`: 상세 제품 요구사항 문서.
- `프로그램개요서.md`: 프로젝트 기획 개요서.
- `my-rules.md`: 프로젝트 전용 AI 행동 규칙.

---

## 개발 컨벤션

### 스타일링
- **Tailwind CSS**: `index.html` 내 CDN을 통해 유틸리티 퍼스트 스타일링 적용. 커심 테마(색상, 폰트 등)는 `tailwind.config` 스크립트 블록에 정의됨.
- **폰트**: 비즈니스 환경의 가독성을 위해 **Pretendard**를 기본 서체로 사용함.

### API 및 로직
- **RESTful API**: 메인 엔드포인트는 `POST /api/convert`이며, JSON 바디에 `text`와 `target` 필드를 기대함.
- **프롬프트 엔지니어링**: `target`에 따라 시스템 프롬프트를 동적으로 선택하여 페르소나에 맞는 결과를 생성함 (예: 상사 대상 '하십시오체', 동료 대상 부드러운 '해요체').
- **에러 처리**: 
  - 백엔드에서는 상세 에러 로그를 `backend/logs/error.log`에 기록함.
  - 프론트엔드에서는 로더 및 알림창을 통해 사용자에게 시각적 피드백을 제공함.

### 버전 관리
- **브랜치 전략**: `feature` -> `develop` -> `main`.
- **커밋 메시지**: 의미 있는 단위로 명확하게 작성할 것을 권장함.

---

## 개발 현황
- **1단계 (환경 설정)**: 완료.
- **2단계 (프론트엔드 UI)**: 완료 (Tailwind 기반 모던 UI 적용).
- **3단계 (백엔드 로직)**: 완료 (Groq API 연동 및 kimi-k2 모델 적용).
- **4단계 (통합 및 배포)**: 진행 예정.