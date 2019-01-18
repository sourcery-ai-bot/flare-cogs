from redbot.core import commands
import discord
import requests
import random


class Movies(commands.Cog):
    """Movie Related Commands"""

    @commands.command()
    async def movie(self, ctx, *, movie: str):
        """Movie Information Lookup"""
        movie = movie.replace(" ", "-")
        r = requests.get(
            "http://omdbapi.com/?t={}?&apikey=39937064".format(movie))
        colour = discord.Color.from_hsv(random.random(), 1, 1)
        try:
            try:
                embed = discord.Embed(title="{}".format(r.json()['Title']), colour=colour,
                                      description=r.json()['Plot'])
                embed.set_thumbnail(url=r.json()['Poster'])
                embed.add_field(name="Year:", value=r.json()['Year'], inline=True)
                embed.add_field(name="Released:", value=r.json()['Released'], inline=True)
                embed.add_field(name="Runtime:", value=r.json()['Runtime'], inline=True)
                embed.add_field(name="Director", value=r.json()['Director'], inline=True)
                embed.add_field(name="Rating:", value=r.json()['Rated'], inline=True)
                for source in r.json()['Ratings']:
                    embed.add_field(name="{}:".format(
                        source['Source']), value=source['Value'], inline=True)
                embed.add_field(name="Genre:", value=r.json()
                ['Genre'], inline=True)
                await ctx.send(embed=embed)
            except Exception:
                embed = discord.Embed(title="{}".format(r.json()['Title']), colour=colour,
                                      description=r.json()['Plot'])
                embed.add_field(name="Year:", value=r.json()['Year'], inline=True)
                embed.add_field(name="Released:", value=r.json()['Released'], inline=True)
                embed.add_field(name="Runtime:", value=r.json()['Runtime'], inline=True)
                embed.add_field(name="Director", value=r.json()['Director'], inline=True)
                embed.add_field(name="Rating:", value=r.json()['Rated'], inline=True)
                for source in r.json()['Ratings']:
                    embed.add_field(name="{}:".format(
                        source['Source']), value=source['Value'], inline=True)
                embed.add_field(name="Genre:", value=r.json()
                ['Genre'], inline=True)
                await ctx.send(embed=embed)
        except KeyError:
            await ctx.send("Ensure the title is valid.")