# Base Code Citation: https://www.youtube.com/watch?v=jHZlvRr9KxM
import discord
from discord.ext import commands
import youtube_dl
import urllib.request
import re


queue = []
current_song = None;

class music(commands.Cog):
  def __init__(self, client):
    self.client = client

  @commands.command()
  async def join(self, ctx):
    # If command is being called by user not in a voice channel.
    if ctx.author.voice is None:
      await ctx.send("You cannot issue voice commands outside of a voice channel.")
    voice_channel = ctx.author.voice.channel
    # If bot is not already in a channel
    if ctx.voice_client is None:
      await voice_channel.connect()
    # Otherwise, move to voice channel command is called
    else:
      await ctx.voice_client.move_to(voice_channel)

  @commands.command()
  async def disconnect(self, ctx):
    #await ctx.voice_client.stop()
    #await ctx.voice_client.disconnect()
    await ctx.send("> Bye!")
    await ctx.voice_client.disconnect()

  @commands.command()
  async def play(self, ctx, *search_keyword):
    global current_song
    search_keyword_stitched = "+".join(search_keyword)

    voice_channel = ctx.author.voice.channel
    if ctx.voice_client is None:
      await voice_channel.connect()


    print("Checking if audio already playing")
    print()
    # Stop any song currently being played when one is requested
    ctx.voice_client.stop()
    # Standard preferences
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    # Play in best audio format
    YDL_OPTIONS = {'format':'bestaudio'}
    vc = ctx.voice_client

    with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
      info = None;
      if "https://www.youtube.com/watch?v=" not in search_keyword_stitched:
        ytSearch = searchYT(search_keyword_stitched)
        current_song = ytSearch
        info = ydl.extract_info(ytSearch, download = False)
        await ctx.send("> Playing the following YouTube video: " + ytSearch)
      else:
        info = ydl.extract_info(search_keyword_stitched, download = False)
        current_song = search_keyword_stitched
        await ctx.send("> Playing the following YouTube video: " + search_keyword_stitched)
      url2 = info['formats'][0]['url']
      source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
      if not ctx.voice_client.is_playing():
        vc.play(source)
      else: 
        queue.append(source)

  @commands.command()
  async def seek(self, ctx, timestamp): 
    if current_song is None:
      await ctx.send("> There is no music playing!")
    else:
      ctx.voice_client.stop()

      FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn -ss ' + timestamp}
      YDL_OPTIONS = {'format':'bestaudio'}
      with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
        vc = ctx.voice_client
        info = ydl.extract_info(current_song, download = False)
        url2 = info['formats'][0]['url']
        source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
        vc.play(source)

      

  @commands.command()
  async def pause(self, ctx):
    #await ctx.voice_client.pause()
    #await ctx.send("Music paused.")
    await ctx.send("> Music paused!")
    await ctx.voice_client.pause()

  @commands.command()
  async def resume(self, ctx):
    #await ctx.voice_client.resume()
    #await ctx.send("Music resumed.")
    await ctx.send("> Music resumed!")
    await ctx.voice_client.resume()
    

  @commands.command()
  async def skip(self, ctx):
    #await ctx.voice_client.stop()
    #await ctx.send("Music skipped.")
    await ctx.send("> Song skipped!")
    ctx.voice_client.stop()
    

def setup(client):
  client.add_cog(music(client))

# Citation: https://www.youtube.com/watch?v=XLDvri9VS50
def searchYT(keyword):
  html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + keyword)
  video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
  return("https://www.youtube.com/watch?v=" + video_ids[0])
