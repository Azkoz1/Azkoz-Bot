"""
Utility functions and helpers
"""

import discord
from typing import Optional
import asyncio

def format_duration(seconds: int) -> str:
    """Convert seconds to human readable format"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        return f"{seconds // 60}m"
    elif seconds < 86400:
        return f"{seconds // 3600}h"
    else:
        return f"{seconds // 86400}d"

def has_role(member: discord.Member, role_name: str) -> bool:
    """Check if member has a role"""
    return any(role.name.lower() == role_name.lower() for role in member.roles)

async def send_embed(ctx, title: str, description: str = "", color = discord.Color.blue(), fields: dict = None):
    """Send a formatted embed message"""
    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )
    
    if fields:
        for field_name, field_value in fields.items():
            embed.add_field(name=field_name, value=field_value, inline=False)
    
    await ctx.send(embed=embed)

async def paginate_results(ctx, items: list, page_size: int = 10):
    """Send results in paginated format"""
    if not items:
        await ctx.send("❌ No results found.")
        return
    
    pages = [items[i:i + page_size] for i in range(0, len(items), page_size)]
    
    for page_num, page in enumerate(pages, 1):
        embed = discord.Embed(
            title=f"Results (Page {page_num}/{len(pages)})",
            color=discord.Color.blue()
        )
        
        for item in page:
            embed.add_field(name=item, value="", inline=False)
        
        await ctx.send(embed=embed)
