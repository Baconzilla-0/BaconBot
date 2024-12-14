import discord
import BaconBotLib as BotLib
import BaconBotLib.Types as Types



Bot = BotLib.Bot()
Music = BotLib.Music(Bot)

async def KillCommand(Response: Types.CommandResponse, Args: str):
    await Response.Respond(Embed=discord.Embed(title=f"Bye!", color=discord.Color.red()))
    exit("User Exited")
Bot.Command("Kill", "Stops the bot.", KillCommand, False, False, False)

async def ReloadCommand(Response: Types.CommandResponse, Args: str):
    await Response.Respond(Embed=discord.Embed(title=f"Reloading...", color=discord.Color.green()))
    
    File = "./Main.py"
    BotLib.Reloader.Reload(File)
    exit("File Reloaded")
Bot.Command("Reload", "Reloads the bot.", ReloadCommand, False, False, False)

async def SyncCommand(Response: Types.CommandResponse, Args: str):
    await Bot.Client.sync_commands()
Bot.Command("Sync", "Syncs all commands because discord is stupid.", SyncCommand, False, False, False)

async def SayCommand(Response: Types.CommandResponse, Args: str):
    Args = Args.split(" ", 1)
    print(Args)
    if len(Args) > 2:
        Guild =  Bot.Client.get_guild(int(Args[0]))
        Channel = Guild.get_channel(int(Args[1]))
        Message = await Channel.send(Args[2])
    else:
        Data = Args[0].removeprefix("https://discord.com/channels/").split("/")
        Guild =  Bot.Client.get_guild(int(Data[0]))
        Channel = Guild.get_channel(int(Data[1]))
        Message = await Channel.send(Args[1])

    Embed = discord.Embed(title=f"Sent message in server `{Guild.name}`, `{Channel.name}`", description=f"[Message Link](https://discord.com/channels/{Guild.id}/{Channel.id}/{Message.id})")

    await Response.Respond(Embed=Embed)
Bot.Command( "Say", f"I love spreading misinformation, syntax: {Bot.Prefix}say [serverid] [channelid] [Text]", SayCommand, True, False, False)

async def LinkCommand(Response: Types.CommandResponse, Args: str):
    Args = Args.split(" ", 2)
    print(Args)

    Data = Args[0].removeprefix("https://discord.com/channels/").split("/")
    FromGuild = Bot.Client.get_guild(int(Data[0]))
    FromChannel = FromGuild.get_channel(int(Data[1]))
    
    Data = Args[1].removeprefix("https://discord.com/channels/").split("/")
    ToGuild = Bot.Client.get_guild(int(Data[0]))
    ToChannel = ToGuild.get_channel(int(Data[1]))

    #if Args[2] == "both":
    Bot.Link(FromChannel, ToChannel, True)
    #else:
        #Bot.Link(FromChannel, ToChannel)

    

    Embed = discord.Embed(title=f"Linked `{FromGuild.name}`, `{FromChannel.name}` to `{ToGuild.name}`, `{ToChannel.name}`")

    await Response.Respond(Embed=Embed)
Bot.Command( "Link", f"links two channels syntax: -link from to", LinkCommand, True, False, False)


async def InviteCommand(Response: Types.CommandResponse, Args: str):
    return f"Here Ya Go! ||{Bot.Invite}||"
Bot.Command( "Invite", "Get the bots invite link.", InviteCommand, False, True, False)

async def HelloCommand(Response: Types.CommandResponse, Args: str):
    return f"Hello, <@{Response.Context.author.id}>"
Bot.Command( "Hello", "Say Hello! :D", HelloCommand, False, True, False)

async def DMCommand(Response: Types.CommandResponse, Args: str):
    Send = Args.split(" ", 1)[1]
    Mention = Args.split(" ", 1)[0].removeprefix("<@").removesuffix(">")

    #User = Response.Context.mentions[0]
    User = Bot.Client.get_user(int(Mention))
    DirectMessage = User.dm_channel
    if DirectMessage == None:
        DirectMessage = await User.create_dm()

    Embed = discord.Embed(title=f"From: {Response.Context.author.name} in {Response.Context.guild.name}", description=Send, color=Bot.Colours["Other"].value)

    await Response.Respond(Embed=Embed)
    await DirectMessage.send(embed=Embed)
Bot.Command( "DM", f"Sends a dm to a user of your choice, syntax: {Bot.Prefix}DM `@Mention` [Your text here].", DMCommand, True, False, True)

async def JoinCommand(Response: Types.CommandResponse, Args: str):
    if (Response.Context.author.voice): # If the person is in a channel
        channel = Response.Context.author.voice.channel
        await channel.connect()
        return f"Bot joined <#{Response.Context.author.voice.channel.id}>"
    else: #But is (s)he isn't in a voice channel
        return "You must be in a voice channel first so I can join it."
Bot.Command( "Join", "Makes the bot join your voice channel.", JoinCommand, False, True, False)

async def LeaveCommand(Response: Types.CommandResponse, Args: str):
    if (Response.Context.guild.voice_client): # If the bot is in a voice channel 
        await Response.Context.guild.voice_client.disconnect(force=True) # Leave the channel 
        return f"Bot left"
    else: # But if it isn't
        return "I'm not in a voice channel, use the join command to make me join"
Bot.Command( "Leave", "makes the bot leave your voice channel.", LeaveCommand, False, True, False)

async def TestCommand(Response: Types.CommandResponse, Args: str):
    List = [f"Item {i}" for i in range(1, 10000)]
    Embed = BotLib.PagedEmbed("Test Pages", 20, List)

    await Embed.Display(Response)
Bot.Command( "Test", "my nuts itch", TestCommand, False, True, False)

Bot.Run()