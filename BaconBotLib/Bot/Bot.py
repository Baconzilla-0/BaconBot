from asyncio import AbstractEventLoop
import discord
import types

from .. import Utils
from .. import Types

from .Link import Link
from .Command import *

class Client(discord.Bot):
    def __init__(self, Self, *, loop: AbstractEventLoop | types.NoneType = None, **options: discord.Any):
        super().__init__(loop=loop, **options)
        self.Bot = Self


    async def on_ready(self):
        activity = discord.Activity(name="the voices", type=discord.ActivityType.listening)
        await self.change_presence(status=discord.Status.online, activity=activity)
        print(f'Logged on as {self.user}!')


    async def on_message(self, message: discord.Message):
        print(f'Message in {message.guild} from {message.author}: {message.content}')
        if message.author.id != self.Bot.Client.user.id:
            HasCommand = False
            for Cmd in self.Bot.Commands:
                Cmd: Bot.Command
                HasCommand = await Cmd.Run(self.Bot, message)
                
            for Input in self.Bot.Inputs:
                await Input.Check(message)
        
            for Linked in self.Bot.Links:
                if Linked.Omni == True:
                    if message.channel.id == Linked.To.id:
                        await Linked.Message(message)
                if message.channel.id == Linked.From.id:
                    await Linked.Message(message)


    async def on_voice_state_update(self, user: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if before != after:
            if after.channel:
                print(f'{user.name} has joined {after.channel.name} in {after.channel.guild.name}')

class Bot:
    Colours = {
        "Help": discord.Colour.green(),
        "Error": discord.Colour.red(),
        "Warn":discord.Colour.yellow(),
        "Feedback": discord.Colour.blue(),
        "Other": discord.Colour.purple()
    }

    def __init__(self):
        self.Commands = []
        self.Inputs = []
        self.Prefix = "-"
        self.Invite = "i dont fakin think so"
        self.Colours = Bot.Colours
        self.CatchErrors = False

        self.Links = []

        Intents = discord.Intents.default()
        Intents.typing = True
        Intents.messages = True
        Intents.voice_states = True
        Intents.members = True
        Intents.message_content = True
        Intents.message_content = True

        self.Client = Client(self, intents=Intents)


        async def HelpCmd(Response: Types.CommandResponse, Args: str):
            HelpList = ""

            for Cmd in self.Commands:
                Cmd: Command

                HelpList = HelpList + f"{Cmd.Name} | {Cmd.Description}\n"

            HelpEmbed = discord.Embed(title=f"{self.Client.user.name} Help", description=HelpList, color=Bot.Colours["Help"].value)

            await Response.Respond(Embed=HelpEmbed)
            return None
        
        self.Command("Help", "Shows information about various commands.", HelpCmd, False, False, False)

    def Run(self):
        Token = ""
        if Token == "":
            with open("./Token.txt", "r") as TokenFile:
                TokenLines = TokenFile.readlines()
                Token = TokenLines[0]
        
        self.Client.run(Token)

    def Link(self, From, To, Omni = False):
        New = Link(From, To, Omni)
        self.Links.append(New)

    def Command(self, Name, Description, Callback, Args = True, Reply = True, Embedded = True, Server = None):
        MultiCommand(self, Name, Description, Callback, Args, Reply, Embedded, Server)

    def Input(self, Channel, User, Prompt, Callback):
        return Input(self, Channel, User, Prompt, Callback)

    async def Embed(self, Text, Colour: discord.Color, Channel: discord.TextChannel):
        Emb = discord.Embed(title=Text, color=Colour)

        await Channel.send(embed=Emb)
                 
    def Message(Channel: discord.TextChannel, Content: str):
        Channel.send(Content)
