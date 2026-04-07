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
        
        # 確保有題目且有答案 (1~4個)
        if question and answers:
            try:
                # 調用封裝好的模板設定
                return set_buttons_template(
                    header=QuizMessages.QUIZ_PROMPT,
                    question=question,
                    answers=answers,
                    template_id="quiz",
                    image_url=None, # 這裡設為 None，內部會處理標題保護
                    alt_text=QuizMessages.QUIZ_ALT_TEXT,
                )
            except Exception as e:
                print(f"DEBUG: set_buttons_template failed: {e}")
    
    return TextSendMessage(text=QuizMessages.QUIZ_ERROR)

def fetch_quiz():
    url = "http://www.taiwanbible.com/quiz/todayinnerXML.jsp"
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = response.apparent_encoding 
        if response.status_code == 200:
            return response.text.strip()
    except Exception as e:
        print(f"DEBUG: fetch_quiz error: {e}")
    return None

def parse_quiz_data(quiz_data):
    try:
        # 1. 強力過濾：只提取 <xml> 到 </xml>
        xml_match = re.search(r'<xml>.*</xml>', quiz_data, re.I | re.S)
        if not xml_match:
            return None, []
        
        xml_content = xml_match.group(0)
        root = ET.fromstring(xml_content)
        
        # 2. 抓取題目 (支援小寫 question)
        q_node = root.find(".//question")
        if q_node is None: q_node = root.find(".//QUESTION")
        question = q_node.text.strip() if q_node is not None else "題目加載中"
        
        # 3. 抓取答案清單
        answers = []
        ans_container = root.find(".//answer")
        if ans_container is None: ans_container = root.find(".//ANSWER")
        
        if ans_container is not None:
            # 遍歷 ans1, ans2... 
            for child in ans_container:
                a_node = child.find("ans")
                if a_node is None: a_node = child.find("ANS")
                
                c_node = child.find("correct")
                if c_node is None: c_node = child.find("CORRECT")
                
                if a_node is not None and c_node is not None:
                    txt = a_node.text.strip() if a_node.text else ""
                    val = c_node.text.strip() if c_node.text else "0"
                    if txt:
                        # 限制 label 20 字 (LINE 硬性規定)
                        answers.append((txt[:20], val))

        # 4. LINE 安全閥：按鈕數量必須在 1~4 之間
        if not answers:
            return None, []
        if len(answers) > 4:
            answers = answers[:4]

        return question, answers
    except Exception as e:
        print(f"DEBUG: parse_quiz_data exception: {e}")
        return None, []

def handle_postback(event):
    user_id = event.source.user_id
    try:
        profile = get_user_profile(user_id)
        display_name = profile.display_name if profile else "用戶"
        
        postback_data = json.loads(event.postback.data)
        answer = postback_data.get("answer", "0")

        if answer == "1":
            reply_text = f"{display_name}{QuizMessages.QUIZ_CORRECT}"
        else:
            reply_text = f"{display_name}{QuizMessages.QUIZ_WRONG}"

        return TextSendMessage(text=reply_text)
    except Exception as e:
        print(f"DEBUG: handle_postback error: {e}")
        return TextSendMessage(text=QuizMessages.QUIZ_ERROR)
