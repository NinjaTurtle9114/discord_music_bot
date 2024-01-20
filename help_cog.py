import discord
from discord.ext import commands


def handle_response(message):
    p_message = message.lower()

    if p_message == "-test":
        return "Epic test"


class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.help_message = f"""
        ```
        Commands:
        {self.bot.command_prefix}help - Displays all commands
        {self.bot.command_prefix}p / play <message> - finds the song on youtube and plays it in a voice channel
        {self.bot.command_prefix}q / queue - displays current song queue
        {self.bot.command_prefix}skip - skips the current song
        {self.bot.command_prefix}clear - stops the current song and clears the queue
        {self.bot.command_prefix}d / disconnect - Disconnects the bot from the voice channel
        {self.bot.command_prefix}f / fuckoff - pauses the current song or resumes if song is paused
        {self.bot.command_prefix}resume - resumes the current song
        ```
        """

        self.text_channel_text = []

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(activity=discord.Game(f"type {self.bot.command_prefix}help"))

    async def send_to_all(self, message):
        for text_channel in self.text_channel_text:
            await text_channel.send(message)

    @commands.command(name="help", help="Displays all commands")
    async def help_command(self, ctx):
        await ctx.send(self.help_message)
