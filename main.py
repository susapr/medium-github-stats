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

def get_articles():
    """
    Parse the Medium RSS feed and return up to three articles.
    For each article, extract:
      - title: from entry.title.
      - subtitle: either the first <blockquote> text found in entry.content,
                  or, if not available, the first 10 words of the first <p>.
      - link: the article URL.
      - image: the featured image (if available).
    """
    feed = feedparser.parse(MEDIUM_RSS_URL)
    articles = []
    for entry in feed.entries[:3]:
        title = entry.title
        link = entry.link

        # Attempt to generate a subtitle.
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
        # Fallback to summary (trimmed to 10 words) if no subtitle was generated.
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
    Render an SVG with a dark-themed card for each of the three most recent Medium articles.
    
    Each card includes:
      - A clickable area (wrapped in an <a>) that directs to the article.
      - On the left: a text container (using a foreignObject) displaying the article title (bold, white)
        and subtitle (smaller, gray) in GitHub’s system font.
      - On the right: the featured image (if available), shown with rounded corners and some right padding.
    """
    articles = get_articles()
    width = 600
    card_height = 160
    gap = 20
    height = (card_height + gap) * len(articles) + gap if articles else gap

    svg_parts = []
    # Begin SVG document.
    svg_parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">')
    svg_parts.append("<style>")
    # Use a GitHub dark theme background for the card.
    svg_parts.append(".card { fill: #0d1117; stroke: #444; stroke-width: 1; }")
    svg_parts.append(".clickable { cursor: pointer; }")
    svg_parts.append("</style>")

    y_offset = gap
    for i, article in enumerate(articles):
        svg_parts.append(f'<a href="{article["link"]}" target="_blank">')
        # Draw the card background with rounded corners.
        svg_parts.append(f'<rect class="card clickable" x="20" y="{y_offset}" width="{width - 40}" height="{card_height}" rx="10" ry="10"/>')
        # Left-hand text container using foreignObject. We set the font-family to mimic GitHub's.
        svg_parts.append(f'''<foreignObject x="30" y="{y_offset + 10}" width="370" height="{card_height - 20}">
  <body xmlns="http://www.w3.org/1999/xhtml" style="margin:0; padding:0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;">
    <div style="color:#fff; font-size:18px; font-weight:bold; line-height:1.2;">{article["title"]}</div>
    <div style="color:#ccc; font-size:14px; margin-top:5px;">{article["subtitle"]}</div>
  </body>
</foreignObject>''')
        # Right-hand: display the featured image (if available) with rounded corners and right padding.
        if article["image"]:
            # Set image parameters.
            img_x = 420
            img_width = 150  # This gives a little right-side padding within the card.
            clip_id = f"clipImage{i}"
            # Define a clipPath for rounded image corners.
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
