import os
from dotenv import load_dotenv
from collections import deque
import json
load_dotenv()  # 載入env檔
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)
import google.generativeai as genai

app = Flask(__name__)

YOUR_CHANNEL_ACCESS_TOKEN = os.getenv('YOUR_CHANNEL_ACCESS_TOKEN')
YOUR_CHANNEL_SECRET = os.getenv('YOUR_CHANNEL_SECRET')

# 初始化 WebhookHandler 和 Configuration
handler = WebhookHandler(YOUR_CHANNEL_SECRET)
configuration = Configuration(access_token=YOUR_CHANNEL_ACCESS_TOKEN)

# 設定 Gemini
genai.configure(api_key=os.environ["Gemini_API"])
model = genai.GenerativeModel('gemini-pro')

# 初始化對話歷史
MAX_HISTORY = 10
conversation_history = {}

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    return 'OK'

@app.route("/")
def index():
    return "Flask is running!"

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_id = event.source.user_id
    user_message = event.message.text
    
    # 獲取或初始化用戶的對話歷史
    if user_id not in conversation_history:
        conversation_history[user_id] = deque(maxlen=MAX_HISTORY)
    
    # 添加用戶消息到歷史
    conversation_history[user_id].append({"role": "user", "parts": [user_message]})
    
    # 準備完整的對話歷史供 Gemini 使用
    full_conversation = list(conversation_history[user_id])
    
    # 呼叫 Gemini API 進行回應
    gemini_response = model.generate_content(full_conversation)
    response_text = gemini_response.text
    
    # 添加 Gemini 的回應到歷史
    conversation_history[user_id].append({"role": "model", "parts": [response_text]})
    
    app.logger.info(f"Conversation history for user {user_id}: {json.dumps(list(conversation_history[user_id]))}")
    
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=response_text)]
            )
        )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)