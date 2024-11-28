from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from linebot.models import (
    MessageEvent,
    TextSendMessage,
    TemplateSendMessage,
    ButtonsTemplate,
    PostbackTemplateAction,
    PostbackEvent,
)
from ..utils.linebot_utils import parser, reply_message
from ..utils.quiz_utils import fetch_quiz, parse_quiz_data, handle_postback
from linebot.exceptions import InvalidSignatureError, LineBotApiError


@csrf_exempt
def callback(request):
    if request.method == "POST":
        signature = request.META["HTTP_X_LINE_SIGNATURE"]
        body = request.body.decode("utf-8")

        try:
            events = parser.parse(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()

        for event in events:
            if isinstance(event, MessageEvent):
                if event.message.text == "耶穌我準備好了🙏":
                    try:
                        quiz_data = fetch_quiz()
                        if quiz_data is not None:
                            question, answers = parse_quiz_data(quiz_data)

                            buttons_template = ButtonsTemplate(
                                title="聖經問答",
                                text=question,
                                actions=[
                                    PostbackTemplateAction(
                                        label=answers[0][0],
                                        data=f"<ANS>{answers[0][0]}<CORRECT>{answers[0][1]}</CORRECT></ANS>",
                                    ),
                                    PostbackTemplateAction(
                                        label=answers[1][0],
                                        data=f"<ANS>{answers[1][0]}<CORRECT>{answers[1][1]}</CORRECT></ANS>",
                                    ),
                                    PostbackTemplateAction(
                                        label=answers[2][0],
                                        data=f"<ANS>{answers[2][0]}<CORRECT>{answers[2][1]}</CORRECT></ANS>",
                                    ),
                                    PostbackTemplateAction(
                                        label=answers[3][0],
                                        data=f"<ANS>{answers[3][0]}<CORRECT>{answers[3][1]}</CORRECT></ANS>",
                                    ),
                                ],
                            )
                            template_message = TemplateSendMessage(
                                alt_text="聖經問答", template=buttons_template
                            )

                            reply_message(event.reply_token, template_message)
                        else:
                            reply_message(
                                event.reply_token,
                                TextSendMessage(
                                    text="無法獲取問題和選項資料，請稍後再試！"
                                ),
                            )
                    except LineBotApiError:
                        reply_message(
                            event.reply_token,
                            TextSendMessage(
                                text="我的孩子～將我加入為你的好友吧～\n加完好友再輸入一次『耶穌我準備好了🙏』"
                            ),
                        )
            elif isinstance(event, PostbackEvent):
                handle_postback(event)
        return HttpResponse()
    else:
        return HttpResponseBadRequest()
