"""
Quick Start Guide for Discord Bot Framework
"""

# SETUP INSTRUCTIONS

## Step 1: Install Python
Download Python 3.8+ from https://www.python.org/downloads/

## Step 2: Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

## Step 3: Install Dependencies
```bash
pip install -r requirements-base.txt
```

## Step 4: Get Discord Bot Token
1. Go to https://discord.com/developers/applications
2. Click "New Application"
3. Go to Bot section → "Add Bot"
4. Copy the token

## Step 5: Configure Bot
1. Copy `.env.example` to `.env`
2. Paste your token: `DISCORD_TOKEN=your_token_here`

## Step 6: Invite Bot to Server
1. Go to OAuth2 → URL Generator
2. Select scopes: `bot`
3. Select permissions:
   - Send Messages
   - Embed Links
   - Manage Messages
   - Manage Roles
   - Manage Members
   - Moderate Members
4. Copy and open generated URL

## Step 7: Run Bot
```bash
python run.py
```

## Available Commands

### Mass Messaging (Admin only)
- `!broadcast channels <message>` - Send to all text channels
- `!broadcast users <message>` - Send DMs to all members
- `!broadcast roles <role> <message>` - DM users with specific role
- `!broadcast schedule <seconds> <message>` - Schedule for later
- `!broadcast list` - View scheduled broadcasts

### Moderation (Moderator+)
- `!warn <user> [reason]` - Warn a user
- `!mute <user> <seconds> [reason]` - Timeout user
- `!unmute <user>` - Remove timeout
- `!kick <user> [reason]` - Remove from server
- `!ban <user> [reason]` - Ban from server
- `!purge <amount>` - Delete last N messages
- `!purgeuser <user> <amount>` - Delete user's messages

### Role Management (Admin+)
- `!role give <user> <role>` - Assign role
- `!role remove <user> <role>` - Remove role
- `!role create <name> [color]` - Create role
- `!role delete <role>` - Delete role
- `!role list` - Show all roles

### Analytics (Anyone)
- `!analytics server` - Server stats
- `!analytics users [limit]` - Top active users
- `!analytics log <channel>` - Set audit log channel

### Welcome System (Admin+)
- `!welcome set <channel>` - Set welcome channel
- `!welcome message <text>` - Set custom message
- `!welcome remove` - Disable welcome

## File Structure

bot.py - Main bot class
run.py - Entry point
config.py - Settings
cogs/ - Feature modules
  ├── mass_messaging.py - Broadcasts
  ├── moderation.py - Moderation tools
  ├── welcome_roles.py - Welcome & roles
  └── analytics.py - Statistics & logs
utils/ - Helper functions
database/ - Data models

## Common Issues

**Bot won't start**
- Check DISCORD_TOKEN in .env
- Make sure token is valid
- Try `pip install --upgrade discord.py`

**Commands not working**
- Verify bot has permissions
- Check bot role position (higher than target)
- Ensure user has required permissions

**Permission denied**
- Add bot to server with proper OAuth2 scopes
- Check role hierarchy

## Next Steps

1. Customize welcome messages
2. Set up logging channel
3. Configure role names for your server
4. Test broadcast in private server first
5. Monitor logs for errors

## Security Tips

- Never share your bot token
- Use .env file (don't commit it)
- Rotate token if exposed
- Limit bot to minimum required permissions
- Review audit logs regularly

## Support

For issues, check:
1. Discord.py documentation: https://discordpy.readthedocs.io/
2. Discord API reference: https://discord.com/developers/docs
3. Check logs for error messages
