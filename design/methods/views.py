from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

@login_required
def getUserName(request):
	username = None
	if request.user.is_authenticated:
		username = request.user.username
	return HttpResponse(username)
    
@login_required
def getTeamName(request):
	teamname = None
	if request.user.is_authenticated:
		teamname = request.user.username.split("_")[0]
	return HttpResponse(teamname)

