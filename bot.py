import asyncio
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

# ==================== НАСТРОЙКИ ====================
TOKEN = "9243770351:AAFTLitdGm4zf28nAr6itokvWnXvsFxvms8"  # Токен от @BotFather

# Ссылка на ваш профиль
MY_PROFILE_URL = "https://rbx.tg/IZlia-qu" 

# Юзернейм для связи и поддержки
SUPPORT_USERNAME = "xdico"
# Юзернейм вашего бота (без @) для формирования реферальных ссылок
BOT_USERNAME = "FfreepetssAdoptme_bot" 

# Ваш Telegram ID для доступа к статистике
ADMIN_ID = 8504571450
# ====================================================

bot = Bot(token=TOKEN)
dp = Dispatcher()

# База данных в памяти
users_db = {}

def get_user_data(user_id: int):
    if user_id not in users_db:
        users_db[user_id] = {
            "pets": [],
            "profile_claimed": False,
            "selected_pet": None,
            "referrals": 0
        }
    return users_db[user_id]

def main_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="🐾 Мои питомцы")
    builder.button(text="🎁 Выбрать питомца за дружбу")
    builder.button(text="🔗 Реферальная ссылка")
    builder.button(text="💬 Поддержка")
    builder.adjust(2, 2)
    return builder.as_markup(resize_keyboard=True)

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    get_user_data(user_id)
    
    args = message.text.split()
    if len(args) > 1:
        try:
            referrer_id = int(args[1])
            if referrer_id != user_id and referrer_id in users_db:
                referrer_data = get_user_data(referrer_id)
                referrer_data["referrals"] += 1
                try:
                    await bot.send_message(
                        referrer_id, 
                        f"🎉 По вашей реферальной ссылке зарегистрировался новый игрок!\n"
                        f"Всего приглашено: {referrer_data['referrals']} чел."
                    )
                except Exception:
                    pass
        except ValueError:
            pass

    text = (
        f"Привет, {message.from_user.first_name}! 👋\n\n"
        "Добро пожаловать в официальный бот раздачи питомцев Adopt Me!\n\n"
        "Как получить питомца?\n"
        "Всё очень просто! Я раздаю топовых питомцев за то, что вы переходите по моей ссылке, входите в аккаунт и добавляете меня в друзья.\n\n"
        "Нажми «🎁 Выбрать питомца за дружбу» в меню ниже и забирай свою награду!"
    )
    await message.answer(text, reply_markup=main_keyboard())

# ==================== КОМАНДА СТАТИСТИКИ ====================
@dp.message(F.text == "/stats")
async def show_stats(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("У вас нет доступа к этой команде.")
        return
        
    total_users = len(users_db)
    claimed_count = sum(1 for data in users_db.values() if data["profile_claimed"])
    
    # Подсчет популярных питомцев
    pet_stats = {}
    for data in users_db.values():
        pet = data.get("selected_pet")
        if pet:
            pet_stats[pet] = pet_stats.get(pet, 0) + 1
            
    stats_pets_text = ""
    if pet_stats:
        stats_pets_text = "\n\nВыбранные питомцы:\n" + "\n".join([f"• {pet}: {count} шт." for pet, count in pet_stats.items()])
    
    text = (
        "📊 Статистика вашего бота:\n\n"
        f"👥 Всего запустили бота: {total_users} чел.\n"
        f"🎁 Оформили заявку: {claimed_count} чел."
        f"{stats_pets_text}"
    )
    await message.answer(text)
# ==========================================================

@dp.message(F.text == "🐾 Мои питомцы")
async def show_my_pets(message: types.Message):
    user_data = get_user_data(message.from_user.id)
    pets = user_data["pets"]
    
    if not pets:
        await message.answer("У вас пока нет питомцев. Нажмите «🎁 Выбрать питомца за дружбу», чтобы выбрать первого!")
        return
        
    text = "Ваш инвентарь питомцев:\n\n" + "\n".join([f"• {pet}" for pet in pets])
    await message.answer(text)

@dp.message(F.text == "🎁 Выбрать питомца за дружбу")
async def choose_pet_menu(message: types.Message):
    user_data = get_user_data(message.from_user.id)
    
    if user_data["profile_claimed"]:
        await message.answer(f"Вы уже отправили заявку на питомца «{user_data['selected_pet']}»! Ожидайте выдачи лично в ЛС.")
        return
        
    builder = InlineKeyboardBuilder()
    builder.button(text="🦉 Сова NFR (Neon Fly Ride Owl)", callback_data="select_owl")
    builder.button(text="❄️ Фрост Дракон (Frost Dragon)", callback_data="select_frost")
    builder.button(text="🐢 Черепаха NFR (Neon Fly Ride Turtle)", callback_data="select_turtle")
    builder.button(text="🦘 Кенгуру FR (Fly Ride Kangaroo)", callback_data="select_kanga")
    builder.adjust(1)
    
    text = (
        "📜 КАТАЛОГ ПИТОМЦЕВ ДЛЯ ПОЛУЧЕНИЯ\n\n"
        "Выберите питомца, которого вы хотите получить за добавление в друзья:"
    )
    await message.answer(text, reply_markup=builder.as_markup())

@dp.callback_query(F.data.startswith("select_"))
async def process_pet_selection(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user_data = get_user_data(user_id)
    
    if user_data["profile_claimed"]:
        await callback.answer("Заявка уже была отправлена!", show_alert=True)
        return

    pets_map = {
        "select_owl": "🦉 Сова NFR (Neon Fly Ride Owl)",
        "select_frost": "❄️ Фрост Дракон (Frost Dragon)",
        "select_turtle": "🐢 Черепаха NFR (Neon Fly Ride Turtle)",
        "select_kanga": "🦘 Кенгуру FR (Fly Ride Kangaroo)"
    }
    
    chosen_pet = pets_map.get(callback.data, "🦉 Сова NFR")
    user_data["selected_pet"] = chosen_pet

    builder = InlineKeyboardBuilder()
    builder.button(text="🌐 Перейти по ссылке и добавить в друзья", url=MY_PROFILE_URL)
    builder.button(text="✅ Я вошел(ась) и добавил(ась) в друзья!", callback_data="check_friend_profile")
    builder.adjust(1)
    
    text = (
        f"🎁 Вы выбрали: {chosen_pet}\n\n"
        "⚠️ ВНИМАНИЕ: Обязательно ВЫКЛЮЧИТЕ VPN перед переходом по ссылке, иначе сайт может не загрузиться!\n\n"
        "1. Перейдите по ссылке (с выключенным VPN), войдите в аккаунт и отправьте заявку в друзья.\n"
        "2. Нажмите кнопку «✅ Я вошел(ась) и добавил(ась) в друзья!» ниже.\n\n"
        f"⏱ ВАЖНО: После выполнения условий я лично проверю заявку и пришлю вам подарок ({chosen_pet})!"
    )
    await callback.message.edit_text(text, reply_markup=builder.as_markup())

@dp.callback_query(F.data == "check_friend_profile")
async def process_check_profile(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user_data = get_user_data(user_id)
    
    if user_data["profile_claimed"]:
        await callback.answer("Заявка уже была отправлена!", show_alert=True)
        return
        
    chosen_pet = user_data.get("selected_pet", "🦉 Сова NFR (Neon Fly Ride Owl)")
    user_data["profile_claimed"] = True
    user_data["pets"].append(chosen_pet)
    
    try:
        await bot.send_message(
            chat_id=user_id,
            text=f"🎉 Заявка принята!\nПитомец {chosen_pet} успешно забронирован за вами.\n\nОжидайте, я лично проверю заявку в течение пару минут и напишу вам в личные сообщения для передачи подарка!"
        )
    except Exception:
        pass

    await callback.answer("🎉 Заявка отправлена! Ожидайте сообщения от создателя.", show_alert=True)

@dp.message(F.text == "🔗 Реферальная ссылка")
async def show_ref_link(message: types.Message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)
    
    ref_link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
    
    text = (
        f"Ваша персональная реферальная ссылка:\n{ref_link}\n\n"
        f"Приглашено друзей: {user_data['referrals']}\n\n"
        "Делитесь ссылкой с друзьями, чтобы получать ещё больше питомцев!"
    )
    await message.answer(text)

@dp.message(F.text == "💬 Поддержка")
async def show_support(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="✍️ Написать создателю (@xdico)", url=f"https://t.me/{SUPPORT_USERNAME}")
    builder.adjust(1)
    
    text = (
        "Центр поддержки\n\n"
        "Возникли вопросы или нужно ускорить получение питомца?\n"
        "Нажмите кнопку ниже, чтобы написать мне напрямую (@xdico)!"
    )
    await message.answer(text, reply_markup=builder.as_markup())

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())