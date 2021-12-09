from flask import Flask, request, abort
import os

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    CarouselColumn, CarouselTemplate, 
    FollowEvent, MessageEvent, TextMessage, TextSendMessage, TemplateSendMessage,
    PostbackTemplateAction
)

app = Flask(__name__)

# 環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

# ブラウザでherokuにアクセスした場合の処理
@app.route("/")
def hello_world():
    return "hello world!"

# LINEからメッセージを受け取った場合の処理
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        # 署名を検証し、問題なければhandleに定義されている関数を呼び出す
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# フォローイベントの場合の処理
@handler.add(FollowEvent)
def handle_follow(event):
    profile = line_bot_api.get_profile(event.source.user_id)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=profile.display_name + "さん、はじめまして！\n" +
        "友だち追加ありがとうございます。ナビふくくん(仮)です。\n" +
        "まずは窓口の分野を選択するか、キーワードを入力してください。")
    )

# メッセージイベントの場合の処理
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    content = event.message.text # メッセージの内容を取得する
    if content in ['カテゴリ選択']:
        carousel_columns = [
            CarouselColumn(
                text='カテゴリを選択してください',
                title='カテゴリ選択',
                actions=[
                    PostbackTemplateAction(
                        label='医療・保健・福祉関連',
                        data='callback',
                        text='医療・保健・福祉関連'
                        
                    ),
                    PostbackTemplateAction(
                        label='震災・復旧・復興関連',
                        data='callback',
                        text='震災・復旧・復興関連'
                    ),
                    PostbackTemplateAction(
                        label='生活関連',
                        data='callback',
                        text='生活関連'
                    )
                ]
            ),
            CarouselColumn(
                text='カテゴリを選択してください',
                title='カテゴリ選択',
                actions=[
                    PostbackTemplateAction(
                        label='環境関連',
                        data='callback',
                        text='環境関連'
                    ),
                    PostbackTemplateAction(
                        label='産業・労働・就業関連',
                        data='callback',
                        text='産業・労働・就業関連'
                    ),
                    PostbackTemplateAction(
                        label='警察・犯罪関連',
                        data='callback',
                        text='警察・犯罪関連'
                    )
                ]
            ),
            CarouselColumn(
                text='カテゴリを選択してください',
                title='カテゴリ選択',
                actions=[
                    PostbackTemplateAction(
                        label='パスポート・外国人関連',
                        data='callback',
                        text='パスポート・外国人関連'
                    ),
                    PostbackTemplateAction(
                        label='教育関連',
                        data='callback',
                        text='教育関連'
                    ),
                    PostbackTemplateAction(
                        label='県政相談',
                        data='callback',
                        text='県政相談'
                    )
                ]
            )
        ]
        message_template = CarouselTemplate(columns=carousel_columns)
        line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(alt_text='carousel template', template=message_template)
        )
    elif content in ['医療・保健・福祉関連']:
        carousel_columns = [
            CarouselColumn(
                text = '分野を選択してください',
                title = '分野選択',
                actions = [
                    PostbackTemplateAction(
                        label = '保険・福祉',
                        date = 'callback',
                        text = '保険・福祉'
                    ),
                    PostbackTemplateAction(
                        label = '救急・医療',
                        date = 'callback',
                        text = '救急・医療'
                    ),
                    PostbackTemplateAction(
                        label = '障がい者',
                        date = 'callback',
                        text = '障がい者'
                    )
                ]
            ),
            CarouselColumn(
                text = '分野を選択してください',
                title = '分野選択',
                actions =[
                    PostbackTemplateAction(
                        label = '精神',
                        date = 'callback',
                        text = '精神'
                    ),
                    PostbackTemplateAction(
                        label = '女性',
                        date = 'callback',
                        text = '女性'
                    ),
                    PostbackTemplateAction(
                        label = '健康・生活',
                        date = 'callback',
                        text = '健康・生活'
                    )
                ]
            )
        ]
        message_template = CarouselTemplate(columns=carousel_columns)
        line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(alt_text='carousel template', template=message_template)
        )

    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content)) # 受け取った文字列をそのまま返す

if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT"))
    app.run(host="0.0.0.0", port=port)