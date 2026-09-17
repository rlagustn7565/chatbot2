import re
import os
from typing import Optional
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, RequestBlocked
import requests
import urllib3
from anthropic import Anthropic
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
os.environ['REQUESTS_CA_BUNDLE'] = ''
os.environ['CURL_CA_BUNDLE'] = ''

CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')

# 프리 프록시 리스트 (백업용)
FREE_PROXIES = [
    "http://45.142.212.109:8080",
    "http://34.159.224.249:3128",
    "http://35.239.31.112:3128",
    "http://190.92.153.37:3128",
    "http://35.198.154.165:3128",
]


def extract_video_id(url: str) -> Optional[str]:
    try:
        match = re.search(r'(?:youtu\.be\/|youtube\.com\/watch\?v=)([^&\n?#]+)', url)
        if match:
            return match.group(1)

        match = re.search(r'(?:youtube\.com\/.*[?&]v=|youtu\.be\/)([^&\n?#]+)', url)
        if match:
            return match.group(1)

        return None
    except Exception as e:
        print(f"⚠️ Video ID 추출 중 오류: {e}")
        return None


def get_youtube_transcript(url: str) -> Optional[str]:
    video_id = extract_video_id(url)
    if not video_id:
        print("❌ 유효한 유튜브 URL이 아닙니다.")
        return None

    print(f"🎥 Video ID: {video_id}")
    print("📝 자막을 가져오는 중...")

    # 프록시 없이 먼저 시도
    transcript_list = _try_fetch_transcript(video_id, proxy=None)
    if transcript_list:
        return _format_transcript(transcript_list, "기본")

    # 프록시로 재시도
    print("🔄 프록시를 사용하여 재시도 중...")
    for i, proxy in enumerate(FREE_PROXIES, 1):
        print(f"   프록시 {i}/{len(FREE_PROXIES)} 시도 중...")
        time.sleep(1)

        transcript_list = _try_fetch_transcript(video_id, proxy=proxy)
        if transcript_list:
            return _format_transcript(transcript_list, f"프록시 {i}")

    print("❌ 모든 방법으로도 자막을 가져올 수 없습니다.")
    return None


def _try_fetch_transcript(video_id: str, proxy: Optional[str] = None) -> Optional[list]:
    """프록시를 사용하여 자막 가져오기 시도"""
    try:
        # Session 생성
        http_client = requests.Session()
        http_client.verify = False

        # 자연스러운 User-Agent
        http_client.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        # 프록시 설정
        if proxy:
            proxies = {'http': proxy, 'https': proxy}
            http_client.proxies.update(proxies)

        client = YouTubeTranscriptApi(http_client=http_client)
        transcript_list = None

        # 한국어 시도
        try:
            transcript_list = client.fetch(video_id, languages=['ko'])
            return transcript_list
        except (NoTranscriptFound, RequestBlocked):
            pass

        # 영어 시도
        try:
            transcript_list = client.fetch(video_id, languages=['en'])
            return transcript_list
        except (NoTranscriptFound, RequestBlocked):
            pass

        # 사용 가능한 자막 (자동 생성)
        try:
            transcript_list = client.fetch(video_id)
            return transcript_list
        except (NoTranscriptFound, RequestBlocked):
            pass

        return None

    except TranscriptsDisabled:
        print("   ⚠️ 이 영상은 자막이 비활성화되어 있습니다.")
        return None
    except Exception as e:
        return None


def _format_transcript(transcript_list: list, source: str) -> str:
    """자막을 포맷팅"""
    transcript_text = " ".join([item.text for item in transcript_list])
    print(f"✅ {source}으로 자막을 찾았습니다!")
    print(f"✅ 총 {len(transcript_list)}개의 자막 항목을 추출했습니다.")
    print(f"📊 총 {len(transcript_text)}자의 텍스트입니다.\n")
    return transcript_text


def summarize_transcript(transcript_text: str, max_length: int = 500) -> Optional[str]:
    if not CLAUDE_API_KEY:
        print("❌ Claude API 키가 설정되지 않았습니다.")
        return None

    try:
        print("🤖 Claude AI로 요약 중...")

        client = Anthropic(api_key=CLAUDE_API_KEY)

        prompt = f"""다음 유튜브 영상의 자막을 간결하게 요약해줘.

요약 규칙:
- 한국어로 작성
- 핵심 내용만 간결하게
- 3-5개의 주요 포인트
- 총 {max_length}자 이내
- bullet point 형식으로 정리

자막:
{transcript_text[:2000]}

요약:"""

        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=500,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        summary = message.content[0].text

        print("✅ 요약 완료!\n")
        return summary

    except Exception as e:
        print(f"❌ 요약 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return None


def get_youtube_summary(url: str) -> Optional[str]:
    print("=" * 60)
    print("📺 유튜브 영상 요약 시작")
    print("=" * 60 + "\n")

    transcript = get_youtube_transcript(url)

    if not transcript:
        print("❌ 자막을 가져올 수 없습니다.")
        return None

    summary = summarize_transcript(transcript)

    if not summary:
        print("❌ 요약을 생성할 수 없습니다.")
        return None

    return summary


if __name__ == "__main__":
    test_urls = [
        "https://www.youtube.com/watch?v=jNQXAC9IVRw",
    ]

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
