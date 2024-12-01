import requests
import json
import xml.etree.ElementTree as ET
from ..utils.linebot_utils import get_user_profile, set_buttons_template
from ..utils.messages import QuizMessages
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError


# 取得聖經問答
def get_quiz():
    quiz_data = fetch_quiz()
    if quiz_data is not None:
        question, answers = parse_quiz_data(quiz_data)
        buttons_template = set_buttons_template(
            header=QuizMessages.QUIZ_PROMPT,
            question=question,
            answers=answers,
            template_id="quiz",
            image_url=None,
            alt_text=QuizMessages.QUIZ_ALT_TEXT,
        )
        return buttons_template
    else:
        return TextSendMessage(text=QuizMessages.QUIZ_ERROR)


# 取得今日聖經問答API
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
                reply_text = f"{display_name}{QuizMessages.QUIZ_CORRECT}"
            else:
                reply_text = f"{display_name}{QuizMessages.QUIZ_WRONG}"

            return TextSendMessage(text=reply_text)
        else:
            return TextSendMessage(text=QuizMessages.QUIZ_WRONG_DEFAULT)
    except LineBotApiError:
        return TextSendMessage(text=QuizMessages.QUIZ_ERROR)
