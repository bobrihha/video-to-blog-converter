import sys
import youtube_transcript_api
from youtube_transcript_api import YouTubeTranscriptApi

print(f"Python executable: {sys.executable}")
print(f"Library location: {youtube_transcript_api.__file__}")
print(f"Library version: {youtube_transcript_api.__version__ if hasattr(youtube_transcript_api, '__version__') else 'unknown'}")
print("Attributes of YouTubeTranscriptApi:")
print(dir(YouTubeTranscriptApi))

try:
    YouTubeTranscriptApi.list_transcripts("G_RQZPt10eI")
    print("\nlist_transcripts worked!")
except AttributeError as e:
    print(f"\nError: {e}")
except Exception as e:
    print(f"\nOther Error: {e}")
