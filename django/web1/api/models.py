from django.db import models

# python manage.py check
# python manage.py makemigrations api
# python manage.py migrate api

class Item(models.Model):
    objects = models.Manager() # vs code 오류 제거용

    no      = models.AutoField(primary_key=True)
    name    = models.CharField(max_length=30)
    price   = models.IntegerField()
    regdate = models.DateTimeField(auto_now_add=True)
    