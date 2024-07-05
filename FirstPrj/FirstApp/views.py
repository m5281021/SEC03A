from django.http import HttpResponse
from FirstApp.models import User, Movie, Showtime, Seat
from django.db import transaction

user_name = 'John Clark'
seat_number = 10
showtime_number = 1
date = '2024-07-02'
movie_name = 'Spiderman'

def index(request):
    return HttpResponse("Welcome to the site!")

def hello(request):
    return HttpResponse("Hello there!")

def register_new_user(request):
    u = User(name = user_name)
    u.save()
    return HttpResponse("You registered!")

def register_new_movie_seats(request):
    try:
        with transaction.atomic():
            u = User.objects.filter(name = user_name).get()
            st = Showtime.objects.filter(number = showtime_number).get()
            seat = Seat.objects.select_for_update().all()
            seat = Seat(showtime = st, reserved = True, user = u)
            seat.save()
    except register_new_movie_seats:
        return HttpResponse("Something went wrong.")
    return HttpResponse("You completed to register a seat of movie!")

def show_user_movies(request):
    try:
        with transaction.atomic():
            s = Seat.objects.filter(user__name = user_name)
            print(s)
    except show_user_movies:
        return HttpResponse("Something went wrong.")
    return HttpResponse("You can watch your movies!")

def show_matching_movies_date(request):
    try:
        with transaction.atomic():
            show_movie = Showtime.objects.filter(time = date)
            print(show_movie)
    except show_matching_movies_date:
        return HttpResponse("Something went wrong.")
    return HttpResponse("These movies may match you!")

def show_matching_dates_movie(request):
    try:
        with transaction.atomic():
            date = Showtime.objects.filter(movie__name = movie_name)
            print(date)
    except show_matching_dates_movie:
        return HttpResponse("Something went wrong.")
    return HttpResponse("These days may match you!")