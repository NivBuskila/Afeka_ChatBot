import logging
import json
import sys
from pathlib import Path
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

# Add the AI services path to sys.path
ai_services_path = Path(__file__).parent.parent.parent.parent.parent / "ai"
if str(ai_services_path) not in sys.path:
    sys.path.insert(0, str(ai_services_path))

# Import from Supabase-enabled modules
try:
    from src.ai.config.current_profile import get_current_profile, set_current_profile
    from src.ai.config.rag_config_profiles import get_profile, save_new_profile, delete_profile
    
    # Define get_available_profiles as our fresh function
    def get_available_profiles():
        return _get_fresh_available_profiles()
        
except ImportError:
    # Try alternative import paths
    import sys
    import os
    ai_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'ai')
    sys.path.insert(0, ai_path)
    try:
        from config.current_profile import get_current_profile, set_current_profile
        from config.rag_config_profiles import get_profile, save_new_profile, delete_profile
        
        # Define get_available_profiles as our fresh function
        def get_available_profiles():
            return _get_fresh_available_profiles()
            
    except ImportError:
        # Fallback functions if AI modules are not available
        def get_current_profile():
            return "maximum_accuracy"
        def set_current_profile(profile_name):
            pass
        def get_available_profiles():
            return _get_fresh_available_profiles()
        def save_new_profile(profile_id, profile_data):
            pass
        def delete_profile(profile_id):
            return False
        get_profile = None

logger = logging.getLogger(__name__)
router = APIRouter(tags=["RAG Management"])

def _get_fresh_available_profiles():
    """Get fresh list of available profiles including dynamically created ones"""
    logger.info("_get_fresh_available_profiles called")
    
    # Force reload of the modules to get fresh data
    try:
        import importlib
        import sys
        
        # Reload the modules if they're already loaded
        if 'src.ai.config.rag_config_profiles' in sys.modules:
            importlib.reload(sys.modules['src.ai.config.rag_config_profiles'])
            logger.info("Reloaded rag_config_profiles module")
        
        if 'src.ai.config.current_profile' in sys.modules:
            importlib.reload(sys.modules['src.ai.config.current_profile'])
            logger.info("Reloaded current_profile module")
            
    except Exception as reload_error:
        logger.warning(f"Could not reload modules: {reload_error}")
    
    # Try to import the new list_profiles function that filters hidden profiles
    try:
        from src.ai.config.rag_config_profiles import list_profiles
        available = list_profiles()  # This already filters hidden profiles
        logger.info(f"Available profiles (filtered): {list(available.keys())}")
        return available
    except ImportError as e:
        logger.error(f"Could not import list_profiles: {e}")
        raise HTTPException(status_code=500, detail="Could not load profile configurations")

def get_real_config_for_profile(profile_id: str) -> Dict[str, Any]:
    """
    קבלת הקונפיגורציה האמיתית של פרופיל
    """
    if get_profile is None:
        # Fallback אם לא ניתן לייבא
        return {
            "similarityThreshold": 0.4,
            "maxChunks": 20,
            "temperature": 0.1,
            "modelName": "gemini-2.0-flash",
            "chunkSize": 2000,
            "chunkOverlap": 200,
            "maxContextTokens": 8000
        }
    
    try:
        actual_config = get_profile(profile_id)
        return {
            "similarityThreshold": actual_config.search.SIMILARITY_THRESHOLD,
            "maxChunks": actual_config.search.MAX_CHUNKS_RETRIEVED,
            "maxChunksForContext": actual_config.search.MAX_CHUNKS_FOR_CONTEXT,
            "temperature": actual_config.llm.TEMPERATURE,
            "modelName": "gemini-2.0-flash",  # כרגע קבוע
            "chunkSize": actual_config.chunk.DEFAULT_CHUNK_SIZE,
            "chunkOverlap": actual_config.chunk.DEFAULT_CHUNK_OVERLAP,
            "maxContextTokens": actual_config.context.MAX_CONTEXT_TOKENS,
            "targetTokensPerChunk": actual_config.chunk.TARGET_TOKENS_PER_CHUNK,
            "hybridSemanticWeight": actual_config.search.HYBRID_SEMANTIC_WEIGHT,
            "hybridKeywordWeight": actual_config.search.HYBRID_KEYWORD_WEIGHT
        }
    except Exception as e:
        logger.error(f"Error getting real config for {profile_id}: {e}")
        return {
            "similarityThreshold": 0.4,
            "maxChunks": 20,
            "temperature": 0.1,
            "modelName": "gemini-2.0-flash",
            "chunkSize": 2000,
            "chunkOverlap": 200,
            "maxContextTokens": 8000
        }

def get_profile_characteristics(profile_id: str, config: Dict[str, Any], language: str = "he") -> Dict[str, Any]:
    """
    קבלת מאפיינים וצפי ביצועים מהקונפיגורציה האמיתית
    """
    characteristics = {
        "focus": "",
        "expectedSpeed": "",
        "expectedQuality": "",
        "bestFor": "",
        "tradeoffs": ""
    }
    
    # בדיקה אם זה פרופיל דינמי עם מאפיינים שמורים
    try:
        from src.ai.config.rag_config_profiles import load_dynamic_profiles
        dynamic_profiles = load_dynamic_profiles()
        
        if profile_id in dynamic_profiles:
            saved_characteristics = dynamic_profiles[profile_id].get('characteristics', {})
            logger.debug(f"Loading saved characteristics for {profile_id}: {saved_characteristics}")
            if saved_characteristics and any(saved_characteristics.values()):
                # אם יש מאפיינים שמורים, השתמש בהם במקום ליצור חדשים
                characteristics.update(saved_characteristics)
                logger.debug(f"Updated characteristics for {profile_id}: {characteristics}")
                return characteristics
    except Exception as e:
        logger.warning(f"Could not load dynamic profile characteristics for {profile_id}: {e}")
    
    # ניתוח מאפיינים לפי הקונפיגורציה האמיתית (רק לפרופילים סטטיים)
    similarity_threshold = config.get("similarityThreshold", 0.4)
    max_chunks = config.get("maxChunks", 20)
    temperature = config.get("temperature", 0.1)
    chunk_size = config.get("chunkSize", 2000)
    
    # Define characteristics for each profile in both languages
    profile_characteristics = {
        "enhanced_testing": {
            "he": {
                "focus": "זיהוי מדויק של סעיפים ספציפיים",
                "expectedSpeed": f"איטי מאוד ({max_chunks} צ'אנקים, סף נמוך {similarity_threshold})",
                "expectedQuality": f"דיוק מקסימלי (טמפ׳ קפואה: {temperature})",
                "bestFor": "בדיקות פרמטריות מדויקות, זיהוי סעיפי תקנון",
                "tradeoffs": "זמן תגובה ארוך תמורת דיוק מקסימלי"
            },
            "en": {
                "focus": "Precise section identification and detailed analysis",
                "expectedSpeed": f"Very slow ({max_chunks} chunks, low threshold {similarity_threshold})",
                "expectedQuality": f"Maximum accuracy (frozen temp: {temperature})",
                "bestFor": "Parametric testing, regulation section identification",
                "tradeoffs": "Long response time for maximum precision"
            }
        },
        "high_quality": {
            "he": {
                "focus": "איכות תשובות גבוהה עם דיוק מעולה",
                "expectedSpeed": f"איטי-בינוני ({max_chunks} צ'אנקים, סף גבוה {similarity_threshold})",
                "expectedQuality": f"גבוה מאוד (טמפ׳ נמוכה: {temperature})",
                "bestFor": "שאלות מורכבות הדורשות תשובות מפורטות",
                "tradeoffs": "מאוזן - איכות גבוהה במחיר זמן סביר"
            },
            "en": {
                "focus": "High-quality responses with excellent accuracy",
                "expectedSpeed": f"Slow-medium ({max_chunks} chunks, high threshold {similarity_threshold})",
                "expectedQuality": f"Very high (low temp: {temperature})",
                "bestFor": "Complex questions requiring detailed answers",
                "tradeoffs": "Balanced - high quality at reasonable time cost"
            }
        },
        "balanced": {
            "he": {
                "focus": "איזון אופטימלי בין מהירות לדיוק",
                "expectedSpeed": f"בינוני ({max_chunks} צ'אנקים, סף מאוזן {similarity_threshold})",
                "expectedQuality": f"טוב-גבוה (טמפ׳ מאוזנת: {temperature})",
                "bestFor": "שימוש יומיומי כללי, רוב השאלות",
                "tradeoffs": "הפשרה הטובה ביותר לשימוש רגיל"
            },
            "en": {
                "focus": "Optimal balance between speed and accuracy",
                "expectedSpeed": f"Medium ({max_chunks} chunks, balanced threshold {similarity_threshold})",
                "expectedQuality": f"Good-high (balanced temp: {temperature})",
                "bestFor": "General daily use, most questions",
                "tradeoffs": "Best compromise for regular usage"
            }
        },
        "fast": {
            "he": {
                "focus": "תגובות מהירות לשאלות פשוטות",
                "expectedSpeed": f"מהיר ({max_chunks} צ'אנקים מעטים, סף גבוה {similarity_threshold})",
                "expectedQuality": f"בסיסי-טוב (טמפ׳ גבוהה: {temperature})",
                "bestFor": "שאלות פשוטות, חיפוש מהיר, סקירה כללית",
                "tradeoffs": "מהירות גבוהה אך עלול להחמיץ פרטים"
            },
            "en": {
                "focus": "Fast responses for simple questions",
                "expectedSpeed": f"Fast ({max_chunks} few chunks, high threshold {similarity_threshold})",
                "expectedQuality": f"Basic-good (high temp: {temperature})",
                "bestFor": "Simple questions, quick search, general overview",
                "tradeoffs": "High speed but may miss details"
            }
        },
        "improved": {
            "he": {
                "focus": "זיהוי מידע נסתר וחסר ברמה עמוקה",
                "expectedSpeed": f"בינוני-איטי ({max_chunks} צ'אנקים, סף נמוך {similarity_threshold})",
                "expectedQuality": f"גבוה עם כיסוי רחב (טמפ׳: {temperature})",
                "bestFor": "מקרים שפרופילים אחרים החמיצו מידע",
                "tradeoffs": "יותר 'רעש' אך מוצא מידע נסתר"
            },
            "en": {
                "focus": "Deep hidden and missing information detection",
                "expectedSpeed": f"Medium-slow ({max_chunks} chunks, low threshold {similarity_threshold})",
                "expectedQuality": f"High with broad coverage (temp: {temperature})",
                "bestFor": "Cases where other profiles missed information",
                "tradeoffs": "More 'noise' but finds hidden information"
            }
        },
        "debug": {
            "he": {
                "focus": "ניתוח מפורט עם לוגים מלאים לפיתוח",
                "expectedSpeed": f"איטי עם לוגים ({max_chunks} צ'אנקים, סף {similarity_threshold})",
                "expectedQuality": f"משתנה עם תובנות (טמפ׳: {temperature})",
                "bestFor": "פיתוח מערכת, ניתוח ביצועים, בדיקות",
                "tradeoffs": "הרבה מידע נוסף אך איטי מאוד"
            },
            "en": {
                "focus": "Detailed analysis with full logs for development",
                "expectedSpeed": f"Slow with logs ({max_chunks} chunks, threshold {similarity_threshold})",
                "expectedQuality": f"Variable with insights (temp: {temperature})",
                "bestFor": "System development, performance analysis, testing",
                "tradeoffs": "Lots of extra info but very slow"
            }
        },
        "optimized_testing": {
            "he": {
                "focus": "ביצועים מאוזנים מבוססי ניתוח נתונים",
                "expectedSpeed": f"בינוני-מהיר ({max_chunks} צ'אנקים, סף {similarity_threshold})",
                "expectedQuality": f"גבוה ועקבי (טמפ׳ נמוכה: {temperature})",
                "bestFor": "בדיקות שגרתיות עם דרישות איכות",
                "tradeoffs": "איזון מושכל בין דיוק לביצועים"
            },
            "en": {
                "focus": "Data-driven balanced performance optimization",
                "expectedSpeed": f"Medium-fast ({max_chunks} chunks, threshold {similarity_threshold})",
                "expectedQuality": f"High and consistent (low temp: {temperature})",
                "bestFor": "Routine testing with quality requirements",
                "tradeoffs": "Smart balance between accuracy and performance"
            }
        },
        "maximum_accuracy": {
            "he": {
                "focus": "דיוק מוחלט ללא פשרות - מצב קיצוני",
                "expectedSpeed": f"איטי מאוד ({max_chunks} צ'אנקים רבים, סף גבוה {similarity_threshold})",
                "expectedQuality": f"מקסימלי-מושלם (טמפ׳ דטרמיניסטית: {temperature})",
                "bestFor": "מקרים קריטיים, וולידציה סופית, מחקר",
                "tradeoffs": "רק התאמות מדויקות ביותר - איכות מקסימלית"
            },
            "en": {
                "focus": "Absolute precision with no compromises - extreme mode",
                "expectedSpeed": f"Very slow ({max_chunks} many chunks, high threshold {similarity_threshold})",
                "expectedQuality": f"Maximum-perfect (deterministic temp: {temperature})",
                "bestFor": "Critical cases, final validation, research",
                "tradeoffs": "Only most precise matches - maximum quality"
            }
        }
    }
    
    # Get characteristics for the profile and language
    if profile_id in profile_characteristics and language in profile_characteristics[profile_id]:
        characteristics.update(profile_characteristics[profile_id][language])
    else:
        # Fallback to default characteristics
        lang_suffix = "he" if language == "he" else "en"
        if lang_suffix == "he":
            characteristics.update({
                "focus": "פרופיל כללי",
                "expectedSpeed": f"בינוני ({max_chunks} צ'אנקים)",
                "expectedQuality": f"טוב (סף: {similarity_threshold})",
                "bestFor": "שימוש כללי",
                "tradeoffs": "איזון בסיסי"
            })
        else:
            characteristics.update({
                "focus": "General profile",
                "expectedSpeed": f"Medium ({max_chunks} chunks)",
                "expectedQuality": f"Good (threshold: {similarity_threshold})",
                "bestFor": "General use",
                "tradeoffs": "Basic balance"
            })
    
    return characteristics

@router.get("/profiles")
async def get_rag_profiles(language: str = "he"):
    """Get all available RAG profiles with their configurations"""
    try:
        current_profile_id = get_current_profile()
        available_profiles = get_available_profiles()
        logger.debug(f"Available profiles from get_available_profiles(): {list(available_profiles.keys())}")
        
        profiles_data = []
        for profile_id, description in available_profiles.items():
            try:
                # Get real configuration
                real_config = get_real_config_for_profile(profile_id)
                
                # Get characteristics based on language
                characteristics = get_profile_characteristics(profile_id, real_config, language)
                
                # Check if this is a custom (deletable) profile
                built_in_profiles = {"high_quality", "fast", "balanced", "improved", "debug", 
                                   "enhanced_testing", "optimized_testing", "maximum_accuracy"}
                is_custom = profile_id not in built_in_profiles
                
                # Create profile data
                profile_data = {
                    "id": profile_id,
                    "name": profile_id.replace('_', ' ').title(),
                    "description": description,
                    "isActive": profile_id == current_profile_id,
                    "isCustom": is_custom,
                    "config": real_config,
                    "characteristics": characteristics
                }
                
                profiles_data.append(profile_data)
                
            except Exception as e:
                logger.error(f"Error loading profile {profile_id}: {e}")
                continue
        
        return JSONResponse(content={
            "currentProfile": current_profile_id,
            "profiles": profiles_data
        })
        
    except Exception as e:
        logger.error(f"Error getting RAG profiles: {e}")
        raise HTTPException(status_code=500, detail=f"Error loading profiles: {str(e)}")

@router.post("/profiles/{profile_id}/activate")
async def activate_rag_profile(profile_id: str):
    """Activate a specific RAG profile"""
    try:
        available_profiles = get_available_profiles()
        
        if profile_id not in available_profiles:
            raise HTTPException(
                status_code=404, 
                detail=f"Profile '{profile_id}' not found. Available profiles: {list(available_profiles.keys())}"
            )
        
        # Set the new profile
        success = set_current_profile(profile_id)
        
        if not success:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to activate profile: {profile_id}"
            )
        
        logger.info(f"Successfully activated RAG profile: {profile_id}")
        
        return JSONResponse(
            content={
                "message": f"Successfully activated profile: {profile_id}",
                "activeProfile": profile_id,
                "profileDescription": available_profiles[profile_id]
            }
        )
        
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.exception(f"Error activating RAG profile {profile_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error activating profile: {profile_id}")

@router.get("/current-profile")
async def get_current_rag_profile():
    """Get the currently active RAG profile"""
    try:
        current_profile_name = get_current_profile()
        available_profiles = get_available_profiles()
        
        if current_profile_name not in available_profiles:
            logger.warning(f"Current profile '{current_profile_name}' not found in available profiles")
            return JSONResponse(
                content={
                    "profileId": current_profile_name,
                    "description": "Unknown profile",
                    "isValid": False
                }
            )
        
        return JSONResponse(
            content={
                "profileId": current_profile_name,
                "description": available_profiles[current_profile_name],
                "isValid": True
            }
        )
        
    except Exception as e:
        logger.exception(f"Error getting current RAG profile: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving current RAG profile")

@router.post("/test")
async def test_rag_query(request: Dict[str, Any]):
    """Test a query with the current RAG configuration"""
    try:
        query = request.get("query", "").strip()
        
        if not query:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Import RAGService here to avoid circular imports
        try:
            from src.ai.services.rag_service import RAGService
            
            # Create RAG service with current profile
            rag_service = RAGService()
            
            # Run the test query
            result = await rag_service.generate_answer(query, search_method="hybrid")
            
            # Get chunk text for display
            chunk_text = ""
            chunks_selected = result.get("chunks_selected", [])
            if chunks_selected:
                # Take the first chunk as the main chunk text
                first_chunk = chunks_selected[0]
                chunk_text = first_chunk.get("chunk_text", first_chunk.get("content", ""))
            
            return JSONResponse(
                content={
                    "query": query,
                    "answer": result.get("answer", "No answer generated"),
                    "responseTime": result.get("response_time_ms", 0),
                    "sourcesFound": len(result.get("sources", [])),
                    "chunks": len(result.get("chunks_selected", [])),
                    "searchMethod": result.get("search_method", "unknown"),
                    "configUsed": result.get("config_used", {}),
                    "chunkText": chunk_text
                }
            )
            
        except ImportError as import_err:
            logger.error(f"Could not import RAGService: {import_err}")
            raise HTTPException(status_code=500, detail="RAG service not available")
            
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.exception(f"Error testing RAG query: {e}")
        raise HTTPException(status_code=500, detail="Error processing RAG test query")

@router.post("/profiles")
async def create_rag_profile(request: Dict[str, Any]):
    """Create a new RAG profile"""
    try:
        profile_id = request.get("id", "").strip()
        profile_name = request.get("name", "").strip()
        profile_description = request.get("description", "").strip()
        profile_config = request.get("config", {})
        profile_characteristics = request.get("characteristics", {})
        
        if not profile_id or not profile_name:
            raise HTTPException(status_code=400, detail="Profile ID and name are required")
        
        # Check if profile already exists
        available_profiles = get_available_profiles()
        if profile_id in available_profiles:
            raise HTTPException(status_code=400, detail=f"Profile '{profile_id}' already exists")
        
        # Validate configuration values
        required_config_fields = [
            "similarityThreshold", "maxChunks", "temperature", "modelName"
        ]
        for field in required_config_fields:
            if field not in profile_config:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Missing required configuration field: {field}"
                )
        
        # Create the profile data for saving
        profile_data = {
            "id": profile_id,
            "name": profile_name,
            "description": profile_description,
            "config": profile_config,
            "characteristics": profile_characteristics,
            "isActive": False
        }
        
        # Save the profile using the new function
        try:
            save_new_profile(profile_id, profile_data)
            logger.info(f"Successfully saved custom profile: {profile_id}")
            
            # Create full profile object for response
            created_profile = {
                "id": profile_id,
                "name": profile_name,
                "description": profile_description,
                "isActive": False,
                "isCustom": True,
                "config": profile_config,
                "characteristics": profile_characteristics
            }
            
            return JSONResponse(
                content={
                    "message": f"Successfully created profile: {profile_name}",
                    "profile": created_profile
                }
            )
            
        except Exception as save_error:
            logger.error(f"Error saving profile: {save_error}")
            raise HTTPException(
                status_code=500, 
                detail=f"Error saving profile: {str(save_error)}"
            )
            
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.exception(f"Error creating RAG profile: {e}")
        raise HTTPException(status_code=500, detail="Error creating RAG profile")

@router.delete("/profiles/{profile_id}")
async def delete_rag_profile(profile_id: str, force: bool = False, permanent: bool = None):
    """Delete custom profiles permanently or hide built-in profiles"""
    try:
        # Check if profile exists
        available_profiles = get_available_profiles()
        if profile_id not in available_profiles:
            raise HTTPException(
                status_code=404, 
                detail=f"Profile '{profile_id}' not found"
            )
        
        # Check if trying to delete current active profile
        current_profile = get_current_profile()
        if profile_id == current_profile:
            raise HTTPException(
                status_code=400, 
                detail="Cannot delete the currently active profile. Please switch to another profile first."
            )
        
        from src.ai.config.supabase_profile_manager import get_supabase_profile_manager
        
        manager = get_supabase_profile_manager()
        
        # Check if it's a built-in profile
        built_in_profiles = [
            'high_quality', 'fast', 'balanced', 'improved', 'debug',
            'enhanced_testing', 'optimized_testing', 'maximum_accuracy'
        ]
        
        is_builtin = profile_id in built_in_profiles
        
        if is_builtin:
            # Built-in profiles can only be hidden, never permanently deleted
            if permanent is True:
                raise HTTPException(
                    status_code=400,
                    detail="Built-in profiles cannot be permanently deleted. They can only be hidden."
                )
            
            # Require force for built-in profiles
            if not force:
                raise HTTPException(
                    status_code=400,
                    detail="Built-in profile deletion requires force=true parameter"
                )
            
            # Hide the built-in profile
            success = manager.set_profile_hidden(profile_id, True)
            
            if success:
                logger.info(f"Successfully hidden built-in profile: {profile_id}")
                return {
                    "message": f"Successfully deleted מובנה profile: {profile_id}",
                    "profile_id": profile_id,
                    "action": "hidden"
                }
            else:
                raise HTTPException(status_code=500, detail="Failed to hide profile")
        
        else:
            # Custom profiles: hard delete by default, soft delete only if permanent=false explicitly
            if permanent is False:
                # Explicitly requested soft delete
                success = manager.delete_profile(profile_id)
                action = "soft_deleted"
                message = f"Successfully soft deleted custom profile: {profile_id}"
            else:
                # Default behavior (permanent=None or permanent=True): hard delete custom profiles
                success = manager.hard_delete_profile(profile_id)
                action = "permanently_deleted"
                message = f"Successfully permanently deleted custom profile: {profile_id}"
            
            if success:
                logger.info(f"Successfully {action} custom profile: {profile_id}")
                return {
                    "message": message,
                    "profile_id": profile_id,
                    "action": action
                }
            else:
                raise HTTPException(status_code=500, detail="Failed to delete profile")
        
    except Exception as e:
        logger.error(f"Error deleting profile {profile_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting profile: {str(e)}")

@router.post("/profiles/{profile_id}/restore")
async def restore_rag_profile(profile_id: str):
    """Restore a hidden profile"""
    try:
        from src.ai.config.supabase_profile_manager import get_supabase_profile_manager
        
        manager = get_supabase_profile_manager()
        
        # Check if profile is hidden
        hidden_profiles = manager.get_hidden_profiles()
        if profile_id not in hidden_profiles:
            raise HTTPException(
                status_code=404, 
                detail=f"Profile '{profile_id}' is not hidden or does not exist"
            )
        
        # Restore the profile (set it as visible)
        success = manager.set_profile_hidden(profile_id, False)
        
        if success:
            logger.info(f"Successfully restored profile: {profile_id}")
            return JSONResponse(
                content={
                    "message": f"Successfully restored profile: {profile_id}",
                    "restoredProfile": profile_id,
                    "note": "Profile is now visible in the profiles list"
                }
            )
        else:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to restore profile '{profile_id}'"
            )
            
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.exception(f"Error restoring RAG profile {profile_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error restoring profile: {profile_id}")

@router.get("/hidden-profiles")
async def get_hidden_profiles():
    """Get list of hidden profiles from Supabase"""
    try:
        from src.ai.config.supabase_profile_manager import get_supabase_profile_manager
        
        manager = get_supabase_profile_manager()
        hidden_profiles = manager.get_hidden_profiles()
        
        return JSONResponse(
            content={
                "hiddenProfiles": hidden_profiles
            }
        )
        
    except Exception as e:
        logger.exception(f"Error getting hidden profiles: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving hidden profiles")

@router.delete("/profiles/{profile_id}/permanent")
async def permanently_delete_profile(profile_id: str, confirm: bool = False):
    """Permanently delete a profile from the database (HARD DELETE)"""
    try:
        # Safety check - require explicit confirmation
        if not confirm:
            raise HTTPException(
                status_code=400,
                detail="Permanent deletion requires confirm=true parameter. This action cannot be undone!"
            )
        
        # Check if profile exists
        available_profiles = get_available_profiles()
        if profile_id not in available_profiles:
            raise HTTPException(
                status_code=404, 
                detail=f"Profile '{profile_id}' not found"
            )
        
        # Check if trying to delete current active profile
        current_profile = get_current_profile()
        if profile_id == current_profile:
            raise HTTPException(
                status_code=400, 
                detail="Cannot permanently delete the currently active profile. Please switch to another profile first."
            )
        
        from src.ai.config.supabase_profile_manager import get_supabase_profile_manager
        
        manager = get_supabase_profile_manager()
        
        # Check if it's a built-in profile
        built_in_profiles = [
            'high_quality', 'fast', 'balanced', 'improved', 'debug',
            'enhanced_testing', 'optimized_testing', 'maximum_accuracy'
        ]
        
        if profile_id in built_in_profiles:
            raise HTTPException(
                status_code=400,
                detail="Built-in profiles cannot be permanently deleted. They can only be hidden."
            )
        
        # Perform hard delete
        success = manager.hard_delete_profile(profile_id)
        
        if success:
            logger.warning(f"🔥 PERMANENTLY DELETED profile: {profile_id}")
            return {
                "message": f"Profile '{profile_id}' has been permanently deleted from the database",
                "profile_id": profile_id,
                "action": "permanently_deleted",
                "warning": "This action cannot be undone"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to permanently delete profile")
        
    except Exception as e:
        logger.error(f"Error permanently deleting profile {profile_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error permanently deleting profile: {str(e)}") 