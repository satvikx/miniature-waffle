from rest_framework import serializers
from .models import User, Train, Seat

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        style={'input_type': 'password'}
    )
    confirm_password = serializers.CharField(
        write_only=True, 
        required=True, 
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'password', 'confirm_password']
        extra_kwargs = {
            'username': {'required': True},
            'name': {'required': True}
        }

    def validate(self, data):
        # Check if passwords match
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords must match."})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        
        # Create user
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            name=validated_data['name']
        )
        return user

class TrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields = ['train_no', 'source', 'destination', 'total_seats']
        extra_kwargs = {
            'train_no': {'required': True},
            'source': {'required': True},
            'destination': {'required': True},
            'total_seats': {'required': True, 'min_value': 1}
        }

class TrainAvailabilitySerializer(serializers.ModelSerializer):
    available_seats = serializers.SerializerMethodField()  # Seats Manually added on TR124

    class Meta:
        model = Train
        fields = ['train_no', 'source', 'destination', 'total_seats', 'available_seats']

    def get_available_seats(self, obj):
        return obj.seats.filter(is_booked=False).count()
    

'''
    from your_app.models import Train, Seat
train_id = TR124
train = Train.objects.get(id=train_id)

seats_to_create = []
for seat_no in range(1, 6):
    seats_to_create.append(
        Seat(
            train=train,
            seat_no=f'{seat_no}',  # Convert to string
            is_booked=False
        )
    )

Seat.objects.bulk_create(seats_to_create)

seats = Seat.objects.filter(train=train)
for seat in seats:
    print(seat.seat_no, seat.is_booked)
'''