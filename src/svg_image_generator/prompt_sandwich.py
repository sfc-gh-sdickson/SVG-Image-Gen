"""
Prompt Sandwich implementation for SVG Image Generator.

This module implements the prompt sandwich approach for improved SVG generation
by refining user prompts through Cortex AI before generating the final SVG.
"""

import logging
from typing import Tuple

from snowflake.snowpark import Session

from .cortex import safe_cortex_call

# Set up logging
logger = logging.getLogger(__name__)


def refine_prompt_with_cortex(session: Session, raw_prompt: str, model: str) -> str:
    """Use Cortex to refine and structure the user prompt"""
    try:
        logger.info(f"[Prompt Sandwich] Refining prompt with {model}")

        refinement_prompt = f"""You are an expert SVG generation assistant. Given this user request, create a clear, specific prompt for generating an SVG:

User Request: {raw_prompt}

Generate a refined prompt that:
1. Is specific about visual elements (colors, shapes, layout)
2. Includes appropriate dimensions if mentioned
3. Specifies style preferences
4. Is optimized for SVG generation
5. Maintains the user's original intent

Return only the refined prompt, no explanations."""

        refined_prompt = safe_cortex_call(
            session, model, refinement_prompt, "Prompt refinement"
        )

        if refined_prompt:
            logger.info(f"[Prompt Sandwich] Refined prompt: {refined_prompt}")
            return refined_prompt.strip()
        else:
            logger.warning(
                "[Prompt Sandwich] Refinement returned no result, using original prompt"
            )
            return raw_prompt

    except Exception as e:
        logger.error(f"[Prompt Sandwich] Error refining prompt: {e}")
        # Note: We don't have access to st here, so we log the warning
        logger.warning(f"⚠️ Prompt refinement failed: {str(e)}. Using original prompt.")
        return raw_prompt


def generate_svg_with_refined_prompt(
    session: Session, refined_prompt: str, model: str
) -> str:
    """Generate SVG using the refined prompt"""
    try:
        logger.info(f"[Prompt Sandwich] Generating SVG with {model}")

        generation_prompt = f"""Generate a complete, valid SVG file based on this description: {refined_prompt}

Return only the SVG code starting with <svg> and ending with </svg>.
Make sure the SVG is properly formatted and includes all necessary attributes like viewBox, width, and height.
Do not include any explanatory text, just the SVG code."""

        svg_content = safe_cortex_call(
            session, model, generation_prompt, "SVG generation"
        )

        if svg_content:
            logger.info("[Prompt Sandwich] SVG generation completed")
            return svg_content
        else:
            raise ValueError("SVG generation returned no content")

    except Exception as e:
        logger.error(f"[Prompt Sandwich] Error generating SVG: {e}")
        raise e


def implement_prompt_sandwich(
    session: Session, user_prompt: str, model: str
) -> Tuple[str, str, str]:
    """Implement complete prompt sandwich approach"""
    try:
        logger.info(f"[Prompt Sandwich] Starting prompt sandwich for: {user_prompt}")

        # Step 1: Refine the prompt
        refined_prompt = refine_prompt_with_cortex(session, user_prompt, model)

        # Step 2: Generate SVG
        svg_content = generate_svg_with_refined_prompt(session, refined_prompt, model)

        return user_prompt, refined_prompt, svg_content

    except Exception as e:
        logger.error(f"[Prompt Sandwich] Error in prompt sandwich: {e}")
        raise e
