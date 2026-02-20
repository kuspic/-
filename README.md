# 🎬 숏폼 영상 광고 제안서 생성기

랜딩 페이지 URL을 입력하면 소구점 분석 · 영상 광고 기획안 · 제안서를 자동으로 만들어주는 도구입니다.

---

## 배포 순서 (Streamlit Cloud 기준)

### 1단계 — GitHub에 코드 올리기

1. [github.com](https://github.com) 에서 새 저장소(repository) 생성
   - 이름 예시: `shortform-proposal-generator`
   - **Private(비공개)** 으로 설정
2. 아래 파일들을 업로드:
   - `app.py`
   - `requirements.txt`
   - `.streamlit/secrets.toml` ← **절대 올리지 마세요!** (아래 참고)

> ⚠️ `.streamlit/secrets.toml` 은 API 키가 담겨 있으므로 GitHub에 올리지 않습니다.
> 대신 Streamlit Cloud에서 직접 입력합니다. (3단계 참고)

---

### 2단계 — Streamlit Cloud 배포

1. [share.streamlit.io](https://share.streamlit.io) 접속 → GitHub 계정으로 로그인
2. **"New app"** 클릭
3. 저장소 · 브랜치 · 파일(`app.py`) 선택
4. **"Advanced settings"** 클릭

---

### 3단계 — API 키 등록

**Advanced settings → Secrets** 탭에 아래 내용을 붙여넣기:

```toml
ANTHROPIC_API_KEY = "sk-ant-여기에_실제_API_키_입력"
```

5. **"Deploy!"** 클릭 → 1~2분 후 배포 완료

---

### 4단계 — 수강생에게 URL 공유

배포 완료 후 생성되는 URL (예: `https://yourapp.streamlit.app`) 을
강의 커뮤니티 또는 노션 페이지에 공유하세요.

---

## API 키 발급 방법

1. [console.anthropic.com](https://console.anthropic.com) 접속
2. **API Keys** 메뉴 → **"Create Key"**
3. 생성된 키를 복사해서 Streamlit Cloud Secrets에 입력

> 💡 예상 비용: 제안서 1건당 약 $0.03~0.05 (Claude Opus 4.6 기준)
> 수강생 100명 × 월 5회 사용 = 월 $15~25 수준

---

## 파일 구조

```
├── app.py                  # 메인 앱
├── requirements.txt        # 패키지 목록
├── README.md               # 이 파일
└── .streamlit/
    └── secrets.toml        # API 키 (GitHub 제외, 로컬 테스트용)
```

---

## 로컬에서 테스트하는 방법

```bash
pip install -r requirements.txt
streamlit run app.py
```
