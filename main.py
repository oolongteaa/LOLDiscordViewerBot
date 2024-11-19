import discord

class Client(discord.Client):
    async def on_ready(self):
        print(f'HELLO I AM {self.user}')

intents = discord.Intents.default()
intents.message_content = True

client = Client(intents=intents)
client.run('MTMwODI3MTUzODY0MjA5NjE2OA.Gsg_H9.XUUgmzmnyree5ezUBdPp0ujnP1JWu96jTtW_yY')
