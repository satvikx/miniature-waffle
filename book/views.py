from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .serializers import UserRegistrationSerializer, TrainSerializer, TrainAvailabilitySerializer
from .models import Train, Booking, Seat
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from django.db import transaction

class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            # Create user
            user = serializer.save()
            
            #  token for the user
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'name': user.name
                },
                'token': token.key
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        
        if user:
            # Generate or get existing token
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                'token': token.key,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'name': user.name,
                    'is_admin': user.is_admin
                }
            })
        
        return Response(
            {'error': 'Invalid Credentials'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )

class AddTrainView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Additional checks for admin
        if not request.user.is_admin:
            return Response(
                {"error": "Only administrators can add trains"}, 
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = TrainSerializer(data=request.data)
        if serializer.is_valid():
            train = serializer.save()
            return Response({
                "message": "Train added successfully",
                "train": {
                    "train_no": train.train_no,
                    "source": train.source,
                    "destination": train.destination
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class TrainAvailabilityView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        print("User:", request.user)
        print("Is Authenticated:", request.user.is_authenticated)

        source = request.query_params.get('source')
        destination = request.query_params.get('destination')

        print(source, destination)

        if not source or not destination:
            return Response(
                {"error": "Please provide both source and destination"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Find trains matching the source and destination
        trains = Train.objects.filter(
            source__icontains=source, 
            destination__icontains=destination
        )

        if not trains.exists():
            return Response(
                {"message": "No trains found for the given route"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Serialize train data with availability
        serializer = TrainAvailabilitySerializer(trains, many=True)
        return Response(serializer.data)
    

class SeatBookingView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        train_no = request.data.get('train_no')
        
        # Validate input
        if not train_no:
            return Response(
                {"error": "Train number is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            train = Train.objects.get(train_no=train_no)
            available_seat = Seat.objects.filter(
                train=train, 
                is_booked=False
            ).first()

            # print(available_seat)

            if not available_seat:
                return Response(
                    {"error": "No seats available on this train"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create booking
            booking = Booking.objects.create(
                user=request.user,
                train=train,
                seat=available_seat
            )

            # Mark seat as booked
            available_seat.is_booked = True
            available_seat.booked_by = request.user
            available_seat.save()

            return Response({
                "message": "Seat booked successfully",
                "booking_details": {
                    "booking_id": booking.id,
                    "train_no": train.train_no,
                    "seat_no": available_seat.seat_no,
                    "source": train.source,
                    "destination": train.destination
                }
            }, status=status.HTTP_201_CREATED)

        except Train.DoesNotExist:
            return Response(
                {"error": "Train not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class BookingDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, booking_id):
        try:
            # Retrieve booking, ensuring it belongs to the current user
            booking = Booking.objects.get(
                id=booking_id, 
                user=request.user
            )

            return Response({
                "booking_id": booking.id,
                "train_no": booking.train.train_no,
                "seat_no": booking.seat.seat_no,
                "source": booking.train.source,
                "destination": booking.train.destination,
                "booked_at": booking.timestamp,
                "user": booking.user.username
            })

        except Booking.DoesNotExist:
            return Response(
                {"error": "Booking not found"},
                status=status.HTTP_404_NOT_FOUND
            )