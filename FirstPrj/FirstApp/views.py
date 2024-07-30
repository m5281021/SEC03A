from django.shortcuts import render
from django.db import transaction
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password, check_password
from django_htmx.http import trigger_client_event

from FirstApp.models import User, Movie, Showtime, Seat
from FirstApp.forms import RegisterForm, LoginForm, ReserveForm, SeatForm

MAX_SEATS = 5

def base(request):
    return render(request, "base.html")

def login_frame(request, error=""):
    login = request.session.get("authorized_user_login", None)

    return render(
        request,
        "login_logout_frame.html",
        {"login_form": LoginForm(), "user_login": login, "login_error": error},
    )

def register_frame(request):
    login = request.session.get("authorized_user_login", None)
    return render(request, "register_frame.html", {"user_login": login})

def reservations_frame(request):
    login = request.session.get("authorized_user_login", None)
    return render(request, "reservations_frame.html", {"user_login": login})

def reserve_form_frame(request):
    login = request.session.get("authorized_user_login", None)
    user_name = None if not login else User.objects.filter(login = login).get().name
    movie_names = [m.name for m in Movie.objects.all()]
    reserve_form = ReserveForm(movies = movie_names, user = user_name)
    return render(request, "reserve_form_frame.html", {"reserve_form": reserve_form})

def seats_form_frame(request, showtime_obj):
    seats_obj = Seat.objects.filter(showtime = showtime_obj)
    reserved = []
    for s in seats_obj:
        reserved.append(True if s.reserved == True else False)
    seats_form = SeatForm(seats = reserved)
    return render(request, "seats_form_frame.html", {"seats_form": seats_form})

def register_form_frame(request, registered = False, error = ""):
    return render(
        request,
        "register_form_frame.html",
        {
            "registered": registered,
            "error": error,
            "register_form": RegisterForm(),
        },
    )

def register_user_data(f):
    if not f.is_valid():
        raise RuntimeError("Error: " + str(f.errors))
    name = f.cleaned_data["name"]
    login = f.cleaned_data["reg_login"]
    password = f.cleaned_data["reg_password"]
    passagain = f.cleaned_data["passagain"]
    if len(User.objects.filter(login = login)) > 0:
        raise RuntimeError(f"A user with the login {login} already exists.")
    if password != passagain:
        raise RuntimeError("Passwords do not match.")
    User.objects.create(name = name, login = login, password = make_password(password))
    return login

def do_register(request):
    error = None
    f = RegisterForm(request.POST)
    evt = ""
    try:
        login = register_user_data(f)
        evt = "evt_login"
        do_login_user(request, login)
    except RuntimeError as e:
        error = str(e)
    response = register_form_frame(request, error is None, error)
    return trigger_client_event(response, evt)

def do_check_regform(request):
    f = RegisterForm(request.POST)
    r = ""
    u = User.objects.filter(login = f.data["reg_login"])
    if len(u) != 0:
        r = "Login already used!"
    if f.data["reg_password"] != f.data["passagain"]:
        r = "Password do not match!"
    return HttpResponse(r)

def do_login_user(request, login):
    request.session["authorized_user_login"] = login

def do_login(request):
    f = LoginForm(request.POST)
    error = ""
    evt = ""
    try:
        if not f.is_valid():
            raise RuntimeError()
        u = User.objects.filter(login = f.cleaned_data["login"])
        if len(u) == 0 or not check_password(f.cleaned_data["password"], u[0].password):
            raise RuntimeError()
        do_login_user(request, u[0].login)
        evt = "evt_login"
    except RuntimeError:
        error = "Wrong username or password."
    return trigger_client_event(login_frame(request, error), evt)

def do_logout(request):
    request.session["authorized_user_login"] = None
    return trigger_client_event(login_frame(request), "evt_login")

def do_check_seats(request):
    movie_names = [m.name for m in Movie.objects.all()]
    f = ReserveForm(request.POST, movies = movie_names, user = "")
    if f.is_valid():
        movie_obj = None if len(Movie.objects.filter(name = f.cleaned_data["movies"])) == 0 else Movie.objects.filter(name = f.cleaned_data["movies"]).get()
        date_obj = f.cleaned_data["timeslot"]
        if movie_obj != None and f'{date_obj}' != 0:
            showtime_obj = Showtime.objects.filter(time = date_obj, movie = movie_obj).get()
            s = Seat.objects.filter(showtime = showtime_obj, reserved = False)
            if len(s) == 0:
                return HttpResponse("There is no available seat.")
            return trigger_client_event(seats_form_frame(request, showtime_obj), "evt_seat")
    return HttpResponse("")

def reserve_chance(request, f, user_login):
    if not f.is_valid():
        raise RuntimeError("Error: " + str(f.errors))
    with transaction.atomic():
        values = f.cleaned_data
        movie_obj = Movie.objects.filter(name = values["movies"]).get()
        showtime_obj = Showtime.objects.filter(time = values["timeslot"], movie = movie_obj).get()
        seats_obj = Seat.objects.filter(showtime = showtime_obj)
        reserved = []
        for s in seats_obj:
            reserved.append(True if s.reserved else False)
        g = SeatForm(request.POST, seats = reserved)
        if not g.is_valid():
            raise RuntimeError("Error: " + str(g.errors))
        seats = g.cleaned_data
        u = (
            User.objects.create(name = values["user"], login = "", password = "")
            if user_login is None
            else User.objects.filter(login = user_login).get()
        )
        for i in range(MAX_SEATS):
            if seats[f"seat_{i + 1}"]:
                s = Seat.objects.filter(showtime = showtime_obj, number = i + 1).get()
                s.reserved = True
                s.user = u
                s.save()
    return u.name

def do_reserve(request):
    user_login = request.session.get("authorized_user_login", None)
    movie_names = [m.name for m in Movie.objects.all()]
    f = ReserveForm(request.POST, movies = movie_names, user = None)

    try:
        user_name = reserve_chance(request, f, user_login)
        result = render(
            request,
            "reservation_result.html",
            {
                "user_name": user_name,
                "movie_name": f.cleaned_data["movies"],
                "timeslot": f.cleaned_data["timeslot"],
            },
        )
    except RuntimeError as e:
        result = render(request, "reservation_result.html", {"error": str(e)})

    return result

    """
def past_reservations(request):
    user_login = request.session.get("authorized_user_login", None)
    p = Patient.objects.filter(login=user_login).get()
    r_list = Reservation.objects.filter(patient=p).order_by("-timeslot")

    return render(
        request,
        "past_reservations.html",
        {
            "user_login": user_login,
            "user_name": p.name,
            "reservations": r_list,
        },
    )
    """