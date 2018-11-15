from django.contrib import admin

# Register your models here.
from ContestSpace.models import Contest, Problem, User, Team, pendingrequests, userContest, results

admin.site.register(Contest)
admin.site.register(Problem)
admin.site.register(userContest)
admin.site.register(User)
admin.site.register(Team)
admin.site.register(results)
admin.site.register(pendingrequests)