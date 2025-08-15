#!/usr/bin/env python3
"""
Test script for timeline functionality.
This script tests the timeline event creation and retrieval.
"""

import os
import sys
from datetime import datetime, timedelta


# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.data.models import create_database_engine, get_session_factory
from app.logger import logger
from app.services.timeline_service import TimelineService


def test_timeline_functionality():
    """Test the timeline service functionality."""

    try:
        # Create database connection
        database_url = "sqlite:///jobpilot.db"
        engine = create_database_engine(database_url)
        Session = get_session_factory(engine)
        db_session = Session()

        logger.info("Connected to database and created session")

        # Initialize timeline service
        timeline_service = TimelineService(db_session)
        logger.info("Initialized timeline service")

        # Test user profile ID (using demo user)
        test_user_id = "00000000-0000-4000-8000-000000000001"

        # Create some test timeline events
        logger.info("Creating test timeline events...")

        # Test 1: Job saved event
        event1 = timeline_service.log_job_saved(
            user_profile_id=test_user_id,
            job_id="test-job-1",
            job_title="Senior Python Developer",
            company_name="Test Company Inc.",
            notes="Looks like a great opportunity!",
            tags=["python", "remote", "senior"],
        )
        logger.info(f"Created job saved event: {event1.id}")

        # Test 2: Application submitted event
        event2 = timeline_service.log_application_submitted(
            user_profile_id=test_user_id,
            job_id="test-job-1",
            application_id="test-app-1",
            job_title="Senior Python Developer",
            company_name="Test Company Inc.",
            application_method="company website",
        )
        logger.info(f"Created application submitted event: {event2.id}")

        # Test 3: Interview scheduled event
        interview_date = datetime.utcnow() + timedelta(days=7)
        event3 = timeline_service.log_interview_scheduled(
            user_profile_id=test_user_id,
            job_id="test-job-1",
            application_id="test-app-1",
            job_title="Senior Python Developer",
            company_name="Test Company Inc.",
            interview_date=interview_date,
            interview_type="video call",
            interviewer="Jane Smith",
        )
        logger.info(f"Created interview scheduled event: {event3.id}")

        # Test 4: Status change event
        event4 = timeline_service.log_status_change(
            user_profile_id=test_user_id,
            job_id="test-job-1",
            application_id="test-app-1",
            job_title="Senior Python Developer",
            company_name="Test Company Inc.",
            old_status="applied",
            new_status="interviewing",
            notes="Moved to interview stage!",
        )
        logger.info(f"Created status change event: {event4.id}")

        # Test 5: Custom event
        event5 = timeline_service.log_custom_event(
            user_profile_id=test_user_id,
            title="Researched company culture",
            description="Read about company values and recent news",
            job_id="test-job-1",
            event_data={
                "research_time": "2 hours",
                "sources": ["company website", "glassdoor"],
            },
            is_milestone=False,
        )
        logger.info(f"Created custom event: {event5.id}")

        # Test retrieval: Get user timeline
        logger.info("\nTesting timeline retrieval...")
        user_timeline = timeline_service.get_user_timeline(
            user_profile_id=test_user_id, limit=10
        )
        logger.info(f"Retrieved {len(user_timeline)} events from user timeline:")
        for event in user_timeline:
            logger.info(
                f"  - {event.event_date.strftime('%Y-%m-%d %H:%M')} | {event.event_type.value} | {event.title}"
            )

        # Test retrieval: Get job timeline
        job_timeline = timeline_service.get_job_timeline(
            job_id="test-job-1", user_profile_id=test_user_id
        )
        logger.info(f"\nRetrieved {len(job_timeline)} events from job timeline:")
        for event in job_timeline:
            logger.info(
                f"  - {event.event_date.strftime('%Y-%m-%d %H:%M')} | {event.event_type.value} | {event.title}"
            )

        # Test retrieval: Get milestones
        milestones = timeline_service.get_milestones(
            user_profile_id=test_user_id, limit=5, days_back=30
        )
        logger.info(f"\nRetrieved {len(milestones)} milestone events:")
        for event in milestones:
            milestone_marker = "🏆" if event.is_milestone else "📌"
            logger.info(
                f"  - {milestone_marker} {event.event_date.strftime('%Y-%m-%d %H:%M')} | {event.title}"
            )

        # Test retrieval: Get upcoming events
        upcoming = timeline_service.get_upcoming_events(
            user_profile_id=test_user_id, days_ahead=10, limit=5
        )
        logger.info(f"\nRetrieved {len(upcoming)} upcoming events:")
        for event in upcoming:
            logger.info(
                f"  - 📅 {event.event_date.strftime('%Y-%m-%d %H:%M')} | {event.title}"
            )

        # Test event update
        logger.info("\nTesting event update...")
        updated_event = timeline_service.update_event(
            event_id=str(event5.id),
            title="Updated: Researched company culture and competitors",
            description="Read about company values, recent news, and analyzed competitors",
            event_data={
                "research_time": "3 hours",
                "sources": [
                    "company website",
                    "glassdoor",
                    "linkedin",
                    "news articles",
                ],
            },
            is_milestone=True,
        )
        if updated_event:
            logger.info(f"Successfully updated event: {updated_event.title}")

        # Close database session
        db_session.close()
        logger.info("\n✅ All timeline tests completed successfully!")

        return True

    except Exception as e:
        logger.error(f"❌ Timeline test failed: {e}")
        if "db_session" in locals():
            db_session.rollback()
            db_session.close()
        return False


def clean_test_data():
    """Clean up test data from the database."""

    try:
        database_url = "sqlite:///jobpilot.db"
        engine = create_database_engine(database_url)
        Session = get_session_factory(engine)
        db_session = Session()

        timeline_service = TimelineService(db_session)
        test_user_id = "00000000-0000-4000-8000-000000000001"

        # Get all events for the test user
        all_events = timeline_service.get_user_timeline(
            user_profile_id=test_user_id, limit=100
        )

        # Delete test events (those with test job IDs)
        deleted_count = 0
        for event in all_events:
            if event.job_id and str(event.job_id).startswith("test-"):
                timeline_service.delete_event(str(event.id))
                deleted_count += 1
            elif "test" in event.title.lower() or "research" in event.title.lower():
                timeline_service.delete_event(str(event.id))
                deleted_count += 1

        db_session.close()
        logger.info(f"🧹 Cleaned up {deleted_count} test events")

        return True

    except Exception as e:
        logger.error(f"❌ Error cleaning test data: {e}")
        return False


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test timeline functionality")
    parser.add_argument("--clean", action="store_true", help="Clean up test data")
    args = parser.parse_args()

    if args.clean:
        logger.info("🧹 Cleaning up test data...")
        success = clean_test_data()
        if success:
            logger.info("✅ Test data cleanup completed!")
        else:
            logger.error("❌ Test data cleanup failed!")
            sys.exit(1)
    else:
        logger.info("🚀 Starting timeline functionality tests...")
        success = test_timeline_functionality()

        if success:
            logger.info("\n✅ Timeline tests passed!")
            print("\nTo clean up test data, run: python test_timeline.py --clean")
        else:
            logger.error("\n❌ Timeline tests failed!")
            sys.exit(1)
