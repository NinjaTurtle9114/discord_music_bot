import discord
from discord.ext import commands
from youtubesearchpython import VideosSearch
from yt_dlp import YoutubeDL
import asyncio


class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.is_playing = False
        self.is_paused = False
        self.music_queue = []
        self.YDL_OPTIONS = {"format": "bestaudio/best"}
        self.FFMPEG_OPTIONS = {"options": "-vn"}
        self.vc = None
        self.ytdl = YoutubeDL(self.YDL_OPTIONS)

    def search_yt(self, item):
        if item.startswith("https://"):
            title = self.ytdl.extract_info(item, download=False)["title"]
            return {"source": item, "title": title}
        search = VideosSearch(item, limit=1)
        return {"source": search.result()["result"][0]["links"],
                "title": search.result()["result"][0]["title"]}

    async def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            m_url = self.music_queue[0][0]["source"]

            self.music_queue.pop(0)
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(m_url,
                                                                                   download=False))
            song = data["url"]
            self.vc.play(discord.FFmpegPCMAudio(song, executable="ffmpeg.exe",
                                                **self.FFMPEG_OPTIONS),
                         after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(),
                                                                          self.bot.loop))
        else:
            self.is_playing = False

    async def play_song(self, ctx):
        if len(self.music_queue) > 0:
            self.is_playing = True
            m_url = self.music_queue[0][0]["source"]

            if self.vc is None or not self.vc.is_connected():
                self.vc = await self.music_queue[0][1].connect()

                if self.vc is None:
                    await ctx.send("Could not connect to voice channel")

            else:
                await self.vc.move_to(self.music_queue[0][1])

            self.music_queue.pop(0)
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: self.ytdl.extract_info(m_url,
                                                                                   download=False))
            song = data["url"]
            self.vc.play(discord.FFmpegPCMAudio(song, executable="ffmpeg.exe",
                                                **self.FFMPEG_OPTIONS),
                         after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(),
                                                                          self.bot.loop))

        else:
            self.is_playing = False

    @commands.command(name="play", aliases=["p", "playing"], help="Play selected song from youtube")
    async def play(self, ctx, *args):
        query = " ".join(args)
        try:
            voice_channel = ctx.author.voice.channel
        except:
            await ctx.send("```Not connected to voice channel```")
            return

        if self.is_paused:
            self.vc.resume()
        else:
            song = self.search_yt(query)
            if type(song) is type(True):
                await ctx.send("```Could not play song. Incorrect format```")
            else:
                if self.is_playing:
                    await ctx.send(f"**#{len(self.music_queue) + 2} - '{song['title']}'** added to"
                                   f" the queue")
                else:
                    await ctx.send(f"**{song['title']}'** added to queue")
                self.music_queue.append([song, voice_channel])

                if self.is_playing is False:
                    await self.play_song(ctx)

    # currently not working
    @commands.command(name="pause", aliases=["f", "fuckoff"],
                      help="Pause selected song from youtube")
    async def pause(self, ctx, *args):
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            self.vc.paused()
        elif self.is_paused:
            self.is_paused = True
            self.is_playing = False
            self.vc.resume()

    # currently not working
    @commands.command(name="resume", aliases=["r"], help="Resumes playing current song")
    async def resume(self, ctx, *args):
        if self.is_paused:
            self.is_playing = True
            self.is_paused = False
            self.vc.resume()

    @commands.command(name="skip", aliases=["s"], help="Skip selected song from youtube")
    async def skip(self, ctx):
        if self.vc is not None and self.vc:
            self.vc.stop()
            await self.play_song(ctx)

    @commands.command(name="queue", aliases=["q"], help="Display queued songs")
    async def queue(self, ctx):
        retval = ""

        for i in range(len(self.music_queue)):
            retval += f"#{i + 1} -" + self.music_queue[i][0]["title"] + "\n"

        if retval != "":
            await ctx.send(f"```queue:\n{retval}```")
        else:
            await ctx.send("```No songs in queue```")

    @commands.command(name="clear", aliases=["c"],
                      help="Stops playing songs and clears queue")
    async def clear(self, ctx):
        if self.vc is not None and self.is_playing:
            self.vc.stop()
            self.music_queue.clear()
        await ctx.send("```Song queue cleared```")

    @commands.command(name="disconnect", aliases=["d"], help="Disconnects bot")
    async def disconnect(self, ctx):
        self.is_playing = False
        self.is_paused = False
        await self.vc.disconnect()
