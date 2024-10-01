import discord
from discord.ext import commands, tasks
import asyncio
import json
from datetime import datetime, timedelta

TOKEN = 'MTI5MDM0OTEwOTM4Mjc0NjIwNA.GvAit9.Aa08kSGJZn1ubsREkiXDWOMK6oTxFDEaaoZ5Js'
CHANNEL_ID = 1290351163652444231
FILE_PATH = r'C:\Users\jesse\AppData\Roaming\ModrinthApp\profiles\Hardcore Series\saves\Hardcore_Series_creative\stats\ee862b70-f0b9-40fa-9b44-efa4913f0476.json'
MESSAGE_ID_FILE = 'message_id.txt'
OFFLINE_MESSAGE_ID_FILE = 'offline_message_id.txt'
RELOAD_EMOJI = '🔄'  # Emoji für das Neuladen

intents = discord.Intents.default()
intents.messages = True  # Aktiviert die Nachrichten-Intents
intents.message_content = True  # Aktiviert den message_content Intent
intents.reactions = True  # Aktiviert die Reaktions-Intents

bot = commands.Bot(command_prefix='/', intents=intents)

class StatsUpdater:
    def __init__(self, channel):
        self.channel = channel
        self.message = None
        self.last_update = datetime.now()

    async def send_stats(self):
        try:
            with open(FILE_PATH, 'r') as file:
                data = json.load(file)
                print("Daten aus der Datei:", data)  # Debugging-Ausgabe
                embed = discord.Embed(title="Minecraft Stats", color=discord.Color.blue())
                
                # Alle möglichen Statistiken
                all_stats = {
                    "minecraft:mined": {},
                    "minecraft:broken": {},
                    "minecraft:crafted": {},
                    "minecraft:used": {},
                    "minecraft:picked_up": {},
                    "minecraft:dropped": {},
                    "minecraft:killed": {},
                    "minecraft:killed_by": {},
                    "minecraft:custom": {
                        "minecraft:open_chest": 0,
                        "minecraft:sneak_time":0,
                        "minecraft:crouch_one_cm": 0,
                        "minecraft:sprint_one_cm": 0,
                        "minecraft:deaths": 0,
                        "minecraft:walk_one_m": 0,
                        "minecraft:mob_kills": 0,
                        "minecraft:jump": 0,
                        "minecraft:damage_dealt": 0,
                        "minecraft:leave_game": 0,
                        "minecraft:walk_on_water_one_m": 0,
                        "minecraft:sleep_in_bed": 0,
                        "minecraft:climb_one_m": 0,
                        "minecraft:talked_to_villager": 0,
                        "minecraft:time_since_rest": 0,
                        "minecraft:play_time": 0,
                        "minecraft:time_since_death": 0,
                        "minecraft:total_world_time": 0,
                        "minecraft:fly_one_m": 0
                    }
                }
                
                # Daten aus der Datei einfügen

                distance_cm_keys = {
                    "minecraft:crouch_one_cm": "Distance Crouched",
                    "minecraft:sprint_one_cm": "Distance Sprinted"
                    }

                distance_m_keys = {
                    "minecraft:walk_one_m": "Distance Walked",
                    "minecraft:walk_on_water_one_m": "Distance Swam",
                    "minecraft:climb_one_m": "Distance Climbed",
                    "minecraft:fly_one_m": "Distance Flown"
                    }

                time_keys = {
                    "minecraft:sneak_time": "Time sneaked",
                    "minecraft:time_since_rest": "Time since last rest",
                    "minecraft:play_time": "Playtime",
                    "minecraft:time_since_death": "Time since Death",
                    "minecraft:total_world_time": "Time with World open"
                    }

                for key, label in distance_cm_keys.items():
                    if key in data['stats']['minecraft:custom']:
                        distance_cm = data['stats']['minecraft:custom'][key]
                        meters = distance_cm / 100
                        all_stats["minecraft:custom"][f"{label}_"] = f"{meters:.2f} Blocks"
                        del all_stats["minecraft:custom"][key]

                for key, label in distance_m_keys.items():
                    if key in data['stats']['minecraft:custom']:
                        distance_m = data['stats']['minecraft:custom'][key]
                        meters = distance_m * 1
                        all_stats["minecraft:custom"][f"{label}_"] = f"{meters:.2f} Blocks"
                        del all_stats["minecraft:custom"][key]
               
                for key, label in time_keys.items():
                    if key in data['stats']['minecraft:custom']:
                        ticks = data['stats']['minecraft:custom'][key]
                        hours = ticks / 72000
                        all_stats["minecraft:custom"][f"{label}_"] = f"{hours:.2f} Hours"
                        del all_stats["minecraft:custom"][key]
                
                # Kategorien formatieren
                for category, stats in all_stats.items():
                    embed.add_field(name=category.replace("minecraft:", "").capitalize(), value="\n".join([f"{key.replace('minecraft:', '').replace('_', ' ').capitalize()}: {value}" for key, value in stats.items()]), inline=False)
                
                embed.set_footer(text=f"Zuletzt aktualisiert: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
            
            if self.message:
                print(f'Editing message: {self.message.id}')
                await self.message.edit(embed=embed)
                await self.message.clear_reactions()
            else:
                print('Sending new message')
                self.message = await self.channel.send(embed=embed)
                with open(MESSAGE_ID_FILE, 'w') as f:
                    f.write(str(self.message.id))
            await self.message.add_reaction(RELOAD_EMOJI)
            self.last_update = datetime.now()
        except Exception as e:
            print(f'Fehler: {e}')
            await self.channel.send(f'Fehler beim Lesen der Datei: {e}')

@bot.event
async def on_ready():
    print(f'Bot ist eingeloggt als {bot.user}')
    channel = bot.get_channel(CHANNEL_ID)
    
    global stats_updater
    stats_updater = StatsUpdater(channel)
    
    try:
        with open(MESSAGE_ID_FILE, 'r') as f:
            message_id = int(f.read().strip())
            stats_updater.message = await channel.fetch_message(message_id)
            await stats_updater.message.add_reaction(RELOAD_EMOJI)
    except Exception as e:
        print(f'Fehler beim Laden der Nachricht: {e}')
    
    # Lösche die Offline-Nachricht, wenn der Bot wieder online ist
    try:
        with open(OFFLINE_MESSAGE_ID_FILE, 'r') as f:
            offline_message_id = int(f.read().strip())
            offline_message = await channel.fetch_message(offline_message_id)
            await offline_message.delete()
    except Exception as e:
        print(f'Fehler beim Löschen der Offline-Nachricht: {e}')
    
    # Sende die initiale Nachricht
    await stats_updater.send_stats()
    
    update_message.start(stats_updater)

@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    if reaction.message.id == stats_updater.message.id and str(reaction.emoji) == RELOAD_EMOJI:
        await reaction.message.remove_reaction(reaction.emoji, user)
        await stats_updater.send_stats()

@bot.command()
async def stopbot(ctx):
    stop_message = await ctx.send("Bot wird gleich gestoppt...")
    await asyncio.sleep(2)
    await ctx.message.delete()
    await stop_message.delete()
    if stats_updater.message:
        await stats_updater.message.delete()
    
    # Sende die Offline-Nachricht
    offline_embed = discord.Embed(title="Bot Status", description="Der Bot ist zurzeit offline.", color=discord.Color.red())
    offline_message = await ctx.send(embed=offline_embed)
    with open(OFFLINE_MESSAGE_ID_FILE, 'w') as f:
        f.write(str(offline_message.id))
    
    await bot.close()

@tasks.loop(minutes=1)
async def update_message(stats_updater):
    if datetime.now() - stats_updater.last_update >= timedelta(hours=3):
        await stats_updater.send_stats()

@bot.command()
async def hardcorebothelp(ctx):
    embed = discord.Embed(title="Bot Commands", color=discord.Color.green())
    embed.add_field(name="/stopbot", value="Stoppt den Bot und löscht die Nachrichten.", inline=False)
    embed.add_field(name="/hardcorebothelp", value="Zeigt diese Vorschau der Commands an.", inline=False)
    await ctx.send(embed=embed)

async def main():
    await bot.start(TOKEN)

asyncio.run(main())


