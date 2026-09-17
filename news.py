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

                # 필터링: 제목에 종목명이 포함되고, 금융/주식 관련 키워드 있는지 확인
                if title and link and keyword in title:
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
