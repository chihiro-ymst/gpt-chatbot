from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import openai
import os
from dotenv import load_dotenv  # ← これ追加！

load_dotenv()  # ← .envファイルを読み込む！

openai.api_key = os.getenv("OPENAI_API_KEY")  # ← ここで環境変数から読み込み！

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# ✅ サンプルFAQデータ（会社名＋キーワード＋回答）
faq_data = {
    "ヒューマンリンク": {
        "給料日": "ヒューマンリンクでは毎月15日が給料日です。",
        "有給": "有給の申請は専用システムから行ってください。"
    },
    "ネクストスタッフ": {
        "給料日": "ネクストスタッフは月末締め、翌月10日払いです。",
        "有給": "半年以上勤務すると有給が発生します。"
    },
    "サンプル社": {
        "給料日": "サンプル社では毎月25日が給料日です。",
        "有給": "LINEから申請可能です。"
    }
}

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json["message"]
    print("🟡 ユーザーからのメッセージ:", user_input)

    # ✅ 社名を含んでいるかチェック
    matched_company = None
    for company in faq_data:
        if company in user_input:
            matched_company = company
            break

    # ✅ 該当企業のFAQキーワードをチェック
    if matched_company:
        company_faq = faq_data[matched_company]
        for keyword in company_faq:
            if keyword in user_input:
                reply = company_faq[keyword]
                print(f"📚 FAQマッチ: {matched_company} / {keyword} → {reply}")
                return jsonify({"reply": reply})

    # ✅ FAQでマッチしなかった場合はGPTに任せる
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "あなたは派遣会社のスタッフ対応AIです。ユーザーの質問に丁寧に答えてください。"},
            {"role": "user", "content": user_input}
        ]
    )

    reply = response["choices"][0]["message"]["content"]
    print("🧠 GPTの返答:", reply)
    return jsonify({"reply": reply})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(debug=True, host="0.0.0.0", port=port)

    openai.api_key = os.getenv("OPENAI_API_KEY")
