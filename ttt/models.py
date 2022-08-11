import datetime
import uuid
from django.db import models
from django.utils import timezone
from django.template.defaultfilters import slugify
from django.urls import reverse


class Player(models.Model):
    PLAYER_TYPE = (
        ("PRIMARY", 'PRIMARY'),
        ("SECONDARY", 'SECONDARY')
    )
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return self.name


def get_player_uid(prefix):
    return f"{prefix}-{uuid.uuid1()}"


class Game(models.Model):
    GAME_STATUS = (
        ("NEW", "NEW"),
        ("IN-PROGRESS", "IN-PROGRESS"),
        ("ENDED", "ENDED")
    )
    gid = models.UUIDField(default=uuid.uuid4, editable=False)
    status = models.CharField(choices=GAME_STATUS, max_length=20, default="NEW")
    player_1 = models.ForeignKey("Player", related_name="player_1_games", on_delete=models.CASCADE, null=True, blank=True)
    player_2 = models.ForeignKey("Player", related_name="player_2_games", on_delete=models.CASCADE, null=True, blank=True)
    turn = models.ForeignKey("Player", related_name="turns", on_delete=models.CASCADE, null=True, blank=True)
    message = models.CharField(max_length=100, blank=True, null=True)
    player_1_uid = models.CharField(default=uuid.uuid4, max_length=25, editable=False, null=True, blank=True)
    player_2_uid = models.CharField(default=uuid.uuid4, max_length=25, editable=False, null=True, blank=True)

    def __str__(self):
        return f"GAME({self.gid})"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.player_1_uid = f"p-{self.player_1_uid}"
            self.player_2_uid = f"s-{self.player_2_uid}"
        super(Game, self).save(*args, **kwargs)


class Cell(models.Model):
    CELL_STATUS = (
        ("BLANK", "BLANK"),
        ("MARKED", "MARKED"),
    )
    cell_id = models.IntegerField(blank=True, null=True)
    status = models.CharField(choices=CELL_STATUS, max_length=20, default="BLANK")
    game = models.ForeignKey("Game", related_name="cells", on_delete=models.CASCADE)
    marked_by = models.ForeignKey("Player", related_name="cells", on_delete=models.CASCADE, null=True, blank=True)
    winning_cell = models.BooleanField(default=False)

    def __str__(self):
        return str(self.cell_id)