from django.db import models
from django.contrib.auth.models import User
import uuid

class Plant(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=60)
    description = models.TextField(max_length=200)

    moisture_min = models.FloatField()
    moisture_max = models.FloatField()
    temp_min = models.FloatField()
    temp_max = models.FloatField()
    light_min = models.FloatField()
    light_max = models.FloatField()

    def __str__(self):
        return self.name
    
class Pot(models.Model):
    owner = models.ForeignKey(User ,on_delete=models.CASCADE ,related_name="pots")#related_name = yazabılmemız ıcın
    name = models.CharField(max_length=50) #kullanıcının sakısıya verdıgı ısım 
    plant = models.ForeignKey(Plant, on_delete=models.SET_NULL,null=True,blank=True, related_name="pots") #bir saksıya bir bitki atanır ,set_null cunku bıtkı sılınce saksı sılınmıyor
    created_at = models.DateTimeField(auto_now_add=True)

    device_token = models.UUIDField(default=uuid.uuid4 ,unique=True ,editable=False)

    def __str__(self):
        return self.name
    
class Reading(models.Model):
    pot = models.ForeignKey(Pot, on_delete=models.CASCADE, related_name="readings")
    moisture= models.FloatField()
    temp = models.FloatField()
    light = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta: #reading sorgusu yapıldıgında en ustteki degeri dondur yani en yeni veri en uste gelir
        ordering = ["-created_at"]


class Command(models.Model): #mobil/react/unity bir islem istediginde bu istegi veritabanına kaydeder
    STATUS_PENDING = "pending"#mobıl ıstek atı ıstek db kaydedıldı
    STATUS_DONE = "done" #komutu alır sulama yapar
    STATUS_FAILED = "failed" #hata oldu

    STATUS_CHOICES = [
        (STATUS_PENDING , "Pending"),
        (STATUS_DONE , "Done" ),
        (STATUS_FAILED , "Failed"),
    ]

    pot = models.ForeignKey(Pot, on_delete=models.CASCADE, related_name="commands")
    command_type = models.CharField(max_length=50) #ne yapılacak - sulama ısık acma..
    value = models.IntegerField()
    status = models.CharField(max_length=20 ,choices=STATUS_CHOICES ,default=STATUS_PENDING) #hangi asamada oldugunu belırtır. pending, done ..
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]






