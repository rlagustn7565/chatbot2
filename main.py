import os
import requests
from typing import Dict, Any, Optional
from fastapi import FastAPI
from pydantic import BaseModel

# 모듈 임포트
from dotenv import load_dotenv
from youtube import get_youtube_summary
from stock import get_stock_price, get_index_price, get_exchange_rate, get_default_indices, get_default_rates
from news import get_ranking_news, search_news
import FinanceDataReader as fdr

# .env 파일 로드
load_dotenv()

app = FastAPI()

# ============================================================
# [1] 카카오톡 요청/응답 Pydantic 모델
# ============================================================

class KakaoRequest(BaseModel):
    userRequest: Dict[str, Any]

class SimpleText(BaseModel):
    text: str

class Output(BaseModel):
    simpleText: SimpleText

class Template(BaseModel):
    outputs: list[Output]

class SkillPayload(BaseModel):
    version: str = "2.0"
    template: Template

# ============================================================
# [2] FastAPI 라우터 - 동기 즉시 응답
# ============================================================

@app.post("/api/chat")
async def chat(request: KakaoRequest):
    """
    카카오톡에서 사용자 발화를 받아 즉시 분석 결과를 반환합니다.
    (콜백 구조 제거 - 동기 처리)
    """
    try:
        user_request = request.userRequest
        user_utterance = user_request.get("utterance", "").strip()

        print(f"[📞 사용자 발화] {user_utterance}")

        # ========== 헬프 명령어 처리 ==========
        if user_utterance.lower() in ["/help", "도움말", "사용법", "명령어", "help"]:
            print("[ℹ️ 헬프 요청]")
            help_text = """🤖 AI 금융 챗봇 - 사용 가능한 기능

📈 주식 종목 분석
- "삼성전자", "SK하이닉스", "LG화학" 등
- 실시간 주가, 뉴스, AI 투심 분석

📺 유튜브 영상 요약
- 유튜브 링크 입력
- 자막 추출 → AI 요약

📊 지수 조회
- "코스피", "KOSDAQ", "나스닥", "S&P500"

💱 환율 조회
- "USD/KRW", "원달러", "EUR/USD"

📰 뉴스 검색
- "삼성전자 뉴스", "AI 뉴스"

💡 아무 종목명이나 입력하면 분석 시작!"""

            return SkillPayload(
                version="2.0",
                template=Template(
                    outputs=[Output(simpleText=SimpleText(text=help_text))]
                )
            ).model_dump()

        # ========== 분석 시작 (동기 처리) ==========
        result_text = None

        # 유튜브 링크 감지
        if "youtube.com" in user_utterance or "youtu.be" in user_utterance:
            print("[🎥 유튜브 분석]")
            result_text = get_youtube_summary(user_utterance)

        # 명령어: "지수", "지표"
        elif any(cmd in user_utterance for cmd in ["지수", "지표"]):
            print("[📊 지수 조회]")
            result_text = get_default_indices()

        # 명령어: "환율"
        elif "환율" in user_utterance:
            print("[💱 환율 조회]")
            result_text = get_default_rates()

        # 명령어: "뉴스"
        elif "뉴스" in user_utterance:
            words = user_utterance.replace("뉴스", "").strip()

            if not words:
                # "뉴스"만 입력 → 인기 뉴스
                print("[📊 인기 뉴스 조회]")
                ranking = get_ranking_news()
                if ranking:
                    result_text = "📊 **현재 인기 뉴스**\n\n"
                    for i, news in enumerate(ranking[:5], 1):
                        result_text += f"{i}. {news['title']}\n🔗 {news['link']}\n\n"
                else:
                    result_text = "인기 뉴스를 조회할 수 없습니다."
            else:
                # "삼성전자 뉴스" 형식 → 검색
                print("[📰 뉴스 검색]")
                stock_name = extract_stock_name(words)
                if stock_name:
                    news_results = search_news(stock_name)
                    if news_results:
                        result_text = f"📰 **{stock_name} 뉴스**\n\n"
                        for i, news in enumerate(news_results[:3], 1):
                            result_text += f"{i}. {news['title']}\n📝 {news['description']}\n🔗 {news['link']}\n\n"
                    else:
                        result_text = f"'{stock_name}' 관련 뉴스를 찾을 수 없습니다."
                else:
                    result_text = "종목을 찾을 수 없습니다. '삼성전자 뉴스' 형식으로 입력해주세요."

        else:
            # 종목명 추출
            stock_name = extract_stock_name(user_utterance)
            if stock_name:
                print(f"[📈 주식 분석: {stock_name}]")
                result_text = analyze_stock_full(stock_name)
            else:
                # 지수/환율 조회
                print("[📊 지수/환율 조회]")
                result_text = analyze_index_or_exchange(user_utterance)

        # 결과가 없으면 안내 메시지
        if not result_text:
            result_text = "죄송합니다. 요청하신 내용을 분석할 수 없습니다.\n\n다음과 같이 요청해 보세요:\n• 유튜브 링크\n• 종목명 (예: 삼성전자)\n• 지수/환율 (예: KOSPI, USD/KRW)"

        # 즉시 결과 반환
        return SkillPayload(
            version="2.0",
            template=Template(
                outputs=[Output(simpleText=SimpleText(text=result_text))]
            )
        ).model_dump()

    except Exception as e:
        print(f"❌ 요청 처리 중 오류: {e}")
        import traceback
        traceback.print_exc()
        return SkillPayload(
            version="2.0",
            template=Template(
                outputs=[Output(simpleText=SimpleText(text="요청 처리 중 오류가 발생했습니다."))]
            )
        ).model_dump()

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# ============================================================
# [3] 분석 함수
# ============================================================

def analyze_stock_full(stock_name: str) -> Optional[str]:
    """주식 종목 분석 (5초 이내)"""
    try:
        # 1. 주가 정보만 빠르게 조회 (3초 이내)
        price_data = get_stock_price(stock_name)
        if not price_data:
            return f"'{stock_name}' 종목을 찾을 수 없습니다."

        # 2. 간단한 응답 (시간 초과 방지)
        result = f"""📊 {stock_name}

💰 현재가: {price_data['price']:,.0f}원
📈 변화율: {price_data['change_rate']:+.2f}%
📊 고가: {price_data['high']:,.0f}원
📉 저가: {price_data['low']:,.0f}원"""

        return result

    except Exception as e:
        print(f"❌ 주식 분석 오류: {e}")
        return "주식 정보를 조회할 수 없습니다."

def analyze_index_or_exchange(utterance: str) -> Optional[str]:
    """지수/환율 조회"""
    try:
        result_parts = []

        # 지수 검색
        indices = ['KOSPI', '코스피', 'KOSDAQ', '코스닥', 'NASDAQ', '나스닥', 'S&P500', 'SP500', 'DOW']
        for idx in indices:
            if idx in utterance:
                index_data = get_index_price(idx)
                if index_data:
                    result_parts.append(
                        f"📈 {index_data.get('name', idx)}\n"
                        f"현재값: {index_data.get('price', 'N/A'):,.0f}\n"
                        f"변화: {index_data.get('change', 0):+,.0f} ({index_data.get('change_rate', 0):+.2f}%)"
                    )

        # 환율 검색
        exchanges = ['USD/KRW', '원달러', 'EUR/USD', 'JPY/KRW']
        for exch in exchanges:
            if exch in utterance:
                if exch == '원달러':
                    exch = 'USD/KRW'

                rate_data = get_exchange_rate(exch)
                if rate_data:
                    result_parts.append(
                        f"💱 {rate_data.get('pair', exch)}\n"
                        f"환율: {rate_data.get('rate', 'N/A'):,.2f}\n"
                        f"변화: {rate_data.get('change', 0):+,.2f} ({rate_data.get('change_rate', 0):+.2f}%)"
                    )

        if result_parts:
            return "\n\n".join(result_parts)

        return None

    except Exception as e:
        print(f"❌ 지수/환율 조회 오류: {e}")
        return None

def extract_stock_name(utterance: str) -> Optional[str]:
    """StockListing으로 종목명 추출"""
    try:
        stock_list = fdr.StockListing('KRX')

        # 정확한 매칭
        exact = stock_list[stock_list['Name'] == utterance.strip()]
        if not exact.empty:
            return utterance.strip()

        # 부분 매칭
        partial = stock_list[stock_list['Name'].str.contains(utterance, case=False, na=False)]
        if not partial.empty:
            return partial.iloc[0]['Name']

        return None
    except:
        return None

# ============================================================
# [4] 서버 실행
# ============================================================

if __name__ == "__main__":
    import uvicorn
    print("🚀 카카오톡 챗봇 서버 시작...")
    print("📡 엔드포인트: http://0.0.0.0:8000/api/chat")
    uvicorn.run(app, host="0.0.0.0", port=8000)
