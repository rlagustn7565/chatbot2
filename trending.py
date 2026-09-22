import FinanceDataReader as fdr
from datetime import datetime, timedelta
import pandas as pd
from typing import List, Dict, Optional
from sector import SECTORS

def get_trending_stocks(limit: int = 10) -> Optional[str]:
    """급등/급락 종목 분석 - KRX 전체 대상"""
    try:
        print("📈 특징주 분석 중... (거래량 기반)")

        today = pd.Timestamp.today()
        yesterday = today - timedelta(days=1)
        two_days_ago = today - timedelta(days=2)

        # KRX 모든 종목 조회
        stock_list = fdr.StockListing('KRX')
        print(f"   총 {len(stock_list)}개 종목 분석 중...")

        trending_up = []
        trending_down = []

        # 각 종목 분석 (시간 최적화: 거래량이 많은 상위 500개만 우선)
        for idx, row in stock_list.head(500).iterrows():
            try:
                code = row['Code']
                name = row['Name']

                # 최근 2일 데이터만 조회 (빠름)
                df = fdr.DataReader(code, start=two_days_ago)

                if len(df) < 2:
                    continue

                # 최근 데이터
                latest = df.iloc[-1]
                prev = df.iloc[-2] if len(df) >= 2 else df.iloc[0]

                current_price = float(latest['Close'])
                prev_price = float(prev['Close'])
                current_volume = int(latest.get('Volume', 0))
                prev_volume = int(prev.get('Volume', 0))

                # 수익률 계산
                change_rate = ((current_price - prev_price) / prev_price * 100) if prev_price > 0 else 0

                # 거래량 변화
                volume_change = ((current_volume - prev_volume) / prev_volume * 100) if prev_volume > 0 else 0

                # 급등: 상승 + 거래량 증가
                if change_rate > 3 and volume_change > 20:
                    trending_up.append({
                        'name': name,
                        'code': code,
                        'price': current_price,
                        'change_rate': change_rate,
                        'volume_change': volume_change
                    })

                # 급락: 하락 + 거래량 증가
                elif change_rate < -3 and volume_change > 20:
                    trending_down.append({
                        'name': name,
                        'code': code,
                        'price': current_price,
                        'change_rate': change_rate,
                        'volume_change': volume_change
                    })

            except Exception as e:
                continue

        # 정렬
        trending_up.sort(key=lambda x: x['change_rate'], reverse=True)
        trending_down.sort(key=lambda x: x['change_rate'])

        # 결과 생성
        result = """🚀 **특징주 분석**\n\n"""

        if trending_up:
            result += f"""📈 **급등주** (상승 + 거래량 증가)\n"""
            for i, stock in enumerate(trending_up[:limit], 1):
                result += f"{i}. {stock['name']} ({stock['price']:,.0f}원)\n"
                result += f"   변화: {stock['change_rate']:+.2f}% | 거래량: {stock['volume_change']:+.1f}%\n"
        else:
            result += "📈 **급등주**: 없음\n"

        result += "\n"

        if trending_down:
            result += f"""📉 **급락주** (하락 + 거래량 증가)\n"""
            for i, stock in enumerate(trending_down[:limit], 1):
                result += f"{i}. {stock['name']} ({stock['price']:,.0f}원)\n"
                result += f"   변화: {stock['change_rate']:+.2f}% | 거래량: {stock['volume_change']:+.1f}%\n"
        else:
            result += "📉 **급락주**: 없음\n"

        print(f"✅ 특징주 분석 완료! (급등: {len(trending_up)}, 급락: {len(trending_down)})")
        return result

    except Exception as e:
        print(f"❌ 특징주 분석 오류: {e}")
        import traceback
        traceback.print_exc()
        return None


def get_trending_sectors() -> Optional[str]:
    """급등/급락 섹터 분석"""
    try:
        print("📊 특징섹터 분석 중...")

        today = pd.Timestamp.today()
        two_days_ago = today - timedelta(days=2)

        sector_stats = {}

        # 각 섹터의 주도 종목 분석
        for sector_name, sector_info in SECTORS.items():
            up_count = 0
            down_count = 0
            avg_change = 0
            total_volume_change = 0
            analyzed = 0

            for stock_name in sector_info['stocks'][:3]:  # 주도 종목 3개만
                try:
                    stock_list = fdr.StockListing('KRX')
                    stock_row = stock_list[stock_list['Name'] == stock_name]

                    if stock_row.empty:
                        continue

                    code = stock_row.iloc[0]['Code']
                    df = fdr.DataReader(code, start=two_days_ago)

                    if len(df) < 2:
                        continue

                    latest = df.iloc[-1]
                    prev = df.iloc[-2]

                    current_price = float(latest['Close'])
                    prev_price = float(prev['Close'])
                    current_volume = int(latest.get('Volume', 0))
                    prev_volume = int(prev.get('Volume', 0))

                    change_rate = ((current_price - prev_price) / prev_price * 100) if prev_price > 0 else 0
                    volume_change = ((current_volume - prev_volume) / prev_volume * 100) if prev_volume > 0 else 0

                    avg_change += change_rate
                    total_volume_change += volume_change
                    analyzed += 1

                    if change_rate > 0:
                        up_count += 1
                    else:
                        down_count += 1

                except:
                    continue

            if analyzed > 0:
                sector_stats[sector_name] = {
                    'avg_change': avg_change / analyzed,
                    'up_count': up_count,
                    'down_count': down_count,
                    'volume_change': total_volume_change / analyzed
                }

        # 상승/하락 섹터 정렬
        trending_up_sectors = sorted(
            [(k, v) for k, v in sector_stats.items() if v['avg_change'] > 0],
            key=lambda x: x[1]['avg_change'],
            reverse=True
        )

        trending_down_sectors = sorted(
            [(k, v) for k, v in sector_stats.items() if v['avg_change'] < 0],
            key=lambda x: x[1]['avg_change']
        )

        # 결과 생성
        result = """📊 **특징섹터 분석**\n\n"""

        if trending_up_sectors:
            result += f"""📈 **상승 섹터**\n"""
            for i, (sector, stats) in enumerate(trending_up_sectors[:5], 1):
                result += f"{i}. {sector} ({stats['avg_change']:+.2f}%)\n"
                result += f"   주도주: {stats['up_count']}개 상승\n"

        result += "\n"

        if trending_down_sectors:
            result += f"""📉 **하락 섹터**\n"""
            for i, (sector, stats) in enumerate(trending_down_sectors[:5], 1):
                result += f"{i}. {sector} ({stats['avg_change']:+.2f}%)\n"
                result += f"   주도주: {stats['down_count']}개 하락\n"

        print(f"✅ 특징섹터 분석 완료!")
        return result

    except Exception as e:
        print(f"❌ 특징섹터 분석 오류: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    print("=" * 60)
    print("📈 특징주/섹터 분석 테스트")
    print("=" * 60)

    stocks = get_trending_stocks()
    if stocks:
        print(stocks)

    print("\n" + "=" * 60 + "\n")

    sectors = get_trending_sectors()
    if sectors:
        print(sectors)
