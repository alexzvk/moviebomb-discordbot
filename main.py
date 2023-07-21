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
        #self.valid_play = asyncio.Event()
        self.headers = {
            "accept": "application/json",
            "Authorization": secret.MOVIE_TOKEN
        }
        self.previous_player = None
        with open("high_score.txt", "r") as f:
            self.high_score = int(f.read())
        self.tom_hanks_counter = 0
        self.tom_hanks_movies = [13, 497, 568, 591, 594, 857, 858, 862, 10193, 2280, 2565, 2619, 10466, 4147, 10905, 30172, 5516, 5707, 11287, 6538, 6951, 8358, 11974, 12309, 9489, 9586, 9591, 9800, 27348, 13448, 35866, 29968, 64685, 19259, 82424, 77887, 59861, 109424, 170039, 83542, 296098, 207932, 270010, 363676, 374164, 377229, 301528, 426128, 414792, 5255, 121100, 456703, 478639, 224355, 863, 516486, 522402, 567649, 581032, 31107, 638302, 785930, 885058, 923252, 937278, 940139, 1038873, 1061818, 1084244, 640, 10023, 40820, 140823, 130925, 173458, 339988, 356325, 406122, 252451, 446354, 464729, 501907, 325450, 614934, 729031, 532639, 127850, 213121, 237353, 256835, 43714, 550600, 504561, 606078, 740985, 747188, 1071583, 16279, 56235, 380994, 471198, 712062, 181007, 510173, 65262, 467062, 459682, 720203, 989517, 141498, 315085, 305642, 1111122, 1125624, 453422, 698229, 705899, 1016902, 37641, 454330, 473544, 711704, 253639, 962192, 574379, 87061, 32562, 35, 40196, 966435, 838219, 1150794, 15302, 979163, 1113682, 269535, 298859, 1033548, 920, 558912, 773655, 32694, 28236, 881931, 126314, 20763, 1065395, 653610, 42348, 285783, 316067, 37757, 47813]
        self.movie_years = set([])
        self.chris_counter = 0
        self.chrises = [62064, 73457, 74568, 16828]
        self.movies_played_this_game = []
        self.actors_played_this_game = []
        self.horror_movie_counter = 0
        self.tilda_swinton_movies = [20308, 7351, 24936, 9300, 41110, 41801, 38987, 81540, 83401, 84012, 96484, 106304, 110838, 112477, 146140, 255500, 261369, 324807, 338630, 341240, 15030, 71859, 428702, 99453, 413786, 387426, 502386, 511819, 518852, 554794, 556694, 558398, 566038, 580728, 586745, 588994, 565249, 41970, 288388, 542955, 671577, 790867, 435353, 860004, 881366, 901565, 346080, 894319, 1031459, 498357, 1139231, 237, 1546, 31262, 8284, 41488, 41947, 42739, 152603, 400618, 230915, 245324, 262588, 291060, 333032, 360735, 361292, 369328, 445666, 497425, 499805, 665774, 720725, 113102, 852247, 800158, 4566, 4975, 43654, 94794, 140527, 473019, 535581, 542178, 615902, 844176, 999041, 1059301, 308, 1907, 2757, 58937, 110415, 214170, 520900, 526946, 411, 4944, 202872, 222962, 555604, 722902, 747188, 20537, 270487, 284052, 157834, 83666, 561, 1903, 10140, 1049516, 370648, 4922, 271718, 582959, 473021, 197393, 25832, 318042, 120467, 399174, 471208, 299534, 354287, 2454, 473033]


    async def on_ready(self):
        print(f'We have logged in as {client.user}')

    async def on_disconnect():
        print('[main.py on_disconnect()] experienced a disconnect')

    async def on_resumed():
        print('[main.py on_resumed()] experienced a resume')


    async def on_message(self, message):
        #self.valid_play = False
        message_content = message.content.replace(f'<@{secret.TEST_BOT_USERNAME}>', '') # remove the @ing of the bot from the message content when looking things up
        remaining_time = int(time.time()) + 86400 # current time plus 24 hours in seconds
        if message.author == client.user: # don't consider messages the bot sends
            if self.turns == 0:
                return
        elif not self.user.mentioned_in(message) or message.mention_everyone is True: # don't consider messages where the bot is not @ed
            if self.turns == 0:
                return
        #elif self.previous_player == message.author: # don't allow the same person to make two plays in a row
        #    if self.turns == 0:
        #        return
        #    await message.channel.send("Sorry, the same person cannot make two plays in a row!")

        

        # first turn special logic, must start with a movie
        elif self.turns == 0:
            url = f'https://api.themoviedb.org/3/search/movie?query={message_content}&include_adult=false&language=en-US&page=1'

            response = requests.get(url, headers=self.headers)
            try:
                self.current_movie = json.loads(response.text)['results'][0]['id'] # get first movie id from search (too much work to iterate through all search results)
                self.timer_message = await message.channel.send(f'Movie "{json.loads(response.text)["results"][0]["title"]}" is valid.\nCurrently on turn 1.\nGame will end <t:{remaining_time}:R>')
            except:
                return await message.channel.send("Sorry, I couldn't find that movie.")
        
            if self.game_start is None:
                self.game_start = time.time() # when we finish the first turn, set the game start time for counting the length of the game at the end
            self.turns += 1
            self.previous_player = message.author
            self.dispatch('valid_play')
            self.movies_played_this_game.append(self.current_movie)
            await self.achievement_checker(message, self.current_movie)

        # odd numbered turns we check if an actor is in a particular movie
        elif self.turns % 2 == 1:
            actor_name, movies_actor_is_in = self.verify_actor_in_movie(message_content, self.current_movie)
            if actor_name == "-1":
                await message.channel.send("That actor was not found to act in the previous movie.")
            elif actor_name == "-2":
                await message.channel.send("Sorry, I couldn't find that actor.")
            elif actor_name == "-3":
                await message.channel.send("Sorry, that actor has already been used this game.")
            else:
                if self.timer_message:
                    await self.timer_message.delete()
                    #self.timer_message = None
                self.list_of_movies = movies_actor_is_in
                self.timer_message = await message.channel.send(f'Actor "{actor_name}" is valid.\nCurrently on turn {self.turns + 1}.\nGame will end <t:{remaining_time}:R>')
                # only on a successful turn do we increment the turn and bar the player from making two moves in a row
                self.turns += 1
                self.previous_player = message.author
                self.dispatch('valid_play')
                await self.achievement_checker(message, -1)
        # even numbered turns we check if movie has particular actor
        else:
            movie_code, movie_name = self.verify_movie_has_actor(message_content, self.list_of_movies)
            if movie_code == -1:
                await message.channel.send("That movie was not found to include the previous actor.")
            elif movie_code == -2:
                await message.channel.send("Sorry, I couldn't find that movie.")
            elif movie_code == -3:
                await message.channel.send("Sorry, that movie has already been used this game.")
            else:
                if self.timer_message:
                    await self.timer_message.delete()
                    #self.timer_message = None
                self.current_movie = movie_code
                self.timer_message = await message.channel.send(f'Movie "{movie_name}" is valid.\nCurrently on turn {self.turns + 1}.\nGame will end <t:{remaining_time}:R>')
                # only on a successful turn do we increment the turn and bar the player from making two moves in a row
                self.turns += 1
                self.previous_player = message.author
                self.dispatch('valid_play')
                await self.achievement_checker(message, movie_code)
        await self.timer(message)
    
    async def timer(self, message):
        #def check(m):
        #    return self.valid_play
        #self.valid_play.clear()
        try:
            await self.wait_for('valid_play', timeout=86400) # wait one day after a successful play
        except asyncio.TimeoutError: # if there are no plays and the timer runs out, end the game
            if not self.game_start:
                return
            # delete timer message
            # if we already have deleted the message previously, we will try this and throw an error
            # this prevents invalid plays from extending the timer
            try:
                if self.timer_message:
                    await self.timer_message.delete()
                    self.timer_message = None
            except:
                return

            # calculate and write out how much time in days, hours, minutes, and seconds the game took

            time_elapsed = int(time.time()) - int(self.game_start)
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
            self.tom_hanks_counter = 0
            self.tom_hanks_movies = [13, 497, 568, 591, 594, 857, 858, 862, 10193, 2280, 2565, 2619, 10466, 4147, 10905, 30172, 5516, 5707, 11287, 6538, 6951, 8358, 11974, 12309, 9489, 9586, 9591, 9800, 27348, 13448, 35866, 29968, 64685, 19259, 82424, 77887, 59861, 109424, 170039, 83542, 296098, 207932, 270010, 363676, 374164, 377229, 301528, 426128, 414792, 5255, 121100, 456703, 478639, 224355, 863, 516486, 522402, 567649, 581032, 31107, 638302, 785930, 885058, 923252, 937278, 940139, 1038873, 1061818, 1084244, 640, 10023, 40820, 140823, 130925, 173458, 339988, 356325, 406122, 252451, 446354, 464729, 501907, 325450, 614934, 729031, 532639, 127850, 213121, 237353, 256835, 43714, 550600, 504561, 606078, 740985, 747188, 1071583, 16279, 56235, 380994, 471198, 712062, 181007, 510173, 65262, 467062, 459682, 720203, 989517, 141498, 315085, 305642, 1111122, 1125624, 453422, 698229, 705899, 1016902, 37641, 454330, 473544, 711704, 253639, 962192, 574379, 87061, 32562, 35, 40196, 966435, 838219, 1150794, 15302, 979163, 1113682, 269535, 298859, 1033548, 920, 558912, 773655, 32694, 28236, 881931, 126314, 20763, 1065395, 653610, 42348, 285783, 316067, 37757, 47813]
            self.movie_years = set([])
            self.chris_counter = 0
            self.movies_played_this_game = []
            self.actors_played_this_game = []
            self.horror_movie_counter = 0
            self.tilda_swinton_movies = [20308, 7351, 24936, 9300, 41110, 41801, 38987, 81540, 83401, 84012, 96484, 106304, 110838, 112477, 146140, 255500, 261369, 324807, 338630, 341240, 15030, 71859, 428702, 99453, 413786, 387426, 502386, 511819, 518852, 554794, 556694, 558398, 566038, 580728, 586745, 588994, 565249, 41970, 288388, 542955, 671577, 790867, 435353, 860004, 881366, 901565, 346080, 894319, 1031459, 498357, 1139231, 237, 1546, 31262, 8284, 41488, 41947, 42739, 152603, 400618, 230915, 245324, 262588, 291060, 333032, 360735, 361292, 369328, 445666, 497425, 499805, 665774, 720725, 113102, 852247, 800158, 4566, 4975, 43654, 94794, 140527, 473019, 535581, 542178, 615902, 844176, 999041, 1059301, 308, 1907, 2757, 58937, 110415, 214170, 520900, 526946, 411, 4944, 202872, 222962, 555604, 722902, 747188, 20537, 270487, 284052, 157834, 83666, 561, 1903, 10140, 1049516, 370648, 4922, 271718, 582959, 473021, 197393, 25832, 318042, 120467, 399174, 471208, 299534, 354287, 2454, 473033]
            return await message.channel.send(f'Game over!\nThis game lasted {total_turns} turns over {time_elapsed_string}.\nThe high score is {self.high_score} turns.\n@ me with a movie to play again!')

    async def on_valid_play(self):
        return

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
        if actor_id in self.actors_played_this_game:
            return "-3", []

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
                self.actors_played_this_game.append(actor_id)
                if actor_id in self.chrises:
                    self.chris_counter += 1
        
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
                if movie_id in self.movies_played_this_game:
                    return -3, ""
                if movie_id in movies_list:
                    self.movies_played_this_game.append(movie_id)
                    if 27 in movie["genre_ids"]:
                        self.horror_movie_counter
                    self.movie_years.add(movie["release_date"][:3])
                    return movie_id, movie_title
        except:
            return -2, "" # didn't find the movie
        return -1, "" # movie not found to have actor
    

    async def achievement_checker(self, message, movie_id):
        if movie_id in self.tom_hanks_movies:
            self.tom_hanks_counter += 1
            self.tom_hanks_movies.remove(movie_id)
        if self.tom_hanks_counter == 3:
            await message.channel.send("Congratulations! You made the achievement: 'Hanks for the memories:\nName 3 Tom Hanks movies in one game.'")
        if len(self.movie_years) == 5:
            await message.channel.send("Congratulations! You made the achievement: 'Decades of Cinema:\nName movies from 5 different decades in one game.'")
        if movie_id == 2565:
            await message.channel.send("Congratulations! You made the achievement: 'The Best Movie OF ALL TIME:\nName the movie 'Joe versus The Volcano'.'")
        if self.chris_counter == 3:
            await message.channel.send("Congratulations! You made the achievement: 'The Chrises:\nName three of the Chrises (Pine, Pratt, Hemsworth, Evans) in one game.'")
        if self.horror_movie_counter == 3:
            await message.channel.send("Congratulations! You made the achievement: 'What is this, Shock Doctors?:\nName three horror movies in one game.'")
        if movie_id in self.tilda_swinton_movies and self.turns <= 10:
            await message.channel.send("Congratulations! You made the achievement: 'TL;DR Swinton:\nName a Tilda Swinton movie in the first 10 turns of a game.'")
            self.tilda_swinton_movies = []




client = MyClient(intents=intents)
client.run(secret.TEST_BOT_TOKEN)
        