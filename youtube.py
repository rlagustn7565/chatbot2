import re
import os
from typing import Optional
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound
import requests
import urllib3
from google import genai

# SSL 검증 비활성화 (네트워크 보안 정책으로 인한 필요)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
os.environ['REQUESTS_CA_BUNDLE'] = ''
os.environ['CURL_CA_BUNDLE'] = ''

# Gemini API 설정
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')


def extract_video_id(url: str) -> Optional[str]:
    """
    다양한 형태의 유튜브 URL에서 video_id를 추출

    지원하는 URL 형식:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - http://youtube.com/watch?v=VIDEO_ID
    - http://youtu.be/VIDEO_ID

    Args:
        url: 유튜브 URL

    Returns:
        video_id 또는 None (추출 실패 시)
    """
    try:
        # youtu.be/VIDEO_ID 형식
        match = re.search(r'(?:youtu\.be\/|youtube\.com\/watch\?v=)([^&\n?#]+)', url)
        if match:
            return match.group(1)

        # 기타 형식들을 처리하기 위한 추가 정규식
        match = re.search(r'(?:youtube\.com\/.*[?&]v=|youtu\.be\/)([^&\n?#]+)', url)
        if match:
            return match.group(1)

        return None
    except Exception as e:
        print(f"⚠️ Video ID 추출 중 오류: {e}")
        return None


def get_youtube_transcript(url: str) -> Optional[str]:
    """
    유튜브 URL에서 자막을 추출해 하나의 문자열로 반환

    우선순위:
    1. 한국어 자막 (수동)
    2. 한국어 자동 생성 자막
    3. 영어 자막
    4. 첫 번째 사용 가능한 자막

    Args:
        url: 유튜브 URL

    Returns:
        자막 텍스트 (하나의 문자열) 또는 None (추출 실패 시)
    """
    try:
        # Video ID 추출
        video_id = extract_video_id(url)
        if not video_id:
            print("❌ 유효한 유튜브 URL이 아닙니다.")
            return None

        print(f"🎥 Video ID: {video_id}")
        print("📝 자막을 가져오는 중...")

        # SSL 검증을 비활성화한 custom HTTP client 생성
        http_client = requests.Session()
        http_client.verify = False

        client = YouTubeTranscriptApi(http_client=http_client)
        transcript_list = None
        language_used = None

        try:
            # 한국어 자막 시도
            try:
                transcript_list = client.fetch(video_id, languages=['ko'])
                language_used = "한국어"
            except NoTranscriptFound:
                pass

            # 영어 자막 시도
            if not transcript_list:
                try:
                    transcript_list = client.fetch(video_id, languages=['en'])
                    language_used = "영어"
                except NoTranscriptFound:
                    pass

            # 사용 가능한 첫 번째 자막
            if not transcript_list:
                transcript_list = client.fetch(video_id)
                language_used = "사용 가능한 첫 번째"

            if transcript_list:
                print(f"✅ {language_used} 자막을 찾았습니다.")

        except TranscriptsDisabled:
            print("❌ 이 영상은 자막이 비활성화되어 있습니다.")
            return None

        # 자막 텍스트를 하나의 문자열로 결합
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
    """
    Gemini API를 사용해 유튜브 자막을 요약

    Args:
        transcript_text: 자막 텍스트
        max_length: 요약의 최대 길이 (단어 기준)

    Returns:
        요약 텍스트 또는 None (오류 시)
    """
    if not GEMINI_API_KEY:
        print("❌ Gemini API 키가 설정되지 않았습니다.")
        print("   GEMINI_API_KEY 환경 변수를 설정해주세요.")
        return None

    try:
        print("🤖 Gemini AI로 요약 중...")

        client = genai.Client(api_key=GEMINI_API_KEY)

        prompt = f"""다음 유튜브 영상의 자막을 간결하게 요약해줘.

요약 규칙:
- 한국어로 작성
- 핵심 내용만 간결하게
- 3-5개의 주요 포인트
- 총 {max_length}자 이내
- bullet point 형식으로 정리

자막:
{transcript_text}

요약:"""

        interaction = client.interactions.create(
            model="gemini-3.6-flash",
            input=prompt
        )

        summary = interaction.output_text

        print("✅ 요약 완료!\n")
        return summary

    except Exception as e:
        print(f"❌ 요약 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return None


def get_youtube_summary(url: str) -> Optional[str]:
    """
    유튜브 URL에서 자막을 추출하고 Gemini로 요약

    Args:
        url: 유튜브 URL

    Returns:
        요약 텍스트 또는 None (오류 시)
    """
    print("=" * 60)
    print("📺 유튜브 영상 요약 시작")
    print("=" * 60 + "\n")

    # 자막 추출
    transcript = get_youtube_transcript(url)

    if not transcript:
        print("❌ 자막을 가져올 수 없습니다.")
        return None

    # 요약
    summary = summarize_transcript(transcript)

    if not summary:
        print("❌ 요약을 생성할 수 없습니다.")
        return None

    return summary


if __name__ == "__main__":
    # 테스트용 유튜브 URL들
    test_urls = [
        # 테스트 1: 일반적인 유튜브 URL (자막이 있는 영상)
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
