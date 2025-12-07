import os
import youtube_transcript_api

init_file = youtube_transcript_api.__file__
package_dir = os.path.dirname(init_file)
api_file = os.path.join(package_dir, '_api.py')

print(f"Reading {api_file}...")
try:
    with open(api_file, 'r') as f:
        content = f.read()
        print("--- START OF FILE ---")
        print(content[:2000]) # First 2000 chars
        print("--- END OF SNIPPET ---")
except Exception as e:
    print(f"Error reading file: {e}")
