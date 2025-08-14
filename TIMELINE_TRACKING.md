# Job Application Timeline Tracking

This document describes the timeline tracking functionality implemented for JobPilot-OpenManus.

## Overview

The timeline tracking system provides comprehensive event logging for job application activities, enabling users to track their job search progress over time. It captures key events like saving jobs, submitting applications, scheduling interviews, and status changes.

## Features

### Event Types

The system supports the following timeline event types:

- **Job Posted** (`job_posted`) - When a new job is posted
- **Job Saved** (`job_saved`) - When a user saves a job for later
- **Application Submitted** (`application_submitted`) - When an application is submitted
- **Interview Scheduled** (`interview_scheduled`) - When an interview is scheduled
- **Interview Completed** (`interview_completed`) - When an interview is completed
- **Follow-up Sent** (`follow_up_sent`) - When follow-up communications are sent
- **Response Received** (`response_received`) - When responses are received from employers
- **Status Changed** (`status_changed`) - When application status changes
- **Note Added** (`note_added`) - When notes are added to applications
- **Custom Event** (`custom_event`) - User-defined custom events

### Data Structure

Each timeline event contains:

- **Basic Info**: ID, user profile ID, event type, title, description
- **Associations**: Optional job ID and application ID references
- **Event Data**: Flexible JSON field for event-specific metadata
- **Timing**: Event date, milestone flag, created/updated timestamps

### Milestone Tracking

Important events can be marked as milestones for easy identification:
- Application submissions
- Interview scheduling
- Status changes to interviewing, offered, accepted, or rejected

## Implementation

### Backend Components

#### Models (`app/data/models.py`)

- `TimelineEventType` enum - Defines all supported event types
- `TimelineEvent` Pydantic model - Data transfer object
- `TimelineEventDB` SQLAlchemy model - Database representation

#### Service Layer (`app/services/timeline_service.py`)

The `TimelineService` class provides comprehensive timeline management:

**Core Methods:**
- `create_event()` - Create new timeline events
- `get_user_timeline()` - Retrieve user's timeline with filtering
- `get_job_timeline()` - Get events for a specific job
- `get_application_timeline()` - Get events for an application
- `update_event()` - Update existing events
- `delete_event()` - Remove events

**Convenience Methods:**
- `log_job_saved()` - Automatically log job save events
- `log_application_submitted()` - Log application submissions
- `log_interview_scheduled()` - Log interview scheduling
- `log_status_change()` - Log status changes
- `log_custom_event()` - Create custom user-defined events

**Query Methods:**
- `get_milestones()` - Retrieve milestone events
- `get_upcoming_events()` - Get future scheduled events

#### API Endpoints (`app/api/timeline.py`)

RESTful API endpoints for timeline access:

**Timeline Retrieval:**
- `GET /api/timeline/user/{user_profile_id}` - User timeline
- `GET /api/timeline/job/{job_id}` - Job-specific timeline
- `GET /api/timeline/application/{application_id}` - Application timeline
- `GET /api/timeline/user/{user_profile_id}/milestones` - User milestones
- `GET /api/timeline/user/{user_profile_id}/upcoming` - Upcoming events

**Event Management:**
- `POST /api/timeline/user/{user_profile_id}/event` - Create events
- `POST /api/timeline/user/{user_profile_id}/custom-event` - Create custom events
- `PUT /api/timeline/event/{event_id}` - Update events
- `DELETE /api/timeline/event/{event_id}` - Delete events

**Convenience Endpoints:**
- `POST /api/timeline/user/{user_profile_id}/job/{job_id}/saved` - Log job saves
- `POST /api/timeline/user/{user_profile_id}/application/{application_id}/submitted` - Log applications
- `POST /api/timeline/user/{user_profile_id}/application/{application_id}/interview-scheduled` - Log interviews
- `POST /api/timeline/user/{user_profile_id}/application/{application_id}/status-changed` - Log status changes

### Database Schema

The `timeline_events` table structure:

```sql
CREATE TABLE timeline_events (
    id VARCHAR PRIMARY KEY,
    job_id VARCHAR REFERENCES job_listings(id),
    application_id VARCHAR REFERENCES applications(id),
    user_profile_id VARCHAR REFERENCES user_profiles(id) NOT NULL,
    event_type VARCHAR NOT NULL,
    title VARCHAR NOT NULL,
    description TEXT,
    event_data JSON,
    event_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_milestone BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Integration

The timeline system integrates with existing job operations:

- **Job Saving**: Automatically creates `job_saved` events when users save jobs
- **Future Integrations**: Ready for application submissions, status changes, etc.

## Usage Examples

### Creating Timeline Events

```python
from app.services.timeline_service import TimelineService

# Initialize service
timeline_service = TimelineService(db_session)

# Log a job save
timeline_service.log_job_saved(
    user_profile_id="user-123",
    job_id="job-456",
    job_title="Senior Python Developer",
    company_name="TechCorp Inc.",
    notes="Great benefits package",
    tags=["python", "remote"]
)

# Log application submission
timeline_service.log_application_submitted(
    user_profile_id="user-123",
    job_id="job-456",
    application_id="app-789",
    job_title="Senior Python Developer",
    company_name="TechCorp Inc.",
    application_method="company website"
)

# Schedule interview
from datetime import datetime, timedelta
interview_date = datetime.utcnow() + timedelta(days=7)

timeline_service.log_interview_scheduled(
    user_profile_id="user-123",
    job_id="job-456",
    application_id="app-789",
    job_title="Senior Python Developer",
    company_name="TechCorp Inc.",
    interview_date=interview_date,
    interview_type="video call",
    interviewer="Jane Smith"
)
```

### Retrieving Timeline Data

```python
# Get user's recent activity
recent_events = timeline_service.get_user_timeline(
    user_profile_id="user-123",
    limit=20,
    days_back=30
)

# Get events for a specific job
job_events = timeline_service.get_job_timeline(
    job_id="job-456",
    user_profile_id="user-123"
)

# Get milestone events
milestones = timeline_service.get_milestones(
    user_profile_id="user-123",
    limit=10
)

# Get upcoming scheduled events
upcoming = timeline_service.get_upcoming_events(
    user_profile_id="user-123",
    days_ahead=14
)
```

### API Usage

```bash
# Get user timeline
curl "http://localhost:8080/api/timeline/user/user-123?limit=20"

# Create custom event
curl -X POST "http://localhost:8080/api/timeline/user/user-123/custom-event" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Company research completed",
    "description": "Researched company culture and recent news",
    "job_id": "job-456",
    "event_data": {"research_time": "2 hours"},
    "is_milestone": false
  }'

# Get upcoming events
curl "http://localhost:8080/api/timeline/user/user-123/upcoming?days_ahead=7"
```

## Setup and Installation

### 1. Database Migration

Run the migration script to create the timeline events table:

```bash
python create_timeline_tables.py
```

### 2. Test the Implementation

Run the test script to verify functionality:

```bash
# Run tests
python test_timeline.py

# Clean up test data
python test_timeline.py --clean
```

### 3. Start the Server

The timeline API endpoints are automatically included when running the web server:

```bash
python web_server.py --host 0.0.0.0 --port 8080
```

## Future Enhancements

Potential improvements and extensions:

1. **Frontend Integration**: Timeline visualization components for the web UI
2. **Analytics**: Timeline analytics and progress tracking
3. **Notifications**: Email/push notifications for upcoming events
4. **Export**: Export timeline data to PDF or other formats
5. **Templates**: Event templates for common activities
6. **Automation**: Automated event creation based on external integrations
7. **Reporting**: Timeline-based reporting and statistics

## Technical Notes

- **Performance**: Database queries are optimized with proper indexing on user_profile_id, job_id, and event_date
- **Scalability**: JSON event_data field allows flexible extension without schema changes
- **Error Handling**: Comprehensive error handling with logging for debugging
- **Type Safety**: Full type hints and Pydantic models for data validation
- **Testing**: Complete test suite covering all major functionality

The timeline tracking system provides a solid foundation for comprehensive job application tracking and can be easily extended to meet evolving user needs.
