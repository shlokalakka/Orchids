from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import openai
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

openai.api_key = os.getenv("OPENAI_API_KEY")

class CloneRequest(BaseModel):
    url: str

@app.get("/")
def read_root():
    return {"message": "Hello Orchids"}

@app.post("/clone")
async def clone_website(data: CloneRequest):
    try:
        # 🔎 PART 1: Scraping the target website
        response = requests.get(data.url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract full HTML structure of <body>
        dom_html = str(soup.body) if soup.body else "<body>(empty)</body>"

        # Extract inline <style> tags
        styles = "\n".join(str(tag) for tag in soup.find_all("style"))

        # Download and inject external stylesheets as inline <style>
        links = soup.find_all("link", rel="stylesheet")
        for link in links:
            href = link.get("href")
            if href:
                full_url = urljoin(data.url, href)
                try:
                    css_response = requests.get(full_url, timeout=5)
                    css_response.raise_for_status()
                    styles += f"\n<style>{css_response.text}</style>"
                except Exception:
                    continue  # Skip stylesheet if loading fails

        # Convert relative image srcs to absolute URLs
        for img in soup.find_all("img"):
            src = img.get("src")
            if src:
                img["src"] = urljoin(data.url, src)

        # 🧠 PART 2: Enhanced LLM prompt with full HTML structure
        prompt = f"""
You are an expert front-end developer. Your job is to replicate the structure and styling of the provided webpage as closely as possible. Do not output markdown or explanations.

Output a complete, functional HTML document with embedded CSS that resembles the original site visually.

- Target URL: {data.url}
- Styles:
{styles[:3500]}
- HTML Body:
{dom_html[:3500]}
"""

        # 🤖 PART 3: Send prompt to OpenAI and return the HTML clone
        client = openai.OpenAI()
        llm_response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You generate accurate HTML/CSS clones from scraped site content."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=3500
        )

        cloned_html = llm_response.choices[0].message.content
        if cloned_html.startswith("```html"):
            cloned_html = cloned_html.strip().removeprefix("```html").removesuffix("```")

        return {"cloned_html": cloned_html}

    except Exception as e:
        return {"error": str(e)}
