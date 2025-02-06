# medium-github-stats
An embed webservice to display your latest Medium articles on your GitHub README.md

Created by ![Suyesh Prabhugaonkar](https://suye.sh)

This project generates a dynamic SVG card displaying your three most recent Medium articles, including the title, a generated subtitle, and the publication date. The SVG is designed to be embedded in your GitHub README.md and updates dynamically on each request.

## Features
- **Dynamic Updates**: Always fetches your latest Medium articles.
- **Customizable Layout**: Displays the title (bold), a generated subtitle (from a blockquote or the first paragraph), and the publication date in a GitHub-dark-themed card.
- **Fully Clickable**: Each card links directly to the article.
- **Optimized for GitHub**: Uses only supported SVG elements for proper rendering.
- **Easy Hosting**: Deployable for free on Render.

## Getting Started

### Prerequisites
- Python 3.7+
- [pip](https://pip.pypa.io/en/stable/installation/)

### Installation

1. **Fork the Repository:**
   Instead of cloning directly, it is better practice to fork the repository first. This way, you can push changes to your fork instead of the original project. Visit the repository page and click the "Fork" button in the top-right corner. Then, clone your forked repository:
   ```bash
   git clone https://github.com/susapr/medium-github-stats.git
   cd medium-github-stats
   ```

2. **Install Dependencies:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   pip install -r requirements.txt
   ```

   Your `requirements.txt` should include:
   ```txt
   fastapi
   uvicorn
   requests
   feedparser
   beautifulsoup4
   ```

### Configuration

1. **Update Your Medium Username:**
   Open the `main.py` file and locate the following line:
   ```python
   MEDIUM_RSS_URL = "https://medium.com/feed/@susapr"
   ```
   Replace `@susapr` with your Medium username. For example, if your Medium username is `johndoe`, update it as:
   ```python
   MEDIUM_RSS_URL = "https://medium.com/feed/@johndoe"
   ```

## Running Locally
To test the service locally, run:
```bash
python main.py
```
This starts a FastAPI server (default: [http://127.0.0.1:8000](http://127.0.0.1:8000)). View the card at:
```
http://127.0.0.1:8000/card
```

## Deploying on Render (Free Hosting)
Render provides free hosting for web services. Follow these steps to deploy:

1. **Push Your Code to GitHub:**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Create a Render Account:**
   - Sign up at [Render.com](https://render.com).
   - Click **"New"** > **"Web Service"**.
   - Connect your GitHub repo.

3. **Configure the Service:**
   - **Name:** Choose a name (e.g., `medium-card`).
   - **Region:** Select the closest region.
   - **Branch:** Select your main branch.
   - **Build Command:**
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command:**
     ```bash
     uvicorn main:app --host 0.0.0.0 --port $PORT
     ```
   - Click **"Create Web Service"**.

4. **Verify Deployment:**
   After deployment, Render provides a URL (e.g., `https://medium-card.onrender.com`). Visit:
   ```
   https://medium-card.onrender.com/card
   ```
   You should see your Medium articles displayed.

## Embedding in GitHub README
Add this to your `README.md` to embed the SVG dynamically:
```md
![Medium Articles](https://medium-card.onrender.com/card)
```
Replace the URL with your Render service URL.

## Support the Project
If you found this project helpful, consider giving it a ⭐ on GitHub! Forking and sharing the project is also greatly appreciated. If you use this project in your own work, please give credit by linking back to the original repository!

## License
This project is licensed under the [MIT License](LICENSE).

## Acknowledgments
- [FastAPI](https://fastapi.tiangolo.com/)
- [Render.com](https://render.com/)
- [Feedparser](https://pythonhosted.org/feedparser/)
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)

---
Enjoy showcasing your latest Medium articles on your GitHub profile!

