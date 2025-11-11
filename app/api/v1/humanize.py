"""
Humanization Endpoints
"""

import time
import asyncio
from fastapi import APIRouter, HTTPException, Depends, WebSocket
from typing import Dict
import json
from datetime import datetime
from starlette.websockets import WebSocketDisconnect

from app.models.schemas import (
    HumanizeRequest, HumanizeResponse, BatchHumanizeRequest, BatchHumanizeResponse
)
from app.core.dependencies import get_humanizer_service, get_cache_service
from app.services.humanizer_service import HumanizerService
from app.services.cache_service import CacheService
from app.services.engine import DetectionEvasion
from app.core.logging import logger

router = APIRouter(prefix="/humanize", tags=["humanize"])


@router.post("", response_model=HumanizeResponse)
async def humanize_text(
    request: HumanizeRequest,
    humanizer_service: HumanizerService = Depends(get_humanizer_service),
    cache_service: CacheService = Depends(get_cache_service)
):
    """Main endpoint for text humanization"""
    
    start_time = time.time()
    
    # Check cache if enabled
    if request.cache and cache_service:
        cache_key = cache_service.generate_key(request.text, request.mode, request.intensity)
        cached = await cache_service.get(cache_key)
        if cached:
            cached["cached"] = True
            cached["processing_time"] = time.time() - start_time
            logger.info(f"Cache hit for mode: {request.mode}")
            return HumanizeResponse(**cached)
    
    try:
        # Get appropriate humanizer
        humanizer = humanizer_service.get_humanizer(request.mode)
        fast_mode = (request.mode == "fast")
        
        # Apply custom techniques if specified
        if request.techniques:
            humanizer.techniques = request.techniques
        
        # Perform humanization
        humanized = humanizer.humanize(
            request.text,
            intensity=request.intensity,
            preserve_meaning=request.preserve_meaning,
            fast_mode=fast_mode
        )
        
        # Apply additional evasion techniques
        humanized = DetectionEvasion.vary_punctuation(humanized)
        if request.intensity > 0.8:
            humanized = DetectionEvasion.add_unicode_variations(humanized)
        
        # Calculate similarity if meaning preservation is enabled
        similarity_score = None
        if request.preserve_meaning and not fast_mode:
            try:
                from sentence_transformers import SentenceTransformer
                import numpy as np
                encoder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
                orig_emb = encoder.encode([request.text])[0]
                new_emb = encoder.encode([humanized])[0]
                similarity_score = float(np.dot(orig_emb, new_emb) / 
                                       (np.linalg.norm(orig_emb) * np.linalg.norm(new_emb)))
            except Exception as e:
                logger.warning(f"Could not calculate similarity: {e}")
        
        processing_time = time.time() - start_time
        
        response = {
            "original_text": request.text,
            "humanized_text": humanized,
            "processing_time": processing_time,
            "mode": request.mode,
            "techniques_applied": humanizer.techniques,
            "similarity_score": similarity_score
        }
        
        # Cache result
        if request.cache and cache_service:
            await cache_service.set(cache_key, response)
        
        logger.info(f"Humanized text in {processing_time:.2f}s (mode: {request.mode})")
        return HumanizeResponse(**response)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Humanization error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch", response_model=BatchHumanizeResponse)
async def humanize_batch(
    request: BatchHumanizeRequest,
    humanizer_service: HumanizerService = Depends(get_humanizer_service)
):
    """Batch processing endpoint"""
    
    start_time = time.time()
    
    try:
        # Get humanizer
        humanizer = humanizer_service.get_humanizer(request.mode)
        
        # Process in parallel using asyncio
        async def process_text(text: str) -> str:
            return humanizer.humanize(
                text,
                intensity=request.intensity,
                preserve_meaning=True,
                fast_mode=True
            )
        
        # Create tasks for parallel processing
        tasks = [process_text(text) for text in request.texts]
        humanized_texts = await asyncio.gather(*tasks)
        
        results = []
        for original, humanized in zip(request.texts, humanized_texts):
            results.append({
                "original": original,
                "humanized": humanized
            })
        
        processing_time = time.time() - start_time
        
        logger.info(f"Batch processed {len(request.texts)} texts in {processing_time:.2f}s")
        
        return BatchHumanizeResponse(
            results=results,
            total_texts=len(request.texts),
            processing_time=processing_time,
            mode=request.mode
        )
        
    except Exception as e:
        logger.error(f"Batch humanization error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/ws")
async def websocket_humanize(
    websocket: WebSocket
):
    """WebSocket endpoint for real-time humanization"""
    from app.core.dependencies import humanizer_service
    
    await websocket.accept()
    logger.info("WebSocket connection established")
    
    try:
        while True:
            # Receive text from client
            data = await websocket.receive_text()
            request_data = json.loads(data)
            
            # Process text
            humanizer = humanizer_service.get_humanizer("fast")
            humanized = humanizer.humanize(
                request_data.get("text", ""),
                intensity=request_data.get("intensity", 0.7),
                preserve_meaning=True,
                fast_mode=True
            )
            
            # Send result back
            await websocket.send_json({
                "humanized": humanized,
                "timestamp": datetime.now().isoformat()
            })
    except WebSocketDisconnect:
        # Client disconnected; nothing to do
        logger.info("WebSocket disconnected")
        return
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        try:
            await websocket.close()
        except Exception:
            pass

