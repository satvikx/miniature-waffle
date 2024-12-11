from django.urls import path
from .views import UserRegistrationView, UserLoginView, AddTrainView, TrainAvailabilityView, SeatBookingView, BookingDetailsView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-registration'),
    path('login/', UserLoginView.as_view(), name='user-login'), 
    # Add Train (Admin Only)
    path('admin/add-train/', AddTrainView.as_view(), name='add-train'),

    path('trains/availability/', TrainAvailabilityView.as_view(), name='train-availability'),
    
    path('book-seat/', SeatBookingView.as_view(), name='book-seat'),
    
    path('booking/<int:booking_id>/', BookingDetailsView.as_view(), name='booking-details'),
]