import datetime
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

class CreateteamForm(forms.Form):
	teamname = forms.CharField(label='Your Team Name', max_length=100)
	username2 = forms.CharField(label='Team member 2', max_length=100, required=False)
	username3 = forms.CharField(label='Team member 3', max_length=100, required=False)