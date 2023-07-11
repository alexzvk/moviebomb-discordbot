import discord
import time
import asyncio
import secret # put your bot token in a file called secret.py, name the token BOT_TOKEN

intents = discord.Intents.default()
intents.message_content = True

class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # an attribute we can access from our task
        self.timer_message = None
        self.game_start = None
        self.turns = 0

    async def on_ready(self):
        print(f'We have logged in as {client.user}')


    async def on_message(self, message):
        if message.author == client.user:
            return
        if self.timer_message:
            await self.timer_message.delete()
        if self.game_start is None:
            self.game_start = time.time()
        
        remaining_time = int(time.time()) + 86400 # current time plus 24 hours in seconds
        self.timer_message = await message.channel.send(f'Game will end <t:{remaining_time}:R>')

        self.turns += 1

        try:
            await client.wait_for('message', timeout=86400)
        except asyncio.TimeoutError:
            time_elapsed = time.time() - self.game_start
            time_elapsed_string = f'{int(time_elapsed / 86400)} days, {int(time_elapsed % 86400 / 3600)} hours, {int(time_elapsed % 86400 % 3600 / 60)} minutes, and {int(time_elapsed % 86400 % 3600 % 60)} seconds'
            total_turns = self.turns
            self.turns = 0
            self.game_start = None
            return await message.channel.send(f'Game over!\nThis game lasted {total_turns} turns over {time_elapsed_string}.')


client = MyClient(intents=intents)
client.run(secret.BOT_TOKEN)
        