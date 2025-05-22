#!/usr/bin/env python3
"""
Emerald's Killfeed - Discord Bot for Deadside PvP Engine
Full production-grade bot with killfeed parsing, stats, economy, and premium features
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

import discord
from discord.ext import commands
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from bot.models.database import DatabaseManager
from bot.parsers.killfeed_parser import KillfeedParser
from bot.parsers.historical_parser import HistoricalParser
from bot.parsers.log_parser import LogParser

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class EmeraldKillfeedBot(commands.Bot):
    """Main bot class for Emerald's Killfeed"""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.members = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None,
            case_insensitive=True
        )
        
        # Py-cord handles slash commands automatically through cogs
        
        # Bot configuration
        self.mongo_client = None
        self.database = None
        self.db_manager = None
        self.scheduler = AsyncIOScheduler()
        self.dev_mode = os.getenv('DEV_MODE', 'true').lower() == 'true'
        
        # Parsers (PHASE 2)
        self.killfeed_parser = None
        self.historical_parser = None
        self.log_parser = None
        
        # Asset paths
        self.assets_path = Path('./assets')
        self.dev_data_path = Path('./dev_data')
        
        logger.info("Bot initialized in %s mode", "development" if self.dev_mode else "production")
    
    async def setup_hook(self):
        """Setup hook called when bot is starting"""
        logger.info("Setting up bot...")
        
        # Connect to MongoDB
        await self.setup_database()
        
        # Start scheduler
        self.setup_scheduler()
        
        # Schedule parsers (PHASE 2)
        if self.killfeed_parser:
            self.killfeed_parser.schedule_killfeed_parser()
        if self.log_parser:
            self.log_parser.schedule_log_parser()
        
        # Load cogs
        await self.load_cogs()
        
        logger.info("Bot setup completed")
    
    async def load_cogs(self):
        """Load all bot cogs"""
        try:
            # Load cogs in order
            cogs = [
                'bot.cogs.economy',
                'bot.cogs.gambling', 
                'bot.cogs.linking',
                'bot.cogs.stats',
                'bot.cogs.bounties',
                'bot.cogs.factions',
                'bot.cogs.premium',
                'bot.cogs.leaderboards'
            ]
            
            loaded_cogs = []
            failed_cogs = []
            
            for cog in cogs:
                try:
                    self.load_extension(cog)
                    loaded_cogs.append(cog)
                    logger.info(f"✅ Successfully loaded cog: {cog}")
                except Exception as e:
                    failed_cogs.append(cog)
                    logger.error(f"❌ Failed to load cog {cog}: {e}")
            
            # Verify commands are registered
            command_count = len(self.pending_application_commands)
            logger.info(f"📊 Loaded {len(loaded_cogs)}/{len(cogs)} cogs successfully")
            logger.info(f"📊 Total slash commands registered: {command_count}")
            
            if failed_cogs:
                logger.error(f"❌ Failed cogs: {failed_cogs}")
                return False
            else:
                logger.info("✅ All cogs loaded and commands registered successfully")
                return True
            
        except Exception as e:
            logger.error(f"❌ Critical failure loading cogs: {e}")
            return False
    
    async def setup_database(self):
        """Setup MongoDB connection"""
        mongo_uri = os.getenv('MONGO_URI')
        if not mongo_uri:
            logger.error("MONGO_URI not found in environment variables")
            return False
            
        try:
            self.mongo_client = AsyncIOMotorClient(mongo_uri)
            self.database = self.mongo_client.emerald_killfeed
            
            # Initialize database manager with PHASE 1 architecture
            self.db_manager = DatabaseManager(self.mongo_client)
            
            # Test connection
            await self.mongo_client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")
            
            # Initialize database indexes
            await self.db_manager.initialize_indexes()
            logger.info("Database architecture initialized (PHASE 1)")
            
            # Initialize parsers (PHASE 2)
            self.killfeed_parser = KillfeedParser(self)
            self.historical_parser = HistoricalParser(self)
            self.log_parser = LogParser(self)
            logger.info("Parsers initialized (PHASE 2)")
            
            return True
            
        except Exception as e:
            logger.error("Failed to connect to MongoDB: %s", e)
            return False
    
    def setup_scheduler(self):
        """Setup background job scheduler"""
        try:
            self.scheduler.start()
            logger.info("Background job scheduler started")
            return True
        except Exception as e:
            logger.error("Failed to start scheduler: %s", e)
            return False
    
    async def on_ready(self):
        """Called when bot is ready and connected to Discord"""
        if self.user:
            logger.info("Bot is ready! Logged in as %s (ID: %s)", self.user.name, self.user.id)
        logger.info("Connected to %d guilds", len(self.guilds))
        
        # Py-cord automatically syncs slash commands from cogs
        logger.info("Slash commands loaded from cogs and available in Discord")
        
        # Verify assets exist
        if self.assets_path.exists():
            assets = list(self.assets_path.glob('*.png'))
            logger.info("Found %d asset files", len(assets))
        else:
            logger.warning("Assets directory not found")
        
        # Verify dev data exists (for testing)
        if self.dev_mode:
            csv_files = list(self.dev_data_path.glob('csv/*.csv'))
            log_files = list(self.dev_data_path.glob('logs/*.log'))
            logger.info("Dev mode: Found %d CSV files and %d log files", len(csv_files), len(log_files))
    
    async def on_guild_join(self, guild):
        """Called when bot joins a new guild"""
        logger.info("Joined guild: %s (ID: %s)", guild.name, guild.id)
        
        # Initialize guild in database (will be implemented in Phase 1)
        # await self.database.guilds.insert_one({
        #     'guild_id': guild.id,
        #     'guild_name': guild.name,
        #     'created_at': datetime.utcnow(),
        #     'premium_servers': [],
        #     'channels': {}
        # })
    
    async def on_guild_remove(self, guild):
        """Called when bot is removed from a guild"""
        logger.info("Left guild: %s (ID: %s)", guild.name, guild.id)
    
    async def close(self):
        """Clean shutdown"""
        logger.info("Shutting down bot...")
        
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped")
        
        if self.mongo_client:
            self.mongo_client.close()
            logger.info("MongoDB connection closed")
        
        await super().close()
        logger.info("Bot shutdown complete")

async def main():
    """Main entry point"""
    # Check required environment variables
    bot_token = os.getenv('BOT_TOKEN')
    mongo_uri = os.getenv('MONGO_URI')
    
    if not bot_token:
        logger.error("BOT_TOKEN not found in environment variables")
        logger.error("Please set your Discord bot token in the .env file")
        return
    
    if not mongo_uri:
        logger.error("MONGO_URI not found in environment variables")
        logger.error("Please set your MongoDB connection string in the .env file")
        return
    
    # Create and run bot
    bot = EmeraldKillfeedBot()
    
    try:
        await bot.start(bot_token)
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error("An error occurred: %s", e)
    finally:
        await bot.close()

if __name__ == "__main__":
    asyncio.run(main())