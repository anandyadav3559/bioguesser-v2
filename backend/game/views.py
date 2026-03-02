from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from backend.throttling import GuessSubmitThrottle, RoundStartThrottle
from .services import GameService
from .models import Room, Round, Player
from animal.models import Animal, AnimalLocation
from django.shortcuts import get_object_or_404

class CreateRoomView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]  # global 60/min fallback is fine for room creation

    def post(self, request):
        try:
            # For single-player we just use the default options or can accept from request
            room = GameService.create_room(
                host_user=request.user,
                max_players=1, # Single player
                max_rounds=100, # Large number for endless single player
                time_per_round=int(request.data.get('time_per_round', 30))
            )
            return Response({
                'room_code': room.room_code,
                'status': room.status
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class StartRoundView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [RoundStartThrottle]  # 30/minute per user

    def post(self, request):
        room_code = request.data.get('room_code')
        animal_id = request.data.get('animal_id')
        
        if not room_code or not animal_id:
            return Response({'error': 'room_code and animal_id are required'}, status=status.HTTP_400_BAD_REQUEST)
            
        room = get_object_or_404(Room, room_code=room_code)
        
        # Verify user is in room
        if not room.players.filter(user=request.user).exists():
            return Response({'error': 'Not in room'}, status=status.HTTP_403_FORBIDDEN)
            
        animal = get_object_or_404(Animal, pk=animal_id)
            
        try:
            # In single player we manage the rounds a bit differently 
            # Or we can just use the natural round increment but specify the animal
            new_round_num = room.rounds.count() + 1
            new_round = Round.objects.create(
                room=room,
                round_number=new_round_num,
                animal=animal,
                status='active'
            )
            
            # Start the game if it was waiting
            if room.status == 'waiting':
                room.status = 'playing'
                room.save()
            return Response({
                'round_number': new_round.round_number,
                'status': new_round.status
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class SubmitGuessView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [GuessSubmitThrottle]  # 20/minute per user — guards evaluate_round() DB transactions

    def post(self, request):
        room_code = request.data.get('room_code')
        lat = request.data.get('latitude')
        lng = request.data.get('longitude')
        
        room = get_object_or_404(Room, room_code=room_code)
        player = get_object_or_404(Player, room=room, user=request.user)
        
        # Get active round
        active_round = room.rounds.filter(status='active').order_by('-round_number').first()
        if not active_round:
            return Response({'error': 'No active round'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            # Submit guess
            guess = GameService.submit_answer(player, active_round, float(lat), float(lng))
            
            # Since it's single player, evaluate immediately
            results = GameService.evaluate_round(active_round)
            
            # Find the user's generated score
            user_result = next((r for r in results if r['player_username'] == request.user.username), None)

            # Get the real locations so the frontend can plot them
            # Return up to 50 max points to avoid clutter or huge payloads
            true_locations = list(AnimalLocation.objects.filter(
                animal=active_round.animal
            ).values('latitude', 'longitude', 'count')[:50])
            
            return Response({
                'score_awarded': user_result['score_awarded'] if user_result else 0,
                'total_score': user_result['total_score'] if user_result else 0,
                'true_locations': true_locations
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
