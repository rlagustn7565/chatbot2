import re
import os
from typing import Optional
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
import requests
import urllib3
from anthropic import Anthropic

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
os.environ['REQUESTS_CA_BUNDLE'] = ''
os.environ['CURL_CA_BUNDLE'] = ''

CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')


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
    try:
        video_id = extract_video_id(url)
        if not video_id:
            print("❌ 유효한 유튜브 URL이 아닙니다.")
            return None

        print(f"🎥 Video ID: {video_id}")
        print("📝 자막을 가져오는 중...")

        http_client = requests.Session()
        http_client.verify = False

        client = YouTubeTranscriptApi(http_client=http_client)
        transcript_list = None
        language_used = None

        try:
            try:
                transcript_list = client.fetch(video_id, languages=['ko'])
                language_used = "한국어"
            except NoTranscriptFound:
                pass

            if not transcript_list:
                try:
                    transcript_list = client.fetch(video_id, languages=['en'])
                    language_used = "영어"
                except NoTranscriptFound:
                    pass

            if not transcript_list:
                transcript_list = client.fetch(video_id)
                language_used = "사용 가능한 첫 번째"

            if transcript_list:
                print(f"✅ {language_used} 자막을 찾았습니다.")

        except TranscriptsDisabled:
            print("❌ 이 영상은 자막이 비활성화되어 있습니다.")
            return None

        if transcript_list:
            transcript_text = " ".join([item.text for item in transcript_list])
            print(f"✅ 총 {len(transcript_list)}개의 자막 항목을 추출했습니다.")
            print(f"📊 총 {len(transcript_text)}자의 텍스트입니다.\n")
            return transcript_text

        return None

    except Exception as e:
        print(f"❌ 자막 추출 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return None


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
            model="claude-opus-5",
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
