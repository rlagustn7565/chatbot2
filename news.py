import os
import requests
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import urllib3
import html
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# .env 파일 로드
load_dotenv()

# Naver API 설정
NAVER_CLIENT_ID = os.getenv('NAVER_CLIENT_ID')
NAVER_CLIENT_SECRET = os.getenv('NAVER_CLIENT_SECRET')


def get_ranking_news() -> List[Dict[str, str]]:
    """
    네이버 금융의 '많이 본 뉴스' 상위 5개를 스크래핑

    Returns:
        List[Dict[str, str]]: 뉴스 제목과 링크의 딕셔너리 리스트
        예: [{"title": "제목", "link": "https://..."},...]
    """
    try:
        url = "https://finance.naver.com/news/"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10, verify=False)
        response.encoding = 'utf-8'

        if response.status_code != 200:
            print(f"⚠️ 네이버 금융 페이지 접속 오류: {response.status_code}")
            return get_mock_ranking_news()

        soup = BeautifulSoup(response.content, 'html.parser')

        # '많이 본 뉴스' 섹션 찾기
        ranking_section = soup.find('div', {'class': 'ranking_box'})

        if not ranking_section:
            print("⚠️ 많이 본 뉴스 섹션을 찾을 수 없습니다.")
            return get_mock_ranking_news()

        news_list = []
        articles = ranking_section.find_all('li')

        for article in articles[:5]:
            try:
                link_tag = article.find('a')
                if not link_tag:
                    continue

                title = link_tag.get_text(strip=True)
                link = link_tag.get('href', '')

                # 상대 URL을 절대 URL로 변환
                if link and not link.startswith('http'):
                    link = 'https://finance.naver.com' + link

                if title and link:
                    news_list.append({
                        'title': title,
                        'link': link
                    })
            except Exception as e:
                print(f"뉴스 항목 파싱 중 오류: {e}")
                continue

        return news_list if news_list else get_mock_ranking_news()

    except Exception as e:
        print(f"⚠️ 많이 본 뉴스 조회 중 오류: {e}")
        return get_mock_ranking_news()


def search_news(keyword: str) -> List[Dict[str, str]]:
    """
    네이버 뉴스 검색을 통해 특정 키워드의 최신 뉴스 3개 조회

    Args:
        keyword: 검색 키워드

    Returns:
        List[Dict[str, str]]: 뉴스 제목, 링크, 설명의 딕셔너리 리스트
        예: [{"title": "제목", "link": "https://...", "description": "요약"},...]
    """
    if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
        print("⚠️ 네이버 API 키가 설정되지 않았습니다.")
        return get_mock_search_news(keyword)

    try:
        url = "https://naverapihub.apigw.ntruss.com/search/v1/news"

        headers = {
            'X-NCP-APIGW-API-KEY-ID': NAVER_CLIENT_ID,
            'X-NCP-APIGW-API-KEY': NAVER_CLIENT_SECRET
        }

        params = {
            'query': keyword,
            'display': 3,
            'sort': 'date',
            'start': 1
        }

        response = requests.get(url, headers=headers, params=params, timeout=10, verify=False)
        response.encoding = 'utf-8'

        if response.status_code != 200:
            print(f"⚠️ 뉴스 검색 API 응답 오류: {response.status_code}")
            return get_mock_search_news(keyword)

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

        return news_list[:3] if news_list else get_mock_search_news(keyword)

    except Exception as e:
        print(f"⚠️ 뉴스 검색 중 오류: {e}")
        return get_mock_search_news(keyword)


def get_article_text(url: str) -> Optional[str]:
    """
    기사 URL에서 본문 텍스트를 BeautifulSoup으로 추출

    Args:
        url: 기사 URL

    Returns:
        str: 추출된 본문 텍스트 (실패 시 None)
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10, verify=False)
        response.encoding = 'utf-8'

        if response.status_code != 200:
            print(f"⚠️ URL 접속 실패: {response.status_code}")
            return None

        soup = BeautifulSoup(response.content, 'html.parser')

        # 네이버 기사 본문 찾기 (여러 선택자 시도)
        article_body = None

        # 네이버 뉴스 기사 본문
        article_body = soup.find('div', {'class': 'article_body'})

        # 다른 사이트 기사 본문
        if not article_body:
            article_body = soup.find('article')

        if not article_body:
            article_body = soup.find('div', {'class': ['content', 'article', 'post']})

        if not article_body:
            # 모든 p 태그 수집
            paragraphs = soup.find_all('p')
            if paragraphs:
                text = ' '.join([p.get_text(strip=True) for p in paragraphs])
            else:
                return None
        else:
            text = article_body.get_text(separator='\n', strip=True)

        # 불필요한 공백 제거
        text = re.sub(r'\n+', '\n', text)
        text = text.strip()

        if text:
            print(f"✅ 본문 추출 성공 ({len(text)}자)")
            return text
        else:
            print("⚠️ 추출된 본문이 없습니다.")
            return None

    except Exception as e:
        print(f"⚠️ 본문 추출 중 오류: {e}")
        return None


def get_mock_ranking_news() -> List[Dict[str, str]]:
    """테스트용 많이 본 뉴스 임시 데이터"""
    return [
        {
            'title': '코스피, 장중 2,500선 회복... 반도체·자동차 강세',
            'link': 'https://finance.naver.com/news/article/001/0000000001'
        },
        {
            'title': '삼성전자, 반도체 신규 투자 확대... 4분기 실적 기대감 상승',
            'link': 'https://finance.naver.com/news/article/002/0000000002'
        },
        {
            'title': '기준금리 현 수준 유지... 금융통화위원회 결정',
            'link': 'https://finance.naver.com/news/article/003/0000000003'
        },
        {
            'title': '원화·달러 환율 1,200원 근처... 엔저 영향으로 변동성 커져',
            'link': 'https://finance.naver.com/news/article/004/0000000004'
        },
        {
            'title': '미국 인플레이션 둔화... 글로벌 주식시장 상승 마감',
            'link': 'https://finance.naver.com/news/article/005/0000000005'
        }
    ]


def get_mock_search_news(keyword: str) -> List[Dict[str, str]]:
    """테스트용 검색 결과 임시 데이터"""
    return [
        {
            'title': f'"{keyword}" 관련 최신 뉴스 1',
            'link': 'https://news.naver.com/article/001/0001',
            'description': f'{keyword}에 대한 최신 소식입니다.'
        },
        {
            'title': f'"{keyword}" 관련 최신 뉴스 2',
            'link': 'https://news.naver.com/article/002/0002',
            'description': f'{keyword} 시장 분석 결과가 나왔습니다.'
        },
        {
            'title': f'"{keyword}" 관련 최신 뉴스 3',
            'link': 'https://news.naver.com/article/003/0003',
            'description': f'{keyword} 업계 전문가 의견입니다.'
        }
    ]


if __name__ == "__main__":
    print("=" * 60)
    print("📰 뉴스 수집 기능 테스트")
    print("=" * 60)

    # 1. 많이 본 뉴스 테스트
    print("\n[1] 네이버 금융 '많이 본 뉴스' 상위 5개")
    print("-" * 60)
    ranking_news = get_ranking_news()

    if ranking_news:
        print(f"✅ 총 {len(ranking_news)}개의 뉴스를 가져왔습니다:\n")
        for i, item in enumerate(ranking_news, 1):
            print(f"{i}. 제목: {item['title']}")
            print(f"   링크: {item['link']}\n")
    else:
        print("❌ 뉴스를 가져올 수 없습니다.")

    # 2. 키워드 검색 테스트
    print("\n[2] 키워드 검색 ('AI'로 검색, 최신 3개)")
    print("-" * 60)
    search_results = search_news("AI")

    if search_results:
        print(f"✅ 총 {len(search_results)}개의 뉴스를 가져왔습니다:\n")
        for i, item in enumerate(search_results, 1):
            print(f"{i}. 제목: {item['title']}")
            print(f"   링크: {item['link']}")
            print(f"   설명: {item['description']}\n")
    else:
        print("❌ 뉴스를 가져올 수 없습니다.")

    # 3. 본문 추출 테스트 (간단한 예시)
    print("\n[3] 본문 추출 테스트")
    print("-" * 60)
    if ranking_news:
        test_url = ranking_news[0]['link']
        print(f"테스트 URL: {test_url}\n")
        article_text = get_article_text(test_url)
        if article_text:
            print(f"추출된 본문 (처음 200자):\n{article_text[:200]}...\n")
        else:
            print("본문 추출 실패\n")

    print("=" * 60)
    print("✅ 테스트 완료")
    print("=" * 60)
