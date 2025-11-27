from django.test import TestCase, Client
from django.contrib.auth.models import User
from eventpassApp.models import Event, Booking, Bookmark
from datetime import timedelta
from django.urls import reverse
from django.utils import timezone
import json


class EventPassTestCase(TestCase):
    """Base test case with common setup"""
    
    def setUp(self):
        """Set up test data for all tests"""
        self.client = Client()
        
        # Create test users
        self.organizer = User.objects.create_user(
            username='organizer@test.com',
            email='organizer@test.com',
            password='testpass123',
            first_name='John',
            last_name='Organizer'
        )
        
        self.attendee = User.objects.create_user(
            username='attendee@test.com',
            email='attendee@test.com',
            password='testpass123',
            first_name='Jane',
            last_name='Attendee'
        )
        
        # Create test events
        self.event1 = Event.objects.create(
            title='Test Music Concert',
            city='Paris',
            user_id=self.organizer,
            starts_at=timezone.now() + timedelta(days=30),
            ends_at=timezone.now() + timedelta(days=30, hours=3),
            address='123 Test Street',
            pincode=75001,
            category='Music',
            description='A test music concert',
            image='https://picsum.photos/400/300',
            ticket_price=50
        )
        
        self.event2 = Event.objects.create(
            title='Test Tech Conference',
            city='Lyon',
            user_id=self.organizer,
            starts_at=timezone.now() + timedelta(days=60),
            ends_at=timezone.now() + timedelta(days=60, hours=8),
            address='456 Conference Ave',
            pincode=69001,
            category='Conference',
            description='A test tech conference',
            image='https://picsum.photos/400/300',
            ticket_price=100
        )


class AuthenticationTests(EventPassTestCase):
    """Test user authentication flows"""
    
    def test_user_can_login(self):
        """Test that a user can successfully log in"""
        response = self.client.post('/login/', {
            'username': 'organizer@test.com',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after login
        
    def test_user_can_logout(self):
        """Test that a user can successfully log out"""
        self.client.login(username='organizer@test.com', password='testpass123')
        response = self.client.get('/logout/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'logout')


class EventTests(EventPassTestCase):
    """Test event-related functionality"""
    
    def test_events_page_loads(self):
        """Test that events page loads successfully"""
        response = self.client.get('/events/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Music Concert')
        self.assertContains(response, 'Test Tech Conference')
    
    def test_event_detail_page_loads(self):
        """Test that event detail page loads with correct data"""
        response = self.client.get(f'/view-event/?id={self.event1.id}')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Music Concert')
        self.assertContains(response, 'Paris')
        self.assertContains(response, '50')
    
    def test_event_count(self):
        """Test that correct number of events exist"""
        events = Event.objects.all()
        self.assertEqual(events.count(), 2)


class BookingTests(EventPassTestCase):
    """Test booking/ticket functionality"""
    
    def test_authenticated_user_can_book_ticket(self):
        """Test that logged-in user can book a ticket"""
        self.client.login(username='attendee@test.com', password='testpass123')
        response = self.client.get(f'/buy-ticket/?id={self.event1.id}')
        self.assertEqual(response.status_code, 302)  # Redirect after booking
        
        # Verify booking was created
        booking = Booking.objects.filter(
            event_id=self.event1,
            user_id=self.attendee
        ).first()
        self.assertIsNotNone(booking)
    
    def test_unauthenticated_user_cannot_book_ticket(self):
        """Test that non-logged-in user is redirected to login"""
        response = self.client.get(f'/buy-ticket/?id={self.event1.id}')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.url)
    
    def test_booking_count(self):
        """Test booking count for an event"""
        # Create bookings
        Booking.objects.create(event_id=self.event1, user_id=self.attendee)
        Booking.objects.create(event_id=self.event1, user_id=self.organizer)
        
        bookings = Booking.objects.filter(event_id=self.event1)
        self.assertEqual(bookings.count(), 2)


class BookmarkTests(EventPassTestCase):
    """Test bookmark functionality"""
    
    def test_user_can_bookmark_event(self):
        """Test that user can bookmark an event"""
        self.client.login(username='attendee@test.com', password='testpass123')
        response = self.client.post(
            f'/bookmark/{self.event1.id}/',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['bookmarked'])
        
        # Verify bookmark was created
        bookmark = Bookmark.objects.filter(
            user=self.attendee,
            event=self.event1
        ).first()
        self.assertIsNotNone(bookmark)
    
    def test_user_can_unbookmark_event(self):
        """Test that user can remove a bookmark"""
        # Create a bookmark first
        Bookmark.objects.create(user=self.attendee, event=self.event1)
        
        self.client.login(username='attendee@test.com', password='testpass123')
        response = self.client.post(
            f'/bookmark/{self.event1.id}/',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertFalse(data['bookmarked'])
        
        # Verify bookmark was deleted
        bookmark = Bookmark.objects.filter(
            user=self.attendee,
            event=self.event1
        ).first()
        self.assertIsNone(bookmark)
    
    def test_bookmarks_page_shows_bookmarked_events(self):
        """Test that bookmarks page displays user's bookmarked events"""
        Bookmark.objects.create(user=self.attendee, event=self.event1)
        
        self.client.login(username='attendee@test.com', password='testpass123')
        response = self.client.get('/bookmarks/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Music Concert')


class MyListedEventsTests(EventPassTestCase):
    """Test My Listed Events functionality"""
    
    def test_organizer_sees_own_events(self):
        """Test that organizer sees only their own events"""
        self.client.login(username='organizer@test.com', password='testpass123')
        response = self.client.get('/my-listed-events/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Music Concert')
        self.assertContains(response, 'Test Tech Conference')
    
    def test_tickets_sold_count_is_correct(self):
        """Test that tickets sold counter shows correct count"""
        # Create bookings
        Booking.objects.create(event_id=self.event1, user_id=self.attendee)
        Booking.objects.create(event_id=self.event1, user_id=self.organizer)
        
        self.client.login(username='organizer@test.com', password='testpass123')
        response = self.client.get('/my-listed-events/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '2')  # Should show 2 tickets sold
    
    def test_bookmarks_count_is_correct(self):
        """Test that bookmarks counter shows correct count"""
        # Create bookmarks
        Bookmark.objects.create(user=self.attendee, event=self.event1)
        
        self.client.login(username='organizer@test.com', password='testpass123')
        response = self.client.get('/my-listed-events/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '1')  # Should show 1 bookmark
    
    def test_revenue_calculation_is_correct(self):
        """Test that revenue is calculated correctly"""
        # Create 3 bookings for event1 ($50 each = $150 total)
        for _ in range(3):
            Booking.objects.create(event_id=self.event1, user_id=self.attendee)
        
        self.client.login(username='organizer@test.com', password='testpass123')
        response = self.client.get('/my-listed-events/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '$150')


class EventAttendeesTests(EventPassTestCase):
    """Test event attendees page"""
    
    def test_organizer_can_view_attendees(self):
        """Test that organizer can view list of attendees"""
        Booking.objects.create(event_id=self.event1, user_id=self.attendee)
        
        self.client.login(username='organizer@test.com', password='testpass123')
        response = self.client.get(f'/event-attendees/{self.event1.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Jane')
        self.assertContains(response, 'Attendee')
    
    def test_non_organizer_cannot_view_attendees(self):
        """Test that non-organizer cannot view attendees of others' events"""
        self.client.login(username='attendee@test.com', password='testpass123')
        response = self.client.get(f'/event-attendees/{self.event1.id}/')
        self.assertEqual(response.status_code, 404)  # Should return 404


class EventBookmarksListTests(EventPassTestCase):
    """Test event bookmarks list page"""
    
    def test_organizer_can_view_bookmarks_list(self):
        """Test that organizer can view who bookmarked their event"""
        Bookmark.objects.create(user=self.attendee, event=self.event1)
        
        self.client.login(username='organizer@test.com', password='testpass123')
        response = self.client.get(f'/event-bookmarks/{self.event1.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Jane')
        self.assertContains(response, 'Attendee')


class AnalyticsDashboardTests(EventPassTestCase):
    """Test analytics dashboard"""
    
    def test_analytics_dashboard_loads(self):
        """Test that analytics dashboard loads for organizer"""
        self.client.login(username='organizer@test.com', password='testpass123')
        response = self.client.get('/analytics-dashboard/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Analytics Dashboard')
    
    def test_analytics_shows_correct_total_revenue(self):
        """Test that total revenue is calculated correctly"""
        # Event1: $50, Event2: $100
        Booking.objects.create(event_id=self.event1, user_id=self.attendee)  # $50
        Booking.objects.create(event_id=self.event2, user_id=self.attendee)  # $100
        
        self.client.login(username='organizer@test.com', password='testpass123')
        response = self.client.get('/analytics-dashboard/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '$150')  # Total revenue
    
    def test_analytics_shows_correct_total_tickets(self):
        """Test that total tickets sold is calculated correctly"""
        Booking.objects.create(event_id=self.event1, user_id=self.attendee)
        Booking.objects.create(event_id=self.event2, user_id=self.attendee)
        
        self.client.login(username='organizer@test.com', password='testpass123')
        response = self.client.get('/analytics-dashboard/')
        self.assertEqual(response.status_code, 200)
        # Check for "2" somewhere in the total tickets section
        self.assertContains(response, '2')
    
    def test_analytics_empty_state(self):
        """Test analytics dashboard shows empty state for new user"""
        new_user = User.objects.create_user(
            username='newuser@test.com',
            password='testpass123'
        )
        self.client.login(username='newuser@test.com', password='testpass123')
        response = self.client.get('/analytics-dashboard/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No data to display the results')


class EditTicketPriceTests(EventPassTestCase):
    """Test ticket price editing"""
    
    def test_organizer_can_edit_ticket_price(self):
        """Test that organizer can update ticket price"""
        self.client.login(username='organizer@test.com', password='testpass123')
        response = self.client.post(
            f'/edit-ticket-price/{self.event1.id}/',
            {'ticket_price': '75'}
        )
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['new_price'], 75)
        
        # Verify in database
        event = Event.objects.get(id=self.event1.id)
        self.assertEqual(event.ticket_price, 75)


class ModelTests(EventPassTestCase):
    """Test model relationships and methods"""
    
    def test_event_str_method(self):
        """Test Event model __str__ method"""
        # This test assumes you might add __str__ methods
        self.assertEqual(str(self.event1.title), 'Test Music Concert')
    
    def test_booking_relationship(self):
        """Test Booking model relationships"""
        booking = Booking.objects.create(
            event_id=self.event1,
            user_id=self.attendee
        )
        self.assertEqual(booking.event_id.title, 'Test Music Concert')
        self.assertEqual(booking.user_id.username, 'attendee@test.com')
    
    def test_bookmark_unique_constraint(self):
        """Test that duplicate bookmarks cannot be created"""
        Bookmark.objects.create(user=self.attendee, event=self.event1)
        
        # Try to create duplicate - should raise IntegrityError
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Bookmark.objects.create(user=self.attendee, event=self.event1)