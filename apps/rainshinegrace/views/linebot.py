import json
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from linebot.models import (
    MessageEvent,
    PostbackEvent,
)
from ..utils.linebot_utils import parser
from ..utils.quiz_utils import handle_postback, get_quiz
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
                print("event", event)
                if event.message.text == "耶穌我準備好了🙏":
                    get_quiz(event)
            elif isinstance(event, PostbackEvent):
                postback_data = json.loads(event.postback.data)
                if postback_data["template_id"] == "quiz":
                    handle_postback(event)
        return HttpResponse()
    else:
        return HttpResponseBadRequest()
