import os
import django
import uuid

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from authentication.models import User
from animal.models import Animal, AnimalLocation
from game.services import GameService
from game.models import Room, Player, Round, Guess
import h3

def setup_test_data():
    print("Setting up test data...")
    # Create test users
    user1, _ = User.objects.get_or_create(username="test_host", defaults={"email": "host@test.com", "auth_provider": "test", "is_guest": False})
    user2, _ = User.objects.get_or_create(username="test_guest", defaults={"is_guest": True, "auth_provider": "guest"})

    # Ensure there's an animal with known h3 cells for testing
    animal, _ = Animal.objects.get_or_create(name="Test Animal", scientific_name="Testus animalis", defaults={"max_probability": 0.5, "entropy": 1.2})
    
    # Create a known cluster near lat/lng (0, 0)
    test_lat, test_lon = 0.0, 0.0
    h3_index = h3.latlng_to_cell(test_lat, test_lon, 2)
    AnimalLocation.objects.get_or_create(animal=animal, h3_index=h3_index, defaults={'latitude': test_lat, 'longitude': test_lon, 'count': 50})
    
    # Another smaller cluster
    h3_index_2 = h3.latlng_to_cell(10.0, 10.0, 2)
    AnimalLocation.objects.get_or_create(animal=animal, h3_index=h3_index_2, defaults={'latitude': 10.0, 'longitude': 10.0, 'count': 10})

    return user1, user2, animal

def test_game_loop():
    user1, user2, animal = setup_test_data()

    print("\n--- Testing Room Creation ---")
    room = GameService.create_room(host_user=user1, max_players=2, max_rounds=2)
    print(f"Room Created: {room.room_code}, Status: {room.status}, Host: {room.host.username}")

    print("\n--- Testing Add Player ---")
    player2 = GameService.add_player(room, user2)
    print(f"Player Added: {player2.user.username}, Room Players: {room.players.count()}")

    print("\n--- Testing Start Round ---")
    round1 = GameService.start_round(room)
    print(f"Round Started: {round1.round_number}, Animal: {round1.animal.name}, Status: {round1.status}")

    # Player 1 (user1) is host. We need to get their player object.
    player1 = room.players.get(user=user1)

    print("\n--- Testing Submit Answer ---")
    # Player 1 guesses perfectly near (0, 0)
    guess1 = GameService.submit_answer(player1, round1, 0.001, 0.001)
    print(f"Player 1 Guessed at (0.001, 0.001). Initial score: {guess1.score_awarded}")

    # Player 2 guesses poorly away from clusters
    guess2 = GameService.submit_answer(player2, round1, 45.0, 45.0)
    print(f"Player 2 Guessed at (45.0, 45.0). Initial score: {guess2.score_awarded}")

    print("\n--- Testing Evaluate Round (Applying Entropy Scoring) ---")
    results = GameService.evaluate_round(round1)
    for r in results:
        print(f"Player: {r['player_username']}, Points Awarded: {r['score_awarded']}, Total Score: {r['total_score']}")

    print("\n--- Testing Start Round 2 ---")
    round2 = GameService.start_round(room)
    print(f"Round Started: {round2.round_number}, Status: {round2.status}")

    print("\n--- Testing End Game ---")
    leaderboard = GameService.end_game(room)
    print("Leaderboard:")
    for idx, entry in enumerate(leaderboard):
        print(f"{idx+1}. {entry['user__username']} - {entry['score']} pts")

    print("\nCleaning up test data...")
    room.delete()
    user1.delete()
    user2.delete()
    animal.delete()
    print("Test Complete.")

if __name__ == "__main__":
    test_game_loop()
