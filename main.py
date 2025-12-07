from services.processor import process_video

def main():
    print("Welcome to the AI YouTube-to-SEO Converter!")
    print("-" * 50)
    
    url = input("Insert YouTube video link: ").strip()
    
    tone_input = input("Enter desired tone (formal/friendly/sales) [default: formal]: ").strip()
    tone = tone_input if tone_input else "formal"
    
    print("Processing video and generating article... (this may take a few seconds)")
    try:
        result = process_video(url, tone)
    except Exception as e:
        print(f"Failed: {e}")
        return

    if result.get("cached"):
        print("Found cached article. Skipped regeneration.")

    print("Success!")
    print(f"Markdown file: {result['markdown_path']}")
    print(f"HTML file: {result['html_path']}")

if __name__ == "__main__":
    main()
