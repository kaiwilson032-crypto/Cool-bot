"""
All In One Setup - Discord Bot
Production-ready Discord server setup bot with template system, undo/delete functionality
Python 3.12+ | discord.py 2.x
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Any

# Load environment variables before any discord imports
try:
    from dotenv import load_dotenv
except ImportError:
    print("ERROR: python-dotenv not installed. Run: pip install python-dotenv")
    sys.exit(1)

# Suppress discord.py audio warnings
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

try:
    import discord
    from discord import app_commands, Interaction, ButtonStyle, SelectOption
    from discord.ext import commands, tasks
except ImportError as e:
    print(f"ERROR: discord.py not installed. Run: pip install discord.py")
    sys.exit(1)

# ============================================================================
# CONFIGURATION
# ============================================================================

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
BOT_VERSION = "1.0.0"
BOT_NAME = "All In One Setup"
TEMPLATES_DIR = Path("templates")
DATA_DIR = Path("data")

if not TOKEN:
    print("ERROR: DISCORD_TOKEN not found in .env file")
    sys.exit(1)

# ============================================================================
# LOGGING
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# INTENTS & BOT SETUP
# ============================================================================

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="/", intents=intents)

# ============================================================================
# GLOBAL STATE
# ============================================================================

# Track setup operations for undo functionality
setup_history: Dict[int, Dict[str, Any]] = {}  # guild_id -> operation data
bot_start_time = datetime.now()


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def ensure_directories() -> None:
    """Ensure required directories exist."""
    TEMPLATES_DIR.mkdir(exist_ok=True)
    DATA_DIR.mkdir(exist_ok=True)
    logger.info(f"Directories ensured: {TEMPLATES_DIR}, {DATA_DIR}")


def load_example_templates() -> None:
    """Create example template files if none exist."""
    if list(TEMPLATES_DIR.glob("*.json")):
        return
    
    templates = {
        "gaming.json": {
            "name": "Gaming Server",
            "description": "Complete setup for a gaming community",
            "roles": [
                {"name": "Owner", "color": discord.Color.red().value, "permissions": ["administrator"]},
                {"name": "Staff", "color": discord.Color.orange().value, 
                 "permissions": ["manage_channels", "manage_messages", "kick_members", "moderate_members"]},
                {"name": "Member", "color": discord.Color.blue().value, "permissions": []},
                {"name": "Muted", "color": discord.Color.greyple().value, "permissions": []}
            ],
            "categories": [
                {
                    "name": "📋 General",
                    "channels": [
                        {"name": "announcements", "type": "text", "read_only_staff": False},
                        {"name": "general", "type": "text", "read_only_staff": False},
                        {"name": "introductions", "type": "text", "read_only_staff": False}
                    ]
                },
                {
                    "name": "🎮 Gaming",
                    "channels": [
                        {"name": "gaming-chat", "type": "text", "read_only_staff": False},
                        {"name": "gaming-voice", "type": "voice", "read_only_staff": False},
                        {"name": "raid-planning", "type": "text", "read_only_staff": False},
                        {"name": "raid-voice", "type": "voice", "read_only_staff": False}
                    ]
                },
                {
                    "name": "👥 Community",
                    "channels": [
                        {"name": "events", "type": "text", "read_only_staff": False},
                        {"name": "media", "type": "text", "read_only_staff": False},
                        {"name": "giveaways", "type": "text", "read_only_staff": False}
                    ]
                },
                {
                    "name": "🔒 Staff",
                    "channels": [
                        {"name": "staff-chat", "type": "text", "read_only_staff": True},
                        {"name": "logs", "type": "text", "read_only_staff": True},
                        {"name": "moderation", "type": "text", "read_only_staff": True}
                    ]
                }
            ]
        },
        "minecraft.json": {
            "name": "Minecraft Server",
            "description": "Organized server for Minecraft players",
            "roles": [
                {"name": "Owner", "color": discord.Color.red().value, "permissions": ["administrator"]},
                {"name": "Admin", "color": discord.Color.orange().value, 
                 "permissions": ["manage_channels", "manage_messages", "kick_members"]},
                {"name": "Builder", "color": discord.Color.blue().value, "permissions": []},
                {"name": "Member", "color": discord.Color.green().value, "permissions": []}
            ],
            "categories": [
                {
                    "name": "📍 Server Info",
                    "channels": [
                        {"name": "rules", "type": "text", "read_only_staff": False},
                        {"name": "server-status", "type": "text", "read_only_staff": False},
                        {"name": "announcements", "type": "text", "read_only_staff": False}
                    ]
                },
                {
                    "name": "🛠️ Gameplay",
                    "channels": [
                        {"name": "main-chat", "type": "text", "read_only_staff": False},
                        {"name": "survival-chat", "type": "text", "read_only_staff": False},
                        {"name": "creative-chat", "type": "text", "read_only_staff": False},
                        {"name": "voice-general", "type": "voice", "read_only_staff": False}
                    ]
                },
                {
                    "name": "🏗️ Building",
                    "channels": [
                        {"name": "builds", "type": "text", "read_only_staff": False},
                        {"name": "build-voice", "type": "voice", "read_only_staff": False},
                        {"name": "world-projects", "type": "text", "read_only_staff": False}
                    ]
                },
                {
                    "name": "🔐 Admin",
                    "channels": [
                        {"name": "admin-chat", "type": "text", "read_only_staff": True},
                        {"name": "logs", "type": "text", "read_only_staff": True}
                    ]
                }
            ]
        },
        "community.json": {
            "name": "Community Server",
            "description": "Inclusive community for all interests",
            "roles": [
                {"name": "Owner", "color": discord.Color.red().value, "permissions": ["administrator"]},
                {"name": "Moderator", "color": discord.Color.orange().value, 
                 "permissions": ["manage_channels", "manage_messages", "kick_members"]},
                {"name": "Member", "color": discord.Color.blue().value, "permissions": []}
            ],
            "categories": [
                {
                    "name": "📢 Announcements",
                    "channels": [
                        {"name": "announcements", "type": "text", "read_only_staff": False},
                        {"name": "updates", "type": "text", "read_only_staff": False}
                    ]
                },
                {
                    "name": "💬 General",
                    "channels": [
                        {"name": "general", "type": "text", "read_only_staff": False},
                        {"name": "introductions", "type": "text", "read_only_staff": False},
                        {"name": "casual", "type": "text", "read_only_staff": False},
                        {"name": "voice-chat", "type": "voice", "read_only_staff": False}
                    ]
                },
                {
                    "name": "🎨 Creative",
                    "channels": [
                        {"name": "art", "type": "text", "read_only_staff": False},
                        {"name": "music", "type": "text", "read_only_staff": False},
                        {"name": "writing", "type": "text", "read_only_staff": False}
                    ]
                },
                {
                    "name": "🤝 Support",
                    "channels": [
                        {"name": "help", "type": "text", "read_only_staff": False},
                        {"name": "feedback", "type": "text", "read_only_staff": False}
                    ]
                }
            ]
        },
        "creator.json": {
            "name": "Content Creator Server",
            "description": "Server for streamers and content creators",
            "roles": [
                {"name": "Owner", "color": discord.Color.red().value, "permissions": ["administrator"]},
                {"name": "Moderator", "color": discord.Color.orange().value, 
                 "permissions": ["manage_channels", "manage_messages", "kick_members"]},
                {"name": "Creator", "color": discord.Color.gold().value, "permissions": []},
                {"name": "Supporter", "color": discord.Color.blue().value, "permissions": []}
            ],
            "categories": [
                {
                    "name": "📺 Content",
                    "channels": [
                        {"name": "stream-announcements", "type": "text", "read_only_staff": False},
                        {"name": "stream-chat", "type": "text", "read_only_staff": False},
                        {"name": "upload-schedule", "type": "text", "read_only_staff": False}
                    ]
                },
                {
                    "name": "🎙️ Voice",
                    "channels": [
                        {"name": "general-voice", "type": "voice", "read_only_staff": False},
                        {"name": "stream-voice", "type": "voice", "read_only_staff": False},
                        {"name": "collaboration", "type": "voice", "read_only_staff": False}
                    ]
                },
                {
                    "name": "🛠️ Creator Tools",
                    "channels": [
                        {"name": "tips-tricks", "type": "text", "read_only_staff": False},
                        {"name": "resources", "type": "text", "read_only_staff": False},
                        {"name": "collaborations", "type": "text", "read_only_staff": False}
                    ]
                },
                {
                    "name": "🔐 Staff",
                    "channels": [
                        {"name": "staff-chat", "type": "text", "read_only_staff": True},
                        {"name": "moderation", "type": "text", "read_only_staff": True}
                    ]
                }
            ]
        }
    }
    
    for filename, template_data in templates.items():
        filepath = TEMPLATES_DIR / filename
        with open(filepath, "w") as f:
            json.dump(template_data, f, indent=2)
        logger.info(f"Created example template: {filename}")


def load_templates() -> Dict[str, Dict[str, Any]]:
    """Load all templates from JSON files."""
    templates = {}
    for template_file in TEMPLATES_DIR.glob("*.json"):
        try:
            with open(template_file, "r") as f:
                template_data = json.load(f)
                template_id = template_file.stem
                templates[template_id] = template_data
                logger.info(f"Loaded template: {template_id}")
        except Exception as e:
            logger.error(f"Error loading template {template_file}: {e}")
    return templates


def get_uptime() -> str:
    """Get bot uptime as a formatted string."""
    delta = datetime.now() - bot_start_time
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}h {minutes}m {seconds}s"


async def check_permissions(guild: discord.Guild, interaction: Interaction) -> bool:
    """Check if user has permission to run setup commands."""
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ You need Administrator permissions to use this command.",
            ephemeral=True
        )
        return False
    
    bot_member = guild.get_member(bot.user.id)
    if not bot_member:
        await interaction.response.send_message(
            "❌ Bot not found in guild.",
            ephemeral=True
        )
        return False
    
    if not bot_member.guild_permissions.administrator:
        await interaction.response.send_message(
            "❌ Bot needs Administrator permissions.",
            ephemeral=True
        )
        return False
    
    return True


# ============================================================================
# DISCORD VIEWS - UI COMPONENTS
# ============================================================================

class TemplateSelectView(discord.ui.View):
    """View for selecting a template."""
    
    def __init__(self, templates: Dict[str, Dict[str, Any]], interaction: Interaction):
        super().__init__(timeout=120)
        self.templates = templates
        self.interaction = interaction
        self.selected_template: Optional[str] = None
        
        # Create select menu
        options = [
            SelectOption(
                label=template_data["name"],
                value=template_id,
                description=template_data["description"][:100]
            )
            for template_id, template_data in templates.items()
        ]
        
        self.select_menu.options = options
    
    @discord.ui.select(placeholder="Select a template...", min_values=1, max_values=1)
    async def select_menu(self, interaction: Interaction, select: discord.ui.Select) -> None:
        """Handle template selection."""
        self.selected_template = select.values[0]
        template_data = self.templates[self.selected_template]
        
        # Create preview embed
        embed = discord.Embed(
            title=f"📋 {template_data['name']}",
            description=template_data["description"],
            color=discord.Color.blue()
        )
        embed.add_field(
            name="📊 Statistics",
            value=f"Categories: {len(template_data['categories'])}\n"
                  f"Channels: {sum(len(c['channels']) for c in template_data['categories'])}\n"
                  f"Roles: {len(template_data['roles'])}",
            inline=True
        )
        embed.add_field(name="⚙️ Setup", value="Click 'Create Template' to proceed", inline=True)
        
        await interaction.response.edit_message(embed=embed, view=TemplateConfirmView())
    
    async def on_timeout(self) -> None:
        """Called when view times out."""
        logger.warning("TemplateSelectView timed out")


class TemplateConfirmView(discord.ui.View):
    """View for confirming template creation."""
    
    def __init__(self):
        super().__init__(timeout=120)
        self.confirmed: Optional[bool] = None
    
    @discord.ui.button(label="Create Template", style=ButtonStyle.green, emoji="✅")
    async def confirm_button(self, interaction: Interaction, button: discord.ui.Button) -> None:
        """Confirm template creation."""
        self.confirmed = True
        await interaction.response.defer()
        self.stop()
    
    @discord.ui.button(label="Cancel", style=ButtonStyle.red, emoji="❌")
    async def cancel_button(self, interaction: Interaction, button: discord.ui.Button) -> None:
        """Cancel template creation."""
        self.confirmed = False
        await interaction.response.defer()
        self.stop()


class UndoConfirmView(discord.ui.View):
    """View for confirming undo operation."""
    
    def __init__(self):
        super().__init__(timeout=60)
        self.confirmed: Optional[bool] = None
    
    @discord.ui.button(label="Yes, Undo", style=ButtonStyle.red, emoji="⚠️")
    async def confirm_button(self, interaction: Interaction, button: discord.ui.Button) -> None:
        """Confirm undo."""
        self.confirmed = True
        await interaction.response.defer()
        self.stop()
    
    @discord.ui.button(label="Cancel", style=ButtonStyle.grey, emoji="❌")
    async def cancel_button(self, interaction: Interaction, button: discord.ui.Button) -> None:
        """Cancel undo."""
        self.confirmed = False
        await interaction.response.defer()
        self.stop()


class DeleteConfirmView(discord.ui.View):
    """View for confirming delete operation."""
    
    def __init__(self):
        super().__init__(timeout=60)
        self.confirmed: Optional[bool] = None
    
    @discord.ui.button(label="DELETE ALL", style=ButtonStyle.danger, emoji="🔥")
    async def confirm_button(self, interaction: Interaction, button: discord.ui.Button) -> None:
        """Confirm deletion."""
        self.confirmed = True
        await interaction.response.defer()
        self.stop()
    
    @discord.ui.button(label="Cancel", style=ButtonStyle.grey, emoji="❌")
    async def cancel_button(self, interaction: Interaction, button: discord.ui.Button) -> None:
        """Cancel deletion."""
        self.confirmed = False
        await interaction.response.defer()
        self.stop()


# ============================================================================
# SETUP SYSTEM
# ============================================================================

async def create_roles(
    guild: discord.Guild,
    roles_data: List[Dict[str, Any]]
) -> Dict[str, discord.Role]:
    """Create roles from template data."""
    created_roles = {}
    
    for role_data in roles_data:
        try:
            role = await guild.create_role(
                name=role_data["name"],
                color=discord.Color(role_data.get("color", 0)),
                hoist=True
            )
            created_roles[role_data["name"]] = role
            logger.info(f"Created role: {role_data['name']} in {guild.name}")
        except discord.Forbidden:
            logger.error(f"No permission to create role {role_data['name']}")
        except Exception as e:
            logger.error(f"Error creating role {role_data['name']}: {e}")
    
    return created_roles


async def create_categories_and_channels(
    guild: discord.Guild,
    categories_data: List[Dict[str, Any]],
    created_roles: Dict[str, discord.Role]
) -> tuple[List[discord.CategoryChannel], List[discord.abc.GuildChannel]]:
    """Create categories and channels from template data."""
    created_categories = []
    created_channels = []
    
    for category_data in categories_data:
        try:
            category = await guild.create_category(name=category_data["name"])
            created_categories.append(category)
            logger.info(f"Created category: {category_data['name']}")
            
            # Create channels in this category
            for channel_data in category_data.get("channels", []):
                try:
                    channel_type = channel_data.get("type", "text").lower()
                    
                    if channel_type == "voice":
                        channel = await guild.create_voice_channel(
                            name=channel_data["name"],
                            category=category
                        )
                    elif channel_type == "forum":
                        channel = await guild.create_forum(
                            name=channel_data["name"],
                            category=category
                        )
                    else:  # text
                        channel = await guild.create_text_channel(
                            name=channel_data["name"],
                            category=category
                        )
                    
                    created_channels.append(channel)
                    
                    # Set permissions
                    await set_channel_permissions(
                        channel,
                        guild,
                        created_roles,
                        channel_data.get("read_only_staff", False)
                    )
                    
                    logger.info(f"Created channel: {channel_data['name']}")
                
                except Exception as e:
                    logger.error(f"Error creating channel {channel_data['name']}: {e}")
        
        except discord.Forbidden:
            logger.error(f"No permission to create category {category_data['name']}")
        except Exception as e:
            logger.error(f"Error creating category {category_data['name']}: {e}")
    
    return created_categories, created_channels


async def set_channel_permissions(
    channel: discord.abc.GuildChannel,
    guild: discord.Guild,
    created_roles: Dict[str, discord.Role],
    staff_only: bool = False
) -> None:
    """Set channel permissions based on role hierarchy."""
    try:
        owner_role = created_roles.get("Owner")
        staff_role = created_roles.get("Staff")
        member_role = created_roles.get("Member")
        muted_role = created_roles.get("Muted")
        admin_role = created_roles.get("Admin")
        moderator_role = created_roles.get("Moderator")
        
        # Default: deny @everyone
        await channel.set_permissions(
            guild.default_role,
            view_channel=False
        )
        
        # Allow Owner role
        if owner_role:
            await channel.set_permissions(
                owner_role,
                view_channel=True,
                send_messages=True,
                speak=True,
                connect=True,
                manage_channels=True,
                manage_messages=True,
                manage_permissions=True
            )
        
        # Handle staff roles
        for staff_role in [staff_role, admin_role, moderator_role]:
            if staff_role:
                await channel.set_permissions(
                    staff_role,
                    view_channel=True,
                    send_messages=True,
                    speak=True,
                    connect=True,
                    manage_messages=True
                )
        
        # Handle member roles
        for member_role in [member_role]:
            if member_role and not staff_only:
                await channel.set_permissions(
                    member_role,
                    view_channel=True,
                    send_messages=True,
                    speak=True,
                    connect=True
                )
        
        # Muted role
        if muted_role:
            await channel.set_permissions(
                muted_role,
                send_messages=False,
                speak=False
            )
    
    except Exception as e:
        logger.error(f"Error setting permissions for {channel.name}: {e}")


# ============================================================================
# COMMANDS
# ============================================================================

@bot.event
async def on_ready() -> None:
    """Bot ready event."""
    logger.info(f"Logged in as {bot.user}")
    await bot.tree.sync()
    logger.info("Slash commands synced")


@bot.tree.command(
    name="setup",
    description="Browse and install server templates"
)
async def setup_command(interaction: Interaction) -> None:
    """Setup command - displays template selection menu."""
    guild = interaction.guild
    if not guild:
        await interaction.response.send_message(
            "❌ This command can only be used in a guild.",
            ephemeral=True
        )
        return
    
    # Check permissions
    if not await check_permissions(guild, interaction):
        return
    
    # Load templates
    templates = load_templates()
    if not templates:
        await interaction.response.send_message(
            "❌ No templates found. Please add template files to the templates/ directory.",
            ephemeral=True
        )
        return
    
    # Send initial message
    embed = discord.Embed(
        title="🎨 Server Setup",
        description="Select a template to view details and create your server structure.",
        color=discord.Color.blue()
    )
    embed.set_footer(text=f"Templates available: {len(templates)}")
    
    await interaction.response.send_message(
        embed=embed,
        view=TemplateSelectView(templates, interaction),
        ephemeral=False
    )


@bot.tree.command(
    name="undo",
    description="Undo the last template installation"
)
async def undo_command(interaction: Interaction) -> None:
    """Undo command - removes last created resources."""
    guild = interaction.guild
    if not guild:
        await interaction.response.send_message(
            "❌ This command can only be used in a guild.",
            ephemeral=True
        )
        return
    
    # Check permissions
    if not await check_permissions(guild, interaction):
        return
    
    # Check if there's a history entry
    if guild.id not in setup_history:
        await interaction.response.send_message(
            "❌ No setup history found. Nothing to undo.",
            ephemeral=True
        )
        return
    
    # Get history
    history = setup_history[guild.id]
    
    # Show confirmation
    embed = discord.Embed(
        title="⚠️ Confirm Undo",
        description="This will delete:\n"
                    f"• {len(history['roles'])} roles\n"
                    f"• {len(history['categories'])} categories\n"
                    f"• {len(history['channels'])} channels",
        color=discord.Color.orange()
    )
    
    await interaction.response.send_message(embed=embed, view=UndoConfirmView(), ephemeral=True)
    
    # Wait for confirmation
    view = UndoConfirmView()
    await view.wait()
    
    if view.confirmed:
        await interaction.followup.send("🔄 Undoing setup...", ephemeral=True)
        
        # Delete categories (cascades to channels)
        deleted_count = 0
        for category_id in history["categories"]:
            try:
                category = guild.get_channel(category_id)
                if category:
                    await category.delete()
                    deleted_count += 1
                    logger.info(f"Deleted category: {category.name}")
            except Exception as e:
                logger.error(f"Error deleting category {category_id}: {e}")
        
        # Delete roles
        for role_id in history["roles"]:
            try:
                role = guild.get_role(role_id)
                if role and role != guild.default_role:
                    await role.delete()
                    deleted_count += 1
                    logger.info(f"Deleted role: {role.name}")
            except Exception as e:
                logger.error(f"Error deleting role {role_id}: {e}")
        
        # Remove from history
        del setup_history[guild.id]
        
        # Send completion message
        embed = discord.Embed(
            title="✅ Undo Complete",
            description=f"Removed {deleted_count} objects from your server.",
            color=discord.Color.green()
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
        logger.info(f"Undo completed for guild {guild.id}")


@bot.tree.command(
    name="delete",
    description="Dangerous: Delete all channels and roles"
)
async def delete_command(interaction: Interaction) -> None:
    """Delete command - dangerous cleanup command."""
    guild = interaction.guild
    if not guild:
        await interaction.response.send_message(
            "❌ This command can only be used in a guild.",
            ephemeral=True
        )
        return
    
    # Check permissions
    if not await check_permissions(guild, interaction):
        return
    
    # Show warning
    embed = discord.Embed(
        title="🔥 DANGEROUS OPERATION",
        description="This will **DELETE** all channels and roles except:\n"
                    "• @everyone role\n"
                    "• Discord managed roles\n"
                    "• The current channel",
        color=discord.Color.red()
    )
    embed.add_field(
        name="⚠️ WARNING",
        value="**This action CANNOT be undone!**\nClick 'DELETE ALL' to proceed.",
        inline=False
    )
    
    await interaction.response.send_message(embed=embed, view=DeleteConfirmView(), ephemeral=True)
    
    # Wait for confirmation
    view = DeleteConfirmView()
    await view.wait()
    
    if view.confirmed:
        await interaction.followup.send("🔄 Deleting server structure...", ephemeral=True)
        
        bot_member = guild.get_member(bot.user.id)
        if not bot_member:
            await interaction.followup.send("❌ Bot not found in guild.", ephemeral=True)
            return
        
        deleted_count = 0
        failed_count = 0
        
        # Delete categories and channels
        for category in list(guild.categories):
            if category.id == interaction.channel.category_id:
                continue
            
            try:
                # Delete channels in category
                for channel in category.channels:
                    if channel.id != interaction.channel.id:
                        await channel.delete()
                        deleted_count += 1
                
                # Delete the category
                await category.delete()
                deleted_count += 1
                logger.info(f"Deleted category: {category.name}")
            except Exception as e:
                logger.error(f"Error deleting category {category.name}: {e}")
                failed_count += 1
        
        # Delete text channels not in categories
        for channel in list(guild.text_channels):
            if channel.id == interaction.channel.id:
                continue
            try:
                await channel.delete()
                deleted_count += 1
            except Exception as e:
                logger.error(f"Error deleting text channel {channel.name}: {e}")
                failed_count += 1
        
        # Delete voice channels
        for channel in list(guild.voice_channels):
            try:
                await channel.delete()
                deleted_count += 1
            except Exception as e:
                logger.error(f"Error deleting voice channel {channel.name}: {e}")
                failed_count += 1
        
        # Delete stage channels
        for channel in list(guild.stage_channels):
            try:
                await channel.delete()
                deleted_count += 1
            except Exception as e:
                logger.error(f"Error deleting stage channel {channel.name}: {e}")
                failed_count += 1
        
        # Delete roles
        for role in list(guild.roles):
            if role == guild.default_role or role.managed or role > bot_member.top_role:
                continue
            
            try:
                await role.delete()
                deleted_count += 1
                logger.info(f"Deleted role: {role.name}")
            except Exception as e:
                logger.error(f"Error deleting role {role.name}: {e}")
                failed_count += 1
        
        # Send completion message
        embed = discord.Embed(
            title="✅ Deletion Complete",
            color=discord.Color.green()
        )
        embed.add_field(name="Deleted", value=str(deleted_count))
        if failed_count > 0:
            embed.add_field(name="Failed", value=str(failed_count))
        
        await interaction.followup.send(embed=embed, ephemeral=True)
        logger.info(f"Delete operation completed for guild {guild.id}")


@bot.tree.command(
    name="info",
    description="View bot information and commands"
)
async def info_command(interaction: Interaction) -> None:
    """Info command - displays bot information."""
    templates = load_templates()
    
    embed = discord.Embed(
        title=f"ℹ️ {BOT_NAME}",
        description="A powerful Discord server setup bot with templates and automation.",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="📊 Bot Information",
        value=f"**Version:** {BOT_VERSION}\n"
              f"**Uptime:** {get_uptime()}\n"
              f"**Templates:** {len(templates)}\n"
              f"**Ping:** {round(bot.latency * 1000)}ms",
        inline=False
    )
    
    embed.add_field(
        name="📋 Commands",
        value="**/setup** - Browse and install server templates\n"
              "**/undo** - Undo the last template installation\n"
              "**/delete** - Remove all channels and roles\n"
              "**/info** - View this information",
        inline=False
    )
    
    embed.add_field(
        name="🎨 Available Templates",
        value=", ".join(template_data["name"] for template_data in templates.values()) or "None loaded",
        inline=False
    )
    
    embed.set_footer(text="Created with discord.py 2.x")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main() -> None:
    """Main entry point."""
    ensure_directories()
    load_example_templates()
    
    logger.info(f"Starting {BOT_NAME} bot...")
    try:
        bot.run(TOKEN)
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
