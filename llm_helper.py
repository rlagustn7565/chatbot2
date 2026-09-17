import os
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from google import genai

# .env 파일 로드
load_dotenv()

# Gemini API 설정
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')


def summarize_news(news_list: List[Dict[str, str]]) -> Optional[str]:
    """
    뉴스 리스트를 받아 Gemini AI로 3줄 요약 생성

    Args:
        news_list: 뉴스 딕셔너리 리스트
        [{"title": "제목", "link": "URL", "description": "요약"},...]

    Returns:
        요약 텍스트 또는 None (오류 시)
    """
    if not GEMINI_API_KEY:
        print("❌ Gemini API 키가 설정되지 않았습니다.")
        return None

    if not news_list or len(news_list) == 0:
        print("⚠️ 뉴스가 없습니다.")
        return None

    try:
        print("🤖 Gemini AI로 뉴스 요약 중...")

        # 뉴스 텍스트 구성
        news_text = ""
        for i, news in enumerate(news_list, 1):
            news_text += f"\n기사 {i}:\n"
            news_text += f"제목: {news.get('title', '')}\n"
            news_text += f"설명: {news.get('description', '')}\n"

        prompt = f"""다음 금융 뉴스들을 읽고, 주식 초보자도 이해하기 쉽게 핵심 내용을 정확히 3줄로 요약해 줘.

{news_text}

요약 (정확히 3줄):"""

        client = genai.Client(api_key=GEMINI_API_KEY)

        interaction = client.interactions.create(
            model="gemini-3.6-flash",
            input=prompt
        )

        summary = interaction.output_text.strip()

        print("✅ 뉴스 요약 완료!\n")
        return summary

    except Exception as e:
        print(f"❌ 뉴스 요약 중 오류: {e}")
        import traceback
        traceback.print_exc()
        return None


def analyze_stock(price_data: Dict[str, Any], news_list: List[Dict[str, str]]) -> Optional[str]:
    """
    주식 가격 데이터와 뉴스 리스트를 받아 Gemini AI로 투심 분석 진행

    Args:
        price_data: 주식 데이터 딕셔너리
        {
            "name": "종목명",
            "code": "종목코드",
            "price": 현재가,
            "change": 변화액,
            "change_rate": 등락률,
            ...
        }
        news_list: 뉴스 리스트

    Returns:
        마크다운 형식의 투심 분석 텍스트
    """
    if not GEMINI_API_KEY:
        print("❌ Gemini API 키가 설정되지 않았습니다.")
        return None

    if not price_data or not news_list:
        print("⚠️ 데이터가 부족합니다.")
        return None

    try:
        print("🤖 Gemini AI로 투심 분석 중...")

        # 가격 데이터 텍스트 구성
        stock_name = price_data.get('name', 'N/A')
        current_price = price_data.get('price', 0)
        change_rate = price_data.get('change_rate', 0)

        price_text = f"""
[주식 정보]
종목명: {stock_name}
현재가: {current_price:,.0f}원
등락률: {change_rate:+.2f}%
"""

        # 뉴스 텍스트 구성
        news_text = ""
        for i, news in enumerate(news_list, 1):
            news_text += f"\n[기사 {i}]\n"
            news_text += f"제목: {news.get('title', '')}\n"
            news_text += f"내용: {news.get('description', '')}\n"

        prompt = f"""당신은 증권 전문가입니다. 다음 정보를 분석하여 마크다운 형식으로 투심 분석을 작성해 주세요.

{price_text}

{news_text}

다음 4가지 항목을 반드시 포함하여 작성해 주세요:

1. **📈 현재가 브리핑**: 현재가와 등락률을 요약하며, 오늘의 시장 움직임을 간단히 설명

2. **📰 관련 기사 요약**: 전달된 기사 3개의 핵심 내용을 각각 1-2줄씩 간단히 요약

3. **⚖️ 투심 분석**: 기사 내용을 바탕으로 현재 이 종목에 대한 시장의 분위기가 긍정적인지 부정적인지 평가하고, 그 이유를 명확히 설명 (긍정/부정/중립)

4. **🔗 관련주/테마주**: 당신의 지식을 활용하여 {stock_name}과 함께 움직일 가능성이 높은 관련주 2~3개를 꼽고, 각각 한 줄로 이유를 설명

📱 카카오톡에서 읽기 편하도록 적절한 이모지를 섞어 작성해 주세요.
마크다운 형식을 유지하되, 가독성을 최우선으로 하세요."""

        client = genai.Client(api_key=GEMINI_API_KEY)

        interaction = client.interactions.create(
            model="gemini-3.6-flash",
            input=prompt
        )

        analysis = interaction.output_text.strip()

        print("✅ 투심 분석 완료!\n")
        return analysis

    except Exception as e:
        print(f"❌ 투심 분석 중 오류: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    print("=" * 60)
    print("🤖 LLM Helper 테스트")
    print("=" * 60)

    # 테스트 데이터: 삼성전자
    test_price_data = {
        'name': '삼성전자',
        'code': '005930',
        'price': 80000,
        'change': 1600,
        'change_rate': 2.0,
        'date': '2026-09-17'
    }

    test_news_list = [
        {
            'title': '삼성전자, AI칩 수요 급증으로 반도체 부문 호황',
            'link': 'https://news.naver.com/article/001/0000000001',
            'description': '삼성전자가 AI 시대의 수혜주로 떠오르면서 반도체 부문의 실적이 크게 개선되고 있습니다.'
        },
        {
            'title': '삼성전자 신제품 갤럭시 Z Fold 6 사전주문 100만대 돌파',
            'link': 'https://news.naver.com/article/002/0000000002',
            'description': '갤럭시 Z Fold 6가 출시 이틀 만에 사전주문 100만대를 넘어서며 시장의 기대를 뛰어넘었습니다.'
        },
        {
            'title': '삼성전자, 쿼터 순익 역대 최고 경신 예상...투자심 회복',
            'link': 'https://news.naver.com/article/003/0000000003',
            'description': '애널리스트들이 삼성전자 3분기 순익이 역대 최고를 기록할 것으로 예상하면서 투자자들의 심리가 회복되고 있습니다.'
        }
    ]

    # 1. 뉴스 요약 테스트
    print("\n[1] 뉴스 요약 테스트")
    print("-" * 60)
    news_summary = summarize_news(test_news_list)
    if news_summary:
        print("📄 요약 결과:")
        print(news_summary)
        print()

    # 2. 투심 분석 테스트
    print("\n[2] 투심 분석 테스트")
    print("-" * 60)
    analysis = analyze_stock(test_price_data, test_news_list)
    if analysis:
        print("📊 분석 결과:")
        print(analysis)

    print("\n" + "=" * 60)
    print("✅ 테스트 완료")
    print("=" * 60)
