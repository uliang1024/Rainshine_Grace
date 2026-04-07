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
        # 1. 強力清洗：只抓取 <xml> ... </xml> 之間的內容，過濾掉 html/body
        xml_match = re.search(r'(<xml>.*</xml>)', quiz_data, re.DOTALL)
        if not xml_match:
            print("找不到 XML 結構")
            return None, []
        
        xml_content = xml_match.group(1)
        
        # 2. 解析 XML
        root = ET.fromstring(xml_content)
        
        # 3. 抓取問題 (現在是小寫 <question>)
        q_element = root.find(".//question")
        question = q_element.text.strip() if q_element is not None else "無題目資料"
        
        # 4. 抓取答案 (現在是 <ans1>, <ans2> ... 裡面的 <ans> 和 <correct>)
        answers = []
        # 遍歷 <answer> 下的所有子標籤 (ans1, ans2, ans3, ans4)
        answer_container = root.find(".//answer")
        if answer_container is not None:
            for ans_item in answer_container:
                ans_text_el = ans_item.find("ans")
                correct_el = ans_item.find("correct")
                
                if ans_text_el is not None and correct_el is not None:
                    answers.append((
                        ans_text_el.text.strip(), 
                        correct_el.text.strip()
                    ))

        return question, answers
        
    except Exception as e:
        print("解析聖經問答失敗:", e)
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
