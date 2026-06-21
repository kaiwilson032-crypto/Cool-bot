#!/usr/bin/env python3
"""
All In One Setup Discord Bot
Production-ready bot for automatic Discord server structure creation
Compatible with discord.py 2.x and Python 3.12+
FIX: Handles audioop import error that occurs in discord.py
"""

# CRITICAL FIX: Prevent audioop error before discord loads
import sys
import types
fake_audioop = types.ModuleType('audioop')
sys.modules['audioop'] = fake_audioop

import discord
from discord.ext import commands
import json
import os
import logging
from typing import Optional, Dict
from datetime import datetime
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
TEMPLATES_DIR = "templates"
BOT_VERSION = "1.0.0"
STARTUP_TIME = datetime.now()

class TemplateManager:
    """Manages template loading and validation"""
    
    def __init__(self, templates_dir: str = TEMPLATES_DIR):
        self.templates_dir = templates_dir
        self.templates: Dict = {}
        self._ensure_templates_exist()
        self.load_templates()
    
    def _ensure_templates_exist(self) -> None:
        """Create templates directory and example templates if they don't exist"""
        if not os.path.exists(self.templates_dir):
            os.makedirs(self.templates_dir)
            logger.info(f"Created templates directory: {self.templates_dir}")
            self._create_example_templates()
    
    def _create_example_templates(self) -> None:
        """Create example template files on first startup"""
        examples = {
            "gaming.json": {
                "name": "Gaming Hub",
                "description": "Professional esports & gaming community with competitive features",
                "roles": [
                    {"name": "Owner", "permissions": ["administrator"]},
                    {"name": "Admin", "permissions": ["manage_channels", "manage_messages", "manage_roles", "kick_members", "ban_members"]},
                    {"name": "Moderator", "permissions": ["manage_messages", "kick_members"]},
                    {"name": "Streamer", "permissions": []},
                    {"name": "Member", "permissions": []},
                    {"name": "Muted", "permissions": []}
                ],
                "categories": [
                    {
                        "name": "📢 Announcements",
                        "channels": [
                            {"name": "announcements", "type": "text"},
                            {"name": "updates", "type": "text"},
                            {"name": "events", "type": "text"}
                        ]
                    },
                    {
                        "name": "🎮 Gaming",
                        "channels": [
                            {"name": "general-chat", "type": "text"},
                            {"name": "game-discussions", "type": "text"},
                            {"name": "tournament-bracket", "type": "text"},
                            {"name": "lobby", "type": "voice"},
                            {"name": "competitive", "type": "voice"},
                            {"name": "casual", "type": "voice"}
                        ]
                    },
                    {
                        "name": "🎬 Content",
                        "channels": [
                            {"name": "streaming", "type": "text"},
                            {"name": "clips", "type": "text"},
                            {"name": "highlights", "type": "text"}
                        ]
                    },
                    {
                        "name": "🛡️ Moderation",
                        "channels": [
                            {"name": "mod-logs", "type": "text"},
                            {"name": "reports", "type": "text"},
                            {"name": "staff-chat", "type": "text"}
                        ]
                    }
                ]
            },
            "community.json": {
                "name": "Community Central",
                "description": "Inclusive community hub with engagement-focused features",
                "roles": [
                    {"name": "Owner", "permissions": ["administrator"]},
                    {"name": "Admin", "permissions": ["manage_channels", "manage_messages", "manage_roles", "kick_members", "ban_members"]},
                    {"name": "Moderator", "permissions": ["manage_messages", "kick_members"]},
                    {"name": "Contributor", "permissions": []},
                    {"name": "Member", "permissions": []},
                    {"name": "Restricted", "permissions": []}
                ],
                "categories": [
                    {
                        "name": "👋 Welcome",
                        "channels": [
                            {"name": "welcome", "type": "text"},
                            {"name": "rules", "type": "text"},
                            {"name": "introductions", "type": "text"},
                            {"name": "faq", "type": "text"}
                        ]
                    },
                    {
                        "name": "💬 Discussion",
                        "channels": [
                            {"name": "general", "type": "text"},
                            {"name": "off-topic", "type": "text"},
                            {"name": "memes", "type": "text"},
                            {"name": "showcase", "type": "text"}
                        ]
                    },
                    {
                        "name": "🎉 Events",
                        "channels": [
                            {"name": "events", "type": "text"},
                            {"name": "giveaways", "type": "text"},
                            {"name": "event-voice", "type": "voice"}
                        ]
                    },
                    {
                        "name": "📋 Community",
                        "channels": [
                            {"name": "feedback", "type": "text"},
                            {"name": "suggestions", "type": "text"},
                            {"name": "reports", "type": "text"}
                        ]
                    },
                    {
                        "name": "🔒 Moderation",
                        "channels": [
                            {"name": "mod-chat", "type": "text"},
                            {"name": "mod-logs", "type": "text"}
                        ]
                    }
                ]
            },
            "business.json": {
                "name": "Enterprise Pro",
                "description": "Enterprise-grade server for professional teams and organizations",
                "roles": [
                    {"name": "Owner", "permissions": ["administrator"]},
                    {"name": "Director", "permissions": ["manage_channels", "manage_messages", "manage_roles", "kick_members"]},
                    {"name": "Manager", "permissions": ["manage_messages"]},
                    {"name": "Team Lead", "permissions": []},
                    {"name": "Employee", "permissions": []},
                    {"name": "Guest", "permissions": []}
                ],
                "categories": [
                    {
                        "name": "📊 Executive",
                        "channels": [
                            {"name": "announcements", "type": "text"},
                            {"name": "company-updates", "type": "text"},
                            {"name": "board-meeting", "type": "voice"}
                        ]
                    },
                    {
                        "name": "🚀 Projects",
                        "channels": [
                            {"name": "project-alpha", "type": "text"},
                            {"name": "project-beta", "type": "text"},
                            {"name": "project-gamma", "type": "text"},
                            {"name": "sprint-planning", "type": "voice"},
                            {"name": "standups", "type": "voice"}
                        ]
                    },
                    {
                        "name": "💼 Departments",
                        "channels": [
                            {"name": "engineering", "type": "text"},
                            {"name": "marketing", "type": "text"},
                            {"name": "sales", "type": "text"},
                            {"name": "hr", "type": "text"}
                        ]
                    },
                    {
                        "name": "📚 Resources",
                        "channels": [
                            {"name": "documentation", "type": "text"},
                            {"name": "training", "type": "text"},
                            {"name": "knowledge-base", "type": "text"}
                        ]
                    },
                    {
                        "name": "⚙️ Operations",
                        "channels": [
                            {"name": "admin-logs", "type": "text"},
                            {"name": "security", "type": "text"},
                            {"name": "staff-only", "type": "text"}
                        ]
                    }
                ]
            },
            "education.json": {
                "name": "Academic Hub",
                "description": "Educational platform for schools, universities, and online learning communities",
                "roles": [
                    {"name": "Principal", "permissions": ["administrator"]},
                    {"name": "Teacher", "permissions": ["manage_channels", "manage_messages", "kick_members"]},
                    {"name": "Teaching Assistant", "permissions": ["manage_messages"]},
                    {"name": "Student", "permissions": []},
                    {"name": "Suspended", "permissions": []}
                ],
                "categories": [
                    {
                        "name": "📚 Courses",
                        "channels": [
                            {"name": "mathematics", "type": "text"},
                            {"name": "science", "type": "text"},
                            {"name": "literature", "type": "text"},
                            {"name": "history", "type": "text"}
                        ]
                    },
                    {
                        "name": "📖 Lectures",
                        "channels": [
                            {"name": "lecture-hall-a", "type": "voice"},
                            {"name": "lecture-hall-b", "type": "voice"},
                            {"name": "study-groups", "type": "voice"}
                        ]
                    },
                    {
                        "name": "✏️ Assignments",
                        "channels": [
                            {"name": "homework", "type": "text"},
                            {"name": "submissions", "type": "text"},
                            {"name": "grading", "type": "text"}
                        ]
                    },
                    {
                        "name": "🎓 Resources",
                        "channels": [
                            {"name": "syllabus", "type": "text"},
                            {"name": "study-materials", "type": "text"},
                            {"name": "exam-prep", "type": "text"}
                        ]
                    },
                    {
                        "name": "💬 Campus Life",
                        "channels": [
                            {"name": "announcements", "type": "text"},
                            {"name": "events", "type": "text"},
                            {"name": "clubs", "type": "text"}
                        ]
                    },
                    {
                        "name": "👨‍💼 Administration",
                        "channels": [
                            {"name": "staff-chat", "type": "text"},
                            {"name": "moderation", "type": "text"}
                        ]
                    }
                ]
            },
            "startup.json": {
                "name": "Startup Incubator",
                "description": "Fast-paced startup environment with agile workflows and innovation focus",
                "roles": [
                    {"name": "Founder", "permissions": ["administrator"]},
                    {"name": "Executive", "permissions": ["manage_channels", "manage_messages", "kick_members"]},
                    {"name": "Team Member", "permissions": []},
                    {"name": "Advisor", "permissions": []},
                    {"name": "Intern", "permissions": []}
                ],
                "categories": [
                    {
                        "name": "🎯 Strategy",
                        "channels": [
                            {"name": "vision", "type": "text"},
                            {"name": "roadmap", "type": "text"},
                            {"name": "quarterly-planning", "type": "voice"}
                        ]
                    },
                    {
                        "name": "⚡ Execution",
                        "channels": [
                            {"name": "sprint-backlog", "type": "text"},
                            {"name": "daily-standup", "type": "voice"},
                            {"name": "code-review", "type": "text"},
                            {"name": "deployment", "type": "text"}
                        ]
                    },
                    {
                        "name": "💰 Business",
                        "channels": [
                            {"name": "funding", "type": "text"},
                            {"name": "pitch-deck", "type": "text"},
                            {"name": "partnerships", "type": "text"},
                            {"name": "customer-feedback", "type": "text"}
                        ]
                    },
                    {
                        "name": "🎨 Product",
                        "channels": [
                            {"name": "design", "type": "text"},
                            {"name": "ux-research", "type": "text"},
                            {"name": "feature-requests", "type": "text"}
                        ]
                    },
                    {
                        "name": "🚀 Growth",
                        "channels": [
                            {"name": "marketing", "type": "text"},
                            {"name": "community", "type": "text"},
                            {"name": "metrics", "type": "text"}
                        ]
                    },
                    {
                        "name": "🔐 Internal",
                        "channels": [
                            {"name": "announcements", "type": "text"},
                            {"name": "admin-logs", "type": "text"}
                        ]
                    }
                ]
            },
            "creative.json": {
                "name": "Creative Studio",
                "description": "Collaborative space for artists, designers, and creatives to showcase and collaborate",
                "roles": [
                    {"name": "Studio Lead", "permissions": ["administrator"]},
                    {"name": "Creative Director", "permissions": ["manage_channels", "manage_messages"]},
                    {"name": "Artist", "permissions": []},
                    {"name": "Contributor", "permissions": []},
                    {"name": "Enthusiast", "permissions": []}
                ],
                "categories": [
                    {
                        "name": "🎨 Projects",
                        "channels": [
                            {"name": "current-projects", "type": "text"},
                            {"name": "briefs", "type": "text"},
                            {"name": "project-discussion", "type": "voice"}
                        ]
                    },
                    {
                        "name": "🖼️ Showcase",
                        "channels": [
                            {"name": "artwork", "type": "text"},
                            {"name": "design-showcase", "type": "text"},
                            {"name": "animations", "type": "text"},
                            {"name": "photography", "type": "text"}
                        ]
                    },
                    {
                        "name": "💡 Inspiration",
                        "channels": [
                            {"name": "inspiration-board", "type": "text"},
                            {"name": "references", "type": "text"},
                            {"name": "trends", "type": "text"}
                        ]
                    },
                    {
                        "name": "🎓 Learning",
                        "channels": [
                            {"name": "tutorials", "type": "text"},
                            {"name": "resources", "type": "text"},
                            {"name": "critiques", "type": "voice"}
                        ]
                    },
                    {
                        "name": "💬 Community",
                        "channels": [
                            {"name": "general-chat", "type": "text"},
                            {"name": "events", "type": "text"},
                            {"name": "collabs", "type": "text"}
                        ]
                    },
                    {
                        "name": "📋 Operations",
                        "channels": [
                            {"name": "announcements", "type": "text"},
                            {"name": "moderation", "type": "text"}
                        ]
                    }
                ]
            }
        }
        
        for filename, template in examples.items():
            filepath = os.path.join(self.templates_dir, filename)
            if not os.path.exists(filepath):
                with open(filepath, 'w') as f:
                    json.dump(template, f, indent=2)
                logger.info(f"Created example template: {filename}")
    
    def load_templates(self) -> None:
        """Load all template JSON files from templates directory"""
        self.templates.clear()
        
        if not os.path.exists(self.templates_dir):
            logger.warning(f"Templates directory not found: {self.templates_dir}")
            return
        
        for filename in os.listdir(self.templates_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.templates_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        template = json.load(f)
                        template_id = filename.replace('.json', '')
                        self.templates[template_id] = template
                        logger.info(f"Loaded template: {template_id}")
                except Exception as e:
                    logger.error(f"Failed to load template {filename}: {e}")
    
    def get_templates(self) -> Dict:
        return self.templates
    
    def get_template(self, template_id: str) -> Optional[Dict]:
        return self.templates.get(template_id)


class SetupView(discord.ui.View):
    """View for template selection menu"""
    
    def __init__(self, templates: Dict, bot_instance: 'SetupBot'):
        super().__init__(timeout=300)
        self.templates = templates
        self.bot = bot_instance
        
        options = [
            discord.SelectOption(
                label=template_data.get('name', template_id),
                value=template_id,
                description=template_data.get('description', 'No description')[:100]
            )
            for template_id, template_data in templates.items()
        ]
        
        if options:
            select = discord.ui.Select(
                placeholder="Choose a server template...",
                options=options,
                min_values=1,
                max_values=1
            )
            select.callback = self.select_template
            self.add_item(select)
    
    async def select_template(self, interaction: discord.Interaction) -> None:
        """Handle template selection"""
        if not interaction.response.is_done():
            await interaction.response.defer()
        
        select_value = interaction.data['values'][0]
        template_data = self.templates[select_value]
        
        embed = discord.Embed(
            title=f"Template Preview: {template_data.get('name')}",
            description=template_data.get('description', 'No description'),
            color=discord.Color.blue()
        )
        
        num_categories = len(template_data.get('categories', []))
        num_channels = sum(len(cat.get('channels', [])) for cat in template_data.get('categories', []))
        num_roles = len(template_data.get('roles', []))
        
        embed.add_field(name="Categories", value=str(num_categories), inline=True)
        embed.add_field(name="Channels", value=str(num_channels), inline=True)
        embed.add_field(name="Roles", value=str(num_roles), inline=True)
        embed.set_footer(text="Click 'Create Template' to proceed or 'Cancel' to go back")
        
        confirm_view = ConfirmCreateView(
            template_id=select_value,
            template_data=template_data,
            bot_instance=self.bot,
            interaction_user=interaction.user
        )
        
        await interaction.followup.send(embed=embed, view=confirm_view, ephemeral=True)


class ConfirmCreateView(discord.ui.View):
    """View for confirming template creation"""
    
    def __init__(self, template_id: str, template_data: Dict, bot_instance: 'SetupBot', interaction_user: discord.User):
        super().__init__(timeout=300)
        self.template_id = template_id
        self.template_data = template_data
        self.bot = bot_instance
        self.interaction_user = interaction_user
    
    @discord.ui.button(label="Create Template", style=discord.ButtonStyle.success, emoji="✅")
    async def create_template(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.defer()
        
        if interaction.user.id != self.interaction_user.id:
            await interaction.followup.send("You cannot use this button.", ephemeral=True)
            return
        
        if not interaction.guild.me.guild_permissions.administrator:
            await interaction.followup.send("❌ Bot requires Administrator permission.", ephemeral=True)
            return
        
        try:
            # Initial progress message
            progress_embed = discord.Embed(
                title="⚙️ Setting up your server...",
                description="Creating roles and structure",
                color=discord.Color.blurple()
            )
            progress_msg = await interaction.followup.send(embed=progress_embed, ephemeral=True)
            
            created_resources = {'roles': [], 'categories': [], 'channels': []}
            
            # Create roles
            role_count = len(self.template_data.get('roles', []))
            for idx, role_data in enumerate(self.template_data.get('roles', []), 1):
                try:
                    permissions = discord.Permissions()
                    for perm in role_data.get('permissions', []):
                        setattr(permissions, perm, True)
                    
                    role = await interaction.guild.create_role(
                        name=role_data['name'],
                        permissions=permissions
                    )
                    created_resources['roles'].append(role.id)
                    logger.info(f"Created role: {role.name}")
                    
                    # Update progress
                    progress_embed = discord.Embed(
                        title="⚙️ Setting up your server...",
                        description=f"Creating roles ({idx}/{role_count})",
                        color=discord.Color.blurple()
                    )
                    await progress_msg.edit(embed=progress_embed)
                except Exception as e:
                    logger.error(f"Failed to create role: {e}")
            
            # Create categories and channels
            category_count = len(self.template_data.get('categories', []))
            for cat_idx, category_data in enumerate(self.template_data.get('categories', []), 1):
                try:
                    # Update progress for category
                    progress_embed = discord.Embed(
                        title="⚙️ Setting up your server...",
                        description=f"Creating categories ({cat_idx}/{category_count})",
                        color=discord.Color.blurple()
                    )
                    await progress_msg.edit(embed=progress_embed)
                    
                    category = await interaction.guild.create_category(name=category_data['name'])
                    created_resources['categories'].append(category.id)
                    logger.info(f"Created category: {category.name}")
                    
                    channel_count = len(category_data.get('channels', []))
                    for chan_idx, channel_data in enumerate(category_data.get('channels', []), 1):
                        try:
                            channel_type = channel_data.get('type', 'text')
                            
                            if channel_type == 'text':
                                channel = await interaction.guild.create_text_channel(
                                    name=channel_data['name'],
                                    category=category
                                )
                            elif channel_type == 'voice':
                                channel = await interaction.guild.create_voice_channel(
                                    name=channel_data['name'],
                                    category=category
                                )
                            else:
                                continue
                            
                            created_resources['channels'].append(channel.id)
                            logger.info(f"Created channel: {channel.name}")
                            
                            # Update progress for channels
                            progress_embed = discord.Embed(
                                title="⚙️ Setting up your server...",
                                description=f"Creating channels in {category_data['name']} ({chan_idx}/{channel_count})",
                                color=discord.Color.blurple()
                            )
                            await progress_msg.edit(embed=progress_embed)
                        except Exception as e:
                            logger.error(f"Failed to create channel: {e}")
                
                except Exception as e:
                    logger.error(f"Failed to create category: {e}")
            
            self.bot.last_setup[interaction.guild.id] = {
                'template_id': self.template_id,
                'resources': created_resources,
                'timestamp': datetime.now()
            }
            
            # Final completion message
            embed = discord.Embed(
                title="✅ Template Created Successfully!",
                description=f"Server structure from **{self.template_data.get('name')}** has been created.",
                color=discord.Color.green()
            )
            embed.add_field(name="✨ Roles Created", value=len(created_resources['roles']), inline=True)
            embed.add_field(name="📁 Categories Created", value=len(created_resources['categories']), inline=True)
            embed.add_field(name="💬 Channels Created", value=len(created_resources['channels']), inline=True)
            embed.set_footer(text="Use /priority to reorder categories or /settings to configure channels")
            
            await progress_msg.edit(embed=embed)
        
        except Exception as e:
            logger.error(f"Error creating template: {e}")
            await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)
    
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger, emoji="❌")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.defer()
        if interaction.user.id != self.interaction_user.id:
            await interaction.followup.send("You cannot use this button.", ephemeral=True)
            return
        await interaction.followup.send("Template creation cancelled.", ephemeral=True)


class ConfirmUndoView(discord.ui.View):
    """View for confirming undo operation"""
    
    def __init__(self, bot_instance: 'SetupBot', interaction_user: discord.User):
        super().__init__(timeout=60)
        self.bot = bot_instance
        self.interaction_user = interaction_user
    
    @discord.ui.button(label="Confirm Undo", style=discord.ButtonStyle.danger, emoji="⚠️")
    async def confirm_undo(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.defer()
        
        if interaction.user.id != self.interaction_user.id:
            await interaction.followup.send("You cannot use this button.", ephemeral=True)
            return
        
        guild_id = interaction.guild.id
        
        if guild_id not in self.bot.last_setup:
            await interaction.followup.send("❌ No previous setup found to undo.", ephemeral=True)
            return
        
        setup_data = self.bot.last_setup[guild_id]
        resources = setup_data['resources']
        deleted_count = {'roles': 0, 'categories': 0, 'channels': 0}
        
        try:
            for channel_id in resources.get('channels', []):
                try:
                    channel = interaction.guild.get_channel(channel_id)
                    if channel:
                        await channel.delete()
                        deleted_count['channels'] += 1
                except Exception as e:
                    logger.error(f"Failed to delete channel: {e}")
            
            for category_id in resources.get('categories', []):
                try:
                    category = interaction.guild.get_channel(category_id)
                    if category:
                        await category.delete()
                        deleted_count['categories'] += 1
                except Exception as e:
                    logger.error(f"Failed to delete category: {e}")
            
            for role_id in resources.get('roles', []):
                try:
                    role = interaction.guild.get_role(role_id)
                    if role and role.id != interaction.guild.default_role.id:
                        await role.delete()
                        deleted_count['roles'] += 1
                except Exception as e:
                    logger.error(f"Failed to delete role: {e}")
            
            del self.bot.last_setup[guild_id]
            
            embed = discord.Embed(
                title="✅ Setup Undone Successfully!",
                description="All created resources have been removed.",
                color=discord.Color.green()
            )
            embed.add_field(name="Roles Deleted", value=deleted_count['roles'], inline=True)
            embed.add_field(name="Categories Deleted", value=deleted_count['categories'], inline=True)
            embed.add_field(name="Channels Deleted", value=deleted_count['channels'], inline=True)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
        
        except Exception as e:
            logger.error(f"Error during undo: {e}")
            await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)
    
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary, emoji="❌")
    async def cancel_undo(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.defer()
        if interaction.user.id != self.interaction_user.id:
            await interaction.followup.send("You cannot use this button.", ephemeral=True)
            return
        await interaction.followup.send("Undo operation cancelled.", ephemeral=True)


class ConfirmDeleteView(discord.ui.View):
    """View for confirming dangerous delete operation"""
    
    def __init__(self, bot_instance: 'SetupBot', interaction_user: discord.User):
        super().__init__(timeout=60)
        self.bot = bot_instance
        self.interaction_user = interaction_user
    
    @discord.ui.button(label="⚠️ PERMANENTLY DELETE ALL", style=discord.ButtonStyle.danger, emoji="🗑️")
    async def confirm_delete(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.defer()
        
        if interaction.user.id != self.interaction_user.id:
            await interaction.followup.send("You cannot use this button.", ephemeral=True)
            return
        
        guild = interaction.guild
        deleted_count = {'roles': 0, 'channels': 0, 'categories': 0}
        
        try:
            channels = list(guild.channels)
            
            for channel in channels:
                try:
                    if channel.id == interaction.channel.id:
                        continue
                    
                    await channel.delete()
                    if isinstance(channel, discord.CategoryChannel):
                        deleted_count['categories'] += 1
                    else:
                        deleted_count['channels'] += 1
                except Exception as e:
                    logger.error(f"Failed to delete channel: {e}")
            
            for role in guild.roles:
                try:
                    if (role.id != guild.default_role.id and 
                        not role.managed and 
                        role < guild.me.top_role):
                        await role.delete()
                        deleted_count['roles'] += 1
                except Exception as e:
                    logger.error(f"Failed to delete role: {e}")
            
            embed = discord.Embed(
                title="🗑️ Server Cleanup Complete",
                description="All designated channels and roles have been deleted.",
                color=discord.Color.orange()
            )
            embed.add_field(name="Roles Deleted", value=deleted_count['roles'], inline=True)
            embed.add_field(name="Channels Deleted", value=deleted_count['channels'], inline=True)
            embed.add_field(name="Categories Deleted", value=deleted_count['categories'], inline=True)
            embed.add_field(name="⚠️ Warning", value="This action cannot be undone.", inline=False)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
        
        except Exception as e:
            logger.error(f"Error during delete: {e}")
            await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)
    
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary, emoji="❌")
    async def cancel_delete(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.defer()
        if interaction.user.id != self.interaction_user.id:
            await interaction.followup.send("You cannot use this button.", ephemeral=True)
            return
        await interaction.followup.send("Delete operation cancelled.", ephemeral=True)


class RenameChannelModal(discord.ui.Modal, title="Rename Channel"):
    """Modal for renaming a channel"""
    
    new_name = discord.ui.TextInput(
        label="New Channel Name",
        placeholder="Enter new channel name",
        required=True,
        max_length=100
    )
    
    def __init__(self, channel: discord.TextChannel):
        super().__init__()
        self.channel = channel
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            await self.channel.edit(name=self.new_name.value)
            embed = discord.Embed(
                title="✅ Channel Renamed",
                description=f"Channel is now called **{self.new_name.value}**",
                color=discord.Color.green()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)


class EditTopicModal(discord.ui.Modal, title="Edit Channel Topic"):
    """Modal for editing channel topic"""
    
    topic = discord.ui.TextInput(
        label="Channel Topic",
        placeholder="Enter channel topic",
        required=False,
        max_length=1024
    )
    
    def __init__(self, channel: discord.TextChannel):
        super().__init__()
        self.channel = channel
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            await self.channel.edit(topic=self.topic.value)
            embed = discord.Embed(
                title="✅ Topic Updated",
                description=f"Channel topic is now: {self.topic.value if self.topic.value else '(empty)'}",
                color=discord.Color.green()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)


class SetupBot(commands.Cog):
    """Main bot cog with all commands"""
    
    def __init__(self, bot: commands.Bot, template_manager: TemplateManager):
        self.bot = bot
        self.template_manager = template_manager
        self.last_setup: Dict = {}
    
    @discord.app_commands.command(name="setup", description="Browse and install server templates")
    async def setup(self, interaction: discord.Interaction) -> None:
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="You need Administrator permissions to use this command.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        templates = self.template_manager.get_templates()
        
        if not templates:
            embed = discord.Embed(
                title="❌ No Templates Available",
                description="No templates are currently loaded.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🔧 Server Template Setup",
            description="Select a template below to see details and create your server structure.",
            color=discord.Color.blue()
        )
        
        view = SetupView(templates, self)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.app_commands.command(name="undo", description="Undo the last template installation")
    async def undo(self, interaction: discord.Interaction) -> None:
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="You need Administrator permissions to use this command.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        guild_id = interaction.guild.id
        
        if guild_id not in self.last_setup:
            embed = discord.Embed(
                title="ℹ️ No Setup to Undo",
                description="No previous template installation found for this server.",
                color=discord.Color.blue()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        setup_data = self.last_setup[guild_id]
        template_name = self.template_manager.get_template(setup_data['template_id']).get('name', 'Unknown')
        
        embed = discord.Embed(
            title="⚠️ Confirm Undo Operation",
            description=f"This will remove all resources created by the **{template_name}** template.",
            color=discord.Color.orange()
        )
        
        view = ConfirmUndoView(self, interaction.user)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.app_commands.command(name="delete", description="Remove all server channels and roles (DANGEROUS)")
    async def delete(self, interaction: discord.Interaction) -> None:
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="You need Administrator permissions to use this command.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🚨 DANGEROUS OPERATION 🚨",
            description="This will **permanently delete** all channels and roles from this server.",
            color=discord.Color.red()
        )
        embed.add_field(
            name="⚠️ Will be deleted:",
            value="• All text channels\n• All voice channels\n• All categories\n• All custom roles",
            inline=False
        )
        embed.add_field(
            name="✅ Will be preserved:",
            value="• @everyone role\n• Discord managed roles\n• Command execution channel",
            inline=False
        )
        
        view = ConfirmDeleteView(self, interaction.user)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.app_commands.command(name="priority", description="Set category priority from 1 (top) to 5 (bottom)")
    @discord.app_commands.describe(category="Select category to reorder", priority="Position 1-5 (1=top, 5=bottom)")
    async def priority(self, interaction: discord.Interaction, category: discord.CategoryChannel, priority: int) -> None:
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="You need Administrator permissions to use this command.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if priority < 1 or priority > 5:
            embed = discord.Embed(
                title="❌ Invalid Priority",
                description="Priority must be between 1 (top) and 5 (bottom).",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await interaction.response.defer()
        
        try:
            # Position is 0-indexed, so priority 1 = position 0, priority 5 = position 4
            position = priority - 1
            await category.edit(position=position)
            
            embed = discord.Embed(
                title="✅ Priority Updated",
                description=f"**{category.name}** moved to position **{priority}/5**",
                color=discord.Color.green()
            )
            embed.add_field(name="Position", value=f"{'▓' * priority}{'░' * (5 - priority)}", inline=False)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)
    
    @discord.app_commands.command(name="dupe", description="Scan and delete duplicate channels")
    async def dupe(self, interaction: discord.Interaction) -> None:
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="You need Administrator permissions to use this command.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await interaction.response.defer()
        
        try:
            # Show scanning progress
            scan_embed = discord.Embed(
                title="🔍 Scanning for duplicates...",
                description="Please wait while I scan all channels",
                color=discord.Color.blurple()
            )
            progress_msg = await interaction.followup.send(embed=scan_embed, ephemeral=True)
            
            # Group channels by name
            channel_names = {}
            all_channels = []
            
            for category in interaction.guild.categories:
                for channel in category.channels:
                    all_channels.append(channel)
                    if channel.name not in channel_names:
                        channel_names[channel.name] = []
                    channel_names[channel.name].append(channel)
            
            # Find duplicates
            duplicates = {name: channels for name, channels in channel_names.items() if len(channels) > 1}
            
            if not duplicates:
                result_embed = discord.Embed(
                    title="✅ No Duplicates Found",
                    description="Your server has no duplicate channels!",
                    color=discord.Color.green()
                )
                await progress_msg.edit(embed=result_embed)
                return
            
            # Show duplicates and ask for confirmation
            dup_list = ""
            total_dupes = 0
            for name, channels in duplicates.items():
                dup_list += f"\n**{name}** - {len(channels)} duplicates"
                total_dupes += len(channels) - 1  # Keep 1, delete the rest
            
            confirm_embed = discord.Embed(
                title="⚠️ Duplicates Found",
                description=f"Found {len(duplicates)} duplicate channel(s):\n{dup_list}",
                color=discord.Color.orange()
            )
            confirm_embed.add_field(
                name="Action",
                value=f"Will delete {total_dupes} channel(s) and keep the oldest of each",
                inline=False
            )
            
            # Create confirmation view
            confirm_view = discord.ui.View()
            
            async def confirm_delete(interaction: discord.Interaction):
                await interaction.response.defer()
                
                deleted_count = 0
                deleted_names = []
                
                for name, channels in duplicates.items():
                    # Sort by creation time, keep the oldest (first created)
                    sorted_channels = sorted(channels, key=lambda c: c.created_at)
                    
                    # Delete all except the first one
                    for channel in sorted_channels[1:]:
                        try:
                            await channel.delete()
                            deleted_count += 1
                            deleted_names.append(f"• {channel.name} (ID: {channel.id})")
                            logger.info(f"Deleted duplicate channel: {channel.name}")
                        except Exception as e:
                            logger.error(f"Failed to delete channel {channel.name}: {e}")
                
                success_embed = discord.Embed(
                    title="✅ Duplicates Deleted",
                    description=f"Successfully deleted {deleted_count} duplicate channel(s)",
                    color=discord.Color.green()
                )
                success_embed.add_field(
                    name="Deleted Channels",
                    value="\n".join(deleted_names) if deleted_names else "None",
                    inline=False
                )
                success_embed.add_field(
                    name="Kept",
                    value="The oldest copy of each duplicate was kept",
                    inline=False
                )
                
                await interaction.followup.send(embed=success_embed, ephemeral=True)
            
            async def cancel_delete(interaction: discord.Interaction):
                await interaction.response.defer()
                
                cancel_embed = discord.Embed(
                    title="❌ Cancelled",
                    description="No channels were deleted",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=cancel_embed, ephemeral=True)
            
            confirm_btn = discord.ui.Button(label="Delete Duplicates", style=discord.ButtonStyle.danger, emoji="🗑️")
            confirm_btn.callback = confirm_delete
            confirm_view.add_item(confirm_btn)
            
            cancel_btn = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.secondary, emoji="❌")
            cancel_btn.callback = cancel_delete
            confirm_view.add_item(cancel_btn)
            
            await progress_msg.edit(embed=confirm_embed, view=confirm_view)
        
        except Exception as e:
            logger.error(f"Error in dupe command: {e}")
            await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)
    
    @discord.app_commands.command(name="settings", description="Configure channel permissions and visibility")
    @discord.app_commands.describe(channel="Select channel to configure")
    async def settings(self, interaction: discord.Interaction, channel: Optional[discord.TextChannel] = None) -> None:
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="You need Administrator permissions to use this command.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if not channel:
            embed = discord.Embed(
                title="❌ Invalid Channel",
                description="Please specify a text channel to configure.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        embed = discord.Embed(
            title=f"⚙️ Channel Settings: {channel.name}",
            description="Select an action to perform",
            color=discord.Color.blue()
        )
        
        view = discord.ui.View()
        
        # Quick role selector
        async def show_role_selector(interaction: discord.Interaction):
            await interaction.response.defer()
            
            roles = [r for r in interaction.guild.roles if r != interaction.guild.default_role][:25]
            
            if not roles:
                await interaction.followup.send("❌ No roles available.", ephemeral=True)
                return
            
            role_embed = discord.Embed(
                title=f"👥 Role Visibility: {channel.name}",
                description="Select roles that should see this channel",
                color=discord.Color.blue()
            )
            
            role_view = discord.ui.View()
            
            role_options = [
                discord.SelectOption(
                    label=role.name[:100],
                    value=str(role.id),
                    description=f"ID: {role.id}"
                )
                for role in roles
            ]
            
            role_select = discord.ui.Select(
                placeholder="Choose roles (can select multiple)...",
                options=role_options,
                min_values=1,
                max_values=min(25, len(role_options))
            )
            
            async def role_select_callback(interaction: discord.Interaction):
                await interaction.response.defer()
                selected_role_ids = [int(rid) for rid in interaction.data['values']]
                
                try:
                    # First, deny everyone
                    await channel.set_permissions(interaction.guild.default_role, read_messages=False)
                    
                    # Then allow selected roles
                    allowed_count = 0
                    for role_id in selected_role_ids:
                        role = interaction.guild.get_role(role_id)
                        if role:
                            await channel.set_permissions(role, read_messages=True, send_messages=True)
                            allowed_count += 1
                    
                    role_names = [interaction.guild.get_role(rid).name for rid in selected_role_ids if interaction.guild.get_role(rid)]
                    
                    success_embed = discord.Embed(
                        title="✅ Channel Visibility Updated",
                        description=f"{channel.name} is now visible to:\n" + "\n".join([f"• {name}" for name in role_names]),
                        color=discord.Color.green()
                    )
                    await interaction.followup.send(embed=success_embed, ephemeral=True)
                except Exception as e:
                    await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)
            
            role_select.callback = role_select_callback
            role_view.add_item(role_select)
            
            await interaction.followup.send(embed=role_embed, view=role_view, ephemeral=True)
        
        # Permissions button
        async def show_perms(interaction: discord.Interaction):
            await interaction.response.defer()
            
            roles = interaction.guild.roles
            options = [
                discord.SelectOption(
                    label=role.name[:100],
                    value=str(role.id),
                    description="Configure this role's permissions"
                )
                for role in roles[:25]
            ]
            
            perm_embed = discord.Embed(
                title=f"👥 Role Permissions: {channel.name}",
                description="Select a role to manage individually",
                color=discord.Color.blue()
            )
            
            perm_view = discord.ui.View()
            perm_select = discord.ui.Select(
                placeholder="Choose role...",
                options=options,
                min_values=1,
                max_values=1
            )
            
            async def role_callback(interaction: discord.Interaction):
                await interaction.response.defer()
                role_id = int(interaction.data['values'][0])
                role = interaction.guild.get_role(role_id)
                
                if not role:
                    await interaction.followup.send("❌ Role not found.", ephemeral=True)
                    return
                
                perms_view = discord.ui.View()
                
                # Allow all
                async def allow_all(interaction: discord.Interaction):
                    await interaction.response.defer()
                    try:
                        await channel.set_permissions(role, read_messages=True, send_messages=True)
                        msg = await interaction.followup.send(f"✅ Allowed all permissions for {role.name}", ephemeral=True)
                    except Exception as e:
                        await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)
                
                # Deny all
                async def deny_all(interaction: discord.Interaction):
                    await interaction.response.defer()
                    try:
                        await channel.set_permissions(role, read_messages=False, send_messages=False)
                        msg = await interaction.followup.send(f"🚫 Denied all permissions for {role.name}", ephemeral=True)
                    except Exception as e:
                        await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)
                
                # View only
                async def view_only(interaction: discord.Interaction):
                    await interaction.response.defer()
                    try:
                        await channel.set_permissions(role, read_messages=True, send_messages=False)
                        msg = await interaction.followup.send(f"👁️ View-only for {role.name}", ephemeral=True)
                    except Exception as e:
                        await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)
                
                allow_btn = discord.ui.Button(label="Allow All", style=discord.ButtonStyle.success, emoji="✅")
                allow_btn.callback = allow_all
                perms_view.add_item(allow_btn)
                
                view_btn = discord.ui.Button(label="View Only", style=discord.ButtonStyle.primary, emoji="👁️")
                view_btn.callback = view_only
                perms_view.add_item(view_btn)
                
                deny_btn = discord.ui.Button(label="Deny All", style=discord.ButtonStyle.danger, emoji="🚫")
                deny_btn.callback = deny_all
                perms_view.add_item(deny_btn)
                
                perm_config_embed = discord.Embed(
                    title=f"🔐 Permissions for {role.name}",
                    description=f"Configure {role.name}'s access to {channel.name}",
                    color=discord.Color.blue()
                )
                
                await interaction.followup.send(embed=perm_config_embed, view=perms_view, ephemeral=True)
            
            perm_select.callback = role_callback
            perm_view.add_item(perm_select)
            
            await interaction.followup.send(embed=perm_embed, view=perm_view, ephemeral=True)
        
        # Rename button
        async def rename_channel(interaction: discord.Interaction):
            await interaction.response.send_modal(RenameChannelModal(channel))
        
        # Topic button
        async def edit_topic(interaction: discord.Interaction):
            await interaction.response.send_modal(EditTopicModal(channel))
        
        # Quick role visibility button
        role_visibility_btn = discord.ui.Button(label="Quick Role Visibility", style=discord.ButtonStyle.success, emoji="👁️")
        role_visibility_btn.callback = show_role_selector
        view.add_item(role_visibility_btn)
        
        perms_btn = discord.ui.Button(label="Detailed Permissions", style=discord.ButtonStyle.primary, emoji="👥")
        perms_btn.callback = show_perms
        view.add_item(perms_btn)
        
        rename_btn = discord.ui.Button(label="Rename Channel", style=discord.ButtonStyle.secondary, emoji="✏️")
        rename_btn.callback = rename_channel
        view.add_item(rename_btn)
        
        topic_btn = discord.ui.Button(label="Edit Topic", style=discord.ButtonStyle.secondary, emoji="📝")
        topic_btn.callback = edit_topic
        view.add_item(topic_btn)
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.app_commands.command(name="info", description="View bot information and available commands")
    async def info(self, interaction: discord.Interaction) -> None:
        uptime = datetime.now() - STARTUP_TIME
        uptime_str = f"{uptime.days}d {uptime.seconds // 3600}h {(uptime.seconds // 60) % 60}m"
        
        embed = discord.Embed(
            title="🤖 All In One Setup - Bot Information",
            color=discord.Color.blurple()
        )
        
        embed.add_field(name="Bot Name", value="All In One Setup", inline=True)
        embed.add_field(name="Version", value=BOT_VERSION, inline=True)
        embed.add_field(name="Uptime", value=uptime_str, inline=True)
        embed.add_field(name="Templates Loaded", value=len(self.template_manager.get_templates()), inline=True)
        embed.add_field(name="Servers Using Bot", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="Developer", value="Wilson", inline=True)
        embed.add_field(
            name="📋 Template Commands",
            value=(
                "**`/setup`** - Browse and install from 6 professional templates\n"
                "Select a template, preview the structure, and auto-create all channels & roles with real-time progress tracking\n\n"
                "**`/undo`** - Safely undo the last template installation\n"
                "Removes all resources created by the previous setup. Existing content is preserved\n\n"
                "**`/delete`** - Emergency server cleanup (DANGEROUS!)\n"
                "Removes all channels and custom roles. Use with caution - this cannot be undone!"
            ),
            inline=False
        )
        embed.add_field(
            name="⚙️ Management Commands",
            value=(
                "**`/priority [category] [1-5]`** - Set category priority\n"
                "Position 1 = top, 5 = bottom. Organize categories exactly how you want\n\n"
                "**`/settings [channel]`** - Configure channel permissions\n"
                "Quick role visibility selector, detailed per-role permissions, rename channels, or edit topics\n\n"
                "**`/dupe`** - Delete duplicate channels\n"
                "Scans all channels, finds duplicates, and safely removes them (keeps oldest copy)\n\n"
                "**`/info`** - View this information\n"
                "Shows bot stats, command descriptions, and templates"
            ),
            inline=False
        )
        embed.add_field(
            name="📌 Available Templates",
            value=(
                "🎮 **Gaming Hub** - Esports & competitive gaming\n"
                "👥 **Community Central** - Inclusive community hub\n"
                "💼 **Enterprise Pro** - Professional team organization\n"
                "🎓 **Academic Hub** - Schools & universities\n"
                "🚀 **Startup Incubator** - Fast-paced startup environment\n"
                "🎨 **Creative Studio** - Artists & designers collaboration"
            ),
            inline=False
        )
        embed.add_field(
            name="ℹ️ Quick Start Guide",
            value=(
                "1️⃣ Run `/setup` to browse templates\n"
                "2️⃣ Preview template structure and resources\n"
                "3️⃣ Click 'Create Template' - watch real-time progress\n"
                "4️⃣ Customize with `/priority` and `/settings`\n"
                "5️⃣ Fine-tune channels, roles, and permissions"
            ),
            inline=False
        )
        embed.add_field(
            name="⚠️ IMPORTANT DISCLAIMER",
            value=(
                "✅ **Templates are starting points!**\n\n"
                "After creating a template, **always review and customize**:\n"
                "• **Channel Purposes** - Verify each channel matches your needs\n"
                "• **Channel Permissions** - Check role visibility with `/settings`\n"
                "• **Role Permissions** - Review what each role can do\n"
                "• **Channel Order** - Use `/priority` to organize categories\n"
                "• **Channel Names** - Rename with `/settings` if needed\n"
                "• **Channel Topics** - Add descriptions with `/settings`\n\n"
                "Templates provide a solid foundation, but **your server, your rules!**"
            ),
            inline=False
        )
        
        embed.set_footer(text="Built with discord.py 2.x | Always double-check your setup!")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def main() -> None:
    """Start the bot"""
    token = os.getenv('DISCORD_TOKEN')
    
    if not token:
        logger.error("DISCORD_TOKEN environment variable not set")
        raise ValueError("DISCORD_TOKEN environment variable is required")
    
    intents = discord.Intents.default()
    intents.message_content = True
    
    bot = commands.Bot(command_prefix="/", intents=intents)
    
    template_manager = TemplateManager()
    
    @bot.event
    async def on_ready() -> None:
        """Bot startup event"""
        logger.info(f"✅ Bot logged in as {bot.user}")
        logger.info(f"📁 Loaded {len(template_manager.get_templates())} templates")
        try:
            synced = await bot.tree.sync()
            logger.info(f"🔄 Synced {len(synced)} command(s)")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")
    
    @bot.event
    async def on_error(event: str, *args, **kwargs) -> None:
        """Global error handler"""
        logger.error(f"Error in {event}:", exc_info=True)
    
    cog = SetupBot(bot, template_manager)
    await bot.add_cog(cog)
    
    try:
        await bot.start(token)
    except KeyboardInterrupt:
        logger.info("Bot shutdown by user")
        await bot.close()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
