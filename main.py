import discord
import time
import asyncio
import secret # put your bot token in a file called secret.py, name the token BOT_TOKEN
import requests
import json

intents = discord.Intents.default()
intents.message_content = True

class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timer_message = None
        self.game_start = None
        self.turns = 0
        self.list_of_movies = []
        self.current_movie = -1
        self.headers = {
            "accept": "application/json",
            "Authorization": secret.MOVIE_TOKEN
        }
        self.previous_player = None
        with open("high_score.txt", "r") as f:
            self.high_score = int(f.read())


    async def on_ready(self):
        print(f'We have logged in as {client.user}')


    async def on_message(self, message):
        if message.author == client.user: # don't consider messages the bot sends
            return
        if not self.user.mentioned_in(message) or message.mention_everyone is True: # don't consider messages where the bot is not @ed
            return
        if self.previous_player == message.author: # don't allow the same person to make two plays in a row
            return await message.channel.send("Sorry, the same person cannot make two plays in a row!")
        
        message_content = message.content.replace(f'<@{secret.BOT_USERNAME}>', '') # remove the @ing of the bot from the message content when looking things up
        remaining_time = int(time.time()) + 86400 # current time plus 24 hours in seconds
        # first turn special logic, must start with a movie
        if self.turns == 0:
            url = f'https://api.themoviedb.org/3/search/movie?query={message_content}&include_adult=false&language=en-US&page=1'

            response = requests.get(url, headers=self.headers)
            try:
                self.current_movie = json.loads(response.text)['results'][0]['id'] # get first movie id from search (too much work to iterate through all search results)
                self.timer_message = await message.channel.send(f'Movie "{json.loads(response.text)["results"][0]["title"]}" is valid.\nCurrently on turn 1.\nGame will end <t:{remaining_time}:R>')
            except:
                return await message.channel.send("Sorry, I couldn't find that movie.")
        
            if self.game_start is None:
                self.game_start = time.time() # when we finish the first turn, set the game start time for counting the length of the game at the end
        # odd numbered turns we check if an actor is in a particular movie
        elif self.turns % 2 == 1:
            actor_name, movies_actor_is_in = self.verify_actor_in_movie(message_content, self.current_movie)
            if actor_name == "-1":
                return await message.channel.send("That actor was not found to act in the previous movie.")
            elif actor_name == "-2":
                return await message.channel.send("Sorry, I couldn't find that actor.")
            if self.timer_message:
                await self.timer_message.delete()
            self.list_of_movies = movies_actor_is_in
            self.timer_message = await message.channel.send(f'Actor "{actor_name}" is valid.\nCurrently on turn {self.turns + 1}.\nGame will end <t:{remaining_time}:R>')
        # even numbered turns we check if movie has particular actor
        else:
            movie_code, movie_name = self.verify_movie_has_actor(message_content, self.list_of_movies)
            if movie_code == -1:
                return await message.channel.send("That movie was not found to include the previous actor.")
            elif movie_code == -2:
                return await message.channel.send("Sorry, I couldn't find that movie.")
            if self.timer_message:
                await self.timer_message.delete()
            self.current_movie = movie_code
            self.timer_message = await message.channel.send(f'Movie "{movie_name}" is valid.\nCurrently on turn {self.turns + 1}.\nGame will end <t:{remaining_time}:R>')

        # only on a successful turn do we increment the turn and bar the player from making two moves in a row
        self.turns += 1
        self.previous_player = message.author

        try:
            await client.wait_for('message', timeout=86400) # wait one day after a successful play
        except asyncio.TimeoutError: # if there are no plays and the timer runs out, end the game
            # delete timer message
            if self.timer_message:
                await self.timer_message.delete()
                self.timer_message = None
            # calculate and write out how much time in days, hours, minutes, and seconds the game took
            time_elapsed = time.time() - self.game_start
            time_elapsed_string = f'{int(time_elapsed / 86400)} days, {int(time_elapsed % 86400 / 3600)} hours, {int(time_elapsed % 86400 % 3600 / 60)} minutes, and {int(time_elapsed % 86400 % 3600 % 60)} seconds'
            # if game took more turns then high score, update high score
            total_turns = self.turns
            if total_turns > self.high_score:
                self.high_score = total_turns
                with open("high_score.txt", "w") as f:
                    f.write(str(self.high_score))
            # reinitialize all variables, send game end message
            self.turns = 0
            self.game_start = None
            self.list_of_movies = []
            self.current_movie = -1
            self.previous_player = None
            return await message.channel.send(f'Game over!\nThis game lasted {total_turns} turns over {time_elapsed_string}.\nThe high score is {self.high_score} turns.\n@ me with a movie to play again!')
        
    
    def verify_actor_in_movie(self, actor_string, movie_id):
        # first make a call to look up the actor and get the actor id
        url = f'https://api.themoviedb.org/3/search/person?query={actor_string}&include_adult=false&language=en-US&page=1'

        response = requests.get(url, headers=self.headers)

        try:
            results_dict = json.loads(response.text)['results'][0] # use the first result for an actor (too lazy rn to loop through all of them)
        except:
            return "-2", []

        actor_name = results_dict['name']
        actor_id = results_dict["id"]

        # then look up all movies the actor is in by actor id
        url = f'https://api.themoviedb.org/3/person/{actor_id}/movie_credits?language=en-US'

        response = requests.get(url, headers=self.headers)

        try:
            acted_in_movies_list = json.loads(response.text)['cast']
        except:
            return "-2", [] # didn't find the actor

        found = False

        # loop through all of the movies and get a list of movie ids the actor is in. If that includes the movie id currently in play, return the list
        # keep the list of movies the actor is in so the next movie listed we can cross-reference with said list
        movies_list = []
        for movie in acted_in_movies_list:
            movies_list.append(movie['id'])
            if movie_id == movie['id']:
                found = True
        
        if found:
            return actor_name, movies_list
        
        return "-1", [] # actor not found to act


    def verify_movie_has_actor(self, movie_string, movies_list):
        url = f'https://api.themoviedb.org/3/search/movie?query={movie_string}&include_adult=false&language=en-US&page=1'

        response = requests.get(url, headers=self.headers)
        # when a movie is named, look it up and check if the id is in the list of movies that the previously named actor has acted in
        # if that movie is found, return the movie id for checking in actor's acted movies later
        try:
            for movie in json.loads(response.text)['results']: # check ALL the search results for the named movie, since in my testing this search capacity is poor
                movie_id = movie['id']
                movie_title = movie['title']
                if movie_id in movies_list:
                    return movie_id, movie_title
        except:
            return -2, "" # didn't find the movie
        return -1, "" # movie not found to have actor



client = MyClient(intents=intents)
client.run(secret.TEST_BOT_TOKEN)
        