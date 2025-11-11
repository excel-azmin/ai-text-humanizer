"""
Text Analysis Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import (
    AnalyzeRequest, AnalyzeResponse, DetectRequest, DetectResponse
)
from app.core.dependencies import get_humanizer_service
from app.services.humanizer_service import HumanizerService
from app.core.logging import logger

router = APIRouter(prefix="/analyze", tags=["analyze"])


@router.post("", response_model=AnalyzeResponse)
async def analyze_text(request: AnalyzeRequest):
    """Analyze text for AI patterns"""
    
    try:
        text = request.text
        sentences = text.split('.')
        sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
        
        # Simple AI pattern detection
        ai_patterns = {
            "repetitive_structure": False,
            "uniform_sentence_length": False,
            "lack_of_contractions": False,
            "formal_tone": False,
            "perfect_grammar": False,
            "ai_phrases": []
        }
        
        # Check for uniform sentence length
        variance = 0
        if sentence_lengths:
            avg_length = sum(sentence_lengths) / len(sentence_lengths)
            variance = sum((l - avg_length) ** 2 for l in sentence_lengths) / len(sentence_lengths)
            ai_patterns["uniform_sentence_length"] = variance < 10
        
        # Check for contractions
        contractions = ["'s", "'t", "'re", "'ve", "'ll", "'d", "'m"]
        has_contractions = any(c in text for c in contractions)
        ai_patterns["lack_of_contractions"] = not has_contractions
        
        # Check for AI-typical phrases
        ai_phrases = [
            "it is important to note",
            "in conclusion",
            "furthermore",
            "moreover",
            "nevertheless",
            "it should be noted",
            "in summary"
        ]
        found_phrases = [phrase for phrase in ai_phrases if phrase in text.lower()]
        ai_patterns["ai_phrases"] = found_phrases
        
        # Calculate AI probability score
        ai_score = 0
        if ai_patterns["uniform_sentence_length"]:
            ai_score += 25
        if ai_patterns["lack_of_contractions"]:
            ai_score += 25
        if len(found_phrases) > 2:
            ai_score += 25
        if variance < 5:
            ai_score += 25
        
        return AnalyzeResponse(
            text_length=len(text),
            sentence_count=len(sentences),
            ai_patterns_detected=ai_patterns,
            ai_probability=f"{ai_score}%",
            recommendation="High humanization needed" if ai_score > 50 else "Light touch-up sufficient"
        )
        
    except Exception as e:
        logger.error(f"Analysis error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/detect-and-humanize", response_model=DetectResponse)
async def detect_and_humanize(
    request: DetectRequest,
    humanizer_service: HumanizerService = Depends(get_humanizer_service)
):
    """Analyze text and automatically humanize based on detection"""
    from app.api.v1.humanize import humanize_text
    
    try:
        # First analyze
        analysis_request = AnalyzeRequest(text=request.text)
        analysis = await analyze_text(analysis_request)
        analysis_dict = analysis.dict()
        
        # Determine intensity based on AI probability
        ai_score = int(analysis.ai_probability.rstrip('%'))
        if ai_score > 75:
            intensity = 0.9
            mode = "quality"
        elif ai_score > 50:
            intensity = 0.7
            mode = "balanced"
        else:
            intensity = 0.5
            mode = "fast"
        
        # Humanize with appropriate settings
        humanize_request = HumanizeRequest(
            text=request.text,
            mode=mode,
            intensity=intensity,
            preserve_meaning=True
        )
        
        humanized_response = await humanize_text(
            humanize_request,
            humanizer_service=humanizer_service
        )
        
        return DetectResponse(
            analysis=analysis_dict,
            humanization=humanized_response.dict(),
            auto_settings={
                "mode": mode,
                "intensity": intensity,
                "reason": f"Based on {ai_score}% AI probability"
            }
        )
        
    except Exception as e:
        logger.error(f"Detect and humanize error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

