from flask import Flask, request, abort
import os
import psycopg2

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
DATABASE_URL = os.environ.get('DATABASE_URL')

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

# データベースの表の出力
@app.route("/database")
def database():
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as curs:
            curs.execute("SELECT * FROM window_list ORDER BY Id ASC")
            curs.fetchall()
    return "database page"

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
                        data = 'callback',
                        text = '保険・福祉'
                    ),
                    PostbackTemplateAction(
                        label = '救急・医療',
                        data = 'callback',
                        text = '救急・医療'
                    ),
                    PostbackTemplateAction(
                        label = '障がい者',
                        data = 'callback',
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
                        data = 'callback',
                        text = '精神'
                    ),
                    PostbackTemplateAction(
                        label = '女性',
                        data = 'callback',
                        text = '女性'
                    ),
                    PostbackTemplateAction(
                        label = '健康・生活',
                        data = 'callback',
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

    elif content in ['震災・復旧・復興関連']:
        carousel_columns = [
            CarouselColumn(
                text = '分野を選択してください',
                title = '分野選択',
                actions = [
                    PostbackTemplateAction(
                        label = '原発',
                        data = 'callback',
                        text = '原発'
                    ),
                    PostbackTemplateAction(
                        label = '生活',
                        data = 'callback',
                        text = '生活'
                    )
                ]
            ),
            CarouselColumn(
                text = '分野を選択してください',
                title = '分野選択',
                actions = [
                    PostbackTemplateAction(
                        label = '企業・経営',
                        data = 'callback',
                        text = '企業・経営'
                    ),
                    PostbackTemplateAction(
                        label = '復興支援',
                        data = 'callback',
                        text = '復興支援'
                    )
                ]
            )
        ]
        message_template = CarouselTemplate(columns=carousel_columns)
        line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(alt_text='carousel template', template=message_template)
        )

    elif content in ['生活関連']:
        carousel_columns = [
            CarouselColumn(
                text = '分野を選択してください',
                title = '分野選択',
                actions = [
                    PostbackTemplateAction(
                        label = '事故',
                        data = 'callback',
                        text = '事故'
                    ),
                    PostbackTemplateAction(
                        label = '生活・人間関係',
                        data = 'callback',
                        text = '生活・人間関係'
                    ),  
                ]
            ),
            CarouselColumn(
                text = '分野を選択してください',
                title = '分野選択',
                actions = [
                    PostbackTemplateAction(
                        label = '食品・安全',
                        data = 'callback',
                        text = '食品・安全'
                    ),
                    PostbackTemplateAction(
                        label = 'その他',
                        data = 'callback',
                        text = 'その他'
                    )
                ]
            )
        ]
        message_template = CarouselTemplate(columns=carousel_columns)
        line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(alt_text='carousel template', template=message_template)
        )

    elif content in ['環境関連']:
        carousel_columns = [
            CarouselColumn(
                text = '分野を選択してください',
                title = '分野選択',
                actions = [
                    PostbackTemplateAction(
                        label = '環境問題',
                        data = 'callback',
                        text = '環境問題'
                    ),
                    PostbackTemplateAction(
                        label = '公害・廃棄物',
                        data = 'callback',
                        text = '公害・廃棄物'
                    ),
                    PostbackTemplateAction(
                        label = '環境保全活動',
                        data = 'callback',
                        text = '環境保全活動'
                    )
                ]
            )
        ]
        message_template = CarouselTemplate(columns=carousel_columns)
        line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(alt_text='carousel template', template=message_template)
        )

    elif content in ['産業・労働・就業関連']:
        carousel_columns = [
            CarouselColumn(
                text = '分野を選択してください',
                title = '分野選択',
                actions = [
                    PostbackTemplateAction(
                        label = '労働環境',
                        data = 'callback',
                        text = '労働環境'
                    ),
                    PostbackTemplateAction(
                        label = '経営',
                        data = 'callback',
                        text = '経営'
                    ),
                    PostbackTemplateAction(
                        label = '産業',
                        data = 'callback',
                        text = '産業'
                    )
                ]
            )
        ]
        message_template = CarouselTemplate(columns=carousel_columns)
        line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(alt_text='carousel template', template=message_template)
        )

    elif content in ['警察・犯罪関連']:
        carousel_columns = [
            CarouselColumn(
                text = '分野を選択してください',
                title = '分野選択',
                actions = [
                    PostbackTemplateAction(
                        label = '安全相談',
                        data = 'callback',
                        text = '安全相談'
                    ),
                    PostbackTemplateAction(
                        label = '交通安全',
                        data = 'callback',
                        text = '交通安全'
                    )
                ]
            ),
            CarouselColumn(
                text = '分野を選択してください',
                title = '分野選択',
                actions = [
                    PostbackTemplateAction(
                        label = 'いじめ・子ども相談',
                        data = 'callback',
                        text = 'いじめ・子ども相談'
                    ),
                     PostbackTemplateAction(
                        label = '犯罪関連',
                        data = 'callback',
                        text = '犯罪関連'
                    )
                ]
            )
        ]
        message_template = CarouselTemplate(columns=carousel_columns)
        line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(alt_text='carousel template', template=message_template)
        )
    
    elif content in ['パスポート関係・外国人向け']:
        carousel_columns = [
            CarouselColumn(
                text = '分野を選択してください',
                title = '分野選択',
                actions = [
                    PostbackTemplateAction(
                        label = 'パスポート',
                        data = 'callback',
                        text = 'パスポート'
                    ),
                    PostbackTemplateAction(
                        label = '外国人向け相談窓口',
                        data = 'callback',
                        text = '外国人向け相談窓口'
                    )
                ]
            )
        ]
        message_template = CarouselTemplate(columns=carousel_columns)
        line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(alt_text='carousel template', template=message_template)
        )

    elif content in ['教育関連']:
        carousel_columns = [
            CarouselColumn(
                text = '分野を選択してください',
                title = '分野選択',
                actions = [
                    PostbackTemplateAction(
                        label = '教育相談',
                        data = 'callback',
                        text = '教育相談'
                    ),
                    PostbackTemplateAction(
                        label = '障がい児関連',
                        data = 'callback',
                        text = '障がい児関連'
                    ),
                    PostbackTemplateAction(
                        label = '調査・文化財',
                        data = 'callback',
                        text = '調査・文化財'
                    )
                ]
            )
        ]
        message_template = CarouselTemplate(columns=carousel_columns)
        line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(alt_text='carousel template', template=message_template)
        )

    elif content in ['産業']:
        carousel_columns = [
            CarouselColumn(
                text = '分野を選択してください',
                title = '分野選択',
                actions = [
                    PostbackTemplateAction(
                        label = '農林水産業',
                        data = 'callback',
                        text = '農林水産業'
                    ),
                    PostbackTemplateAction(
                        label = 'テクノロジー',
                        data = 'callback',
                        text = 'テクノロジー'
                    ),
                    
                ]
            )
        ]
        message_template = CarouselTemplate(columns=carousel_columns)
        line_bot_api.reply_message(
            event.reply_token,
            TemplateSendMessage(alt_text='carousel template', template=message_template)
        )

    elif content in ['障がい児関連']:
        carousel_columns = [
            CarouselColumn(
                text = '分野を選択してください',
                title = '分野選択',
                actions = [
                    PostbackTemplateAction(
                        label = '視覚障がい',
                        data = 'callback',
                        text = '視覚障がい'
                    ),
                    PostbackTemplateAction(
                        label = '聴覚障がい',
                        data = 'callback',
                        text = '聴覚障がい'
                    ),
                    PostbackTemplateAction(
                        label = '肢体不自由',
                        data = 'callback',
                        text = '肢体不自由'
                    )
                ]
            ),
            CarouselColumn(
                text = '分野を選択してください',
                title = '分野選択',
                actions = [
                    PostbackTemplateAction(
                        label = '病弱障がい',
                        data = 'callback',
                        text = '病弱障がい'
                    ),
                    PostbackTemplateAction(
                        label = '知的障がい',
                        data = 'callback',
                        text = '知的障がい'
                    ),
                    PostbackTemplateAction(
                        label = 'LD・ADHD等',
                        data = 'callback',
                        text = 'LD・ADHD等'
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