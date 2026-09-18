from typing import Dict, List, Optional
from news import search_news

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
        'keywords': ['IT', 'AI', '소프트웨어']
    },
    '코인': {
        'name': '암호화폐',
        'stocks': [],
        'keywords': ['비트코인', '이더리움', '암호화폐']
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

        result = f"""📈 **{sector['name']} 섹터 분석**

🏢 **주도 종목:**"""

        if sector['stocks']:
            for stock in sector['stocks']:
                result += f"\n• {stock}"
        else:
            result += "\n• 암호화폐 시장 전반"

        # 섹터 뉴스 조회
        result += f"\n\n📰 **최신 뉴스:**\n"

        news_found = False
        for keyword in sector['keywords']:
            news_list = search_news(keyword)
            if news_list:
                for i, news in enumerate(news_list[:2], 1):
                    result += f"\n{i}. {news['title']}"
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
    result = "📊 **사용 가능한 섹터:**\n\n"
    for key in SECTORS.keys():
        result += f"• {key}\n"
    return result
