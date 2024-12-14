import discord
import spotdl
import os
import asyncio
import threading

from .. import Globals
from .. import Bot
from .. import Types
from .. import Utils

from . import Music as Music
from . import States

async def IsMusic(Player, Response: Types.CommandResponse):
    if Player.Song:
        return True
    else:
        await Response.Respond("There must be a song playing to use this command!")
        return False

MusicPlayers = {}

async def CreateCommands(Music: Music, Bot: Bot):
    async def PlayerInit(Response: Types.CommandResponse, Args: str):
        
        try:
            if MusicPlayers[str(Response.Context.guild.id)]:
                return "There is already a music player for this server!"
        except:
            #await Response.Respond(Embed=discord.Embed(title="Created music player!"))

            Player = Music.Player(Music, Response)

            MusicPlayers[str(Response.Context.guild.id)] = Player
            PlayerCommands(Player, Response.Context.guild.id)
            await Bot.Client.sync_commands()

            return "Created music player!"

    Bot.Command( "Music", "enables the music module.", PlayerInit, False, True, True)

    def PlayerCommands(Player, Guild):

        async def PlayCommand(Response: Types.CommandResponse, Args: str):
            if (Response.Context.author.voice): # If the person is in a channel
                Query = Args
                
                await Player.Play(Query, Response)
                return None
            else: #But is (s)he isn't in a voice channel
                return "You must be in a voice channel first so I can join it."
        Bot.Command( "Play", "makes the bot play music.", PlayCommand, True, True, False, Guild)


        async def PlayFileCommand(Response: Types.CommandResponse, Args: str):
            if (Response.Context.author.voice): # If the person is in a channel
                Query = Args
                
                await Player.PlayFile(f"./Temp/{Query}", Response)
                return None
            else: #But is (s)he isn't in a voice channel
                return "You must be in a voice channel first so I can join it."
        Bot.Command( "File", "makes the bot play file.", PlayFileCommand, True, True, False, Guild)

        async def PlaylistCommand(Response: Types.CommandResponse, Args: str):
            if (Response.Context.author.voice): # If the person is in a channel
                Query = Args
                await Response.Respond(f"Loading playlist `{Args}`...")
                await Player.Playlist(Response, Query)
                return None
            else: #But is (s)he isn't in a voice channel
                return "You must be in a voice channel first so I can join it."
        Bot.Command( "Playlist", "loads a playlist to the queue", PlaylistCommand, True, True, False, Guild)
        
        async def SearchCommand(Response: Types.CommandResponse, Args: str):
            if (Response.Context.author.voice): # If the person is in a channel
                Query = Args

                Prompt = await Response.Respond("Searching...")
                await Player.Search(Response, Query)
                await Prompt.delete()
                return None
            else: #But is (s)he isn't in a voice channel
                return "You must be in a voice channel first so I can join it."
        Bot.Command( "Search", "searches for a song.", SearchCommand, True, True, False, Guild)

        async def SkipCommand(Response: Types.CommandResponse, Args: str):
            if await IsMusic(Player, Response):
                await Player.Skip()
                
                return f"Skipped song"
        Bot.Command( "Skip", "skip song.", SkipCommand, False, True, False, Guild)

        async def PauseCommand(Response: Types.CommandResponse, Args: str):
            if await IsMusic(Player, Response):
                await Player.Pause()
                
                return f"Set pause to `{Player.Paused}`"
        Bot.Command( "Pause", "toggles pause.", PauseCommand, False, True, False, Guild)

        async def NowPlayingCommand(Response: Types.CommandResponse, Args: str):
            if await IsMusic(Player, Response):
                await Player.NowPlaying(Response)
        Bot.Command( "Np", "shows the current song playing.", NowPlayingCommand, False, False, False, Guild)

        async def StopCommand(Response: Types.CommandResponse, Args: str):
            if await IsMusic(Player, Response):
                await Player.Stop(Response)
        Bot.Command( "Stop", "stops the music player.", StopCommand, False, False, False, Guild)

        async def QueueCommand(Response: Types.CommandResponse, Args: str):
            if await IsMusic(Player, Response):
                await Player.GetQueue(Response)
        Bot.Command( "Queue", "shows the queue.", QueueCommand, False, False, False, Guild)

        async def FileListCommand(Response: Types.CommandResponse, Args: str):
            await Player.GetFiles(Response)
        Bot.Command( "Files", "lists all files in the bot's `Temp` folder.", FileListCommand, False, True, False, Guild)

        async def LoopCommand(Response: Types.CommandResponse, Args: str):
            if await IsMusic(Player, Response):
                await Player.Loop()
                return f"Set loop to `{Player.Repeat}`"
        Bot.Command( "Loop", "toggles repeat for the current song.", LoopCommand, False, True, False, Guild)

        async def DebugCommand(Response: Types.CommandResponse, Args: str):
            await Player.DebugInfo(Response.Context.channel)
        Bot.Command( "PlayerDebug", "helps me fix my dogshit code.", DebugCommand, False, False, False, Guild)

        