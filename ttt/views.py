from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.shortcuts import render
from .forms import GameCreateForm, GameJoinForm
from .models import Game, Player, Cell
from django.utils import timezone
from datetime import timedelta


class CreateGame(View):
    form_class = GameCreateForm
    # initial = {'key': 'value'}
    template_name = 'ttt/game-create.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        games = Game.objects.all().order_by('-id')[:10]
        return render(request, self.template_name, {'form': form, 'games': games})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            player_1 = form.cleaned_data['Player_1']
            player_2 = form.cleaned_data['Player_2']

            if player_1.strip() == player_2.strip():
                return render(request, 'ttt/game-create.html', {'form': form, 'error': 'Players name cannot be same'})

            # create player objects
            p1, _ = Player.objects.get_or_create(name=player_1)
            p2, _ = Player.objects.get_or_create(name=player_2)

            # create game
            game = Game()
            game.player_1 = p1
            game.player_2 = p2

            game.turn = p1
            game.message = f"{p1.name} Turn"
            game.save()

            # create cells
            Cell.objects.bulk_create([Cell(cell_id=i, game=game) for i in range(1, 10)])

            return HttpResponseRedirect(f'/play-game/{game.player_1_uid}')


def thanks(request):

    return HttpResponse("Thanks")


class JoinGame(View):
    form_class = GameJoinForm
    # initial = {'key': 'value'}
    template_name = 'ttt/game-join.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            return HttpResponseRedirect(f'/play-game/{code}')


def play_game(request, uid: str):
    if uid.startswith('p'):
        game = Game.objects.get(player_1_uid=uid)
        player = game.player_1
        player_type = "PRIMARY"
    elif uid.startswith('s'):
        game = Game.objects.get(player_2_uid=uid)
        player = game.player_2
        player_type = "SECONDARY"
    else:
        return HttpResponse("Invalid Game ID")

    return render(request, 'ttt/game-play.html',
                  {"game": game, "player": player, "player_type": player_type, "player_id": uid,
                   "secondary_player_uid": game.player_2_uid})


def clean_up(request):
    try:
        now = timezone.now()
        now = now - timedelta(hours=1)
        # now = now - timedelta(minutes=1)
        count, objs = Player.objects.filter(created_at__lte=now).delete()

        return JsonResponse(dict(status="ok", total_objs_delete=count))
    except Exception as e:
        return JsonResponse(dict(status="error", error="An error occurred while deleting objs"))


def get_board(request, uid: str):
    if uid.startswith('p'):
        game = Game.objects.get(player_1_uid=uid)
        player_type = "PRIMARY"
        player = game.player_1

    elif uid.startswith('s'):
        game = Game.objects.get(player_2_uid=uid)
        player_type = "SECONDARY"
        player = game.player_2
    else:
        return JsonResponse({"status": "error", "desc": "Invalid Game ID"})

    cells = []
    for cell in game.cells.all():
        cell = dict(
            id=cell.cell_id,
            status=cell.status,
            marked_by=cell.marked_by.pk if cell.marked_by else None,
            marked_by_user=cell.marked_by.name if cell.marked_by else None,
            winning_cell=cell.winning_cell
        )
        cells.append(cell)

    data = dict(
        status="ok",
        gid=game.gid,
        message=game.message,
        player_turn=game.turn.id,
        player_turn_name=game.turn.name,
        player_1=game.player_1.id,
        player_1_name=game.player_1.name,
        player_2=game.player_2.id,
        player_2_name=game.player_2.name,
        current_player=player.pk,
        current_player_name=player.name,
        current_player_type=player_type,
        player_uid=uid,
        cells=cells,
        can_play=True if game.turn == player else False,
        game_status=game.status,
        game_message=game.message
    )

    return JsonResponse(data)


@method_decorator(csrf_exempt, name='dispatch')
class MarkCell(View):
    def post(self, request, *args, **kwargs):
        uid = kwargs.get('uid')
        cell_id, player_type, gid, player_id = request.POST.get("cell_id"), request.POST.get(
            "player_type"), request.POST.get("gid"), request.POST.get("player_id")

        try:
            game = Game.objects.get(gid=gid)
        except Exception as e:
            return JsonResponse(dict(
                status="error",
                desc="Invalid game"
            ))

        if game.status == "FINISHED":
            return JsonResponse(dict(status="error", error="GAME already Finished"))

        try:
            cell = Cell.objects.get(cell_id=cell_id, game=game)
        except Exception as e:
            return JsonResponse(dict(
                status="error",
                desc="Invalid CELL"
            ))

        if cell.status != "BLANK":
            return JsonResponse(dict(status="error", error="CELL is already marked"))

        if int(player_id) == game.turn.pk:
            cell.status = "MARKED"
            cell.marked_by = game.turn
            cell.save()

            if player_type == "PRIMARY":
                game.turn = game.player_2
            elif player_type == "SECONDARY":
                game.turn = game.player_1

            game.message = f"{game.turn.name} Turn"

            if game.status == "NEW":
                game.status = "INPROGRESS"

            game.save()

        cells = Cell.objects.filter(marked_by=cell.marked_by, game=game)

        if len(cells) >= 3:
            # check winning matrix
            marked_cells = [c.cell_id for c in cells]
            marked_cells.sort()
            winning_mat = (
                (1, 2, 3),
                (1, 4, 7),
                (1, 5, 9),
                (2, 5, 8),
                (3, 6, 9),
                (3, 5, 7),
                (4, 5, 6),
                (7, 8, 9)
            )
            for seq in winning_mat:
                if set(seq).issubset(set(marked_cells)):
                    player = Player.objects.get(id=player_id)
                    game.message = f"{player.name} won the game"
                    game.status = "FINISHED"
                    game.save()
                    for cell_id in seq:
                        cell = Cell.objects.get(cell_id=cell_id, game=game)
                        cell.winning_cell = True
                        cell.save()
                    break
            else:
                cell_count = Cell.objects.filter(status="BLANK", game=game).count()
                if cell_count == 0:
                    game.message = f"Match drawn!"
                    game.status = "FINISHED"
                    game.save()

        return JsonResponse({"status": "ok"})

