import requests
import json
import xml.etree.ElementTree as ET
import re
from ..utils.linebot_utils import get_user_profile, set_buttons_template
from ..utils.messages import QuizMessages
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError

def get_quiz():
    quiz_data = fetch_quiz()
    if quiz_data:
        question, answers = parse_quiz_data(quiz_data)
        # --- DEBUG 點 1 ---
        print(f"DEBUG: question={question}, answers_count={len(answers)}")
        
        if question and answers:
            try:
                # 確保你的 set_buttons_template 能處理 [(text, correct), ...] 這種格式
                return set_buttons_template(
                    header=QuizMessages.QUIZ_PROMPT,
                    question=question,
                    answers=answers,
                    template_id="quiz",
                    image_url=None,
                    alt_text=QuizMessages.QUIZ_ALT_TEXT,
                )
            except Exception as e:
                print(f"DEBUG: set_buttons_template failed: {e}")
    
    # 如果走到這代表前面有東西回傳了 None
    return TextSendMessage(text=QuizMessages.QUIZ_ERROR)

def fetch_quiz():
    url = "http://www.taiwanbible.com/quiz/todayinnerXML.jsp"
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = response.apparent_encoding 
        if response.status_code == 200:
            return response.text.strip()
    except Exception as e:
        print(f"DEBUG: fetch_quiz error: {e}")
    return None

def parse_quiz_data(quiz_data):
    try:
        # 1. 抓取 XML 區塊
        xml_match = re.search(r'<xml>.*</xml>', quiz_data, re.I | re.S)
        if not xml_match:
            print("DEBUG: 找不到 <xml> 標籤")
            return None, []
        
        xml_content = xml_match.group(0)
        root = ET.fromstring(xml_content)
        
        # 2. 抓取題目 (支援大小寫)
        q_node = root.find(".//question")
        if q_node is None: q_node = root.find(".//QUESTION")
        question = q_node.text.strip() if q_node is not None else "題目加載失敗"
        
        # 3. 抓取答案
        answers = []
        ans_container = root.find(".//answer")
        if ans_container is None: ans_container = root.find(".//ANSWER")
        
        if ans_container is not None:
            for child in ans_container:
                a_node = child.find("ans")
                if a_node is None: a_node = child.find("ANS")
                
                c_node = child.find("correct")
                if c_node is None: c_node = child.find("CORRECT")
                
                if a_node is not None and c_node is not None:
                    # 限制 label 20 字，並確保有內容
                    label = a_node.text.strip()[:20] if a_node.text else ""
                    value = c_node.text.strip() if c_node.text else "0"
                    if label:
                        answers.append((label, value))

        # --- 重要安全閥：LINE ButtonsTemplate 最多只能有 4 個按鈕 ---
        if len(answers) > 4:
            print(f"DEBUG: 原始選項有 {len(answers)} 個，已截斷至 4 個")
            answers = answers[:4]

        return question, answers
    except Exception as e:
        print(f"DEBUG: 解析異常: {e}")
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
