import requests
import re
import json
from ..utils.messages import DailyBibleMessages
from linebot.models import TextSendMessage, FlexSendMessage


def get_daily_bible_flex():
    daily_bible_data = fetch_daily_bible()
    if daily_bible_data is not None:
        lines = daily_bible_data.split("\n")
        chapter_verse = lines[0]
        verse_text = lines[1]

        # 解析 chapter_verse
        book_name, chapter_verse_number = chapter_verse.split(" ")
        chapter, verse = chapter_verse_number.split(":")

        # 讀取 book.json 文件
        with open("book.json", "r", encoding="utf-8") as f:
            book_data = json.load(f)

        # 查找書名和章節的 USFM 縮寫
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

        # 構建 URL
        if book_code and chapter_code:
            bible_url = f"https://www.bible.com/zh-TW/bible/46/{chapter_code}"
        else:
            bible_url = (
                "https://www.bible.com/zh-TW/bible/46/UNKNOWN"
            )

        with open("daily_bible_flex.json", "r", encoding="utf-8") as f:
            flex_message_json = json.load(f)

        flex_message_json_str = json.dumps(flex_message_json)
        flex_message_json_str = flex_message_json_str.replace(
            "{chapter_verse}", chapter_verse
        )
        flex_message_json_str = flex_message_json_str.replace(
            "{verse_text}", verse_text
        )
        flex_message_json_str = flex_message_json_str.replace("{bible_url}", bible_url)
        flex_message_json = json.loads(flex_message_json_str)

        flex_message = FlexSendMessage(
            alt_text=DailyBibleMessages.DAILY_BIBLE_ALT_TEXT,
            contents=flex_message_json,
        )
        return flex_message
    else:
        return TextSendMessage(text=DailyBibleMessages.DAILY_BIBLE_ERROR)


def fetch_daily_bible():
    url = "https://www.taiwanbible.com/blog/dailyverse.jsp"
    response = requests.get(url)
    if response.status_code == 200:
        content = response.text.strip()
        content = "\n".join(
            line.strip() for line in content.splitlines() if line.strip()
        )

        match = re.match(r"(.+? \d+:\d+) (.+)", content)
        if match:
            chapter_verse = match.group(1)
            verse_text = match.group(2)
            formatted_content = f"{chapter_verse}\n{verse_text}"
            return formatted_content
        else:
            return DailyBibleMessages.DAILY_BIBLE_ERROR
    else:
        return DailyBibleMessages.DAILY_BIBLE_ERROR
