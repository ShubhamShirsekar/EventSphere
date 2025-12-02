from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Event, Booking, Ticket
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q
from django.core.files.storage import FileSystemStorage
from django.templatetags.static import static
from django.utils import timezone
from django.db import models
# --- Image Upload to CDN ---
import os
import sys
import base64
import requests
from dotenv import load_dotenv
load_dotenv('.env')
import datetime
# ---------------------------
# --- Bookmark Events ----
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Bookmark
# ---------------------------

# def appHome(request):
#     event_records = Event.objects.all().order_by('id')[:5]
#     return render(request, 'index.html', context={'user': request.user, 'event_records': event_records})
def appHome(request):
    # Get the latest 5 events
    event_records = Event.objects.all().order_by('id')[:5]

    # Render the home page with events
    return render(request, 'index.html', context={
        'user': request.user,
        'event_records': event_records
    })

def signup(request):
    if request.user.is_authenticated:
        return redirect('/profile')

    if request.method == "POST":
        first_name = request.POST.get('first_name')
        
        user = User.objects.create(
            first_name = request.POST.get('name'),
            username = request.POST.get('email')
        )
        user.set_password(request.POST.get('password'))
        user.save()
        return redirect('/login')

    else:
        return render(request, 'signup.html')

def loginUser(request):
    if request.user.is_authenticated:
        return redirect('/profile')

    if request.method == "POST":
        username = request.POST.get("email")
        password = request.POST.get("password")

        if not User.objects.filter(username=username).exists():
            messages.error(request, 'Invalid Usernaame')
            return redirect('/login/')
        
        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, "Invalid Password")
            return redirect('/login/')
        else:
            login(request, user)

        return redirect('/profile/')
    
    else:
        return render(request, "login.html")

def logoutUser(request):
    if request.method == "POST":
        logout(request)
        return redirect('/')
    
    if request.user.is_authenticated:
        return render(request, 'logout.html', context={'user': request.user})
    else:
        return redirect('/login')


def profile(request):
    if request.user.is_authenticated:
        return render(request, "profile.html", context={'user': request.user})
    else:
        return redirect('/login/')


def about(request):
    return render(request, 'about.html', context={'user': request.user})        


# def eventsPage(request):
#     # fill events into the template

#     return render(request, 'events.html', context={'user': request.user})

def eventsPage(request):
    print(">>> eventsPage() CALLED <<<", flush=True)

    # Get all events (newest first)
    event_records = Event.objects.all().order_by('-id')
    print(f">>> Retrieved {len(event_records)} events <<<", flush=True)
    
    # Add bookmark information
    bookmarked_event_ids = []
    if request.user.is_authenticated:
        bookmarked_event_ids = list(
            Bookmark.objects.filter(user=request.user).values_list('event_id', flat=True)
        )

    return render(request, 'events.html', context={
        'user': request.user,
        'event_records': event_records,
        'bookmarked_event_ids': bookmarked_event_ids
    })

def createEvent(request):
    print(">>> createEvent() CALLED <<<", flush=True)

    if not request.user.is_authenticated:
        print(">>> User not authenticated, redirecting to login <<<", flush=True)
        return redirect('/login')

    if request.method == "POST":
        print(">>> STEP 1: Entered POST block", flush=True)
        print(">>> POST data:", request.POST, flush=True)
        print(">>> FILES:", request.FILES, flush=True)

        # Extract all form fields
        title = request.POST.get('event-title')
        event_type = request.POST.get('event-type')
        address = request.POST.get('location-address')
        city = request.POST.get('location-city')
        pincode = request.POST.get('location-pincode')
        start_datetime_str = request.POST.get('start-date-time')  # "2025-11-07T10:00"
        start_datetime = datetime.datetime.strptime(start_datetime_str, "%Y-%m-%dT%H:%M")
        start_datetime = timezone.make_aware(start_datetime)
        # start_datetime = request.POST.get('start-date-time')
        end_datetime = request.POST.get('end-date-time')
        description = request.POST.get('event-description')
        ticket_price = request.POST.get('ticket-price')
        image_file = request.FILES.get('image-upload')

        # Default images map
        default_images = {
            "music": "https://www.goodmedicinemusic.com/wp-content/uploads/2018/04/10_Hundred-Waters_Music-Hall-of-Williamsburg.jpg",
            "conference": "https://media.licdn.com/dms/image/v2/D4D12AQFxuo8CWk6qIg/article-cover_image-shrink_720_1280/article-cover_image-shrink_720_1280/0/1681980612057?e=2147483647&v=beta&t=f9M7hoyYpXFYlLmwfvzCWg4qyzF6ixX36j3jIOnCfa0",
            "sport": "https://www.coe.int/documents/24916852/0/Supporters3.jpg",
            "theatre": "https://res.cloudinary.com/simpleview/image/upload/v1645649075/clients/fairfax-redesign/Events_Capital_One_Hall_943397d7-a016-412c-8c28-3f722f2a26ea.png",
            "workshop": "https://images.stockcake.com/public/c/1/6/c16363bd-4aec-4b52-a658-97b792e336a5_large/team-coding-session-stockcake.jpg",
            "festival": static("images/default_festival.jpg")
        }

        # Debug
        print(f">>> STEP 2: Got image file = {image_file}", flush=True)

        image_url = None
        if image_file:
            try:
                imgbb_key = os.environ.get("IMGBB_KEY")
                if imgbb_key:
                    image_bytes = image_file.read()
                    response = requests.post(
                        'https://api.imgbb.com/1/upload',
                        params={'key': imgbb_key},
                        files={'image': (image_file.name, image_bytes, image_file.content_type)}
                    )
                    response_data = response.json()
                    print(">>> imgbb response:", response_data, flush=True)
                    if response.status_code == 200 and 'data' in response_data:
                        image_url = response_data['data']['url']
                else:
                    print(">>> ERROR: IMGBB_KEY not found in environment variables <<<", flush=True)
            except Exception as e:
                print(">>> EXCEPTION during image upload:", str(e), flush=True)

        # If no image uploaded, assign default
        if not image_url:
            image_url = default_images.get(event_type.lower(), static("images/default_generic.jpg"))

        # Create the event object
        try:
            event = Event.objects.create(
                title=title,
                category=event_type,
                address=address,
                city=city,
                pincode=pincode,
                starts_at=start_datetime,
                ends_at=end_datetime,
                description=description,
                ticket_price=ticket_price,
                image=image_url,
                user_id=request.user
            )

            print(f">>> STEP 3: Event '{event.title}' created successfully <<<", flush=True)
            return redirect('/events')
        except Exception as e:
            print(">>> ERROR creating event:", str(e), flush=True)
            return render(request, 'event_create_form.html', {
                'user': request.user,
                'error': 'Failed to create event. Check logs for details.'
            })

    # GET request: render empty form
    print(">>> Rendering event_create_form.html (GET) <<<", flush=True)
    return render(request, 'event_create_form.html', context={'user': request.user})

def myTicketsList(request):
    if request.user.is_authenticated:
        # get the userid
        user_id = request.user.id
        # for that userid get the tickets record
        ticket_records = Booking.objects.filter(user_id=user_id).select_related('event_id')
        
        # Group tickets by event
        grouped_tickets = {}
        for t_record in ticket_records:
            event_record = t_record.event_id
            event_id = event_record.id
            
            if event_id not in grouped_tickets:
                grouped_tickets[event_id] = {
                    'event_name': event_record.title,
                    'dateTime': event_record.starts_at,
                    'location': event_record.city,
                    'event_image': event_record.image,
                    'tickets': []
                }
            
            ticket = {
                'id': t_record.id,
                'is_cancelled': t_record.is_cancelled,
                'can_cancel': t_record.can_cancel(),
                'booked_at': t_record.booked_at
            }
            grouped_tickets[event_id]['tickets'].append(ticket)
        
        # Convert to list and calculate counts
        grouped_tickets_list = []
        for event_id, data in grouped_tickets.items():
            data['event_id'] = event_id
            data['total_tickets'] = len(data['tickets'])
            data['active_tickets'] = sum(1 for t in data['tickets'] if not t['is_cancelled'])
            data['cancelled_tickets'] = sum(1 for t in data['tickets'] if t['is_cancelled'])
            grouped_tickets_list.append(data)
        
        # Sort by most recent booking
        grouped_tickets_list.sort(key=lambda x: max(t['booked_at'] for t in x['tickets']), reverse=True)
        
        # pass to the template
        return render(request, 'mytickets.html', context={'grouped_tickets': grouped_tickets_list})
    else:
        return redirect('/login')


def showTicket(request):
    ticket_id = request.GET.get('id')
    user_id = request.user.id
    ticket_record = Booking.objects.get(id=ticket_id)
    # check if this userid have access to the request ticket using ticket id
    if ticket_record.user_id.id == user_id:
        ticket = {}
        ticket['id'] = ticket_record.id
        ticket['ename'] = ticket_record.event_id.title
        ticket['dateTime'] = ticket_record.event_id.starts_at
        ticket['location'] = ticket_record.event_id.city
        ticket['holder'] = ticket_record.user_id.first_name

        return render(request, 'ticket.html', context={'ticket': ticket})
    else:
        return redirect('/my-tickets')
        

def searchResults(request):
    search_query = request.GET.get('query', '').strip()
    search_date = request.GET.get('date', '').strip()
    search_type = request.GET.get('search-type', '').strip()
    
    # Start with all events
    event_records = Event.objects.all()
    
    # Filter by search query if provided
    if search_query:
        if search_type == 'name':
            # Search only by name
            event_records = event_records.filter(title__icontains=search_query)
        elif search_type == 'location':
            # Search only by location
            event_records = event_records.filter(city__icontains=search_query)
        else:
            # Search in both title and city
            query = Q(title__icontains=search_query)
            query.add(Q(city__icontains=search_query), Q.OR)
            event_records = event_records.filter(query)
    
    # Filter by date if provided (applies regardless of search_type)
    if search_date:
        try:
            # Parse the date from the date input (format: YYYY-MM-DD)
            search_datetime = datetime.datetime.strptime(search_date, '%Y-%m-%d')
            search_datetime = timezone.make_aware(search_datetime)
            next_day = search_datetime + datetime.timedelta(days=1)
            
            # Filter events that start on the selected date
            event_records = event_records.filter(
                starts_at__gte=search_datetime,
                starts_at__lt=next_day
            )
        except ValueError:
            messages.error(request, 'Invalid date format.')
    
    # If no search parameters provided at all, redirect to home
    if not search_query and not search_date:
        return redirect('/')
    
    # Pass search values back to template to preserve them
    context = {
        'event_records': event_records,
        'search_query': search_query,
        'search_date': search_date,
        'search_type': search_type
    }
    
    return render(request, 'events.html', context=context)

def viewEvent(request):
    event_id = request.GET.get('id')
    if event_id:
        event = Event.objects.get(id=event_id)
        organizer = User.objects.get(id=event.user_id_id).first_name
        
        # Add bookmark check
        bookmarked_event_ids = []
        if request.user.is_authenticated:
            bookmarked_event_ids = list(
                Bookmark.objects.filter(user=request.user, event=event).values_list('event_id', flat=True)
            )
        
        return render(request, 'view_event.html', context={
            'event': event, 
            'organizer': organizer,
            'bookmarked_event_ids': bookmarked_event_ids
        })
    else:
        return HttpResponse(status=204)

def buyTicket(request):
    if request.user.is_authenticated:
        event_id = request.GET.get('id')

        event_record = Event.objects.get(id=event_id)
        user_record = User.objects.get(id=request.user.id)
        Booking.objects.create(
            event_id=event_record,
            user_id=user_record
        )
        return redirect('/my-tickets')

    else:
        return redirect('/login')

@login_required
@require_POST
def cancel_ticket(request, booking_id):
    """Cancel a ticket booking if 5 or more days before event"""
    booking = get_object_or_404(Booking, id=booking_id, user_id=request.user)
    
    if booking.can_cancel():
        booking.is_cancelled = True
        booking.cancelled_at = timezone.now()
        booking.save()
        messages.success(request, f"Ticket for '{booking.event_id.title}' has been cancelled successfully.")
    else:
        if booking.is_cancelled:
            messages.error(request, "This ticket has already been cancelled.")
        else:
            messages.error(request, "Cannot cancel ticket. Must be at least 5 days before the event.")
    
    return redirect('/my-tickets')
    
def deleteEvent(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    # Only event creator can delete
    if event.user_id != request.user:
        messages.error(request, "You are not allowed to delete this event.")
        return redirect('/events')

    # Check if tickets have been sold
    tickets_sold = Ticket.objects.filter(event=event).count()
    if tickets_sold > 0:
        messages.error(request, "Cannot delete event. Tickets have already been sold.")
        return redirect('/events')

    # Delete event
    event.delete()
    messages.success(request, "Event deleted successfully.")
    return redirect('/events')

@login_required
@require_POST
def toggle_bookmark(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, event=event)
    
    if not created:
        bookmark.delete()
        return JsonResponse({'bookmarked': False})
    
    return JsonResponse({'bookmarked': True})

@login_required
def bookmarked_events(request):
    bookmarks = Bookmark.objects.filter(user=request.user).select_related('event')
    bookmarked_events_list = [bookmark.event for bookmark in bookmarks]
    
    context = {
        'events': bookmarked_events_list,
        'page_title': 'Bookmarked Events'
    }
    return render(request, 'bookmarks.html', context)

@login_required
def my_listed_events(request):
    # Get all events created by the logged-in user
    user_events = Event.objects.filter(user_id=request.user).order_by('-id')
    
    # Calculate stats for each event
    events_with_stats = []
    for event in user_events:
        # Count bookings (tickets sold) for this event
        bookings_count = Booking.objects.filter(event_id=event).count()
        
        bookmarks_count = Bookmark.objects.filter(event=event).count()
        
        events_with_stats.append({
            'event': event,
            'tickets_sold': bookings_count,
            'bookmarks_count': bookmarks_count,
            'revenue': bookings_count * event.ticket_price
        })
    
    context = {
        'events_with_stats': events_with_stats
    }
    return render(request, 'my_listed_events.html', context)


@login_required
def event_attendees(request, event_id):
    event = get_object_or_404(Event, id=event_id, user_id=request.user)
    
    # Get all bookings for this event
    bookings = Booking.objects.filter(event_id=event).select_related('user_id').order_by('-id')
    
    # Calculate total revenue (each booking = 1 ticket in your current model)
    total_bookings = bookings.count()
    total_revenue = total_bookings * event.ticket_price
    
    context = {
        'event': event,
        'bookings': bookings,
        'total_revenue': total_revenue
    }
    return render(request, 'event_attendees.html', context)


@login_required
def event_bookmarks_list(request, event_id):
    event = get_object_or_404(Event, id=event_id, user_id=request.user)
    
    # Get all bookmarks for this event
    bookmarks = Bookmark.objects.filter(event=event).select_related('user').order_by('-created_at')
    
    context = {
        'event': event,
        'bookmarks': bookmarks
    }
    return render(request, 'event_bookmarks_list.html', context)


@login_required
def edit_ticket_price(request, event_id):
    event = get_object_or_404(Event, id=event_id, user_id=request.user)
    
    if request.method == 'POST':
        new_price = request.POST.get('ticket_price')
        if new_price:
            try:
                event.ticket_price = int(new_price)
                event.save()
                return JsonResponse({'success': True, 'new_price': event.ticket_price})
            except ValueError:
                return JsonResponse({'success': False, 'error': 'Invalid price'})
    
    return JsonResponse({'success': False})

@login_required
def analytics_dashboard(request):
    # Get all events created by the logged-in user
    user_events = Event.objects.filter(user_id=request.user)
    
    # Check if user has any events
    if not user_events.exists():
        context = {
            'has_data': False,
            'message': 'No data to display the results'
        }
        return render(request, 'analytics_dashboard.html', context)
    
    # Calculate total revenue and tickets sold
    total_tickets_sold = 0
    total_revenue = 0
    event_stats = []
    category_revenue = {}
    
    for event in user_events:
        bookings_count = Booking.objects.filter(event_id=event).count()
        revenue = bookings_count * event.ticket_price
        
        total_tickets_sold += bookings_count
        total_revenue += revenue
        
        event_stats.append({
            'title': event.title,
            'tickets_sold': bookings_count,
            'revenue': revenue
        })
        
        # Aggregate by category
        if event.category in category_revenue:
            category_revenue[event.category] += revenue
        else:
            category_revenue[event.category] = revenue
    
    # Sort events by tickets sold and get top 5
    top_5_events = sorted(event_stats, key=lambda x: x['tickets_sold'], reverse=True)[:5]
    
    # Sort categories by revenue and get top 5
    top_5_categories = sorted(category_revenue.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Calculate percentage for pie chart (all events)
    event_revenue_percentage = []
    if total_revenue > 0:
        for stat in event_stats:
            if stat['revenue'] > 0:
                percentage = (stat['revenue'] / total_revenue) * 100
                event_revenue_percentage.append({
                    'title': stat['title'],
                    'revenue': stat['revenue'],
                    'percentage': round(percentage, 2)
                })
    
    context = {
        'has_data': True,
        'total_revenue': total_revenue,
        'total_tickets_sold': total_tickets_sold,
        'top_5_events': top_5_events,
        'top_5_categories': top_5_categories,
        'event_revenue_percentage': event_revenue_percentage,
    }
    
    return render(request, 'analytics_dashboard.html', context)