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

                # 기본 필터링
                if not title or not link:
                    continue

                # 종목명이 정확히 포함되어야 함
                if keyword not in title:
                    continue

                # ETF, 펀드 등 관련성 낮은 상품 제외만 함
                exclude_keywords = ['ETF', '펀드', '파생상품', '선물', '옵션', '스왑']
                has_exclude = any(exc_keyword in title for exc_keyword in exclude_keywords)

                if not has_exclude:
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


def get_trending_news() -> Optional[List[Dict[str, str]]]:
    """최신 트렌드 뉴스 수집 (기업 지정 없이 섹터별 수집)"""
    try:
        print("📊 최신 트렌드 뉴스 조회 중...")

        # 섹터별 키워드 (기업이 아닌 산업/섹터)
        keywords = ['반도체', 'AI', '자동차', '금융', '시장', '투자']
        news_list = []

        for keyword in keywords:
            try:
                results = search_news(keyword)
                if results:
                    news_list.extend(results)
                    if len(news_list) >= 10:
                        break
            except:
                continue

        if news_list:
            print(f"✅ {len(news_list)}개의 최신 뉴스를 찾았습니다!")
            return news_list[:10]
        else:
            print("⚠️ 뉴스를 찾을 수 없습니다.")
            return None

    except Exception as e:
        print(f"❌ 트렌드 뉴스 조회 오류: {e}")
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
