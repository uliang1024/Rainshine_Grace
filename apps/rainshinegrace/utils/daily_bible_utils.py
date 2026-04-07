import requests
import re
import json
import os
from ..utils.messages import DailyBibleMessages
from linebot.models import TextSendMessage, FlexSendMessage

# 取得目前檔案 (daily_bible_utils.py) 的絕對目錄
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

def get_daily_bible_flex():
    # 1. 獲取資料
    data = fetch_daily_bible()
    
    # 2. 檢查是否成功解析成字典
    if isinstance(data, dict):
        chapter_verse = data['chapter_verse']
        verse_text = data['verse_text']
        
        # 3. 取得連結與 Flex JSON
        bible_url = construct_bible_url(chapter_verse)
        flex_message_json = load_flex_message_json(chapter_verse, verse_text, bible_url)
        
        return FlexSendMessage(
            alt_text=DailyBibleMessages.DAILY_BIBLE_ALT_TEXT,
            contents=flex_message_json,
        )
    else:
        # 4. 失敗時回傳文字訊息
        return TextSendMessage(text=DailyBibleMessages.DAILY_BIBLE_ERROR)

def construct_bible_url(chapter_verse):
    try:
        # 分解 "馬太福音 12:36"
        parts = chapter_verse.split(" ")
        book_name = parts[0]
        chapter_verse_number = parts[1]
        chapter = chapter_verse_number.split(":")[0]
        
        # 使用絕對路徑讀取 book.json
        book_json_path = os.path.join(CURRENT_DIR, "book.json")
        with open(book_json_path, "r", encoding="utf-8") as f:
            book_data = json.load(f)

        book_code = None
        chapter_code = None
        for book in book_data["books"]:
            if book["human"] == book_name:
                book_code = book["usfm"]
                for chap in book["chapters"]:
                    if chap["human"] == chapter:
                        chapter_code = chap["usfm"]
                        break
                break

        if book_code and chapter_code:
            return f"https://www.bible.com/zh-TW/bible/46/{chapter_code}"
    except Exception as e:
        print(f"URL construct error: {e}")
        
    return "https://www.bible.com/zh-TW/bible/46/MAT.1" # 預設失敗回傳

def load_flex_message_json(chapter_verse, verse_text, bible_url):
    # 使用絕對路徑讀取 daily_bible_flex.json
    json_path = os.path.join(CURRENT_DIR, "daily_bible_flex.json")
    with open(json_path, "r", encoding="utf-8") as f:
        flex_message_json = json.load(f)

    # 替換變數
    flex_str = json.dumps(flex_message_json)
    flex_str = flex_str.replace("{chapter_verse}", chapter_verse)
    flex_str = flex_str.replace("{verse_text}", verse_text)
    flex_str = flex_str.replace("{bible_url}", bible_url)
    
    return json.loads(flex_str)

def fetch_daily_bible():
    url = "https://www.taiwanbible.com/blog/dailyverse.jsp"
    try:
        response = requests.get(url, timeout=10)
        # 確保編碼正確，解決潛在亂碼問題
        response.encoding = response.apparent_encoding 
        
        if response.status_code == 200:
            content = response.text.strip()
            print(f"Original content: {content}") 

            # Regex 說明：(.+? \d+:\d+) 抓章節，\s+ 抓空格或換行，(.+) 抓剩下的經文
            match = re.search(r"(.+? \d+:\d+)\s+(.+)", content)
            if match:
                return {
                    "chapter_verse": match.group(1).strip(),
                    "verse_text": match.group(2).strip()
                }
            else:
                print("Regex match failed.")
    except Exception as e:
        print(f"Fetch error: {e}")
    
    return None
