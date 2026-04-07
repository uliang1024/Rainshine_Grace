import json
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import LineBotApiError
from linebot.models import (
    ButtonsTemplate,
    PostbackTemplateAction,
    TemplateSendMessage,
)
from django.conf import settings

# 初始化 LineBotApi
line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)

def get_user_profile(user_id):
    try:
        return line_bot_api.get_profile(user_id)
    except LineBotApiError:
        return None

def reply_message(reply_token, messages):
    try:
        line_bot_api.reply_message(reply_token, messages)
    except LineBotApiError as e:
        print(f"Error sending reply message: {e}")

def set_buttons_template(header, question, answers, template_id, image_url, alt_text):
    """
    設定按鈕模板，並處理 LINE API 的各種長度與數量限制
    """
    # 建立按鈕列表 (最多 4 個)
    actions = [
        PostbackTemplateAction(
            label=answer[0][:20], # LINE 規定最多 20 字
            data=json.dumps({"template_id": template_id, "answer": answer[1]})
        )
        for answer in answers[:4]
    ]
    
    # 參數保護邏輯：
    # LINE 規定：若無 thumbnail_image_url，則 title 建議為空，避免排版出錯
    final_title = header[:40] if image_url else None
    final_image = image_url if image_url else None

    buttons_template = ButtonsTemplate(
        title=final_title,
        text=question[:160], # LINE 規定最多 160 字
        actions=actions,
        thumbnail_image_url=final_image,
    )
    
    return TemplateSendMessage(alt_text=alt_text[:400], template=buttons_template)

def push_message(to, messages):
    try:
        line_bot_api.push_message(to, messages)
    except LineBotApiError as e:
        print(f"Error sending push message: {e}")
