# Base Code Citation: https://www.youtube.com/watch?v=jHZlvRr9KxM
import discord
from discord.ext import commands
import youtube_dl
import urllib.request
import re
import asyncio


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
    
    voice_channel = ctx.author.voice.channel
    if ctx.voice_client is None:
      await voice_channel.connect()
    await ctx.send("> Bye!")
    await ctx.voice_client.disconnect()

  @commands.command()
  async def play(self, ctx, *search_keyword):
    global current_song, queue
    search_keyword_stitched = "+".join(search_keyword)

    voice_channel = ctx.author.voice.channel
    if ctx.voice_client is None:
      await voice_channel.connect()

    info = None;
    if "https://www.youtube.com/watch?v=" not in search_keyword_stitched:
      search_keyword_stitched = searchYT(search_keyword_stitched)
    
    YDL_OPTIONS = {'format':'bestaudio'}
    with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
      info = None;
      if "https://www.youtube.com/watch?v=" not in search_keyword_stitched:
        search_keyword_stitched = searchYT(search_keyword_stitched)
      info = ydl.extract_info(search_keyword_stitched, download = False)
      current_song = search_keyword_stitched
      # current_song is the URL
      if not ctx.voice_client.is_playing():
        try:
          vc = ctx.voice_client
          url2 = info['formats'][0]['url']
          vc.play(discord.FFmpegPCMAudio(source=url2), after=lambda e: play_next(ctx))
        except:
          queue.append(search_keyword_stitched)
          print("Audio not playing, but in process")
          return
      else:
        queue.append(search_keyword_stitched)
    
    


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
    global queue;
    #await ctx.voice_client.stop()
    #await ctx.send("Music skipped.")
    await ctx.send("> Song skipped!")
    #ctx.voice_client.stop()
    ctx.voice_client.stop()

      
    

def setup(client):
  client.add_cog(music(client))

# Citation: https://www.youtube.com/watch?v=XLDvri9VS50
def searchYT(keyword):
  html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + keyword)
  video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
  return("https://www.youtube.com/watch?v=" + video_ids[0])

def play_next(ctx):
    global current_song, queue
    print("IN NEXT")
    if len(queue) > 0:
      YDL_OPTIONS = {'format':'bestaudio'}
      search_keyword_stitched = queue.pop()
      current_song = search_keyword_stitched
      
      YDL_OPTIONS = {'format':'bestaudio'}
      with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(search_keyword_stitched, download = False)
        vc = ctx.voice_client
        url2 = info['formats'][0]['url']
        vc.play(discord.FFmpegPCMAudio(source=url2), after=lambda e: play_next(ctx))