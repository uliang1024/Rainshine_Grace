import requests
import json
import xml.etree.ElementTree as ET
import re  # 確保有這行！
from ..utils.linebot_utils import get_user_profile, set_buttons_template
from ..utils.messages import QuizMessages
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError

# 取得聖經問答
def get_quiz():
    quiz_data = fetch_quiz()
    if quiz_data:
        question, answers = parse_quiz_data(quiz_data)
        if question and answers:
            return set_buttons_template(
                header=QuizMessages.QUIZ_PROMPT,
                question=question,
                answers=answers,
                template_id="quiz",
                image_url=None,
                alt_text=QuizMessages.QUIZ_ALT_TEXT,
            )
    return TextSendMessage(text=QuizMessages.QUIZ_ERROR)

# 取得今日聖經問答API
def fetch_quiz():
    url = "http://www.taiwanbible.com/quiz/todayinnerXML.jsp"
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        # 針對台灣聖經網，有時候 Big5 或 UTF-8 會跳，用 apparent_encoding
        response.encoding = response.apparent_encoding 
        
        if response.status_code == 200:
            content = response.text.strip()
            # Vercel Log 會看到這個，確認有沒有抓到 html/xml
            print(f"DEBUG_QUIZ_RAW: {content[:100]}") 
            return content
    except Exception as e:
        print("Fetch Quiz Error:", e)
    return None

# 解析聖經問答資料
def parse_quiz_data(quiz_data):
    try:
        # 1. 抓取 <xml> 到 </xml> 之間的內容 (無視外層 <html><body>)
        # re.DOTALL 讓 . 可以匹配換行符
        xml_match = re.search(r'(<xml>.*</xml>)', quiz_data, re.DOTALL | re.IGNORECASE)
        if not xml_match:
            print("解析失敗：找不到 <xml> 標籤")
            return None, []
        
        xml_content = xml_match.group(1)
        
        # 2. 解析 XML
        root = ET.fromstring(xml_content)
        
        # 3. 抓取問題 (根據你提供的內容，標籤是小寫 <question>)
        # 使用 .// 確保能找到深層標籤
        q_element = root.find(".//question")
        if q_element is None:
            # 備用方案：試試看大寫
            q_element = root.find(".//QUESTION")
            
        question = q_element.text.strip() if q_element is not None else None

        # 4. 抓取答案
        answers = []
        # 遍歷 <answer> 下的所有子元素 (ans1, ans2...)
        answer_node = root.find(".//answer")
        if answer_node is not None:
            for child in answer_node:
                ans_text_node = child.find("ans")
                correct_node = child.find("correct")
                
                if ans_text_node is not None and correct_node is not None:
                    # 確保 text 不是 None
                    a_txt = ans_text_node.text.strip() if ans_text_node.text else ""
                    c_txt = correct_node.text.strip() if correct_node.text else "0"
                    if a_txt:
                        answers.append((a_txt, c_txt))

        print(f"解析成功: {question}, 選項數: {len(answers)}")
        return question, answers
        
    except Exception as e:
        print(f"XML 解析致命錯誤: {str(e)}")
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
