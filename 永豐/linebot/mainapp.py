import os
from dotenv import load_dotenv
load_dotenv() #載入env檔

from flask import Flask, request, abort

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
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

app = Flask(__name__)

YOUR_CHANNEL_ACCESS_TOKEN=os.getenv('YOUR_CHANNEL_ACCESS_TOKEN')
YOUR_CHANNEL_SECRET=os.getenv('YOUR_CHANNEL_SECRET')

# 初始化 WebhookHandler 和 Configuration
handler = WebhookHandler(YOUR_CHANNEL_SECRET)
configuration = Configuration(access_token=YOUR_CHANNEL_ACCESS_TOKEN)

#引進Gemini 
import google.generativeai as genai
import os

genai.configure(api_key=os.environ["Gemini_API"])

model = genai.GenerativeModel('gemini-1.5-flash')

#Gemini回應訊息 
response = model.generate_content("Hello")
print(response.text)

# 清理回應
gemini_response_cleaned = response.text.strip().replace("\n", " ")
gemini_response_cleaned

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature'] #驗證是否是line平台發出的 

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
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
    # 取得用戶傳來的訊息
    user_message = event.message.text
    # 呼叫 Gemini API 進行回應
    gemini_response = model.generate_content(f"請先講一個有關陳容琦的笑話，再用繁體中文回答以下用戶傳來的訊息:{user_message}")
    app.logger.info("Handling message event")
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(\
                reply_token=event.reply_token,
                messages=[TextMessage(text=gemini_response.text)]
            )
        )


if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5001) #host設定允許之後所有網路訪問 包含容器外部

    


