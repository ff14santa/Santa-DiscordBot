import env
import discord
from discord import app_commands
from FFlogs import FFlogs

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    # async def setup_hook(self):
    #     self.tree.copy_global_to(guild=discord.Object(id=0))
    #     await self.tree.sync(guild=discord.Object(id=0))

fflogs = FFlogs(FFLOG_CLIENT=env.FFLOG_CLIENT, FFLOG_SECRET=env.FFLOG_SECRET)


intents = discord.Intents.default()
client = MyClient(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')

@client.tree.command()
@app_commands.rename(nickname='닉네임', server='서버')
@app_commands.choices(server=[app_commands.Choice(name=k, value=v) for k, v in env.SERVERS.items()])
async def 프프로그(interaction: discord.Interaction, nickname: str, server: app_commands.Choice[str]):
    msg_lines = list()
    raw_msg = fflogs.get_fflogs(nickname, server.value)
    for k, v in raw_msg.items():
        msg_lines.append(f"`{k}`\n> `점수` : `{v['rankPercent']:.1f}`\n> `직업` : `{env.JOBS[v['bestSpec']]}`")
    msg = '\n'.join(msg_lines) if msg_lines else '검색 결과가 없습니다.'
    await interaction.response.send_message(msg)

client.run(env.DISCORD_TOKEN)
