from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Room(models.Model):
    name = models.CharField('会议室名称',max_length=32)
    capacity = models.IntegerField('容量')

class RoomBooking(models.Model):
    booking_date = models.DateField('预定时间')
    time_choices = (
        (1,'8:00'),
        (2,'9:00'),
        (3,'10:00'),
        (4,'11:00'),
        (6,'12:00'),
        (7,'13:00'),
        (8,'14:00'),
        (9,'15:00'),
        (10,'16:00'),
        (11,'17:00'),
                    )
    booking_time = models.IntegerField('预定时间段',choices=time_choices)
    room = models.ForeignKey(to=Room,verbose_name='预定会议室')
    user = models.ForeignKey(to=User,verbose_name='预定人')