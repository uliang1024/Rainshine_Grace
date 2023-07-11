from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
 
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage, TemplateSendMessage, ButtonsTemplate, PostbackTemplateAction, PostbackEvent
 
from rainshinegrace.lineNotify import line_notify_send_message
 
import re
import requests
 
line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)
 
 
def fetch_quiz():
    url = 'http://www.taiwanbible.com/quiz/todayinnerXML.jsp'

    try:
        response = requests.get(url)
        response.raise_for_status()

        content = response.text.replace('\n', '').replace('\r', '').replace(' ', '')

        return content
    except requests.exceptions.RequestException as e:
        print('Error:', e)
        return None

def handle_postback(event):
    user_id = event.source.user_id
    try:
        profile = line_bot_api.get_profile(user_id)
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

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )
    except LineBotApiError:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='我的孩子～將我加入為你的好友吧～')
        )
        line_notify_send_message(message='加完好友再輸入一次『耶穌我準備好了🙏』')
        
@csrf_exempt
def callback(request):
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')

        try:
            events = parser.parse(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()

        for event in events:
            if isinstance(event, MessageEvent):
                if event.message.text == '耶穌我準備好了🙏':
                    user_id = event.source.user_id

                    try:
                        profile = line_bot_api.get_profile(user_id)
                        quiz_data = fetch_quiz()
                        if quiz_data is not None:
                            question = re.search(r"<QUESTION>(.*?)</QUESTION>", quiz_data).group(1)
                            ans1 = re.search(r"<ANS1><ANS>(.*?)</ANS>", quiz_data).group(1)
                            ans1_correct = re.search(r"<ANS1><ANS>.*?</ANS><CORRECT>(.*?)</CORRECT>", quiz_data).group(1)
                            ans2 = re.search(r"<ANS2><ANS>(.*?)</ANS>", quiz_data).group(1)
                            ans2_correct = re.search(r"<ANS2><ANS>.*?</ANS><CORRECT>(.*?)</CORRECT>", quiz_data).group(1)
                            ans3 = re.search(r"<ANS3><ANS>(.*?)</ANS>", quiz_data).group(1)
                            ans3_correct = re.search(r"<ANS3><ANS>.*?</ANS><CORRECT>(.*?)</CORRECT>", quiz_data).group(1)
                            ans4 = re.search(r"<ANS4><ANS>(.*?)</ANS>", quiz_data).group(1)
                            ans4_correct = re.search(r"<ANS4><ANS>.*?</ANS><CORRECT>(.*?)</CORRECT>", quiz_data).group(1)

                            buttons_template = ButtonsTemplate(
                                title='聖經問答',
                                text=question,
                                actions=[
                                    PostbackTemplateAction(label=ans1, data=f"<ANS>{ans1}<CORRECT>{ans1_correct}</CORRECT></ANS>"),
                                    PostbackTemplateAction(label=ans2, data=f"<ANS>{ans2}<CORRECT>{ans2_correct}</CORRECT></ANS>"),
                                    PostbackTemplateAction(label=ans3, data=f"<ANS>{ans3}<CORRECT>{ans3_correct}</CORRECT></ANS>"),
                                    PostbackTemplateAction(label=ans4, data=f"<ANS>{ans4}<CORRECT>{ans4_correct}</CORRECT></ANS>")
                                ]
                            )
                            template_message = TemplateSendMessage(
                                alt_text='聖經問答',
                                template=buttons_template
                            )

                            line_bot_api.reply_message(
                                event.reply_token,
                                template_message
                            )
                        else:
                            line_bot_api.reply_message(
                                event.reply_token,
                                TextSendMessage(text='無法獲取問題和選項資料，請稍後再試！')
                            )
                    except LineBotApiError:
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text='我的孩子～將我加入為你的好友吧～')
                        )
                        line_notify_send_message(message='加完好友再輸入一次『耶穌我準備好了🙏』')
            elif isinstance(event, PostbackEvent):
                handle_postback(event)
        return HttpResponse()
    else:
        return HttpResponseBadRequest()