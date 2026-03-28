# campuscare/appointments/urls.py — Step 5
from django.urls import path

from appointments.views import BookSlotView, MyTokenView, SlotListView, queue_count_view

app_name = 'appointments'

urlpatterns = [
    path('', SlotListView.as_view(), name='slot_list'),
    path('slot/<int:slot_id>/book/', BookSlotView.as_view(), name='book'),
    path('my-token/', MyTokenView.as_view(), name='my_token'),
    path('queue/<int:token_id>/', queue_count_view, name='queue_count'),
]
