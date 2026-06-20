# All In One Setup - Discord Bot

A production-ready Discord bot for automatic server setup from pre-made templates.

## Features

✅ **Template System** - Browse and install pre-made server structures
✅ **Automatic Creation** - Creates categories, channels, roles, and permissions
✅ **Undo System** - Revert the last setup operation
✅ **Dangerous Delete** - Clean up entire server structures (with confirmation)
✅ **Modern UI** - Discord embeds, buttons, and select menus
✅ **Permission Management** - Automatic role and channel permission setup
✅ **Logging** - Full operation logging to bot.log
✅ **Error Handling** - Graceful error handling and recovery

## Built-in Templates

- 🎮 **Gaming Server** - Complete gaming community setup
- ⛏️ **Minecraft Server** - Minecraft-focused organization
- 🌍 **Community Server** - Inclusive community structure
- 📺 **Content Creator Server** - For streamers and creators

## Requirements

- Python 3.12+
- discord.py 2.4.0+
- python-dotenv

## Installation

### 1. Clone Repository

```bash
git clone <your-repo-url>
cd all-in-one-setup
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Create .env File

```bash
cp .env.example .env
```

Edit `.env` and add your Discord bot token:

```
DISCORD_TOKEN=your_bot_token_here
```

### 4. Run the Bot

```bash
python bot.py
```

## Discord Bot Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to "Bot" section and create a bot
4. Copy the token and paste it in `.env`
5. Enable required intents:
   - Message Content Intent
   - Server Members Intent
   - Guilds
6. Go to OAuth2 > URL Generator
7. Select scopes: `bot`
8. Select permissions:
   - Administrator (recommended for full functionality)
9. Copy the generated URL and invite the bot to your server

## Commands

### /setup
Browse available templates and create server structure.

**Usage:** `/setup`

**Steps:**
1. Select a template from the dropdown
2. Review the template information
3. Click "Create Template" to proceed
4. Bot will create all categories, channels, and roles

### /undo
Undo the last template installation.

**Usage:** `/undo`

**Notes:**
- Only removes items created in the last setup
- Requires confirmation before proceeding
- Preserves existing channels and roles

### /delete
Dangerous cleanup command - removes all channels and roles.

**Usage:** `/delete`

**Preserved:**
- @everyone role
- Discord-managed roles
- Roles above the bot
- The channel where command was executed

**Notes:**
- Requires confirmation
- **Cannot be undone!**
- Requires administrator permissions

### /info
View bot information and available templates.

**Usage:** `/info`

## Custom Templates

Create your own templates in the `templates/` directory as JSON files.

### Template Format

```json
{
  "name": "Custom Server",
  "description": "Your server description here",
  "roles": [
    {
      "name": "Owner",
      "color": 16711680,
      "permissions": ["administrator"]
    },
    {
      "name": "Member",
      "color": 3447003,
      "permissions": []
    }
  ],
  "categories": [
    {
      "name": "📋 General",
      "channels": [
        {
          "name": "general",
          "type": "text",
          "read_only_staff": false
        },
        {
          "name": "voice",
          "type": "voice",
          "read_only_staff": false
        }
      ]
    }
  ]
}
```

### Template Options

- **name** - Template display name
- **description** - Short description of the template
- **roles** - Array of role definitions
  - **name** - Role name
  - **color** - Discord color code (decimal)
  - **permissions** - Array of permission names
- **categories** - Array of category definitions
  - **name** - Category name with optional emoji
  - **channels** - Array of channels in the category
    - **name** - Channel name
    - **type** - `text`, `voice`, or `forum`
    - **read_only_staff** - If true, only staff can message

## Deployment to Railway

1. Push code to GitHub repository
2. Go to [Railway](https://railway.app)
3. Create new project
4. Connect GitHub repository
5. Set environment variable `DISCORD_TOKEN` in Railway settings
6. Deploy

Railway will automatically detect `requirements.txt` and install dependencies.

## File Structure

```
.
├── bot.py                    # Main bot code
├── requirements.txt          # Python dependencies
├── .env.example             # Environment file template
├── README.md                # This file
├── templates/               # Template JSON files (auto-created)
│   ├── gaming.json
│   ├── minecraft.json
│   ├── community.json
│   └── creator.json
├── data/                    # Data directory (auto-created)
└── bot.log                  # Log file (auto-created)
```

## Logging

All operations are logged to `bot.log`:
- Role creation
- Channel creation
- Setup operations
- Undo operations
- Errors and exceptions

## Error Handling

The bot handles:
- Missing permissions gracefully
- Discord API rate limits
- Duplicate channel/role names
- Missing roles or channels
- User permission validation

## Troubleshooting

### Bot doesn't appear online
- Check `DISCORD_TOKEN` in `.env`
- Verify bot is invited to server
- Check Discord Developer Portal application status

### Commands don't show up
- Bot needs `/` slash command permissions
- May take up to 1 hour to sync globally
- Try using in a specific guild first

### Permission denied errors
- Ensure bot has Administrator role
- Verify bot role is higher than target roles
- Check server role hierarchy

### Templates don't load
- Check `templates/` directory exists
- Verify JSON syntax in template files
- Check bot.log for specific errors

## Support

For issues, check:
1. `bot.log` for error messages
2. Discord Developer Portal bot settings
3. Server role permissions and hierarchy

## License

Created for Discord server automation.
