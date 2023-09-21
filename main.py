import discord
from discord.ext import commands, tasks
import requests
#Bot TOKEN
token = "TOKEN"
chanellid = 12345678910      #channel id
prefix = "!"
intents = discord.Intents.default()
intents.typing = False
intents.presences = False

bot = commands.Bot(command_prefix=prefix, intents=intents)

#put your server ips
server_info = {
    "madcraft": "play.madcraft.ir",
    "voidpixel": "play.voidpixel.ir",
    "trexmine": "play.trexmine.com",
    "pikanetwork": "mcslq.pika.host"
}


class Leaderboard:
    def __init__(self, channel):
        self.servers = server_info
        self.channel = channel
        self.last_message = None  

    def get_leaderboard(self):
        sorted_servers = sorted(self.servers.items(), key=lambda x: get_players_online(x[1]), reverse=True)
        return sorted_servers

leaderboard = Leaderboard(channel=None)


def get_players_online(server_ip):
    try:
        url = f"https://api.mcsrvstat.us/2/{server_ip}"
        response = requests.get(url)
        data = response.json()
        if "players" in data and "online" in data["players"]:
            players_online = data["players"]["online"]
            return players_online
        else:
            return 0
    except Exception as e:
        print(f"خطا در دریافت اطلاعات سرور: {str(e)}")
        return 0


@tasks.loop(minutes=2)
async def update_leaderboard():
    sorted_servers = leaderboard.get_leaderboard()
    
    embed = discord.Embed(title="بیشترین پلیر ها", color=0x00ff00)
    
    for idx, (server_name, server_ip) in enumerate(sorted_servers, start=1):
        players_online = get_players_online(server_ip)
        embed.add_field(name=f"{idx}. {server_name}", value=f"آنلاین: {players_online}", inline=False)

    if leaderboard.channel:
        if leaderboard.last_message:
            await leaderboard.last_message.edit(embed=embed) 
        else:
            leaderboard.last_message = await leaderboard.channel.send(embed=embed)  


@bot.event
async def on_ready():
    print(f"بات {bot.user.name} آماده است.")
    leaderboard.channel = bot.get_channel(chanellid)  
    update_leaderboard.start()

bot.run(token)
