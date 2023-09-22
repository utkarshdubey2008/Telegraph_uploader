from telegraph import upload_file
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import pymongo
from sample_config import Config

# Setup MongoDB connection
mongo_client = pymongo.MongoClient(Config.MONGO_URI)
db = mongo_client[Config.MONGO_DATABASE]

app = Client(
    "Telegra.ph Uploader",
    api_id=Config.APP_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.TG_BOT_TOKEN,
)

# Define a collection in MongoDB for storing subscribed users
subscribed_users = db["subscribed_users"]

@app.on_message(filters.photo)
async def upload_photo(client, message):
    # Check if user is subscribed
    subscribed = await is_user_subscribed(message.from_user.id)
    
    if not subscribed:
        await client.send_message(
            chat_id=message.chat.id,
            text="Please subscribe to @thealphabotz channel to use this bot.",
            reply_to_message_id=message.message_id
        )
        return
    
    msg = await message.reply_text("Downloading...")
    img_path = f"./DOWNLOADS/{message.from_user.id}.jpg"
    img_path = await client.download_media(message=message, file_name=img_path)
    await msg.edit_text("Uploading...")
    try:
        upload_result = upload_file(img_path)
        telegraph_url = "https://telegra.ph" + upload_result[0]
        await msg.edit_text(f"Image uploaded: {telegraph_url}")
    except:
        await msg.edit_text("Something went wrong")
    finally:
        os.remove(img_path)

@app.on_message(filters.animation)
async def upload_animation(client, message):
    subscribed = await is_user_subscribed(message.from_user.id)
    
    if not subscribed:
        await client.send_message(
            chat_id=message.chat.id,
            text="Please subscribe to @thealphabotz channel to use this bot.",
            reply_to_message_id=message.message_id
        )
        return

    if message.animation.file_size < 5242880:
        msg = await message.reply_text("Downloading...")
        gif_path = f"./DOWNLOADS/{message.from_user.id}.mp4"
        gif_path = await client.download_media(message=message, file_name=gif_path)
        await msg.edit_text("Uploading...")
        try:
            upload_result = upload_file(gif_path)
            telegraph_url = "https://telegra.ph" + upload_result[0]
            await msg.edit_text(f"GIF uploaded: {telegraph_url}")
        except:
            await msg.edit_text("Something went wrong")
        finally:
            os.remove(gif_path)
    else:
        await message.reply_text("Size should be less than 5 MB")

# Add other upload functions for videos and handle_messages (if needed)

async def is_user_subscribed(user_id):
    user = subscribed_users.find_one({"user_id": user_id})
    return True if user else False

@app.on_message(filters.command(["start"]))
async def home(client, message):
    buttons = [
        [
            InlineKeyboardButton('Help', callback_data='help'),
            InlineKeyboardButton('Close', callback_data='close')
        ],
        [
            InlineKeyboardButton('Our Channel', url='http://telegram.me/alpha_bot_updates'),
            InlineKeyboardButton('Support', url='http://telegram.me/alpha_bot_support')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await client.send_message(
        chat_id=message.chat.id,
        text="<strong>Hey there,</strong>\n\nI'm a Telegraph Uploader that can upload photos, videos, and GIFs to Telegraph URL.\n\nSimply send me a photo, video, or GIF to use.",
        reply_markup=reply_markup,
        parse_mode="html",
        reply_to_message_id=message.message_id
    )
    

app.run()
