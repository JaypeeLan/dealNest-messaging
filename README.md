# 📩 DealNest Messaging - Unread Message Notification Service

A **Django-based messaging system** with intelligent background notifications using **Celery** and **Redis**.  
Messages are automatically flagged for email notifications after a configurable delay, with **smart cancellation** when users read their messages.

---

## 🎯 Overview

This system implements the core messaging workflow used at DealNest:

1. **User sends message** → System creates message and schedules notification
2. **Timer runs** → After configured delay (default 1–2 minutes per user)
3. **Smart notification** → Email sent only if message still unread
4. **Instant cancellation** → Reading message cancels pending notifications

---

## 🏗️ Architecture

### Core Components

- **Django REST API** → Message creation & management endpoints
- **Celery + Redis** → Distributed task queue for delayed notifications
- **PostgreSQL/SQLite** → Message & user data storage
- **Email Backend** → Configurable email delivery system

### Key Features

✅ Per-user notification delays (configurable from 1 minute to hours)  
✅ Smart task cancellation (no notifications for read messages)  
✅ Unread message aggregation (counts all unread messages in notification)  
✅ RESTful API with validation  
✅ Background processing (non-blocking operations)  
✅ Comprehensive test suite (models, APIs, tasks)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Redis Server
- Git

### Installation

```bash
# 1. Clone and setup
git clone <repository-url>
cd dealnest_messaging

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup database
python manage.py makemigrations
python manage.py migrate
```

### Create Test Users

```python
from messaging.models import User

alice = User.objects.create_user(
    username='alice',
    email='alice@example.com',
    password='testpass123',
    notification_delay_minutes=1
)

bob = User.objects.create_user(
    username='bob',
    email='bob@example.com',
    password='testpass123',
    notification_delay_minutes=2
)

print(f"Alice ID: {alice.id}, Bob ID: {bob.id}")
```

### Start Services

**Terminal 1 - Redis**

```bash
redis-server
```

**Terminal 2 - Django**

```bash
source venv/bin/activate
python manage.py runserver
```

**Terminal 3 - Celery Worker**

```bash
source venv/bin/activate
celery -A config worker --loglevel=info
```

---

## 📡 API Reference

**Base URL:** `http://localhost:8000/api/`

### 1. Create Message

**POST** `/api/messages/`  
Schedules notification after recipient’s delay.

**Request**

```json
{
  "sender_id": 1,
  "recipient_id": 2,
  "body": "Hello! This is a test message."
}
```

**Response (201 Created)**

```json
{
  "message": {
    "id": 1,
    "sender": 1,
    "recipient": 2,
    "body": "Hello! This is a test message.",
    "is_read": false,
    "created_at": "2024-09-25T14:30:00.123456Z",
    "sender_username": "alice",
    "recipient_username": "bob"
  },
  "notification_scheduled_for": "2024-09-25T14:32:00.123456Z",
  "task_id": "abc123-def456-789ghi"
}
```

---

### 2. Mark Message as Read

**POST** `/api/messages/mark-read/`  
Cancels pending notification.

**Request**

```json
{
  "message_id": 1
}
```

**Response**

```json
{
  "message": {
    "id": 1,
    "sender": 1,
    "recipient": 2,
    "body": "Hello! This is a test message.",
    "is_read": true,
    "created_at": "2024-09-25T14:30:00.123456Z",
    "sender_username": "alice",
    "recipient_username": "bob"
  },
  "notification_cancelled": true
}
```

---

### 3. List Messages (Debug)

**GET** `/api/messages/list/`

**Response**

```json
[
  {
    "id": 1,
    "sender": 1,
    "recipient": 2,
    "body": "Hello! This is a test message.",
    "is_read": true,
    "created_at": "2024-09-25T14:30:00.123456Z",
    "sender_username": "alice",
    "recipient_username": "bob"
  }
]
```

---

## 🧪 Testing with Postman

### Base Setup

- **Base URL** → `http://localhost:8000/api`
- **Env Variables**

```json
{
  "baseUrl": "http://localhost:8000/api",
  "aliceId": 1,
  "bobId": 2
}
```

### Test Scenarios

1. **Unread Notification** → Create message, wait delay, unread triggers email.
2. **Read Message (No Notification)** → Mark read immediately, no email sent.
3. **Multiple Messages** → Create multiple, email aggregates unread count.

---

## 🔧 Configuration

### User Notification Delays

```python
user = User.objects.get(username='bob')
user.notification_delay_minutes = 5
user.save()
```

### Email Backend

**Development (console)**:

```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

**Production (SMTP)**:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

### Redis Settings (`settings.py`)

```python
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
```

---

## 📊 Data Models

### User

```python
class User(AbstractUser):
    notification_delay_minutes = IntegerField(default=1)
```

### Message

```python
class Message(models.Model):
    sender = ForeignKey(User, related_name='sent_messages')
    recipient = ForeignKey(User, related_name='received_messages')
    body = TextField()
    is_read = BooleanField(default=False)
    created_at = DateTimeField(auto_now_add=True)
    notification_task_id = CharField(max_length=255, blank=True)
```

---

## 🎛️ Admin Interface

- Visit: `http://localhost:8000/admin/`
- Manage users, messages, and preferences.
- Monitor tasks and debug status.

---

## 🧪 Running Tests

```bash
python manage.py test
python manage.py test messaging.tests.MessageAPITest
python manage.py test messaging.tests.NotificationTaskTest
```

With coverage:

```bash
pip install coverage
coverage run manage.py test
coverage report
```

---

## 🐛 Troubleshooting

### Common Issues

1. **Redis Connection Error**

```bash
redis-cli ping  # Expect: PONG
```

2. **Celery Tasks Not Executing**

```bash
celery -A config inspect active
celery -A config purge
```

3. **Migration Issues**

```bash
rm messaging/migrations/000*.py
python manage.py makemigrations messaging
python manage.py migrate
```

4. **Email Not Showing**

- Check console output
- Verify recipient email
- Ensure delay passed
- Check Celery logs

---

## ⚒️ Debug Commands

```bash
python manage.py check
celery -A config inspect active
```

---

## 🏗️ Built With

- Django
- Celery
- Redis

---
