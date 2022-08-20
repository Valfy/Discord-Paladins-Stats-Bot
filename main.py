# -- coding: utf-8 --

import discord
from discord.ext import commands
import environ
import pyrez
from pyrez.api import PaladinsAPI

from allowed_dicts import *
from vn_logger import VN_logger

VN_logger.PRINT_MESSAGES = True
VN_logger.LOGGING = True
VN_logger.LOG_LEVEL_CEILING = 0
if VN_logger.LOGGING:
    VN_logger.logging('RUN', f'Запуск логгера с параметрами FILENAME={VN_logger._FILENAME}.txt,'
                             f' PRINT_MESSAGES={VN_logger.PRINT_MESSAGES},'
                             f' LOGGING={VN_logger.LOGGING},'
                             f' LOG_LEVEL_CEILING={VN_logger.LOG_LEVEL_CEILING}')

env = environ.Env()
environ.Env.read_env()
CHANNELS = set()

try:
    VN_logger.logging('INFO', 'Шаг 1 из 5 Попытка прочитать channels.txt')
    with open('channels.txt', 'r') as reader:
        line_number = 0
        for line in reader:
            line_number += 1
            try:
                channel_to_add = int(line)
            except ValueError as error:
                if line != '\n':
                    VN_logger.logging('INFO', f'Пропуск линии №{line_number}')
                    VN_logger.logging('ERROR', error)
            else:
                CHANNELS.add(channel_to_add)
        reader.close()
except FileNotFoundError as error:
    VN_logger.logging('INFO', 'Шаг 2 из 5 Неудачная попытка прочитать channels.txt, создаю чистый')
    VN_logger.logging('ERROR', error)
    with open('channels.txt', 'w+') as create:
        create.write('')
        create.close()
else:
    VN_logger.logging('INFO', 'Шаг 2 из 5 Успешно прочитан channels.txt')

try:
    VN_logger.logging('INFO', 'Шаг 3 из 5 Попытка подключится к API')
    pAPI = PaladinsAPI(devId=env('DEV_ID'), authKey=env('AUTH_KEY'))
    pSession = pAPI._createSession()
except (pyrez.exceptions.InvalidArgument, pyrez.exceptions.IdOrAuthEmpty) as error:
    VN_logger.logging('INFO', 'Шаг 4 из 5 Неудачная попытка подключится к API')
    VN_logger.logging('ERROR', error)
    exit(0)
else:
    VN_logger.logging('INFO', 'Шаг 4 из 5 Успешное подключение к API')

bot = commands.Bot(command_prefix='vora!', status=discord.Status.dnd)

@bot.event
async def on_ready():
    VN_logger.logging('INFO', 'Шаг 5 из 5 Вора готова!')


@bot.command(pass_context=True)
async def add_channel(ctx, channelID):
    VN_logger.logging('COMMAND', f'Вызов команды add_channel, с параметрами {channelID}, от пользователя {ctx.author}')
    global CHANNELS
    if ctx.message.author.guild_permissions.administrator:
        try:
            channel_to_add = int(channelID)
        except Exception as error:
            VN_logger.logging('ERROR', error)
            VN_logger.logging('RESPONSE', f'Ответ пользователю {ctx.author}: Нужно число!')
            await ctx.send('Нужно число!')
        else:
            if channel_to_add in CHANNELS:
                VN_logger.logging('RESPONSE', f'Ответ пользователю {ctx.author}: Такой канал уже в списках!')
                await ctx.send('Такой канал уже в списках!')
            else:
                CHANNELS.add(channel_to_add)
                with open('channels.txt', 'a') as writer:
                    writer.write(f'{channel_to_add}\n')
                    writer.close()
                VN_logger.logging('RESPONSE', f'Ответ пользователю {ctx.author}: Понятно!')
                await ctx.send('Понятно!')
    else:
        VN_logger.logging('RESPONSE', f'Ответ пользователю {ctx.author}: У тебя нет прав!')
        await ctx.send('У тебя нет прав!')


@bot.command(pass_context=True)
async def delete_channel(ctx, channelID):
    VN_logger.logging('COMMAND', f'Вызов команды delete_channel, с параметрами {channelID}, от пользователя {ctx.author}')
    global CHANNELS
    if ctx.message.author.guild_permissions.administrator:
        try:
            channel_to_add = int(channelID)
        except Exception as error:
            VN_logger.logging('ERROR', error)
            VN_logger.logging('RESPONSE', f'Ответ пользователю {ctx.author}: Нужно число!')
            await ctx.send('Нужно число!')
        else:
            if channel_to_add in CHANNELS:
                CHANNELS.remove(channel_to_add)
                with open('channels.txt', 'w') as writer:
                    for channel in CHANNELS:
                        writer.write(f'{channel}\n')
                    writer.close()
                VN_logger.logging('RESPONSE', f'Ответ пользователю {ctx.author}: Канал успешно удалён!')
                await ctx.send('Канал успешно удалён!')
            else:
                VN_logger.logging('RESPONSE', f'Ответ пользователю {ctx.author}: Такого канала нет в списках!')
                await ctx.send('Такого канала нет в списках!')
    else:
        VN_logger.logging('RESPONSE', f'Ответ пользователю {ctx.author}: У тебя нет прав!')
        await ctx.send('У тебя нет прав!')


@bot.command(pass_context=True)
async def return_channels(ctx):
    VN_logger.logging('COMMAND', f'Вызов команды return_channel, от пользователя {ctx.author}')
    global CHANNELS
    if ctx.message.author.guild_permissions.administrator:
        VN_logger.logging('RESPONSE', f'Ответ пользователю {ctx.author}: Список каналов: {list(CHANNELS)}')
        await ctx.send(f'Список каналов: {list(CHANNELS)}')
    else:
        VN_logger.logging('RESPONSE', f'Ответ пользователю {ctx.author}: У тебя нет прав!')
        await ctx.send('У тебя нет прав!')


@bot.command(pass_context=True)
async def mh(ctx, playername, matches=None):
    VN_logger.logging('COMMAND', f'Вызов команды mh, с параметрами {playername}, {matches}, от пользователя {ctx.author}')
    if ctx.channel.id in CHANNELS:
        if matches is None:
            matches = 5
        try:
            matches = int(matches)
        except ValueError:
            VN_logger.logging('RESPONSE', f'Ответ пользователю {ctx.author}: Нужно указать количество матчей в виде цифр от 1 до 12')
            await ctx.send('Нужно указать количество матчей в виде цифр от 1 до 12')
        else:
            if matches > 12:
                matches = 12
            if matches < 1:
                matches = 5
            try:
                p_getplayerid = pAPI.getPlayerId(playerName=playername, portalId=None, xboxOrSwitch=False)[0]
                p_playerid = str(p_getplayerid["player_id"])
            except IndexError:
                VN_logger.logging('RESPONSE', f'Ответ пользователю {ctx.author}: Игрок с таким именем не найден!')
                await ctx.send('Игрок с таким именем не найден!')
            else:
                try:
                    p_mh = pAPI.getMatchHistory(playerId=p_playerid)
                except:
                    VN_logger.collect_traceback()
                    VN_logger.logging('RESPONSE', f'Ответ пользователю {ctx.author}: Ошибочка!')
                    await ctx.send('Ошибочка!')
                else:
                    p_matches = p_mh[:matches]
                    embed = discord.Embed(title=f'Последние матчи игрока {playername}:',
                                          color=0xdd2266)
                    for match in p_matches:
                        title_to_send, value_to_send = "", ""
                        if match["Win_Status"] == "Win":
                            title_to_send += "🟦 (Победа) "
                        else:
                            title_to_send += "🟥 (Поражение) "
                        title_to_send += f'ID: {match["Match"]}'

                        value_to_send += f'Чемпион: {champions_ru_names[match["Champion"]]} 🔹 ' \
                            if match["Champion"] in champions_ru_names else f'Чемпион: {match["Champion"]} 🔹 '

                        map_name, map_mode = '', ''
                        for map in maps_ru_names:
                            if map in match["Map_Game"]:
                                map_name += maps_ru_names[map] + ' '
                        if map_name != '':
                            for mode in gamemode_ru_names:
                                if mode in match["Map_Game"]:
                                    map_mode = gamemode_ru_names[mode]
                        if map_mode == '':
                            map_mode = '(Казуал)'
                        if map_name != '':
                            value_to_send += f'На карте: {map_name}{map_mode} \n'
                        else:
                            value_to_send += f'в {match["Map_Game"]} \n'

                        value_to_send += f'{match["Match_Time"]}'
                        embed.add_field(name=title_to_send, value=value_to_send, inline=False)
                    VN_logger.logging('RESPONSE', f'Ответ пользователю {ctx.author}: embed*')
                    await ctx.send(embed=embed)


@bot.command(pass_context=True)
async def mi(ctx, matchid, theme='standart'):
    VN_logger.logging('COMMAND', f'Вызов команды mi, с параметрами {matchid}, {theme}, от пользователя {ctx.author}')
    if ctx.channel.id in CHANNELS:
        try:
            p_mi = pAPI.getMatch(matchId=matchid)
        except:
            VN_logger.collect_traceback()
            VN_logger.logging('RESPONSE', f'Ответ пользователю {ctx.author}: Ошибочка!')
            await ctx.send('Ошибочка!')
        else:
            map_name, map_mode = '', ''
            for map in maps_ru_names:
                if map in p_mi[0]["Map_Game"]:
                    map_name += maps_ru_names[map] + ' '
            if map_name != '':
                for mode in gamemode_ru_names:
                    if mode in p_mi[0]["Map_Game"]:
                        map_mode = gamemode_ru_names[mode]
            if map_mode == '':
                map_mode = '(Казуал)'
            if map_name != '':
                embed = discord.Embed(title=f'Матч {matchid} на карте {map_name}{map_mode}: \n',
                                      color=0xdd2266)
            else:
                embed = discord.Embed(title=f'Матч {matchid} в {p_mi[0]["Map_Game"]}:',
                                      color=0xdd2266)
            count = 0
            for paladin in p_mi:
                title_to_send, value_to_send = "", ""
                count += 1
                if paladin["Win_Status"] == "Winner":
                    title_to_send += "🔵 "
                else:
                    title_to_send += "🔴 "
                if paladin["playerName"] != "":
                    title_to_send += f'{paladin["playerName"]} на '
                else:
                    title_to_send += "??? на "
                title_to_send += f'{champions_ru_names[paladin["Reference_Name"]]}' \
                    if paladin["Reference_Name"] in champions_ru_names else f'{paladin["Reference_Name"]}'
                if theme == 'iconic':
                    value_to_send += "☠: " + str(paladin["Kills_Player"]) + '/' + str(paladin["Deaths"]) + \
                              '/' + str(paladin["Assists"]) + \
                              "  ⚔: " + str(paladin["Damage_Player"]) + \
                              "  🩹: " + str(paladin["Healing"]) + \
                              "  🛡: " + str(paladin["Damage_Mitigated"]) + \
                              "  🩸: " + str(paladin["Healing_Player_Self"])
                else:
                    value_to_send += "KDA: " + str(paladin["Kills_Player"]) + '/' + str(paladin["Deaths"]) + \
                              '/' + str(paladin["Assists"]) + \
                              " 🔹 Урон: " + str(paladin["Damage_Player"]) + \
                              " 🔹 Хил: " + str(paladin["Healing"]) + \
                              " 🔹 Щит: " + str(paladin["Damage_Mitigated"]) + \
                              " 🔹 Самолечение: " + str(paladin["Healing_Player_Self"])
                embed.add_field(name=title_to_send, value=value_to_send, inline=False)
            VN_logger.logging('RESPONSE', f'Ответ пользователю {ctx.author}: embed*')
            await ctx.send(embed=embed)


@bot.command(pass_context=True)
async def profile(ctx, playername):
    VN_logger.logging('COMMAND', f'Вызов команды profile, с параметрами {playername}, от пользователя {ctx.author}')
    if ctx.channel.id in CHANNELS:
        try:
            p_getplayer = pAPI.getPlayer(player=playername)
            p_champdata = pAPI.getChampionRanks(playerId=p_getplayer["Id"])
            p_status = pAPI.getPlayerStatus(playerId=p_getplayer["Id"])
        except:
            VN_logger.collect_traceback()
            VN_logger.logging('RESPONSE', f'Ответ пользователю {ctx.author}: Ошибочка!')
            await ctx.send('Ошибочка!')
        else:
            p_rank = ranks_ru_names[max(p_getplayer["Tier_RankedKBM"], p_getplayer["Tier_RankedController"])]
            embed = discord.Embed(title=f'Профиль игрока {playername} \n',
                                  description=f'Уровень **{p_getplayer["Level"]}** \n'
                                              f'Часы в игре **{p_getplayer["HoursPlayed"]}** \n'
                                              f'Звание **{p_getplayer["Title"]}** \n'
                                              f'Ранг **{p_rank}** \n',
                                  color=0xdd2266)
            embed.set_thumbnail(url=p_getplayer["AvatarURL"] if p_getplayer["AvatarURL"] else 'https://hirez-api-docs.herokuapp.com/paladins/avatar/0')
            embed.add_field(name='Статус' if p_status["status"] else f'Статус (был в сети {p_getplayer["Last_Login_Datetime"]})',
                            value=status_messages[p_status["status"]],
                            inline=False)
            value_to_send = ''
            for champion in p_champdata[:10]:
                value_to_send += '**'
                value_to_send += champions_ru_names[champion["champion"]] \
                            if champion["champion"] in champions_ru_names else champion["champion"]
                value_to_send += f'** ({champion["Rank"]}) 🔹 Сыграно матчей ' \
                                 f'{champion["Wins"] + champion["Losses"]} из них выиграно {champion["Wins"]} \n'
            embed.add_field(name='Топ чемпионов:',
                            value=value_to_send,
                            inline=False)
            VN_logger.logging('RESPONSE', f'Ответ пользователю {ctx.author}: embed*')
            await ctx.send(embed=embed)


TOKEN = env('VORA_TOKEN')
bot.run(TOKEN)
