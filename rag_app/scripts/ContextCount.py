import os 
from pathlib import Path
from google import genai

MODEL = "gemini-2.5-flash"
VERSION = "v1"
DOCS_DIR = Path(f"/app/data/processed/{VERSION}")

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def count_tokens(text: str) -> int:
    response = client.models.count_tokens(
        model=MODEL,
        contents=text,
    )
    return response.total_tokens


def main():
    for file_path in DOCS_DIR.glob("*.md"):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        print(f"File: {file_path.name}")
        print(f"Tokens: {count_tokens(content)}")
        print("-" * 20)


if __name__ == "__main__":
    main()