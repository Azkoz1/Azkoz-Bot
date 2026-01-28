"""
Welcome & Roles Cog - Welcome system and role management
"""

import discord
from discord.ext import commands
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class WelcomeRoles(commands.Cog):
    """Welcome messages and role management"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.welcome_config = {}  # guild_id -> welcome_channel_id
    
    @commands.group(name='welcome', invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def welcome(self, ctx):
        """Welcome system commands"""
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="👋 Welcome Commands",
                description="Manage welcome messages",
                color=discord.Color.green()
            )
            embed.add_field(name="!welcome set <channel>", value="Set welcome channel", inline=False)
            embed.add_field(name="!welcome message <message>", value="Set welcome message", inline=False)
            embed.add_field(name="!welcome remove", value="Remove welcome system", inline=False)
            await ctx.send(embed=embed)
    
    @welcome.command(name='set')
    @commands.has_permissions(administrator=True)
    async def set_welcome(self, ctx, channel: discord.TextChannel):
        """Set the welcome channel"""
        self.welcome_config[ctx.guild.id] = channel.id
        
        embed = discord.Embed(
            title="✓ Welcome Channel Set",
            description=f"Welcome messages will be sent to {channel.mention}",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Welcome new members"""
        guild_id = member.guild.id
        
        if guild_id not in self.welcome_config:
            return
        
        channel_id = self.welcome_config[guild_id]
        channel = member.guild.get_channel(channel_id)
        
        if not channel:
            return
        
        embed = discord.Embed(
            title="👋 Welcome to the Server!",
            description=f"Welcome {member.mention}!",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Member Count", value=member.guild.member_count, inline=True)
        embed.add_field(name="Account Created", value=member.created_at.strftime('%Y-%m-%d'), inline=True)
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.set_footer(text=f"ID: {member.id}")
        
        try:
            await channel.send(f"Welcome {member.mention}! 👋", embed=embed)
        except discord.Forbidden:
            logger.warning(f"Cannot send welcome message in {channel.name}")
    
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        """Log member leaving"""
        guild_id = member.guild.id
        
        if guild_id not in self.welcome_config:
            return
        
        channel_id = self.welcome_config[guild_id]
        channel = member.guild.get_channel(channel_id)
        
        if not channel:
            return
        
        embed = discord.Embed(
            title="👋 Member Left",
            description=f"{member} has left the server.",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        
        try:
            await channel.send(embed=embed)
        except discord.Forbidden:
            logger.warning(f"Cannot send goodbye message in {channel.name}")
    
    @commands.group(name='role', invoke_without_command=True)
    @commands.has_permissions(manage_roles=True)
    async def role_group(self, ctx):
        """Role management commands"""
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="🏷️ Role Commands",
                color=discord.Color.purple()
            )
            embed.add_field(name="!role give <member> <role>", value="Give a role to a member", inline=False)
            embed.add_field(name="!role remove <member> <role>", value="Remove a role from a member", inline=False)
            embed.add_field(name="!role create <name> [color]", value="Create a new role", inline=False)
            embed.add_field(name="!role delete <role>", value="Delete a role", inline=False)
            embed.add_field(name="!role list", value="List all roles", inline=False)
            await ctx.send(embed=embed)
    
    @role_group.command(name='give')
    @commands.has_permissions(manage_roles=True)
    async def give_role(self, ctx, member: discord.Member, role: discord.Role):
        """Give a role to a member"""
        if role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.send("❌ Cannot give this role.")
            return
        
        try:
            await member.add_roles(role)
            await ctx.send(f"✓ Gave {role.mention} to {member.mention}")
        except discord.Forbidden:
            await ctx.send("❌ Cannot give this role.")
    
    @role_group.command(name='remove')
    @commands.has_permissions(manage_roles=True)
    async def remove_role(self, ctx, member: discord.Member, role: discord.Role):
        """Remove a role from a member"""
        if role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.send("❌ Cannot remove this role.")
            return
        
        try:
            await member.remove_roles(role)
            await ctx.send(f"✓ Removed {role.mention} from {member.mention}")
        except discord.Forbidden:
            await ctx.send("❌ Cannot remove this role.")
    
    @role_group.command(name='create')
    @commands.has_permissions(manage_roles=True)
    async def create_role(self, ctx, name: str, color: str = "000000"):
        """Create a new role"""
        try:
            # Convert hex color to discord.Color
            color_int = int(color.replace('#', ''), 16)
            role_color = discord.Color(color_int)
        except ValueError:
            role_color = discord.Color.default()
        
        try:
            role = await ctx.guild.create_role(name=name, color=role_color)
            await ctx.send(f"✓ Created role {role.mention}")
        except discord.Forbidden:
            await ctx.send("❌ Cannot create roles.")
    
    @role_group.command(name='delete')
    @commands.has_permissions(manage_roles=True)
    async def delete_role(self, ctx, role: discord.Role):
        """Delete a role"""
        if role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
            await ctx.send("❌ Cannot delete this role.")
            return
        
        try:
            await role.delete()
            await ctx.send(f"✓ Deleted role {role.name}")
        except discord.Forbidden:
            await ctx.send("❌ Cannot delete this role.")
    
    @role_group.command(name='list')
    async def list_roles(self, ctx):
        """List all roles in the server"""
        roles = [role.mention for role in ctx.guild.roles if role != ctx.guild.default_role]
        
        embed = discord.Embed(
            title=f"🏷️ Roles ({len(roles)})",
            description="\n".join(roles[:20]) if roles else "No roles",
            color=discord.Color.purple()
        )
        
        if len(roles) > 20:
            embed.set_footer(text=f"... and {len(roles) - 20} more roles")
        
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    """Load the cog"""
    await bot.add_cog(WelcomeRoles(bot))
