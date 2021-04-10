import random
import asyncio
import aiofiles
import os
import json
import yaml 

import discord
from discord.ext import commands

""" Globals """
backup_filename = 'stu_data.json'

intents = discord.Intents.default()
intents.members = True # enable member inspection
bot = commands.Bot(command_prefix='>', intents=intents)

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

    async def choice_add(self, ctx, game_titles):
        if len(game_titles) == 0:
            await ctx.send("Oh! You didn't include any games man!")
            return
        
        for game_title in game_titles:
            if game_title not in self.choice_list:
                self.choice_list.append(game_title)
        
        if len(game_titles) == 1:
            pronoun = game_titles[0]
            game_string = ""
        elif len(game_titles) > 1:
            pronoun = "these"
            game_string = "\n> " + self._generate_games_str(game_titles)
        
        await ctx.send('Oh! Added {0} to the games list, yeah!{1}'.format(pronoun, game_string))
        asyncio.ensure_future(self._backup_data())

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
            await ctx.send('Hold on there, the games list is emptier than a discotheque after 1992!')
    
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
    
    def _generate_games_str(self, games_list):
        return '\n> '.join(games_list)


    async def user_add(self, ctx, games):
        id_str = str(ctx.author.id) # saving id as str instead of int makes backing up easier
        if id_str in self.user_games_dict:
            msg_format = "Reconfigured the user *{0}* with the following games:\n> {1}".format(ctx.author.name, self._generate_games_str(games))
        else:
            msg_format = "Added the user *{0} with the following games:\n> {1}".format(ctx.author.name, self._generate_games_str(games))
        self.user_games_dict[id_str] = games
        await ctx.send(msg_format)
        asyncio.ensure_future(self._backup_data())

    async def user_remove(self, ctx):
        if ctx.author.id in self.user_games_dict:
            msg = "*{}*? Their bad vibes are off the dance floor!".format(ctx.author)
            del self.user_games_dict[ctx.author.id]
        else: 
            msg = "*{}* ain't in the discoteque, baby!".format(ctx.author)

        await ctx.send(msg)
        asyncio.ensure_future(self._backup_data()) #TODO: could make this into a decorated wrapper 

    def _get_user_id_for_user_list(self, user_names, members):
        ids = []
        for user in user_names:
            # try to find command-supplied user in members list
            # if this weren't a tiny bot I'd probably implement a smarter search
            found = False
            for member in members:
                if member.name.lower() == user.lower() or (member.nick and member.nick.lower() == user.lower()):
                    ids.append(str(member.id))
                    found = True
                    break
            if not found:
                raise KeyError('User not found')
        return ids
    
    def _get_common_games(self, user_ids):
        if not user_ids:
            selected_games = self.user_games_dict.values()
        else:
            selected_games = [self.user_games_dict[u_id] for u_id in user_ids]
        
        common_games = None
        for games in selected_games:
            if common_games:
                common_games &= set(games)
            else:
                common_games = set(games)

        return common_games

    async def games(self, ctx, users):
        if users:
            try:
                user_ids = self._get_user_id_for_user_list(users, ctx.guild.members)
            except:
                await ctx.send("I wasn't able to find one of your supplied users, man!")
                return
        else:
            user_ids = None
        
        try:
            common_games = self._get_common_games(user_ids)
        except:
            await ctx.send("One or more users don't have games configured!")
            return
        
        users_str = "Everybody has " if not users else "Requested groovers have "
        
        if common_games:
            msg = "{0} the following jams in common: \n> {1}".format(users_str, self._generate_games_str(list(common_games)))
        else:
            msg = "No games in common, not cool!"

        await ctx.send(msg)

    async def choose_game(self, ctx, users):
        if users:
            try:
                user_ids = self._get_user_id_for_user_list(users, ctx.guild.members)
            except:
                await ctx.send("I wasn't able to find one of your supplied users, man!")
                return
        else:
            user_ids = None

        try:
            common_games = self._get_common_games(user_ids)
        except:
            await ctx.send("One or more users don't have games configured!")
            return
        
        if common_games:
            msg = "You cool cats are playing {}".format(random.choice(list(common_games)))
        else:
            msg = "No games in common!"

        await ctx.send(msg)

""" utilities """
def parse_comma_list(args_tuple):
    # bot assumes space-separated args but game names can have spaces in them
    # so we have to re-join the args then split how we want
    args_str = ' '.join(args_tuple)
    retlist = [g.strip() for g in args_str.split(',')]
    if len(retlist) == 1 and retlist[0] == "":
        retlist = []
    return retlist

""" Bot commands """ 
@bot.command(description='Calling planet earth!')
async def ping(ctx):
    await disco_stu.ping(ctx)

@bot.command(description='Add a game to the list, baby!')
async def choice_add(ctx, *game: str):
    game_title = parse_comma_list(game)
    await disco_stu.choice_add(ctx, game_title)

@bot.command(description='Strike that game from the list, man!')
async def choice_remove(ctx, *game: str):
    game_title = ' '.join(game)
    await disco_stu.choice_remove(ctx, game_title)

@bot.command(description='Pick a game at random, dancing queen!')
async def choice(ctx):
    #TODO: have choice optionally take a list and choose from that one
    await disco_stu.choice(ctx)

@bot.command(description='Flip through the pages of the jukebox brother!')
async def choice_show(ctx):
    await disco_stu.choice_show(ctx)

@bot.command(description='Start over like ABBA in 2008!')
async def choice_clear(ctx):
    await disco_stu.choice_clear(ctx)

@bot.command(description='Add a dancer to the party!')
async def user_add(ctx, *game: str):
    games = parse_comma_list(game)
    await disco_stu.user_add(ctx, games)

@bot.command(description='Kick that dancer off the floor!')
async def user_remove(ctx):
    await disco_stu.user_remove(ctx)

@bot.command(description='Get a list of games in common baby!')
async def games(ctx, *user: str):
    if not user or user == 'all':
        users = None
    else:
        users = parse_comma_list(user)
    await disco_stu.games(ctx, users)

@bot.command(description='Pick a game from common games')
async def choose_game(ctx, *user: str):
    if not user or user == 'all':
        users = None
    else:
        users = parse_comma_list(user)
    await disco_stu.choose_game(ctx, users)

""" Run the bot """
disco_stu = DiscoStu(backup_filename)

with open(r'config.yaml') as config_file:
    config = yaml.load(config_file, Loader=yaml.FullLoader)

token = config['token']

bot.run(token)

