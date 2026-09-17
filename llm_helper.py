import os
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from anthropic import Anthropic
import threading

# .env 파일 로드
load_dotenv()

# Claude API 설정
CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')


def analyze_stock(price_data: Dict[str, Any], news_list: List[Dict[str, str]]) -> Optional[str]:
    """Claude API를 사용한 주식 분석"""
    if not price_data or not news_list:
        print("⚠️ 데이터가 부족합니다.")
        return None

    stock_name = price_data.get('name', 'N/A')
    current_price = price_data.get('price', 0)
    change_rate = price_data.get('change_rate', 0)

    try:
        print("🤖 Claude AI로 투심 분석 중...")

        # 뉴스 텍스트 준비
        news_text = ""
        for i, news in enumerate(news_list[:3], 1):
            title = news.get('title', '')[:40]
            news_text += f"기사{i}: {title}\n"

        prompt = f"""{stock_name}: {current_price:,.0f}원 ({change_rate:+.2f}%)
뉴스: {news_text}

긍정/부정/중립만 답변."""

        result = [None]
        error = [None]

        def call_claude():
            try:
                print(">>> [디버그] Claude 클라이언트 생성 중...")
                if not CLAUDE_API_KEY:
                    error[0] = "API 키 없음"
                    return

                client = Anthropic(api_key=CLAUDE_API_KEY)
                print(">>> [디버그] Claude 클라이언트 생성 완료")

                print(">>> [디버그] Claude API 네트워크 요청 시작...")
                message = client.messages.create(
                    model="claude-opus-5",
                    max_tokens=100,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                print(">>> [디버그] Claude API 응답 수신 완료!")

                result[0] = message.content[0].text.strip()[:400]
                print(f">>> [디버그] 응답 처리 완료 (길이: {len(result[0])}자)")
            except Exception as e:
                print(f">>> [디버그] call_claude 예외 발생: {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()
                error[0] = str(e)

        # 스레드에서 Claude 호출 (20초 타임아웃)
        thread = threading.Thread(target=call_claude, daemon=True)
        thread.start()
        thread.join(timeout=20)

        if result[0]:
            print("✅ 투심 분석 완료!\n")
            return result[0]

        if error[0]:
            print(f"⚠️ Claude 오류: {error[0]}")

        raise Exception("Claude 응답 없음")

    except Exception as e:
        print(f"⚠️ Claude 분석 실패, 폴백 사용: {e}")

        # 폴백: 뉴스 기반 간단한 분석
        sentiment = "중립"
        for news in news_list:
            title = news.get('title', '').lower()
            if any(word in title for word in ['상승', '호황', '증가', '상향', '강세']):
                sentiment = "긍정"
                break
            elif any(word in title for word in ['하락', '부진', '감소', '하향', '약세']):
                sentiment = "부정"
                break

        fallback = f"""📈 현재가: {stock_name} {current_price:,.0f}원 ({change_rate:+.2f}%)
⚖️ 투심: {sentiment}적
🔗 관련주: 미정

(AI 분석 불가로 기본 정보만 제공됩니다)"""

        print(f"✅ 폴백 분석 반환\n")
        return fallback


def summarize_news(news_list: List[Dict[str, str]]) -> Optional[str]:
    """뉴스 요약 (사용되지 않음 - analyze_stock에 통합)"""
    if not news_list:
        return None

    return "뉴스 요약 기능은 analyze_stock에 통합되었습니다."


if __name__ == "__main__":
    print("=" * 60)
    print("🤖 LLM Helper 테스트")
    print("=" * 60)

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

    print("\n[투심 분석 테스트]")
    print("-" * 60)
    analysis = analyze_stock(test_price_data, test_news_list)
    if analysis:
        print("📊 분석 결과:")
        print(analysis)

    print("\n" + "=" * 60)
    print("✅ 테스트 완료")
    print("=" * 60)
