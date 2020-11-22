import yaml
import random
import asyncio
import aiofiles
import os
import json

import discord
from discord.ext import commands

""" Globals """
backup_filename = 'stu_data.yaml'

bot = commands.Bot(command_prefix='>')

class DiscoStu:
    """ class to store Stu's operating data """
    def __init__(self, backup_location, load_backup=True):
        self.choice_list = []
        self.user_games_dict = {}
        self.backup_location = backup_location
        if load_backup:
            self._load_backup()

    async def _backup_data(self):
        backup_dict = {'list': self.choice_list, 'user_games': self.user_games_dict}
        async with aiofiles.open(self.backup_location, mode='w') as backup_file:
            # aiofiles means we can't use any formatting libs (yaml, json, pickle, etc) to
            # save to files. Should probably find a more robust way than stringifying...
            json_str = json.dumps(backup_dict)
            await backup_file.write(json_str)

    def _load_backup(self):
        # loading is done synchronously because it's only called at intialization
        # (you can't really call an async function in __init__)
        if os.path.exists(self.backup_location):
            with open(self.backup_location, mode='r') as backup_file:
                backup_dict = json.loads(backup_file.read())
                self.choice_list = backup_dict['list']
                self.user_games_dict = backup_dict['user_games']

    async def ping(self, ctx):
        await ctx.send('Get down and pong, baby!')

    async def choice_add(self, ctx, game_title):
        if game_title not in self.choice_list:
            self.choice_list.append(game_title)
            await ctx.send('Oh! Added {0} to the games list, yeah!'.format(game_title))
            asyncio.ensure_future(self._backup_data())
        else:
            await ctx.send('Woah, daddy-o! {} is already in the games list man!'.format(game_title))

    async def choice_remove(self, ctx, game_title):
        if game_title in self.choice_list:
            self.choice_list.remove(game_title)
            await ctx.send('Hey now! {} is gone for good mama!'.format(game_title))
            asyncio.ensure_future(self._backup_data())
        else:
            await ctx.send('Shake it out! {} was never in the list sister!'.format(game_title))

    async def choice(self, ctx):
        if len(self.choice_list) > 0:
            game = random.choice(self.choice_list)
            await ctx.send('Get on up brothers and sisters, we\'re playing {}!'.format(game))
        else:
            await ctx.send('Hold on there, the games list is emptier than a discoteque after 1992!')
    
    async def choice_show(self, ctx):
        if len(self.choice_list) > 0:
            games_str = '\n> '.join(self.choice_list)
            await ctx.send('''Let's see what the DJ's got on those hot turntables tonight!
                              > {}'''.format(games_str))
        else:
            await ctx.send('This playlist\'s empty, my man!')

    async def choice_clear(self, ctx):
        self.choice_list = []
        await ctx.send('Cleared that games list like the dance floor after a party foul, oh!')
        asyncio.ensure_future(self._backup_data())


""" Bot commands """ 
@bot.command(description='Calling planet earth!')
async def ping(ctx):
    await disco_stu.ping(ctx)

@bot.command(description='Add a game to the list, baby!')
async def choice_add(ctx, *game: str):
    #TODO: make this support comma-separated lists
    game_title = ' '.join(game)
    await disco_stu.choice_add(ctx, game_title)

@bot.command(description='Strike that game from the list, man!')
async def choice_remove(ctx, *game: str):
    game_title = ' '.join(game)
    await disco_stu.choice_remove(ctx, game_title)

@bot.command(description='Pick a game at random, dancing queen!')
async def choice(ctx):
    await disco_stu.choice(ctx)

@bot.command(description='Flip through the pages of the jukebox brother!')
async def choice_show(ctx):
    await disco_stu.choice_show(ctx)

@bot.command(description='Start over like ABBA in 2008!')
async def choice_clear(ctx):
    await disco_stu.choice_clear(ctx)

""" Run the bot """
disco_stu = DiscoStu(backup_filename)

with open(r'config.yaml') as config_file:
    config = yaml.load(config_file, Loader=yaml.FullLoader)

token = config['token']

bot.run(token)

