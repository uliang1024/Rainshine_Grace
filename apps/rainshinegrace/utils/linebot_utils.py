from linebot import LineBotApi, WebhookParser
from django.conf import settings

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)


def get_user_profile(user_id):
    return line_bot_api.get_profile(user_id)


def reply_message(reply_token, messages):
    line_bot_api.reply_message(reply_token, messages)
