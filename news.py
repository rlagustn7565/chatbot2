import requests
from typing import List, Dict, Optional
import os
import html
from dotenv import load_dotenv

load_dotenv()

NAVER_CLIENT_ID = os.getenv('NAVER_CLIENT_ID')
NAVER_CLIENT_SECRET = os.getenv('NAVER_CLIENT_SECRET')


def get_ranking_news() -> Optional[List[Dict[str, str]]]:
    """주요 종목의 뉴스 5개 (Naver API 실시간)"""
    try:
        print("📊 주요 종목 뉴스 조회 중...")
        stocks = ['삼성전자', 'SK하이닉스', '현대자동차', 'LG전자', 'NAVER']
        news_list = []
        
        for stock in stocks:
            results = search_news(stock)
            if results:
                news_list.extend(results)
                if len(news_list) >= 5:
                    break
        
        if news_list:
            print(f"✅ {len(news_list)}개의 뉴스를 찾았습니다!")
            return news_list[:5]
        else:
            print("⚠️ 뉴스를 찾을 수 없습니다.")
            return None
    except Exception as e:
        print(f"❌ 인기 뉴스 조회 오류: {e}")
        return None


def search_news(keyword: str) -> Optional[List[Dict[str, str]]]:
    """Naver API로 실시간 뉴스 검색"""
    try:
        print(f"📰 '{keyword}' 관련 뉴스 검색 중...")

        if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
            return None

        url = "https://naverapihub.apigw.ntruss.com/search/v1/news"

        headers = {
            'X-NCP-APIGW-API-KEY-ID': NAVER_CLIENT_ID,
            'X-NCP-APIGW-API-KEY': NAVER_CLIENT_SECRET
        }

        # 더 정확한 쿼리로 관련 없는 뉴스 필터링
        params = {
            'query': keyword,  # 종목명만으로 검색 (주가 제거 - 검색 결과 향상)
            'display': 20,  # 더 많이 가져와서 필터링
            'sort': 'date',
            'start': 1
        }

        response = requests.get(url, headers=headers, params=params, timeout=10, verify=False)

        if response.status_code != 200:
            return None

        data = response.json()
        news_list = []

        for item in data.get('items', []):
            try:
                title = html.unescape(item.get('title', ''))
                title = title.replace('<b>', '').replace('</b>', '')
                link = item.get('link', '')
                description = html.unescape(item.get('description', ''))
                description = description.replace('<b>', '').replace('</b>', '')[:200]

                # 강화된 필터링
                if not title or not link:
                    continue

                # 종목명이 정확히 포함되어야 함
                if keyword not in title:
                    continue

                # 금융/투자 관련 키워드 필터링
                finance_keywords = ['주가', '주식', '상승', '하락', '상승', '하락', '수익', '실적',
                                   '주가지수', '종가', '장중', '거래량', '투자', '수익률', '수익성',
                                   '주가지수', '증액', '감액', '매도', '매수', '배당', '신고가', '저가']

                has_finance_keyword = any(keyword in (title + description).lower() for keyword in finance_keywords)

                # ETF, 펀드 등 관련성 낮은 상품 제외
                exclude_keywords = ['ETF', '펀드', '파생상품', '선물', '옵션', '스왑']
                has_exclude = any(keyword in title for keyword in exclude_keywords)

                if has_finance_keyword and not has_exclude:
                    news_list.append({
                        'title': title,
                        'link': link,
                        'description': description
                    })
            except:
                continue

        if news_list:
            print(f"✅ {len(news_list)}개의 관련 뉴스를 찾았습니다!")
            return news_list[:3]
        return None

    except Exception as e:
        print(f"❌ 뉴스 검색 오류: {e}")
        return None


if __name__ == "__main__":
    print("=" * 60)
    print("📰 뉴스 API 테스트")
    print("=" * 60)
    
    ranking = get_ranking_news()
    if ranking:
        for i, news in enumerate(ranking, 1):
            print(f"{i}. {news['title']}")
            print(f"   {news['description']}")
            print(f"   🔗 {news['link']}\n")
    
    print("✅ 테스트 완료")
