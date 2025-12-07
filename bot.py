import os
import asyncio
import logging
import sys

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

from services.processor import process_video

# --- Config ---
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")
logger = logging.getLogger(__name__)

# Initialize Bot and Dispatcher
if not TOKEN:
    logger.error("Error: TELEGRAM_BOT_TOKEN not found in environment.")
    sys.exit(1)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- States & User Data ---
# Simple in-memory storage for demonstration. For production, use Redis or DB.
user_tones = {}  # {user_id: 'formal'}


# --- Handlers ---

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привет! Я AI-конвертер YouTube видео в статьи.\n\n"
        "🎬 **Как пользоваться:**\n"
        "Просто отправь мне ссылку на YouTube видео.\n\n"
        "⚙️ **Настройки:**\n"
        "Текущий тон: Formal (официальный).\n"
        "Используй /tone чтобы изменить."
    )

@dp.message(F.text.startswith("/"))
async def cmd_commands(message: types.Message):
    if message.text == "/tone":
        builder = InlineKeyboardBuilder()
        builder.button(text="Formal 👔", callback_data="tone_formal")
        builder.button(text="Friendly 🤝", callback_data="tone_friendly")
        builder.button(text="Sales 💰", callback_data="tone_sales")
        builder.button(text="Clickbait 😱", callback_data="tone_clickbait")
        builder.adjust(2)
        await message.answer("Выберите желаемый тон статьи:", reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("tone_"))
async def callback_tone(callback: types.CallbackQuery):
    tone = callback.data.split("_")[1]
    user_tones[callback.from_user.id] = tone
    await callback.message.edit_text(f"✅ Установлен тон: **{tone.capitalize()}**")
    await callback.answer()

@dp.message(F.text)
async def handle_video_link(message: types.Message):
    url = message.text.strip()
    
    # Basic modification to handle mobile/shorts links if needed
    if "youtube.com" not in url and "youtu.be" not in url:
        return # Ignore non-links silently or reply? Let's ignore chatting for now.
    
    user_id = message.from_user.id
    tone = user_tones.get(user_id, "formal")
    
    status_msg = await message.answer(f"⏳ **Обрабатываю видео...**\nТон: {tone}\nЭто может занять минуту.")
    
    try:
        # Run processing in a thread executor to avoid blocking the event loop
        # (Since services.processor is synchronous)
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, process_video, url, tone)
        
        # Send Markdown file
        md_file = FSInputFile(result["markdown_path"])
        await message.answer_document(md_file, caption=f"📄 Статья (Markdown)\nID: `{result['video_id']}`")
        
        # Send HTML file
        html_file = FSInputFile(result["html_path"])
        await message.answer_document(html_file, caption=f"🌐 Статья (HTML)\nОткрыть в браузере")
        
        await status_msg.delete()
        
    except ValueError:
        await status_msg.edit_text("❌ Ошибка: Неверная ссылка на YouTube.")
    except RuntimeError as e:
        await status_msg.edit_text(f"❌ Ошибка генерации: {e}")
    except Exception as e:
        logger.exception("Processing error")
        await status_msg.edit_text("❌ Произошла неизвестная ошибка.")

# --- Main ---
async def main():
    logger.info("Bot started polling...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
