from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, JobQueue, Job
from telegram.constants import ParseMode
import asyncio
from datetime import datetime
import arrow
from datetime import time
from tzlocal import get_localzone

import parser
from task_api import TaskAPI
from config import USER_ID, BOT_TOKEN

local_tz = get_localzone()

class ReminderBot:
    def __init__(self):
        self.token = BOT_TOKEN
        self.user_id = int(USER_ID)
        self.task_api = TaskAPI()

        self.application = Application.builder().token(self.token).build()
        self.application.add_handler(CommandHandler("next", self.start_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.on_text))

        # Schedule the daily job
        self.application.job_queue.run_once(
            self.send_daily_tasks,
            when=2,
            name="OneTimeReminder"
        )
        self.application.job_queue.run_daily(
            self.send_daily_tasks,
            time=time(hour=22, minute=51, tzinfo=local_tz),
            name="DailyTaskReminder"
        )

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id == self.user_id:
            user = update.effective_user
            await update.message.reply_html(
                rf"Hi {user.mention_html()}!",
                reply_markup=ForceReply(selective=True),
            )

    async def on_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        from telegram.constants import ParseMode

    async def on_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if update.effective_user.id != self.user_id:
            return

        raw_text = update.message.text
        parsed_data = parser.parse(raw_text)

        if parsed_data is None:
            await update.message.reply_text(
                text="Error!"
            )
            return
        
        date_data, text_data, is_precise = parsed_data
        
        status_msg = await update.message.reply_text(
            text="🕓 *Creating task...*",
            parse_mode=ParseMode.MARKDOWN
        )

        if date_data:
            present = arrow.now()
            local_tz = present.tzinfo

            date_obj = date_data if is_precise else date_data.date()
            if isinstance(date_obj, datetime) and date_obj.tzinfo is None:
                date_obj = date_obj.replace(tzinfo=local_tz)
            arrow_dt = arrow.get(date_obj)
            date_str = arrow_dt.format("HH:mm ddd. DD.MM") if is_precise else arrow_dt.format("ddd. DD.MM")
            date_relative = arrow_dt.humanize(present)

            await self.task_api.create_task(text_data, date_obj, not is_precise)
            # await asyncio.sleep(1)
            final_msg = f"`{text_data}`\n📅 {date_str} _({date_relative})_"
        else:
            await self.task_api.create_task(text_data)
            # await asyncio.sleep(1)
            final_msg = f"`{text_data}`"

        await status_msg.edit_text(
            text=final_msg,
            parse_mode=ParseMode.MARKDOWN
        )

    async def send_daily_tasks(self, context: ContextTypes.DEFAULT_TYPE) -> None:
        tasks = await self.task_api.get_todays_tasks()

        if not tasks:
            message = "✅ You have no tasks for today!"
        else:
            task_lines = "\n".join(f"• {task}" for task in tasks)
            message = f"🗓 *Today's Tasks:*\n{task_lines}"

        await context.bot.send_message(
            chat_id=self.user_id,
            text=message,
            parse_mode=ParseMode.MARKDOWN
        )

    async def start(self):
        print('Reminder bot started!')
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()

    async def stop(self):
        await self.application.updater.stop()
        await self.application.stop()
        await self.application.shutdown()

async def main():
    bot = ReminderBot()
    await bot.start()
    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        await bot.stop()

if __name__ == "__main__":
    asyncio.run(main())