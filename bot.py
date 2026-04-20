import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
import replicate
from replicate.helpers import File

load_dotenv()

bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))
dp = Dispatcher()
client = replicate.Client(api_token=os.getenv("REPLICATE_API_TOKEN"))

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🖼 Фото по тексту", callback_data="photo")],
        [InlineKeyboardButton(text="🎥 Видео по тексту", callback_data="video")],
        [InlineKeyboardButton(text="✏️ Редактировать фото", callback_data="edit")],
        [InlineKeyboardButton(text="📸 Видео с МОИМ лицом", callback_data="me_video")]
    ])

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer("🚀 ИИ-бот готов!\nНапиши промпт или отправь фото + описание.", reply_markup=main_menu())

@dp.message(F.text & ~F.caption)
async def text_to_photo(message: types.Message):
    await message.answer("🖼 Генерирую фото FLUX.2 Pro...")
    try:
        output = client.run(
            "black-forest-labs/flux-2-pro",
            input={"prompt": message.text, "aspect_ratio": "1:1"}
        )
        await message.answer_photo(output[0])
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)[:150]}")

@dp.message(F.photo, F.caption)
async def photo_with_caption(message: types.Message):
    await bot.download_file((await bot.get_file(message.photo[-1].file_id)).file_path, "input.jpg")
    await message.answer("⏳ Генерирую... это может занять 30–90 секунд")

    try:
        if any(x in message.caption.lower() for x in ["видео", "video", "animate"]):
            output = client.run(
                "bytedance/seedance-2.0",
                input={
                    "prompt": message.caption,
                    "image": File(open("input.jpg", "rb")),
                    "duration": 6
                }
            )
            await message.answer_video(output)
        else:
            output = client.run(
                "black-forest-labs/flux-2-pro",
                input={"prompt": message.caption, "image": File(open("input.jpg", "rb"))}
            )
            await message.answer_photo(output[0])
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)[:250]}")

async def main():
    print("✅ Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
