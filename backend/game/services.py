import uuid
import random
import string
import math
import h3
from django.db import transaction
from django.db.models import F
from game.models import Room, Player, Round, Guess
from animal.models import Animal, AnimalLocation

class GameService:
    
    @staticmethod
    def generate_room_code(length=6):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

    @staticmethod
    @transaction.atomic
    def create_room(host_user, max_players=4, max_rounds=5, time_per_round=30):
        room_code = GameService.generate_room_code()
        
        # Ensure unique room code
        while Room.objects.filter(room_code=room_code).exists():
            room_code = GameService.generate_room_code()

        room = Room.objects.create(
            room_code=room_code,
            host=host_user,
            status='waiting',
            max_players=max_players,
            max_rounds=max_rounds,
            time_per_round=time_per_round
        )

        # Add host as a player
        GameService.add_player(room, host_user)
        return room

    @staticmethod
    @transaction.atomic
    def add_player(room, user):
        if room.status != 'waiting':
            raise ValueError("Cannot join room that is not waiting.")
            
        current_players = room.players.count()
        if current_players >= room.max_players:
            raise ValueError("Room is full.")
            
        # Check if player already in room
        player, created = Player.objects.get_or_create(
            user=user,
            room=room,
            defaults={'score': 0, 'is_active': True}
        )
        
        if not created and not player.is_active:
            player.is_active = True
            player.save()
            
        return player

    @staticmethod
    @transaction.atomic
    def start_round(room):
        current_round_count = room.rounds.count()
        
        if current_round_count >= room.max_rounds:
            return GameService.end_game(room)
            
        if room.status == 'waiting':
            room.status = 'playing'
            room.save()

        # Get animals already played in this room
        played_animal_ids = room.rounds.exclude(animal__isnull=True).values_list('animal_id', flat=True)
        
        # Pick a random animal not yet played
        # In a real app, query efficiency matters here. For now, picking randomly.
        available_animals = Animal.objects.exclude(id__in=played_animal_ids)
        if not available_animals.exists():
            # If we run out of animals, end game or allow repeats. Let's allow repeats if strictly out.
            available_animals = Animal.objects.all()
            
        selected_animal = available_animals.order_by('?').first()

        new_round = Round.objects.create(
            room=room,
            round_number=current_round_count + 1,
            animal=selected_animal,
            status='active'
        )
        return new_round

    @staticmethod
    @transaction.atomic
    def submit_answer(player, round_obj, latitude, longitude):
        if round_obj.status != 'active':
            raise ValueError("Round is not active.")
            
        # Ensure player hasn't already guessed
        if Guess.objects.filter(player=player, round=round_obj).exists():
            raise ValueError("Player has already submitted a guess for this round.")

        guess = Guess.objects.create(
            player=player,
            round=round_obj,
            latitude=latitude,
            longitude=longitude
        )
        return guess

    @staticmethod
    @transaction.atomic
    def evaluate_round(round_obj):
        round_obj.status = 'finished'
        round_obj.save()

        animal = round_obj.animal
        p_max = animal.max_probability or 1.0
        entropy = animal.entropy or 1.0

        guesses = Guess.objects.filter(round=round_obj)
        evaluated_guesses = []
        locations = AnimalLocation.objects.filter(animal=animal)
        
        # Total sightings of this animal for calculating real probabilities online if not pre-calculated
        total_sightings = sum(loc.count for loc in locations) if locations else 0

        # Define an entropy scaling factor function
        def f_entropy(ent):
            return max(0.1, math.exp(-0.2 * ent))

        scaling_factor = f_entropy(entropy)
        H3_RESOLUTION = 2 

        loc_dict = {loc.h3_index: loc.count for loc in locations}
        
        # Calculate great-circle distance using Haversine formula
        def haversine(lat1, lon1, lat2, lon2):
            R = 6371.0 # Earth radius in km
            dLat = math.radians(lat2 - lat1)
            dLon = math.radians(lon2 - lon1)
            a = math.sin(dLat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon / 2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            return R * c

        for guess in guesses:
            if guess.latitude == 200.0 and guess.longitude == 200.0:
                final_score = 0
            else:
                guessed_h3 = h3.latlng_to_cell(guess.latitude, guess.longitude, H3_RESOLUTION)
                cell_count = loc_dict.get(guessed_h3, 0)
                
                p_guess = (cell_count / total_sightings) if total_sightings > 0 else 0
                score_local = (p_guess / p_max) if p_max > 0 else 0
                
                # If the exact cell wasn't matched, provide distance-based fallback scoring
                if score_local == 0 and locations.exists():
                    # Find the closest known location
                    closest_dist = min([haversine(guess.latitude, guess.longitude, loc.latitude, loc.longitude) for loc in locations])
                    
                    # Max distance to award any points (e.g., 5000 km)
                    max_dist_for_points = 5000.0
                    if closest_dist < max_dist_for_points:
                        # Exponential falloff score based on distance
                        score_local = max(0, 1.0 - (closest_dist / max_dist_for_points))

                max_points = 5000
                final_score = int(score_local * scaling_factor * max_points)
                final_score = max(0, min(max_points, final_score))

            guess.score_awarded = final_score
            guess.save()

            player = guess.player
            player.score = F('score') + final_score
            player.save()

            evaluated_guesses.append({
                'guess_id': guess.id,
                'player_username': player.user.username,
                'score_awarded': final_score,
                'total_score': player.score
            })

        return evaluated_guesses

    @staticmethod
    @transaction.atomic
    def end_game(room):
        room.status = 'finished'
        room.save()

        # Update all active rounds to finished just in case
        Round.objects.filter(room=room, status='active').update(status='finished')

        leaderboard = room.players.all().order_by('-score').values('user__username', 'score')
        return list(leaderboard)
