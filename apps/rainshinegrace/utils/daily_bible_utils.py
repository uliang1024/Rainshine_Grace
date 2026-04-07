import requests
import re
import json
import os
from ..utils.messages import DailyBibleMessages
from linebot.models import TextSendMessage, FlexSendMessage

# 1. 路徑設定
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# 根據你的 debug，BASE_DIR 是 /var/task，檔案都在這
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(CURRENT_DIR)))

def get_daily_bible_flex():
    data = fetch_daily_bible()
    
    if isinstance(data, dict):
        chapter_verse = data['chapter_verse']
        verse_text = data['verse_text']
        
        bible_url = construct_bible_url(chapter_verse)
        flex_message_json = load_flex_message_json(chapter_verse, verse_text, bible_url)
        
        if flex_message_json is None:
            return TextSendMessage(text="[系統提示] 讀取 Flex 模板檔案失敗，請檢查根目錄是否有 daily_bible_flex.json")

        return FlexSendMessage(
            alt_text=DailyBibleMessages.DAILY_BIBLE_ALT_TEXT,
            contents=flex_message_json,
        )
    else:
        # 如果還是失敗，把抓到的原始網頁內容噴出來看看
        return TextSendMessage(text=f"無法獲取經文，來源內容異常。")

def construct_bible_url(chapter_verse):
    try:
        parts = chapter_verse.split(" ")
        book_name = parts[0]
        chapter = parts[1].split(":")[0]
        
        book_json_path = os.path.join(BASE_DIR, "book.json")
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
        print(f"URL Error: {e}")
    return "https://www.bible.com/zh-TW/bible/46/MAT.1"

def load_flex_message_json(chapter_verse, verse_text, bible_url):
    try:
        # 根據你的 debug 訊息，flex json 似乎是在根目錄
        json_path = os.path.join(BASE_DIR, "daily_bible_flex.json")
        
        with open(json_path, "r", encoding="utf-8") as f:
            flex_message_json = json.load(f)

        flex_str = json.dumps(flex_message_json)
        flex_str = flex_str.replace("{chapter_verse}", chapter_verse)
        flex_str = flex_str.replace("{verse_text}", verse_text)
        flex_str = flex_str.replace("{bible_url}", bible_url)
        return json.loads(flex_str)
    except Exception as e:
        print(f"Flex File Error: {e}")
        return None

def fetch_daily_bible():
    url = "https://www.taiwanbible.com/blog/dailyverse.jsp"
    try:
        # 加上 Headers 模擬瀏覽器，避免被擋
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8' # 強制指定
        
        if response.status_code == 200:
            content = response.text.strip()
            if not content:
                return None

            # 針對 "馬太福音 12:36 我又告訴你們..." 的格式
            # 先嘗試用第一個空格切開「卷名」，再找剩下的
            parts = content.split(" ", 2)
            if len(parts) >= 3:
                return {
                    "chapter_verse": f"{parts[0]} {parts[1]}",
                    "verse_text": parts[2]
                }
            
            # 如果 split 失敗，用 Regex 當保險
            match = re.search(r"(.+?\s\d+:\d+)\s+(.+)", content)
            if match:
                return {
                    "chapter_verse": match.group(1).strip(),
                    "verse_text": match.group(2).strip()
                }
    except Exception as e:
        print(f"Fetch Error: {e}")
    return None
