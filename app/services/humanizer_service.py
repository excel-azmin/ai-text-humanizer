"""
Humanizer Service
Service layer for text humanization
"""

from typing import Optional
import torch
from app.services.engine import HumanizerEngine, DetectionEvasion
from app.core.config import settings
from app.core.logging import logger


class HumanizerService:
    """Service for managing humanizer instances"""
    
    def __init__(self):
        self.fast_humanizer: Optional[HumanizerEngine] = None
        self.standard_humanizer: Optional[HumanizerEngine] = None
        self.advanced_humanizer: Optional[HumanizerEngine] = None
        self._initialized = False
    
    def initialize(self):
        """Initialize all humanizer instances"""
        if self._initialized:
            return
        
        logger.info("Initializing humanizer models...")
        
        try:
            # Fast mode - minimal models
            self.fast_humanizer = HumanizerEngine(
                use_gpu=False,  # CPU for consistency
                model_size=settings.MODEL_SIZE_FAST,
                techniques=["sentence_variation", "human_patterns"]
            )
            logger.info("Fast humanizer initialized")
            
            # Balanced mode
            self.standard_humanizer = HumanizerEngine(
                use_gpu=settings.USE_GPU and torch.cuda.is_available(),
                model_size=settings.MODEL_SIZE_BALANCED,
                techniques=["sentence_variation", "human_patterns", "semantic_paraphrasing"]
            )
            logger.info("Standard humanizer initialized")
            
            # Quality mode - all techniques
            self.advanced_humanizer = HumanizerEngine(
                use_gpu=settings.USE_GPU and torch.cuda.is_available(),
                model_size=settings.MODEL_SIZE_QUALITY,
                techniques=[
                    "sentence_variation",
                    "perplexity_modulation",
                    "stylistic_injection",
                    "semantic_paraphrasing",
                    "human_patterns"
                ]
            )
            logger.info("Advanced humanizer initialized")
            
            self._initialized = True
            logger.info("All humanizer models initialized successfully!")
            
        except Exception as e:
            logger.error(f"Error initializing humanizers: {e}")
            raise
    
    def get_humanizer(self, mode: str) -> HumanizerEngine:
        """Get humanizer instance based on mode"""
        if not self._initialized:
            raise RuntimeError("Humanizer service not initialized")
        
        if mode == "fast":
            return self.fast_humanizer
        elif mode == "balanced":
            return self.standard_humanizer
        elif mode == "quality":
            return self.advanced_humanizer
        else:
            raise ValueError(f"Invalid mode: {mode}")
    
    def is_initialized(self) -> bool:
        """Check if service is initialized"""
        return self._initialized


