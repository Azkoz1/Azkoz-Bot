"""
Mass Messaging Cog - Broadcast messages across channels and users
"""

import discord
from discord.ext import commands, tasks
import asyncio
import logging
from typing import List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class MassMessaging(commands.Cog):
    """Mass messaging and broadcasting functionality"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.active_broadcasts = {}
        self.message_queue = []
    
    @commands.group(name='broadcast', invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def broadcast(self, ctx):
        """Broadcast commands group"""
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="📢 Broadcast Commands",
                description="Commands for broadcasting messages",
                color=discord.Color.blue()
            )
            embed.add_field(name="!broadcast channels", value="Broadcast to all channels", inline=False)
            embed.add_field(name="!broadcast users", value="Send DMs to users", inline=False)
            embed.add_field(name="!broadcast roles", value="Message users with specific roles", inline=False)
            embed.add_field(name="!broadcast schedule", value="Schedule a broadcast", inline=False)
            embed.add_field(name="!broadcast list", value="List active broadcasts", inline=False)
            await ctx.send(embed=embed)
    
    @broadcast.command(name='channels')
    @commands.has_permissions(administrator=True)
    async def broadcast_channels(self, ctx, *, message: str):
        """Broadcast a message to all text channels"""
        confirm = await self.confirm_action(ctx, f"Broadcast to {len(ctx.guild.text_channels)} channels?")
        if not confirm:
            await ctx.send("❌ Broadcast cancelled.")
            return
        
        embed = discord.Embed(
            title="📢 Broadcast Message",
            description=message,
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=f"Sent by {ctx.author}")
        
        success_count = 0
        failed_count = 0
        
        async with ctx.typing():
            for channel in ctx.guild.text_channels:
                try:
                    if channel.permissions_for(ctx.me).send_messages:
                        await channel.send(embed=embed)
                        success_count += 1
                        await asyncio.sleep(0.5)  # Rate limiting
                except discord.Forbidden:
                    failed_count += 1
                    logger.warning(f"No permission to send in {channel.name}")
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Error sending to {channel.name}: {e}")
        
        result_embed = discord.Embed(
            title="✓ Broadcast Complete",
            color=discord.Color.green()
        )
        result_embed.add_field(name="Successful", value=f"{success_count} channels", inline=True)
        result_embed.add_field(name="Failed", value=f"{failed_count} channels", inline=True)
        await ctx.send(embed=result_embed)
    
    @broadcast.command(name='users')
    @commands.has_permissions(administrator=True)
    async def broadcast_users(self, ctx, *, message: str):
        """Send direct messages to all users in the guild"""
        members = ctx.guild.members
        confirm = await self.confirm_action(ctx, f"Send DMs to {len(members)} members?")
        if not confirm:
            await ctx.send("❌ Broadcast cancelled.")
            return
        
        embed = discord.Embed(
            title=f"Message from {ctx.guild.name}",
            description=message,
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        success_count = 0
        failed_count = 0
        
        async with ctx.typing():
            for member in members:
                if member.bot:
                    continue
                try:
                    await member.send(embed=embed)
                    success_count += 1
                    await asyncio.sleep(0.5)  # Rate limiting
                except discord.Forbidden:
                    failed_count += 1
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Error sending DM to {member}: {e}")
        
        result_embed = discord.Embed(
            title="✓ DM Broadcast Complete",
            color=discord.Color.green()
        )
        result_embed.add_field(name="Successful", value=f"{success_count} users", inline=True)
        result_embed.add_field(name="Failed", value=f"{failed_count} users", inline=True)
        await ctx.send(embed=result_embed)
    
    @broadcast.command(name='roles')
    @commands.has_permissions(administrator=True)
    async def broadcast_roles(self, ctx, role: discord.Role, *, message: str):
        """Broadcast message to users with a specific role"""
        members = role.members
        confirm = await self.confirm_action(ctx, f"Send DMs to {len(members)} members with {role.mention}?")
        if not confirm:
            await ctx.send("❌ Broadcast cancelled.")
            return
        
        embed = discord.Embed(
            title=f"Special Message for {role.name}",
            description=message,
            color=role.color,
            timestamp=datetime.utcnow()
        )
        
        success_count = 0
        failed_count = 0
        
        async with ctx.typing():
            for member in members:
                if member.bot:
                    continue
                try:
                    await member.send(embed=embed)
                    success_count += 1
                    await asyncio.sleep(0.5)
                except discord.Forbidden:
                    failed_count += 1
                except Exception as e:
                    failed_count += 1
        
        result_embed = discord.Embed(
            title="✓ Role Broadcast Complete",
            color=discord.Color.green()
        )
        result_embed.add_field(name="Successful", value=f"{success_count} users", inline=True)
        result_embed.add_field(name="Failed", value=f"{failed_count} users", inline=True)
        await ctx.send(embed=result_embed)
    
    @broadcast.command(name='schedule')
    @commands.has_permissions(administrator=True)
    async def schedule_broadcast(self, ctx, delay_seconds: int, *, message: str):
        """Schedule a broadcast to all channels after a delay"""
        if delay_seconds < 0:
            await ctx.send("❌ Delay must be positive.")
            return
        
        confirm = await self.confirm_action(ctx, f"Schedule broadcast in {delay_seconds} seconds?")
        if not confirm:
            await ctx.send("❌ Scheduling cancelled.")
            return
        
        broadcast_id = f"{ctx.guild.id}_{datetime.utcnow().timestamp()}"
        self.active_broadcasts[broadcast_id] = {
            'guild': ctx.guild,
            'message': message,
            'scheduled_time': datetime.utcnow(),
            'delay': delay_seconds
        }
        
        embed = discord.Embed(
            title="⏰ Broadcast Scheduled",
            description=f"Message will be sent to all channels in {delay_seconds} seconds",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)
        
        # Schedule the broadcast
        await asyncio.sleep(delay_seconds)
        
        if broadcast_id in self.active_broadcasts:
            broadcast_data = self.active_broadcasts[broadcast_id]
            
            embed = discord.Embed(
                title="📢 Scheduled Broadcast",
                description=broadcast_data['message'],
                color=discord.Color.green(),
                timestamp=datetime.utcnow()
            )
            
            for channel in broadcast_data['guild'].text_channels:
                try:
                    if channel.permissions_for(ctx.me).send_messages:
                        await channel.send(embed=embed)
                        await asyncio.sleep(0.5)
                except Exception as e:
                    logger.error(f"Scheduled broadcast error: {e}")
            
            del self.active_broadcasts[broadcast_id]
    
    @broadcast.command(name='list')
    @commands.has_permissions(administrator=True)
    async def list_broadcasts(self, ctx):
        """List all active scheduled broadcasts"""
        if not self.active_broadcasts:
            await ctx.send("❌ No active broadcasts.")
            return
        
        embed = discord.Embed(
            title="📢 Active Broadcasts",
            color=discord.Color.blue()
        )
        
        for broadcast_id, data in self.active_broadcasts.items():
            embed.add_field(
                name=f"ID: {broadcast_id}",
                value=f"Guild: {data['guild'].name}\nScheduled: {data['scheduled_time'].strftime('%Y-%m-%d %H:%M:%S')}",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @broadcast.command(name='cancel')
    @commands.has_permissions(administrator=True)
    async def cancel_broadcast(self, ctx, broadcast_id: str):
        """Cancel a scheduled broadcast"""
        if broadcast_id in self.active_broadcasts:
            del self.active_broadcasts[broadcast_id]
            await ctx.send(f"✓ Broadcast {broadcast_id} cancelled.")
        else:
            await ctx.send(f"❌ Broadcast {broadcast_id} not found.")
    
    async def confirm_action(self, ctx, message: str) -> bool:
        """Ask user to confirm an action"""
        confirm_embed = discord.Embed(
            title="⚠️ Confirmation Required",
            description=message,
            color=discord.Color.yellow()
        )
        confirm_message = await ctx.send(embed=confirm_embed)
        
        await confirm_message.add_reaction('✅')
        await confirm_message.add_reaction('❌')
        
        try:
            reaction, user = await self.bot.wait_for(
                'reaction_add',
                timeout=30.0,
                check=lambda r, u: u == ctx.author and str(r.emoji) in ['✅', '❌']
            )
            return str(reaction.emoji) == '✅'
        except asyncio.TimeoutError:
            await ctx.send("❌ Confirmation timeout.")
            return False

async def setup(bot: commands.Bot):
    """Load the cog"""
    await bot.add_cog(MassMessaging(bot))
