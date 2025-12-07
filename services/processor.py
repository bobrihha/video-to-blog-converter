import os
import re
from typing import Optional, Tuple

from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
import google.generativeai as genai
import markdown

# Load environment variables once
load_dotenv()


def extract_video_id(url: str) -> Optional[str]:
    """
    Extracts the video ID from a YouTube URL.
    Supports standard youtube.com and short youtu.be links.
    """
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None


def _ensure_output_dir(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)


def get_transcript(video_id: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Fetches the transcript for a given video ID.
    Returns transcript text and language code (if available).
    """
    try:
        # Adaptation for different library versions
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        except AttributeError:
            if hasattr(YouTubeTranscriptApi, "list"):
                try:
                    transcript_list = YouTubeTranscriptApi.list(video_id)
                except Exception:
                    api = YouTubeTranscriptApi()
                    transcript_list = api.list(video_id)
            else:
                api = YouTubeTranscriptApi()
                transcript_list = api.list(video_id)

        # Try to fetch manual transcripts first (priority: Russian, English)
        try:
            transcript = transcript_list.find_manually_created_transcript(["ru", "en"])
        except Exception:
            # Fallback to auto-generated
            try:
                transcript = transcript_list.find_generated_transcript(["ru", "en"])
            except Exception:
                transcript = next(iter(transcript_list))

        fetched_transcript = transcript.fetch()

        # Support dict entries as well as objects with a .text attribute (library version differences)
        def _entry_text(entry):
            if isinstance(entry, dict):
                return entry.get("text", "")
            return getattr(entry, "text", "")

        full_text = " ".join(
            [txt for txt in (_entry_text(entry) for entry in fetched_transcript) if txt]
        )

        language_code = getattr(transcript, "language_code", None) or getattr(
            transcript, "language", None
        )

        return full_text, language_code

    except Exception as e:
        print(f"Error fetching transcript: {e}")
        return None, None


def generate_article(transcript_text: str, tone: str = "formal", language: Optional[str] = None) -> Optional[str]:
    """
    Sends the transcript to Gemini API to generate an SEO article.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        print("Error: GEMINI_API_KEY not found in .env file.")
        return None

    genai.configure(api_key=api_key)

    prompt = f"""
    You are a professional blog editor and SEO specialist. Your task is to turn the following video transcript into an engaging, structured blog article.
    
    Tone: {tone}
    
    Write the article in the transcript's original language: {language or "use transcript language"}
    
    Requirements:
    1. Create a clickbait H1 title.
    2. Write an engaging introduction.
    3. Break the content into logical chapters (H2, H3).
    4. Highlight key points in bulleted lists.
    5. Write a conclusion.
    6. Output format: Markdown.
    
    Transcript:
    {transcript_text}
    """

    model_candidates = [
        "models/gemini-2.5-flash",
        "models/gemini-flash-latest",
        "models/gemini-2.0-flash",
        "models/gemini-pro-latest",
        "gemini-1.5-flash",
        "gemini-pro",
    ]
    last_error = None

    for model_name in model_candidates:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            last_error = e
            print(f"Error generating content with {model_name}: {e}")

    print(f"Error generating content with Gemini: {last_error}")
    return None


def _render_html(markdown_text: str, language: Optional[str]) -> str:
    """Wrap markdown HTML in a mobile-friendly template with UTF-8 and viewport."""
    body_html = markdown.markdown(markdown_text)
    lang_attr = f' lang="{language}"' if language else ""
    return f"""<!doctype html>
<html{lang_attr}>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Article</title>
  <style>
    :root {{
      color-scheme: light;
    }}
    * {{
      box-sizing: border-box;
    }}
    body {{
      margin: 0;
      padding: 0;
      background: #f7f7fb;
      color: #0f172a;
      font-family: "Inter", "Segoe UI", system-ui, -apple-system, sans-serif;
      line-height: 1.7;
    }}
    .page {{
      max-width: 820px;
      width: min(92vw, 820px);
      margin: 0 auto;
      padding: 28px 18px 48px;
      background: #fff;
      box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
      border-radius: 14px;
    }}
    h1, h2, h3 {{
      line-height: 1.3;
      margin: 0 0 12px;
      color: #0b1021;
    }}
    h1 {{ font-size: clamp(24px, 4vw, 32px); }}
    h2 {{ font-size: clamp(20px, 3.2vw, 26px); }}
    h3 {{ font-size: clamp(18px, 2.8vw, 22px); }}
    p {{ margin: 0 0 14px; }}
    ul, ol {{
      padding-left: 22px;
      margin: 0 0 16px;
    }}
    li {{ margin: 6px 0; }}
    a {{ color: #2563eb; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    img, video, iframe {{
      max-width: 100%;
      height: auto;
      display: block;
      margin: 12px 0;
    }}
    code {{
      background: #f3f4f6;
      padding: 2px 5px;
      border-radius: 4px;
      font-size: 0.95em;
    }}
    pre {{
      background: #0f172a;
      color: #e2e8f0;
      padding: 14px;
      border-radius: 8px;
      overflow-x: auto;
    }}
  </style>
</head>
<body>
  <div class="page">
    {body_html}
  </div>
</body>
</html>
"""


def save_article(markdown_text: str, video_id: str, tone: str, language: Optional[str]) -> Tuple[str, str]:
    """
    Saves the generated article to Markdown and HTML files.
    Returns paths to markdown and html files.
    """
    safe_tone = re.sub(r"[^a-zA-Z0-9_-]+", "_", tone.strip().lower() or "formal")
    md_filename = f"output/Article_{video_id}_{safe_tone}.md"
    html_filename = f"output/Article_{video_id}_{safe_tone}.html"

    _ensure_output_dir(md_filename)

    try:
        with open(md_filename, "w", encoding="utf-8") as f:
            f.write(markdown_text)

        html_content = _render_html(markdown_text, language)
        with open(html_filename, "w", encoding="utf-8") as f:
            f.write(html_content)

        return md_filename, html_filename
    except Exception as e:
        print(f"Error saving files: {e}")
        raise


def process_video(url: str, tone: str = "formal"):
    """
    Full pipeline: extract video ID, fetch transcript, generate article, save files.
    Returns dict with paths and flags.
    """
    video_id = extract_video_id(url)
    if not video_id:
        raise ValueError("Invalid YouTube URL.")

    safe_tone = re.sub(r"[^a-zA-Z0-9_-]+", "_", tone.strip().lower() or "formal")
    md_cache = f"output/Article_{video_id}_{safe_tone}.md"
    html_cache = f"output/Article_{video_id}_{safe_tone}.html"

    if os.path.exists(md_cache):
        # Ensure HTML exists; if not, regenerate from markdown cache.
        if not os.path.exists(html_cache):
            with open(md_cache, "r", encoding="utf-8") as f:
                html_content = _render_html(f.read(), None)
            _ensure_output_dir(html_cache)
            with open(html_cache, "w", encoding="utf-8") as f:
                f.write(html_content)

        return {
            "video_id": video_id,
            "tone": tone,
            "markdown_path": md_cache,
            "html_path": html_cache,
            "cached": True,
        }

    transcript, language = get_transcript(video_id)
    if not transcript:
        raise RuntimeError("Could not retrieve transcript.")

    article = generate_article(transcript, tone, language)
    if not article:
        raise RuntimeError("Failed to generate article.")

    md_path, html_path = save_article(article, video_id, tone, language)

    return {
        "video_id": video_id,
        "tone": tone,
        "markdown_path": md_path,
        "html_path": html_path,
        "cached": False,
    }
