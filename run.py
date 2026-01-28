"""
Main entry point for the Discord Bot Framework
"""

import asyncio
import logging
import os
from dotenv import load_dotenv
from bot import create_bot

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Main function to start the bot"""
    bot = create_bot()
    
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        raise ValueError("DISCORD_TOKEN environment variable not set. Please add it to .env file")
    
    async with bot:
        try:
            await bot.start(token)
        except discord.LoginFailure:
            logger.error("Failed to login. Check your DISCORD_TOKEN")
        except Exception as e:
            logger.error(f"Bot startup failed: {e}")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested by user")
