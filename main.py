import os
import requests
from typing import Dict, Any, Optional
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import threading

# 모듈 임포트
from dotenv import load_dotenv
from youtube import get_youtube_summary
from news import search_news, get_article_text
from stock import get_stock_price, get_stock_news, get_index_price, get_exchange_rate
from llm_helper import analyze_stock, summarize_news

# .env 파일 로드
load_dotenv()

app = FastAPI()

# ============================================================
# [1] 카카오톡 요청/응답 Pydantic 모델
# ============================================================

class KakaoRequest(BaseModel):
    """카카오톡 스킬에서 받는 요청 모델"""
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
# [2] FastAPI 라우터 - 즉시 응답 엔드포인트
# ============================================================

@app.post("/api/chat")
async def chat(request: KakaoRequest, background_tasks: BackgroundTasks):
    """
    카카오톡에서 사용자 발화를 받아 즉시 응답하고,
    백그라운드에서 분석 작업을 실행합니다.
    """
    try:
        # userRequest에서 발화와 콜백URL 파싱
        user_request = request.userRequest
        user_utterance = user_request.get("utterance", "")
        callback_url = user_request.get("callbackUrl")

        print(f"[📞 사용자 발화] {user_utterance}")
        print(f"[📡 콜백 URL] {callback_url}")

        # 즉시 응답: "분석 중입니다" 메시지
        immediate_response = SkillPayload(
            version="2.0",
            template=Template(
                outputs=[
                    Output(
                        simpleText=SimpleText(
                            text="데이터를 수집하고 AI가 분석 중입니다 ⏳\n잠시만 기다려주세요."
                        )
                    )
                ]
            )
        )

        # 백그라운드 작업 등록
        if callback_url:
            background_tasks.add_task(
                process_analysis_background,
                user_utterance,
                callback_url
            )

        return immediate_response.model_dump()

    except Exception as e:
        print(f"❌ 요청 처리 중 오류: {e}")
        return SkillPayload(
            version="2.0",
            template=Template(
                outputs=[
                    Output(
                        simpleText=SimpleText(text="요청 처리 중 오류가 발생했습니다.")
                    )
                ]
            )
        ).model_dump()


@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {"status": "ok"}


# ============================================================
# [3] 백그라운드 작업 함수 - 분석 로직
# ============================================================

def process_analysis_background(utterance: str, callback_url: str):
    """
    백그라운드에서 실행되는 분석 함수

    발화를 분석하여:
    1. 유튜브 링크 → 자막 추출 + 요약
    2. 종목명 → 주가 분석 + LLM 투심 분석
    3. 지수/환율 → 지수/환율 정보 조회
    """
    try:
        print(f"\n[🔄 백그라운드 분석 시작] {utterance}")

        result_text = None

        # ========== 분기 1: 유튜브 링크 감지 ==========
        if "youtube.com" in utterance or "youtu.be" in utterance:
            print("[🎥 유튜브 분석 시작]")
            result_text = analyze_youtube(utterance)

        # ========== 분기 2: 주식 종목 분석 ==========
        else:
            # 종목명 추출 (간단한 휴리스틱)
            stock_name = extract_stock_name(utterance)
            if stock_name:
                print(f"[📈 주식 분석 시작: {stock_name}]")
                result_text = analyze_stock_full(stock_name)

            # ========== 분기 3: 지수/환율 분석 ==========
            else:
                print("[📊 지수/환율 조회 시도]")
                result_text = analyze_index_or_exchange(utterance)

        # 결과가 없으면 안내 메시지
        if not result_text:
            result_text = "죄송합니다. 요청하신 내용을 분석할 수 없습니다.\n\n다음과 같이 요청해 보세요:\n• 유튜브 링크 (예: https://youtube.com/watch?v=...)\n• 종목명 (예: 삼성전자, SK하이닉스)\n• 지수/환율 (예: KOSPI, USD/KRW)"

        # 콜백 URL로 결과 전송
        send_callback_result(callback_url, result_text)

    except Exception as e:
        print(f"❌ 백그라운드 분석 중 오류: {e}")
        import traceback
        traceback.print_exc()
        send_callback_result(callback_url, f"분석 중 오류가 발생했습니다.\n\n오류: {str(e)}")


def analyze_youtube(utterance: str) -> Optional[str]:
    """
    유튜브 링크 처리
    """
    try:
        # youtube.py에서 get_youtube_summary 호출
        # (youtube.py에서 extract_video_id, get_youtube_transcript, summarize_transcript 사용)
        from youtube import get_youtube_summary

        summary = get_youtube_summary(utterance)

        if summary:
            return f"📺 **유튜브 영상 요약**\n\n{summary}"
        else:
            return "유튜브 영상 분석에 실패했습니다."

    except Exception as e:
        print(f"❌ 유튜브 분석 오류: {e}")
        return None


def analyze_stock_full(stock_name: str) -> Optional[str]:
    """
    주식 종목 분석 (주가 + 뉴스 + LLM 분석)
    """
    try:
        # 1. 주가 정보 조회
        price_data = get_stock_price(stock_name)
        if not price_data:
            return f"'{stock_name}' 종목을 찾을 수 없습니다."

        # 2. 뉴스 정보 조회
        news_list = get_stock_news(stock_name)
        if not news_list:
            return f"'{stock_name}'에 대한 뉴스를 찾을 수 없습니다."

        # 3. LLM으로 투심 분석
        analysis_result = analyze_stock(price_data, news_list)

        if analysis_result:
            return analysis_result
        else:
            return "분석 중 오류가 발생했습니다."

    except Exception as e:
        print(f"❌ 주식 분석 오류: {e}")
        return None


def analyze_index_or_exchange(utterance: str) -> Optional[str]:
    """
    지수/환율 조회
    """
    try:
        result_parts = []

        # 지수 검색
        indices = ['KOSPI', '코스피', 'KOSDAQ', '코스닥', 'NASDAQ', '나스닥', 'S&P500', 'SP500', 'DOW']
        for idx in indices:
            if idx in utterance:
                index_data = get_index_price(idx)
                if index_data:
                    result_parts.append(
                        f"📈 **{index_data.get('name', idx)}**\n"
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
                        f"💱 **{rate_data.get('pair', exch)}**\n"
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
    """
    발화에서 종목명 추출 (간단한 휴리스틱)
    """
    # 주요 대형주 리스트
    major_stocks = [
        '삼성전자', 'SK하이닉스', 'LG화학', 'NAVER', 'KB금융',
        '신한지주', '현대자동차', 'LG전자', '삼성SDI', '삼성화학',
        'SK이노베이션', '포스코', '현대모비스', '기아', 'HMM'
    ]

    for stock in major_stocks:
        if stock in utterance:
            return stock

    return None


def send_callback_result(callback_url: str, result_text: str):
    """
    분석 결과를 카카오톡의 콜백 URL로 POST 요청으로 전송
    """
    try:
        # 결과를 카카오톡 SkillPayload 형식으로 구성
        payload = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": result_text
                        }
                    }
                ]
            }
        }

        # POST 요청으로 콜백 URL에 결과 전송
        response = requests.post(
            callback_url,
            json=payload,
            timeout=10
        )

        if response.status_code == 200:
            print(f"✅ 콜백 전송 성공 (상태코드: {response.status_code})")
        else:
            print(f"⚠️ 콜백 전송 실패 (상태코드: {response.status_code})")

    except Exception as e:
        print(f"❌ 콜백 전송 중 오류: {e}")


# ============================================================
# [4] 서버 실행
# ============================================================

if __name__ == "__main__":
    import uvicorn
    print("🚀 카카오톡 챗봇 서버 시작...")
    print("📡 엔드포인트: http://0.0.0.0:8000/api/chat")
    uvicorn.run(app, host="0.0.0.0", port=8000)
