import discord
from discord.ext import commands
from discord import app_commands
import random
from datetime import datetime, timedelta, timezone
import os

ROLE_DISTRIBUTION = {
    "人狼": 3,
    "狂人": 1,
    "占い師": 1,
    "霊能者": 1,
    "騎士": 1,
    "村人": 6
}

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # グループDM作成のため
client = discord.Client(intents=intents)

# 日本時間のタイムゾーンを設定
JST = timezone(timedelta(hours=+9))

bot = commands.Bot(command_prefix="/", intents=intents)

# 疎通確認用プレイヤー名
TEST_PLAYERS = [f"プレイヤー{i}" for i in range(1, 14)]

def assign_roles(players):
    roles = []
    for role, count in ROLE_DISTRIBUTION.items():
        roles.extend([role] * count)
    random.shuffle(roles)
    return dict(zip(players, roles))

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_disconnect():
    print('Bot has been disconnected, trying to reconnect...')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("!配役"):
        # コマンドを実行したユーザーが指定した13人のメンションを抽出
        mentions = message.mentions
        if len(mentions) != 13:
            await message.channel.send("13人をメンションしてください。")
            return
        
        # 現在の時間を取得
        current_time = datetime.now(JST).strftime('%Y-%m-%d %H:%M:%S')

        # プレイヤーに役職を割り当て
        assigned_roles = assign_roles(mentions)

        # 占い師にランダム白結果を送る
        seer = None
        seer_white = None
        for member, role in assigned_roles.items():
            if role == "占い師":
                seer = member
                non_werewolves = [m for m, r in assigned_roles.items() if r not in ["人狼", "占い師"]]
                seer_white = random.choice(non_werewolves)
                break

        # 人狼リスト
        werewolves = [member for member, role in assigned_roles.items() if role == "人狼"]

        # 各プレイヤーにDMで配役を送信
        for member, role in assigned_roles.items():
            message_text = f'配役時間: {current_time}\nあなたの役職は {role} です。'
            if member == seer and seer_white:
                message_text += f'\nランダム白結果: {seer_white.display_name}'
            elif role == "人狼":
                other_werewolves = [m.display_name for m in werewolves if m != member]
                message_text += f'\nあなたの相方は: {", ".join(other_werewolves)}'
                # 内通グループDM作成のメッセージ追加
                gm_mention = message.author.mention
                message_text += f'\n内通グループDMを作成します。GMをフレンド追加してお待ちください。\nGM: {gm_mention}'
        
            # 末尾にライン追加
            message_text += '\n-------------------------------'

            try:
                await member.send(message_text)
            except Exception as e:
                await message.channel.send(f'{member.display_name} にDMを送信できませんでした。')

        # 人狼3人のグループDMを作成
        if len(werewolves) == 3:
            group_dm = await client.create_dm(werewolves[0])
            await group_dm.send(f'{werewolves[1].display_name}, {werewolves[2].display_name} があなたの仲間です。\nあなたたちは人狼です。')
        
        # コマンド実行者へのメッセージに人狼プレイヤーへの指示を追加
        werewolf_names = "\n".join([f'{werewolf.display_name} : {werewolf.mention}' for werewolf in werewolves])
        gm_message = f'人狼3名をフレンド追加の上、グループDMを作成してください。\n{werewolf_names}'

        # 配役結果とランダム白結果をコマンド実行者に送信
        result_message = "\n".join([f"{member.display_name}: {role}" for member, role in assigned_roles.items()])
        if seer_white:
            result_message += f"\n\n占い師のランダム白結果: {seer_white.display_name}"
        await message.author.send(f'配役結果:\n{result_message}\n\n{gm_message}')
        await message.channel.send("配役が完了しました。DMを確認してください。")

    if message.content.startswith('/テスト配役'):
        # 疎通確認用のプレイヤー名を生成
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        assigned_roles = assign_roles(TEST_PLAYERS)
        result_message = '\n'.join([f'{player}: {role}' for player, role in assigned_roles.items()])
        # 配役結果をコマンドを打った人に送信
        await message.channel.send(f'配役時間: {current_time}\nテスト配役結果:\n{result_message}\n-------------------------')

@bot.tree.command(name="人狼内通会話")
@app_commands.describe(users="会話するユーザーを選んでください")
async def secret_conversation(interaction: discord.Interaction, users: str):
    # 選択されたユーザーIDを取得
    user_ids = [int(user_id.strip()) for user_id in users.split(",")]
    
    # DMグループの作成
    group_dm = await interaction.user.create_dm()
    for user_id in user_ids:
        user = bot.get_user(user_id)
        if user:
            await group_dm.add_recipients(user)
    
    # 成功メッセージを送信
    await interaction.response.send_message("指定されたユーザーとのグループDMを作成しました。")

    # グループDMにウェルカムメッセージを送信
    await group_dm.send("このグループは人狼の内通会話専用です。")

client.run(os.getenv('DISCORD_TOKEN'))
