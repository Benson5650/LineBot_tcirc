# -*- coding: utf-8 -*-


import os
import sys
from argparse import ArgumentParser

from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage

app = Flask(__name__)

#  從環境變數或直接設定取得 LINE Channel Secret 和 Access Token
# **注意:  機密資訊不應直接寫在程式碼中，此處僅為範例**
channel_secret = "67bbfb3746628d07d76750e311669402"  #  請替換為你的 channel secret
channel_access_token = "QLXp1Pm9ybvcU/5ci0lm2sut047Yi+mU8Jnc5yFZQ10yMsegERdpvGnBCQsrFiOZuNLJV//Eo8wkulxpt594Pu6/UzYDu9FMtUUgGo8XAvFg60k010IYeI8+EmP4rLsapWvSCixphulmlLjuk/OKJAdB04t89/1O/w1cDnyilFU="  #  請替換為你的 channel access token

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

    port = options.port
    
    print("=" * 50)
    print(f"Flask 伺服器將在 localhost:{port} 啟動")
    print("請確保您已經啟動了外部的 ngrok 程式，將此 port 暴露在網際網路上")
    print(f"執行命令： ngrok http {port}")
    print("=" * 50)
    print("請將 ngrok 提供的 HTTPS URL 加上 '/callback' 路徑")
    print("例如：https://xxxx-xxxx-xxxx-xxxx.ngrok-free.app/callback")
    print("並將此 URL 設定到 LINE Developers Console 的 Webhook URL")
    print("=" * 50)

    #  啟動 Flask 應用程式
    app.run(debug=options.debug, port=port)


#  外部 Ngrok 使用說明:
#  -----------------------------------
#  本機測試 LINE Bot 需使用 Ngrok 將本機伺服器公開至網際網路。
#  此版本使用外部 ngrok 執行檔而非 pyngrok 函式庫。

#  1. 安裝 ngrok:
#     - 前往 https://ngrok.com/download 下載並安裝 ngrok

#  2. 註冊 Ngrok 帳號並取得 Auth Token:
#     - 前往 ngrok 儀表板 (https://dashboard.ngrok.com/login) 並登入
#     - 在左側選單中，找到 "Your Authtoken"
#     - 複製你的 Auth Token

#  3. 設定 ngrok Auth Token:
#     - 在終端機或命令提示字元中執行: ngrok config add-authtoken <YOUR_AUTH_TOKEN>
#     - 替換 YOUR_AUTH_TOKEN 為你在步驟 2 中複製的令牌

#  4. 設定 LINE Channel Secret 和 Access Token:
#     - 請替換程式碼中的 `<channel_secret>` 和 `<channel_access_token>` 為你的 LINE Bot 的 Channel Secret 和 Access Token

#  5. 啟動 Flask 應用程式:
#     - 在終端機執行: python app_external_ngrok.py
#     - 注意 Flask 使用的端口號 (預設為 8000)

#  6. 在新的終端機視窗啟動 ngrok:
#     - 執行: ngrok http 8000
#     - 如果使用非預設端口，請相應地替換數字

#  7. 複製 Ngrok HTTPS URL:
#     - ngrok 啟動後，終端機將顯示 Forwarding URL
#     - 複製 https 開頭的 URL (例如: https://xxxx-xxxx-xxxx-xxxx.ngrok-free.app)

#  8. 設定 LINE Developers Console Webhook URL:
#     - 開啟 LINE Developers Console (https://developers.line.biz/console/)
#     - 選擇你的 LINE Bot 服務
#     - 進入 "Webhook" 設定頁面
#     - 將 "Webhook URL" 設定為複製的 Ngrok HTTPS URL，並加上 "/callback"
#       (例如: https://xxxx-xxxx-xxxx-xxxx.ngrok-free.app/callback)
#     - 啟用 "Use webhook"
#     - 按下 "Verify" 按鈕，確認 Webhook URL 設定正確

#  完成以上步驟，LINE Bot 即可透過外部 ngrok 隧道連線到本機伺服器進行測試!
