import streamlit as st
import requests
from bs4 import BeautifulSoup
import anthropic
import re
from datetime import datetime

# ── 페이지 설정 ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="숏폼 영상 광고 제안서 생성기",
    page_icon="🎬",
    layout="wide",
)

st.markdown("""
<style>
    /* 메인 타이틀 */
    .main-title {
        text-align: center;
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }
    .sub-title {
        text-align: center;
        color: #888;
        margin-bottom: 1.5rem;
    }
    /* 결과 탭 내 마크다운 여백 */
    .block-container { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

# ── Claude API 키 로드 ────────────────────────────────────────────────────────
def get_api_key():
    """Streamlit Secrets → 환경 변수 순서로 API 키를 불러옵니다."""
    try:
        return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        import os
        return os.environ.get("ANTHROPIC_API_KEY", "")

# ── 랜딩 페이지 수집 ─────────────────────────────────────────────────────────
def fetch_page(url: str) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    resp = requests.get(url, headers=headers, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.content, "html.parser")

    # 불필요한 태그 제거
    for tag in soup(["script", "style", "nav", "footer", "iframe", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator="\n", strip=True)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # 토큰 과소비 방지: 최대 6,000자
    return text[:6000] + ("\n\n[이하 생략]" if len(text) > 6000 else "")


# ── Claude 호출 함수들 ────────────────────────────────────────────────────────
def run_appeal_analysis(client, page_text: str, url: str) -> str:
    prompt = f"""아래는 랜딩 페이지({url})에서 수집한 내용입니다.

--- 랜딩 페이지 내용 시작 ---
{page_text}
--- 랜딩 페이지 내용 끝 ---

이 내용을 바탕으로 **소구점 분석 보고서**를 작성해주세요.

## 제품·서비스 기본 정보
- 제품명 / 카테고리
- 핵심 타겟 고객
- 가격대 (명시된 경우)

## 현재 강조하고 있는 소구점
각 소구점을 번호로 나열하고, 왜 효과적인지 한 줄씩 설명해주세요.

## 놓치고 있는 소구점 (개선 기회)
랜딩 페이지에서 빠져 있지만 구매 전환에 도움이 될 소구점을 제안해주세요.

## 영상 광고에 활용할 핵심 소구점 TOP 3
선정 이유와 함께 간결하게 정리해주세요."""

    res = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )
    return res.content[0].text


def run_video_plan(client, appeal_result: str) -> str:
    prompt = f"""아래 소구점 분석 결과를 바탕으로 **30초 숏폼 영상 광고 기획안**을 작성해주세요.

--- 소구점 분석 결과 ---
{appeal_result}
--- 끝 ---

## 영상 기본 정보
- 권장 길이 (15초 / 30초)
- 포맷: 세로형 9:16
- 주요 플랫폼 (인스타그램 릴스 / 틱톡 / 유튜브 쇼츠)

## 핵심 메시지 (1문장)

## 타겟 시청자 페르소나
이 영상을 보고 가장 반응할 구체적인 인물을 묘사해주세요.

## 5컷 스토리보드

각 컷은 아래 형식으로 작성해주세요.

**[컷 1] 후킹 (0~3초)**
- 화면:
- 자막/나레이션: "…"
- 목적:

**[컷 2] 문제 제시 (3~8초)**
- 화면:
- 자막/나레이션: "…"
- 목적:

**[컷 3] 제품 소개 (8~18초)**
- 화면:
- 자막/나레이션: "…"
- 목적:

**[컷 4] 증거·신뢰 (18~25초)**
- 화면:
- 자막/나레이션: "…"
- 목적:

**[컷 5] CTA (25~30초)**
- 화면:
- 자막/나레이션: "…"
- 목적:

## 촬영·제작 가이드
- 필요한 촬영 소재
- 권장 편집 스타일
- BGM 분위기"""

    res = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=2500,
        messages=[{"role": "user", "content": prompt}],
    )
    return res.content[0].text


def run_proposal(client, appeal_result: str, video_plan: str) -> str:
    prompt = f"""아래 소구점 분석 및 영상 광고 기획안을 바탕으로 클라이언트에게 제출할 **숏폼 영상 광고 제안서**를 작성해주세요.
비즈니스 문서이므로 예의 바르고 전문적인 톤앤매너를 유지해주세요.

--- 소구점 분석 ---
{appeal_result[:1200]}
--- 끝 ---

--- 영상 광고 기획안 ---
{video_plan[:1200]}
--- 끝 ---

---

# 숏폼 영상 광고 제안서

## 1. 제안 개요
제안 목적 및 배경을 2~3문장으로 작성해주세요.

## 2. 현황 분석
- 제품·서비스의 주요 강점
- 숏폼 영상 광고가 필요한 이유

## 3. 제안 내용
- 영상 광고의 핵심 방향
- 주요 소구점 및 메시지 전략
- 영상 구성 요약

## 4. 기대 효과
- 고객 전환율 향상 (가능하면 업계 평균 데이터나 예시 수치 포함)
- 매출 증대 효과
- 브랜드 인지도 제고
- 플랫폼별 도달 효과

## 5. 제작 범위 및 일정 (예시)
기획/스크립트 → 촬영 → 편집·자막 → 납품 순서로 간단히 정리해주세요.

## 6. 마무리
전문적이고 신뢰감 있는 마무리 인사말을 작성해주세요."""

    res = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )
    return res.content[0].text


# ── UI ───────────────────────────────────────────────────────────────────────
st.markdown("<div class='main-title'>🎬 숏폼 영상 광고 제안서 생성기</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='sub-title'>랜딩 페이지 URL을 붙여넣으면 소구점 분석 · 영상 기획안 · 제안서를 자동으로 만들어드립니다.</div>",
    unsafe_allow_html=True,
)
st.divider()

url_input = st.text_input(
    "🔗 랜딩 페이지 URL",
    placeholder="https://example.com/product",
    help="분석할 제품 또는 서비스의 랜딩 페이지 주소를 입력하세요.",
)

generate_btn = st.button("🚀 제안서 생성하기", type="primary", use_container_width=True)

if generate_btn:
    api_key = get_api_key()

    # ── 입력 검증 ──
    if not api_key:
        st.error("API 키가 설정되어 있지 않습니다. 관리자에게 문의하세요.")
        st.stop()
    if not url_input.strip():
        st.warning("URL을 입력해주세요.")
        st.stop()
    if not url_input.startswith(("http://", "https://")):
        st.warning("URL은 http:// 또는 https://로 시작해야 합니다.")
        st.stop()

    client = anthropic.Anthropic(api_key=api_key)

    try:
        with st.status("분석 진행 중...", expanded=True) as status:

            st.write("📄 랜딩 페이지 내용을 수집하고 있습니다...")
            page_text = fetch_page(url_input.strip())
            st.write("✅ 랜딩 페이지 수집 완료")

            st.write("🔍 소구점을 분석하고 있습니다...")
            appeal_result = run_appeal_analysis(client, page_text, url_input)
            st.write("✅ 소구점 분석 완료")

            st.write("🎬 영상 광고 기획안을 작성하고 있습니다...")
            video_plan = run_video_plan(client, appeal_result)
            st.write("✅ 영상 광고 기획안 완료")

            st.write("📋 제안서를 작성하고 있습니다...")
            proposal = run_proposal(client, appeal_result, video_plan)
            st.write("✅ 제안서 작성 완료")

            status.update(label="✅ 완료! 아래에서 결과를 확인하세요.", state="complete")

        # ── 결과 탭 ──
        tab1, tab2, tab3 = st.tabs(["📊 소구점 분석", "🎬 영상 광고 기획안", "📋 제안서"])
        with tab1:
            st.markdown(appeal_result)
        with tab2:
            st.markdown(video_plan)
        with tab3:
            st.markdown(proposal)

        # ── 다운로드 ──
        now_str = datetime.now().strftime("%Y%m%d_%H%M")
        full_doc = f"""# 숏폼 영상 광고 제안서 패키지
생성일: {datetime.now().strftime("%Y년 %m월 %d일 %H:%M")}
URL: {url_input}

{"="*60}
# 1. 소구점 분석
{"="*60}

{appeal_result}

{"="*60}
# 2. 영상 광고 기획안
{"="*60}

{video_plan}

{"="*60}
# 3. 제안서
{"="*60}

{proposal}
"""
        st.download_button(
            label="📥 전체 결과 다운로드 (.txt)",
            data=full_doc.encode("utf-8"),
            file_name=f"영상광고제안서_{now_str}.txt",
            mime="text/plain",
            use_container_width=True,
        )

    except requests.exceptions.ConnectionError:
        st.error("랜딩 페이지에 접근할 수 없습니다. URL을 다시 확인해주세요.")
    except requests.exceptions.Timeout:
        st.error("랜딩 페이지 응답 시간이 초과되었습니다. 잠시 후 다시 시도해주세요.")
    except requests.exceptions.HTTPError as e:
        st.error(f"페이지를 불러오지 못했습니다: {e}")
    except anthropic.AuthenticationError:
        st.error("API 인증에 실패했습니다. 관리자에게 문의하세요.")
    except anthropic.RateLimitError:
        st.error("API 요청 한도에 도달했습니다. 잠시 후 다시 시도해주세요.")
    except Exception as e:
        st.error(f"예상치 못한 오류가 발생했습니다: {e}")
