##### 実際のサーバー側の処理 #####
import os
import sqlite3
# flaskのBlueprintを使って実装
from flask import Blueprint, render_template, request, redirect, url_for, send_from_directory, session
from werkzeug import secure_filename
# ディープラーニングの予測処理を行うpredictモジュール
from vegechecker.net.predict import predict

# Blueprintのアプリケーションを設定。checkという名前で読み込んでいる
app = Blueprint('check', __name__, template_folder='templates', static_folder="./static", static_url_path="/static")

# アップロードされたファイルが置かれる場所を設定。アップロードされた画像はuploadsに置かれる
upload_dir = './uploads'
# アップロードできる画像形式の種類を設定
allowed_extensions = set(['png', 'jpg', 'gif'])
# アプリケーションのコンフィグを設定。コンフィグは辞書で管理（コンフィグが増えた時に便利なように辞書で持っておく）
config = {}
# アップロードするディレクトリをupload_dirで引けるように辞書に登録
config['upload_dir'] = upload_dir

# アップロードされたファイルが指定された画像形式に合っているかどうかを読む
# allowed_fileがTrueの時にアップロードが成功するように後で書く
def allowed_file(filename):
    # allowed_file関数ではファイル名に拡張子がついていて、ファイル名がpng, jpg, gifである時にTrueを返す
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in allowed_extensions

# ここからがflaskを用いたアプリケーションのapiを叩く処理になる
# アプリケーションのトップにアクセスされた時の処理
@app.route("/")
# トップページにアクセスされるとdef indexが実行される
def index():
    # render_template関数はテンプレートに対してメッセージや文字列などを渡すことができる
    return render_template('index.html')

# static_file関数で動的に変わらない静的コンテンツを出力する処理（今回は無い）
@app.route('/<path:path>')
def static_file(path):
    return app.send_static_file(path)

# index.htmlの一番上のファイルを選択ボタンが押された時の処理
# apiはホストのパスで示される（apiはapiであることを示し、v1はバージョン番号、実際のapiの名前はsend）
# POSTの時はif文の中が実行されて、GETの時はelseが実行される
@app.route('/api/v1/send', methods=['GET', 'POST'])
def send():
        # POSTリクエストの中にあるimg_fileを取り出している
    if request.method == 'POST':
        # img_fileは最初のファイル選択のインプットボタンで押されたファイルについてそのパスを取り出している
        img_file = request.files['img_file']
        # 取り出したイメージファイルがアップロードできる形式png, jpg, gifであるか確かめている
        if img_file and allowed_file(img_file.filename):
            filename = secure_filename(img_file.filename)
        # img_file.saveメソッドを呼んで、このイメージファイルをサーバーのupload_dirのフォルダに保存している
            img_file.save(os.path.join(config['upload_dir'], filename))
            # Webページに送る画像のURLをここで指定している
            img_url = '/uploads/' + filename
            # index.htmlを再描画（画像ファイルのURLのimg_urlと画像ファイルの名前filenameを渡す
            return render_template('index.html', img_url=img_url, filename=filename)
        else:
            return ''' <p>許可されていない拡張子です</p> '''
    else:
        # アプリケーションのトップにリダイレクト
        return redirect(url_for(''))

# 画像を認識するためのvegecheckボタンが押されると下記のapiがたたかれる（<filename>はボタンで送られたファイルネームが入る）
@app.route('/api/v1/check/<filename>', methods=['GET', 'POST'])
# POSTの時にif文の中が実行される
def check(filename):
    if request.method == 'POST':
        # ファイルネームを画像URLの形に戻している
        img_url = '/uploads/' + filename
        # predict関数を呼んで、このファイルをディープラーニングで認識するという関数を書いている
        vege_type = predict(filename)
        # index.htmlを再描画する（画像ファイルのURLのimg_urlと認識した野菜の種類を渡す
        return render_template('index.html', img_url=img_url, vege_type=vege_type)
    else:
        return redirect(url_for(''))

# # アップロードした画像を確認するためのapi（画像を表示するときに<filename>で指定された画像をsend_from_directoryでアップロードファイルから送っている
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(config['upload_dir'], filename)

if __name__ == '__main__':
    app.debug = True
    app.run()
