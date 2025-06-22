"""
System Prompts API Routes
========================

API endpoints for managing system prompts in Admin Dashboard.
Only accessible to admin users.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from ....core.dependencies import get_supabase_client, require_admin
from ...core.auth import get_current_user
from supabase import Client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/system-prompts", tags=["system-prompts"])

# Pydantic models for request/response
from pydantic import BaseModel

class SystemPromptResponse(BaseModel):
    id: str
    prompt_text: str
    version: int
    is_active: bool
    created_at: str
    updated_at: str
    updated_by: Optional[str]
    notes: Optional[str]
    updated_by_email: Optional[str] = None

class SystemPromptUpdate(BaseModel):
    prompt_text: str
    notes: Optional[str] = None

class SystemPromptCreate(BaseModel):
    prompt_text: str
    notes: Optional[str] = None

@router.get("/current", response_model=SystemPromptResponse)
async def get_current_system_prompt(
    supabase: Client = Depends(get_supabase_client),
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """Get the currently active system prompt"""
    try:
        logger.info(f"🔍 Getting current system prompt for admin: {current_user.get('email')}")
        
        # Get active prompt
        response = supabase.table("system_prompts").select("*").eq("is_active", True).order("created_at", desc=True).limit(1).execute()
        
        if not response.data:
            logger.warning("⚠️ No active system prompt found")
            raise HTTPException(
                status_code=404,
                detail="No active system prompt found"
            )
        
        prompt_data = response.data[0]
        
        # Format response
        result = SystemPromptResponse(
            id=prompt_data["id"],
            prompt_text=prompt_data["prompt_text"],
            version=prompt_data["version"],
            is_active=prompt_data["is_active"],
            created_at=prompt_data["created_at"],
            updated_at=prompt_data["updated_at"],
            updated_by=prompt_data["updated_by"],
            notes=prompt_data["notes"],
            updated_by_email=None  # Email lookup removed for now
        )
        
        logger.info(f"✅ Retrieved current system prompt (ID: {result.id}, Version: {result.version})")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting current system prompt: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get current system prompt: {str(e)}"
        )

@router.get("/history", response_model=List[SystemPromptResponse])
async def get_system_prompt_history(
    limit: int = 10,
    supabase: Client = Depends(get_supabase_client),
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """Get history of system prompts"""
    try:
        logger.info(f"📜 Getting system prompt history for admin: {current_user.get('email')}")
        
        # Get prompt history
        response = supabase.table("system_prompts").select("*").order("created_at", desc=True).limit(limit).execute()
        
        results = []
        for prompt_data in response.data:
            result = SystemPromptResponse(
                id=prompt_data["id"],
                prompt_text=prompt_data["prompt_text"],
                version=prompt_data["version"],
                is_active=prompt_data["is_active"],
                created_at=prompt_data["created_at"],
                updated_at=prompt_data["updated_at"],
                updated_by=prompt_data["updated_by"],
                notes=prompt_data["notes"],
                updated_by_email=None  # Email lookup removed for now
            )
            results.append(result)
        
        logger.info(f"✅ Retrieved {len(results)} system prompt history entries")
        return results
        
    except Exception as e:
        logger.error(f"❌ Error getting system prompt history: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get system prompt history: {str(e)}"
        )

@router.post("/", response_model=SystemPromptResponse)
async def create_system_prompt(
    prompt_data: SystemPromptCreate,
    supabase: Client = Depends(get_supabase_client),
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """Create a new system prompt"""
    try:
        logger.info(f"➕ Creating new system prompt for admin: {current_user.get('email')}")
        
        # Validate prompt text
        if not prompt_data.prompt_text.strip():
            raise HTTPException(
                status_code=400,
                detail="System prompt text cannot be empty"
            )
        
        # Get next version number
        version_response = supabase.table("system_prompts").select("version").order("version", desc=True).limit(1).execute()
        next_version = 1 if not version_response.data else version_response.data[0]["version"] + 1
        
        # Create new prompt (will automatically deactivate others due to trigger)
        insert_data = {
            "prompt_text": prompt_data.prompt_text.strip(),
            "version": next_version,
            "is_active": True,  # New prompt becomes active
            "updated_by": current_user["id"],
            "notes": prompt_data.notes
        }
        
        response = supabase.table("system_prompts").insert(insert_data).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=500,
                detail="Failed to create system prompt"
            )
        
        created_prompt = response.data[0]
        
        result = SystemPromptResponse(
            id=created_prompt["id"],
            prompt_text=created_prompt["prompt_text"],
            version=created_prompt["version"],
            is_active=created_prompt["is_active"],
            created_at=created_prompt["created_at"],
            updated_at=created_prompt["updated_at"],
            updated_by=created_prompt["updated_by"],
            notes=created_prompt["notes"],
            updated_by_email=current_user.get("email")
        )
        
        logger.info(f"✅ Created new system prompt (ID: {result.id}, Version: {result.version})")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error creating system prompt: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create system prompt: {str(e)}"
        )

@router.put("/{prompt_id}", response_model=SystemPromptResponse)
async def update_system_prompt(
    prompt_id: str,
    prompt_data: SystemPromptUpdate,
    supabase: Client = Depends(get_supabase_client),
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """Update an existing system prompt"""
    try:
        logger.info(f"✏️ Updating system prompt {prompt_id} for admin: {current_user.get('email')}")
        
        # Validate prompt text
        if not prompt_data.prompt_text.strip():
            raise HTTPException(
                status_code=400,
                detail="System prompt text cannot be empty"
            )
        
        # Check if prompt exists
        existing_response = supabase.table("system_prompts").select("*").eq("id", prompt_id).execute()
        if not existing_response.data:
            raise HTTPException(
                status_code=404,
                detail="System prompt not found"
            )
        
        # Update the prompt
        update_data = {
            "prompt_text": prompt_data.prompt_text.strip(),
            "updated_by": current_user["id"],
            "notes": prompt_data.notes
        }
        
        response = supabase.table("system_prompts").update(update_data).eq("id", prompt_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=500,
                detail="Failed to update system prompt"
            )
        
        updated_prompt = response.data[0]
        
        result = SystemPromptResponse(
            id=updated_prompt["id"],
            prompt_text=updated_prompt["prompt_text"],
            version=updated_prompt["version"],
            is_active=updated_prompt["is_active"],
            created_at=updated_prompt["created_at"],
            updated_at=updated_prompt["updated_at"],
            updated_by=updated_prompt["updated_by"],
            notes=updated_prompt["notes"],
            updated_by_email=current_user.get("email")
        )
        
        logger.info(f"✅ Updated system prompt (ID: {result.id}, Version: {result.version})")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error updating system prompt: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update system prompt: {str(e)}"
        )

@router.post("/{prompt_id}/activate", response_model=SystemPromptResponse)
async def activate_system_prompt(
    prompt_id: str,
    supabase: Client = Depends(get_supabase_client),
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """Activate a specific system prompt (making it the current one)"""
    try:
        logger.info(f"🔄 Activating system prompt {prompt_id} for admin: {current_user.get('email')}")
        
        # Check if prompt exists
        existing_response = supabase.table("system_prompts").select("*").eq("id", prompt_id).execute()
        if not existing_response.data:
            raise HTTPException(
                status_code=404,
                detail="System prompt not found"
            )
        
        # Activate the prompt (trigger will deactivate others)
        update_data = {
            "is_active": True,
            "updated_by": current_user["id"]
        }
        
        response = supabase.table("system_prompts").update(update_data).eq("id", prompt_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=500,
                detail="Failed to activate system prompt"
            )
        
        activated_prompt = response.data[0]
        
        result = SystemPromptResponse(
            id=activated_prompt["id"],
            prompt_text=activated_prompt["prompt_text"],
            version=activated_prompt["version"],
            is_active=activated_prompt["is_active"],
            created_at=activated_prompt["created_at"],
            updated_at=activated_prompt["updated_at"],
            updated_by=activated_prompt["updated_by"],
            notes=activated_prompt["notes"],
            updated_by_email=current_user.get("email")
        )
        
        logger.info(f"✅ Activated system prompt (ID: {result.id}, Version: {result.version})")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error activating system prompt: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to activate system prompt: {str(e)}"
        )

@router.post("/reset-to-default", response_model=SystemPromptResponse)
async def reset_to_default_system_prompt(
    supabase: Client = Depends(get_supabase_client),
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """Reset to the original default system prompt"""
    try:
        logger.info(f"🔄 Resetting to default system prompt for admin: {current_user.get('email')}")
        
        # Import the original default prompt from system_prompts.py
        try:
            from src.ai.config.system_prompts import system_prompts
            original_default_text = system_prompts.MAIN_SYSTEM_PROMPT
        except ImportError:
            # Fallback to hardcoded default if import fails
            original_default_text = """# SYSTEM PROMPT - Academic Assistant for Afeka College

## Role and Purpose
You are an expert academic assistant for Afeka College of Engineering in Tel Aviv. Your role is to help students, applicants, and staff with questions about regulations, academic procedures, student rights, and institutional information.

**IMPORTANT: Always respond in Hebrew unless explicitly asked to respond in another language.**

## Information Sources
Base your responses ONLY on the official documents provided through the RAG system. Always include accurate citations with document name and section number.

## Response Methodology
1. Identify the topic and relevant documents
2. Search for specific information and identify conditions or limitations
3. **Present comprehensive, structured response immediately** - avoid brief answers
4. Include all relevant details, exceptions, and context in the first response
5. Use clear formatting with bullet points, numbered lists, and bold headings

## Critical Guidelines

### Required:
- Absolute accuracy - only information explicitly stated in documents
- Precise source citations for all claims
- **Comprehensive first responses** - provide all relevant details immediately
- **Clear structure** with bullet points, numbered lists, and headings
- Emphasis on deadlines, conditions, and requirements
- Professional yet supportive tone

### Prohibited:
- Inventing information not in documents
- Making unsupported generalizations
- Ignoring conditions or limitations
- Providing interpretation without basis

## Handling Missing Information
When requested information is not available in documents, respond in Hebrew:
"מצטער, המידע הספציפי שביקשת לא זמין במסמכים הרשמיים שברשותי. אני ממליץ לפנות ל[גורם רלוונטי] או לבדוק באתר המכללה הרשמי."

## Response Structure
**Always provide comprehensive, well-structured responses from the first answer. Never give brief answers that require follow-up questions.**

Format every response as follows (in Hebrew):
1. **Direct answer** to the main question
2. **Detailed breakdown** with bullet points or numbered lists when applicable
3. **Important conditions/exceptions** clearly highlighted
4. **Relevant deadlines or timeframes** if applicable
5. **Additional helpful information** or next steps
6. **Accurate citations** with document name and section

**Language requirement: All responses must be in clear, professional Hebrew with organized formatting.**

## Citation Examples
**Correct:** "על פי [שם המסמך], סעיף X.Y..." | "According to [Document Name], Section X.Y..."
**Incorrect:** "לפי מדיניות המכללה..." | "According to college policy..." (without specific citation)

## Core Principles
- **Comprehensive responses**: Always provide complete, detailed answers from the start
- **Structured formatting**: Use bullet points, numbers, and clear organization
- Accuracy above all - prefer "I don't know" over incorrect information
- Maximum helpfulness within available information constraints
- Empathy - understand that real needs lie behind every question
- Professionalism - you represent the digital face of Afeka College

Remember: Every response reflects the excellence and values of Afeka College. Always communicate in clear, professional Hebrew to serve our Hebrew-speaking community effectively."""
        
        # Get next version number
        version_response = supabase.table("system_prompts").select("version").order("version", desc=True).limit(1).execute()
        next_version = 1 if not version_response.data else version_response.data[0]["version"] + 1
        
        # Create new prompt with original default text
        insert_data = {
            "prompt_text": original_default_text,
            "version": next_version,
            "is_active": True,  # New prompt becomes active
            "updated_by": current_user["id"],
            "notes": "Reset to original default system prompt from system_prompts.py"
        }
        
        response = supabase.table("system_prompts").insert(insert_data).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=500,
                detail="Failed to reset to default system prompt"
            )
        
        created_prompt = response.data[0]
        
        result = SystemPromptResponse(
            id=created_prompt["id"],
            prompt_text=created_prompt["prompt_text"],
            version=created_prompt["version"],
            is_active=created_prompt["is_active"],
            created_at=created_prompt["created_at"],
            updated_at=created_prompt["updated_at"],
            updated_by=created_prompt["updated_by"],
            notes=created_prompt["notes"],
            updated_by_email=current_user.get("email")
        )
        
        logger.info(f"✅ Reset to default system prompt (ID: {result.id}, Version: {result.version})")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error resetting to default system prompt: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reset to default system prompt: {str(e)}"
        ) 