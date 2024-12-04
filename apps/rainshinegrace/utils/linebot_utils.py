import json
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import LineBotApiError
from linebot.models import (
    ButtonsTemplate,
    PostbackTemplateAction,
    TemplateSendMessage,
)
from django.conf import settings

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)

# 取得用戶資料
def get_user_profile(user_id):
    try:
        return line_bot_api.get_profile(user_id)
    except LineBotApiError:
        return None


# 回覆訊息
def reply_message(reply_token, messages):
    try:
        line_bot_api.reply_message(reply_token, messages)
    except LineBotApiError as e:
        print(f"Error sending reply message: {e}")


# 設定按鈕模板
def set_buttons_template(header, question, answers, template_id, image_url, alt_text):
    actions = [
        PostbackTemplateAction(
            label=answer[0][:20],  # 限制 label 的长度为最多 20 个字符
            data=json.dumps({"template_id": template_id, "answer": answer[1]}),
        )
        for answer in answers
    ]
    buttons_template = ButtonsTemplate(
        title=header[:40],  # 如果 title 也有长度限制，可按需截短
        text=question[:160],  # 如果 text 有限制，可按需截短
        actions=actions,
        thumbnail_image_url=image_url,
    )
    return TemplateSendMessage(alt_text=alt_text, template=buttons_template)


def push_message(to, messages):
    try:
        line_bot_api.push_message(to, messages)
    except LineBotApiError as e:
        print(f"Error sending push message: {e}")
