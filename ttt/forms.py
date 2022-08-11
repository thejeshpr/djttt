from django import forms


class GameCreateForm(forms.Form):
    Player_1 = forms.CharField(label='Player 1', max_length=100, required=True)
    Player_2 = forms.CharField(label='Player 2', max_length=100, required=True)


class GameJoinForm(forms.Form):
    code = forms.CharField(label='code', max_length=100, required=True)