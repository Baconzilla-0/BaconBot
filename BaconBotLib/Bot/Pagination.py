import discord
from .. import Types
from typing import Callable, Optional


class Pagination(discord.ui.View):
    def __init__(self, Response: Types.CommandResponse, get_page: Callable):
        self.Response = Response
        self.Message = Response.Context

        self.get_page = get_page
        self.total_pages: Optional[int] = None
        self.index = 1
        super().__init__(timeout=100)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user == self.Message.author:
            return True
        else:
            #emb = discord.Embed(
            #    description=f"Only the author of the command can perform this action.",
            #    color=16711680
            #)
            #await interaction.response.send_message(embed=emb, ephemeral=True)
            return False

    async def navegate(self):
        emb, self.total_pages = await self.get_page(self.index)
        if self.total_pages == 1:
            await self.Response.Respond(Embed=emb)
        elif self.total_pages > 1:
            self.update_buttons()
            await self.Response.Respond(Embed=emb, View=self)

    async def edit_page(self, interaction: discord.Interaction):
        await interaction.response.defer()
        emb, self.total_pages = await self.get_page(self.index)
        self.update_buttons()
        await self.Response.Edit(Embed=emb, View=self)

    def update_buttons(self):
        if self.index > self.total_pages // 2:
            self.children[2].emoji = "⏮️"
        else:
            self.children[2].emoji = "⏭️"
        self.children[0].disabled = self.index == 1
        self.children[1].disabled = self.index == self.total_pages

    @discord.ui.button(emoji="◀️", style=discord.ButtonStyle.blurple)
    async def previous(self, button: discord.Button, interaction: discord.Interaction):
        self.index -= 1
        await self.edit_page(interaction)

    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.blurple)
    async def next(self, button: discord.Button, interaction: discord.Interaction):
        self.index += 1
        await self.edit_page(interaction)

    @discord.ui.button(emoji="⏭️", style=discord.ButtonStyle.blurple)
    async def end(self, button: discord.Button, interaction: discord.Interaction):
        if self.index <= self.total_pages//2:
            self.index = self.total_pages
        else:
            self.index = 1
        await self.edit_page(interaction)

    async def on_timeout(self):
        # remove buttons on timeout
        await self.Response.Edit(View=None)

    @staticmethod
    def compute_total_pages(total_results: int, results_per_page: int) -> int:
        return ((total_results - 1) // results_per_page) + 1

class PagedEmbed:
    def __init__(self, Title, Limit, List):
        self.List = List
        self.Limit = Limit
        
        self.Title = Title

    async def Display(self, Response: Types.CommandResponse):
        async def Get(Page: int):
            Embed = discord.Embed(title=self.Title, description="")
            offset = (Page - 1) * self.Limit
            for Item in self.List[offset:offset + self.Limit]:
                Embed.description += f"{Item}\n"
            Embed.set_author(name=f"Requested by {Response.Context.author}")
            Count = Pagination.compute_total_pages(len(self.List), self.Limit)
            Embed.set_footer(text=f"Page {Page} of {Count}")

            return Embed, Count

        await Pagination(Response, Get).navegate()


