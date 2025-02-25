import sys
if sys.platform == "win32":
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI, Response
import feedparser
from bs4 import BeautifulSoup
import datetime

app = FastAPI()

# Replace with your actual Medium feed URL (e.g., "https://medium.com/feed/@your_username")
MEDIUM_RSS_URL = "https://medium.com/feed/@susapr"

def wrap_text(text, max_chars):
    """
    A simple text-wrapping function that breaks a string into multiple lines,
    ensuring each line has up to `max_chars` characters.
    """
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
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
      - published: the publication date from <pubDate> formatted as "Month Day, Year".
    """
    feed = feedparser.parse(MEDIUM_RSS_URL)
    articles = []
    for entry in feed.entries[:3]:
        title = entry.title
        link = entry.link

        # Generate a subtitle from the content.
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
        if not subtitle and hasattr(entry, "summary"):
            words = entry.summary.strip().split()
            if len(words) > 10:
                subtitle = " ".join(words[:10]) + "..."
            else:
                subtitle = entry.summary.strip()

        # Extract and format the publication date.
        published = ""
        if hasattr(entry, "published_parsed"):
            dt = datetime.datetime(*entry.published_parsed[:6])
            published = dt.strftime("%B %d, %Y").replace(" 0", " ")

        articles.append({
            "title": title,
            "subtitle": subtitle,
            "link": link,
            "published": published
        })
    return articles

@app.get("/card")
def card():
    """
    Render an SVG with a dark-themed card for each of the three most recent Medium articles.
    Each card includes:
      - A clickable area (<a>) linking to the article.
      - The article title (bold, white) and subtitle (smaller, gray) rendered using SVG <text> and <tspan> elements.
      - The publication date at the bottom left in italics (e.g., "Published: February 4, 2025").
    Since there’s no image or button, the text spans nearly the full width of the card.
    """
    articles = get_articles()
    width = 600
    card_height = 120  # Smaller card height since only text is displayed.
    gap = 20
    total_height = (card_height + gap) * len(articles) + gap if articles else gap

    svg_parts = []
    svg_parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{total_height}" viewBox="0 0 {width} {total_height}">')
    svg_parts.append("<style>")
    # Card background using a GitHub dark theme color.
    svg_parts.append(".card { fill: #0d1117; stroke: #444; stroke-width: 1; }")
    svg_parts.append(".clickable { cursor: pointer; }")
    svg_parts.append("</style>")
    
    y_offset = gap
    for article in articles:
        svg_parts.append(f'<a href="{article["link"]}" target="_blank">')
        # Draw the card background.
        svg_parts.append(f'<rect class="card clickable" x="20" y="{y_offset}" width="{width - 40}" height="{card_height}" rx="10" ry="10"/>')
        
        text_x = 30  # Left inset for text.
        text_start_y = y_offset + 30  # Starting y-coordinate for title text.
        
        # Render the title.
        title_lines = wrap_text(article["title"], 80)
        svg_parts.append(f'<text x="{text_x}" y="{text_start_y}" fill="#fff" font-size="18" font-family="-apple-system, BlinkMacSystemFont, \'Segoe UI\', Helvetica, Arial, sans-serif" font-weight="bold">')
        for j, line in enumerate(title_lines):
            dy = "0" if j == 0 else "1.2em"
            svg_parts.append(f'<tspan x="{text_x}" dy="{dy}">{line}</tspan>')
        svg_parts.append('</text>')
        
        # Render the subtitle.
        subtitle_lines = wrap_text(article["subtitle"], 100)
        subtitle_y = text_start_y + (len(title_lines) * 1.2 * 18) + 5
        svg_parts.append(f'<text x="{text_x}" y="{subtitle_y}" fill="#ccc" font-size="14" font-family="-apple-system, BlinkMacSystemFont, \'Segoe UI\', Helvetica, Arial, sans-serif">')
        for j, line in enumerate(subtitle_lines):
            dy = "0" if j == 0 else "1.2em"
            svg_parts.append(f'<tspan x="{text_x}" dy="{dy}">{line}</tspan>')
        svg_parts.append('</text>')
        
        # Render the publication date at the bottom left in italics.
        published_y = y_offset + card_height - 10
        svg_parts.append(f'<text x="{text_x}" y="{published_y}" fill="#ccc" font-size="12" font-family="-apple-system, BlinkMacSystemFont, \'Segoe UI\', Helvetica, Arial, sans-serif" font-style="italic">')
        svg_parts.append(f'<tspan x="{text_x}">Published: {article["published"]}</tspan>')
        svg_parts.append('</text>')
        
        svg_parts.append("</a>")
        y_offset += card_height + gap

    svg_parts.append("</svg>")
    svg_content = "\n".join(svg_parts)
    return Response(content=svg_content, media_type="image/svg+xml")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
