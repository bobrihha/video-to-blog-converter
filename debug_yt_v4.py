from youtube_transcript_api import YouTubeTranscriptApi

print("Inspecting fetch() structure...")
try:
    # INSTANTIATE first
    api = YouTubeTranscriptApi()
    transcript_list = api.list("G_RQZPt10eI")
    
    t = next(iter(transcript_list))
    fetched = t.fetch()
    
    if len(fetched) > 0:
        first_item = fetched[0]
        print(f"First item type: {type(first_item)}")
        print(f"First item dir: {dir(first_item)}")
        
except Exception as e:
    print(f"Debug failed: {e}")
