# JobPilot Timeline API - Usage Guide

The Timeline API is now fully integrated and ready to use! This guide shows you how to interact with the timeline functionality.

## 🚀 Quick Start

The timeline API is automatically included when you start the JobPilot web server:

```bash
python web_server.py
```

The API will be available at: `http://localhost:8000/api/timeline`

## 📋 Available Endpoints

### User Timeline
- **GET** `/api/timeline/user/{user_profile_id}` - Get timeline events for a user
- **GET** `/api/timeline/user/{user_profile_id}/milestones` - Get milestone events 
- **GET** `/api/timeline/user/{user_profile_id}/upcoming` - Get upcoming events

### Job & Application Timeline
- **GET** `/api/timeline/job/{job_id}` - Get timeline for a specific job
- **GET** `/api/timeline/application/{application_id}` - Get timeline for a specific application

### Event Management
- **POST** `/api/timeline/user/{user_profile_id}/event` - Create a timeline event
- **POST** `/api/timeline/user/{user_profile_id}/custom-event` - Create a custom event
- **PUT** `/api/timeline/event/{event_id}` - Update an event
- **DELETE** `/api/timeline/event/{event_id}` - Delete an event

### Convenience Endpoints
- **POST** `/api/timeline/user/{user_profile_id}/job/{job_id}/saved` - Log job saved
- **POST** `/api/timeline/user/{user_profile_id}/application/{application_id}/submitted` - Log application submitted
- **POST** `/api/timeline/user/{user_profile_id}/application/{application_id}/interview-scheduled` - Log interview scheduled
- **POST** `/api/timeline/user/{user_profile_id}/application/{application_id}/status-changed` - Log status change

### Utility
- **GET** `/api/timeline/event-types` - Get all available event types

## 📝 Example Usage

### 1. Get User Timeline

```bash
curl "http://localhost:8000/api/timeline/user/user123?limit=10&days_back=30"
```

### 2. Log a Job Saved Event

```bash
curl -X POST "http://localhost:8000/api/timeline/user/user123/job/job456/saved" \
  -G -d "job_title=Software Engineer" \
  -d "company_name=TechCorp" \
  -d "notes=Interesting React position"
```

### 3. Create a Custom Event

```bash
curl -X POST "http://localhost:8000/api/timeline/user/user123/custom-event" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated resume",
    "description": "Added new React project",
    "is_milestone": true
  }'
```

### 4. Log Application Submitted

```bash
curl -X POST "http://localhost:8000/api/timeline/user/user123/application/app789/submitted" \
  -G -d "job_id=job456" \
  -d "job_title=Software Engineer" \
  -d "company_name=TechCorp" \
  -d "application_method=Company Website"
```

## 🔧 Integration in Code

### Using the Timeline Service Directly

```python
from app.services.timeline_service import TimelineService
from app.data.database import get_database_manager
from app.data.models import TimelineEventType

# Get a database session
db_manager = get_database_manager()
with db_manager.get_session() as session:
    # Create timeline service
    timeline_service = TimelineService(session)
    
    # Log a job saved event
    event = timeline_service.log_job_saved(
        user_profile_id="user123",
        job_id="job456", 
        job_title="Software Engineer",
        company_name="TechCorp",
        notes="Great opportunity!"
    )
    
    # Get user timeline
    events = timeline_service.get_user_timeline(
        user_profile_id="user123",
        limit=20,
        days_back=30
    )
```

### Using in FastAPI Endpoints

```python
from fastapi import Depends
from app.api.timeline import get_database_session
from app.services.timeline_service import TimelineService

@app.post("/my-endpoint")
def my_endpoint(db: Session = Depends(get_database_session)):
    timeline_service = TimelineService(db)
    
    # Use timeline service...
    event = timeline_service.create_event(...)
    return {"event_id": event.id}
```

## 🛠️ Timeline Event Types

The following event types are available:

- `JOB_SAVED` - When a user saves a job
- `APPLICATION_SUBMITTED` - When an application is submitted
- `INTERVIEW_SCHEDULED` - When an interview is scheduled
- `INTERVIEW_COMPLETED` - After completing an interview
- `STATUS_CHANGED` - When application status changes
- `OFFER_RECEIVED` - When a job offer is received
- `OFFER_ACCEPTED` - When an offer is accepted
- `OFFER_DECLINED` - When an offer is declined
- `CUSTOM_EVENT` - User-defined custom events

## ✅ Database Integration

The timeline API uses the repository pattern with:
- **DatabaseManager**: Handles database connections and sessions
- **TimelineService**: Business logic for timeline operations  
- **get_database_session()**: FastAPI dependency for session injection

All database operations are automatically handled with proper session management, transactions, and error handling.

## 🧪 Testing

Run the integration tests to verify everything is working:

```bash
python test_integration.py
```

This will test:
- ✅ All imports work correctly
- ✅ Database connections function
- ✅ API endpoints are registered
- ✅ Session management works
- ✅ Services can be instantiated

## 📈 Next Steps

The timeline API is now ready for:

1. **Frontend Integration** - Connect your Solid.js frontend to these endpoints
2. **User Authentication** - Add authentication middleware to protect user data
3. **Real-time Updates** - Use WebSockets to push timeline updates to clients
4. **Analytics** - Build reports and insights from timeline data
5. **Notifications** - Send alerts based on timeline events

The foundation is solid and extensible for building a comprehensive job application tracking system! 🎉
