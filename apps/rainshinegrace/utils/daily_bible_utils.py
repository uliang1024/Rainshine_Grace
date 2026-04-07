import requests
import re
import json
import os
from ..utils.messages import DailyBibleMessages
from linebot.models import TextSendMessage, FlexSendMessage

# 1. 取得專案根目錄路徑 (從 utils 往上推三層到 Rainshine_Grace)
# CURRENT_DIR 是 apps/rainshinegrace/utils
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# BASE_DIR 會是專案根目錄 Rainshine_Grace
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(CURRENT_DIR)))

def get_daily_bible_flex():
    data = fetch_daily_bible()
    
    if isinstance(data, dict):
        chapter_verse = data['chapter_verse']
        verse_text = data['verse_text']
        
        bible_url = construct_bible_url(chapter_verse)
        flex_message_json = load_flex_message_json(chapter_verse, verse_text, bible_url)
        
        # 如果 Flex JSON 讀取失敗，會回傳 None，這裡做個防護
        if flex_message_json is None:
            return TextSendMessage(text="讀取 Flex 模板失敗")

        return FlexSendMessage(
            alt_text=DailyBibleMessages.DAILY_BIBLE_ALT_TEXT,
            contents=flex_message_json,
        )
    else:
        import os
        debug_msg = f"錯誤原因: {data if data else '抓取失敗'}\n"
        debug_msg += f"當前目錄: {os.getcwd()}\n"
        debug_msg += f"BASE_DIR 內容: {os.listdir(BASE_DIR) if os.path.exists(BASE_DIR) else '路徑不存在'}"
        return TextSendMessage(text=debug_msg)
        # return TextSendMessage(text=DailyBibleMessages.DAILY_BIBLE_ERROR)

def construct_bible_url(chapter_verse):
    try:
        # 分解 "馬太福音 12:36"
        parts = chapter_verse.split(" ")
        book_name = parts[0]
        chapter_verse_number = parts[1]
        chapter = chapter_verse_number.split(":")[0]
        
        # 修正路徑：直接去根目錄找 book.json
        book_json_path = os.path.join(BASE_DIR, "book.json")
        
        if not os.path.exists(book_json_path):
            print(f"找不到檔案: {book_json_path}")
            return "https://www.bible.com/zh-TW/bible/46/MAT.1"

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
        
    return "https://www.bible.com/zh-TW/bible/46/MAT.1"

def load_flex_message_json(chapter_verse, verse_text, bible_url):
    try:
        # 假設 daily_bible_flex.json 跟此 py 檔在同一個 utils 資料夾
        json_path = os.path.join(CURRENT_DIR, "daily_bible_flex.json")
        
        with open(json_path, "r", encoding="utf-8") as f:
            flex_message_json = json.load(f)

        flex_str = json.dumps(flex_message_json)
        flex_str = flex_str.replace("{chapter_verse}", chapter_verse)
        flex_str = flex_str.replace("{verse_text}", verse_text)
        flex_str = flex_str.replace("{bible_url}", bible_url)
        
        return json.loads(flex_str)
    except Exception as e:
        print(f"Flex JSON error: {e}")
        return None

def fetch_daily_bible():
    url = "https://www.taiwanbible.com/blog/dailyverse.jsp"
    try:
        response = requests.get(url, timeout=10)
        response.encoding = response.apparent_encoding 
        
        if response.status_code == 200:
            content = response.text.strip()
            print(f"Original content: {content}") 

            # 針對你提供的格式微調 Regex
            # 支援：書卷名(空格)章:節(空格)經文內容
            match = re.search(r"(.+?\s\d+:\d+)\s+(.+)", content)
            if match:
                return {
                    "chapter_verse": match.group(1).strip(),
                    "verse_text": match.group(2).strip()
                }
            else:
                # 備用方案：如果空格抓不到，嘗試抓第一個冒號前後的內容
                print("Regex match failed, trying backup.")
                parts = content.split(" ", 2) # 用空格切分
                if len(parts) >= 2:
                    return {
                        "chapter_verse": f"{parts[0]} {parts[1]}",
                        "verse_text": parts[2] if len(parts) > 2 else ""
                    }
    except Exception as e:
        print(f"Fetch error: {e}")
    
    return None
