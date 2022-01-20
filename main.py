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
    BubbleContainer, CarouselContainer, BoxComponent, TextComponent, ButtonComponent, MessageAction,
    FollowEvent, MessageEvent, TextMessage, TextSendMessage, TemplateSendMessage, FlexSendMessage,
    PostbackAction, PostbackTemplateAction
)

app = Flask(__name__)

# 環境変数取得
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]
DATABASE_URL = os.environ.get('DATABASE_URL')

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)

# 窓口リストを表示する関数
# Pythonでは呼び出す行より上に記述しないとエラーになる
# def window_list(db):
    # result = "窓口一覧\n"
    # for row in db: 
    #     result += "・" + row[3] + "\n"
    # result += "・見つからない場合はこちら"
    # return result

# リストをn個ずつのサブリストに分割する
# l : リスト
# n : サブリストの要素数
def split_list(l, n):
    for idx in range(0, len(l), n):
        yield l[idx:idx + n]

# 窓口一覧表示 (テキスト)
def window_list(db):
    db.append(
        (1,1,1,
        '見つからない場合はこちら',
        '県の総合的な相談窓口',
        '県庁県政相談コーナー',
        '0120-899-721\nkenseisoudan@pref.fukushima.lg.jp',
        '月～金\n9:00～12:00\n13:00～16:00\n(祝日、年末年始を除く)',
        0,'2021-12-10 02:37:02.388856')
        )
    db_column = list(split_list(db, 7))
    
    result = "窓口一覧\n"
    for dbcol in db_column:
        for row in dbcol:
            result += "・" + row[3] + "\n"
        result += "----------\n"
    result += "・見つからない場合はこちら"
    return result

# 窓口一覧表示 (フレックスボックス)
def window_list_flex(db):
    db.append(
        (1,1,1,
        '見つからない場合はこちら',
        '県の総合的な相談窓口',
        '県庁県政相談コーナー',
        '0120-899-721\nkenseisoudan@pref.fukushima.lg.jp',
        '月～金\n9:00～12:00\n13:00～16:00\n(祝日、年末年始を除く)',
        0,'2021-12-10 02:37:02.388856')
        )
    db_column = list(split_list(db, 10))

    contents_carousel = []
    contents_button = []
    for dbcol in db_column:
        for row in dbcol:
            contents_button.append(
                ButtonComponent(
                    style = 'link',
                    height = 'sm',
                    action = PostbackAction(
                        label = str(row[3])[:40],
                        data = 'callback',
                        text = '窓口ID:' + str(row[0])
                    )
                )
            )
        contents_carousel.append(
            CarouselContainer(
                contents = [
                    BubbleContainer(
                        header = BoxComponent(
                            layout = 'vertical',
                            contents = [ 
                                TextComponent(
                                    text = '窓口を選択してください',
                                    weight = 'bold',
                                    color = '#333333',
                                    size = 'xl'
                                )
                            ]
                        ),
                        body = BoxComponent(
                            layout = 'vertical',
                            contents = contents_button
                        )
                    )
                ]
            )
        )

# 窓口の情報を出力
def window_info(db):
    result = "お探しの窓口はこちらですか？\n"\
        + db[0][3] + "\n"\
        + db[0][5] + "\n"\
        + db[0][6] + "\n"\
        + db[0][7]
    return result

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
            db = curs.fetchall()
            result = "<table>\
             <tr>\
              <th>Id</th>\
              <th>Category</th>\
              <th>Number</th>\
              <th>Soudan_name</th>\
              <th>Soudan_content</th>\
              <th>Window_name</th>\
              <th>tel</th>\
              <th>Business_hours</th>\
              <th>Subcategory</th>\
              <th>Timestamp</th>\
             </tr>"
            for row in db: 
                result += "<tr>\
                    <td>" + str(row[0]) + "</td>\
                    <td>" + str(row[1]) + "</td>\
                    <td>" + str(row[2]) + "</td>\
                    <td>" + str(row[3]) + "</td>\
                    <td>" + str(row[4]) + "</td>\
                    <td>" + str(row[5]) + "</td>\
                    <td>" + str(row[6]) + "</td>\
                    <td>" + str(row[7]) + "</td>\
                    <td>" + str(row[8]) + "</td>\
                    <td>" + str(row[9]) + "</td>\
                    </tr>"
            result += "</table>"
    return result

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

    # 以下サブカテゴリ
    elif content in ['保険・福祉']:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as curs:
                curs.execute("SELECT * FROM window_list WHERE subcategory = 21 ORDER BY Id ASC")
                db = curs.fetchall()

        result = CarouselContainer(
            contents = [
                BubbleContainer(
                    header = BoxComponent(
                        layout = 'vertical',
                        contents = [ 
                            TextComponent(
                                text = '窓口を選択してください',
                                weight = 'bold',
                                color = '#333333',
                                size = 'xl'
                            )
                        ]
                    ),
                    body = BoxComponent(
                        layout = 'vertical',
                        contents = [ 
                            ButtonComponent(
                                style = 'link',
                                height = 'sm',
                                action = PostbackAction(
                                    label = str(db[0][3])[:40],
                                    data = 'callback',
                                    text = '窓口' + str(db[0][0])
                                )
                            ),
                            ButtonComponent(
                                style = 'link',
                                height = 'sm',
                                action = PostbackAction(
                                    label = str(db[1][3])[:40],
                                    data = 'callback',
                                    text = '窓口' + str(db[1][0])
                                )
                            ),
                            ButtonComponent(
                                style = 'link',
                                height = 'sm',
                                action = PostbackAction(
                                    label = str(db[2][3])[:40],
                                    data = 'callback',
                                    text = '窓口' + str(db[2][0])
                                )
                            ),
                            ButtonComponent(
                                style = 'link',
                                height = 'sm',
                                action = PostbackAction(
                                    label = str(db[3][3])[:40],
                                    data = 'callback',
                                    text = '窓口' + str(db[3][0])
                                )
                            ),
                            ButtonComponent(
                                style = 'link',
                                height = 'sm',
                                action = PostbackAction(
                                    label = str(db[4][3])[:40],
                                    data = 'callback',
                                    text = '窓口' + str(db[4][0])
                                )
                            ),
                            ButtonComponent(
                                style = 'link',
                                height = 'sm',
                                action = PostbackAction(
                                    label = str(db[5][3])[:40],
                                    data = 'callback',
                                    text = '窓口' + str(db[5][0])
                                )
                            ),
                            ButtonComponent(
                                style = 'link',
                                height = 'sm',
                                action = PostbackAction(
                                    label = str(db[6][3])[:40],
                                    data = 'callback',
                                    text = '窓口' + str(db[6][0])
                                )
                            ),
                            ButtonComponent(
                                style = 'link',
                                height = 'sm',
                                action = PostbackAction(
                                    label = str(db[7][3])[:40],
                                    data = 'callback',
                                    text = '窓口' + str(db[7][0])
                                )
                            ),
                            ButtonComponent(
                                style = 'link',
                                height = 'sm',
                                action = PostbackAction(
                                    label = str(db[8][3])[:40],
                                    data = 'callback',
                                    text = '窓口' + str(db[8][0])
                                )
                            ),
                            ButtonComponent(
                                style = 'link',
                                height = 'sm',
                                action = PostbackAction(
                                    label = str(db[9][3])[:40],
                                    data = 'callback',
                                    text = '窓口' + str(db[9][0])
                                )
                            )
                        ]
                    )
                ),
                BubbleContainer(
                    header = BoxComponent(
                        layout = 'vertical',
                        contents = [ 
                            TextComponent(
                                text = '窓口を選択してください',
                                weight = 'bold',
                                color = '#333333',
                                size = 'xl'
                            )
                        ]
                    ),
                    body = BoxComponent(
                        layout = 'vertical',
                        contents = [ 
                            ButtonComponent(
                                style = 'link',
                                height = 'sm',
                                action = PostbackAction(
                                    label = str(db[10][3])[:40],
                                    data = 'callback',
                                    text = '窓口' + str(db[10][0])
                                )
                            ),
                            ButtonComponent(
                                style = 'link',
                                height = 'sm',
                                action = PostbackAction(
                                    label = str(db[11][3])[:40],
                                    data = 'callback',
                                    text = '窓口' + str(db[11][0])
                                )
                            ),
                            ButtonComponent(
                                style = 'link',
                                height = 'sm',
                                action = PostbackAction(
                                    label = str(db[12][3])[:40],
                                    data = 'callback',
                                    text = '窓口' + str(db[12][0])
                                )
                            ),
                            ButtonComponent(
                                style = 'link',
                                height = 'sm',
                                action = PostbackAction(
                                    label = str(db[13][3])[:40],
                                    data = 'callback',
                                    text = '窓口' + str(db[13][0])
                                )
                            ),
                            ButtonComponent(
                                style = 'link',
                                height = 'sm',
                                action = PostbackAction(
                                    label = str(db[14][3])[:40],
                                    data = 'callback',
                                    text = '窓口' + str(db[14][0])
                                )
                            ),
                            ButtonComponent(
                                style = 'link',
                                height = 'sm',
                                action = PostbackAction(
                                    label = str(db[15][3])[:40],
                                    data = 'callback',
                                    text = '窓口' + str(db[15][0])
                                )
                            ),
                            ButtonComponent(
                                style = 'link',
                                height = 'sm',
                                action = PostbackAction(
                                    label = str(db[16][3])[:40],
                                    data = 'callback',
                                    text = '窓口' + str(db[16][0])
                                )
                            ),
                            ButtonComponent(
                                style = 'link',
                                height = 'sm',
                                action = PostbackAction(
                                    label = str(db[17][3])[:40],
                                    data = 'callback',
                                    text = '窓口' + str(db[17][0])
                                )
                            ),
                            ButtonComponent(
                                style = 'link',
                                height = 'sm',
                                action = PostbackAction(
                                    label = str(db[18][3])[:40],
                                    data = 'callback',
                                    text = '窓口' + str(db[18][0])
                                )
                            ),
                            ButtonComponent(
                                style = 'link',
                                height = 'sm',
                                action = PostbackAction(
                                    label = str(db[19][3])[:40],
                                    data = 'callback',
                                    text = '窓口' + str(db[19][0])
                                )
                            )
                        ]
                    )
                ),
                BubbleContainer(
                    header = BoxComponent(
                        layout = 'vertical',
                        contents = [ 
                            TextComponent(
                                text = '窓口を選択してください',
                                weight = 'bold',
                                color = '#333333',
                                size = 'xl'
                            )
                        ]
                    ),
                    body = BoxComponent(
                        layout = 'vertical',
                        contents = [ 
                            ButtonComponent(
                                style = 'link',
                                height = 'sm',
                                action = PostbackAction(
                                    label = str(db[0][3])[:40],
                                    data = 'callback',
                                    text = '窓口' + str(db[20][0])
                                )
                            ),
                            ButtonComponent(
                                style = 'link',
                                height = 'sm',
                                action = PostbackAction(
                                    label = str(db[1][3])[:40],
                                    data = 'callback',
                                    text = '窓口' + str(db[21][0])
                                )
                            )
                        ]
                    )
                )

            ]
        )

        line_bot_api.reply_message(
            event.reply_token,
            FlexSendMessage(alt_text='flex template', contents=result)
        )

    elif content in ['救急・医療']:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as curs:
                curs.execute("SELECT * FROM window_list WHERE subcategory = 22 ORDER BY Id ASC")
                db = curs.fetchall()

        result = window_list_flex(db)
        
        line_bot_api.reply_message(
            event.reply_token,
            FlexSendMessage(alt_text='flex template', contents=result)
        )

    elif content in ['障がい者']:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as curs:
                curs.execute("SELECT * FROM window_list WHERE subcategory = 23 ORDER BY Id ASC")
                db = curs.fetchall()

        result = window_list(db)
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=result))

    elif content in ['精神']:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as curs:
                curs.execute("SELECT * FROM window_list WHERE subcategory = 24 ORDER BY Id ASC")
                db = curs.fetchall()

        result = window_list(db)
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=result))
    
    elif content in ['女性']:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as curs:
                curs.execute("SELECT * FROM window_list WHERE subcategory = 25 ORDER BY Id ASC")
                db = curs.fetchall()

        result = window_list(db)
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=result))

    elif content in ['健康・生活']:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as curs:
                curs.execute("SELECT * FROM window_list WHERE subcategory = 26 ORDER BY Id ASC")
                db = curs.fetchall()
        
        result = window_list(db)
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=result))

    elif content in ['原発']:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as curs:
                curs.execute("SELECT * FROM window_list WHERE subcategory = 31 ORDER BY Id ASC")
                db = curs.fetchall()

        result = window_list(db)
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=result))

    elif content in ['生活']:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as curs:
                curs.execute("SELECT * FROM window_list WHERE subcategory = 32 ORDER BY Id ASC")
                db = curs.fetchall()

        result = window_list(db)
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=result))

    elif content in ['企業・経営']:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as curs:
                curs.execute("SELECT * FROM window_list WHERE subcategory = 33 ORDER BY Id ASC")
                db = curs.fetchall()

        result = window_list(db)
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=result))

    elif content in ['復興支援']:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as curs:
                curs.execute("SELECT * FROM window_list WHERE subcategory = 34 ORDER BY Id ASC")
                db = curs.fetchall()

        result = window_list(db)
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=result))

    elif content in ['事故']:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as curs:
                curs.execute("SELECT * FROM window_list WHERE subcategory = 41 ORDER BY Id ASC")
                db = curs.fetchall()

        result = window_list(db)
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=result))

    elif content in ['生活・人間関係']:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as curs:
                curs.execute("SELECT * FROM window_list WHERE subcategory = 42 ORDER BY Id ASC")
                db = curs.fetchall()

        result = window_list(db)
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=result))

    elif content in ['食品・安全']:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as curs:
                curs.execute("SELECT * FROM window_list WHERE subcategory = 43 ORDER BY Id ASC")
                db = curs.fetchall()

        result = window_list(db)
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=result))

    elif content in ['その他']:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as curs:
                curs.execute("SELECT * FROM window_list WHERE subcategory = 44 ORDER BY Id ASC")
                db = curs.fetchall()

        result = window_list(db)
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=result))

    elif content in ['環境問題']:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as curs:
                curs.execute("SELECT * FROM window_list WHERE subcategory = 51 ORDER BY Id ASC")
                db = curs.fetchall()

        result = window_list(db)
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=result))

    elif content in ['公害・廃棄物']:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as curs:
                curs.execute("SELECT * FROM window_list WHERE subcategory = 52 ORDER BY Id ASC")
                db = curs.fetchall()

        result = window_list(db)
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=result))

    elif content in ['環境保全活動']:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as curs:
                curs.execute("SELECT * FROM window_list WHERE subcategory = 53 ORDER BY Id ASC")
                db = curs.fetchall()

        result = window_list(db)
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=result))

    elif content in ['労働環境']:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as curs:
                curs.execute("SELECT * FROM window_list WHERE subcategory = 71 ORDER BY Id ASC")
                db = curs.fetchall()

        result = window_list(db)
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=result))

    elif content in ['経営']:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as curs:
                curs.execute("SELECT * FROM window_list WHERE subcategory = 72 ORDER BY Id ASC")
                db = curs.fetchall()

        result = window_list(db)
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=result))

    elif content in ['農林水産業']:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as curs:
                curs.execute("SELECT * FROM window_list WHERE subcategory = 731 ORDER BY Id ASC")
                db = curs.fetchall()

        result = window_list(db)
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=result))

    elif content in ['テクノロジー']:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as curs:
                curs.execute("SELECT * FROM window_list WHERE subcategory = 732 ORDER BY Id ASC")
                db = curs.fetchall()

        result = window_list(db)
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=result))

    elif content in ['安全相談']:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as curs:
                curs.execute("SELECT * FROM window_list WHERE subcategory = 81 ORDER BY Id ASC")
                db = curs.fetchall()

        result = window_list(db)
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=result))

    elif content in ['交通安全']:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as curs:
                curs.execute("SELECT * FROM window_list WHERE subcategory = 82 ORDER BY Id ASC")
                db = curs.fetchall()

        result = window_list(db)
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=result))

    elif content in ['いじめ・子ども相談']:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as curs:
                curs.execute("SELECT * FROM window_list WHERE subcategory = 83 ORDER BY Id ASC")
                db = curs.fetchall()

        result = window_list(db)
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=result))

    elif content in ['犯罪関連']:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as curs:
                curs.execute("SELECT * FROM window_list WHERE subcategory = 84 ORDER BY Id ASC")
                db = curs.fetchall()

        result = window_list(db)
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=result))

    elif content in ['パスポート']:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as curs:
                curs.execute("SELECT * FROM window_list WHERE subcategory = 91 ORDER BY Id ASC")
                db = curs.fetchall()

        result = window_list(db)
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=result))

    elif content in ['外国人向け相談窓口']:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as curs:
                curs.execute("SELECT * FROM window_list WHERE subcategory = 101 ORDER BY Id ASC")
                db = curs.fetchall()

        result = window_list(db)
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=result))

    elif content in ['教育相談']:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as curs:
                curs.execute("SELECT * FROM window_list WHERE subcategory = 111 ORDER BY Id ASC")
                db = curs.fetchall()

        result = window_list(db)
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=result))

    elif content in ['視覚障がい']:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as curs:
                curs.execute("SELECT * FROM window_list WHERE subcategory = 1121 ORDER BY Id ASC")
                db = curs.fetchall()

        result = window_list(db)
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=result))

    elif content in ['聴覚障がい']:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as curs:
                curs.execute("SELECT * FROM window_list WHERE subcategory = 1122 ORDER BY Id ASC")
                db = curs.fetchall()

        result = window_list(db)
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=result))

    elif content in ['肢体不自由']:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as curs:
                curs.execute("SELECT * FROM window_list WHERE subcategory = 1123 ORDER BY Id ASC")
                db = curs.fetchall()

        result = window_list(db)
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=result))

    elif content in ['病弱障がい']:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as curs:
                curs.execute("SELECT * FROM window_list WHERE subcategory = 1124 ORDER BY Id ASC")
                db = curs.fetchall()

        result = window_list(db)
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=result))

    elif content in ['知的障がい']:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as curs:
                curs.execute("SELECT * FROM window_list WHERE subcategory = 1125 ORDER BY Id ASC")
                db = curs.fetchall()

        result = window_list(db)
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=result))

    elif content in ['LD・ADHD等']:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as curs:
                curs.execute("SELECT * FROM window_list WHERE subcategory = 1126 ORDER BY Id ASC")
                db = curs.fetchall()

        result = window_list(db)
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=result))

    elif content in ['調査・文化財']:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as curs:
                curs.execute("SELECT * FROM window_list WHERE subcategory = 113 ORDER BY Id ASC")
                db = curs.fetchall()

        result = window_list(db)
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=result))

    elif content in ['県政相談']:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as curs:
                curs.execute("SELECT * FROM window_list WHERE Id = 1")
                db = curs.fetchall()

        result = window_info(db)
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=result))

                                                                 
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content)) # 受け取った文字列をそのまま返す

if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT"))
    app.run(host="0.0.0.0", port=port)
