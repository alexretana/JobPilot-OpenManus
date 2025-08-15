"""
Simple Leads API for JobPilot
Basic CRUD operations for managing job search contacts and leads
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

router = APIRouter(prefix="/api/leads", tags=["leads"])

# Default user ID (same as in web_server.py)
DEFAULT_USER_ID = "00000000-0000-4000-8000-000000000001"

# =====================================
# Enums and Models
# =====================================


class LeadStatus(str, Enum):
    """Lead status enum."""

    NEW = "new"
    CONTACTED = "contacted"
    RESPONDED = "responded"
    MEETING_SCHEDULED = "meeting_scheduled"
    FOLLOW_UP_NEEDED = "follow_up_needed"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


class LeadType(str, Enum):
    """Lead type enum."""

    RECRUITER = "recruiter"
    HIRING_MANAGER = "hiring_manager"
    EMPLOYEE = "employee"
    REFERRAL = "referral"
    NETWORKING = "networking"
    OTHER = "other"


class Lead(BaseModel):
    """Lead data model."""

    id: str
    user_profile_id: str
    name: str
    title: Optional[str] = None
    company: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    lead_type: LeadType
    status: LeadStatus
    source: Optional[str] = None  # Where did you meet/find them?
    notes: Optional[str] = None
    last_contacted: Optional[datetime] = None
    follow_up_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class CreateLeadRequest(BaseModel):
    """Request model for creating a new lead."""

    name: str
    title: Optional[str] = None
    company: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    lead_type: LeadType = LeadType.OTHER
    status: LeadStatus = LeadStatus.NEW
    source: Optional[str] = None
    notes: Optional[str] = None
    follow_up_date: Optional[datetime] = None


class UpdateLeadRequest(BaseModel):
    """Request model for updating a lead."""

    name: Optional[str] = None
    title: Optional[str] = None
    company: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    lead_type: Optional[LeadType] = None
    status: Optional[LeadStatus] = None
    source: Optional[str] = None
    notes: Optional[str] = None
    last_contacted: Optional[datetime] = None
    follow_up_date: Optional[datetime] = None


# =====================================
# In-Memory Storage (Demo only)
# =====================================

# In a real application, this would be stored in a database
leads_storage: List[Lead] = []

# =====================================
# API Endpoints
# =====================================


@router.post("/")
def create_lead(request: CreateLeadRequest):
    """Create a new lead."""
    try:
        lead = Lead(
            id=str(uuid4()),
            user_profile_id=DEFAULT_USER_ID,
            name=request.name,
            title=request.title,
            company=request.company,
            email=request.email,
            phone=request.phone,
            linkedin_url=request.linkedin_url,
            lead_type=request.lead_type,
            status=request.status,
            source=request.source,
            notes=request.notes,
            last_contacted=None,
            follow_up_date=request.follow_up_date,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        leads_storage.append(lead)

        return lead

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
def get_leads(
    user_profile_id: str = Query(DEFAULT_USER_ID, description="User profile ID"),
    status: Optional[LeadStatus] = Query(None, description="Filter by status"),
    lead_type: Optional[LeadType] = Query(None, description="Filter by lead type"),
    limit: int = Query(20, ge=1, le=100, description="Limit"),
):
    """Get user's leads."""
    try:
        # Filter leads by user
        user_leads = [
            lead for lead in leads_storage if lead.user_profile_id == user_profile_id
        ]

        # Apply filters
        if status:
            user_leads = [lead for lead in user_leads if lead.status == status]
        if lead_type:
            user_leads = [lead for lead in user_leads if lead.lead_type == lead_type]

        # Apply limit
        user_leads = user_leads[:limit]

        return {"leads": user_leads, "total": len(user_leads)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{lead_id}")
def get_lead(lead_id: str):
    """Get a specific lead."""
    try:
        lead = next((lead for lead in leads_storage if lead.id == lead_id), None)
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")

        return lead

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{lead_id}")
def update_lead(lead_id: str, request: UpdateLeadRequest):
    """Update a lead."""
    try:
        lead = next((lead for lead in leads_storage if lead.id == lead_id), None)
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")

        # Update fields if provided
        if request.name is not None:
            lead.name = request.name
        if request.title is not None:
            lead.title = request.title
        if request.company is not None:
            lead.company = request.company
        if request.email is not None:
            lead.email = request.email
        if request.phone is not None:
            lead.phone = request.phone
        if request.linkedin_url is not None:
            lead.linkedin_url = request.linkedin_url
        if request.lead_type is not None:
            lead.lead_type = request.lead_type
        if request.status is not None:
            lead.status = request.status
            if request.status in [LeadStatus.CONTACTED, LeadStatus.RESPONDED]:
                lead.last_contacted = datetime.utcnow()
        if request.source is not None:
            lead.source = request.source
        if request.notes is not None:
            lead.notes = request.notes
        if request.last_contacted is not None:
            lead.last_contacted = request.last_contacted
        if request.follow_up_date is not None:
            lead.follow_up_date = request.follow_up_date

        lead.updated_at = datetime.utcnow()

        return lead

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{lead_id}")
def delete_lead(lead_id: str):
    """Delete a lead."""
    try:
        global leads_storage

        lead = next((lead for lead in leads_storage if lead.id == lead_id), None)
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")

        leads_storage = [lead for lead in leads_storage if lead.id != lead_id]

        return {"message": "Lead deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/summary")
def get_lead_stats(
    user_profile_id: str = Query(DEFAULT_USER_ID, description="User profile ID")
):
    """Get lead statistics summary."""
    try:
        user_leads = [
            lead for lead in leads_storage if lead.user_profile_id == user_profile_id
        ]

        # Status breakdown
        status_counts = {}
        for status in LeadStatus:
            status_counts[status.value] = len(
                [lead for lead in user_leads if lead.status == status]
            )

        # Type breakdown
        type_counts = {}
        for lead_type in LeadType:
            type_counts[lead_type.value] = len(
                [lead for lead in user_leads if lead.lead_type == lead_type]
            )

        # Follow-ups needed
        now = datetime.utcnow()
        follow_ups_due = len(
            [
                lead
                for lead in user_leads
                if lead.follow_up_date and lead.follow_up_date <= now
            ]
        )

        return {
            "total_leads": len(user_leads),
            "status_breakdown": status_counts,
            "type_breakdown": type_counts,
            "follow_ups_due": follow_ups_due,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
