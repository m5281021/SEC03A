from django.contrib import admin
from FirstApp.models import User, Movie, Showtime, Seat

admin.site.register(User)
admin.site.register(Movie)
admin.site.register(Showtime)
admin.site.register(Seat)