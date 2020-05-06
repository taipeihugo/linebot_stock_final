from flask import Flask, request, abort
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import *
import mongodb

import re

app = Flask(__name__)

line_bot_api = LineBotApi('/u+KR9NmRg9UVRk8NWvx578eKypyJUOaXrSltxJaKtY7hHTIM/UY5Nj9jm1vNNbsODDCxVM6HPftyh9oyTL/oFBuBtBI5cS3j/lWsfaWBu1Ea7OclWBxJnWWk10XyMogmtsyYvX60c9RFwSyRlLCwwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('3a3ec40cb756d1640f70aa711372e431')
line_bot_api.push_message('U1d4e838208d0f278714d687538a07600', TextSendMessage(text='-股票小助手已開始運作-'))

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

#訊息傳遞區塊
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    ### 抓到顧客的資料 ###
    profile = line_bot_api.get_profile(event.source.user_id)
    uid = profile.user_id #使用者ID
    usespeak=str(event.message.text) #使用者講的話
    
    
    if re.match('[0-9]{4}[<>][0-9]',usespeak): # 先判斷是否是使用者要用來存股票的
        StockCompany = mongodb.Name_Stock(usespeak[0:4])
        mongodb.write_user_stock_fountion(stock=usespeak[0:4], bs=usespeak[4:5], price=usespeak[5:])
        line_bot_api.push_message(uid, TextSendMessage(StockCompany+' :已經儲存成功'))
        return 0

    
    elif re.match('刪除[0-9]{4}',usespeak): # 刪除存在資料庫裡面的股票
        mongodb.delete_user_stock_fountion(stock=usespeak[2:])
        line_bot_api.push_message(uid, TextSendMessage(usespeak+'已經刪除成功'))
        return 0
    
    elif event.message.text == "apple":
        buttons_template = TemplateSendMessage(
        alt_text='Buttons Template',
        template=ButtonsTemplate(
            title='這是ButtonsTemplate',
            text='ButtonsTemplate可以傳送text,uri',
            thumbnail_image_url='顯示在開頭的大圖片網址',
            actions=[
                MessageTemplateAction(
                    label='ButtonsTemplate',
                    text='ButtonsTemplate'
                ),
                URITemplateAction(
                    label='VIDEO1',
                    uri='影片網址'
                ),
                PostbackTemplateAction(
                    label='postback',
                    text='postback text',
                    data='postback1'
                )
            ]
        )
    )
    line_bot_api.push_message(uid, buttons_template)



if __name__ == '__main__':
    app.run(debug=True)
