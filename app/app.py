import random
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

# Discord botの初期設定
TOKEN = os.getenv("DISCORD_TOKEN")

# 必要なインテントを有効にする
intents = discord.Intents.default()
intents.members = True  # メンバーのインテントを有効にする
intents.presences = True  # プレゼンスのインテントを有効にする

bot = commands.Bot(command_prefix='!', intents=intents)

# アルティメット人狼の配役
roles = ['人狼', '人狼', '人狼', '狂人', '占い師', '霊能者', '騎士', '村人', '村人', '村人', '村人', '村人', '村人']

@bot.command(name='start_game')
async def start_game(ctx, *members: discord.Member):
    if len(members) != 13:
        await ctx.send('13人のメンバーを指定してください。')
        return

    # 配役をランダムにシャッフル
    random.shuffle(roles)
    
    for member, role in zip(members, roles):
        try:
            await member.send(f'あなたの役職は: {role}')
        except discord.Forbidden:
            await ctx.send(f'{member.mention} にメッセージを送信できませんでした。')
    
    await ctx.send('ゲームの配役を送信しました。')

bot.run(TOKEN)
