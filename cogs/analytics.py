"""
Analytics & Logging Cog - Server statistics and activity logging
"""

import discord
from discord.ext import commands, tasks
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class Analytics(commands.Cog):
    """Server analytics and activity tracking"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.message_count: Dict[int, int] = {}  # guild_id -> count
        self.user_activity: Dict[int, Dict[int, int]] = {}  # guild_id -> user_id -> message_count
        self.log_channels: Dict[int, int] = {}  # guild_id -> log_channel_id
    
    @commands.group(name='analytics', invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def analytics(self, ctx):
        """Analytics and logging commands"""
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="📊 Analytics Commands",
                color=discord.Color.blue()
            )
            embed.add_field(name="!analytics server", value="Get server statistics", inline=False)
            embed.add_field(name="!analytics users", value="Get top active users", inline=False)
            embed.add_field(name="!analytics log <channel>", value="Set logging channel", inline=False)
            await ctx.send(embed=embed)
    
    @analytics.command(name='server')
    async def server_stats(self, ctx):
        """Get server statistics"""
        guild = ctx.guild
        
        embed = discord.Embed(
            title=f"📊 {guild.name} Statistics",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        # Member statistics
        total_members = guild.member_count
        bots = sum(1 for m in guild.members if m.bot)
        humans = total_members - bots
        
        embed.add_field(name="👥 Members", value=f"Total: {total_members}\nHumans: {humans}\nBots: {bots}", inline=True)
        
        # Channel statistics
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        embed.add_field(name="💬 Channels", value=f"Text: {text_channels}\nVoice: {voice_channels}", inline=True)
        
        # Role statistics
        embed.add_field(name="🏷️ Roles", value=len(guild.roles), inline=True)
        
        # Server info
        embed.add_field(name="🏢 Created", value=guild.created_at.strftime('%Y-%m-%d'), inline=True)
        embed.add_field(name="📍 Region", value=str(guild.region) if guild.region else "N/A", inline=True)
        embed.add_field(name="🔒 Verification Level", value=str(guild.verification_level).title(), inline=True)
        
        # Top role
        embed.add_field(name="👑 Owner", value=guild.owner.mention if guild.owner else "Unknown", inline=False)
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        await ctx.send(embed=embed)
    
    @analytics.command(name='users')
    async def top_users(self, ctx, limit: int = 10):
        """Get top active users"""
        guild_id = ctx.guild.id
        
        if guild_id not in self.user_activity or not self.user_activity[guild_id]:
            await ctx.send("❌ No activity data available.")
            return
        
        if limit < 1 or limit > 50:
            limit = 10
        
        sorted_users = sorted(
            self.user_activity[guild_id].items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]
        
        embed = discord.Embed(
            title=f"👥 Top {len(sorted_users)} Active Users",
            color=discord.Color.blue()
        )
        
        for idx, (user_id, count) in enumerate(sorted_users, 1):
            user = ctx.guild.get_member(user_id)
            if user:
                embed.add_field(
                    name=f"{idx}. {user}",
                    value=f"{count} messages",
                    inline=False
                )
        
        await ctx.send(embed=embed)
    
    @analytics.command(name='log')
    @commands.has_permissions(administrator=True)
    async def set_log_channel(self, ctx, channel: discord.TextChannel):
        """Set the logging channel"""
        self.log_channels[ctx.guild.id] = channel.id
        
        embed = discord.Embed(
            title="✓ Logging Enabled",
            description=f"Server logs will be sent to {channel.mention}",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Track message activity"""
        if message.author.bot or not message.guild:
            return
        
        guild_id = message.guild.id
        user_id = message.author.id
        
        # Update message count
        if guild_id not in self.message_count:
            self.message_count[guild_id] = 0
        self.message_count[guild_id] += 1
        
        # Update user activity
        if guild_id not in self.user_activity:
            self.user_activity[guild_id] = {}
        
        if user_id not in self.user_activity[guild_id]:
            self.user_activity[guild_id][user_id] = 0
        self.user_activity[guild_id][user_id] += 1
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Log member joins"""
        guild_id = member.guild.id
        
        if guild_id not in self.log_channels:
            return
        
        channel_id = self.log_channels[guild_id]
        channel = member.guild.get_channel(channel_id)
        
        if not channel:
            return
        
        embed = discord.Embed(
            title="✅ Member Joined",
            description=f"{member.mention} ({member})",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Account Age", value=f"{(datetime.utcnow() - member.created_at).days} days", inline=True)
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        
        try:
            await channel.send(embed=embed)
        except discord.Forbidden:
            logger.warning(f"Cannot send logs in {channel.name}")
    
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        """Log member leaves"""
        guild_id = member.guild.id
        
        if guild_id not in self.log_channels:
            return
        
        channel_id = self.log_channels[guild_id]
        channel = member.guild.get_channel(channel_id)
        
        if not channel:
            return
        
        embed = discord.Embed(
            title="❌ Member Left",
            description=f"{member.mention} ({member})",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Time on Server", value=f"{(datetime.utcnow() - member.joined_at).days} days", inline=True)
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        
        try:
            await channel.send(embed=embed)
        except discord.Forbidden:
            logger.warning(f"Cannot send logs in {channel.name}")
    
    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        """Log message edits"""
        if before.author.bot or not before.guild:
            return
        
        guild_id = before.guild.id
        
        if guild_id not in self.log_channels or before.content == after.content:
            return
        
        channel_id = self.log_channels[guild_id]
        channel = before.guild.get_channel(channel_id)
        
        if not channel:
            return
        
        embed = discord.Embed(
            title="✏️ Message Edited",
            color=discord.Color.orange(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Author", value=before.author.mention, inline=True)
        embed.add_field(name="Channel", value=before.channel.mention, inline=True)
        embed.add_field(name="Before", value=before.content[:1024], inline=False)
        embed.add_field(name="After", value=after.content[:1024], inline=False)
        embed.add_field(name="Message Link", value=f"[Jump to message]({after.jump_url})", inline=False)
        
        try:
            await channel.send(embed=embed)
        except discord.Forbidden:
            logger.warning(f"Cannot send logs in {channel.name}")
    
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        """Log message deletions"""
        if message.author.bot or not message.guild:
            return
        
        guild_id = message.guild.id
        
        if guild_id not in self.log_channels:
            return
        
        channel_id = self.log_channels[guild_id]
        channel = message.guild.get_channel(channel_id)
        
        if not channel:
            return
        
        embed = discord.Embed(
            title="🗑️ Message Deleted",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Author", value=message.author.mention, inline=True)
        embed.add_field(name="Channel", value=message.channel.mention, inline=True)
        embed.add_field(name="Content", value=message.content[:1024] if message.content else "[No content]", inline=False)
        
        try:
            await channel.send(embed=embed)
        except discord.Forbidden:
            logger.warning(f"Cannot send logs in {channel.name}")
    
    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        """Log member updates"""
        guild_id = before.guild.id
        
        if guild_id not in self.log_channels:
            return
        
        channel_id = self.log_channels[guild_id]
        channel = before.guild.get_channel(channel_id)
        
        if not channel:
            return
        
        # Check for role changes
        if before.roles != after.roles:
            added_roles = set(after.roles) - set(before.roles)
            removed_roles = set(before.roles) - set(after.roles)
            
            embed = discord.Embed(
                title="🏷️ Member Roles Changed",
                color=discord.Color.yellow(),
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="Member", value=after.mention, inline=True)
            
            if added_roles:
                embed.add_field(name="Added", value=", ".join([r.mention for r in added_roles]), inline=False)
            if removed_roles:
                embed.add_field(name="Removed", value=", ".join([r.mention for r in removed_roles]), inline=False)
            
            try:
                await channel.send(embed=embed)
            except discord.Forbidden:
                pass

async def setup(bot: commands.Bot):
    """Load the cog"""
    await bot.add_cog(Analytics(bot))
