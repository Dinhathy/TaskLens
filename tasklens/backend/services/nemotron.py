"""
Service layer for orchestrating NVIDIA Nemotron model calls.
"""
import base64
import logging
import asyncio
from typing import Dict, Any, Tuple, List
import httpx
from core.schemas import PLAN_SCHEMA, WIRING_PLAN_SCHEMA, TaskPlan, WiringStep
from core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class NemotronService:
    """Service for orchestrating Nemotron Nano 2 VL and Nano 3 models."""

    def __init__(self):
        self.settings = get_settings()
        self.headers = {
            "Authorization": f"Bearer {self.settings.nvidia_api_key}",
            "Content-Type": "application/json"
        }
    
    async def _make_api_call_with_retry(
        self,
        client: httpx.AsyncClient,
        url: str,
        payload: Dict[str, Any],
        operation_name: str
    ) -> Dict[str, Any]:
        """
        Make API call with exponential backoff retry logic.
        
        Args:
            client: HTTP client instance
            url: API endpoint URL
            payload: Request payload
            operation_name: Name of operation for logging
            
        Returns:
            API response as dictionary
            
        Raises:
            httpx.HTTPError: If all retries fail
        """
        max_retries = self.settings.max_retries
        base_delay = 1  # seconds
        
        for attempt in range(max_retries):
            try:
                logger.info(f"{operation_name} - Attempt {attempt + 1}/{max_retries}")
                response = await client.post(url, json=payload, headers=self.headers)
                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPStatusError as e:
                # Don't retry on client errors (4xx)
                if 400 <= e.response.status_code < 500:
                    logger.error(f"{operation_name} - Client error: {e.response.status_code}")
                    raise
                
                # Retry on server errors (5xx)
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(
                        f"{operation_name} - Server error {e.response.status_code}. "
                        f"Retrying in {delay}s... (Attempt {attempt + 1}/{max_retries})"
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"{operation_name} - All retries exhausted")
                    raise
                    
            except httpx.TimeoutException:
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    logger.warning(
                        f"{operation_name} - Timeout. "
                        f"Retrying in {delay}s... (Attempt {attempt + 1}/{max_retries})"
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"{operation_name} - All retries exhausted after timeout")
                    raise

    async def identify_component(
        self,
        image_base64: str,
        user_goal: str
    ) -> str:
        """
        Stage 1: Visual Identification using Nemotron Nano 2 VL.

        CURRENTLY SIMULATED: Returns hardcoded Raspberry Pi 4 identification.

        Args:
            image_base64: Base64 encoded image string
            user_goal: User's stated goal

        Returns:
            String description of identified component

        Raises:
            ValueError: If response parsing fails
        """
        logger.info("Stage 1: Starting LIVE visual identification with Nemotron Nano 2 VL")

        # Validate and clean base64 encoding
        image_format = "jpeg"  # Default to jpeg
        try:
            # Strip data URL prefix if present (from frontend canvas.toDataURL)
            if image_base64.startswith('data:image'):
                # Extract format from data URL (e.g., "data:image/jpeg;base64,...")
                if 'jpeg' in image_base64.lower():
                    image_format = "jpeg"
                elif 'png' in image_base64.lower():
                    image_format = "png"
                image_base64 = image_base64.split(',')[1]
            # Test decode to validate format
            base64.b64decode(image_base64)
        except Exception as e:
            raise ValueError(f"Invalid base64 image data: {str(e)}")

        # Prepare the VLM request for NVIDIA API
        system_prompt = """You are a hardware identification assistant for TaskLens.
Analyze the image and identify the hardware component in ONE concise sentence.

Format: "[Component Type], [Power State]. [Key Observable Features]"
Example: "Raspberry Pi 4 Model B, Unpowered. GPIO header visible, 40-pin layout exposed."

Be precise and brief."""

        payload = {
            "model": "nvidia/nemotron-nano-2-vlm",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": f"data:image/{image_format};base64,{image_base64}"
                        },
                        {
                            "type": "text",
                            "text": f"Identify this hardware component. User goal: {user_goal}"
                        }
                    ]
                }
            ],
            "max_tokens": 200,
            "temperature": 0.2,
            "top_p": 0.7,
            "stream": False
        }

        async with httpx.AsyncClient(timeout=self.settings.api_timeout) as client:
            try:
                response = await client.post(
                    self.settings.nano2_vlm_url,
                    json=payload,
                    headers=self.headers
                )
                response.raise_for_status()
                result = response.json()

                # Extract component identification
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                logger.info(f"VLM identified: {content}")

                if not content:
                    raise ValueError("Empty response from VLM API")

                return content

            except httpx.HTTPError as e:
                logger.error(f"VLM API error: {str(e)}")
                raise

    async def generate_plan(
        self,
        component: str,
        component_state: str,
        user_goal: str
    ) -> Dict[str, Any]:
        """
        Stage 2: Chronological Planning using Nemotron Nano 3.

        Args:
            component: Identified hardware component
            component_state: Current state of component
            user_goal: User's stated goal

        Returns:
            Structured task plan as dictionary

        Raises:
            httpx.HTTPError: If API call fails
            ValueError: If response validation fails
        """
        logger.info("Stage 2: Generating chronological plan with Nemotron Nano 3")

        system_prompt = f"""You are a Specialized Hardware Architect with expertise in {component}.

Generate a safe, chronologically optimal plan to achieve the user's goal.

CRITICAL REQUIREMENTS:
1. Steps must be in strict chronological order
2. Include specific safety levels: "safe", "caution", or "warning"
3. Provide realistic time estimates for each step
4. Include at least one common error state with recovery steps
5. Focus on {component} in its current state: {component_state}

You must respond with valid JSON matching the exact schema provided."""

        user_prompt = f"""Hardware: {component}
Current State: {component_state}
User Goal: {user_goal}

Generate a complete, safe task plan."""

        payload = {
            "model": "nvidia/nemotron-nano-3",
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            "temperature": 0.3,
            "top_p": 0.95,
            "max_tokens": 2000,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "task_plan",
                    "schema": PLAN_SCHEMA,
                    "strict": True
                }
            }
        }

        async with httpx.AsyncClient(timeout=self.settings.api_timeout) as client:
            try:
                response = await client.post(
                    self.settings.nano3_llm_url,
                    json=payload,
                    headers=self.headers
                )
                response.raise_for_status()
                result = response.json()

                # Extract the structured plan
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "{}")
                logger.info(f"LLM Response received: {len(content)} characters")

                # Parse and validate against Pydantic schema
                import json
                plan_dict = json.loads(content)

                # Validate with Pydantic
                validated_plan = TaskPlan(**plan_dict)
                logger.info(f"Plan generated with {len(validated_plan.plan_steps)} steps")

                return validated_plan.model_dump()

            except httpx.HTTPError as e:
                logger.error(f"LLM API call failed: {str(e)}")
                raise
            except Exception as e:
                logger.error(f"Plan generation failed: {str(e)}")
                raise ValueError(f"Failed to generate valid plan: {str(e)}")

    async def generate_wiring_plan(
        self,
        context_description: str,
        user_goal: str
    ) -> List[Dict[str, Any]]:
        """
        Stage 2: Generate 5-step wiring plan with pin guidance using Nemotron Nano 3.

        Args:
            context_description: VLM output describing the hardware
            user_goal: User's stated goal

        Returns:
            List of wiring steps with safe/unsafe pins and coordinates

        Raises:
            httpx.HTTPError: If API call fails
            ValueError: If response validation fails
        """
        logger.info("Stage 2: Generating wiring plan with Nemotron Nano 3")

        system_prompt = f"""detailed thinking on. You are a specialized Hardware Architect with expertise in safe electronics assembly.

Based on the context: {context_description} and the user's goal: {user_goal}, generate a 5-step, chronologically optimal and safe wiring plan.

For each step, include:
1. A SAFE pin to use (correct choice)
2. An UNSAFE pin option (common mistake)
3. X and Y coordinates (0.0 to 1.0) for visual overlay on the component image
4. Detailed feedback explaining why the safe pin is correct
5. Safety-focused error text explaining why the unsafe pin is wrong

CRITICAL: The output MUST strictly conform to the provided JSON Schema."""

        user_prompt = f"""Context: {context_description}
User Goal: {user_goal}

Generate a complete 5-step wiring plan with safety guidance."""

        payload = {
            "model": "nvidia/llama-3.1-nemotron-70b-instruct",
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            "temperature": 0.3,
            "top_p": 0.95,
            "max_tokens": 2000,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "wiring_plan",
                    "schema": WIRING_PLAN_SCHEMA,
                    "strict": True
                }
            }
        }

        async with httpx.AsyncClient(timeout=self.settings.api_timeout) as client:
            try:
                # Use retry mechanism
                result = await self._make_api_call_with_retry(
                    client=client,
                    url=self.settings.nano3_llm_url,
                    payload=payload,
                    operation_name="Wiring Plan Generation"
                )

                # Extract the structured plan
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "[]")
                logger.info(f"LLM Response received: {len(content)} characters")

                # Parse JSON array
                import json
                wiring_steps = json.loads(content)

                # Validate each step with Pydantic
                validated_steps = [WiringStep(**step) for step in wiring_steps]
                logger.info(f"Wiring plan generated with {len(validated_steps)} steps")

                return [step.model_dump() for step in validated_steps]

            except httpx.HTTPError as e:
                logger.error(f"LLM API call failed: {str(e)}")
                raise
            except Exception as e:
                logger.error(f"Wiring plan generation failed: {str(e)}")
                raise ValueError(f"Failed to generate valid wiring plan: {str(e)}")

    async def orchestrate_full_pipeline(
        self,
        image_base64: str,
        user_goal: str
    ) -> List[Dict[str, Any]]:
        """
        Orchestrate the complete two-stage pipeline for wiring plan generation.

        Args:
            image_base64: Base64 encoded image
            user_goal: User's stated goal

        Returns:
            List of wiring steps (JSON array)

        Raises:
            Exception: If any stage fails
        """
        logger.info("Starting TaskLens wiring plan pipeline orchestration")

        # Stage 1: Visual Identification (SIMULATED)
        context_description = await self.identify_component(image_base64, user_goal)

        # Stage 2: Wiring Plan Generation
        wiring_plan = await self.generate_wiring_plan(context_description, user_goal)

        logger.info("Pipeline orchestration completed successfully")
        return wiring_plan
