"""
All In One Setup - Discord Bot
A production-ready Discord bot for creating complete server structures from pre-made templates.

Author: Discord Bot Developer
Version: 1.0.0
Python: 3.12+
discord.py: 2.x
"""

import os
import json
import logging
import asyncio
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any, Set, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
import traceback

import discord
from discord import app_commands, Interaction, User, Member, Role, TextChannel, VoiceChannel, CategoryChannel, ForumChannel
from discord.ext import commands, tasks
from dotenv import load_dotenv

# ═══════════════════════════════════════════════════════════════════════════════════
# CONFIGURATION AND LOGGING
# ═══════════════════════════════════════════════════════════════════════════════════

# Load environment variables
load_dotenv()

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Bot Configuration
BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN', '')
BOT_NAME = "All In One Setup"
BOT_VERSION = "1.0.0"
TEMPLATES_DIR = Path('templates')
CACHE_FILE = Path('bot_cache.json')

# Ensure templates directory exists
TEMPLATES_DIR.mkdir(exist_ok=True)

# ═══════════════════════════════════════════════════════════════════════════════════
# DATA MODELS
# ═══════════════════════════════════════════════════════════════════════════════════

@dataclass
class TemplateSetupTracker:
    """Track all changes made during template installation for undo operations."""
    guild_id: int
    timestamp: datetime
    categories_created: List[int] = field(default_factory=list)
    channels_created: List[int] = field(default_factory=list)
    roles_created: List[int] = field(default_factory=list)
    permission_overwrites: List[Dict[str, Any]] = field(default_factory=list)
    template_name: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'guild_id': self.guild_id,
            'timestamp': self.timestamp.isoformat(),
            'categories_created': self.categories_created,
            'channels_created': self.channels_created,
            'roles_created': self.roles_created,
            'permission_overwrites': self.permission_overwrites,
            'template_name': self.template_name
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TemplateSetupTracker':
        """Create from dictionary loaded from JSON."""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)

# ═══════════════════════════════════════════════════════════════════════════════════
# TEMPLATE SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════════

class TemplateManager:
    """Manages template loading, parsing, and management."""
    
    def __init__(self, templates_dir: Path):
        self.templates_dir = templates_dir
        self.templates: Dict[str, Dict[str, Any]] = {}
        self.template_order: List[str] = []
        self._load_templates()
    
    def _load_templates(self) -> None:
        """Load all templates from JSON files."""
        logger.info("Loading templates...")
        
        if not self.templates_dir.exists():
            logger.warning("Templates directory does not exist. Creating...")
            self.templates_dir.mkdir(exist_ok=True)
            self._create_example_templates()
            return
        
        template_files = list(self.templates_dir.glob('*.json'))
        
        if not template_files:
            logger.warning("No template files found. Creating examples...")
            self._create_example_templates()
            template_files = list(self.templates_dir.glob('*.json'))
        
        for template_file in sorted(template_files):
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    template_data = json.load(f)
                    template_name = template_data.get('name', template_file.stem)
                    self.templates[template_name] = template_data
                    self.template_order.append(template_name)
                    logger.info(f"Loaded template: {template_name}")
            except Exception as e:
                logger.error(f"Failed to load template {template_file}: {e}")
    
    def _create_example_templates(self) -> None:
        """Create example template JSON files."""
        examples = {
            'gaming.json': {
                'name': 'Gaming Server',
                'description': 'A complete gaming server setup with channels for different games and voice channels for parties.',
                'categories': [
                    {
                        'name': '🎮 Games',
                        'channels': [
                            {'name': 'general', 'type': 'text'},
                            {'name': 'announcements', 'type': 'text'},
                            {'name': 'squad-lfg', 'type': 'text'},
                            {'name': 'gaming-party', 'type': 'voice'},
                            {'name': 'ranked-team', 'type': 'voice'}
                        ]
                    },
                    {
                        'name': '💬 Communication',
                        'channels': [
                            {'name': 'off-topic', 'type': 'text'},
                            {'name': 'memes', 'type': 'text'},
                            {'name': 'voice-channel', 'type': 'voice'}
                        ]
                    },
                    {
                        'name': '🔧 Management',
                        'channels': [
                            {'name': 'staff-chat', 'type': 'text', 'private': True},
                            {'name': 'mod-logs', 'type': 'text', 'private': True}
                        ]
                    }
                ],
                'roles': [
                    {'name': 'Owner', 'permissions': ['administrator']},
                    {'name': 'Staff', 'permissions': ['manage_channels', 'manage_messages', 'kick_members', 'moderate_members']},
                    {'name': 'Member', 'permissions': []},
                    {'name': 'Muted', 'permissions': ['view_channel']}
                ]
            },
            'minecraft.json': {
                'name': 'Minecraft Server',
                'description': 'Dedicated Minecraft server with channels for gameplay discussion, technical help, and server management.',
                'categories': [
                    {
                        'name': '⛏️ Gameplay',
                        'channels': [
                            {'name': 'announcements', 'type': 'text'},
                            {'name': 'general-chat', 'type': 'text'},
                            {'name': 'builds-showcase', 'type': 'text'},
                            {'name': 'survival-world', 'type': 'voice'},
                            {'name': 'creative-world', 'type': 'voice'}
                        ]
                    },
                    {
                        'name': '🛠️ Technical',
                        'channels': [
                            {'name': 'server-help', 'type': 'text'},
                            {'name': 'modding-discussion', 'type': 'text'},
                            {'name': 'technical-support', 'type': 'voice'}
                        ]
                    },
                    {
                        'name': '👨‍💼 Administration',
                        'channels': [
                            {'name': 'admin-chat', 'type': 'text', 'private': True},
                            {'name': 'server-logs', 'type': 'text', 'private': True}
                        ]
                    }
                ],
                'roles': [
                    {'name': 'Owner', 'permissions': ['administrator']},
                    {'name': 'Moderator', 'permissions': ['manage_channels', 'manage_messages', 'kick_members']},
                    {'name': 'Builder', 'permissions': []},
                    {'name': 'Member', 'permissions': []}
                ]
            },
            'community.json': {
                'name': 'Community Server',
                'description': 'A welcoming community server for general discussion, events, and community engagement.',
                'categories': [
                    {
                        'name': '📢 General',
                        'channels': [
                            {'name': 'announcements', 'type': 'text'},
                            {'name': 'welcome', 'type': 'text'},
                            {'name': 'general-chat', 'type': 'text'},
                            {'name': 'introductions', 'type': 'text'}
                        ]
                    },
                    {
                        'name': '🎉 Events',
                        'channels': [
                            {'name': 'events', 'type': 'text'},
                            {'name': 'event-voice', 'type': 'voice'},
                            {'name': 'contests', 'type': 'text'}
                        ]
                    },
                    {
                        'name': '🎨 Creative',
                        'channels': [
                            {'name': 'art-showcase', 'type': 'text'},
                            {'name': 'music-discussion', 'type': 'text'},
                            {'name': 'creative-lounge', 'type': 'voice'}
                        ]
                    },
                    {
                        'name': '⚙️ Management',
                        'channels': [
                            {'name': 'mod-chat', 'type': 'text', 'private': True},
                            {'name': 'reports', 'type': 'text', 'private': True}
                        ]
                    }
                ],
                'roles': [
                    {'name': 'Owner', 'permissions': ['administrator']},
                    {'name': 'Moderator', 'permissions': ['manage_messages', 'kick_members', 'moderate_members']},
                    {'name': 'Member', 'permissions': []},
                    {'name': 'Muted', 'permissions': ['view_channel']}
                ]
            },
            'creator.json': {
                'name': 'Content Creator Server',
                'description': 'Server designed for content creators with channels for collaboration, feedback, and community engagement.',
                'categories': [
                    {
                        'name': '📺 Content',
                        'channels': [
                            {'name': 'announcements', 'type': 'text'},
                            {'name': 'stream-schedule', 'type': 'text'},
                            {'name': 'video-uploads', 'type': 'text'},
                            {'name': 'streaming', 'type': 'voice'}
                        ]
                    },
                    {
                        'name': '🤝 Collaboration',
                        'channels': [
                            {'name': 'collab-ideas', 'type': 'text'},
                            {'name': 'feedback', 'type': 'text'},
                            {'name': 'collab-voice', 'type': 'voice'}
                        ]
                    },
                    {
                        'name': '👥 Community',
                        'channels': [
                            {'name': 'general-chat', 'type': 'text'},
                            {'name': 'off-topic', 'type': 'text'},
                            {'name': 'fan-hangout', 'type': 'voice'}
                        ]
                    },
                    {
                        'name': '🔐 Private',
                        'channels': [
                            {'name': 'creator-chat', 'type': 'text', 'private': True},
                            {'name': 'analytics', 'type': 'text', 'private': True}
                        ]
                    }
                ],
                'roles': [
                    {'name': 'Owner', 'permissions': ['administrator']},
                    {'name': 'Moderator', 'permissions': ['manage_messages', 'kick_members']},
                    {'name': 'Collaborator', 'permissions': []},
                    {'name': 'Member', 'permissions': []}
                ]
            }
        }
        
        for filename, template_data in examples.items():
            template_path = self.templates_dir / filename
            if not template_path.exists():
                with open(template_path, 'w', encoding='utf-8') as f:
                    json.dump(template_data, f, indent=2)
                logger.info(f"Created example template: {filename}")
    
    def get_templates(self) -> Dict[str, Dict[str, Any]]:
        """Get all loaded templates."""
        return self.templates
    
    def get_template(self, name: str) -> Optional[Dict[str, Any]]:
        """Get a specific template by name."""
        return self.templates.get(name)
    
    def reload_templates(self) -> None:
        """Reload all templates from disk."""
        self.templates.clear()
        self.template_order.clear()
        self._load_templates()

# ═══════════════════════════════════════════════════════════════════════════════════
# CACHE SYSTEM FOR UNDO
# ═══════════════════════════════════════════════════════════════════════════════════

class UndoCache:
    """Manages caching of setup operations for undo functionality."""
    
    def __init__(self, cache_file: Path):
        self.cache_file = cache_file
        self.cache: Dict[int, TemplateSetupTracker] = {}
        self._load_cache()
    
    def _load_cache(self) -> None:
        """Load cache from file."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for guild_id_str, tracker_data in data.items():
                        guild_id = int(guild_id_str)
                        self.cache[guild_id] = TemplateSetupTracker.from_dict(tracker_data)
                logger.info(f"Loaded undo cache with {len(self.cache)} entries")
            except Exception as e:
                logger.error(f"Failed to load cache: {e}")
    
    def _save_cache(self) -> None:
        """Save cache to file."""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                data = {str(guild_id): tracker.to_dict() for guild_id, tracker in self.cache.items()}
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")
    
    def save_setup(self, tracker: TemplateSetupTracker) -> None:
        """Save a setup operation."""
        self.cache[tracker.guild_id] = tracker
        self._save_cache()
        logger.info(f"Cached setup for guild {tracker.guild_id}: {tracker.template_name}")
    
    def get_setup(self, guild_id: int) -> Optional[TemplateSetupTracker]:
        """Get the last setup for a guild."""
        return self.cache.get(guild_id)
    
    def clear_setup(self, guild_id: int) -> None:
        """Clear the cached setup for a guild."""
        if guild_id in self.cache:
            del self.cache[guild_id]
            self._save_cache()
            logger.info(f"Cleared cached setup for guild {guild_id}")

# ═══════════════════════════════════════════════════════════════════════════════════
# DISCORD UI VIEWS
# ═══════════════════════════════════════════════════════════════════════════════════

class TemplateSelect(discord.ui.Select):
    """Select menu for choosing templates."""
    
    def __init__(self, templates: Dict[str, Dict[str, Any]]):
        self.templates = templates
        
        options = [
            discord.SelectOption(
                label=name,
                value=name,
                description=template_data.get('description', 'No description')[:100],
                emoji='📋'
            )
            for name, template_data in templates.items()
        ]
        
        super().__init__(
            placeholder='Select a template...',
            min_values=1,
            max_values=1,
            options=options
        )
    
    async def callback(self, interaction: Interaction) -> None:
        """Handle template selection."""
        selected = self.values[0]
        template = self.templates.get(selected)
        
        if not template:
            await interaction.response.send_message(
                "❌ Template not found!",
                ephemeral=True
            )
            return
        
        # Create template preview embed
        embed = discord.Embed(
            title=f"📋 {template.get('name', 'Unknown Template')}",
            description=template.get('description', 'No description provided'),
            color=discord.Color.blurple()
        )
        
        categories = template.get('categories', [])
        channels = sum(len(cat.get('channels', [])) for cat in categories)
        roles = len(template.get('roles', []))
        
        embed.add_field(
            name="📊 Template Stats",
            value=f"Categories: {len(categories)}\nChannels: {channels}\nRoles: {roles}",
            inline=False
        )
        
        # Show category preview
        if categories:
            category_preview = "\n".join(f"• {cat.get('name', 'Unknown')}" for cat in categories[:5])
            if len(categories) > 5:
                category_preview += f"\n... and {len(categories) - 5} more"
            embed.add_field(name="📂 Categories Preview", value=category_preview, inline=False)
        
        # Create confirmation view
        view = TemplateConfirmView(template)
        
        await interaction.response.edit_message(embed=embed, view=view)

class TemplateSelectView(discord.ui.View):
    """View containing the template select menu."""
    
    def __init__(self, templates: Dict[str, Dict[str, Any]], timeout: int = 300):
        super().__init__(timeout=timeout)
        self.add_item(TemplateSelect(templates))

class TemplateConfirmView(discord.ui.View):
    """View for confirming template creation."""
    
    def __init__(self, template: Dict[str, Any], timeout: int = 300):
        super().__init__(timeout=timeout)
        self.template = template
        self.confirmed = False
    
    @discord.ui.button(label='Create Template', style=discord.ButtonStyle.success, emoji='✅')
    async def create_template(self, interaction: Interaction, button: discord.ui.Button) -> None:
        """Confirm and create the template."""
        self.confirmed = True
        await interaction.response.defer()
    
    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.danger, emoji='❌')
    async def cancel(self, interaction: Interaction, button: discord.ui.Button) -> None:
        """Cancel template creation."""
        await interaction.response.defer()
        for item in self.children:
            item.disabled = True
        await interaction.edit_original_response(view=self)

class UndoConfirmView(discord.ui.View):
    """View for confirming undo operation."""
    
    def __init__(self, timeout: int = 60):
        super().__init__(timeout=timeout)
        self.confirmed = False
    
    @discord.ui.button(label='Confirm Undo', style=discord.ButtonStyle.danger, emoji='⚠️')
    async def confirm(self, interaction: Interaction, button: discord.ui.Button) -> None:
        """Confirm the undo operation."""
        self.confirmed = True
        await interaction.response.defer()
    
    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.secondary, emoji='❌')
    async def cancel(self, interaction: Interaction, button: discord.ui.Button) -> None:
        """Cancel the undo operation."""
        await interaction.response.defer()
        for item in self.children:
            item.disabled = True
        await interaction.edit_original_response(view=self)

class DeleteConfirmView(discord.ui.View):
    """View for confirming delete operation with warning."""
    
    def __init__(self, timeout: int = 60):
        super().__init__(timeout=timeout)
        self.confirmed = False
    
    @discord.ui.button(label='I understand, delete everything', style=discord.ButtonStyle.danger, emoji='🗑️')
    async def confirm(self, interaction: Interaction, button: discord.ui.Button) -> None:
        """Confirm the delete operation."""
        self.confirmed = True
        await interaction.response.defer()
    
    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.secondary, emoji='❌')
    async def cancel(self, interaction: Interaction, button: discord.ui.Button) -> None:
        """Cancel the delete operation."""
        await interaction.response.defer()
        for item in self.children:
            item.disabled = True
        await interaction.edit_original_response(view=self)

# ═══════════════════════════════════════════════════════════════════════════════════
# PERMISSION UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════════

def get_permissions_from_names(permission_names: List[str]) -> discord.Permissions:
    """Convert permission names to discord.Permissions object."""
    permissions = discord.Permissions()
    
    permission_map = {
        'administrator': 'administrator',
        'manage_channels': 'manage_channels',
        'manage_messages': 'manage_messages',
        'manage_roles': 'manage_roles',
        'kick_members': 'kick_members',
        'ban_members': 'ban_members',
        'moderate_members': 'moderate_members',
        'send_messages': 'send_messages',
        'read_messages': 'read_message_history',
        'view_channel': 'view_channel',
        'connect': 'connect',
        'speak': 'speak',
        'move_members': 'move_members',
        'mute_members': 'mute_members',
        'deafen_members': 'deafen_members',
        'manage_webhooks': 'manage_webhooks',
    }
    
    for name in permission_names:
        perm_name = permission_map.get(name.lower(), name.lower())
        if hasattr(permissions, perm_name):
            setattr(permissions, perm_name, True)
    
    return permissions

# ═══════════════════════════════════════════════════════════════════════════════════
# TEMPLATE CREATION ENGINE
# ═══════════════════════════════════════════════════════════════════════════════════

class TemplateCreator:
    """Handles the actual creation of template structures in Discord."""
    
    def __init__(self, bot: 'AllInOneSetupBot'):
        self.bot = bot
    
    async def create_template(
        self,
        guild: discord.Guild,
        template: Dict[str, Any],
        interaction: Interaction
    ) -> Tuple[bool, str, Optional[TemplateSetupTracker]]:
        """
        Create a complete template structure in the guild.
        
        Returns:
            (success: bool, message: str, tracker: Optional[TemplateSetupTracker])
        """
        tracker = TemplateSetupTracker(
            guild_id=guild.id,
            timestamp=datetime.now(),
            template_name=template.get('name', 'Unknown')
        )
        
        try:
            # Check permissions
            if not guild.me.guild_permissions.manage_channels:
                return False, "❌ Bot lacks `Manage Channels` permission.", None
            if not guild.me.guild_permissions.manage_roles:
                return False, "❌ Bot lacks `Manage Roles` permission.", None
            
            # Create roles first
            logger.info(f"Creating roles for guild {guild.id}")
            roles_config = template.get('roles', [])
            created_roles: Dict[str, Role] = {}
            
            for role_config in roles_config:
                role_name = role_config.get('name', 'Role')
                permissions = role_config.get('permissions', [])
                
                try:
                    perm_obj = get_permissions_from_names(permissions)
                    role = await guild.create_role(
                        name=role_name,
                        permissions=perm_obj,
                        reason="All In One Setup - Template creation"
                    )
                    created_roles[role_name] = role
                    tracker.roles_created.append(role.id)
                    logger.info(f"Created role: {role_name} in guild {guild.id}")
                except Exception as e:
                    logger.error(f"Failed to create role {role_name}: {e}")
                    raise
                
                await asyncio.sleep(0.5)  # Rate limit protection
            
            # Create categories and channels
            logger.info(f"Creating categories and channels for guild {guild.id}")
            categories_config = template.get('categories', [])
            
            for category_config in categories_config:
                category_name = category_config.get('name', 'Category')
                
                try:
                    category = await guild.create_category(
                        name=category_name,
                        reason="All In One Setup - Template creation"
                    )
                    tracker.categories_created.append(category.id)
                    logger.info(f"Created category: {category_name} in guild {guild.id}")
                except Exception as e:
                    logger.error(f"Failed to create category {category_name}: {e}")
                    raise
                
                await asyncio.sleep(0.3)  # Rate limit protection
                
                # Create channels in this category
                channels_config = category_config.get('channels', [])
                
                for channel_config in channels_config:
                    channel_name = channel_config.get('name', 'channel')
                    channel_type = channel_config.get('type', 'text')
                    is_private = channel_config.get('private', False)
                    
                    try:
                        if channel_type == 'voice':
                            channel = await guild.create_voice_channel(
                                name=channel_name,
                                category=category,
                                reason="All In One Setup - Template creation"
                            )
                        else:  # text channel
                            channel = await guild.create_text_channel(
                                name=channel_name,
                                category=category,
                                reason="All In One Setup - Template creation"
                            )
                        
                        tracker.channels_created.append(channel.id)
                        logger.info(f"Created channel: {channel_name} in guild {guild.id}")
                        
                        # Set permissions if private
                        if is_private and channel_type == 'text':
                            try:
                                staff_role = created_roles.get('Staff') or created_roles.get('Owner')
                                everyone_role = guild.default_role
                                
                                if staff_role:
                                    await channel.set_permissions(
                                        staff_role,
                                        view_channel=True,
                                        send_messages=True,
                                        reason="All In One Setup - Setting staff permissions"
                                    )
                                
                                await channel.set_permissions(
                                    everyone_role,
                                    view_channel=False,
                                    reason="All In One Setup - Hiding from public"
                                )
                                
                                tracker.permission_overwrites.append({
                                    'channel_id': channel.id,
                                    'channel_name': channel_name
                                })
                            except Exception as e:
                                logger.error(f"Failed to set permissions for {channel_name}: {e}")
                    
                    except Exception as e:
                        logger.error(f"Failed to create channel {channel_name}: {e}")
                        raise
                    
                    await asyncio.sleep(0.3)  # Rate limit protection
            
            # Send success message
            embed = discord.Embed(
                title="✅ Template Created Successfully!",
                description=f"Template '{template.get('name')}' has been set up.",
                color=discord.Color.green()
            )
            embed.add_field(
                name="📊 Summary",
                value=f"Roles: {len(tracker.roles_created)}\nCategories: {len(tracker.categories_created)}\nChannels: {len(tracker.channels_created)}",
                inline=False
            )
            embed.add_field(
                name="💾 Undo Information",
                value="Use `/undo` to remove this template if needed.",
                inline=False
            )
            embed.set_footer(text="All In One Setup")
            
            await interaction.followup.send(embed=embed)
            
            # Save to undo cache
            self.bot.undo_cache.save_setup(tracker)
            
            return True, "Template created successfully.", tracker
        
        except discord.Forbidden:
            return False, "❌ Permission denied. The bot may lack required permissions.", None
        except discord.HTTPException as e:
            return False, f"❌ Discord API error: {str(e)[:100]}", None
        except Exception as e:
            logger.error(f"Unexpected error during template creation: {e}\n{traceback.format_exc()}")
            return False, f"❌ Unexpected error: {str(e)[:100]}", None
    
    async def undo_template(
        self,
        guild: discord.Guild,
        tracker: TemplateSetupTracker,
        interaction: Interaction
    ) -> Tuple[bool, str]:
        """
        Remove all resources created by template installation.
        
        Returns:
            (success: bool, message: str)
        """
        try:
            deleted_count = {'channels': 0, 'categories': 0, 'roles': 0}
            errors: List[str] = []
            
            # Delete channels
            for channel_id in tracker.channels_created:
                try:
                    channel = guild.get_channel(channel_id)
                    if channel:
                        await channel.delete(reason="All In One Setup - Undo operation")
                        deleted_count['channels'] += 1
                        logger.info(f"Deleted channel {channel_id}")
                except Exception as e:
                    logger.warning(f"Failed to delete channel {channel_id}: {e}")
                    errors.append(f"Channel {channel_id}")
                
                await asyncio.sleep(0.2)
            
            # Delete categories
            for category_id in tracker.categories_created:
                try:
                    category = guild.get_channel(category_id)
                    if category:
                        await category.delete(reason="All In One Setup - Undo operation")
                        deleted_count['categories'] += 1
                        logger.info(f"Deleted category {category_id}")
                except Exception as e:
                    logger.warning(f"Failed to delete category {category_id}: {e}")
                    errors.append(f"Category {category_id}")
                
                await asyncio.sleep(0.2)
            
            # Delete roles
            for role_id in tracker.roles_created:
                try:
                    role = guild.get_role(role_id)
                    if role:
                        # Don't delete if role is above bot's role
                        if role.position >= guild.me.top_role.position:
                            logger.warning(f"Cannot delete role {role_id} - it's above the bot's role")
                            errors.append(f"Role '{role.name}' (too high in hierarchy)")
                            continue
                        
                        await role.delete(reason="All In One Setup - Undo operation")
                        deleted_count['roles'] += 1
                        logger.info(f"Deleted role {role_id}")
                except Exception as e:
                    logger.warning(f"Failed to delete role {role_id}: {e}")
                    errors.append(f"Role {role_id}")
                
                await asyncio.sleep(0.2)
            
            # Create result embed
            embed = discord.Embed(
                title="✅ Undo Completed",
                description=f"Template '{tracker.template_name}' has been removed.",
                color=discord.Color.green()
            )
            embed.add_field(
                name="🗑️ Deleted",
                value=f"Channels: {deleted_count['channels']}\nCategories: {deleted_count['categories']}\nRoles: {deleted_count['roles']}",
                inline=False
            )
            
            if errors:
                embed.add_field(
                    name="⚠️ Failed to Delete",
                    value="\n".join(errors[:5]),
                    inline=False
                )
            
            embed.set_footer(text="All In One Setup")
            await interaction.followup.send(embed=embed)
            
            # Clear from cache
            self.bot.undo_cache.clear_setup(guild.id)
            
            return True, "Template successfully undone."
        
        except Exception as e:
            logger.error(f"Error during undo: {e}\n{traceback.format_exc()}")
            return False, f"❌ Error during undo: {str(e)[:100]}"

class TemplateDeleter:
    """Handles mass deletion of server channels and roles."""
    
    def __init__(self, bot: 'AllInOneSetupBot'):
        self.bot = bot
    
    async def delete_all_structure(
        self,
        guild: discord.Guild,
        interaction: Interaction
    ) -> Tuple[bool, str]:
        """
        Delete all categories, channels, and template-created roles.
        
        Returns:
            (success: bool, message: str)
        """
        try:
            # Permission checks
            if not interaction.user.guild_permissions.administrator:
                return False, "❌ You must be an administrator to use this command."
            
            if not guild.me.guild_permissions.manage_channels:
                return False, "❌ Bot lacks `Manage Channels` permission."
            
            if not guild.me.guild_permissions.manage_roles:
                return False, "❌ Bot lacks `Manage Roles` permission."
            
            deleted_count = {'channels': 0, 'categories': 0, 'roles': 0}
            failed_count = {'channels': 0, 'categories': 0, 'roles': 0}
            
            # Update status
            await interaction.followup.send(
                embed=discord.Embed(
                    title="🔄 Deletion in Progress",
                    description="Removing server structure...",
                    color=discord.Color.orange()
                )
            )
            
            # Delete all text and voice channels (but not the command channel)
            for channel in list(guild.channels):
                if isinstance(channel, (TextChannel, VoiceChannel, ForumChannel)):
                    if channel.id == interaction.channel_id:
                        continue  # Don't delete the channel where command was run
                    
                    try:
                        await channel.delete(reason="All In One Setup - Delete operation")
                        deleted_count['channels'] += 1
                        logger.info(f"Deleted channel {channel.name}")
                    except Exception as e:
                        logger.warning(f"Failed to delete channel {channel.name}: {e}")
                        failed_count['channels'] += 1
                    
                    await asyncio.sleep(0.2)
            
            # Delete all categories
            for category in list(guild.categories):
                try:
                    await category.delete(reason="All In One Setup - Delete operation")
                    deleted_count['categories'] += 1
                    logger.info(f"Deleted category {category.name}")
                except Exception as e:
                    logger.warning(f"Failed to delete category {category.name}: {e}")
                    failed_count['categories'] += 1
                
                await asyncio.sleep(0.2)
            
            # Delete custom roles (but preserve Discord-managed roles and roles above bot)
            for role in list(guild.roles):
                if role.name == "@everyone":
                    continue
                if role.managed:  # Discord managed roles (bot integrations, etc.)
                    continue
                if role.position >= guild.me.top_role.position:  # Above bot's role
                    logger.info(f"Skipping role {role.name} - above bot hierarchy")
                    continue
                
                try:
                    await role.delete(reason="All In One Setup - Delete operation")
                    deleted_count['roles'] += 1
                    logger.info(f"Deleted role {role.name}")
                except Exception as e:
                    logger.warning(f"Failed to delete role {role.name}: {e}")
                    failed_count['roles'] += 1
                
                await asyncio.sleep(0.2)
            
            # Create final summary
            embed = discord.Embed(
                title="✅ Deletion Complete",
                description="Server structure has been cleaned up.",
                color=discord.Color.green()
            )
            embed.add_field(
                name="🗑️ Deleted",
                value=f"Channels: {deleted_count['channels']}\nCategories: {deleted_count['categories']}\nRoles: {deleted_count['roles']}",
                inline=False
            )
            
            if any(failed_count.values()):
                embed.add_field(
                    name="⚠️ Failed to Delete",
                    value=f"Channels: {failed_count['channels']}\nCategories: {failed_count['categories']}\nRoles: {failed_count['roles']}",
                    inline=False
                )
            
            embed.set_footer(text="All In One Setup")
            await interaction.followup.send(embed=embed)
            
            return True, "Deletion completed."
        
        except Exception as e:
            logger.error(f"Error during deletion: {e}\n{traceback.format_exc()}")
            return False, f"❌ Error during deletion: {str(e)[:100]}"

# ═══════════════════════════════════════════════════════════════════════════════════
# MAIN BOT CLASS
# ═══════════════════════════════════════════════════════════════════════════════════

class AllInOneSetupBot(commands.Cog):
    """Main bot cog containing all commands and functionality."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.template_manager = TemplateManager(TEMPLATES_DIR)
        self.undo_cache = UndoCache(CACHE_FILE)
        self.template_creator = TemplateCreator(bot)
        self.template_deleter = TemplateDeleter(bot)
        self.startup_time = datetime.now()
        logger.info("AllInOneSetupBot cog initialized")
    
    # ─────────────────────────────────────────────────────────────────────────────
    # SETUP COMMAND
    # ─────────────────────────────────────────────────────────────────────────────
    
    @app_commands.command(name='setup', description='Browse and install server templates')
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setup(self, interaction: Interaction) -> None:
        """Display template selection menu."""
        try:
            await interaction.response.defer()
            
            templates = self.template_manager.get_templates()
            
            if not templates:
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="❌ No Templates Available",
                        description="No templates were found. Please check the templates folder.",
                        color=discord.Color.red()
                    )
                )
                return
            
            # Create selection menu
            embed = discord.Embed(
                title="📋 Server Template Selector",
                description="Choose a template to install. This will create categories, channels, and roles.",
                color=discord.Color.blurple()
            )
            embed.add_field(
                name="⚠️ Warning",
                value="This may create many channels and roles. Make sure you have the necessary permissions.",
                inline=False
            )
            embed.set_footer(text=f"Select from {len(templates)} available templates")
            
            view = TemplateSelectView(templates)
            await interaction.followup.send(embed=embed, view=view)
            
            # Wait for selection
            await asyncio.sleep(0.5)
            
            # Monitor for template selection
            async def wait_for_template_selection():
                for item in view.children:
                    if isinstance(item, TemplateSelect):
                        # Give user time to select
                        await asyncio.sleep(300)  # 5 minute timeout
                        return
            
            # Create monitoring task
            try:
                await asyncio.wait_for(wait_for_template_selection(), timeout=360)
            except asyncio.TimeoutError:
                pass
        
        except Exception as e:
            logger.error(f"Error in setup command: {e}\n{traceback.format_exc()}")
            await interaction.followup.send(
                embed=discord.Embed(
                    title="❌ Error",
                    description=f"An error occurred: {str(e)[:100]}",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )
    
    # ─────────────────────────────────────────────────────────────────────────────
    # CUSTOM TEMPLATE CREATION (WITH PREVIEW AND CONFIRMATION)
    # ─────────────────────────────────────────────────────────────────────────────
    
    async def handle_template_creation(
        self,
        interaction: Interaction,
        template: Dict[str, Any]
    ) -> None:
        """Handle the actual creation after confirmation."""
        try:
            await interaction.followup.send(
                embed=discord.Embed(
                    title="⏳ Creating Template...",
                    description="Setting up your server structure. This may take a moment.",
                    color=discord.Color.blurple()
                )
            )
            
            guild = interaction.guild
            success, message, tracker = await self.template_creator.create_template(
                guild,
                template,
                interaction
            )
            
            if not success:
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="❌ Creation Failed",
                        description=message,
                        color=discord.Color.red()
                    )
                )
        
        except Exception as e:
            logger.error(f"Error in template creation: {e}\n{traceback.format_exc()}")
            await interaction.followup.send(
                embed=discord.Embed(
                    title="❌ Error",
                    description=f"An error occurred: {str(e)[:100]}",
                    color=discord.Color.red()
                )
            )
    
    # ─────────────────────────────────────────────────────────────────────────────
    # UNDO COMMAND
    # ─────────────────────────────────────────────────────────────────────────────
    
    @app_commands.command(name='undo', description='Undo the last template installation')
    @app_commands.checks.has_permissions(manage_guild=True)
    async def undo(self, interaction: Interaction) -> None:
        """Undo the last template setup."""
        try:
            await interaction.response.defer()
            
            guild = interaction.guild
            tracker = self.undo_cache.get_setup(guild.id)
            
            if not tracker:
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="❌ No Setup to Undo",
                        description="No recent template setup found for this server.",
                        color=discord.Color.red()
                    )
                )
                return
            
            # Show warning and confirmation
            embed = discord.Embed(
                title="⚠️ Undo Confirmation Required",
                description=f"You are about to undo the '{tracker.template_name}' template setup.",
                color=discord.Color.orange()
            )
            embed.add_field(
                name="🗑️ Will Remove",
                value=f"Channels: {len(tracker.channels_created)}\nCategories: {len(tracker.categories_created)}\nRoles: {len(tracker.roles_created)}",
                inline=False
            )
            embed.add_field(
                name="⚠️ This action cannot be undone!",
                value="Click the button below to confirm.",
                inline=False
            )
            
            view = UndoConfirmView()
            message = await interaction.followup.send(embed=embed, view=view)
            
            # Wait for confirmation
            await view.wait()
            
            if not view.confirmed:
                await message.edit(
                    embed=discord.Embed(
                        title="❌ Undo Cancelled",
                        description="The undo operation was cancelled.",
                        color=discord.Color.red()
                    ),
                    view=None
                )
                return
            
            # Proceed with undo
            success, message_text = await self.template_deleter.undo_template(
                guild,
                tracker,
                interaction
            )
            
            if success:
                logger.info(f"Successfully undone template {tracker.template_name} in guild {guild.id}")
            else:
                logger.error(f"Failed to undo template: {message_text}")
        
        except Exception as e:
            logger.error(f"Error in undo command: {e}\n{traceback.format_exc()}")
            await interaction.followup.send(
                embed=discord.Embed(
                    title="❌ Error",
                    description=f"An error occurred: {str(e)[:100]}",
                    color=discord.Color.red()
                )
            )
    
    # ─────────────────────────────────────────────────────────────────────────────
    # DELETE COMMAND
    # ─────────────────────────────────────────────────────────────────────────────
    
    @app_commands.command(name='delete', description='Delete all server channels and roles (DANGEROUS)')
    @app_commands.checks.has_permissions(administrator=True)
    async def delete(self, interaction: Interaction) -> None:
        """Delete all server structure with warning."""
        try:
            await interaction.response.defer()
            
            # Show major warning
            embed = discord.Embed(
                title="🚨 DANGER ZONE - DESTRUCTIVE OPERATION",
                description="This will delete ALL channels, categories, and custom roles in this server.",
                color=discord.Color.red()
            )
            embed.add_field(
                name="⚠️ WARNING",
                value="This action:\n• Cannot be undone\n• Will delete the server structure\n• Will NOT delete @everyone role\n• Will NOT delete Discord-managed roles\n• Will NOT delete roles above the bot",
                inline=False
            )
            embed.add_field(
                name="🔒 Safety Measures",
                value="The channel where you ran this command will NOT be deleted.",
                inline=False
            )
            
            view = DeleteConfirmView()
            message = await interaction.followup.send(embed=embed, view=view)
            
            # Wait for confirmation
            await view.wait()
            
            if not view.confirmed:
                await message.edit(
                    embed=discord.Embed(
                        title="❌ Deletion Cancelled",
                        description="The deletion was cancelled.",
                        color=discord.Color.red()
                    ),
                    view=None
                )
                return
            
            # Proceed with deletion
            success, message_text = await self.template_deleter.delete_all_structure(
                interaction.guild,
                interaction
            )
            
            if success:
                logger.info(f"Successfully deleted server structure in guild {interaction.guild.id}")
            else:
                logger.error(f"Failed to delete structure: {message_text}")
        
        except Exception as e:
            logger.error(f"Error in delete command: {e}\n{traceback.format_exc()}")
            await interaction.followup.send(
                embed=discord.Embed(
                    title="❌ Error",
                    description=f"An error occurred: {str(e)[:100]}",
                    color=discord.Color.red()
                )
            )
    
    # ─────────────────────────────────────────────────────────────────────────────
    # INFO COMMAND
    # ─────────────────────────────────────────────────────────────────────────────
    
    @app_commands.command(name='info', description='View bot information and commands')
    async def info(self, interaction: Interaction) -> None:
        """Display bot information."""
        try:
            await interaction.response.defer()
            
            # Calculate uptime
            uptime = datetime.now() - self.startup_time
            uptime_str = f"{uptime.days}d {uptime.seconds // 3600}h {(uptime.seconds % 3600) // 60}m"
            
            # Count servers
            guild_count = len(self.bot.guilds)
            
            # Create info embed
            embed = discord.Embed(
                title="ℹ️ All In One Setup Bot",
                description="Automatically create complete Discord server structures from pre-made templates.",
                color=discord.Color.blurple()
            )
            
            embed.add_field(
                name="📊 Bot Information",
                value=f"**Name:** {BOT_NAME}\n**Version:** {BOT_VERSION}\n**Uptime:** {uptime_str}\n**Servers:** {guild_count}",
                inline=False
            )
            
            embed.add_field(
                name="📋 Templates Available",
                value=f"{len(self.template_manager.get_templates())} templates loaded",
                inline=False
            )
            
            embed.add_field(
                name="🎮 Commands",
                value="**/setup** - Browse and install templates\n"
                      "**/undo** - Undo the last template installation\n"
                      "**/delete** - Remove all server channels and roles\n"
                      "**/info** - View this message",
                inline=False
            )
            
            embed.add_field(
                name="🔐 Permissions Required",
                value="• Manage Server (for `/setup`)\n• Administrator (for `/delete`)",
                inline=False
            )
            
            embed.set_footer(text=f"Bot ID: {self.bot.user.id} | discord.py {discord.__version__}")
            
            await interaction.followup.send(embed=embed)
        
        except Exception as e:
            logger.error(f"Error in info command: {e}\n{traceback.format_exc()}")
            await interaction.followup.send(
                embed=discord.Embed(
                    title="❌ Error",
                    description=f"An error occurred: {str(e)[:100]}",
                    color=discord.Color.red()
                )
            )
    
    # ─────────────────────────────────────────────────────────────────────────────
    # EVENTS
    # ─────────────────────────────────────────────────────────────────────────────
    
    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Called when bot is ready."""
        logger.info(f"Bot is ready! Logged in as {self.bot.user}")
        logger.info(f"Connected to {len(self.bot.guilds)} guilds")
        logger.info(f"Loaded {len(self.template_manager.get_templates())} templates")
        
        # Set status
        await self.bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="/setup to get started"
            )
        )

# ═══════════════════════════════════════════════════════════════════════════════════
# BOT INITIALIZATION AND STARTUP
# ═══════════════════════════════════════════════════════════════════════════════════

async def setup_bot() -> commands.Bot:
    """Initialize and setup the bot."""
    # Create bot with intents
    intents = discord.Intents.default()
    intents.message_content = True
    intents.guild_messages = True
    intents.guilds = True
    
    bot = commands.Bot(
        command_prefix='!',
        intents=intents,
        application_id=None
    )
    
    # Add cog
    await bot.add_cog(AllInOneSetupBot(bot))
    
    logger.info("Bot setup complete")
    return bot

async def main() -> None:
    """Main entry point."""
    if not BOT_TOKEN:
        raise ValueError(
            "DISCORD_BOT_TOKEN not set! Please set the DISCORD_BOT_TOKEN environment variable."
        )
    
    bot = await setup_bot()
    
    try:
        logger.info("Starting bot...")
        await bot.start(BOT_TOKEN)
    except KeyboardInterrupt:
        logger.info("Bot interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}\n{traceback.format_exc()}")
    finally:
        await bot.close()

# ═══════════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    
    if sys.version_info < (3, 12):
        logger.error("Python 3.12+ is required")
        sys.exit(1)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot shutdown")
