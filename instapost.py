import telebot
import os
import requests
from dotenv import load_dotenv

# ======================
# LOAD ENV
# ======================
load_dotenv()

BOT_TOKEN = os.getenv("8748187189:AAHvpCSsR6IICPU7eik0OI5GSESOOls5Orw")
IMGBB_API_KEY = os.getenv("f0bfd190fa35268ec184f6c5a9ddd89e")
IG_USER_ID = os.getenv("837019579363873")
ACCESS_TOKEN = os.getenv("EAARbz37wT4EBRT479sDTuJ0ZC06ztHqauYbC6jyB864neWkgqG0XYlSinl7ySOmZAjOvDBnphXgSJHBuhZAbLrZB98iGWCAPjdE2hR3zDaDs1RelUlNLj0P49q6nw2TocvZBJUkjK8gmYhJEQP4KjZCsZAHJxe4cVOj3IABD9NyO5Qa6qZA2a53ZC94s4cimHB43k1wMZAtFaRLSU07yEMKZBkYtRLep6JODnX7OksZA")

if not BOT_TOKEN:
    print("❌ BOT_TOKEN missing")
    exit()

bot = telebot.TeleBot(BOT_TOKEN)

# ======================
# UPLOAD TO IMGBB
# ======================
def upload_imgbb(path):

    with open(path, "rb") as f:
        res = requests.post(
            "https://api.imgbb.com/1/upload",
            data={"key": IMGBB_API_KEY},
            files={"image": f}
        ).json()

    return res["data"]["url"]

# ======================
# INSTAGRAM POST
# ======================
def post_instagram(image_url, caption):

    create = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media"

    r = requests.post(create, data={
        "image_url": image_url,
        "caption": caption,
        "access_token": ACCESS_TOKEN
    }).json()

    if "id" not in r:
        return r

    publish = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media_publish"

    return requests.post(publish, data={
        "creation_id": r["id"],
        "access_token": ACCESS_TOKEN
    }).json()

# ======================
# TELEGRAM HANDLER
# ======================
@bot.message_handler(content_types=['photo'])
def handle_photo(message):

    caption = message.caption or "New Post"

    file = bot.get_file(message.photo[-1].file_id)
    file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file.file_path}"

    img = requests.get(file_url).content

    path = "temp.jpg"
    with open(path, "wb") as f:
        f.write(img)

    # upload to imgbb
    image_url = upload_imgbb(path)

    # post to instagram
    result = post_instagram(image_url, caption)

    bot.reply_to(message, f"✅ Posted!\n\n{result}")

# ======================
# START
# ======================
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🚀 Production Bot Ready\nSend image to post")

print("Bot running...")
bot.infinity_polling()