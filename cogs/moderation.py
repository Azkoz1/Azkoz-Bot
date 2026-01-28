"""
Moderation Cog - Automatic community moderation and user management
"""

import discord
from discord.ext import commands
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class Moderation(commands.Cog):
    """Server moderation and user management"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.user_warnings: Dict[int, Dict[int, int]] = {}  # guild_id -> user_id -> warning_count
        self.muted_users: Dict[int, set] = {}  # guild_id -> set of muted user_ids
    
    @commands.command(name='warn')
    @commands.has_permissions(moderate_members=True)
    async def warn_user(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        """Warn a user"""
        if member.top_role >= ctx.author.top_role:
            await ctx.send("❌ Cannot warn this user.")
            return
        
        guild_id = ctx.guild.id
        if guild_id not in self.user_warnings:
            self.user_warnings[guild_id] = {}
        
        user_id = member.id
        warnings = self.user_warnings[guild_id].get(user_id, 0) + 1
        self.user_warnings[guild_id][user_id] = warnings
        
        embed = discord.Embed(
            title="⚠️ User Warned",
            color=discord.Color.yellow()
        )
        embed.add_field(name="User", value=member.mention, inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Warnings", value=f"{warnings}/3", inline=True)
        embed.set_footer(text=f"Warned by {ctx.author}")
        
        try:
            await member.send(f"You've been warned in {ctx.guild.name} for: {reason}")
        except discord.Forbidden:
            pass
        
        await ctx.send(embed=embed)
        
        # Auto-kick on 3 warnings
        if warnings >= 3:
            try:
                await member.kick(reason=f"Automatic kick after {warnings} warnings")
                await ctx.send(f"🚫 {member} has been kicked due to excessive warnings.")
                self.user_warnings[guild_id][user_id] = 0
            except discord.Forbidden:
                await ctx.send("❌ Cannot kick this user.")
    
    @commands.command(name='warnings')
    async def get_warnings(self, ctx, member: discord.Member):
        """Check user's warning count"""
        guild_id = ctx.guild.id
        user_id = member.id
        
        if guild_id not in self.user_warnings:
            warnings = 0
        else:
            warnings = self.user_warnings[guild_id].get(user_id, 0)
        
        embed = discord.Embed(
            title="⚠️ User Warnings",
            color=discord.Color.yellow()
        )
        embed.add_field(name="User", value=member.mention, inline=True)
        embed.add_field(name="Warnings", value=f"{warnings}/3", inline=True)
        
        await ctx.send(embed=embed)
    
    @commands.command(name='clearwarnings')
    @commands.has_permissions(administrator=True)
    async def clear_warnings(self, ctx, member: discord.Member):
        """Clear user's warnings"""
        guild_id = ctx.guild.id
        if guild_id in self.user_warnings:
            self.user_warnings[guild_id][member.id] = 0
            await ctx.send(f"✓ Cleared warnings for {member.mention}")
        else:
            await ctx.send(f"❌ {member.mention} has no warnings.")
    
    @commands.command(name='mute')
    @commands.has_permissions(moderate_members=True)
    async def mute_user(self, ctx, member: discord.Member, duration_seconds: int, *, reason: str = "No reason"):
        """Mute a user for a specified duration"""
        if member.top_role >= ctx.author.top_role:
            await ctx.send("❌ Cannot mute this user.")
            return
        
        try:
            await member.timeout(timedelta(seconds=duration_seconds), reason=reason)
            
            embed = discord.Embed(
                title="🔇 User Muted",
                color=discord.Color.orange()
            )
            embed.add_field(name="User", value=member.mention, inline=True)
            embed.add_field(name="Duration", value=f"{duration_seconds} seconds", inline=True)
            embed.add_field(name="Reason", value=reason, inline=False)
            
            await ctx.send(embed=embed)
            
            try:
                await member.send(f"You've been muted in {ctx.guild.name} for {duration_seconds}s. Reason: {reason}")
            except discord.Forbidden:
                pass
        
        except discord.Forbidden:
            await ctx.send("❌ Cannot mute this user.")
    
    @commands.command(name='unmute')
    @commands.has_permissions(moderate_members=True)
    async def unmute_user(self, ctx, member: discord.Member):
        """Unmute a user"""
        try:
            await member.timeout(None)
            await ctx.send(f"✓ {member.mention} has been unmuted.")
        except discord.Forbidden:
            await ctx.send("❌ Cannot unmute this user.")
    
    @commands.command(name='kick')
    @commands.has_permissions(kick_members=True)
    async def kick_user(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        """Kick a user from the server"""
        if member.top_role >= ctx.author.top_role:
            await ctx.send("❌ Cannot kick this user.")
            return
        
        try:
            await member.kick(reason=reason)
            
            embed = discord.Embed(
                title="🚫 User Kicked",
                color=discord.Color.red()
            )
            embed.add_field(name="User", value=str(member), inline=True)
            embed.add_field(name="Reason", value=reason, inline=False)
            
            await ctx.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("❌ Cannot kick this user.")
    
    @commands.command(name='ban')
    @commands.has_permissions(ban_members=True)
    async def ban_user(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        """Ban a user from the server"""
        if member.top_role >= ctx.author.top_role:
            await ctx.send("❌ Cannot ban this user.")
            return
        
        try:
            await member.ban(reason=reason, delete_message_seconds=0)
            
            embed = discord.Embed(
                title="🔨 User Banned",
                color=discord.Color.red()
            )
            embed.add_field(name="User", value=str(member), inline=True)
            embed.add_field(name="Reason", value=reason, inline=False)
            
            await ctx.send(embed=embed)
        except discord.Forbidden:
            await ctx.send("❌ Cannot ban this user.")
    
    @commands.command(name='unban')
    @commands.has_permissions(ban_members=True)
    async def unban_user(self, ctx, user: discord.User):
        """Unban a user"""
        try:
            await ctx.guild.unban(user)
            await ctx.send(f"✓ {user} has been unbanned.")
        except discord.NotFound:
            await ctx.send("❌ User not found in ban list.")
        except discord.Forbidden:
            await ctx.send("❌ Cannot unban users.")
    
    @commands.command(name='purge')
    @commands.has_permissions(manage_messages=True)
    async def purge_messages(self, ctx, amount: int = 10):
        """Delete a number of messages from the current channel"""
        if amount < 1 or amount > 100:
            await ctx.send("❌ Please specify a number between 1 and 100.")
            return
        
        deleted = await ctx.channel.purge(limit=amount)
        await ctx.send(f"✓ Deleted {len(deleted)} messages.", delete_after=5)
    
    @commands.command(name='purgeuser')
    @commands.has_permissions(manage_messages=True)
    async def purge_user_messages(self, ctx, member: discord.Member, amount: int = 10):
        """Delete messages from a specific user"""
        if amount < 1 or amount > 100:
            await ctx.send("❌ Please specify a number between 1 and 100.")
            return
        
        deleted = await ctx.channel.purge(
            limit=100,
            check=lambda m: m.author == member,
            before=None if amount == 100 else ctx.message
        )
        await ctx.send(f"✓ Deleted {len(deleted)} messages from {member.mention}.", delete_after=5)
    
    @commands.command(name='slowmode')
    @commands.has_permissions(manage_channels=True)
    async def set_slowmode(self, ctx, seconds: int = 0):
        """Set slowmode for the current channel"""
        if seconds < 0 or seconds > 21600:
            await ctx.send("❌ Slowmode must be between 0 and 21600 seconds.")
            return
        
        await ctx.channel.edit(slowmode_delay=seconds)
        
        if seconds == 0:
            await ctx.send("✓ Slowmode disabled.")
        else:
            await ctx.send(f"✓ Slowmode set to {seconds} seconds.")
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Reset warnings when user joins"""
        guild_id = member.guild.id
        if guild_id in self.user_warnings:
            self.user_warnings[guild_id][member.id] = 0

async def setup(bot: commands.Bot):
    """Load the cog"""
    await bot.add_cog(Moderation(bot))
