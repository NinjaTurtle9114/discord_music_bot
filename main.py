import json
import discord
import asyncio
from discord.ext import commands

from help_cog import HelpCog
from music_cog import MusicCog


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="-", intents=intents, help_command=None)

with open(".env.json", "r") as f:
    TOKEN = json.loads(f.read())["discord_token"]


async def main():
    async with bot:
        await bot.add_cog(HelpCog(bot))
        await bot.add_cog(MusicCog(bot))
        await bot.start(TOKEN)

asyncio.run(main())
