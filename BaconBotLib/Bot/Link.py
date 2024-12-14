import discord

class Link:
    def __init__(self, From: discord.TextChannel, To: discord.TextChannel, Omni):
        self.From = From
        self.To = To

        self.Omni = Omni
    
    async def Message(self, ctx: discord.Message):
        if ctx.channel == self.To:
            await self.From.send(f"`{ctx.author.name}`: {ctx.content}")
        else:
            await self.To.send(f"`{ctx.author.name}`: {ctx.content}")