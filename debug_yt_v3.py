from youtube_transcript_api import YouTubeTranscriptApi

print("Trying updated method names...")
try:
    # Try instantiation if it's a class
    api = YouTubeTranscriptApi()
    
    # Check if 'list' method exists and works
    if hasattr(api, 'list'):
        print("Found 'list' method on instance.")
        # Attempt to call it (assuming it takes video_id)
        # We need a real video ID to test, or we catch the error
        try:
            transcripts = api.list("G_RQZPt10eI")
            print(f"api.list result: {transcripts}")
        except Exception as e:
            print(f"api.list call failed: {e}")
    else:
        print("No 'list' method on instance.")

except Exception as e:
    print(f"Instantiation failed: {e}")

# Check static too just in case
print("\nChecking static methods...")
if hasattr(YouTubeTranscriptApi, 'list'):
    print("Found 'list' as static method")
