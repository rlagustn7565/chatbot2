import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from newspaper import Article
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_ranking_news() -> Optional[List[Dict[str, str]]]:
    """네이버 금융의 '많이 본 뉴스' 상위 5개 스크래핑"""
    try:
        print("📊 네이버 금융 인기 뉴스 조회 중...")

        url = "https://finance.naver.com/news/news_list.naver?mode=LSS2D&section=stock&search=&keyword="
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10, verify=False)
        response.encoding = 'utf-8'

        if response.status_code != 200:
            print(f"⚠️ 요청 실패: {response.status_code}")
            return None

        soup = BeautifulSoup(response.content, 'html.parser')
        
        articles = soup.find_all('tr', class_='_tr')[:5]
        
        news_list = []
        for article in articles:
            try:
                title_elem = article.find('a', class_='_link_title')
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                link = title_elem.get('href', '')
                
                if title and link:
                    if link.startswith('/'):
                        link = 'https://finance.naver.com' + link
                    
                    news_list.append({
                        'title': title,
                        'link': link
                    })
            except Exception as e:
                continue

        if news_list:
            print(f"✅ {len(news_list)}개의 인기 뉴스를 찾았습니다!")
            return news_list[:5]
        else:
            print("⚠️ 뉴스를 찾을 수 없습니다.")
            return None

    except Exception as e:
        print(f"❌ 인기 뉴스 조회 오류: {e}")
        return None


def search_news(keyword: str) -> Optional[List[Dict[str, str]]]:
    """네이버 뉴스 검색으로 키워드 관련 뉴스 3개 조회"""
    try:
        print(f"📰 '{keyword}' 관련 뉴스 검색 중...")

        url = f"https://search.naver.com/search.naver?where=news&query={keyword}&sort=date"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=10, verify=False)
        response.encoding = 'utf-8'

        if response.status_code != 200:
            print(f"⚠️ 검색 실패: {response.status_code}")
            return None

        soup = BeautifulSoup(response.content, 'html.parser')
        
        news_items = soup.find_all('div', class_='news_wrap')[:3]
        
        news_list = []
        for item in news_items:
            try:
                title_elem = item.find('a', class_='news_tit')
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                link = title_elem.get('href', '')
                
                desc_elem = item.find('div', class_='news_dsc')
                description = desc_elem.get_text(strip=True) if desc_elem else "설명 없음"

                if title and link:
                    news_list.append({
                        'title': title,
                        'link': link,
                        'description': description[:150]
                    })
            except Exception as e:
                continue

        if news_list:
            print(f"✅ {len(news_list)}개의 뉴스를 찾았습니다!")
            return news_list[:3]
        else:
            print("⚠️ 검색 결과가 없습니다.")
            return None

    except Exception as e:
        print(f"❌ 뉴스 검색 오류: {e}")
        return None


def get_article_text(url: str) -> Optional[str]:
    """기사 URL에서 본문 텍스트 추출"""
    try:
        print(f"📄 기사 본문 추출 중...")

        article = Article(url, language='ko')
        article.download()
        article.parse()

        if article.text:
            print(f"✅ {len(article.text)}자의 본문을 추출했습니다!")
            return article.text[:500]
        else:
            print("⚠️ 본문을 추출할 수 없습니다.")
            return None

    except Exception as e:
        print(f"❌ 본문 추출 오류: {e}")
        return None


if __name__ == "__main__":
    print("=" * 60)
    print("📰 뉴스 크롤링 테스트")
    print("=" * 60)

    print("\n[1] 네이버 금융 인기 뉴스")
    print("-" * 60)
    ranking = get_ranking_news()
    if ranking:
        for i, news in enumerate(ranking, 1):
            print(f"{i}. {news['title']}")
            print(f"   🔗 {news['link']}\n")

    print("\n[2] 뉴스 검색: 삼성전자")
    print("-" * 60)
    search_results = search_news("삼성전자")
    if search_results:
        for i, news in enumerate(search_results, 1):
            print(f"{i}. {news['title']}")
            print(f"   설명: {news['description']}")
            print(f"   🔗 {news['link']}\n")

    if search_results and search_results[0].get('link'):
        print("\n[3] 첫 번째 기사 본문 추출")
        print("-" * 60)
        article_text = get_article_text(search_results[0]['link'])
        if article_text:
            print(article_text[:300] + "...")

    print("\n" + "=" * 60)
    print("✅ 테스트 완료")
    print("=" * 60)
