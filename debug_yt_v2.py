import sys
import youtube_transcript_api
from youtube_transcript_api import YouTubeTranscriptApi

print(f"Module: {youtube_transcript_api}")
print(f"Module dir: {dir(youtube_transcript_api)}")
print(f"Class: {YouTubeTranscriptApi}")
print(f"Class type: {type(YouTubeTranscriptApi)}")
print(f"Class dir: {dir(YouTubeTranscriptApi)}")

try:
    print("Trying get_transcript...")
    # This is the old/simple way
    res = YouTubeTranscriptApi.get_transcript("G_RQZPt10eI")
    print(f"get_transcript result length: {len(res)}")
except Exception as e:
    print(f"get_transcript failed: {e}")
