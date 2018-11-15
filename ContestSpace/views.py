from django.shortcuts import render
from django.views import generic
import json
import requests
from ContestSpace.models import Contest, Problem, User, Team, pendingrequests, userContest, results
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime
from ContestSpace.forms import CreateteamForm
from django.http import HttpResponse
from django.shortcuts import render
from datetime import timedelta
from datetime import datetime
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.utils.timezone import make_aware
import operator
import pytz
from django.shortcuts import render_to_response
from django.template import RequestContext


def index(request, temp = ""):
	if temp == "logout":
		return logout(request)
	content = ""
	if 'code' in request.GET and request.GET['code'] != "" and 'access_token' not in request.session:
		auth_code = request.GET['code']
		request.session['auth_code'] = auth_code
		return access(request)
	now = request.session.get('time', 0)
	if now:
		now = datetime.strptime(now, '%Y-%m-%d %H:%M:%S.%f')
		if datetime.now() - now > timedelta(seconds=55*60):
			refresh(request)
	if 'access_token' in request.session:
		content = userContest.objects.filter(user__exact = request.session['username'], endDate__gte = datetime.now())
		teams = Team.objects.filter(user1__exact = request.session['username'])
		teams = teams | Team.objects.filter(user2__exact = request.session['username'])
		teams = teams | Team.objects.filter(user3__exact = request.session['username'])
		content = content | userContest.objects.filter(team__in=teams, endDate__gte = datetime.now())
	return render(request, 'index.html', {'user_name':request.session.get('username', '123'), 'content': content})
	
def access(request):
	headers = {
		'content-Type': 'application/json',
	}
	data = '{"grant_type": "authorization_code","code": "' + request.session["auth_code"] + \
		'","client_id":"YOUR_ID","client_secret":"YOUR_s",' \
		'"redirect_uri":"http://149.129.139.177:8000/ContestSpace/"}'
	response = requests.post('https://api.codechef.com/oauth/token', headers=headers, data=data)
	json_data = response.json()
	request.session["access_token"] = json_data["result"]["data"]["access_token"]
	request.session["refresh_token"] = json_data["result"]["data"]["refresh_token"]
	now = datetime.now()
	now = str(now)
	#now = now.strftime('%Y-%m-%d %H:%M')
	request.session["time"] = now
	headers = {
		'Accept': 'application/json',
		'Authorization': 'Bearer '+request.session["access_token"],
	}
	response = requests.get('https://api.codechef.com/users/me/', headers=headers)
	if response.status_code == 200:
		info = json.loads(response.content.decode('utf-8'))
		request.session['username'] = info["result"]["data"]["content"]["username"]

	content = userContest.objects.filter(user__exact = request.session['username'], endDate__gte = datetime.now())
	teams = Team.objects.filter(user1__exact = request.session['username'])
	teams = teams | Team.objects.filter(user2__exact = request.session['username'])
	teams = teams | Team.objects.filter(user3__exact = request.session['username'])
	content = content | userContest.objects.filter(team__in=teams, endDate__gte = datetime.now())
	return render(request, 'index.html',  {'user_name':request.session.get('username', '123'), 'content': content})

def logout(request):
	if 'auth_code' in request.session:
		del request.session['auth_code']
	if 'access_token' in request.session:
		del request.session['access_token']
	if 'refresh_token' in request.session:
		del request.session['refresh_token']
	if 'username' in request.session:
		del request.session['username']
	if 'time' in request.session:
		del request.session['time']
	return render(request, 'index.html', {'user_name': '123'})


def refresh(request):
	data = [
		('grant_type', 'refresh_token'),
		('refresh_token', request.session["refresh_token"]),
		('client_id', 'YOUR_ID'),
		('client_secret', 'YOUR_secret'),
	]	
	response = requests.post('https://api.codechef.com/oauth/token', data=data)
	json_data = response.json()
	request.session["access_token"] = json_data["result"]["data"]["access_token"]
	request.session["refresh_token"] = json_data["result"]["data"]["refresh_token"]
	now = datetime.now()
	now = str(now)
	#now = now.strftime('%Y-%m-%d %H:%M')
	request.session["time"] = now
	return index(request)

def contests(request, temp):
	if "username" not in request.session or request.session.get("username", '123') == "123":
		return render(request, '404.html')
	now = request.session.get('time')
	if now:
		now = datetime.strptime(now, '%Y-%m-%d %H:%M:%S.%f')
		if datetime.now() - now > timedelta(seconds=55*60):
			refresh(request)
	contents = userContest.objects.filter(user__exact = request.session['username'], endDate__gte = datetime.now())
	teams = Team.objects.filter(user1__exact = request.session['username'])
	teams = teams | Team.objects.filter(user2__exact = request.session['username'])
	teams = teams | Team.objects.filter(user3__exact = request.session['username'])
	contents = contents | userContest.objects.filter(team__in=teams, endDate__gte = datetime.now())
	if temp == 'a':
		content = Contest.objects.filter(contesttype__exact = 'a')
		return render(request, 'ContestSpace/contest_page.html', {'contents':contents, 'content':content, 'button': 'Start Contest', 'link':'startcontest','user_name':request.session.get('username', '123')})
	elif temp == 'b':
		content = Contest.objects.filter(contesttype__exact = 'b')
		return render(request, 'ContestSpace/contest_page.html', {'contents':contents, 'content':content, 'button': 'Start Contest', 'link':'startcontest','user_name':request.session.get('username', '123')})
	elif temp == 'c':
		content = Contest.objects.filter(contesttype__exact = 'c')
		return render(request, 'ContestSpace/contest_page.html', {'contents':contents, 'content':content, 'button': 'Start Contest', 'link':'startcontest','user_name':request.session.get('username', '123')})
	elif temp == 'list':
		if "username" not in request.session or request.session.get("username", '123') == "123":
			return render(request, '404.html')
		content = userContest.objects.filter(user__exact = request.session['username'], endDate__lte = datetime.now())
		teams = Team.objects.filter(user1__exact = request.session['username'])
		teams = teams | Team.objects.filter(user2__exact = request.session['username'])
		teams = teams | Team.objects.filter(user3__exact = request.session['username'])
		content = content | userContest.objects.filter(team__in=teams, endDate__lte = datetime.now())
		return render(request, 'ContestSpace/contest_page.html', {'contents': contents, 'content': content, 'user_name':request.session.get('username', '123'), 'button': 'View Result',  'link':'showresult'})

def createteamform(request):
	if "username" not in request.session or request.session.get("username", '123') == "123":
		return render(request, '404.html')
	now = request.session['time']
	if now:
		now = datetime.strptime(now, '%Y-%m-%d %H:%M:%S.%f')
		if datetime.now() - now > timedelta(seconds=55*60):
			refresh(request)
    # if this is a POST request we need to process the form data
	if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        # check whether it's valid:
		form = CreateteamForm(request.POST)
		if form.is_valid():
			teamname = form.cleaned_data['teamname']
			unique_id = get_random_string(length=32)
			b = Team(teamname = teamname, teamid = unique_id, user1 = request.session['username'])
			b.save()
			member2 = form.cleaned_data['username2'] #NULL h to????/
			member3 = form.cleaned_data['username3']
			a = pendingrequests(userp = member2, teamname = teamname,  teamidp = unique_id)
			a.save()
			a = pendingrequests(userp = member3, teamname = teamname, teamidp = unique_id)
			a.save()
			return HttpResponseRedirect(reverse('manageteams') )
	# if a GET (or any other method) we'll create a blank form
	else:
		form = CreateteamForm()

	return render(request, 'ContestSpace/forms.html', {'form': form, 'user_name':request.session.get('username', '123')})
def startcontest(request, temp):
	if "username" not in request.session or request.session.get("username", '123') == "123":
		return render(request, '404.html')
	now = request.session['time']
	contents = userContest.objects.filter(user__exact = request.session['username'], endDate__gte = datetime.now())
	teams = Team.objects.filter(user1__exact = request.session['username'])
	teams = teams | Team.objects.filter(user2__exact = request.session['username'])
	teams = teams | Team.objects.filter(user3__exact = request.session['username'])
	contents = contents | userContest.objects.filter(team__in=teams, endDate__gte = datetime.now())
	if now:
		now = datetime.strptime(now, '%Y-%m-%d %H:%M:%S.%f')
		if datetime.now() - now > timedelta(seconds=55*60):
			refresh(request)
	teams = Team.objects.filter(user1__exact = request.session['username'])
	teams = teams | Team.objects.filter(user2__exact = request.session['username'])
	teams = teams | Team.objects.filter(user3__exact = request.session['username'])
	if request.method == 'POST':
		teamname = request.POST['team_name']
		t = Team.objects.filter(teamname__exact = teamname)
		conname = Contest.objects.filter(ContestCode__exact = temp)
		team = ""
		for u in t:
			team = u
		for c in conname:
			contestname = c.name
			timedel = c.duration
		if team == "" or '(single)' in teamname:
			team = request.session['username']
			contest = userContest(ContestCode = temp, name = contestname, startDate = datetime.now(), endDate = datetime.now() + timedel, user = team)
			contest.save() 
			contestid = contest.pk 
		else:
			contest = userContest(ContestCode = temp, name = contestname, startDate = datetime.now(), endDate = datetime.now() + timedel, team = team)
			contest.save() 
			contestid = contest.pk 
		return HttpResponseRedirect(reverse('problems', args = (temp, contestid, )) )
	return render(request, 'ContestSpace/startcontest.html', {'contents': contents, 'teams': teams, 'user_name':request.session['username']})

def manageteams(request):
	if "username" not in request.session or request.session.get("username", '123') == "123":
		return render(request, '404.html')
	now = request.session['time']
	contents = userContest.objects.filter(user__exact = request.session['username'], endDate__gte = datetime.now())
	teams = Team.objects.filter(user1__exact = request.session['username'])
	teams = teams | Team.objects.filter(user2__exact = request.session['username'])
	teams = teams | Team.objects.filter(user3__exact = request.session['username'])
	contents = contents | userContest.objects.filter(team__in=teams, endDate__gte = datetime.now())
	if now:
		now = datetime.strptime(now, '%Y-%m-%d %H:%M:%S.%f')
		if datetime.now() - now > timedelta(seconds=55*60):
			refresh(request)
	teams = Team.objects.filter(user1__exact = request.session['username'])
	teams = teams | Team.objects.filter(user2__exact = request.session['username'])
	teams = teams | Team.objects.filter(user3__exact = request.session['username'])
	pendingreq = pendingrequests.objects.filter(userp__exact = request.session['username'])
	if request.method == 'POST':
		if request.POST.get('accept'):
			teamidp = request.POST['accept']
			t = pendingrequests.objects.filter(teamidp__exact = teamidp)
			for u in t:
				u.delete()
			t = Team.objects.filter(teamid__exact = teamidp)
			for u in t:
				if not u.user2:
					u.user2 = request.session['username']
					u.save()
				elif not u.user3:
					u.user3 = request.session['username']
					u.save()
		if request.POST.get('decline'):
			teamidp = request.POST['decline']
			t = pendingrequests.objects.filter(teamidp__exact = teamidp)
			for u in t:
				u.delete()
		if request.POST.get('leave'):
			teamid = request.POST['leave']
			t = Team.objects.filter(teamid__exact = teamid)
			for u in t:
				if u.user1 == request.session['username']:
					u.user1 = ""
					u.save()
				elif u.user2 == request.session['username']:
					u.user2 = ""
					u.save()
				elif u.user3 == request.session['username']:
					u.user3 = ""
					u.save()
				if not u.user1 and (not u.user2) and (not u.user3):
					u.delete()
	return render(request, 'ContestSpace/manageteam.html', {'contents': contents, 'teams': teams, 'pendingreq': pendingreq, 'user_name':request.session.get('username', '123')})
											
def problems(request, temp, id):
	if "username" not in request.session or request.session.get("username", '123') == "123":
		return render(request, '404.html')
	now = request.session['time']
	contents = userContest.objects.filter(user__exact = request.session['username'], endDate__gte = datetime.now())
	teams = Team.objects.filter(user1__exact = request.session['username'])
	teams = teams | Team.objects.filter(user2__exact = request.session['username'])
	teams = teams | Team.objects.filter(user3__exact = request.session['username'])
	contents = contents | userContest.objects.filter(team__in=teams, endDate__gte = datetime.now())
	if now:
		now = datetime.strptime(now, '%Y-%m-%d %H:%M:%S.%f')
		if datetime.now() - now > timedelta(seconds=55*60):
			refresh(request)
	content =  Contest.objects.filter(ContestCode__exact = temp)
	cont = userContest.objects.get(pk=id)
	context = {
		'content':content,
		'contents':contents,
		'id': id,
		'cont': cont,
		'user_name':request.session.get('username', '123'),
	}
	p = datetime.now(timezone.utc)
	t = cont.endDate
	context['expired'] = False
	if p >= t: 
		context['expired'] = True
	context['endtime'] = t
	return render(request, 'ContestSpace/problem_page.html', context = context)


def result(request, temp, id):
	if "username" not in request.session or request.session.get("username", '123') == "123":
		return render(request, '404.html')
	now = request.session['time']
	contents = userContest.objects.filter(user__exact = request.session['username'], endDate__gte = datetime.now())
	teams = Team.objects.filter(user1__exact = request.session['username'])
	teams = teams | Team.objects.filter(user2__exact = request.session['username'])
	teams = teams | Team.objects.filter(user3__exact = request.session['username'])
	contents = contents | userContest.objects.filter(team__in=teams, endDate__gte = datetime.now())
	if now:
		now = datetime.strptime(now, '%Y-%m-%d %H:%M:%S.%f')
		if datetime.now() - now > timedelta(seconds=55*60):
			refresh(request)
	t = Team.objects.filter(usercontest__in=userContest.objects.filter(pk=id))	
	cont = userContest.objects.get(pk=id)
	user2, user3 = "", ""
	for u in t:
		user1 = u.user1
		user2 = u.user2
		user3 = u.user3
	headers = {
		'Accept': 'application/json',
		'Authorization': 'Bearer '+ request.session["access_token"],
	}
	sub = {}
	if not t:
		user1 = request.session['username']
	if user1:
		response = requests.get('https://api.codechef.com/submissions/?year=2018&username=' + user1 + '&limit=20&offset=0', headers=headers)
		if response.status_code==200:
			info = json.loads(response.content.decode('utf-8'))
			if info["result"]["data"]["code"] == 9001:
				for i in info["result"]["data"]["content"]:
					tz = pytz.timezone('Asia/Kolkata')
					i["date"] = datetime.strptime(i["date"], "%Y-%m-%d %H:%M:%S")
					i["date"] = make_aware(i["date"], timezone = tz, is_dst = True)
					if(i["date"] > cont.startDate and i["date"] <= cont.endDate):
						sub.setdefault(i["problemCode"], []).append({'result': i["result"], 'time': i["date"]})
		else:
			return refresh(request, temp, id)
		response = requests.get('https://api.codechef.com/submissions/?year=2018&username=' + user1 + '&limit=20&offset=20', headers=headers)
		if response.status_code==200:
			info = json.loads(response.content.decode('utf-8'))
			if info["result"]["data"]["code"] == 9001:
				for i in info["result"]["data"]["content"]:
					tz = pytz.timezone('Asia/Kolkata')
					i["date"] = datetime.strptime(i["date"], "%Y-%m-%d %H:%M:%S")
					i["date"] = make_aware(i["date"], timezone = tz, is_dst = True)
					if(i["date"] > cont.startDate and i["date"] <= cont.endDate):
						sub.setdefault(i["problemCode"], []).append({'result': i["result"], 'time': i["date"]})
		else:
			return refresh(request)
	if user2:
		response = requests.get('https://api.codechef.com/submissions/?year=2018&username=' + user2 + '&limit=20&offset=0', headers=headers)
		if response.status_code==200:
			info = json.loads(response.content.decode('utf-8'))
			if info["result"]["data"]["code"] == 9001:
				for i in info["result"]["data"]["content"]:
					tz = pytz.timezone('Asia/Kolkata')
					i["date"] = datetime.strptime(i["date"], "%Y-%m-%d %H:%M:%S")
					i["date"] = make_aware(i["date"], timezone = tz, is_dst = True)
					if(i["date"] > cont.startDate and i["date"] <= cont.endDate):
						sub.setdefault(i["problemCode"], []).append({'result': i["result"], 'time': i["date"]})
		else:
			return refresh(request)
		response = requests.get('https://api.codechef.com/submissions/?year=2018&username=' + user1 + '&limit=20&offset=20', headers=headers)
		if response.status_code==200:
			info = json.loads(response.content.decode('utf-8'))
			if info["result"]["data"]["code"] == 9001:
				for i in info["result"]["data"]["content"]:
					tz = pytz.timezone('Asia/Kolkata')
					i["date"] = datetime.strptime(i["date"], "%Y-%m-%d %H:%M:%S")
					i["date"] = make_aware(i["date"], timezone = tz, is_dst = True)
					if(i["date"] > cont.startDate and i["date"] <= cont.endDate):
						sub.setdefault(i["problemCode"], []).append({'result': i["result"], 'time': i["date"]})
		else:
			return refresh(request)
	
	if user3 :
		response = requests.get('https://api.codechef.com/submissions/?year=2018&username=' + user3 + '&limit=20&offset=0', headers=headers)
		if response.status_code==200:
			info = json.loads(response.content.decode('utf-8'))
			if info["result"]["data"]["code"] == 9001:
				for i in info["result"]["data"]["content"]:
					tz = pytz.timezone('Asia/Kolkata')
					i["date"] = datetime.strptime(i["date"], "%Y-%m-%d %H:%M:%S")
					i["date"] = make_aware(i["date"], timezone = tz, is_dst = True)
					if(i["date"] > cont.startDate and i["date"] <= cont.endDate):
						sub.setdefault(i["problemCode"], []).append({'result': i["result"], 'time': i["date"]})
		else:
			return refresh(request, temp, id)
		response = requests.get('https://api.codechef.com/submissions/?year=2018&username=' + user1 + '&limit=20&offset=20', headers=headers)
		if response.status_code==200:
			info = json.loads(response.content.decode('utf-8'))
			if info["result"]["data"]["code"] == 9001:
				for i in info["result"]["data"]["content"]:
					tz = pytz.timezone('Asia/Kolkata')
					i["date"] = datetime.strptime(i["date"], "%Y-%m-%d %H:%M:%S")
					i["date"] = make_aware(i["date"], timezone = tz, is_dst = True)
					if(i["date"] > cont.startDate and i["date"] <= cont.endDate):
						sub.setdefault(i["problemCode"], []).append({'result': i["result"], 'time': i["date"]})
		else:
			return refresh(request, temp, id)
	
	cont = Contest.objects.filter(ContestCode__exact = temp)
	for i in cont:
		for problemcode in i.problemcode.all():
			p = results(contestid = id, problemcode = problemcode)
			p.save()

	for i in sub:
		sub[i].sort(key=operator.itemgetter('time'))
		pp = results.objects.filter(contestid__exact = id, problemcode__exact = i)
		for ii in pp:
			p = ii
		pen = 1
		for j in sub[i]:
			if j["result"] == "WA":
				pen = pen + 1
			else:
				p.time = j["time"]
				p.penalty = pen
				break
		p.save()
	return index(request)

def showresult(request, temp, id):
	contents = userContest.objects.filter(user__exact = request.session['username'], endDate__gte = datetime.now())
	teams = Team.objects.filter(user1__exact = request.session['username'])
	teams = teams | Team.objects.filter(user2__exact = request.session['username'])
	teams = teams | Team.objects.filter(user3__exact = request.session['username'])
	contents = contents | userContest.objects.filter(team__in=teams, endDate__gte = datetime.now())
	now = request.session['time']
	if now:
		now = datetime.strptime(now, '%Y-%m-%d %H:%M:%S.%f')
		if datetime.now() - now > timedelta(seconds=55*60):
			refresh(request)
	if "username" not in request.session or request.session.get("username", '123') == "123":
		return render(request, '404.html')
	cont = userContest.objects.get(pk=id)
	t =  results.objects.filter(contestid__exact = id)
	
	if not t :
		result(request, temp, id)
	ls = []
	cont.endDate = datetime.now(timezone.utc)
	cont.save()
	context = {
		'contents': contents,
		'content': t,
		'user_name':request.session.get('username', '123'),
	}
	totalscore = 0
	totaltime = timedelta(seconds=0)
	for i in t:
		if not i.time:
			i.time = ""
			i.penalty = ""
		if i.time:
			totalscore = totalscore + 1
			totaltime = totaltime + (i.time - cont.startDate) + timedelta(seconds=(20*60*(i.penalty - 1)))
			i.time =  (i.time - cont.startDate)
			i.time = i.time - timedelta(microseconds=(i.time).microseconds)
			i.penalty = i.penalty - 1
	context["totalscore"] = totalscore
	context["totaltime"] = totaltime - timedelta(microseconds=(totaltime).microseconds)
	return render(request, 'ContestSpace/result.html', context = context)	


