from django.urls import path, re_path

from . import views

app_name = 'ttt'

urlpatterns = [
    path('create-game/', views.CreateGame.as_view(), name='create-game'),
    path('join-game/', views.JoinGame.as_view(), name='join-game'),
    path('play-game/<str:uid>', views.play_game, name='play-game'),
    path('get-board/<str:uid>', views.get_board, name='get-board'),
    path('mark-cell/<str:uid>', views.MarkCell.as_view(), name='mark_cell'),
    path('clean-up', views.clean_up, name='clean-up'),
    path('thanks/', views.thanks, name='thanks'),
]