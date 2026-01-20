import os
import json
import logging
import asyncio
from datetime import datetime
from telethon import TelegramClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_ID = os.getenv("APP_ID")
API_HASH = os.getenv("APP_HASH")
CHANNELS = os.getenv("CHANNELS", "CheMed123,lobelia4cosmetics,tikvahpharma").split(",")
DATA_DIR = "data/raw/telegram_messages"
IMAGE_DIR = "data/raw/images"
LOG_DIR = "logs"

# Ensure directories exist
os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=f"{LOG_DIR}/scraper.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("scraper")
logger.setLevel(logging.INFO)
fh = logging.FileHandler(f"{LOG_DIR}/scraper.log")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)

async def scrape_channel(client, channel_username):
    """Scrapes messages and images from a given channel."""
    logger.info(f"Starting scrape for channel: {channel_username}")
    try:
        entity = await client.get_entity(channel_username)
        channel_name = entity.username or entity.title
        
        # Partitioned directory for JSON: DATA_DIR/<channel_id>/<date>/
        date_str = datetime.now().strftime("%Y-%m-%d")
        channel_data_dir = os.path.join(DATA_DIR, str(entity.id), date_str)
        os.makedirs(channel_data_dir, exist_ok=True)
        
        messages = []
        async for message in client.iter_messages(entity, limit=500):
            msg_data = {
                "id": message.id,
                "date": message.date.isoformat(),
                "text": message.text,
                "views": message.views,
                "forwards": message.forwards,
                "media": bool(message.media),
                "sender_id": message.sender_id,
                "reply_to": message.reply_to.reply_to_msg_id if message.reply_to else None,
                "channel_id": entity.id,
                "channel_name": channel_name
            }
            messages.append(msg_data)
            
            # Download images
            if message.photo:
                img_channel_dir = os.path.join(IMAGE_DIR, str(entity.id))
                os.makedirs(img_channel_dir, exist_ok=True)
                filename = f"{entity.id}_{message.id}.jpg"
                save_path = os.path.join(img_channel_dir, filename)
                if not os.path.exists(save_path):
                    try:
                        await client.download_media(message.photo, save_path)
                        logger.info(f"Downloaded image for message {message.id} in {channel_name}")
                    except Exception as img_err:
                        logger.warning(f"Failed to download image for message {message.id}: {img_err}")

        # Save to JSON
        json_filename = f"{entity.id}_{channel_name}_{date_str}.json"
        with open(os.path.join(channel_data_dir, json_filename), "w", encoding="utf-8") as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Successfully scraped {len(messages)} messages from {channel_username}")
    
    except Exception as e:
        logger.error(f"Error scraping {channel_username}: {e}")
        # Add a small delay to prevent rapid-fire errors if it's a connection issue
        await asyncio.sleep(5)

async def main():
    async with TelegramClient('src/session_name', API_ID, API_HASH) as client:
        for channel in CHANNELS:
            await scrape_channel(client, channel)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
