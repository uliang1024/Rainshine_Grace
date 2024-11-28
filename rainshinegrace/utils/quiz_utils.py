import re
import requests
from ..utils.linebot_utils import get_user_profile, reply_message
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError


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


def parse_quiz_data(quiz_data):
    question = re.search(r"<QUESTION>(.*?)</QUESTION>", quiz_data).group(1)
    answers = []
    for i in range(1, 5):
        ans = re.search(rf"<ANS{i}><ANS>(.*?)</ANS>", quiz_data).group(1)
        correct = re.search(
            rf"<ANS{i}><ANS>.*?</ANS><CORRECT>(.*?)</CORRECT>", quiz_data
        ).group(1)
        answers.append((ans, correct))
    return question, answers


def handle_postback(event):
    user_id = event.source.user_id
    try:
        profile = get_user_profile(user_id)
        display_name = profile.display_name

        postback_data = event.postback.data
        print(event.postback.data)

        option = re.search(r"<ANS>(.*?)</ANS>", postback_data).group(1)
        is_correct = re.search(r"<CORRECT>(.*?)</CORRECT>", postback_data).group(1)

        option = re.sub(r"<CORRECT>.*?</CORRECT>", "", option)

        if is_correct == "1":
            reply_text = f"{display_name}答對啦！🎉"
        else:
            reply_text = f"{display_name}選錯囉～多讀聖經！😔"

        reply_message(event.reply_token, TextSendMessage(text=reply_text))
    except LineBotApiError:
        reply_message(
            event.reply_token,
            TextSendMessage(
                text="我的孩子～將我加入為你的好友吧～\n加完好友再輸入一次『耶穌我準備好了🙏』"
            ),
        )
