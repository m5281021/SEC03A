from django.shortcuts import render
from django.db import transaction
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password, check_password
from django_htmx.http import trigger_client_event

from FirstApp.models import User, Showtime, Seat
from FirstApp.forms import RegisterForm, LoginForm

seat_number = 50
data = '1010-10-10'
movie_name = f'spiderman'

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


def register_form_frame(request, registered = False, error = ""):
    return render(
        request,
        "register_form_user.html",
        {
            "registered": registered,
            "error": error,
            "register_form": RegisterForm(),
        },
    )

""" def register_new_movie_seats(request):
    login = request.session.get("authorized_user_login", None)
    try:
        with transaction.atomic():
            u = User.objects.filter(login = login).get()
            st = Showtime.objects.filter(number = seat_number).get()
            seat = Seat.objects.select_for_update().all()
            seat = Seat(showtime = st, reserved = True, user = u)
            seat.save()
    except RuntimeError:
        return HttpResponse("Something went wrong.")
    return HttpResponse("You completed to register a seat of movie!")

def show_user_movies(request):
    login = request.session.get("authorized_user_login", None)
    try:
        with transaction.atomic():
            s = Seat.objects.filter(user__login = login)
            print(s)
    except RuntimeError:
        return HttpResponse("Something went wrong.")
    return HttpResponse("You can watch your movies!")

def show_matching_movies_date(request):
    try:
        with transaction.atomic():
            show_movie = Showtime.objects.filter(time = date)
            print(show_movie)
    except RuntimeError:
        return HttpResponse("Something went wrong.")
    return HttpResponse("These movies may match you!")

def show_matching_dates_movie(request):
    try:
        with transaction.atomic():
            date = Showtime.objects.filter(movie__name = movie_name)
            print(date)
    except RuntimeError:
        return HttpResponse("Something went wrong.")
    return HttpResponse("These days may match you!") """

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
    f = RegisterForm(request.post)
    event = ""
    try:
        login = register_user_data(f)
        event = "event_login"
        do_login_user(request, login)
    except RuntimeError as e:
        error = str(e)
    response = register_form_frame(request, error is None, error)
    return trigger_client_event(response, event)

def do_check_regform(request):
    f = RegisterForm(request.post)
    r = ""
    u = User.objects.filter(login = f.data["reg_login"])
    if len(u) != 0:
        r = "Login already used!"
    if f.data["reg_password"] != f.data["passagain"]:
        r = "Password do not match!"
    return HttpResponse(r)

def do_login_user(request, login):
    request.session["authorized_user_login"] = login


""" def do_login(request):
    f = LoginForm(request.POST)
    error = ""
    evt = ""
    try:
        if not f.is_valid():
            raise RuntimeError()

        p = Patient.objects.filter(login=f.cleaned_data["login"])
        if len(p) == 0 or not check_password(f.cleaned_data["password"], p[0].password):
            raise RuntimeError()

        do_login_user(request, p[0].login)
        evt = "evt_login"

    except RuntimeError:
        error = "Wrong username or password."

    return trigger_client_event(login_frame(request, error), evt)


def load_login_logout_frame(request):
    return render(request, "test-form.html", {"counter": None})


def do_logout(request):
    request.session["authorized_user_login"] = None
    return trigger_client_event(login_frame(request), "evt_login")


def reserve_form_frame(request):
    login = request.session.get("authorized_user_login", None)
    user_name = None if not login else Patient.objects.filter(login=login).get().name
    doctor_names = [d.name for d in Doctor.objects.all()]
    reserve_form = ReserveForm(doctors=doctor_names, patient=user_name)

    return render(request, "reserve_form_frame.html", {"reserve_form": reserve_form})


def reserve_appointment(f, user_login):
    if not f.is_valid():
        raise RuntimeError("Error: " + str(f.errors))

    with transaction.atomic():
        values = f.cleaned_data
        p = (
            Patient.objects.create(name=values["patient"], login="", password="")
            if user_login is None
            else Patient.objects.filter(login=user_login).get()
        )
        d = Doctor.objects.filter(name=values["doctor"]).get()
        Reservation.objects.create(timeslot=values["timeslot"], doctor=d, patient=p)

        r_count = len(Reservation.objects.filter(timeslot=values["timeslot"], doctor=d))
        if r_count > MAX_DAILY_RESERVATIONS:
            raise RuntimeError("The doctor has too many patients on this day.")


def do_reserve(request):
    user_login = request.session.get("authorized_user_login", None)
    doctor_names = [d.name for d in Doctor.objects.all()]
    f = ReserveForm(request.POST, doctors=doctor_names, patient=None)

    try:
        reserve_appointment(f, user_login)
        result = render(
            request,
            "reservation_result.html",
            {
                "patient_name": f.cleaned_data["patient"],
                "doctor_name": f.cleaned_data["doctor"],
                "timeslot": f.cleaned_data["timeslot"],
            },
        )
    except RuntimeError as e:
        result = render(request, "reservation_result.html", {"error": str(e)})

    return result


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


def do_check_reserve(request):
    doctor_names = [d.name for d in Doctor.objects.all()]
    f = ReserveForm(request.POST, doctors=doctor_names, patient="")

    if f.is_valid():
        # print(f)
        doc_obj = Doctor.objects.filter(name=f.cleaned_data["doctor"]).get()
        date_obj = f.cleaned_data["timeslot"]
        bookings = len(Reservation.objects.filter(timeslot=date_obj, doctor=doc_obj))
        r = " " if bookings < MAX_DAILY_RESERVATIONS else "This day is fully booked"
        return HttpResponse(r)

    return HttpResponse("") """