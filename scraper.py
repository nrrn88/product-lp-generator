import requests
from bs4 import BeautifulSoup
import re

def clean_text(text):
    """
    テキストから不要な空白や改行を削除して整形する
    """
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def scrape_web_page(url):
    """
    指定されたURLからタイトルと本文テキストを取得する
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 不要なタグ（スクリプトやスタイル）を削除
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.extract()
            
        title = soup.title.string if soup.title else "No Title"
        # bodyなどの主要なテキストを取得
        text = soup.get_text()
        
        cleaned_text = clean_text(text)
        
        return {
            "url": url,
            "title": title,
            "content": cleaned_text[:10000] # 文字数制限（トークン節約のため一旦10000文字）
        }
    except Exception as e:
        return {
            "url": url,
            "error": str(e)
        }

def scrape_multiple_urls(urls):
    """
    複数のURLをリストまたは改行区切りテキストで受け取り、結果をリストで返す
    """
    if isinstance(urls, str):
        urls = [u.strip() for u in urls.split('\n') if u.strip()]
    
    results = []
    for url in urls:
        results.append(scrape_web_page(url))
    return results
