import sys
if sys.platform == "win32":
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI, Response
import feedparser
from bs4 import BeautifulSoup

app = FastAPI()

# Replace with your actual Medium feed URL (e.g., "https://medium.com/feed/@your_username")
MEDIUM_RSS_URL = "https://medium.com/feed/@susapr"

def wrap_text(text, max_chars):
    """
    A simple text-wrapping function that breaks a string into multiple lines,
    with each line having up to `max_chars` characters.
    """
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        # Add a space only if current_line is not empty.
        if len(current_line) + len(word) + (1 if current_line else 0) <= max_chars:
            current_line = f"{current_line} {word}" if current_line else word
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines

def get_articles():
    """
    Parse the Medium RSS feed and return up to three articles.
    For each article, extract:
      - title: from entry.title.
      - subtitle: either the text of the first <blockquote> if found,
                  or, if not available, the first 10 words of the first <p> (ending with '...').
      - link: the article URL.
      - image: the featured image (if available).
    """
    feed = feedparser.parse(MEDIUM_RSS_URL)
    articles = []
    for entry in feed.entries[:3]:
        title = entry.title
        link = entry.link

        # Generate a subtitle.
        subtitle = ""
        if hasattr(entry, "content"):
            content_html = entry.content[0].value
            soup = BeautifulSoup(content_html, "html.parser")
            blockquote = soup.find("blockquote")
            if blockquote:
                subtitle = blockquote.get_text(strip=True)
            else:
                p = soup.find("p")
                if p:
                    words = p.get_text(strip=True).split()
                    if len(words) > 10:
                        subtitle = " ".join(words[:10]) + "..."
                    else:
                        subtitle = p.get_text(strip=True)
        # Fallback to summary (trimmed) if nothing else was found.
        if not subtitle and hasattr(entry, "summary"):
            words = entry.summary.strip().split()
            if len(words) > 10:
                subtitle = " ".join(words[:10]) + "..."
            else:
                subtitle = entry.summary.strip()

        # Extract image URL.
        image = None
        if "media_content" in entry:
            image = entry.media_content[0]["url"]
        elif hasattr(entry, "content"):
            soup = BeautifulSoup(entry.content[0].value, "html.parser")
            img_tag = soup.find("img")
            if img_tag and img_tag.get("src"):
                image = img_tag.get("src")

        articles.append({
            "title": title,
            "subtitle": subtitle,
            "link": link,
            "image": image
        })
    return articles

@app.get("/card")
def card():
    """
    Render an SVG containing a dark-themed card for each of the three most recent Medium articles.
    Each card includes:
      - A clickable area (<a>) linking to the article.
      - On the left: the title (bold, white) and subtitle (smaller, gray), rendered using SVG <text> elements.
      - On the right: the featured image (if available) with rounded corners and right padding.
    """
    articles = get_articles()
    width = 600
    card_height = 160
    gap = 20
    total_height = (card_height + gap) * len(articles) + gap if articles else gap

    svg_parts = []
    svg_parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{total_height}" viewBox="0 0 {width} {total_height}">')
    svg_parts.append("<style>")
    svg_parts.append(".card { fill: #0d1117; stroke: #444; stroke-width: 1; }")
    svg_parts.append(".clickable { cursor: pointer; }")
    svg_parts.append("</style>")
    
    y_offset = gap
    for i, article in enumerate(articles):
        svg_parts.append(f'<a href="{article["link"]}" target="_blank">')
        # Card background.
        svg_parts.append(f'<rect class="card clickable" x="20" y="{y_offset}" width="{width - 40}" height="{card_height}" rx="10" ry="10"/>')
        
        # Prepare wrapped title and subtitle.
        title_lines = wrap_text(article["title"], 40)  # Adjust max_chars as needed.
        subtitle_lines = wrap_text(article["subtitle"], 50)  # Adjust max_chars as needed.
        
        # Render the title using <text> and <tspan>.
        text_x = 30
        text_start_y = y_offset + 30  # Starting y for the title.
        svg_parts.append(f'<text x="{text_x}" y="{text_start_y}" fill="#fff" font-size="18" font-family="-apple-system, BlinkMacSystemFont, \'Segoe UI\', Helvetica, Arial, sans-serif" font-weight="bold">')
        for j, line in enumerate(title_lines):
            # For the first line, dy is 0; for subsequent lines, use dy="1.2em".
            dy = "0" if j == 0 else "1.2em"
            svg_parts.append(f'<tspan x="{text_x}" dy="{dy}">{line}</tspan>')
        svg_parts.append('</text>')
        
        # Render the subtitle below the title.
        # Calculate y position: base it on the number of title lines.
        subtitle_y = text_start_y + (len(title_lines) * 1.2 * 18) + 5  # 18 is the title font size.
        svg_parts.append(f'<text x="{text_x}" y="{subtitle_y}" fill="#ccc" font-size="14" font-family="-apple-system, BlinkMacSystemFont, \'Segoe UI\', Helvetica, Arial, sans-serif">')
        for j, line in enumerate(subtitle_lines):
            dy = "0" if j == 0 else "1.2em"
            svg_parts.append(f'<tspan x="{text_x}" dy="{dy}">{line}</tspan>')
        svg_parts.append('</text>')
        
        # Display the featured image on the right, if available.
        if article["image"]:
            img_x = 420
            img_width = 150  # Leaves some padding on the right.
            clip_id = f"clipImage{i}"
            svg_parts.append(f'''<clipPath id="{clip_id}">
  <rect x="{img_x}" y="{y_offset + 10}" width="{img_width}" height="{card_height - 20}" rx="10" ry="10" />
</clipPath>''')
            svg_parts.append(f'<image href="{article["image"]}" x="{img_x}" y="{y_offset + 10}" width="{img_width}" height="{card_height - 20}" preserveAspectRatio="xMidYMid slice" clip-path="url(#{clip_id})" />')
        svg_parts.append("</a>")
        y_offset += card_height + gap

    svg_parts.append("</svg>")
    svg_content = "\n".join(svg_parts)
    return Response(content=svg_content, media_type="image/svg+xml")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
