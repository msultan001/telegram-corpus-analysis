import os
import json
import logging
from datetime import datetime
from telethon import TelegramClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_ID = os.getenv("APP_ID")
API_HASH = os.getenv("APP_HASH")
CHANNELS = ["CheMed123", "lobelia4cosmetics", "tikvahpharma"]
DATA_DIR = "data/raw/telegram_messages"
IMAGE_DIR = "data/raw/images"
LOG_DIR = "logs"

# Ensure directories exist
os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# Setup Logging
logging.basicConfig(
    filename=f"{LOG_DIR}/scraper.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

async def scrape_channel(client, channel_username):
    """Scrapes messages and images from a given channel."""
    logging.info(f"Starting scrape for channel: {channel_username}")
    try:
        entity = await client.get_entity(channel_username)
        channel_name = entity.username or entity.title
        
        # Partitioned directory for JSON
        date_str = datetime.now().strftime("%Y-%m-%d")
        channel_data_dir = os.path.join(DATA_DIR, date_str)
        os.makedirs(channel_data_dir, exist_ok=True)
        
        messages = []
        async for message in client.iter_messages(entity, limit=100):
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
                img_path = os.path.join(IMAGE_DIR, channel_name)
                os.makedirs(img_path, exist_ok=True)
                filename = f"{message.id}.jpg"
                save_path = os.path.join(img_path, filename)
                if not os.path.exists(save_path):
                    try:
                        await client.download_media(message.photo, save_path)
                        logging.info(f"Downloaded image for message {message.id} in {channel_name}")
                    except Exception as img_err:
                        logging.warning(f"Failed to download image for message {message.id}: {img_err}")

        # Save to JSON
        json_filename = f"{channel_name}.json"
        with open(os.path.join(channel_data_dir, json_filename), "w", encoding="utf-8") as f:
            json.dump(messages, f, ensure_ascii=False, indent=4)
        
        logging.info(f"Successfully scraped {len(messages)} messages from {channel_username}")
    
    except Exception as e:
        logging.error(f"Error scraping {channel_username}: {e}")
        # Add a small delay to prevent rapid-fire errors if it's a connection issue
        await asyncio.sleep(5)

async def main():
    async with TelegramClient('src/session_name', API_ID, API_HASH) as client:
        for channel in CHANNELS:
            await scrape_channel(client, channel)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
