import os
import logging
from datetime import datetime
from collections import defaultdict
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)
TOKEN = os.environ.get("BOT_TOKEN", "")

message_counts = defaultdict(lambda: defaultdict(int))
user_names = {}
daily_counts = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 أهلاً! الأوامر:\n/stats - إحصائيات\n/top - الأكثر نشاطاً\n/mystat - إحصائياتي\n/today - نشاط اليوم")

async def track_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_user:
        return
    chat_id = update.effective_chat.id
    user = update.effective_user
    user_names[user.id] = user.full_name or f"User{user.id}"
    message_counts[chat_id][user.id] += 1
    today = datetime.now().strftime("%Y-%m-%d")
    daily_counts[chat_id][today][user.id] += 1

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not message_counts[chat_id]:
        await update.message.reply_text("لا توجد إحصائيات بعد!")
        return
    total = sum(message_counts[chat_id].values())
    members = len(message_counts[chat_id])
    today = datetime.now().strftime("%Y-%m-%d")
    today_total = sum(daily_counts[chat_id][today].values())
    await update.message.reply_text(f"📊 الإحصائيات:\n💬 مجموع الرسائل: {total}\n👥 الأعضاء النشطين: {members}\n📅 رسائل اليوم: {today_total}")

async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not message_counts[chat_id]:
        await update.message.reply_text("لا توجد بيانات بعد!")
        return
    sorted_users = sorted(message_counts[chat_id].items(), key=lambda x: x[1], reverse=True)[:10]
    medals = ["🥇","🥈","🥉","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
    text = "🏆 الأكثر نشاطاً:\n"
    for i, (uid, count) in enumerate(sorted_users):
        text += f"{medals[i]} {user_names.get(uid, f'User{uid}')}: {count} رسالة\n"
    await update.message.reply_text(text)

async def mystat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    uid = update.effective_user.id
    total = message_counts[chat_id].get(uid, 0)
    today = datetime.now().strftime("%Y-%m-%d")
    today_count = daily_counts[chat_id][today].get(uid, 0)
    sorted_users = sorted(message_counts[chat_id].items(), key=lambda x: x[1], reverse=True)
    rank = next((i+1 for i, (u, _) in enumerate(sorted_users) if u == uid), 0)
    await update.message.reply_text(f"👤 إحصائياتك:\n💬 مجموع رسائلك: {total}\n📅 اليوم: {today_count}\n🏆 ترتيبك: #{rank}")

async def today_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    today = datetime.now().strftime("%Y-%m-%d")
    data = daily_counts[chat_id][today]
    if not data:
        await update.message.reply_text("لا يوجد نشاط اليوم!")
        return
    total = sum(data.values())
    top5 = sorted(data.items(), key=lambda x: x[1], reverse=True)[:5]
    text = f"📅 نشاط اليوم: {total} رسالة\n"
    for i, (uid, count) in enumerate(top5, 1):
        text += f"{i}. {user_names.get(uid, f'User{uid}')}: {count}\n"
    await update.message.reply_text(text)

def main():
    if not TOKEN:
        print("خطأ: BOT_TOKEN غير موجود!")
        return
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("top", top))
    app.add_handler(CommandHandler("mystat", mystat))
    app.add_handler(CommandHandler("today", today_stats))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, track_message))
    print("البوت شغال!")
    app.run_polling()

if __name__ == "__main__":
    main()