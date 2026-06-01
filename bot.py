import asyncio
import logging
import os
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes, filters
from apscheduler.schedulers.asyncio import AsyncIOScheduler

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

TOKEN   = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))

def kalan_sure():
    tz    = pytz.timezone("Europe/Istanbul")
    simdi = datetime.now(tz)
    gece_yarisi = (simdi + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    kalan = gece_yarisi - simdi
    toplam = int(kalan.total_seconds())
    saat   = toplam // 3600
    dakika = (toplam % 3600) // 60
    saniye = toplam % 60
    return saat, dakika, saniye

def kalan_mesaj_olustur(ayrintili=False):
    saat, dakika, saniye = kalan_sure()

    if saat == 0 and dakika == 0:
        return (
            "🎉 *Jack'in mesaisi sona erdi!*\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🔧 _develop by Berk@an_"
        )

    if ayrintili:
        sure = f"*{saat} saat {dakika} dakika {saniye} saniye*"
    else:
        sure = f"*{saat} saat*"

    return (
        f"⏰ Jack'in mesaisine {sure} kaldı!\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🔧 _develop by Berk@an_"
    )

# Gece yarısı mesajı
async def gece_yarisi_mesaj():
    bot = Bot(token=TOKEN)
    metin = (
        "Gececi orospular için mesai vakti düt düttt 🚂\n"
        "Sağ baştan say!\n\n"
        "Dölmüt\n"
        "Dölrun\n"
        "Dölrat"
    )
    await bot.send_message(chat_id=CHAT_ID, text=metin)
    logger.info("Gece yarısı mesajı gönderildi.")

# /saat komutu — anlık, dakika+saniye dahil
async def saat_komutu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Bot mesajlarını yoksay
    if update.effective_user.is_bot:
        return
    metin = kalan_mesaj_olustur(ayrintili=True)
    await update.message.reply_text(metin, parse_mode="Markdown")
    logger.info(f"/saat komutu kullanıldı — {update.effective_user.username}")

async def main():
    app = Application.builder().token(TOKEN).build()
    # Sadece gerçek kullanıcılardan gelen komutları dinle
    app.add_handler(CommandHandler("saat", saat_komutu, filters=~filters.VIA_BOT))

    scheduler = AsyncIOScheduler(timezone="Europe/Istanbul")
    scheduler.add_job(
        gece_yarisi_mesaj,
        trigger="cron",
        hour=0,
        minute=0
    )

    scheduler.start()
    logger.info("Bot başlatıldı. /saat komutu ve 3 saatlik bildirimler aktif.")

    async with app:
        await app.start()
        await app.updater.start_polling()
        try:
            while True:
                await asyncio.sleep(3600)
        except (KeyboardInterrupt, SystemExit):
            pass
        finally:
            await app.updater.stop()
            await app.stop()
            scheduler.shutdown()
            logger.info("Bot durduruldu.")

if __name__ == "__main__":
    asyncio.run(main())
