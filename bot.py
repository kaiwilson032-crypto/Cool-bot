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
                "name": "Gaming Server",
                "description": "Perfect for gaming communities with voice channels and game roles",
                "roles": [
                    {"name": "Owner", "permissions": ["administrator"]},
                    {"name": "Moderator", "permissions": ["manage_channels", "manage_messages", "kick_members", "ban_members"]},
                    {"name": "Member", "permissions": []},
                    {"name": "Muted", "permissions": []}
                ],
                "categories": [
                    {
                        "name": "General",
                        "channels": [
                            {"name": "announcements", "type": "text"},
                            {"name": "general", "type": "text"},
                            {"name": "rules", "type": "text"}
                        ]
                    },
                    {
                        "name": "Voice",
                        "channels": [
                            {"name": "Lobby", "type": "voice"},
                            {"name": "Gaming", "type": "voice"},
                            {"name": "AFK", "type": "voice"}
                        ]
                    },
                    {
                        "name": "Staff",
                        "channels": [
                            {"name": "staff-chat", "type": "text"},
                            {"name": "logs", "type": "text"}
                        ]
                    }
                ]
            },
            "community.json": {
                "name": "Community Server",
                "description": "A welcoming community space for general discussion and events",
                "roles": [
                    {"name": "Owner", "permissions": ["administrator"]},
                    {"name": "Moderator", "permissions": ["manage_channels", "manage_messages", "kick_members"]},
                    {"name": "Member", "permissions": []},
                    {"name": "Muted", "permissions": []}
                ],
                "categories": [
                    {
                        "name": "Welcome",
                        "channels": [
                            {"name": "welcome", "type": "text"},
                            {"name": "rules", "type": "text"},
                            {"name": "introductions", "type": "text"}
                        ]
                    },
                    {
                        "name": "Discussion",
                        "channels": [
                            {"name": "general", "type": "text"},
                            {"name": "events", "type": "text"},
                            {"name": "feedback", "type": "text"}
                        ]
                    },
                    {
                        "name": "Moderation",
                        "channels": [
                            {"name": "mod-chat", "type": "text"},
                            {"name": "reports", "type": "text"}
                        ]
                    }
                ]
            },
            "business.json": {
                "name": "Business Server",
                "description": "Professional server for team collaboration and project management",
                "roles": [
                    {"name": "Owner", "permissions": ["administrator"]},
                    {"name": "Manager", "permissions": ["manage_channels", "manage_messages", "kick_members"]},
                    {"name": "Team", "permissions": []},
                    {"name": "Intern", "permissions": []}
                ],
                "categories": [
                    {
                        "name": "General",
                        "channels": [
                            {"name": "announcements", "type": "text"},
                            {"name": "general", "type": "text"},
                            {"name": "watercooler", "type": "text"}
                        ]
                    },
                    {
                        "name": "Projects",
                        "channels": [
                            {"name": "project-alpha", "type": "text"},
                            {"name": "project-beta", "type": "text"},
                            {"name": "meetings", "type": "voice"}
                        ]
                    },
                    {
                        "name": "Management",
                        "channels": [
                            {"name": "exec-chat", "type": "text"},
                            {"name": "performance", "type": "text"}
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
            created_resources = {'roles': [], 'categories': [], 'channels': []}
            
            for role_data in self.template_data.get('roles', []):
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
                except Exception as e:
                    logger.error(f"Failed to create role: {e}")
            
            for category_data in self.template_data.get('categories', []):
                try:
                    category = await interaction.guild.create_category(name=category_data['name'])
                    created_resources['categories'].append(category.id)
                    logger.info(f"Created category: {category.name}")
                    
                    for channel_data in category_data.get('channels', []):
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
                        except Exception as e:
                            logger.error(f"Failed to create channel: {e}")
                
                except Exception as e:
                    logger.error(f"Failed to create category: {e}")
            
            self.bot.last_setup[interaction.guild.id] = {
                'template_id': self.template_id,
                'resources': created_resources,
                'timestamp': datetime.now()
            }
            
            embed = discord.Embed(
                title="✅ Template Created Successfully!",
                description=f"Server structure from **{self.template_data.get('name')}** has been created.",
                color=discord.Color.green()
            )
            embed.add_field(name="Roles Created", value=len(created_resources['roles']), inline=True)
            embed.add_field(name="Categories Created", value=len(created_resources['categories']), inline=True)
            embed.add_field(name="Channels Created", value=len(created_resources['channels']), inline=True)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
        
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
        embed.add_field(name="Developers", value="Community", inline=True)
        embed.add_field(
            name="📋 Available Commands",
            value=(
                "`/setup` - Browse and install server templates\n"
                "`/undo` - Undo the last template installation\n"
                "`/delete` - Remove all channels and roles\n"
                "`/info` - View this information"
            ),
            inline=False
        )
        embed.add_field(
            name="ℹ️ How to Use",
            value=(
                "1. Run `/setup` to browse templates\n"
                "2. Select a template from the dropdown menu\n"
                "3. Preview the template structure\n"
                "4. Click 'Create Template' to build your server\n"
                "5. Use `/undo` to revert any installation"
            ),
            inline=False
        )
        
        embed.set_footer(text="Built with discord.py 2.x")
        
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
