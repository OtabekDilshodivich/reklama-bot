import asyncio
import json
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from config import TOKEN, ADMIN_ID

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

CHANNELS_FILE = 'channels.json'
AD_FILE = 'ad.json'
STOP_AD = False

menu = ReplyKeyboardMarkup(resize_keyboard=True)
menu.add(KeyboardButton("➕ Kanal qo‘shish"), KeyboardButton("❌ Kanalni o‘chirish"))
menu.add(KeyboardButton("✏️ Reklama kiritish"), KeyboardButton("🖼 Media yuklash"))
menu.add(KeyboardButton("⏸ Reklamani to‘xtatish"), KeyboardButton("♻️ Reklamani yangilash"))
menu.add(KeyboardButton("❌ Reklamani o‘chirish"))

def load_json(path):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except:
        return {} if 'ad' in path else []

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("Kechirasiz, siz admin emassiz.")
    await message.answer("Reklama botiga xush kelibsiz!", reply_markup=menu)

# Kanal qo‘shish
@dp.message_handler(lambda m: m.text == "➕ Kanal qo‘shish")
async def add_channel(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("Kanal usernameni yuboring (masalan: @kanalim)")

    @dp.message_handler()
    async def save_channel(m: types.Message):
        chans = load_json(CHANNELS_FILE)
        chans.append(m.text)
        save_json(CHANNELS_FILE, chans)
        await m.answer("Kanal qo‘shildi.")

# Kanalni o‘chirish
@dp.message_handler(lambda m: m.text == "❌ Kanalni o‘chirish")
async def delete_channel(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    chans = load_json(CHANNELS_FILE)
    if chans:
        await message.answer("O‘chirmoqchi bo‘lgan kanal usernameni yuboring:")

        @dp.message_handler()
        async def delete_ch(m: types.Message):
            if m.text in chans:
                chans.remove(m.text)
                save_json(CHANNELS_FILE, chans)
                await m.answer("Kanal o‘chirildi.")
            else:
                await m.answer("Bunday kanal topilmadi.")
    else:
        await message.answer("Kanal ro'yxati bo‘sh.")

# Reklama kiritish
@dp.message_handler(lambda m: m.text == "✏️ Reklama kiritish")
async def set_ad_text(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("Reklama matnini yuboring:")

    @dp.message_handler()
    async def save_ad_text(m: types.Message):
        ad = load_json(AD_FILE)
        ad["text"] = m.text
        save_json(AD_FILE, ad)
        await m.answer("Reklama matni saqlandi.")

# Media yuklash
@dp.message_handler(lambda m: m.text == "🖼 Media yuklash")
async def upload_media(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("Rasm yoki video yuboring:")

    @dp.message_handler(content_types=['photo', 'video'])
    async def save_media(m: types.Message):
        ad = load_json(AD_FILE)
        if m.photo:
            ad["photo"] = m.photo[-1].file_id
        elif m.video:
            ad["video"] = m.video.file_id
        save_json(AD_FILE, ad)
        await m.answer("Media saqlandi.")

# Reklamani o‘chirish
@dp.message_handler(lambda m: m.text == "❌ Reklamani o‘chirish")
async def delete_ad(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    save_json(AD_FILE, {})
    await message.answer("Reklama o‘chirildi.")

# Reklamani to‘xtatish
@dp.message_handler(lambda m: m.text == "⏸ Reklamani to‘xtatish")
async def stop_ads(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    global STOP_AD
    STOP_AD = True
    await message.answer("Reklama to‘xtatildi.")

# Reklamani yangilash
@dp.message_handler(lambda m: m.text == "♻️ Reklamani yangilash")
async def resume_ads(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    global STOP_AD
    STOP_AD = False
    await message.answer("Reklama davom etadi.")

async def send_ads():
    await bot.wait_until_ready()
    global STOP_AD
    while True:
        if not STOP_AD:
            ad = load_json(AD_FILE)
            chans = load_json(CHANNELS_FILE)
            for ch in chans:
                try:
                    if "photo" in ad:
                        await bot.send_photo(ch, ad["photo"], caption=ad.get("text", ""))
                    elif "video" in ad:
                        await bot.send_video(ch, ad["video"], caption=ad.get("text", ""))
                    elif "text" in ad:
                        await bot.send_message(ch, ad["text"])
                except Exception as e:
                    print(f"Xatolik: {e}")
        await asyncio.sleep(300)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(send_ads())
    executor.start_polling(dp, skip_updates=True)
