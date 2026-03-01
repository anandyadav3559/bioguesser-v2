from django.urls import path
from .views import CreateRoomView, StartRoundView, SubmitGuessView

urlpatterns = [
    path('create/', CreateRoomView.as_view(), name='create_room'),
    path('start_round/', StartRoundView.as_view(), name='start_round'),
    path('guess/', SubmitGuessView.as_view(), name='submit_guess'),
]
