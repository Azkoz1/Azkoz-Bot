"""
Discord Bot Framework - Main Bot Class
Community Management & Mass Messaging Bot
"""

import discord
from discord.ext import commands
import asyncio
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.moderation = True
intents.presences = True

class DiscordBot(commands.Bot):
    """Custom Discord Bot with extended functionality"""
    
    def __init__(self):
        super().__init__(
            command_prefix='!',
            intents=intents,
            description='Community Management & Mass Messaging Framework'
        )
        self.synced = False
    
    async def setup_hook(self):
        """Setup hook for loading cogs and syncing commands"""
        await self.load_cogs()
    
    async def load_cogs(self):
        """Load all cogs from the cogs directory"""
        cogs_dir = 'cogs'
        
        if not os.path.exists(cogs_dir):
            logger.warning(f"{cogs_dir} directory not found")
            return
        
        for filename in os.listdir(cogs_dir):
            if filename.endswith('.py') and not filename.startswith('_'):
                cog_name = filename[:-3]
                try:
                    await self.load_extension(f'cogs.{cog_name}')
                    logger.info(f"✓ Loaded cog: {cog_name}")
                except Exception as e:
                    logger.error(f"✗ Failed to load cog {cog_name}: {e}")
    
    async def on_ready(self):
        """Triggered when bot successfully connects to Discord"""
        logger.info(f'✓ Bot logged in as {self.user}')
        logger.info(f'✓ Bot ID: {self.user.id}')
        
        if not self.synced:
            try:
                synced = await self.tree.sync()
                logger.info(f'✓ Synced {len(synced)} slash command(s)')
                self.synced = True
            except Exception as e:
                logger.error(f'✗ Failed to sync commands: {e}')
        
        # Set bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name='your community | !help'
            )
        )
    
    async def on_command_error(self, ctx, error):
        """Global error handler for commands"""
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("❌ Command not found. Use `!help` for available commands.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"❌ Missing required argument: {error.param}")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don't have permission to use this command.")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("❌ I don't have the required permissions.")
        else:
            logger.error(f"Command error: {error}")
            await ctx.send(f"❌ Error: {str(error)[:100]}")

def create_bot():
    """Factory function to create and return bot instance"""
    return DiscordBot()
