# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Player, Game, Cell


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')
    search_fields = ('name',)


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('id', 'gid', 'status', 'player_1', 'player_2', 'turn', 'message', 'player_1_uid', 'player_2_uid')
    list_filter = ('player_1', 'player_2')


@admin.register(Cell)
class CellAdmin(admin.ModelAdmin):
    list_display = ('id', 'cell_id', 'status', 'game', 'marked_by')
    list_filter = ('game', 'marked_by')