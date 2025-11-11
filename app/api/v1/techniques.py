"""
Techniques Endpoint
"""

from fastapi import APIRouter
from app.models.schemas import TechniquesResponse, TechniqueInfo

router = APIRouter(prefix="/techniques", tags=["techniques"])


@router.get("", response_model=TechniquesResponse)
async def get_techniques():
    """Get available humanization techniques"""
    return TechniquesResponse(
        techniques=[
            TechniqueInfo(
                name="sentence_variation",
                description="Varies sentence structure and length",
                speed="fast"
            ),
            TechniqueInfo(
                name="perplexity_modulation",
                description="Adds controlled unpredictability to word choices",
                speed="medium"
            ),
            TechniqueInfo(
                name="stylistic_injection",
                description="Injects human-like stylistic elements",
                speed="medium"
            ),
            TechniqueInfo(
                name="semantic_paraphrasing",
                description="Paraphrases while preserving meaning",
                speed="slow"
            ),
            TechniqueInfo(
                name="human_patterns",
                description="Adds human writing patterns and minor imperfections",
                speed="fast"
            )
        ]
    )


