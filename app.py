##### アプリケーションのメイン関数 #####
from flask import Flask
# チェックというコントローラーをインポート
from vegechecker.controllers import check

# フラスクのアプリケーションを作る
app = Flask(__name__)
# チェックを登録する
app.register_blueprint(check.app)

# 起動する
if __name__ == "__main__":
    # 実行（全てのホストから見えるように0.0.0.0を指定）
    app.run(host='0.0.0.0')
