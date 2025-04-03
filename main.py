import os
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv
import openai

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

user_last_chart = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    welcome_text = (
        "👋 **Hello, Welcome to the CCSIT225 ENG-103 Writing Practice BOT!**\n\n"
        "📊 You'll receive a **random graph** to write about.\n\n"
        "📝 Write a **three-paragraph essay** that describes the data in the graph and explains the trends.\n\n"
        "✒️ **Instructions:**\n"
        "• The *introduction* should briefly describe the graph.\n"
        "• The *body* should analyze the data and explain trends.\n"
        "• The *conclusion* should summarize findings and suggest possible reasons.\n"
        "• Word count: **150–200 words**\n"
        "• ✏️ Plan your essay by brainstorming and outlining first.\n\n"
        "🤖 The bot will instantly give you a **score and feedback**!\n\n"
        "🚀 *Ready? Here's your graph:*\n\n"
        "👤 MADE BY: **SAJJAD** 🇸🇦🇲🇦"
    )
    await update.message.reply_text(welcome_text, parse_mode='Markdown')
    await send_random_chart(update, context, user_id)

async def send_random_chart(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id=None):
    chart_dir = "charts"
    chart_files = os.listdir(chart_dir)
    selected_chart = random.choice(chart_files)
    chart_path = os.path.join(chart_dir, selected_chart)

    if not user_id:
        user_id = update.effective_user.id

    user_last_chart[user_id] = selected_chart

    with open(chart_path, "rb") as img:
        await update.message.reply_photo(photo=img, caption="📊 Describe this graph in 150–200 words:")

async def chart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_random_chart(update, context)

async def grade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    user_id = update.effective_user.id
    chart_filename = user_last_chart.get(user_id, "Unknown")

    prompt = (
    f"You are an English teacher. The student was given a chart titled: {chart_filename}.\n\n"
    f"Their writing:\n\"\"\"\n{user_input}\n\"\"\"\n\n"
    "Please give a grade out of 10 and explain any grammar/clarity issues."
)


    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{ "role": "user", "content": prompt }]
        )
        feedback = response.choices[0].message.content
        await update.message.reply_text(feedback)
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("chart", chart))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, grade))
    print("Bot is running...")
    app.run_polling()
