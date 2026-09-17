import os
from typing import Dict, Optional, List
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import urllib3
import html
from pykrx import stock as krx_stock
import pandas as pd
from datetime import datetime, timedelta
import FinanceDataReader as fdr

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# .env 파일 로드
load_dotenv()

# 네이버 API 설정
NAVER_CLIENT_ID = os.getenv('NAVER_CLIENT_ID')
NAVER_CLIENT_SECRET = os.getenv('NAVER_CLIENT_SECRET')


def get_stock_code_by_name(stock_name: str) -> Optional[str]:
    """
    종목명으로 종목코드 조회

    Args:
        stock_name: 종목명 (예: "삼성전자", "SK하이닉스")

    Returns:
        종목코드 (예: "005930") 또는 None
    """
    try:
        print(f"🔍 '{stock_name}' 종목코드 검색 중...")

        # 주요 종목 매핑
        stock_map = {
            '삼성전자': '005930',
            'SK하이닉스': '000660',
            'LG화학': '051910',
            'NAVER': '035420',
            'KB금융': '105560',
            '신한지주': '055550',
            '현대자동차': '005380',
            'LG전자': '066570',
            '삼성SDI': '006400',
            '삼성화학': '000810',
            'SK이노베이션': '096770',
            '포스코': '005490',
            '현대모비스': '012330',
            '기아': '000270',
            'HMM': '011200',
        }

        # 정확한 매칭
        if stock_name in stock_map:
            code = stock_map[stock_name]
            print(f"✅ 종목코드 찾음: {stock_name} ({code})")
            return code

        # 부분 매칭
        for name, code in stock_map.items():
            if stock_name in name or name in stock_name:
                print(f"✅ 종목코드 찾음: {name} ({code})")
                return code

        print(f"⚠️ '{stock_name}'을 찾을 수 없습니다.")
        return None

    except Exception as e:
        print(f"⚠️ 종목코드 검색 중 오류: {e}")
        return None


def get_stock_price(stock_name: str) -> Optional[Dict[str, any]]:
    """
    종목명을 입력받아 현재가와 등락률을 반환 (pykrx 사용)

    Args:
        stock_name: 종목명 (예: "삼성전자", "SK하이닉스")

    Returns:
        Dict: {
            "name": "종목명",
            "code": "종목코드",
            "price": 현재가,
            "change": 전일 대비 변화액,
            "change_rate": 등락률 (%)
        }
        또는 None (오류 시)
    """
    try:
        # 종목코드 조회
        stock_code = get_stock_code_by_name(stock_name)
        if not stock_code:
            print(f"❌ '{stock_name}'을 찾을 수 없습니다.")
            return None

        print(f"📊 {stock_name} 주가 정보 조회 중...")
        print(f">>> [디버그] pykrx 호출 시작 (종목코드: {stock_code})")

        # 오늘 날짜 기준 최근 데이터 조회
        today = pd.Timestamp.today()
        start_date = (today - timedelta(days=10)).strftime('%Y%m%d')
        end_date = today.strftime('%Y%m%d')
        print(f">>> [디버그] 조회 기간: {start_date} ~ {end_date}")

        # pykrx에서 OHLCV 데이터 조회
        print(f">>> [디버그] krx_stock.get_market_ohlcv 호출 중...")
        df = krx_stock.get_market_ohlcv(start_date, end_date, stock_code)
        print(f">>> [디버그] pykrx 응답 수신 완료! (행 수: {len(df)})")

        if df.empty:
            print(f"❌ 주가 데이터를 찾을 수 없습니다.")
            return None

        # 최신 데이터 (마지막 행)
        latest = df.iloc[-1]
        current_price = float(latest['종가'])

        # 전일 데이터와 비교
        change = 0
        change_rate = 0

        if len(df) > 1:
            prev = df.iloc[-2]
            prev_price = float(prev['종가'])
            change = current_price - prev_price
            change_rate = (change / prev_price) * 100

        result = {
            'name': stock_name,
            'code': stock_code,
            'price': current_price,
            'change': change,
            'change_rate': round(change_rate, 2),
            'date': str(df.index[-1].date()),
            'high': float(latest['고가']),
            'low': float(latest['저가']),
            'volume': int(latest['거래량'])
        }

        print(f"✅ 주가 조회 완료!")
        print(f"   현재가: {result['price']:,.0f}원")
        print(f"   변화액: {result['change']:+,.0f}원")
        print(f"   등락률: {result['change_rate']:+.2f}%")
        print(f"   고가: {result['high']:,.0f}원 | 저가: {result['low']:,.0f}원")

        return result

    except Exception as e:
        print(f"❌ 주가 조회 중 오류: {e}")
        import traceback
        traceback.print_exc()
        return None


def get_index_price(index_name: str) -> Optional[Dict[str, any]]:
    """
    지수명을 입력받아 현재가와 변화율을 반환 (finance-datareader 사용)

    Args:
        index_name: 지수명 (예: "KOSPI", "NASDAQ", "S&P500")

    Returns:
        Dict: {
            "name": "지수명",
            "symbol": "기호",
            "price": 현재값,
            "change": 변화액,
            "change_rate": 변화율 (%)
        }
        또는 None (오류 시)
    """
    try:
        # 지수 심볼 매핑
        index_map = {
            'KOSPI': '^KS11',
            '코스피': '^KS11',
            'KOSDAQ': '^KQ11',
            '코스닥': '^KQ11',
            'NASDAQ': '^IXIC',
            '나스닥': '^IXIC',
            'S&P500': '^GSPC',
            'SP500': '^GSPC',
            'DOW': '^DJI',
            'DAX': '^GDAXI',
        }

        # 심볼 찾기
        symbol = index_map.get(index_name)
        if not symbol:
            print(f"⚠️ '{index_name}' 지수를 찾을 수 없습니다.")
            return None

        print(f"📊 {index_name} 지수 조회 중...")

        # finance-datareader로 데이터 조회
        df = fdr.DataReader(symbol, '2026-09-01')

        if df.empty:
            print(f"❌ 지수 데이터를 찾을 수 없습니다.")
            return None

        latest = df.iloc[-1]
        current_price = float(latest['Close'])

        # 변화량 계산
        change = 0
        change_rate = 0

        if len(df) > 1:
            prev = df.iloc[-2]
            prev_price = float(prev['Close'])
            change = current_price - prev_price
            change_rate = (change / prev_price) * 100

        result = {
            'name': index_name,
            'symbol': symbol,
            'price': current_price,
            'change': change,
            'change_rate': round(change_rate, 2),
            'date': str(df.index[-1].date())
        }

        print(f"✅ 지수 조회 완료!")
        print(f"   현재값: {result['price']:,.0f}")
        print(f"   변화: {result['change']:+,.0f}")
        print(f"   변화율: {result['change_rate']:+.2f}%")

        return result

    except Exception as e:
        print(f"❌ 지수 조회 중 오류: {e}")
        return None


def get_exchange_rate(currency_pair: str) -> Optional[Dict[str, any]]:
    """
    환율을 조회 (finance-datareader 사용)

    Args:
        currency_pair: 환율 쌍 (예: "USD/KRW", "EUR/USD", "JPY/KRW")

    Returns:
        Dict: {
            "pair": "USD/KRW",
            "rate": 1379.36,
            "change": 변화액,
            "change_rate": 변화율 (%)
        }
        또는 None (오류 시)
    """
    try:
        print(f"💱 {currency_pair} 환율 조회 중...")

        # finance-datareader로 환율 조회
        df = fdr.DataReader(currency_pair, '2026-09-01')

        if df.empty:
            print(f"❌ 환율 데이터를 찾을 수 없습니다.")
            return None

        latest = df.iloc[-1]
        current_rate = float(latest['Close'])

        # 변화량 계산
        change = 0
        change_rate = 0

        if len(df) > 1:
            prev = df.iloc[-2]
            prev_rate = float(prev['Close'])
            change = current_rate - prev_rate
            change_rate = (change / prev_rate) * 100

        result = {
            'pair': currency_pair,
            'rate': round(current_rate, 2),
            'change': round(change, 2),
            'change_rate': round(change_rate, 2),
            'date': str(df.index[-1].date())
        }

        print(f"✅ 환율 조회 완료!")
        print(f"   {currency_pair}: {result['rate']:,.2f}")
        print(f"   변화: {result['change']:+,.2f}")
        print(f"   변화율: {result['change_rate']:+.2f}%")

        return result

    except Exception as e:
        print(f"❌ 환율 조회 중 오류: {e}")
        return None


def get_stock_news(stock_name: str) -> Optional[List[Dict[str, str]]]:
    """
    종목명을 입력받아 최신 뉴스 3개 반환

    Args:
        stock_name: 종목명 (예: "삼성전자", "SK하이닉스")

    Returns:
        List[Dict]: 뉴스 제목, 링크, 설명의 딕셔너리 리스트
        [{"title": "제목", "link": "URL", "description": "요약"},...]
        또는 None (오류 시)
    """
    if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
        print("⚠️ 네이버 API 키가 설정되지 않았습니다.")
        return get_mock_news(stock_name)

    try:
        print(f"📰 {stock_name} 관련 뉴스 검색 중...")
        print(f">>> [디버그] Naver API 뉴스 검색 시작")

        url = "https://naverapihub.apigw.ntruss.com/search/v1/news"

        headers = {
            'X-NCP-APIGW-API-KEY-ID': NAVER_CLIENT_ID,
            'X-NCP-APIGW-API-KEY': NAVER_CLIENT_SECRET
        }

        params = {
            'query': f"{stock_name} 주가",
            'display': 3,
            'sort': 'date',
            'start': 1
        }

        print(f">>> [디버그] requests.get 호출 중...")
        response = requests.get(url, headers=headers, params=params, timeout=10, verify=False)
        print(f">>> [디버그] Naver API 응답 수신 (상태코드: {response.status_code})")
        response.encoding = 'utf-8'

        if response.status_code != 200:
            print(f"⚠️ 뉴스 조회 API 응답 오류: {response.status_code}")
            return get_mock_news(stock_name)

        data = response.json()
        news_list = []

        for item in data.get('items', []):
            try:
                title = html.unescape(item.get('title', ''))
                title = title.replace('<b>', '').replace('</b>', '')

                link = item.get('link', '')
                description = html.unescape(item.get('description', ''))
                description = description.replace('<b>', '').replace('</b>', '')

                if title and link:
                    news_list.append({
                        'title': title,
                        'link': link,
                        'description': description
                    })
            except Exception as e:
                print(f"뉴스 항목 파싱 중 오류: {e}")
                continue

        if news_list:
            print(f"✅ {len(news_list)}개의 뉴스를 가져왔습니다!")
            return news_list[:3]
        else:
            print("⚠️ 관련 뉴스를 찾을 수 없습니다.")
            return get_mock_news(stock_name)

    except Exception as e:
        print(f"❌ 뉴스 조회 중 오류: {e}")
        return get_mock_news(stock_name)


def get_mock_news(stock_name: str) -> List[Dict[str, str]]:
    """테스트용 임시 뉴스 데이터"""
    return [
        {
            'title': f'{stock_name}, 실적 발표 예정... 투자자 관심 높아져',
            'link': 'https://news.naver.com/article/001/0000000001',
            'description': f'{stock_name}의 분기별 실적이 기대보다 좋을 것 같습니다.'
        },
        {
            'title': f'{stock_name} 신제품 출시... 시장 점유율 확대 예상',
            'link': 'https://news.naver.com/article/002/0000000002',
            'description': f'{stock_name}이 새로운 제품 라인업을 공개했습니다.'
        },
        {
            'title': f'{stock_name}, 외국인 순매수 지속... 주가 상승률 높아',
            'link': 'https://news.naver.com/article/003/0000000003',
            'description': f'외국인 투자자들이 {stock_name}을 지속적으로 사고 있습니다.'
        }
    ]


if __name__ == "__main__":
    print("=" * 60)
    print("📊 금융 정보 수집 기능 테스트 (pykrx + finance-datareader)")
    print("=" * 60)

    # 1. 주가 정보 테스트
    print(f"\n[1] 주가 조회: SK하이닉스")
    print("-" * 60)
    price_info = get_stock_price("SK하이닉스")
    if price_info:
        print(f"   현재가: {price_info['price']:,.0f}원")
        print(f"   변화: {price_info['change']:+,.0f}원 ({price_info['change_rate']:+.2f}%)\n")

    # 2. 지수 정보 테스트
    print(f"[2] 지수 조회: KOSPI")
    print("-" * 60)
    index_info = get_index_price("KOSPI")
    if index_info:
        print(f"   현재값: {index_info['price']:,.0f}")
        print(f"   변화: {index_info['change']:+,.0f} ({index_info['change_rate']:+.2f}%)\n")

    # 3. 환율 정보 테스트
    print(f"[3] 환율 조회: USD/KRW")
    print("-" * 60)
    rate_info = get_exchange_rate("USD/KRW")
    if rate_info:
        print(f"   환율: {rate_info['rate']:,.2f}원")
        print(f"   변화: {rate_info['change']:+,.2f} ({rate_info['change_rate']:+.2f}%)\n")

    # 4. 뉴스 정보 테스트
    print(f"[4] 뉴스 조회: SK하이닉스")
    print("-" * 60)
    news_list = get_stock_news("SK하이닉스")
    if news_list:
        print(f"✅ {len(news_list)}개 뉴스:")
        for i, news in enumerate(news_list, 1):
            print(f"   {i}. {news['title'][:50]}...\n")

    print("=" * 60)
    print("✅ 모든 테스트 완료")
    print("=" * 60)
