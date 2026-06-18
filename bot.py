"""
Discord Server Setup Bot - Professional Edition
Pre-built templates for professional Discord servers with detailed configurations,
role permissions, read-only channels, admin-only channels, and custom colors.
"""

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
from typing import List, Dict, Tuple

# ============================================================================
# CONFIGURATION
# ============================================================================

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

BOT_COLOR = 0x5865F2
DATABASE_FILE = "server_setup.db"

# Role colors (hex codes)
COLORS = {
    "admin": 0xFF0000,      # Red
    "moderator": 0xFF9900,  # Orange
    "staff": 0xFFFF00,      # Yellow
    "members": 0x00FF00,    # Green
    "vip": 0x9900FF,        # Purple
    "verified": 0x00FFFF,   # Cyan
    "support": 0xFF00FF,    # Magenta
    "developer": 0x0099FF,  # Blue
}

# ============================================================================
# PROFESSIONAL TEMPLATES
# ============================================================================

TEMPLATES = {
    "Professional": {
        "server_name": "Professional Server",
        "description": "A complete professional workspace with announcements, projects, and team communication.",
        "roles": [
            {
                "name": "Owner",
                "color": COLORS["admin"],
                "permissions": ["administrator"]
            },
            {
                "name": "Management",
                "color": COLORS["moderator"],
                "permissions": ["manage_messages", "manage_roles", "manage_channels", "manage_guild"]
            },
            {
                "name": "Team Lead",
                "color": COLORS["staff"],
                "permissions": ["manage_messages", "kick_members"]
            },
            {
                "name": "Team Member",
                "color": COLORS["members"],
                "permissions": []
            },
            {
                "name": "Intern",
                "color": COLORS["verified"],
                "permissions": []
            }
        ],
        "categories": [
            {
                "name": "📢 Announcements",
                "channels": [
                    {
                        "name": "announcements",
                        "type": "text",
                        "read_only": True,
                        "admin_only": False,
                        "description": "Important company announcements"
                    },
                    {
                        "name": "updates",
                        "type": "text",
                        "read_only": True,
                        "admin_only": False,
                        "description": "Project and system updates"
                    },
                    {
                        "name": "policy-changes",
                        "type": "text",
                        "read_only": True,
                        "admin_only": False,
                        "description": "New policies and guidelines"
                    }
                ]
            },
            {
                "name": "💼 Management",
                "channels": [
                    {
                        "name": "leadership",
                        "type": "text",
                        "read_only": False,
                        "admin_only": True,
                        "description": "Leadership discussions"
                    },
                    {
                        "name": "strategy",
                        "type": "text",
                        "read_only": False,
                        "admin_only": True,
                        "description": "Strategic planning and decisions"
                    },
                    {
                        "name": "performance-reviews",
                        "type": "text",
                        "read_only": False,
                        "admin_only": True,
                        "description": "Employee performance discussions"
                    }
                ]
            },
            {
                "name": "👥 Teams",
                "channels": [
                    {
                        "name": "general",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "General team discussion"
                    },
                    {
                        "name": "projects",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Project management and tracking"
                    },
                    {
                        "name": "team-voice",
                        "type": "voice",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Team voice chat"
                    },
                    {
                        "name": "meetings",
                        "type": "voice",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Meeting room"
                    }
                ]
            },
            {
                "name": "📚 Resources",
                "channels": [
                    {
                        "name": "documentation",
                        "type": "text",
                        "read_only": True,
                        "admin_only": False,
                        "description": "Technical documentation"
                    },
                    {
                        "name": "knowledge-base",
                        "type": "text",
                        "read_only": True,
                        "admin_only": False,
                        "description": "Company knowledge base"
                    },
                    {
                        "name": "templates",
                        "type": "text",
                        "read_only": True,
                        "admin_only": False,
                        "description": "Shared templates and resources"
                    }
                ]
            },
            {
                "name": "💬 Social",
                "channels": [
                    {
                        "name": "watercooler",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Off-topic casual chat"
                    },
                    {
                        "name": "celebrations",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Team celebrations and milestones"
                    },
                    {
                        "name": "lounge",
                        "type": "voice",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Casual voice hang out"
                    }
                ]
            }
        ]
    },
    
    "Gaming Community": {
        "server_name": "Gaming Community",
        "description": "A vibrant gaming community with guilds, tournaments, and social channels.",
        "roles": [
            {
                "name": "Owner",
                "color": COLORS["admin"],
                "permissions": ["administrator"]
            },
            {
                "name": "Moderator",
                "color": COLORS["moderator"],
                "permissions": ["manage_messages", "kick_members", "ban_members", "manage_channels"]
            },
            {
                "name": "Guild Master",
                "color": COLORS["staff"],
                "permissions": ["manage_messages", "kick_members"]
            },
            {
                "name": "Verified Member",
                "color": COLORS["verified"],
                "permissions": []
            },
            {
                "name": "Streamer",
                "color": COLORS["vip"],
                "permissions": []
            }
        ],
        "categories": [
            {
                "name": "📢 Server",
                "channels": [
                    {
                        "name": "announcements",
                        "type": "text",
                        "read_only": True,
                        "admin_only": False,
                        "description": "Server news and announcements"
                    },
                    {
                        "name": "rules",
                        "type": "text",
                        "read_only": True,
                        "admin_only": False,
                        "description": "Server rules and guidelines"
                    },
                    {
                        "name": "moderation-logs",
                        "type": "text",
                        "read_only": True,
                        "admin_only": True,
                        "description": "Moderation action logs"
                    }
                ]
            },
            {
                "name": "🎮 Games",
                "channels": [
                    {
                        "name": "general",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "General gaming discussion"
                    },
                    {
                        "name": "game-lfg",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Looking for group / team recruitment"
                    },
                    {
                        "name": "tournaments",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Tournament information and signups"
                    },
                    {
                        "name": "gaming-voice-1",
                        "type": "voice",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Gaming voice chat"
                    },
                    {
                        "name": "gaming-voice-2",
                        "type": "voice",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Gaming voice chat"
                    }
                ]
            },
            {
                "name": "👥 Guilds & Teams",
                "channels": [
                    {
                        "name": "guild-announcements",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Guild news and updates"
                    },
                    {
                        "name": "guild-recruitment",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Guild recruitment and applications"
                    },
                    {
                        "name": "guild-voice",
                        "type": "voice",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Guild voice chat"
                    }
                ]
            },
            {
                "name": "📺 Streamers",
                "channels": [
                    {
                        "name": "stream-announcements",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Streamer schedule announcements"
                    },
                    {
                        "name": "streaming-tips",
                        "type": "text",
                        "read_only": True,
                        "admin_only": False,
                        "description": "Streaming guides and tips"
                    }
                ]
            },
            {
                "name": "💬 Community",
                "channels": [
                    {
                        "name": "introductions",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Introduce yourself"
                    },
                    {
                        "name": "general-chat",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Off-topic discussion"
                    },
                    {
                        "name": "lounge",
                        "type": "voice",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Casual hang out"
                    }
                ]
            }
        ]
    },

    "Content Creator": {
        "server_name": "Creator Hub",
        "description": "A dedicated space for content creators with community engagement, sponsorships, and collaboration.",
        "roles": [
            {
                "name": "Creator",
                "color": COLORS["admin"],
                "permissions": ["administrator"]
            },
            {
                "name": "Manager",
                "color": COLORS["moderator"],
                "permissions": ["manage_messages", "manage_roles", "manage_channels"]
            },
            {
                "name": "Editor",
                "color": COLORS["staff"],
                "permissions": ["manage_messages"]
            },
            {
                "name": "Collaborator",
                "color": COLORS["vip"],
                "permissions": []
            },
            {
                "name": "Sponsor",
                "color": COLORS["vip"],
                "permissions": []
            },
            {
                "name": "Community Member",
                "color": COLORS["verified"],
                "permissions": []
            }
        ],
        "categories": [
            {
                "name": "📢 Creator Info",
                "channels": [
                    {
                        "name": "announcements",
                        "type": "text",
                        "read_only": True,
                        "admin_only": False,
                        "description": "Upload schedule and news"
                    },
                    {
                        "name": "content-calendar",
                        "type": "text",
                        "read_only": True,
                        "admin_only": False,
                        "description": "Upcoming content schedule"
                    },
                    {
                        "name": "creator-studio",
                        "type": "text",
                        "read_only": False,
                        "admin_only": True,
                        "description": "Creator's private workspace"
                    }
                ]
            },
            {
                "name": "🎬 Content",
                "channels": [
                    {
                        "name": "content-ideas",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Brainstorm and suggest content"
                    },
                    {
                        "name": "collaboration",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Collaboration opportunities"
                    },
                    {
                        "name": "behind-the-scenes",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Behind the scenes content"
                    }
                ]
            },
            {
                "name": "🤝 Sponsorships",
                "channels": [
                    {
                        "name": "sponsor-info",
                        "type": "text",
                        "read_only": True,
                        "admin_only": False,
                        "description": "Sponsor information and perks"
                    },
                    {
                        "name": "sponsor-lounge",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Exclusive sponsor chat"
                    },
                    {
                        "name": "sponsorship-deals",
                        "type": "text",
                        "read_only": False,
                        "admin_only": True,
                        "description": "Sponsorship negotiations"
                    }
                ]
            },
            {
                "name": "👥 Community",
                "channels": [
                    {
                        "name": "general",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "General community chat"
                    },
                    {
                        "name": "fan-theories",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Community theories and discussions"
                    },
                    {
                        "name": "fan-art",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Community fan art showcase"
                    }
                ]
            },
            {
                "name": "🎙️ Voice",
                "channels": [
                    {
                        "name": "hangout",
                        "type": "voice",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Community hangout voice"
                    },
                    {
                        "name": "recording",
                        "type": "voice",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Recording sessions"
                    }
                ]
            }
        ]
    },

    "Community Server": {
        "server_name": "Community Hub",
        "description": "A welcoming community server with discussion forums, events, and social activities.",
        "roles": [
            {
                "name": "Admin",
                "color": COLORS["admin"],
                "permissions": ["administrator"]
            },
            {
                "name": "Moderator",
                "color": COLORS["moderator"],
                "permissions": ["manage_messages", "kick_members", "ban_members", "manage_channels"]
            },
            {
                "name": "Event Organizer",
                "color": COLORS["staff"],
                "permissions": ["manage_messages"]
            },
            {
                "name": "Verified",
                "color": COLORS["verified"],
                "permissions": []
            },
            {
                "name": "Member",
                "color": COLORS["members"],
                "permissions": []
            }
        ],
        "categories": [
            {
                "name": "📜 Welcome",
                "channels": [
                    {
                        "name": "welcome",
                        "type": "text",
                        "read_only": True,
                        "admin_only": False,
                        "description": "Welcome message and rules"
                    },
                    {
                        "name": "introductions",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Introduce yourself to the community"
                    },
                    {
                        "name": "announcements",
                        "type": "text",
                        "read_only": True,
                        "admin_only": False,
                        "description": "Important announcements"
                    }
                ]
            },
            {
                "name": "💬 Discussion",
                "channels": [
                    {
                        "name": "general",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "General discussion"
                    },
                    {
                        "name": "off-topic",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Off-topic conversations"
                    },
                    {
                        "name": "questions",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Ask questions to the community"
                    }
                ]
            },
            {
                "name": "🎉 Events",
                "channels": [
                    {
                        "name": "events",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Event announcements and sign-ups"
                    },
                    {
                        "name": "game-nights",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Game night coordination"
                    },
                    {
                        "name": "events-voice",
                        "type": "voice",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Voice for events"
                    }
                ]
            },
            {
                "name": "🏆 Spotlight",
                "channels": [
                    {
                        "name": "achievements",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Share community achievements"
                    },
                    {
                        "name": "member-spotlight",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Featured member of the month"
                    }
                ]
            },
            {
                "name": "🎙️ Voice",
                "channels": [
                    {
                        "name": "general-voice",
                        "type": "voice",
                        "read_only": False,
                        "admin_only": False,
                        "description": "General voice chat"
                    },
                    {
                        "name": "lounge",
                        "type": "voice",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Casual hangout voice"
                    }
                ]
            },
            {
                "name": "🛡️ Moderation",
                "channels": [
                    {
                        "name": "reports",
                        "type": "text",
                        "read_only": False,
                        "admin_only": True,
                        "description": "User reports"
                    },
                    {
                        "name": "mod-logs",
                        "type": "text",
                        "read_only": True,
                        "admin_only": True,
                        "description": "Moderation action logs"
                    }
                ]
            }
        ]
    }
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
                    template_name TEXT NOT NULL,
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
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS created_channels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    channel_id INTEGER NOT NULL,
                    channel_name TEXT NOT NULL,
                    channel_type TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            logger.info("Database initialized")
        except Exception as e:
            logger.error(f"Database init error: {e}")
        finally:
            conn.close()
    
    def save_setup(self, guild_id: int, user_id: int, template_name: str):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM setups WHERE guild_id = ?", (guild_id,))
            cursor.execute("DELETE FROM created_roles WHERE guild_id = ?", (guild_id,))
            cursor.execute("DELETE FROM created_channels WHERE guild_id = ?", (guild_id,))
            cursor.execute(
                "INSERT INTO setups (guild_id, user_id, template_name) VALUES (?, ?, ?)",
                (guild_id, user_id, template_name)
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
# SERVER CREATOR
# ============================================================================

class ServerCreator:
    """Creates Discord server elements with advanced configuration."""
    
    @staticmethod
    async def create_roles(guild: discord.Guild, roles: List[Dict]) -> Tuple[List[discord.Role], List[str]]:
        """Create roles with colors and permissions."""
        created_roles = []
        errors = []
        existing_roles = {role.name.lower() for role in guild.roles}
        
        for role_data in roles:
            try:
                role_name = role_data.get("name", "").strip()
                
                if not role_name or role_name.lower() in existing_roles:
                    continue
                
                color = role_data.get("color", discord.Color.default())
                permissions = discord.Permissions()
                
                for perm in role_data.get("permissions", []):
                    if perm == "administrator":
                        permissions.administrator = True
                    elif perm == "manage_messages":
                        permissions.manage_messages = True
                    elif perm == "manage_roles":
                        permissions.manage_roles = True
                    elif perm == "manage_channels":
                        permissions.manage_channels = True
                    elif perm == "manage_guild":
                        permissions.manage_guild = True
                    elif perm == "kick_members":
                        permissions.kick_members = True
                    elif perm == "ban_members":
                        permissions.ban_members = True
                
                new_role = await guild.create_role(
                    name=role_name,
                    permissions=permissions,
                    color=color,
                    reason="Server setup by user"
                )
                
                created_roles.append(new_role)
                existing_roles.add(role_name.lower())
                logger.info(f"Created role: {role_name}")
                
            except discord.Forbidden:
                errors.append(f"Failed: No permission to create role '{role_name}'")
            except Exception as e:
                errors.append(f"Failed: Role creation error")
        
        return created_roles, errors
    
    @staticmethod
    async def create_categories_and_channels(
        guild: discord.Guild,
        categories: List[Dict],
        created_roles: List[discord.Role]
    ) -> Tuple[List[Tuple], List[str]]:
        """Create categories and channels with permissions and read-only settings."""
        created_structure = []
        errors = []
        existing_channels = {channel.name.lower() for channel in guild.channels}
        
        # Find admin and everyone roles
        admin_role = discord.utils.find(lambda r: r.name in ["Owner", "Admin"], guild.roles)
        everyone_role = guild.default_role
        
        for category_data in categories:
            try:
                category_name = category_data.get("name", "").strip()
                
                if not category_name:
                    continue
                
                category = await guild.create_category(
                    name=category_name,
                    reason="Server setup by user"
                )
                
                created_channels = []
                
                for channel_data in category_data.get("channels", []):
                    try:
                        channel_name = channel_data.get("name", "").strip()
                        channel_type = channel_data.get("type", "text").lower()
                        is_read_only = channel_data.get("read_only", False)
                        is_admin_only = channel_data.get("admin_only", False)
                        
                        if not channel_name or channel_type not in ["text", "voice"]:
                            continue
                        
                        if channel_name.lower() in existing_channels:
                            errors.append(f"Skipped: Channel '{channel_name}' already exists")
                            continue
                        
                        # Create channel
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
                        
                        # Set permissions
                        overwrites = {}
                        
                        if is_admin_only and admin_role:
                            # Admin only: deny everyone, allow admin
                            overwrites[everyone_role] = discord.PermissionOverwrite(view_channel=False)
                            overwrites[admin_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)
                        elif is_read_only:
                            # Read only: everyone can view but not send
                            overwrites[everyone_role] = discord.PermissionOverwrite(send_messages=False, send_tts_messages=False)
                        
                        if overwrites:
                            await channel.edit(overwrites=overwrites)
                        
                        created_channels.append(channel)
                        existing_channels.add(channel_name.lower())
                        logger.info(f"Created {channel_type} channel: {channel_name}")
                        
                    except Exception as e:
                        errors.append(f"Failed: Channel '{channel_data.get('name')}' creation error")
                
                created_structure.append((category, created_channels))
                
            except Exception as e:
                errors.append(f"Failed: Category creation error")
        
        return created_structure, errors
    
    @staticmethod
    async def delete_roles(guild: discord.Guild, role_ids: List[int]) -> Tuple[int, int]:
        """Delete roles."""
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
        """Delete channels."""
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
        "👥 Creating Roles",
        "📂 Creating Categories",
        "📨 Creating Channels",
        "🔐 Setting Permissions",
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
# TEMPLATE SELECT
# ============================================================================

class TemplateSelect(discord.ui.Select):
    """Select menu for templates."""
    
    def __init__(self):
        options = [
            discord.SelectOption(label="Professional", value="Professional", emoji="💼"),
            discord.SelectOption(label="Gaming Community", value="Gaming Community", emoji="🎮"),
            discord.SelectOption(label="Content Creator", value="Content Creator", emoji="🎬"),
            discord.SelectOption(label="Community Server", value="Community Server", emoji="👥"),
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
            template_name
        )
        
        progress_embed = discord.Embed(title="🔧 Setting Up Template", color=BOT_COLOR)
        progress_message = await interaction.followup.send(embed=progress_embed)
        
        try:
            await update_progress(progress_message, "👥 Creating Roles...", 0, 5)
            
            created_roles, role_errors = await ServerCreator.create_roles(
                interaction.guild,
                template.get("roles", [])
            )
            
            for role in created_roles:
                db.add_role(interaction.guild.id, role.id, role.name)
            
            await update_progress(progress_message, "📂 Creating Categories...", 1, 5)
            
            created_structure, channel_errors = await ServerCreator.create_categories_and_channels(
                interaction.guild,
                template.get("categories", []),
                created_roles
            )
            
            for category, channels in created_structure:
                for channel in channels:
                    db.add_channel(
                        interaction.guild.id,
                        channel.id,
                        channel.name,
                        "voice" if isinstance(channel, discord.VoiceChannel) else "text"
                    )
            
            await update_progress(progress_message, "✅ Setup Complete!", 4, 5)
            
            summary_embed = discord.Embed(
                title="✅ Server Setup Complete!",
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
            
            if role_errors or channel_errors:
                all_errors = role_errors + channel_errors
                error_text = "\n".join(all_errors[:3])
                if len(all_errors) > 3:
                    error_text += f"\n... and {len(all_errors) - 3} more"
                summary_embed.add_field(name="⚠️ Notes", value=error_text, inline=False)
            
            summary_embed.add_field(
                name="✨ Features",
                value="✓ Read-only announcement channels\n"
                      "✓ Admin-only management channels\n"
                      "✓ Custom role colors and permissions\n"
                      "✓ Professional organization",
                inline=False
            )
            
            summary_embed.add_field(
                name="🔄 Other Commands",
                value="• `/undo_setup` - Remove all created elements\n"
                      "• `/show_templates` - Browse templates again",
                inline=False
            )
            
            summary_embed.set_footer(text=f"Setup by {interaction.user}")
            await progress_message.edit(embed=summary_embed)
            
        except Exception as e:
            logger.error(f"Template error: {e}", exc_info=True)
            await send_error(progress_message, "Setup Error", f"Error: {str(e)}")

class TemplateSelectView(discord.ui.View):
    """View for template selection."""
    
    def __init__(self):
        super().__init__()
        self.add_item(TemplateSelect())

# ============================================================================
# COMMANDS
# ============================================================================

@bot.tree.command(
    name="show_templates",
    description="Browse and apply professional Discord server templates."
)
async def show_templates(interaction: discord.Interaction):
    """Show available templates."""
    
    if not interaction.user.guild_permissions.administrator:
        embed = discord.Embed(
            title="❌ Permission Denied",
            description="Only server administrators can use this command.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    embed = discord.Embed(
        title="🎨 Professional Server Templates",
        description="Select a template to instantly set up your server with roles, channels, and permissions.",
        color=BOT_COLOR
    )
    
    embed.add_field(
        name="💼 Professional",
        value="Complete workspace with management channels, teams, announcements, and resources.",
        inline=False
    )
    
    embed.add_field(
        name="🎮 Gaming Community",
        value="Gaming-focused with guilds, tournaments, streamers, and gaming voice channels.",
        inline=False
    )
    
    embed.add_field(
        name="🎬 Content Creator",
        value="Creator hub with collaboration, sponsorships, and community engagement channels.",
        inline=False
    )
    
    embed.add_field(
        name="👥 Community Server",
        value="Welcoming community with discussions, events, spotlights, and moderation tools.",
        inline=False
    )
    
    embed.add_field(
        name="✨ Features",
        value="✓ Pre-configured roles with custom colors\n"
              "✓ Read-only announcement channels\n"
              "✓ Admin-only management channels\n"
              "✓ Proper permission setup\n"
              "✓ Professional channel organization",
        inline=False
    )
    
    view = TemplateSelectView()
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

@bot.tree.command(
    name="undo_setup",
    description="Remove all channels and roles created by setup."
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
