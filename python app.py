import os
import requests
from flask import Flask, request

app = Flask(__name__)

# =========================
# ENV (настраивается в Render → Environment)
# =========================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip()

# Ссылка на бесплатные медитации (можно оставить пустой и позже заполнить)
MEDITATIONS_URL = os.environ.get("MEDITATIONS_URL", "").strip()

# Ссылка на магазин/оплату (Tentary)
TENTARY_URL = os.environ.get("TENTARY_URL", "").strip()

# Фото для приветствия (опционально).
# Можно поставить Telegram file_id или прямую ссылку на картинку (https://...jpg/png)
WELCOME_PHOTO = os.environ.get("WELCOME_PHOTO", "").strip()

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set (Render → Environment → BOT_TOKEN)")

API = f"https://api.telegram.org/bot{BOT_TOKEN}"


# =========================
# Helpers
# =========================
def build_keyboard():
    """URL-кнопки (без callback), чтобы не было багов и лишней логики."""
    keyboard = {"inline_keyboard": []}

    if MEDITATIONS_URL:
        keyboard["inline_keyboard"].append(
            [{"text": "📩 Бесплатные медитации", "url": MEDITATIONS_URL}]
        )

    if TENTARY_URL:
        keyboard["inline_keyboard"].append(
            [{"text": "💳 Купить медитации", "url": TENTARY_URL}]
        )

    return keyboard


def send_welcome(chat_id: int):
    text = (
        "Добро пожаловать в Lexxa Quantum ✨\n\n"
        "Выбери, что нужно сделать:"
    )
    keyboard = build_keyboard()

    # Если фото задано — отправляем фото + кнопки
    if WELCOME_PHOTO:
        requests.post(
            f"{API}/sendPhoto",
            json={
                "chat_id": chat_id,
                "photo": WELCOME_PHOTO,
                "caption": text,
                "reply_markup": keyboard,
            },
            timeout=15,
        )
        return

    # Иначе обычное сообщение + кнопки
    requests.post(
        f"{API}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text,
            "reply_markup": keyboard,
        },
        timeout=15,
    )


# =========================
# Routes
# =========================
@app.get("/")
def index():
    return "Bot is running | CLEAN VERSION", 200


@app.post("/telegram")
def telegram_webhook():
    data = request.json or {}
    msg = data.get("message") or data.get("edited_message")

    if not msg:
        return {"ok": True}

    chat = msg.get("chat") or {}
    chat_id = chat.get("id")
    text = (msg.get("text") or "").strip().lower()

    if chat_id and (text == "/start" or text.startswith("/start ")):
        send_welcome(chat_id)

    return {"ok": True}


# =========================
# Run (Render)
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)
