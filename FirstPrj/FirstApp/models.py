from django.db import models

class User(models.Model):
    name = models.CharField(max_length = 20)
    
    def __str__(self):
        return self.name

class Movie(models.Model):
    name = models.CharField(max_length = 20)
    
    def __str__(self):
        return self.name

class Showtime(models.Model):
    time = models.DateField()
    number = models.IntegerField()
    movie = models.ForeignKey(Movie, on_delete = models.CASCADE, related_name = 'movies')
    
    def __str__(self):
        return f'{str(self.time)} {str(self.number)} [{str(self.movie)}]'

class Seat(models.Model):
    showtime = models.ForeignKey(Showtime, on_delete = models.CASCADE, related_name = 'showtimes')
    reserved = models.BooleanField()
    user = models.ForeignKey(User, on_delete = models.PROTECT, related_name = 'users')
    
    def __str__(self):
        return f'{str(self.showtime)} {str(self.user)} {str(self.reserved)}'