import json
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from linebot.models import (
    MessageEvent,
    PostbackEvent,
    JoinEvent,
)
from ..utils.linebot_utils import parser
from ..utils.quiz_utils import handle_postback, get_quiz
from ..utils.daily_bible_utils import get_daily_bible_flex
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from ..utils.messages import QuizMessages, DailyBibleMessages
from ..utils.linebot_utils import push_message, reply_message
from django.http import JsonResponse


@csrf_exempt
def callback(request):
    if request.method == "POST":
        signature = request.META["HTTP_X_LINE_SIGNATURE"]
        body = request.body.decode("utf-8")
        events = parse_events(body, signature)
        if events is None:
            return HttpResponseBadRequest()

        for event in events:
            handle_event(event)
        return HttpResponse()
    else:
        return HttpResponseBadRequest()

def parse_events(body, signature):
    try:
        return parser.parse(body, signature)
    except InvalidSignatureError:
        return HttpResponseForbidden()
    except LineBotApiError:
        return None

def handle_event(event):
    if isinstance(event, MessageEvent):
        handle_message_event(event)
    elif isinstance(event, PostbackEvent):
        handle_postback_event(event)
    elif isinstance(event, JoinEvent):
        handle_join_event(event)

def handle_message_event(event):
    if event.message.text == QuizMessages.QUIZ_READY_MESSAGE:
        reply_message(event.reply_token, get_quiz())
    elif event.message.text == DailyBibleMessages.DAILY_BIBLE_MESSAGE:
        reply_message(event.reply_token, get_daily_bible_flex())

def handle_postback_event(event):
    postback_data = json.loads(event.postback.data)
    if postback_data["template_id"] == "quiz":
        reply_message(event.reply_token, handle_postback(event))

def handle_join_event(event):
    group_id = event.source.group_id
    print(f"Joined group with ID: {group_id}")


@csrf_exempt
def send_quiz_to_group(request):
    if request.method == "POST":
        group_id = request.POST.get("group_id")
        if not group_id:
            return JsonResponse({"error": "Group ID is required"}, status=400)
        try:
            push_message(group_id, get_quiz())
            return JsonResponse({"status": "success"})
        except Exception:
            return JsonResponse({"error": "Internal server error"}, status=500)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt
def send_daily_bible_to_group(request):
    if request.method == "POST":
        group_id = request.POST.get("group_id")
        if not group_id:
            return JsonResponse({"error": "Group ID is required"}, status=400)
        try:
            push_message(group_id, get_daily_bible_flex())
            return JsonResponse({"status": "success"})
        except Exception:
            return JsonResponse({"error": "Internal server error"}, status=500)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)
