import uuid
from django.db import models
from authentication.models import User
from animal.models import Animal

class Room(models.Model):
    ROOM_STATUS_CHOICES = [
        ('waiting', 'Waiting'),
        ('playing', 'Playing'),
        ('finished', 'Finished'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room_code = models.CharField(max_length=10, unique=True, db_index=True)
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='hosted_rooms')
    status = models.CharField(max_length=20, choices=ROOM_STATUS_CHOICES, default='waiting')
    max_players = models.IntegerField(default=4)
    max_rounds = models.IntegerField(default=5)
    time_per_round = models.IntegerField(default=30)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'rooms'
        ordering = ['-created_at']

    def __str__(self):
        return f"Room {self.room_code}"

class MultiplayerGame(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.OneToOneField(Room, on_delete=models.CASCADE, related_name='multiplayer_data')
    has_permanent_player = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'multiplayer_games'

    def __str__(self):
        return f"Multiplayer Data for Room {self.room.room_code}"


class Player(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='game_profiles')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='players')
    score = models.FloatField(default=0.0)
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'players'
        unique_together = ('user', 'room')
        ordering = ['joined_at']

    def __str__(self):
        return f"{self.user.username} in Room {self.room.room_code}"


class Round(models.Model):
    ROUND_STATUS_CHOICES = [
        ('active', 'Active'),
        ('finished', 'Finished'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='rounds')
    round_number = models.IntegerField()
    animal = models.ForeignKey(Animal, on_delete=models.DO_NOTHING, blank=True, null=True, db_constraint=False, related_name='rounds')
    status = models.CharField(max_length=20, choices=ROUND_STATUS_CHOICES, default='active')
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'rounds'
        unique_together = ('room', 'round_number')
        ordering = ['round_number']

    def __str__(self):
        return f"Round {self.round_number} for Room {self.room.room_code}"

class Guess(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='guesses')
    round = models.ForeignKey(Round, on_delete=models.CASCADE, related_name='guesses')
    latitude = models.FloatField()
    longitude = models.FloatField()
    score_awarded = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'guesses'
        unique_together = ('player', 'round') # A player can only guess once per round
        ordering = ['created_at']

    def __str__(self):
        return f"Guess by {self.player.user.username} for Round {self.round.round_number}"

from django.db.models.signals import pre_delete
from django.dispatch import receiver

@receiver(pre_delete, sender=User)
def cleanup_user_rooms(sender, instance, **kwargs):
    """
    When a User is deleted (e.g. guest logout), evaluate all their rooms.
    If it's a single player room, delete it entirely.
    If it's a multiplayer room and they are the LAST permanent player (or there are no permanent players left), delete it.
    """
    user_rooms = Room.objects.filter(players__user=instance)
    for room in user_rooms:
        if hasattr(room, 'multiplayer_data'):
            # Multiplayer: Retain the room if there are OTHER permanent players.
            other_permanent = room.players.exclude(user=instance).filter(user__is_guest=False).exists()
            if not other_permanent:
                room.delete()
            else:
                # Need to check if THEY were the host. If host, assign it to someone else or Null
                if room.host == instance:
                    # Let the SET_NULL cascade handle it, or we could manually assign the first surviving player.
                    pass
        else:
            # Single player strictly tied to them - purge
            room.delete()
