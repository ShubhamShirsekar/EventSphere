from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from eventsphereApp.models import Event, Booking, Bookmark
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = 'Load test data for EventSphere application'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing test data before loading new data',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing test data...')
            # Don't delete superuser
            User.objects.filter(is_superuser=False).delete()
            Event.objects.all().delete()
            Booking.objects.all().delete()
            Bookmark.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Cleared existing data'))

        self.stdout.write('Creating test users...')
        users = self.create_users()
        
        self.stdout.write('Creating test events...')
        events = self.create_events(users)
        
        self.stdout.write('Creating test bookings...')
        self.create_bookings(users, events)
        
        self.stdout.write('Creating test bookmarks...')
        self.create_bookmarks(users, events)
        
        self.stdout.write(self.style.SUCCESS('Successfully loaded test data!'))
        self.stdout.write(f'Created {len(users)} users, {len(events)} events')

    def create_users(self):
        users = []
        user_data = [
            {'username': 'alice@example.com', 'email': 'alice@example.com', 'first_name': 'Alice', 'last_name': 'Johnson'},
            {'username': 'bob@example.com', 'email': 'bob@example.com', 'first_name': 'Bob', 'last_name': 'Smith'},
            {'username': 'charlie@example.com', 'email': 'charlie@example.com', 'first_name': 'Charlie', 'last_name': 'Brown'},
            {'username': 'diana@example.com', 'email': 'diana@example.com', 'first_name': 'Diana', 'last_name': 'Davis'},
            {'username': 'eve@example.com', 'email': 'eve@example.com', 'first_name': 'Eve', 'last_name': 'Wilson'},
        ]
        
        for data in user_data:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'email': data['email'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name']
                }
            )
            if created:
                user.set_password('testpass123')
                user.save()
            users.append(user)
        
        return users

    def create_events(self, users):
        events = []
        categories = ['Music', 'Conference', 'Sport', 'Theatre', 'Workshop', 'Festival']
        cities = ['Paris', 'Lyon', 'Marseille', 'Bordeaux', 'Nantes', 'Toulouse']
        
        event_templates = [
            {'title': 'Summer Music Festival', 'category': 'Music', 'price': 50},
            {'title': 'Tech Conference 2025', 'category': 'Conference', 'price': 100},
            {'title': 'Football Championship', 'category': 'Sport', 'price': 30},
            {'title': 'Shakespeare Night', 'category': 'Theatre', 'price': 40},
            {'title': 'Photography Workshop', 'category': 'Workshop', 'price': 75},
            {'title': 'Wine Tasting Festival', 'category': 'Festival', 'price': 60},
            {'title': 'Jazz Evening', 'category': 'Music', 'price': 45},
            {'title': 'Startup Pitch Day', 'category': 'Conference', 'price': 25},
            {'title': 'Marathon 2025', 'category': 'Sport', 'price': 20},
            {'title': 'Comedy Show', 'category': 'Theatre', 'price': 35},
            {'title': 'Cooking Masterclass', 'category': 'Workshop', 'price': 80},
            {'title': 'Street Food Festival', 'category': 'Festival', 'price': 15},
        ]
        
        for i, template in enumerate(event_templates):
            starts_at = datetime.now() + timedelta(days=random.randint(10, 90))
            ends_at = starts_at + timedelta(hours=random.randint(2, 8))
            
            event = Event.objects.create(
                title=template['title'],
                city=random.choice(cities),
                user_id=users[i % len(users)],  # Distribute events among users
                starts_at=starts_at,
                ends_at=ends_at,
                address=f"{random.randint(1, 100)} Main Street",
                pincode=random.randint(10000, 99999),
                category=template['category'],
                description=f"An amazing {template['category'].lower()} event that you won't want to miss! Join us for an unforgettable experience.",
                image=f"https://picsum.photos/400/300?random={i}",
                ticket_price=template['price']
            )
            events.append(event)
        
        return events

    def create_bookings(self, users, events):
        # Create random bookings
        for event in events:
            # Each event gets 0-10 random bookings
            num_bookings = random.randint(0, 10)
            random_users = random.sample(users, min(num_bookings, len(users)))
            
            for user in random_users:
                Booking.objects.create(
                    event_id=event,
                    user_id=user
                )

    def create_bookmarks(self, users, events):
        # Create random bookmarks
        for user in users:
            # Each user bookmarks 0-5 random events
            num_bookmarks = random.randint(0, 5)
            random_events = random.sample(events, min(num_bookmarks, len(events)))
            
            for event in random_events:
                Bookmark.objects.get_or_create(
                    user=user,
                    event=event
                )