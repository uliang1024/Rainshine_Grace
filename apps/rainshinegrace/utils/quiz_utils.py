import requests
import json
import xml.etree.ElementTree as ET
from ..utils.linebot_utils import get_user_profile, reply_message, set_buttons_template
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError


def get_quiz(event):
    quiz_data = fetch_quiz()
    if quiz_data is not None:
        question, answers = parse_quiz_data(quiz_data)
        buttons_template = set_buttons_template(
            header="聖經問答",
            question=question,
            answers=answers,
            template_id="quiz",
            image_url=None,
            alt_text="聖經問答",
        )
        reply_message(event.reply_token, buttons_template)
    else:
        reply_message(
            event.reply_token,
            TextSendMessage(text="無法獲取問題和選項資料，請稍後再試！"),
        )


# 取得今日聖經問答
def fetch_quiz():
    url = "http://www.taiwanbible.com/quiz/todayinnerXML.jsp"
    try:
        response = requests.get(url)
        response.raise_for_status()
        content = response.text.replace("\n", "").replace("\r", "").replace(" ", "")
        return content
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return None


# 解析聖經問答資料
def parse_quiz_data(quiz_data):
    """Parses the quiz data to extract the question and answers."""
    try:
        # 解析 XML 資料
        root = ET.fromstring(quiz_data)
        question = root.find(".//QUESTION").text
        answers = [
            (ans.find("ANS").text.strip(), ans.find("CORRECT").text.strip())
            for ans in root.findall(".//ANSWER/*")
            if ans.find("ANS").text and ans.find("CORRECT").text
        ]

        return question, answers
    except ET.ParseError as e:
        print("Error parsing XML data:", e)
        return None, []


# 處理回傳事件
def handle_postback(event):
    user_id = event.source.user_id
    try:
        profile = get_user_profile(user_id)
        if profile:
            display_name = profile.display_name
            postback_data = json.loads(event.postback.data)
            answer = postback_data["answer"]

            if answer == "1":
                reply_text = f"{display_name}答對啦！🎉"
            else:
                reply_text = (
                    f"{display_name}選錯囉～多讀聖經！\n"
                    f"天國的道理深奧，需要你用心查考，才能明白其中的奧秘。 📖"
                )

            reply_message(event.reply_token, TextSendMessage(text=reply_text))
        else:
            reply_message(
                event.reply_token,
                TextSendMessage(
                    text="總有人摸我，因我覺得有能力從我身上出去。(路8:46)"
                ),
            )
    except LineBotApiError:
        reply_message(
            event.reply_token,
            TextSendMessage(text="發生錯誤，請稍後再試！"),
        )
