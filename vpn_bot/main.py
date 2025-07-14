import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from config import BOT_TOKEN, CHANNEL_USERNAME

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

def get_start_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔗 Подписаться на канал", url=f"https://t.me/{CHANNEL_USERNAME.strip('@')}")],
        [InlineKeyboardButton(text="✅ Я подписался", callback_data="check_sub")]
    ])
    return keyboard

def get_next_key():
    with open("keys.txt", "r") as file:
        keys = file.readlines()
    if not keys:
        return None
    next_key = keys[0].strip()
    with open("keys.txt", "w") as file:
        file.writelines(keys[1:])
    return next_key

@dp.message(F.text == "/start")
async def start(message: types.Message):
    await message.answer(
        "👋 <b>Привет!</b>

Чтобы получить доступ к нашему <b>VPN</b>:
"
        f"1. Подпишись на канал {CHANNEL_USERNAME}
"
        "2. Нажми «Я подписался»

После этого мы выдадим тебе ссылку для подключения 🔐",
        reply_markup=get_start_keyboard()
    )

@dp.callback_query(F.data == "check_sub")
async def check_subscription(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            key = get_next_key()
            if key:
                await callback.message.edit_text(
                    f"✅ Ты подписался! Вот твой ключ доступа к VPN:

<code>{key}</code>

Сохрани его и подключайся 🔒"
                )
            else:
                await callback.message.edit_text("🚫 Все ключи закончились. Обратитесь к администратору.")
        else:
            await callback.answer("Ты ещё не подписан на канал!", show_alert=True)
    except TelegramBadRequest:
        await callback.answer("Ошибка. Возможно, бот не админ в канале.", show_alert=True)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
