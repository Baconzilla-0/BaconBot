import discord
import mutagen.mp3
import spotdl
import os
import datetime

## helps with mp3 format i hate this so much
import mutagen
from mutagen.mp3 import MP3  
from mutagen.easyid3 import EasyID3  
import mutagen.id3  
from mutagen.id3 import ID3, TIT2, TIT3, TALB, TPE1, TRCK, TYER  

## keeps me sane
from . import Types

def Folder(Path):
    if os.path.exists(Path) != True:
        os.mkdir(Path)

    return True

def Log(Msg, Timestamp: datetime.datetime, Channel: discord.TextChannel, User):
    ServerFolder = f"./Logs/{Channel.guild.name} - {Channel.guild.id}"
    CatagoryFolder = f"{ServerFolder}/{Channel.category.name} - {Channel.category.id}"
    
    Folder(ServerFolder)
    Folder(CatagoryFolder)
    Folder()

    ChannelType = None
    if Channel.type == discord.ChannelType.text:
        print('Text Channel')
        ChannelType = "Text"
    elif Channel.type == discord.ChannelType.voice:
        print('Voice Channel')
        ChannelType = "Voice"
    

    with open(f"{CatagoryFolder}/{Channel.name} - {Channel.id}.txt", "a") as LogFile:
        try:
            LogFile.write(f"[ {Timestamp.day}/{Timestamp.month}/{Timestamp.year} | {Timestamp.hour}:{Timestamp.minute}:{Timestamp.second} ] {User} > {Msg} \n")
        except UnicodeError:
            print("Unicode shit itself again :[")
        print(f"[ {Timestamp.day}/{Timestamp.month}/{Timestamp.year} | {Timestamp.hour}:{Timestamp.minute}:{Timestamp.second} ] {User} > {Msg}")

async def IsURL(Str: str):
    return Str.startswith("http://") or Str.startswith("https://")

async def GenerateAudioSources(SongData: Types.Song):
    Source = discord.FFmpegPCMAudio(SongData.File, executable="./ffmpeg/bin/ffmpeg.exe")
    Tracked = Types.AudioSourceTracked(Source)

    SongData.Source = Tracked

    return SongData

async def PredictFilename(Song: Types.Song):
    if len(Song.Meta.artists) > 1: # If more than one artist
        Artists = str(Song.Meta.artists).rstrip("]").lstrip("[").replace("'", "")
        Name = f"{Artists} - {Song.Meta.name}"
    else: # If single artist
        Name = f"{Song.Meta.artist} - {Song.Meta.name}".replace(":", "-").replace("/", "")
    
    return Name

async def MakeSongDescription(Song: Types.Song, Detail):
    """Detail can be 1, 2 or 3. 3 being the most detail."""
    Data = Song.Meta
    if Detail == 1:
        Description = f"{Data.name} by {Data.artist}"
    elif Detail == 2:
        Description = f"{Data.name} by {Data.artist} on album {Data.album_name}"
    elif Detail == 3:
        Description = f"{Data.name} by {Data.artist} on album {Data.album_name} by {Data.album_artist}"

    return Description

async def JoinVoice(Player, Response: Types.CommandResponse):
    if not Player.Voice:
        if Response.Context.guild.voice_client:
            Player.Voice = Response.Context.guild.voice_client
        elif Response.Context.author.voice:
            await Response.Context.author.voice.channel.connect()
            Player.Voice = Player.Server.voice_client
        else:
            await Response.Respond("You have to be in a vc to hear music, sorry deaf people.")
            return None

def Bar(Max, Value, Length):
    PartBar = ""
    Percent = Value / Max
    Scaled = int(Percent * Length)
    Remain = Length - Scaled

    PartBar = PartBar.rjust(Scaled,"█")
    for i in range(Remain):
        PartBar = PartBar + "▒"
    
    return f"{PartBar}"
