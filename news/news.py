import aiohttp
import discord
import validators
from redbot.core import commands
from redbot.core.utils.chat_formatting import humanize_number
from redbot.core.utils.menus import DEFAULT_CONTROLS, menu

import iso8601


class News(commands.Cog):
    """News Cog."""

    __version__ = "0.0.1"
    __author__ = "flare#0001"

    def format_help_for_context(self, ctx):
        """Thanks Sinbad."""
        pre_processed = super().format_help_for_context(ctx)
        return f"{pre_processed}\nCog Version: {self.__version__}\nAuthor: {self.__author__}"

    def __init__(self, bot):
        self.bot = bot
        self.api = "https://newsapi.org/v2/{}?{}&sortBy=publishedAt{}&apiKey={}&page=1{}"
        self.session = aiohttp.ClientSession(loop=self.bot.loop)
        self.newsapikey = None

    async def initalize(self):
        token = await self.bot.get_shared_api_tokens("newsapi")
        self.newsapikey = token.get("key", None)

    @commands.Cog.listener()
    async def on_red_api_tokens_update(self, service_name, api_tokens):
        if service_name == "newsapi":
            self.newsapikey = api_tokens.get("key", None)

    def cog_unload(self):
        self.bot.loop.create_task(self.session.close())

    async def get(self, url):
        async with self.session.get(url) as response:
            data = await response.json()
            if response.status == 200:
                try:
                    return data
                except aiohttp.ServerTimeoutError:
                    return {
                        "failed": "Their appears to be an issue with the API. Please try again later."
                    }
            else:
                return {"failed": data["message"]}

    async def send_embeds(self, ctx, embeds):
        if len(embeds) == 1:
            await ctx.send(embed=embeds[0])
        else:
            await menu(ctx, embeds, DEFAULT_CONTROLS, timeout=90)

    @commands.group()
    async def news(self, ctx):
        """Group Command for News."""

    @commands.command()
    async def newssetup(self, ctx):
        """Instructions on how to setup news related APIs."""
        msg = "**News API Setup**\n**1**. Visit https://newsapi.org and register for an API.\n**2**. Use the following command: {}set api newsapi key <api_key_here>\n**3**. Reload the cog if it doesnt work immediately.".format(
            ctx.prefix
        )
        await ctx.maybe_send_embed(msg)

    @news.command(hidden=True)
    async def countrycodes(self, ctx):
        """Countries supported by the News Cog."""
        await ctx.send(
            "Valid country codes are:\nae ar at au be bg br ca ch cn co cu cz de eg fr gb gr hk hu id ie il in it jp kr lt lv ma mx my ng nl no nz ph pl pt ro rs ru sa se sg si sk th tr tw ua us ve za"
        )

    @news.command()
    async def top(self, ctx, countrycode: str, *, query: str = None):
        """
        Top News from a Country - County must be 2-letter ISO 3166-1 code. Supports querys to search news.

        Check [p]news countrycodes for a list of all possible country codes supported.
        """
        async with ctx.typing():
            data = await self.get(
                self.api.format(
                    "top-headlines",
                    "q={}".format(query) if query is not None else "",
                    "&country={}".format(countrycode),
                    self.newsapikey,
                    "",
                )
            )
        if data.get("failed") is not None:
            return await ctx.send(data.get("failed"))
        if data["totalResults"] == 0:
            return await ctx.send(
                "No results found, ensure you're looking up the correct country code. Check {}countrycodes for a list. Alternatively, your query may be returning no results.".format(
                    ctx.prefix
                )
            )
        embeds = []
        total = 15 if len(data["articles"]) > 15 else len(data["articles"])
        for i, article in enumerate(data["articles"][:15], 1):
            embed = discord.Embed(
                title=article["title"],
                color=await self.bot.get_embed_color(ctx.channel),
                description=f"\n{article['description']}",
                timestamp=iso8601.parse_date(article["publishedAt"]),
                url=article["url"],
            )
            if article["urlToImage"] is not None:
                if validators.url(article["urlToImage"]):
                    embed.set_image(url=article["urlToImage"])
            embed.set_author(name=f"{article['author']} - {article['source']['name']}")
            embed.set_footer(text=f"Article {i}/{total}")
            embeds.append(embed)
        await self.send_embeds(ctx, embeds)

    @news.command(name="global")
    async def global_all(self, ctx, *, query: str = None):
        """News from around the World.

        Not considered top-headlines. May be unreliable, unknown etc.
        """
        async with ctx.typing():
            data = await self.get(
                self.api.format("everything", "q={}".format(query), "", self.newsapikey, "")
            )
        if data.get("failed") is not None:
            return await ctx.send(data.get("failed"))
        if data["totalResults"] == 0:
            return await ctx.send("No results found.")
        embeds = []
        total = 15 if len(data["articles"]) > 15 else len(data["articles"])
        for i, article in enumerate(data["articles"][:15], 1):
            embed = discord.Embed(
                title=article["title"],
                color=await self.bot.get_embed_color(ctx.channel),
                description=f"\n{article['description']}",
                timestamp=iso8601.parse_date(article["publishedAt"]),
                url=article["url"],
            )
            if article["urlToImage"] is not None:
                if validators.url(article["urlToImage"]):
                    embed.set_image(url=article["urlToImage"])
            embed.set_author(name=f"{article['author']} - {article['source']['name']}")
            embed.set_footer(text=f"Article {i}/{total}")
            embeds.append(embed)
        await self.send_embeds(ctx, embeds)

    @news.command()
    async def topglobal(self, ctx, *, query: str):
        """Top Headlines from around the world."""
        async with ctx.typing():
            data = await self.get(
                self.api.format("top-headlines", "q={}".format(query), "", self.newsapikey, "")
            )
        if data.get("failed") is not None:
            return await ctx.send(data.get("failed"))
        if data["totalResults"] == 0:
            return await ctx.send("No results found.")
        embeds = []
        total = 15 if len(data["articles"]) > 15 else len(data["articles"])
        for i, article in enumerate(data["articles"][:15], 1):
            print(article["publishedAt"][:-6])
            embed = discord.Embed(
                title=article["title"],
                color=await self.bot.get_embed_color(ctx.channel),
                description=f"\n{article['description']}",
                timestamp=iso8601.parse_date(article["publishedAt"]),
                url=article["url"],
            )
            if article["urlToImage"] is not None:
                if validators.url(article["urlToImage"]):
                    embed.set_image(url=article["urlToImage"])
            embed.set_author(name=f"{article['author']} - {article['source']['name']}")
            embed.set_footer(text=f"Article {i}/{total}")
            embeds.append(embed)
        await self.send_embeds(ctx, embeds)