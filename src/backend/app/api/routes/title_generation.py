import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
import os
from typing import Optional

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Title Generation"])

# הגדרת המודל
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

class TitleGenerationRequest(BaseModel):
    prompt: str

class TitleGenerationResponse(BaseModel):
    title: str
    success: bool
    error: Optional[str] = None

@router.post("/api/generate-title", response_model=TitleGenerationResponse)
async def generate_title(request: TitleGenerationRequest):
    """
    יצירת כותרת אוטומטית לשיחה בהתבסס על התוכן
    """
    try:
        if not GEMINI_API_KEY:
            logger.error("GEMINI_API_KEY not configured")
            return TitleGenerationResponse(
                title="שיחה חדשה",
                success=False,
                error="AI service not available"
            )

        if not request.prompt or not request.prompt.strip():
            return TitleGenerationResponse(
                title="שיחה חדשה",
                success=False,
                error="Empty prompt provided"
            )

        # הגדרת המודל
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # הוספת הנחיות נוספות לבטיחות ואיכות
        enhanced_prompt = f"""
{request.prompt}

דרישות נוספות:
- אל תחזיר יותר מכותרת אחת בלבד
- הכותרת צריכה להיות ללא סימני פיסוק מיותרים בסוף
- אל תכלול מירכאות או סוגריים
- אל תחזיר הסברים נוספים, רק את הכותרת
- הכותרת צריכה להיות מקצועית ומתאימה למכללה

כותרת:"""

        # יצירת התשובה
        response = await model.generate_content_async(enhanced_prompt)
        
        if not response or not response.text:
            logger.warning("Empty response from Gemini model")
            return TitleGenerationResponse(
                title="שיחה חדשה",
                success=False,
                error="Empty response from AI model"
            )

        # ניקוי התשובה
        title = response.text.strip()
        
        # הסרת סימני פיסוק מיותרים
        title = title.replace('"', '').replace("'", "").replace(':', '').replace('.', '')
        title = title.strip()

        # ווידוא שהכותרת לא ארוכה מדי
        if len(title) > 60:
            title = title[:57] + "..."

        # ווידוא שיש תוכן
        if not title or title.lower().strip() in ['כותרת', 'title', '']:
            title = "שיחה חדשה"

        logger.info(f"Generated title: {title}")
        
        return TitleGenerationResponse(
            title=title,
            success=True
        )

    except Exception as e:
        logger.error(f"Error generating title: {str(e)}")
        return TitleGenerationResponse(
            title="שיחה חדשה",
            success=False,
            error=str(e)
        ) 