"""
Discord Server Generator Bot - All-in-One
AI-powered server generation with Gemini API, SQLite tracking, and 4 slash commands.
"""

# Fix for Python 3.13 audioop removal
import sys
import unittest.mock as mock
sys.modules['audioop'] = mock.MagicMock()

import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
import logging
import sqlite3
import json
import asyncio
import google.generativeai as genai
from typing import List, Dict, Tuple

# ============================================================================
# CONFIGURATION
# ============================================================================

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Bot Settings
BOT_COLOR = 0x5865F2  # Discord Blue
MAX_CHANNELS = 20
MAX_ROLES = 10
MAX_CATEGORIES = 10
DATABASE_FILE = "server_generator.db"

# Configure Gemini API
genai.configure(api_key=GOOGLE_API_KEY)

GEMINI_SYSTEM_PROMPT = """You are a Discord server architecture expert. Based on the user's description, 
generate a JSON structure for a Discord server. Return ONLY valid JSON, no other text.

The JSON must follow this exact structure:
{
  "server_name": "Server Name",
  "roles": [
    {
      "name": "Role Name",
      "permissions": ["permission1", "permission2"]
    }
  ],
  "categories": [
    {
      "name": "Category Name",
      "channels": [
        {
          "name": "channel-name",
          "type": "text" or "voice"
        }
      ]
    }
  ]
}

Rules:
- server_name must be a valid Discord server name (less than 100 chars)
- Role names must be unique and valid
- Channel names must be lowercase with hyphens (no spaces)
- Valid permissions: administrator, manage_messages, manage_roles, kick_members, ban_members, manage_channels, manage_guild
- Channel types must be either "text" or "voice"
- Do NOT include @everyone role
- Keep roles under 10, channels under 20, categories under 10
- Create relevant roles based on the description
- Create channels that match the server's purpose

Return ONLY the JSON object, nothing else."""

PERMISSION_MAP = {
    "administrator": discord.Permissions(administrator=True),
    "manage_messages": discord.Permissions(manage_messages=True),
    "manage_roles": discord.Permissions(manage_roles=True),
    "kick_members": discord.Permissions(kick_members=True),
    "ban_members": discord.Permissions(ban_members=True),
    "manage_channels": discord.Permissions(manage_channels=True),
    "manage_guild": discord.Permissions(manage_guild=True),
}

TEMPLATES = {
    "Gaming": {
        "server_name": "Gaming Hub",
        "roles": [
            {"name": "Admin", "permissions": ["administrator"]},
            {"name": "Moderator", "permissions": ["manage_messages", "kick_members"]},
            {"name": "Members", "permissions": []},
        ],
        "categories": [
            {
                "name": "Information",
                "channels": [
                    {"name": "announcements", "type": "text"},
                    {"name": "rules", "type": "text"},
                ]
            },
            {
                "name": "Gaming",
                "channels": [
                    {"name": "general", "type": "text"},
                    {"name": "game-chat", "type": "text"},
                    {"name": "gaming", "type": "voice"},
                    {"name": "events", "type": "voice"},
                ]
            },
        ]
    },
    "Community": {
        "server_name": "Community Server",
        "roles": [
            {"name": "Admin", "permissions": ["administrator"]},
            {"name": "Moderator", "permissions": ["manage_messages", "kick_members"]},
            {"name": "Members", "permissions": []},
        ],
        "categories": [
            {
                "name": "Welcome",
                "channels": [
                    {"name": "announcements", "type": "text"},
                    {"name": "rules", "type": "text"},
                    {"name": "introduce-yourself", "type": "text"},
                ]
            },
            {
                "name": "General",
                "channels": [
                    {"name": "general", "type": "text"},
                    {"name": "off-topic", "type": "text"},
                ]
            },
            {
                "name": "Voice",
                "channels": [
                    {"name": "lounge", "type": "voice"},
                    {"name": "gaming", "type": "voice"},
                ]
            },
        ]
    },
    "Content Creator": {
        "server_name": "Creator Hub",
        "roles": [
            {"name": "Creator", "permissions": ["administrator"]},
            {"name": "Moderator", "permissions": ["manage_messages"]},
            {"name": "Sponsor", "permissions": []},
            {"name": "Members", "permissions": []},
        ],
        "categories": [
            {
                "name": "Content",
                "channels": [
                    {"name": "announcements", "type": "text"},
                    {"name": "uploads", "type": "text"},
                    {"name": "collaboration", "type": "text"},
                ]
            },
            {
                "name": "Community",
                "channels": [
                    {"name": "fan-chat", "type": "text"},
                    {"name": "sponsor-lounge", "type": "text"},
                    {"name": "hangout", "type": "voice"},
                ]
            },
        ]
    },
    "Business": {
        "server_name": "Business Server",
        "roles": [
            {"name": "Owner", "permissions": ["administrator"]},
            {"name": "Manager", "permissions": ["manage_messages", "manage_roles"]},
            {"name": "Team", "permissions": []},
        ],
        "categories": [
            {
                "name": "Management",
                "channels": [
                    {"name": "announcements", "type": "text"},
                    {"name": "meetings", "type": "text"},
                    {"name": "decisions", "type": "text"},
                ]
            },
            {
                "name": "Projects",
                "channels": [
                    {"name": "project-updates", "type": "text"},
                    {"name": "collaboration", "type": "text"},
                ]
            },
            {
                "name": "Voice",
                "channels": [
                    {"name": "meetings", "type": "voice"},
                    {"name": "brainstorm", "type": "voice"},
                ]
            },
        ]
    },
    "Minecraft": {
        "server_name": "Minecraft Community",
        "roles": [
            {"name": "Admin", "permissions": ["administrator"]},
            {"name": "Moderator", "permissions": ["manage_messages"]},
            {"name": "Builder", "permissions": []},
            {"name": "Player", "permissions": []},
        ],
        "categories": [
            {
                "name": "Server Info",
                "channels": [
                    {"name": "announcements", "type": "text"},
                    {"name": "server-status", "type": "text"},
                    {"name": "rules", "type": "text"},
                ]
            },
            {
                "name": "Trading & Events",
                "channels": [
                    {"name": "trading", "type": "text"},
                    {"name": "events", "type": "text"},
                    {"name": "auctions", "type": "text"},
                ]
            },
            {
                "name": "Staff",
                "channels": [
                    {"name": "staff-chat", "type": "text"},
                    {"name": "reports", "type": "text"},
                ]
            },
            {
                "name": "Voice Chats",
                "channels": [
                    {"name": "main", "type": "voice"},
                    {"name": "events", "type": "voice"},
                    {"name": "afk", "type": "voice"},
                ]
            },
        ]
    },
}

# ============================================================================
# DATABASE
# ============================================================================

class Database:
    """SQLite database handler."""
    
    def __init__(self, db_file: str = DATABASE_FILE):
        self.db_file = db_file
        self._init_database()
    
    def _init_database(self):
        """Create tables if they don't exist."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS setups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    description TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(guild_id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS created_roles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    role_id INTEGER NOT NULL,
                    role_name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (guild_id) REFERENCES setups(guild_id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS created_channels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    channel_id INTEGER NOT NULL,
                    channel_name TEXT NOT NULL,
                    channel_type TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (guild_id) REFERENCES setups(guild_id)
                )
            """)
            
            conn.commit()
            logger.info("Database initialized")
        except Exception as e:
            logger.error(f"Database init error: {e}")
        finally:
            conn.close()
    
    def save_setup(self, guild_id: int, user_id: int, description: str):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM setups WHERE guild_id = ?", (guild_id,))
            cursor.execute("DELETE FROM created_roles WHERE guild_id = ?", (guild_id,))
            cursor.execute("DELETE FROM created_channels WHERE guild_id = ?", (guild_id,))
            cursor.execute(
                "INSERT INTO setups (guild_id, user_id, description) VALUES (?, ?, ?)",
                (guild_id, user_id, description)
            )
            conn.commit()
        except Exception as e:
            logger.error(f"Error saving setup: {e}")
        finally:
            conn.close()
    
    def add_role(self, guild_id: int, role_id: int, role_name: str):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO created_roles (guild_id, role_id, role_name) VALUES (?, ?, ?)",
                (guild_id, role_id, role_name)
            )
            conn.commit()
        except Exception as e:
            logger.error(f"Error adding role: {e}")
        finally:
            conn.close()
    
    def add_channel(self, guild_id: int, channel_id: int, channel_name: str, channel_type: str):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO created_channels (guild_id, channel_id, channel_name, channel_type) VALUES (?, ?, ?, ?)",
                (guild_id, channel_id, channel_name, channel_type)
            )
            conn.commit()
        except Exception as e:
            logger.error(f"Error adding channel: {e}")
        finally:
            conn.close()
    
    def get_created_roles(self, guild_id: int) -> List[Tuple[int, str]]:
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT role_id, role_name FROM created_roles WHERE guild_id = ?",
                (guild_id,)
            )
            result = cursor.fetchall()
            return result
        except Exception as e:
            logger.error(f"Error getting roles: {e}")
            return []
        finally:
            conn.close()
    
    def get_created_channels(self, guild_id: int) -> List[Tuple[int, str, str]]:
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT channel_id, channel_name, channel_type FROM created_channels WHERE guild_id = ?",
                (guild_id,)
            )
            result = cursor.fetchall()
            return result
        except Exception as e:
            logger.error(f"Error getting channels: {e}")
            return []
        finally:
            conn.close()
    
    def get_setup_description(self, guild_id: int) -> str:
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT description FROM setups WHERE guild_id = ?", (guild_id,))
            result = cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            logger.error(f"Error getting description: {e}")
            return None
        finally:
            conn.close()
    
    def delete_setup(self, guild_id: int):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM created_roles WHERE guild_id = ?", (guild_id,))
            cursor.execute("DELETE FROM created_channels WHERE guild_id = ?", (guild_id,))
            cursor.execute("DELETE FROM setups WHERE guild_id = ?", (guild_id,))
            conn.commit()
            logger.info(f"Setup deleted for guild {guild_id}")
        except Exception as e:
            logger.error(f"Error deleting setup: {e}")
        finally:
            conn.close()

db = Database()

# ============================================================================
# AI GENERATOR
# ============================================================================

class AIServerGenerator:
    """Generates server structure using Gemini."""
    
    @staticmethod
    async def generate_structure(description: str) -> dict:
        try:
            model = genai.GenerativeModel('gemini-pro')
            prompt = f"""{GEMINI_SYSTEM_PROMPT}

User's Server Description:
{description}

Important constraints:
- Maximum {MAX_ROLES} roles
- Maximum {MAX_CHANNELS} channels total
- Maximum {MAX_CATEGORIES} categories
- Do NOT include @everyone role
- Channel names must be lowercase with hyphens only

Return ONLY the JSON object."""
            
            response = model.generate_content(prompt)
            
            if not response.text:
                logger.error("Gemini returned empty response")
                return None
            
            json_str = response.text.strip()
            
            if not json_str.startswith("{"):
                start = json_str.find("{")
                if start != -1:
                    json_str = json_str[start:]
            
            if json_str.endswith("```"):
                json_str = json_str[:-3]
            
            structure = json.loads(json_str)
            
            if not AIServerGenerator._validate_structure(structure):
                return None
            
            logger.info(f"Generated structure: {structure.get('server_name')}")
            return structure
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            return None
        except Exception as e:
            logger.error(f"Generation error: {e}")
            return None
    
    @staticmethod
    def _validate_structure(structure: dict) -> bool:
        try:
            if not isinstance(structure, dict):
                return False
            
            if "server_name" not in structure or len(structure["server_name"]) > 100:
                return False
            
            roles = structure.get("roles", [])
            if not isinstance(roles, list) or len(roles) > MAX_ROLES:
                return False
            
            role_names = set()
            for role in roles:
                if not isinstance(role, dict) or "name" not in role:
                    return False
                if role["name"].lower() == "@everyone":
                    return False
                if role["name"] in role_names:
                    return False
                role_names.add(role["name"])
            
            categories = structure.get("categories", [])
            if not isinstance(categories, list) or len(categories) > MAX_CATEGORIES:
                return False
            
            total_channels = 0
            channel_names = set()
            
            for category in categories:
                if not isinstance(category, dict):
                    return False
                
                channels = category.get("channels", [])
                if not isinstance(channels, list):
                    return False
                
                total_channels += len(channels)
                
                for channel in channels:
                    if not isinstance(channel, dict) or "name" not in channel or "type" not in channel:
                        return False
                    if channel["type"].lower() not in ["text", "voice"]:
                        return False
                    if channel["name"] in channel_names:
                        return False
                    channel_names.add(channel["name"])
            
            if total_channels > MAX_CHANNELS:
                return False
            
            return True
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False

# ============================================================================
# SERVER CREATOR
# ============================================================================

class ServerCreator:
    """Creates Discord server elements."""
    
    @staticmethod
    async def create_roles(
        guild: discord.Guild,
        roles_config: List[Dict],
        existing_roles: set
    ) -> Tuple[List[discord.Role], List[str]]:
        created_roles = []
        errors = []
        
        for role_config in roles_config:
            try:
                role_name = role_config.get("name", "").strip()
                
                if not role_name or len(role_name) > 100:
                    continue
                
                if role_name.lower() in existing_roles:
                    errors.append(f"Skipped: Role '{role_name}' already exists")
                    continue
                
                permissions = discord.Permissions()
                perm_list = role_config.get("permissions", [])
                
                for perm in perm_list:
                    if perm in PERMISSION_MAP:
                        permissions |= PERMISSION_MAP[perm]
                
                if role_name.lower() == "@everyone" and permissions.administrator:
                    permissions.administrator = False
                
                new_role = await guild.create_role(
                    name=role_name,
                    permissions=permissions,
                    reason="Server setup by user"
                )
                
                created_roles.append(new_role)
                existing_roles.add(role_name.lower())
                logger.info(f"Created role: {role_name}")
                
            except discord.Forbidden:
                errors.append(f"Failed: No permission to create role")
            except Exception as e:
                errors.append(f"Failed: {str(e)}")
        
        return created_roles, errors
    
    @staticmethod
    async def create_categories_and_channels(
        guild: discord.Guild,
        categories_config: List[Dict],
        existing_channels: set
    ) -> Tuple[List[Tuple[discord.CategoryChannel, List[discord.abc.GuildChannel]]], List[str]]:
        created_structure = []
        errors = []
        
        for category_config in categories_config:
            try:
                category_name = category_config.get("name", "").strip()
                
                if not category_name or len(category_name) > 100:
                    continue
                
                category = await guild.create_category(
                    name=category_name,
                    reason="Server setup by user"
                )
                
                channels = []
                channels_config = category_config.get("channels", [])
                
                for channel_config in channels_config:
                    try:
                        channel_name = channel_config.get("name", "").strip()
                        channel_type = channel_config.get("type", "text").lower()
                        
                        if not channel_name or channel_type not in ["text", "voice"]:
                            continue
                        
                        if channel_name.lower() in existing_channels:
                            errors.append(f"Skipped: Channel '{channel_name}' already exists")
                            continue
                        
                        if channel_type == "voice":
                            channel = await guild.create_voice_channel(
                                name=channel_name,
                                category=category,
                                reason="Server setup by user"
                            )
                        else:
                            channel = await guild.create_text_channel(
                                name=channel_name,
                                category=category,
                                reason="Server setup by user"
                            )
                        
                        channels.append(channel)
                        existing_channels.add(channel_name.lower())
                        logger.info(f"Created {channel_type} channel: {channel_name}")
                        
                    except Exception as e:
                        errors.append(f"Failed: Channel error")
                
                created_structure.append((category, channels))
                
            except Exception as e:
                errors.append(f"Failed: Category error")
        
        return created_structure, errors
    
    @staticmethod
    async def delete_roles(guild: discord.Guild, role_ids: List[int]) -> Tuple[int, int]:
        deleted = 0
        skipped = 0
        
        for role_id in role_ids:
            try:
                role = guild.get_role(role_id)
                if not role:
                    skipped += 1
                    continue
                
                await role.delete(reason="Undo setup")
                deleted += 1
                logger.info(f"Deleted role: {role.name}")
            except Exception as e:
                skipped += 1
        
        return deleted, skipped
    
    @staticmethod
    async def delete_channels(guild: discord.Guild, channel_ids: List[int]) -> Tuple[int, int]:
        deleted = 0
        skipped = 0
        
        for channel_id in channel_ids:
            try:
                channel = guild.get_channel(channel_id)
                if not channel:
                    skipped += 1
                    continue
                
                await channel.delete(reason="Undo setup")
                deleted += 1
                logger.info(f"Deleted channel: {channel.name}")
            except Exception as e:
                skipped += 1
        
        return deleted, skipped

# ============================================================================
# BOT SETUP
# ============================================================================

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.guild_messages = True

bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    """Called when bot is ready."""
    logger.info(f"Logged in as {bot.user}")
    print(f"✓ Bot online as {bot.user}")
    
    try:
        synced = await bot.tree.sync()
        logger.info(f"Synced {len(synced)} command(s)")
        print(f"✓ Synced {len(synced)} slash commands")
    except Exception as e:
        logger.error(f"Failed to sync commands: {e}")

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

async def update_progress(message: discord.Message, status: str, step: int, total_steps: int):
    """Update progress embed."""
    embed = discord.Embed(
        title="🔧 Server Setup in Progress",
        description=status,
        color=BOT_COLOR
    )
    
    steps = [
        "📝 Analyzing Description",
        "🤖 Generating Server Structure",
        "👥 Creating Roles",
        "📂 Creating Categories",
        "📨 Creating Channels",
        "✅ Finalizing"
    ]
    
    progress_text = ""
    for i, step_name in enumerate(steps[:total_steps]):
        if i < step:
            progress_text += f"✅ {step_name}\n"
        elif i == step:
            progress_text += f"⏳ {step_name}\n"
        else:
            progress_text += f"⏬ {step_name}\n"
    
    embed.add_field(name="Progress", value=progress_text, inline=False)
    
    try:
        await message.edit(embed=embed)
    except discord.HTTPException:
        logger.warning("Failed to update progress")

async def send_error(message: discord.Message, title: str, description: str):
    """Send error embed."""
    embed = discord.Embed(
        title=f"❌ {title}",
        description=description,
        color=discord.Color.red()
    )
    try:
        await message.edit(embed=embed)
    except discord.HTTPException:
        logger.warning("Failed to send error")

# ============================================================================
# COMMANDS
# ============================================================================

@bot.tree.command(
    name="setup",
    description="AI-powered server generator. Describe your server and let AI create it."
)
@app_commands.describe(
    description="Describe what kind of server you want (e.g., 'Gaming server with trading and events')"
)
async def setup(interaction: discord.Interaction, description: str):
    """Generate and create a Discord server based on user description."""
    
    if not interaction.user.guild_permissions.administrator:
        embed = discord.Embed(
            title="❌ Permission Denied",
            description="Only server administrators can use this command.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        logger.info(f"Non-admin user {interaction.user} tried to use /setup")
        return
    
    if len(description) < 10:
        embed = discord.Embed(
            title="❌ Invalid Description",
            description="Please provide a longer description (at least 10 characters).",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    await interaction.response.defer()
    
    db.save_setup(interaction.guild.id, interaction.user.id, description)
    
    progress_embed = discord.Embed(
        title="🔧 Server Setup in Progress",
        color=BOT_COLOR
    )
    progress_message = await interaction.followup.send(embed=progress_embed)
    
    try:
        await update_progress(progress_message, "📝 Analyzing Description...", 0, 6)
        await update_progress(progress_message, "🤖 Generating Server Structure...", 1, 6)
        
        logger.info(f"Generating structure: {description}")
        structure = await AIServerGenerator.generate_structure(description)
        
        if not structure:
            await send_error(
                progress_message,
                "Generation Failed",
                "The AI couldn't generate a valid structure. Try a clearer description."
            )
            return
        
        server_name = structure.get("server_name", "New Server")
        
        await update_progress(progress_message, "👥 Creating Roles...", 2, 6)
        
        existing_roles = {role.name.lower() for role in interaction.guild.roles}
        created_roles, role_errors = await ServerCreator.create_roles(
            interaction.guild,
            structure.get("roles", []),
            existing_roles
        )
        
        for role in created_roles:
            db.add_role(interaction.guild.id, role.id, role.name)
        
        await update_progress(progress_message, "📂 Creating Categories...", 3, 6)
        
        existing_channels = {channel.name.lower() for channel in interaction.guild.channels}
        created_structure, channel_errors = await ServerCreator.create_categories_and_channels(
            interaction.guild,
            structure.get("categories", []),
            existing_channels
        )
        
        for category, channels in created_structure:
            for channel in channels:
                db.add_channel(
                    interaction.guild.id,
                    channel.id,
                    channel.name,
                    "voice" if isinstance(channel, discord.VoiceChannel) else "text"
                )
        
        await update_progress(progress_message, "✅ Setup Complete!", 5, 6)
        await asyncio.sleep(1)
        
        summary_embed = discord.Embed(
            title="✅ Server Setup Complete!",
            description=f"Successfully set up **{server_name}**",
            color=discord.Color.green()
        )
        
        summary_embed.add_field(
            name="📊 Summary",
            value=f"**Roles Created:** {len(created_roles)}\n"
                  f"**Categories Created:** {len(created_structure)}\n"
                  f"**Channels Created:** {sum(len(channels) for _, channels in created_structure)}",
            inline=False
        )
        
        if role_errors or channel_errors:
            all_errors = role_errors + channel_errors
            error_text = "\n".join(all_errors[:5])
            if len(all_errors) > 5:
                error_text += f"\n... and {len(all_errors) - 5} more"
            summary_embed.add_field(name="⚠️ Notes", value=error_text, inline=False)
        
        summary_embed.add_field(
            name="🔄 Other Commands",
            value="• `/undo_setup` - Remove all created elements\n"
                  "• `/analyze_server` - Get improvement suggestions\n"
                  "• `/setup_templates` - Browse pre-made templates",
            inline=False
        )
        
        summary_embed.set_footer(text=f"Setup by {interaction.user}")
        await progress_message.edit(embed=summary_embed)
        
    except Exception as e:
        logger.error(f"Setup error: {e}", exc_info=True)
        await send_error(progress_message, "Setup Error", f"Error: {str(e)}")

@bot.tree.command(
    name="undo_setup",
    description="Remove all channels and roles created by the most recent /setup."
)
async def undo_setup(interaction: discord.Interaction):
    """Undo the most recent server setup."""
    
    if not interaction.user.guild_permissions.administrator:
        embed = discord.Embed(
            title="❌ Permission Denied",
            description="Only server administrators can use this command.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    description = db.get_setup_description(interaction.guild.id)
    
    if not description:
        embed = discord.Embed(
            title="❌ No Setup Found",
            description="There's no recorded setup to undo for this server.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    await interaction.response.defer()
    
    progress_embed = discord.Embed(title="🔄 Undoing Setup...", color=BOT_COLOR)
    progress_message = await interaction.followup.send(embed=progress_embed)
    
    try:
        created_roles = db.get_created_roles(interaction.guild.id)
        created_channels = db.get_created_channels(interaction.guild.id)
        
        if not created_roles and not created_channels:
            embed = discord.Embed(
                title="❌ Nothing to Undo",
                description="No channels or roles were recorded.",
                color=discord.Color.red()
            )
            await progress_message.edit(embed=embed)
            return
        
        role_ids = [role[0] for role in created_roles]
        channel_ids = [channel[0] for channel in created_channels]
        
        channels_deleted, channels_skipped = await ServerCreator.delete_channels(
            interaction.guild,
            channel_ids
        )
        
        roles_deleted, roles_skipped = await ServerCreator.delete_roles(
            interaction.guild,
            role_ids
        )
        
        db.delete_setup(interaction.guild.id)
        
        summary_embed = discord.Embed(
            title="✅ Setup Undone!",
            description="All created elements have been removed.",
            color=discord.Color.green()
        )
        
        summary_embed.add_field(
            name="📊 Summary",
            value=f"**Channels Deleted:** {channels_deleted}\n"
                  f"**Roles Deleted:** {roles_deleted}\n\n"
                  f"**Channels Skipped:** {channels_skipped}\n"
                  f"**Roles Skipped:** {roles_skipped}",
            inline=False
        )
        
        await progress_message.edit(embed=summary_embed)
        
    except Exception as e:
        logger.error(f"Undo error: {e}")
        await send_error(progress_message, "Undo Error", f"Error: {str(e)}")

@bot.tree.command(
    name="analyze_server",
    description="Analyze your server and get improvement suggestions."
)
async def analyze_server(interaction: discord.Interaction):
    """Analyze the server and suggest improvements."""
    
    if not interaction.user.guild_permissions.administrator:
        embed = discord.Embed(
            title="❌ Permission Denied",
            description="Only server administrators can use this command.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    await interaction.response.defer()
    
    try:
        guild = interaction.guild
        text_channels = [c for c in guild.channels if isinstance(c, discord.TextChannel)]
        voice_channels = [c for c in guild.channels if isinstance(c, discord.VoiceChannel)]
        categories = [c for c in guild.channels if isinstance(c, discord.CategoryChannel)]
        
        text_channel_names = {c.name.lower() for c in text_channels}
        suggestions = []
        
        if not any(name in text_channel_names for name in ["rules", "rule", "guidelines"]):
            suggestions.append("📜 **Missing Rules Channel** - Add a #rules channel")
        
        if not any(name in text_channel_names for name in ["announcements", "announcement", "news"]):
            suggestions.append("📢 **Missing Announcements Channel** - Add an #announcements channel")
        
        if not any(name in text_channel_names for name in ["general", "chat"]):
            suggestions.append("💬 **Missing General Chat** - Add a #general channel")
        
        if not any(name in text_channel_names for name in ["moderation", "mod-logs", "modlogs", "logs"]):
            suggestions.append("🔐 **No Moderation Logs** - Consider adding a mod-logs channel")
        
        if len(voice_channels) == 0:
            suggestions.append("🎙️ **No Voice Channels** - Add voice channels for members")
        
        roles = [r for r in guild.roles if r.name != "@everyone"]
        if len(roles) < 2:
            suggestions.append("👥 **Limited Roles** - Create more roles for better organization")
        
        if guild.member_count > 50 and len(voice_channels) < 2:
            suggestions.append("🎙️ **Consider More Voice Channels** - Multiple channels help")
        
        if len(categories) == 0:
            suggestions.append("📂 **No Categories** - Organize channels with categories")
        
        if guild.verification_level == discord.VerificationLevel.none:
            suggestions.append("✅ **Enable Verification** - Raise verification level")
        
        embed = discord.Embed(
            title="📊 Server Analysis",
            description=f"Analysis for **{guild.name}**",
            color=BOT_COLOR
        )
        
        embed.add_field(
            name="📈 Statistics",
            value=f"**Members:** {guild.member_count}\n"
                  f"**Text Channels:** {len(text_channels)}\n"
                  f"**Voice Channels:** {len(voice_channels)}\n"
                  f"**Categories:** {len(categories)}\n"
                  f"**Roles:** {len(roles)}",
            inline=False
        )
        
        if suggestions:
            suggestion_text = "\n".join(suggestions)
            embed.add_field(name="💡 Suggestions", value=suggestion_text, inline=False)
        else:
            embed.add_field(name="✅ Status", value="Your server looks well-organized! 🎉", inline=False)
        
        embed.set_footer(text=f"Analysis by {interaction.user}")
        
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        logger.error(f"Analysis error: {e}")

class TemplateSelect(discord.ui.Select):
    """Select menu for templates."""
    
    def __init__(self):
        options = [
            discord.SelectOption(label="Gaming", value="Gaming", emoji="🎮"),
            discord.SelectOption(label="Community", value="Community", emoji="👥"),
            discord.SelectOption(label="Content Creator", value="Content Creator", emoji="🎬"),
            discord.SelectOption(label="Business", value="Business", emoji="💼"),
            discord.SelectOption(label="Minecraft", value="Minecraft", emoji="⛏️"),
        ]
        super().__init__(placeholder="Choose a template...", min_values=1, max_values=1, options=options)
    
    async def callback(self, interaction: discord.Interaction):
        """Handle template selection."""
        template_name = self.values[0]
        template = TEMPLATES.get(template_name)
        
        if not template:
            await interaction.response.send_message("Template not found.", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        db.save_setup(
            interaction.guild.id,
            interaction.user.id,
            f"Template: {template_name}"
        )
        
        progress_embed = discord.Embed(title="🔧 Setting Up Template", color=BOT_COLOR)
        progress_message = await interaction.followup.send(embed=progress_embed)
        
        try:
            existing_roles = {role.name.lower() for role in interaction.guild.roles}
            created_roles, role_errors = await ServerCreator.create_roles(
                interaction.guild,
                template.get("roles", []),
                existing_roles
            )
            
            for role in created_roles:
                db.add_role(interaction.guild.id, role.id, role.name)
            
            existing_channels = {channel.name.lower() for channel in interaction.guild.channels}
            created_structure, channel_errors = await ServerCreator.create_categories_and_channels(
                interaction.guild,
                template.get("categories", []),
                existing_channels
            )
            
            for category, channels in created_structure:
                for channel in channels:
                    db.add_channel(
                        interaction.guild.id,
                        channel.id,
                        channel.name,
                        "voice" if isinstance(channel, discord.VoiceChannel) else "text"
                    )
            
            await asyncio.sleep(1)
            
            summary_embed = discord.Embed(
                title="✅ Template Setup Complete!",
                description=f"Set up **{template_name}** template",
                color=discord.Color.green()
            )
            
            summary_embed.add_field(
                name="📊 Summary",
                value=f"**Roles Created:** {len(created_roles)}\n"
                      f"**Categories Created:** {len(created_structure)}\n"
                      f"**Channels Created:** {sum(len(channels) for _, channels in created_structure)}",
                inline=False
            )
            
            summary_embed.set_footer(text=f"Setup by {interaction.user}")
            await progress_message.edit(embed=summary_embed)
            
        except Exception as e:
            logger.error(f"Template error: {e}")
            await send_error(progress_message, "Setup Error", f"Error: {str(e)}")

class TemplateSelectView(discord.ui.View):
    """View for template selection."""
    
    def __init__(self):
        super().__init__()
        self.add_item(TemplateSelect())

@bot.tree.command(
    name="setup_templates",
    description="Choose a built-in template to set up your server instantly."
)
async def setup_templates(interaction: discord.Interaction):
    """Show template selection menu."""
    
    if not interaction.user.guild_permissions.administrator:
        embed = discord.Embed(
            title="❌ Permission Denied",
            description="Only server administrators can use this command.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    embed = discord.Embed(
        title="🎨 Server Templates",
        description="Select a template to set up your server instantly!",
        color=BOT_COLOR
    )
    
    embed.add_field(
        name="🎮 Gaming",
        value="Perfect for gaming communities with trading, events, and voice chats.",
        inline=False
    )
    
    embed.add_field(
        name="👥 Community",
        value="Great for general communities with welcoming channels and voice.",
        inline=False
    )
    
    embed.add_field(
        name="🎬 Content Creator",
        value="Ideal for content creators with sponsor lounge and fan channels.",
        inline=False
    )
    
    embed.add_field(
        name="💼 Business",
        value="Professional structure with management, projects, and meetings.",
        inline=False
    )
    
    embed.add_field(
        name="⛏️ Minecraft",
        value="Gaming-specific with trading, events, and staff channels.",
        inline=False
    )
    
    view = TemplateSelectView()
    
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

# ============================================================================
# MAIN
# ============================================================================

async def main():
    """Start the bot."""
    async with bot:
        await bot.start(DISCORD_TOKEN)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
