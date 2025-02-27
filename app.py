# -*- coding: utf-8 -*-


import os
import sys
from argparse import ArgumentParser

from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage
from pyngrok import ngrok  #  pyngrok 函式庫，用於 Ngrok 隧道

app = Flask(__name__)

#  從環境變數或直接設定取得 LINE Channel Secret 和 Access Token
# **注意:  機密資訊不應直接寫在程式碼中，此處僅為範例**
channel_secret = "<channel_secret>"  #  請替換為你的 channel secret
channel_access_token = "<channel_access_token>"  #  請替換為你的 channel access token
ngrok_auth_token = "<ngrok_auth_token>"  #  請替換為你的 ngrok auth token



#  設定 Webhook Handler
handler = WebhookHandler(channel_secret)

#  設定 LINE Messaging API Client
configuration = Configuration(access_token=channel_access_token)

#  Webhook 回調路由，接收 LINE Server 的 POST 請求
@app.route("/callback", methods=['POST'])
def callback():
    #  取得 HTTP Header 中的 X-Line-Signature，驗證請求來源
    signature = request.headers['X-Line-Signature']

    #  取得請求內容
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    #  處理 Webhook 請求
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)  #  驗證失敗，回傳 400 Bad Request

    return 'OK'  #  成功接收，回傳 'OK'

#  處理文字訊息事件
@handler.add(MessageEvent, message=TextMessageContent)
def message_text(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        #  回覆訊息
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=event.message.text)] #  直接回覆使用者傳來的文字訊息
            )
        )

#  主程式
if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', default=8000, help='port') #  設定 Port，預設為 8000
    arg_parser.add_argument('-d', '--debug', default=False, help='debug') #  設定 Debug 模式
    options = arg_parser.parse_args()

    ngrok.set_auth_token(ngrok_auth_token) 

    #  使用 pyngrok 建立 Ngrok 隧道
    public_url = ngrok.connect(options.port).public_url
    print(f"Ngrok 隧道 URL: {public_url}/callback")
    print("請將此 Ngrok URL 設定到 LINE Developers Console 的 Webhook URL 設定")
    #  **請將此 Ngrok URL 設定到 LINE Developers Console 的 Webhook URL 設定**


    #  啟動 Flask 應用程式
    app.run(debug=options.debug, port=options.port)



#  Ngrok 使用說明:
#  -----------------------------------
#  本機測試 LINE Bot 需使用 Ngrok 將本機伺服器公開至網際網路。
#  此版本使用 pyngrok 自動啟動 Ngrok 隧道。

#  1. 安裝依賴套件:
#     - pip install -R requirements.txt

#  2. 取得 Ngrok Auth Token:
#     - 前往 ngrok 儀表板 (https://dashboard.ngrok.com/login) 並登入
#     - 在左側選單中，找到 "Your Authtoken" (或 "Account" -> "Settings" -> "Your Authtoken")
#     - 複製你的 Auth Token

#  3. 將 Auth Token 加入程式碼:
#     - 將步驟 2 複製的 Auth Token  貼到程式碼中的  `ngrok.set_auth_token("YOUR_AUTH_TOKEN")`  的引號中，取代  `YOUR_AUTH_TOKEN`

#  4. 設定 LINE Channel Secret 和 Access Token:
#     - 請替換程式碼中的 `<channel_secret>` 和 `<channel_access_token>` 為你的 LINE Bot 的 Channel Secret 和 Access Token

#  5. 執行 Python 程式:
#     - 在終端機執行: python your_script_name.py

#  6. 複製 Ngrok HTTPS URL:
#     - 程式執行後，終端機將印出 Ngrok 隧道 URL (例如： https://xxxxxx.ngrok-free.app)
#     - 複製此 URL

#  7. 設定 LINE Developers Console Webhook URL:
#     - 開啟 LINE Developers Console (https://developers.line.biz/console/)
#     - 選擇你的 LINE Bot 服務
#     - 進入 "Webhook" 設定頁面
#     - 將 "Webhook URL" 設定為複製的 Ngrok HTTPS URL，並加上 "/callback" (例如： https://xxxxxx.ngrok-free.app/callback)
#     - 啟用 "Use webhook"
#     - 按下 "Verify" 按鈕，確認 Webhook URL 設定正確

#  完成以上步驟，LINE Bot 即可透過 pyngrok 隧道連線到本機伺服器進行測試!