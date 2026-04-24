import telebot
from telebot import types

# =========================================================================
# 1. BOT TOKENI
# =========================================================================
BOT_TOKEN = "8562442755:AAGExVFs7EUtWJDe0sOcCKGmQ6shU5vJCQ8" 

# 2. Zakazlar yuboriladigan ID (TASDIQLANDI)
ADMIN_ID = 855204630  # Zakazlar shu ID'ga yuboriladi

bot = telebot.TeleBot(BOT_TOKEN)

# =========================================================================
# 3. MAHSULOTLAR RO'YXATI VA BLOK NARXLARI (RASMDAN OLINDI)
# =========================================================================
MAHSULOTLAR = {
    # --- 0,45 litr (banoshniy) ---
    "🍻 Sarbast Lite CAN 0,45L": 221626,
    "🍻 Sarbast Original CAN 0,45L": 221626,
    "🍻 Sarbast Original Unfiltered CAN 0,45L": 241813,
    "🍻 Sarbast Special CAN 0,45L": 241813,
    "🍺 Tuborg Green CAN 0,45L": 281972,
    "🍺 Zatecky Gus Svetliy CAN 0,45L": 281971,
    "🍺 Zatecky Gus Exportniy CAN 0,45L": 281979,
    "🍺 Zatecky Gus Krepkiy CAN 0,45L": 281979,
    "🍺 Zatecky Gus Nefiltrovaniy CAN 0,45L": 281979,
    "🍺 Tuborg GOLD CAN 0,45L": 301970,
    "🍺 Carlsberg Pilsner CAN 0,45L": 341978,
    
    # --- 0,5 litr (butilkali) ---
    "🍾 Sarbast Lite RGB 0,5L": 201510,
    "🍾 Sarbast Original RGB 0,5L": 201510,
    "🍾 Sarbast Special RGB 0,5L": 218288,
    "🍾 Tuborg Green RGB 0,5L": 234976,
    "🍾 Zatecky Gus Svetliy RGB 0,47L": 234982,
    "🍾 Zatecky Gus Exportniy RGB 0,47L": 234982,
    "🍾 Carlsberg Pilsner RGB 0,45L": 284982,
    
    # --- 1,5 litr (baklashka) ---
    "💧 Sarbast Lite PET 1,5L": 100498,
    "💧 Sarbast Original PET 1,5L": 100498,
    "💧 Sarbast Special PET 1,5L": 100498,
}

# 4. Foydalanuvchi ma'lumotlarini saqlash uchun lug'at
user_data = {}

# --- START BUYRUG'I ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    cid = message.chat.id
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    markup.add(
        types.InlineKeyboardButton("0,45 L (Bankali 🥫)", callback_data='cat_045can'),
        types.InlineKeyboardButton("0,5 L (Shishali 🍾)", callback_data='cat_05rgb'),
        types.InlineKeyboardButton("1,5 L (Baklashka 💧)", callback_data='cat_15pet')
    )
    
    bot.send_message(
        cid, 
        "Assalomu alaykum! 👋\n**Mahsulotlar Katalogi**ga xush kelibsiz.\nIltimos, kerakli mahsulot turini tanlang:",
        reply_markup=markup,
        parse_mode='Markdown'
    )

# --- MAHSULOTLARNI GURUH BO'YICHA KO'RSATISH ---
@bot.callback_query_handler(func=lambda call: call.data.startswith('cat_'))
def show_products_by_category(call):
    cid = call.message.chat.id
    category = call.data.split('_')[1]
    
    markup_products = types.InlineKeyboardMarkup(row_width=1)
    
    for mahsulot_nomi, narx in MAHSULOTLAR.items():
        if (category == '045can' and 'CAN 0,45L' in mahsulot_nomi) or \
           (category == '05rgb' and ('RGB 0,5L' in mahsulot_nomi or 'RGB 0,47L' in mahsulot_nomi)) or \
           (category == '15pet' and 'PET 1,5L' in mahsulot_nomi):
            
            tugma_matni = f"{mahsulot_nomi} ({narx:,} so‘m/blok)"
            markup_products.add(types.InlineKeyboardButton(tugma_matni, callback_data=f"prod_{mahsulot_nomi}"))

    markup_products.add(types.InlineKeyboardButton("⬅️ Bosh menyuga qaytish", callback_data='start_menu'))
    
    # Oldingi xabarni tahrirlash (edit)
    bot.edit_message_text(
        "Mahsulotni tanlang:",
        cid,
        call.message.message_id,
        reply_markup=markup_products
    )
    bot.answer_callback_query(call.id)


# --- MAHSULOT TANLANGANDA ---
@bot.callback_query_handler(func=lambda call: call.data.startswith('prod_'))
def handle_product_choice(call):
    cid = call.message.chat.id
    mahsulot_nomi = call.data[5:] 
    
    user_data[cid] = {'mahsulot': mahsulot_nomi}
    
    bot.edit_message_text(
        f"Siz **{mahsulot_nomi}**ni tanladingiz. 🛒",
        cid,
        call.message.message_id,
        parse_mode='Markdown'
    )
    
    msg = bot.send_message(
        cid, 
        "Iltimos, nechta **blok** olmoqchi ekanligingizni kiriting (faqat son bilan):"
    )
    bot.register_next_step_handler(msg, handle_block_count)
    bot.answer_callback_query(call.id)

# --- BLOK SONINI KIRITISH VA HISOBLASH ---
def handle_block_count(message):
    cid = message.chat.id
    
    if cid not in user_data:
        bot.send_message(cid, "❌ Xatolik! Iltimos, /start buyrug'i bilan boshlang.")
        return
        
    try:
        blok_soni = int(message.text)
        if blok_soni <= 0:
            raise ValueError
    except ValueError:
        msg = bot.send_message(cid, "❌ Uzr, noto'g'ri son kiritdingiz. Iltimos, musbat butun son kiriting:")
        bot.register_next_step_handler(msg, handle_block_count)
        return
        
    mahsulot_nomi = user_data[cid]['mahsulot']
    narx_bir_blok = MAHSULOTLAR.get(mahsulot_nomi, 0)
    
    if narx_bir_blok == 0:
        bot.send_message(cid, "❌ Mahsulot narxi topilmadi. Iltimos, /start buyrug'i bilan qayta urinib ko'ring.")
        return

    jami_narx = narx_bir_blok * blok_soni
    
    user_data[cid]['blok_soni'] = blok_soni
    user_data[cid]['jami_narx'] = jami_narx
    
    # Yakuniy tugmalar
    markup_yakuniy = types.InlineKeyboardMarkup()
    tugma_tasdiq = types.InlineKeyboardButton("✅ Tasdiqlayman", callback_data='tasdiq')
    tugma_bekor = types.InlineKeyboardButton("❌ Bekor qilish", callback_data='bekor')
    markup_yakuniy.add(tugma_tasdiq, tugma_bekor)
    
    # Chiroyli ko‘rinish
    matn = (
        f"➖➖➖➖ **Sizning Zakazingiz** ➖➖➖➖\n"
        f"📦 **Mahsulot:** {mahsulot_nomi}\n"
        f"🔢 **Blok soni:** {blok_soni} ta\n"
        f"💰 **Bitta blok narxi:** {narx_bir_blok:,} so‘m\n"
        f"💸 **Jami to'lov:** **{jami_narx:,} so‘m**\n"
        f"➖➖➖➖➖➖➖➖➖➖➖➖➖➖\n\n"
        f"☝️ Yuqoridagi ma'lumotlar to'g'rimi? **Tasdiqlaysizmi?**"
    )
    
    bot.send_message(
        cid, 
        matn, 
        reply_markup=markup_yakuniy,
        parse_mode='Markdown'
    )


# --- CALLBACK HANDLER ---
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    cid = call.message.chat.id
    
    if call.data == 'start_menu':
        send_welcome(call.message)
        bot.answer_callback_query(call.id, text="Bosh menyu.")
        return

    if cid not in user_data:
        bot.send_message(cid, "❌ Xatolik! Iltimos, /start buyrug'i bilan boshlang.")
        return

    if call.data == 'tasdiq':
        mahsulot = user_data[cid]['mahsulot']
        blok_soni = user_data[cid]['blok_soni']
        jami_narx = user_data[cid]['jami_narx']
        
        # Zakaz matnini tayyorlash (Admin uchun)
        zakaz_matni = (
            f"🔔 **Yangi Zakaz Keldi!** 🔔\n\n"
            f"👤 **Mijoz:** {call.from_user.full_name} (@{call.from_user.username})\n"
            f"🆔 **ID:** `{cid}`\n"
            f"📦 **Mahsulot:** {mahsulot}\n"
            f"🔢 **Blok soni:** {blok_soni} ta\n"
            f"💸 **Jami:** **{jami_narx:,} so‘m**"
        )
        
        try:
            # Zakazni Administratorga yuborish
            bot.send_message(ADMIN_ID, zakaz_matni, parse_mode='Markdown')
            bot.edit_message_text("🎉 **Rahmat!** Zakazingiz qabul qilindi. Operator tez orada siz bilan bog'lanadi.",
                                  cid, call.message.message_id)
        except Exception:
            bot.edit_message_text(f"⚠️ Uzr, zakazni yuborishda xatolik yuz berdi. Iltimos, {ADMIN_ID} ID'li admin bilan bog'laning.",
                                  cid, call.message.message_id)
            
        del user_data[cid]
        
    elif call.data == 'bekor':
        bot.edit_message_text("🚫 Zakaz bekor qilindi. Boshqa mahsulot tanlash uchun /start buyrug'ini kiriting.",
                              cid, call.message.message_id)
        del user_data[cid]
        
    bot.answer_callback_query(call.id)
    
# --- BOTNI ISHGA TUSHIRISH ---
print("Bot ishga tushdi...")
bot.polling(none_stop=True) 
