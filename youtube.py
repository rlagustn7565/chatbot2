import re
import os
from typing import Optional
import urllib3
from anthropic import Anthropic
from yt_dlp import YoutubeDL

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')

# 강화된 프록시 리스트
PROXIES = [
    'http://45.142.212.109:8080',
    'http://34.159.224.249:3128',
    'http://35.239.31.112:3128',
    'http://190.92.153.37:3128',
    'http://35.198.154.165:3128',
    'socks5://127.0.0.1:1080',
]


def extract_video_id(url: str) -> Optional[str]:
    """유튜브 URL에서 video ID 추출"""
    try:
        match = re.search(r'(?:youtu\.be\/|youtube\.com\/watch\?v=)([^&\n?#]+)', url)
        if match:
            return match.group(1)
        return None
    except:
        return None


def get_youtube_transcript(url: str) -> Optional[str]:
    """yt-dlp로 자막 추출 (프록시 지원)"""
    video_id = extract_video_id(url)
    if not video_id:
        print("❌ 유효한 유튜브 URL이 아닙니다.")
        return None

    print(f"🎥 Video ID: {video_id}")
    print("📝 자막을 가져오는 중...")

    # 프록시 없이 먼저 시도
    transcript = _try_fetch_with_proxy(url, None)
    if transcript:
        return transcript
    
    # 프록시로 재시도
    print("🔄 프록시를 사용하여 재시도 중...")
    for i, proxy in enumerate(PROXIES, 1):
        print(f"   프록시 {i}/{len(PROXIES)} 시도 중...")
        transcript = _try_fetch_with_proxy(url, proxy)
        if transcript:
            return transcript
    
    print("❌ 모든 방법으로도 자막을 가져올 수 없습니다.")
    return None


def _try_fetch_with_proxy(url: str, proxy: Optional[str] = None) -> Optional[str]:
    """프록시를 사용하여 자막 가져오기 시도"""
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'writesubtitles': True,
            'skip_unavailable_fragments': True,
            'socket_timeout': 30,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            },
            'extractor_args': {'youtube': {'skip': ['hls', 'dash']}},
        }

        if proxy:
            ydl_opts['proxy'] = proxy

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # 한국어 자막 찾기
            if 'subtitles' in info:
                if 'ko' in info['subtitles']:
                    subs = info['subtitles']['ko']
                    return '\n'.join([s['text'] for s in subs])
                
                # 영어 자막
                if 'en' in info['subtitles']:
                    subs = info['subtitles']['en']
                    return '\n'.join([s['text'] for s in subs])
            
            # 자동 생성 자막
            if 'automatic_captions' in info:
                for lang in ['ko', 'en']:
                    if lang in info['automatic_captions']:
                        subs = info['automatic_captions'][lang]
                        return '\n'.join([s['text'] for s in subs])
        
        return None

    except Exception as e:
        return None


def summarize_transcript(transcript_text: str) -> Optional[str]:
    """Claude로 자막 요약"""
    if not CLAUDE_API_KEY:
        return None

    try:
        print("🤖 Claude AI로 요약 중...")

        client = Anthropic(api_key=CLAUDE_API_KEY)

        prompt = f"""다음 유튜브 영상의 자막을 간결하게 요약해줘.

요약 규칙:
- 한국어로 작성
- 핵심 내용만 간결하게
- 3-5개의 주요 포인트
- bullet point 형식으로 정리

자막:
{transcript_text[:3000]}

요약:"""

        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )

        summary = message.content[0].text
        print("✅ 요약 완료!")
        return summary

    except Exception as e:
        print(f"❌ 요약 중 오류: {e}")
        return None


def get_youtube_summary(url: str) -> Optional[str]:
    """유튜브 영상 요약"""
    print("=" * 60)
    print("📺 유튜브 영상 요약 시작")
    print("=" * 60 + "\n")

    transcript = get_youtube_transcript(url)

    if not transcript:
        return "❌ 자막을 가져올 수 없습니다."

    summary = summarize_transcript(transcript)

    if not summary:
        return "❌ 요약을 생성할 수 없습니다."

    return summary


if __name__ == "__main__":
    test_urls = ["https://www.youtube.com/watch?v=jNQXAC9IVRw"]

    for i, url in enumerate(test_urls, 1):
        print(f"\n[테스트 {i}]")
        print(f"URL: {url}")
        print("-" * 60)

        summary = get_youtube_summary(url)

        if summary:
            print("📄 요약 결과:")
            print(summary)
        else:
            print("요약을 가져올 수 없습니다.")

        print("\n" + "=" * 60)
