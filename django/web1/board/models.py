from django.db import models

# Create your models here.

class Table1(models.Model):
    object  = models.Manager() # vs code 오류 밑줄 제거용, 안써도 된다.

    no      = models.AutoField(primary_key=True)
    title   = models.CharField(max_length=200)
    content = models.TextField()
    writer  = models.CharField(max_length=50)
    hit     = models.IntegerField()
    img     = models.BinaryField(null=True) # 바이너리 필드
    regdate = models.DateField(auto_now_add=True)