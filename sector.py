from typing import Dict, List, Optional
from news import search_news
from llm_helper import analyze_news_sentiment

# 섹터 정의
SECTORS = {
    '반도체': {
        'name': '반도체',
        'stocks': ['삼성전자', 'SK하이닉스', 'NAVER'],
        'keywords': ['반도체', 'AI칩', '파운드리']
    },
    '자동차': {
        'name': '자동차',
        'stocks': ['현대자동차', '기아'],
        'keywords': ['자동차', 'EV', '전기차', '수소차']
    },
    '금융': {
        'name': '금융',
        'stocks': ['신한은행', 'KB금융'],
        'keywords': ['금융', '은행', '투자']
    },
    '전자': {
        'name': '전자',
        'stocks': ['LG전자', '삼성전자'],
        'keywords': ['전자', '가전', 'TV']
    },
    'IT': {
        'name': 'IT',
        'stocks': ['NAVER', '카카오'],
        'keywords': ['IT', '인터넷', '소프트웨어']
    },
    '코인': {
        'name': '암호화폐',
        'stocks': [],
        'keywords': ['비트코인', '이더리움', '암호화폐']
    },
    '바이오': {
        'name': '바이오',
        'stocks': ['셀트리온', '삼성바이오로직스', '제넨바이오'],
        'keywords': ['바이오', '제약', '의약품', '백신']
    },
    '2차전지': {
        'name': '2차전지',
        'stocks': ['LG에너지솔루션', 'SK이노베이션', '삼성SDI'],
        'keywords': ['전지', '배터리', '에너지', '전기']
    },
    'AI': {
        'name': 'AI',
        'stocks': ['NAVER', '카카오', '삼성전자'],
        'keywords': ['AI', '인공지능', '딥러닝', '머신러닝']
    },
    '건설': {
        'name': '건설',
        'stocks': ['현대건설', '삼성물산', '롯데건설'],
        'keywords': ['건설', '부동산', '건축']
    },
    '조선': {
        'name': '조선',
        'stocks': ['현대중공업', '삼성중공업', '대우조선해양'],
        'keywords': ['조선', '선박', '해양']
    },
    '화장품': {
        'name': '화장품',
        'stocks': ['에이모레퍼시픽', 'LG생활건강', '코스맥스'],
        'keywords': ['화장품', '뷰티', '미용']
    },
    '엔터': {
        'name': '엔터테인먼트',
        'stocks': ['하이브', 'SM엔터테인먼트', 'JYP엔터테인먼트'],
        'keywords': ['엔터', '방송', '음악', '영화']
    },
}

def get_sector_analysis(sector_name: str) -> Optional[str]:
    """섹터 분석"""
    try:
        # 섹터 찾기
        sector = None
        for key, value in SECTORS.items():
            if sector_name in key or sector_name in value['name']:
                sector = value
                break

        if not sector:
            return f"❌ '{sector_name}' 섹터를 찾을 수 없습니다.\n사용 가능한 섹터: {', '.join(SECTORS.keys())}"

        print(f"📊 {sector['name']} 섹터 분석 중...")

        result = f"""📈 {sector['name']} 섹터 분석

🏢 주도 종목:"""

        if sector['stocks']:
            for stock in sector['stocks']:
                result += f"\n• {stock}"
        else:
            result += "\n• 암호화폐 시장 전반"

        # 섹터 뉴스 조회
        result += f"\n\n📰 최신 뉴스:\n"

        news_found = False
        for keyword in sector['keywords']:
            news_list = search_news(keyword)
            if news_list:
                for i, news in enumerate(news_list[:2], 1):
                    sentiment = analyze_news_sentiment(sector['name'], news['title'])
                    result += f"\n{i}. {sentiment} {news['title']}"
                    result += f"\n   {news['description'][:100]}"
                news_found = True
                break

        if not news_found:
            result += "\n관련 뉴스를 찾을 수 없습니다."

        return result

    except Exception as e:
        print(f"❌ 섹터 분석 중 오류: {e}")
        return None


def get_all_sectors() -> str:
    """모든 섹터 목록"""
    result = "📊 사용 가능한 섹터:\n\n"
    for key in SECTORS.keys():
        result += f"• {key}\n"
    return result


def get_leading_sector() -> Optional[str]:
    """현재 주도섹터 분석 - 긍정 뉴스가 많은 섹터"""
    try:
        print("📊 주도 섹터 분석 중...")
        sector_scores = {}

        for sector_name, sector in SECTORS.items():
            positive_count = 0
            news_count = 0

            for keyword in sector['keywords']:
                news_list = search_news(keyword)
                if news_list:
                    for news in news_list[:2]:
                        sentiment = analyze_news_sentiment(sector_name, news['title'])
                        news_count += 1
                        if sentiment == "📈":
                            positive_count += 1
                    break

            if news_count > 0:
                score = positive_count / news_count
                sector_scores[sector_name] = {
                    'score': score,
                    'positive': positive_count,
                    'total': news_count
                }

        if not sector_scores:
            return "주도 섹터 분석을 위한 데이터가 부족합니다."

        # 점수 높은 순서로 정렬
        sorted_sectors = sorted(sector_scores.items(), key=lambda x: x[1]['score'], reverse=True)

        result = """📈 현재 주도 섹터

🏆 강세 섹터:"""

        for i, (sector_name, data) in enumerate(sorted_sectors[:3], 1):
            result += f"\n{i}. {sector_name} ({data['positive']}/{data['total']} 긍정뉴스)"

        if len(sorted_sectors) > 3:
            result += "\n\n📊 기타 섹터:"
            for sector_name, data in sorted_sectors[3:]:
                result += f"\n• {sector_name} ({data['positive']}/{data['total']})"

        return result

    except Exception as e:
        print(f"❌ 주도 섹터 분석 중 오류: {e}")
        return None
