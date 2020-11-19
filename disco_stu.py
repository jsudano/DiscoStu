import yaml
import random
import asyncio
import os

import discord
from discord.ext import commands

""" Globals """
games_list = []
backup_period = 300 # 5 minutes
backup_filename = 'games_list.yaml'
bot = commands.Bot(command_prefix='>')

""" Utility functions """
def backup_games():
    old_list = read_backup()
    if games_list != old_list:
        if games_list:
            with open(backup_filename, 'w') as games_file:
                yaml.dump({'games': games_list}, games_file)
        else:
            # list has been cleared
            os.remove(backup_filename)

def read_backup():
    if os.path.exists(backup_filename):
        with open(backup_filename, 'r') as games_file:
            games_list_d = yaml.load(games_file, Loader=yaml.FullLoader)
            return games_list_d['games']
    else:
        return []

def periodic_backup():
    """Periodically writes games list to a local file in the background"""
    backup_games()
    loop = asyncio.get_event_loop()
    loop.call_later(backup_period, periodic_backup)

""" Bot commands """ 
@bot.command(description='Calling planet earth!')
async def ping(ctx):
    await ctx.send('Get down and pong, baby!')

@bot.command(description='Add a game to the list, baby!')
async def add(ctx, *game: str):
    game_title = ' '.join(game)

    if game_title not in games_list:
        games_list.append(game_title)
        await ctx.send('Oh! Added {0} to the games list, yeah!'.format(game_title))
    else:
        await ctx.send('Woah, daddy-o! {} is already in the games list man!'.format(game_title))

@bot.command(description='Strike that game from the list, man!')
async def remove(ctx, *game: str):
    game_title = ' '.join(game)
    
    if game_title in games_list:
        games_list.remove(game_title)
        await ctx.send('Hey now! {} is gone for good mama!'.format(game_title))
    else:
        await ctx.send('Shake it out! {} was never in the list sister!'.format(game_title))

@bot.command(description='Pick a game at random, dancing queen!')
async def choose(ctx):
    if len(games_list) > 0:
        game = random.choice(games_list)
        await ctx.send('Get on up brothers and sisters, we\'re playing {}!'.format(game))
    else:
        await ctx.send('Hold on there, the games list is emptier than a discoteque after 1992!')

@bot.command(description='Flip through the pages of the jukebox brother!')
async def list(ctx):
    if len(games_list) > 0:
        games_str = '\n> '.join(games_list)
        await ctx.send('''Let's see what the DJ's got on those hot turntables tonight!
                          > {}'''.format(games_str))
    else:
        await ctx.send('This playlist\'s empty, my man!')

@bot.command(description='Start over like ABBA in 2008!')
async def clear(ctx):
    global games_list
    games_list = []
    await ctx.send('Cleared that games list like the dance floor after a party foul, oh!')


""" Run the bot """
with open(r'config.yaml') as config_file:
    config = yaml.load(config_file, Loader=yaml.FullLoader)

token = config['token']

games_list = read_backup()

periodic_backup()

bot.run(token)

