"""AI Support Router with Gemini Integration"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import google.generativeai as genai
import os

from app.database import get_db
from app.config import get_settings
from app.schemas.ai_support import ChatRequest, ChatResponse
from app.routers.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/ai-support", tags=["AI Support"])
settings = get_settings()

# System Instruction for the AI Support Bot
SYSTEM_INSTRUCTION = """
You are "RV-Assistant", the official AI companion for the RVSync platform.
RVSync is an advanced Learning Management and Career Development system for engineering students.

Your tone should be:
1. Professional yet friendly and encouraging.
2. Direct and concise (avoid long paragraphs).
3. Highly knowledgeable about the platform features.

Key Platform Info for you:
- Dashboard: Shows academic performance, upcoming events, and quick stats.
- Classroom Hub: Automatically loads the user's specific section (like CSE-2E). It contains the Timetable and Daily Agenda.
- Courses: A vertical list of all academic subjects. Clicking a course leads to a "Premium Detail Page".
- Premium Course Page: Includes Syllabus (unit-wise), Materials, Assignments, Tests, and the "Math Practice Hub".
- Math Practice Hub: Specifically for Linear Algebra (MAT231TC), contains interactive Flashcards and Practice Tests.
- Career Intelligence: Syncs GitHub/LinkedIn to match students with internships and provide career predictions.
- Chat: Allows real-time messaging with classmates and faculty.

If a user asks how to find something, guide them to these specific tabs.
If they ask about Linear Algebra specifically, mention the "Math Practice Hub" in the MAT231TC course page.
Your main goal is to reduce technical friction and help students study more effectively.
"""

# Configure Gemini
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=SYSTEM_INSTRUCTION
    )
else:
    model = None

from datetime import datetime, timedelta
from app.models.event import Event
from app.models.assignment import Assignment
from app.models.course import Course
from app.models.assignment import Test

@router.post("/chat", response_model=ChatResponse)
async def ai_chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Chat with RVSync AI Assistant"""
    # Reload settings to get the key if it was just added
    current_settings = get_settings()
    
    # Re-initialize genai with key if not configured
    if current_settings.GEMINI_API_KEY:
        genai.configure(api_key=current_settings.GEMINI_API_KEY)
        
        # We'll try a few model names that are common
        model_names = ["gemini-1.5-flash", "gemini-1.5-flash-latest", "models/gemini-1.5-flash", "gemini-1.5-pro"]
        chat_model = None
        last_error = ""
        
        for m_name in model_names:
            try:
                # Try creating the model without system_instruction first to avoid v1beta issues
                test_model = genai.GenerativeModel(model_name=m_name)
                # Quick test (optional but safer for naming)
                chat_model = test_model
                break
            except Exception as e:
                last_error = str(e)
                continue
                
        if not chat_model:
            return ChatResponse(
                response=f"I couldn't find a supported Gemini model. Last error: {last_error}",
                is_success=False
            )
    else:
        return ChatResponse(
            response="AI Support is currently in 'Mock Mode' as the Gemini API Key is missing. Please add GEMINI_API_KEY to your .env file to enable the College Specialist bot!",
            is_success=False
        )

    try:
        # 1. Fetch User Context from DB
        # Upcoming Events (next 7 days)
        now = datetime.utcnow()
        week_later = now + timedelta(days=7)
        
        events = db.query(Event).filter(
            Event.start_time >= now,
            Event.start_time <= week_later
        ).all()
        
        # Enrolled Course IDs
        course_ids = [course.id for enrollment in current_user.enrollments for course in enrollment.classroom.courses]
        
        # Upcoming Assignments (next 7 days)
        assignments = db.query(Assignment).filter(
            Assignment.course_id.in_(course_ids),
            Assignment.due_date >= now,
            Assignment.due_date <= week_later
        ).all()

        # Upcoming Tests
        tests = db.query(Test).filter(
            Test.course_id.in_(course_ids),
            Test.is_published == True
        ).all()

        # 2. Format Context for Prompt
        context_str = f"USER CONTEXT:\n- Name: {current_user.name}\n- Branch: {current_user.branch}\n- Year: {current_user.year_level}\n\n"
        
        if events:
            context_str += "UPCOMING EVENTS:\n"
            for e in events:
                context_str += f"- {e.title} at {e.start_time.strftime('%Y-%m-%d %H:%M')}\n"
        
        if assignments:
            context_str += "\nUPCOMING ASSIGNMENTS:\n"
            for a in assignments:
                context_str += f"- {a.title} due on {a.due_date.strftime('%Y-%m-%d %H:%M')}\n"
                
        if tests:
            context_str += "\nAVAILABLE TESTS/ASSESSMENTS:\n"
            for t in tests:
                context_str += f"- {t.title} ({t.total_points} pts)\n"

        full_message = f"{SYSTEM_INSTRUCTION}\n\n{context_str}\nUSER MESSAGE: {request.message}"
        
        response = chat_model.generate_content(full_message)
        
        return ChatResponse(
            response=response.text,
            is_success=True
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return ChatResponse(
            response=f"I'm having a bit of trouble connecting to my central brain. Error: {str(e)}",
            is_success=False
        )
