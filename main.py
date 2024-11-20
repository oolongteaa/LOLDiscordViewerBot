import discord
from discord.ext import commands
from riotIntegrations import riot_api
import os

if __name__ == "__main__":

    TOKEN = os.environ["TOKEN"]
    RIOT_API_KEY = os.environ["RIOT_API_KEY"]

    intents = discord.Intents.default()
    intents.presences = True
    intents.guilds = True
    intents.members = True
    intents.message_content = True

    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_ready():
        print(f"I AM {bot.user.name}")

    """"
    @bot.event
    async def on_presence_update(before: discord.Member, after: discord.Member):
        if after.voice and after.voice.self_stream:
            print(f"{after.name} started streaming")
    """


    @bot.command()
    @commands.guild_only()
    async def streaming(ctx):
        """Command to list all members who are screen sharing."""
        guild = ctx.guild  #Get the server where the command was invoked
        screen_sharing_members = []

        for voice_channel in guild.voice_channels:
            for member in voice_channel.members:
                if member.voice and member.voice.self_stream: #Check if the member is screen sharing
                    screen_sharing_members.append(f"{member.name} in {voice_channel.name}")

        if screen_sharing_members:
            response = "Members currently screen sharing:\n" + "\n".join(screen_sharing_members)
        else:
            response = "No one is currently screen sharing"

        await ctx.send(response)


    @bot.command()
    @commands.guild_only()
    async def bet(ctx, user: discord.User, username: str, amount: int):
        guild = ctx.guild

        response = f"user = {user} username = {username} amount = {amount}"

        await ctx.send(response)

    @bot.command()
    @commands.guild_only()
    async def startgame(ctx, league_username: str, tag: str):
        game = riot_api.is_in_game(RIOT_API_KEY, "americas", "na1", league_username, tag)
        if game is not None:
            gameId = game["gameId"]
            response = f"{league_username} is currently in game"
            riot_api.spawn_game_monitor(RIOT_API_KEY, "americas", gameId, league_username, tag, "na1")
        else:
            response = f"{league_username} is not currently in game"

        await ctx.send(response)


    async def send_message_to_channel(channel_id, message):
        """
        Sends a message to a specific channel by ID.

        :param channel_id: The ID of the channel to send the message to.
        :param message: The message to send.
        """
        # Get the channel object
        channel = bot.get_channel(channel_id)

        if channel:
            # Send the message
            await channel.send(message)
        else:
            print(f"Channel with ID {channel_id} not found.")

    bot.run(TOKEN)