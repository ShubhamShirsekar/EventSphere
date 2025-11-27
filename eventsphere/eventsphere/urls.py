"""
URL configuration for EventSphere project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from eventsphereApp import views
from eventsphereApp.views import *
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', appHome, name='Home'),

    path('login/', loginUser, name='Login'),

    path('signup/', signup, name='Signup'),
 
    path('logout/', logoutUser, name='Logout'),

    path('profile/', profile, name='Profile'),

    path('search/', searchResults, name='SearchResults'),

    path('events/', eventsPage, name='EventsPage'),

    path('bookmark/<int:event_id>/', views.toggle_bookmark, name='toggle_bookmark'),

    path('bookmarks/', views.bookmarked_events, name='bookmarked_events'),

    path('my-listed-events/', views.my_listed_events, name='my_listed_events'),

    path('analytics-dashboard/', views.analytics_dashboard, name='analytics_dashboard'),  # ADD THIS LINE

    path('event-attendees/<int:event_id>/', views.event_attendees, name='event_attendees'),

    path('event-bookmarks/<int:event_id>/', views.event_bookmarks_list, name='event_bookmarks_list'),

    path('edit-ticket-price/<int:event_id>/', views.edit_ticket_price, name='edit_ticket_price'),

    path('view-event/', viewEvent, name='ViewEvent'),

    path('create-event/', createEvent, name='CreateEvent'),

    path('buy-ticket/', buyTicket, name='BuyTicket'),

    path('cancel-ticket/<int:booking_id>/', views.cancel_ticket, name='cancel_ticket'),

    path('my-tickets/', myTicketsList, name='MyTickets'),

    path('ticket/', showTicket, name='Ticket'),
 
    path('about/', about, name='About'),

    path('admin/', admin.site.urls),

    path('delete-event/<int:event_id>/', views.deleteEvent, name='delete_event')
]

# https://testdriven.io/blog/django-static-files/
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)