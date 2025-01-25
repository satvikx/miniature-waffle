from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import MinLengthValidator

class CustomUserManager(BaseUserManager): 
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('Username must be set')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_staff', True)
        
        return self.create_user(username, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    username = models.CharField(
        max_length=50, 
        unique=True, 
        validators=[MinLengthValidator(4)]
    )
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Automatically set is_admin for superusers
        if self.is_superuser:
            self.is_admin = True
        super().save(*args, **kwargs)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.username

class Train(models.Model):
    train_no = models.CharField(
        max_length=20,
        primary_key=True,
        unique=True
    )
    source = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    total_seats = models.IntegerField(default=5)
    available_seats = models.IntegerField(default=0)

    def create_seats(self):
        """
        Automatically add seats to train
        """
        #to prevent duplicate creation
        self.seats.all().delete()

        # Create seats
        seats_to_create = [
            Seat(
                train=self,
                seat_no=f'{seat_no}',  # Convert to string
                is_booked=False
            ) for seat_no in range(1, self.total_seats + 1)
        ]
       
        # Bulk create seats
        Seat.objects.bulk_create(seats_to_create)
        
        self.available_seats = self.total_seats
        self.save()

    def save(self, *args, **kwargs):
#Save the train
        super().save(*args, **kwargs)
        
        # Create seats after saving if not already created
        if self.total_seats > 0 and self.seats.count() == 0:
            self.create_seats()

    def __str__(self):
        return f"{self.train_no} - {self.source} to {self.destination}"
    
class Seat(models.Model):
    class Meta:
        unique_together = ['seat_no', 'train']

    seat_no = models.CharField(max_length=10)
    train = models.ForeignKey(
        Train, 
        on_delete=models.CASCADE, 
        related_name='seats'
    )
    is_booked = models.BooleanField(default=False)
    booked_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='booked_seats'
    )

    def __str__(self):
        return f"{self.seat_no} - Train {self.train.train_no}"

class Booking(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='bookings'
    )
    train = models.ForeignKey(
        Train, 
        on_delete=models.CASCADE, 
        related_name='bookings'
    )
    seat = models.ForeignKey(
        Seat, 
        on_delete=models.CASCADE, 
        related_name='booking'
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'train', 'seat']

    def __str__(self):
        return f"Booking {self.id} - {self.user.username} - {self.train.train_no}"