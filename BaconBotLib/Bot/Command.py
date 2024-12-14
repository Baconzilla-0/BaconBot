import discord
import types

from .. import Utils
from .. import Types


class Input:
        def __init__(self, Bot, Channel: discord.TextChannel, User, Prompt, Callback):
            self.Channel = Channel
            self.User = User
            self.Prompt = Prompt
            self.Callback = Callback
            self.Active = False
            self.Message = None

            Bot.Inputs.append(self)

        async def Display(self):
            self.Active = True
            self.Message = await self.Channel.send(self.Prompt)

        async def Check(self, Msg: discord.Message):
            if self.Active:
                if Msg.channel.id == self.Channel.id:
                    if Msg.author.id == self.User.id:
                        print(f"Received Input: {Msg.content}")
                        await self.Callback(Msg)
                        await Msg.delete(reason="Input received.")
                        await self.Message.delete(reason="Input received.")
                        self.Active = False

class Command:
    def __init__(self, Parent, Name, Description, Callback, Args = True, Reply = True, Embedded = True, Server = None):
        self.Name = Name
        self.Description = Description
        self.Callback = Callback
        self.Feedback = ""
        self.Args = Args
        self.Reply = Reply
        self.Embedded = Embedded
        self.Server = Server
        self.Parent = Parent

        self.Parent.Commands.append(self)

    async def Run(self, Bot, Message: discord.Message):
        Errored = False

        if Message.author.id != Bot.Client.user.id:
            Server = False

            if self.Server == None:
                Server = True
            elif self.Server == Message.guild.id:
                Server = True

            if Server:
                if Message.content.split(" ", 1)[0].lower() == (f"{Bot.Prefix}{self.Name}".lower()):
                    RawMessage = Message.content.lstrip(";")
                    if self.Args:
                        try:
                            Args = RawMessage.split(" ", 1)[1]
                        except Exception as E:
                            Args = None
                    else:
                        Args = None
                    
                    if Bot.CatchErrors:
                        try:
                            Colour = "Feedback"
                            self.Feedback = await self.Callback(Types.CommandResponse(False, Message), Args)
                        except Exception as E:
                            Colour = "Error"
                            self.Feedback = f"Could not run command... Exception: `{E}`"
                            Errored = True
                            ##help(E)
                    else:
                        Colour = "Feedback"
                        self.Feedback = await self.Callback(Types.CommandResponse(False, Message), Args)

                    if Args == None and self.Args == True:
                        Colour = "Error"
                        self.Feedback = f"Could not run command... Invalid Args, Use `{Bot.Prefix}help` if you're confused."
                        Errored = True
                    print(f"Command: {self.Name}, Args: {Args}, Raw: {RawMessage}, Feedback: {self.Feedback}")

                    if self.Reply:
                        if self.Feedback:
                            if self.Embedded or Errored:
                                FeedbackEmbed = discord.Embed(title=self.Feedback, color=Bot.Colours[Colour].value)
                                await Message.channel.send(embed=FeedbackEmbed)
                            else:
                                await Message.reply(self.Feedback)
                    return True
                else:
                    return False
                
class SlashCommand(Command):
    def __init__(self, Parent, Name, Description, Callback, Args, Reply, Embedded, Server = None):
        super().__init__(Parent, Name, Description, Callback, Args, Reply, Embedded, Server)

        Parent.Commands.remove(self)

        Client: discord.Bot = Parent.Client

        Servers = []
        
        if Server:
            Servers = [Server]
        else:
            for Guild in Client.guilds:
                Servers.append(Guild.id)
            
        if Server:
            if self.Args:
                @Client.command(name = Name.lower(), description=Description.lower(), guild_ids=Servers)
                @discord.option(
                    "args", 
                    description="command arguments, see /help for details",
                    required=True,
                    default='',
                )
                async def SlashRun(ctx: discord.ApplicationContext, args):
                    await self.Run(self.Parent, ctx, args)
            else:
                @Client.command(name = Name.lower(), description=Description.lower(), guild_ids=Servers)
                async def SlashRun(ctx: discord.ApplicationContext):
                    await self.Run(self.Parent, ctx, None)
        else:
            if self.Args:
                @Client.command(name = Name.lower(), description=Description.lower())
                @discord.option(
                    "args", 
                    description="command arguments, see /help for details",
                    required=True,
                    default=''
                )
                async def SlashRun(ctx: discord.ApplicationContext, args):
                    await self.Run(self.Parent, ctx, args)
            else:
                @Client.command(name = Name.lower(), description=Description.lower())
                async def SlashRun(ctx: discord.ApplicationContext):
                    await self.Run(self.Parent, ctx, None)
    

    async def Run(self, Bot, Ctx: discord.ApplicationContext, Args = None):
        Errored = False
        await Ctx.defer()

        if Bot.CatchErrors:
            try:
                Colour = "Feedback"
                self.Feedback = await self.Callback(Types.CommandResponse(True, Ctx), Args)
            except Exception as E:
                Colour = "Error"
                self.Feedback = f"Could not run command... Exception: `{E}`"
                Errored = True
                ##help(E)
        else:
            Colour = "Feedback"
            self.Feedback = await self.Callback(Types.CommandResponse(True, Ctx), Args)

        if Args == None and self.Args == True:
            Colour = "Error"
            self.Feedback = f"Could not run command... Invalid Args, Use `{Bot.Prefix}help` if you're confused."
            Errored = True
        print(f"Command: {self.Name}, Args: {Args}, Raw: {None}, Feedback: {self.Feedback}")

        if self.Reply:
            if self.Feedback:
                if self.Embedded or Errored:
                    FeedbackEmbed = discord.Embed(title=self.Feedback, color=Bot.Colours[Colour].value)
                    await Ctx.respond(embed=FeedbackEmbed)
                else:
                    await Ctx.respond(self.Feedback)
        else:
            pass
            #await Ctx.delete()
    
class MultiCommand:
    def __init__(self, Parent, Name, Description, Callback, Args, Reply, Embedded, Server = None):
        self.Slash = SlashCommand(Parent, Name, Description, Callback, Args, Reply, Embedded, Server)
        self.Text = Command(Parent, Name, Description, Callback, Args, Reply, Embedded, Server)
