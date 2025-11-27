# EventSphere 

**EventSphere** is a comprehensive event management and ticketing platform built with Django. It provides a seamless experience for both event organizers and attendees, making event discovery, booking, and management effortless.

##  About

EventSphere simplifies the entire event lifecycle - from creation to attendance. Whether you're an organizer looking to host and manage events or an attendee searching for exciting experiences, EventSphere provides all the tools you need in one intuitive platform.

##  Features

### For Event Attendees
- **Event Discovery**: Browse and search for events by category, location, or keywords
- **Advanced Search**: Filter events based on your preferences
- **Event Booking**: Secure ticket booking with quantity selection
- **Bookmark Events**: Save interesting events for later viewing
- **My Tickets**: View all your booked tickets in one place
- **Ticket Cancellation**: Cancel bookings up to 5 days before the event
- **User Profile**: Manage your account and view booking history

### For Event Organizers
- **Create Events**: Easy-to-use event creation form with image upload
- **Event Management**: View and manage all your listed events
- **Analytics Dashboard**: Track event performance and bookings
- **Attendee Management**: View list of attendees for each event
- **Bookmark Insights**: See how many users bookmarked your events

### Additional Features
- **User Authentication**: Secure signup, login, and logout functionality
- **Responsive Design**: Works seamlessly across desktop and mobile devices
- **Image CDN Integration**: Fast image loading with cloud storage
- **Real-time Updates**: Dynamic booking status and availability

##  Tech Stack

- **Backend**: Django 4.2.2
- **Database**: PostgreSQL (with psycopg2-binary)
- **Frontend**: HTML, CSS, JavaScript
- **Image Processing**: Pillow
- **Environment Management**: python-dotenv
- **Additional Libraries**: requests, urllib3

##  Prerequisites

- Python 3.8+
- PostgreSQL
- pip (Python package manager)

##  Installation

1. **Clone the repository**
   `bash
   git clone https://github.com/ShubhamShirsekar/EventSphere.git
   cd EventSphere
   `

2. **Create a virtual environment**
   `bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   `

3. **Install dependencies**
   `bash
   pip install -r requirements.txt
   `

4. **Set up environment variables**
   - Copy .env.example to .env
   - Configure your database credentials and other settings

5. **Run migrations**
   `bash
   python manage.py migrate
   `

6. **Load test data (optional)**
   `bash
   python manage.py load_test_data
   `

7. **Create a superuser**
   `bash
   python manage.py createsuperuser
   `

8. **Run the development server**
   `bash
   python manage.py runserver
   `

##  Usage

### Creating an Event
1. Sign up or log in to your account
2. Navigate to "Create Event"
3. Fill in event details (title, description, date, location, category, price)
4. Upload an event image
5. Submit to publish your event

### Booking a Ticket
1. Browse or search for events
2. Click on an event to view details
3. Select the number of tickets
4. Confirm your booking
5. View your ticket in "My Tickets"

### Managing Events
- **View Analytics**: Access your dashboard to see booking statistics
- **View Attendees**: Check the list of people who booked tickets
- **Track Bookmarks**: See how many users saved your event

##  Security Features

- Secure password hashing
- User authentication and authorization
- Session management
- Environment-based configuration

##  Developer

**Shubham Shirsekar**
- GitHub: [@ShubhamShirsekar](https://github.com/ShubhamShirsekar)

##  Support

For issues, questions, or suggestions, please open an issue on GitHub.
