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
        # 1. 模擬瀏覽器並處理編碼
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = response.apparent_encoding # 自動偵測編碼 (重要！)
        
        if response.status_code == 200:
            # 2. 不要用 replace(" ", "")，這會破壞 XML 結構
            # 只要去掉前後空白即可
            content = response.text.strip()
            
            # 3. 檢查內容是否為空
            if not content:
                print("Error: API returned empty content")
                return None
                
            print(f"DEBUG_QUIZ_XML: {content[:100]}...") # 打印前100字確認格式
            return content
            
    except Exception as e:
        print("Fetch Quiz Error:", e)
    return None


# 解析聖經問答資料
def parse_quiz_data(quiz_data):
    try:
        # 1. 清理可能存在的雜質 (例如 XML 宣告前的空白)
        quiz_data = quiz_data.strip()
        
        # 2. 解析 XML
        root = ET.fromstring(quiz_data)
        
        # 3. 抓取問題 (增加防呆)
        q_element = root.find(".//QUESTION")
        question = q_element.text.strip() if q_element is not None else "無題目"
        
        # 4. 抓取答案
        answers = []
        # 注意：檢查原本的 XML 結構，確保 find 跟 findall 的路徑正確
        for ans in root.findall(".//ANSWER/*"):
            ans_text_el = ans.find("ANS")
            correct_el = ans.find("CORRECT")
            
            if ans_text_el is not None and correct_el is not None:
                if ans_text_el.text: # 確保裡面有字
                    answers.append((ans_text_el.text.strip(), correct_el.text.strip()))
        
        if not answers:
            print("Error: No answers found in XML")
            return None, []
            
        return question, answers
        
    except ET.ParseError as e:
        print("XML Parse Error:", e)
        # 如果解析失敗，有可能是因為 XML 格式不標準，可以嘗試印出原始資料除錯
        print(f"Faulty XML: {quiz_data}")
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
