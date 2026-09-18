import re
import os
from typing import Optional
from anthropic import Anthropic

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    TRANSCRIPT_API_AVAILABLE = True
except ImportError:
    TRANSCRIPT_API_AVAILABLE = False

CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')


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
    """youtube-transcript-api를 사용한 자막 추출"""
    if not TRANSCRIPT_API_AVAILABLE:
        return None

    video_id = extract_video_id(url)
    if not video_id:
        print("❌ 유효한 유튜브 URL이 아닙니다.")
        return None

    print(f"🎥 Video ID: {video_id}")
    print("📝 자막을 가져오는 중...")

    try:
        # 한국어 자막 시도
        try:
            transcripts = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko'])
            print("✅ 한국어 자막 찾음!")
            return '\n'.join([t['text'] for t in transcripts])
        except:
            pass

        # 영어 자막 시도
        try:
            transcripts = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
            print("✅ 영어 자막 찾음!")
            return '\n'.join([t['text'] for t in transcripts])
        except:
            pass

        # 자동생성 자막 시도
        try:
            transcripts = YouTubeTranscriptApi.get_transcript(video_id)
            print("✅ 자막 찾음!")
            return '\n'.join([t['text'] for t in transcripts])
        except:
            pass

        print("❌ 자막을 찾을 수 없습니다.")
        return None

    except Exception as e:
        print(f"   오류: {type(e).__name__}")
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

    if not TRANSCRIPT_API_AVAILABLE:
        return "❌ YouTube 기능이 준비되지 않았습니다."

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
