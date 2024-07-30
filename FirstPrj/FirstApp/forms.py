from django import forms
from django.forms.widgets import PasswordInput
from django.utils.timezone import datetime

class RegisterForm(forms.Form):
    name = forms.CharField(label = "Name", max_length = 20)
    reg_login = forms.CharField(label = "Login", max_length = 20)
    reg_password = forms.CharField(label = "Password", max_length = 20, widget = forms.PasswordInput())
    passagain = forms.CharField(label = "Password again", max_length = 20, widget = forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["reg_login"].widget.attrs["hx-post"] = "/do_check_regform"
        self.fields["reg_password"].widget.attrs["hx-post"] = "/do_check_regform"
        self.fields["passagain"].widget.attrs["hx-post"] = "/do_check_regform"
        self.fields["reg_login"].widget.attrs["hx-target"] = "#check_regform_result"
        self.fields["reg_password"].widget.attrs["hx-target"] = "#check_regform_result"
        self.fields["passagain"].widget.attrs["hx-target"] = "#check_regform_result"

class LoginForm(forms.Form):
    login = forms.CharField(label = "Login", max_length = 20)
    password = forms.CharField(label = "Password", max_length = 20, widget = PasswordInput())

class DateInput(forms.DateInput):
    input_type = "date"

class ReserveForm(forms.Form):
    user = forms.CharField(label = "Name", max_length=20)
    movies = forms.ChoiceField(label = "Movie")
    timeslot = forms.DateField(label = "Date", widget = DateInput(attrs = {"min": datetime.now().date()}))

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        movies = kwargs.pop("movies")
        super().__init__(*args, **kwargs)
        self.fields["movies"].choices = zip(movies, movies)
        self.fields["movies"].widget.attrs["hx-post"] = "/do_check_seats"
        self.fields["movies"].widget.attrs["hx-target"] = "#check_reserve_result"
        self.fields["timeslot"].widget.attrs["hx-post"] = "/do_check_seats"
        self.fields["timeslot"].widget.attrs["hx-target"] = "#check_reserve_result"
        if user:
            self.fields["user"].initial = user
            self.fields["user"].widget.attrs["readonly"] = True

class SeatForm(forms.Form):
    seat_1 = forms.BooleanField(widget = forms.CheckboxInput(), required = False)
    seat_2 = forms.BooleanField(widget = forms.CheckboxInput(), required = False)
    seat_3 = forms.BooleanField(widget = forms.CheckboxInput(), required = False)
    seat_4 = forms.BooleanField(widget = forms.CheckboxInput(), required = False)
    seat_5 = forms.BooleanField(widget = forms.CheckboxInput(), required = False)
    
    def __init__(self, *args, **kwargs):
        reserved = kwargs.pop("seats")
        super().__init__(*args, **kwargs)
        for i in range(len(reserved)):
            if reserved[i]:
                self.fields[f"seat_{i + 1}"].widget.attrs["disabled"] = True