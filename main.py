# Base Code Citation: https://www.youtube.com/watch?v=jHZlvRr9KxM
import discord
from discord.ext import commands
import youtube_dl
import urllib.request
import re
import asyncio


queue = []
cog = []
current_song = None
beginning_check = False
bot_is_inactive = False

client = commands.Bot(command_prefix='!',intents=discord.Intents.all())

class music(commands.Cog):
  def __init__(self, client):
    self.client = client
    #self.loop = asyncio.new_event_loop()

  @client.event
  async def on_ready():
    # TODO: Add asyncio or await to check if playing every 15 seconds
    # Add either here OR in join. I'd recommend join.
    print("Bot online")
    

  @commands.command()
  async def join(self, ctx):
    global beginning_check
    # If command is being called by user not in a voice channel.
    if ctx.author.voice is None:
      await ctx.send("> You cannot issue voice commands outside of a voice channel.")
    voice_channel = ctx.author.voice.channel
    # If bot is not already in a channel
    if ctx.voice_client is None:
      await voice_channel.connect()
    # Otherwise, move to voice channel command is called
    else:
      await ctx.voice_client.move_to(voice_channel)
    beginning_check = True
    await check_bot_activity(ctx, 15)

  @commands.command()
  async def disconnect(self, ctx):
    #await ctx.voice_client.stop()
    #await ctx.voice_client.disconnect()
    
    if ctx.author.voice is None:
      await ctx.send("> You cannot issue voice commands outside of a voice channel.")
    elif ctx.voice_client is None:
      await ctx.send("> You can't disconnect me. I'm not in a channel!")
    elif not ctx.author.voice.channel == ctx.voice_client.channel:
      await ctx.send("> You can't disconnect me. You're not in the same channel!")
    else:
      await ctx.send("> Bye!")
      await ctx.voice_client.disconnect()
    

  @commands.command()
  async def play(self, ctx, *search_keyword):
    global bot_is_inactive
    global current_song, queue, beginning_check
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
      try:
        if not ctx.voice_client.is_playing():
          bot_is_inactive = False;
          try:
            vc = ctx.voice_client
            url2 = info['formats'][0]['url']
            vc.play(discord.FFmpegPCMAudio(source=url2), after=lambda e: play_next(ctx))
            await ctx.send("> Playing the following YouTube video: " + search_keyword_stitched)
            print("Done queue")
          except:
            queue.append(search_keyword_stitched)
            print("Audio not playing, but in process")
            return
        else:
          queue.append(search_keyword_stitched)
          return
        if not beginning_check:
          beginning_check = True
          await check_bot_activity(ctx, 15)
      except:
        print("Issues with ctx.voice_client.is_playing()")
        return
    
    
    


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


  @commands.command()
  async def seek(self, ctx, timestamp):

    if current_song is None:
      await ctx.send("> There is no music playing!")
    elif timestamp is None:
      await ctx.send("> Please enter a timestamp!")
    else:
      ctx.voice_client.stop()

      FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn -ss ' + timestamp}
      YDL_OPTIONS = {'format':'bestaudio'}
      with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
        vc = ctx.voice_client
        info = ydl.extract_info(current_song, download = False)
        try:
          vc = ctx.voice_client
          url2 = info['formats'][0]['url']
          source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
          vc.play(source, after=lambda e: play_next(ctx))
        except:
          await ctx.send("> Error seeking, sorry... :confused:")

  

async def check_bot_activity(ctx, seconds):
  global check_for_activity, bot_is_inactive
  await asyncio.sleep(seconds)
  print("Check bot hehe")
  try:
    if (ctx.voice_client.is_playing() or len(queue) > 0):
      bot_is_inactive = False
      await check_bot_activity(ctx, seconds)
    elif not bot_is_inactive:
      print("Bot isn't playing. Leaving soon.")
      bot_is_inactive = True
      await check_bot_activity(ctx, seconds)
    else:
      print("Bot leaving")
      await ctx.send("> I'm inactive. Cya!")
      await ctx.voice_client.disconnect()
  except:
    print("Issues with ctx.voice_client.is_playing()")
    return
  
    

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
      search_keyword_stitched = queue.pop(0)
      current_song = search_keyword_stitched
      
      YDL_OPTIONS = {'format':'bestaudio'}
      with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(search_keyword_stitched, download = False)
        vc = ctx.voice_client
        url2 = info['formats'][0]['url']
        '''
        loop = asyncio.get_event_loop()
        loop.create_task(play_next(ctx))
        vc.play(discord.FFmpegPCMAudio(source=url2), after=lambda e: loop)
        '''
        vc.play(discord.FFmpegPCMAudio(source=url2), after=lambda e: play_next(ctx))
    else:
      return


cog.append(setup(client))
client.run("BOT TOKEN")

     