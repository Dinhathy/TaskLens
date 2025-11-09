"""
Service layer for orchestrating OpenAI model calls.
"""
import base64
import logging
import asyncio
import json
from typing import Dict, Any, Tuple, List, Optional
import httpx
from core.schemas import PLAN_SCHEMA, WIRING_PLAN_SCHEMA, TaskPlan, WiringStep
from core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class OpenAIService:
    """Service for orchestrating OpenAI GPT-4 Vision and text models."""

    def __init__(self):
        self.settings = get_settings()
        self.headers = {
            "Authorization": f"Bearer {self.settings.openai_api_key}",
            "Content-Type": "application/json"
        }
        self.chat_url = f"{self.settings.openai_base_url}/chat/completions"
        self.serper_headers = {
            "X-API-KEY": self.settings.serper_api_key,
            "Content-Type": "application/json"
        }
    
    async def web_search_tool(self, query: str) -> str:
        """
        Executes a Google web search for technical diagrams, pinouts, or port definitions
        using the Serper API and returns the URL and snippet of the best result.
        
        Args:
            query: Search query string (e.g., "Raspberry Pi 4 GPIO pinout diagram")
            
        Returns:
            JSON string containing the search result with url and snippet, or error message
        """
        logger.info(f"Web search requested for: {query}")
        
        if not self.settings.serper_api_key:
            logger.warning("SERPER_API_KEY not configured")
            return json.dumps({
                "error": "Search functionality not available - API key not configured",
                "url": "",
                "snippet": ""
            })
        
        try:
            payload = {
                "q": query,
                "num": 3,  # Get top 3 results
                "gl": "us"  # Geographic location
            }
            
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(
                    self.settings.serper_base_url,
                    json=payload,
                    headers=self.serper_headers
                )
                response.raise_for_status()
                result = response.json()
                
                # Extract the best result (first organic result)
                organic_results = result.get("organic", [])
                if not organic_results:
                    logger.warning(f"No search results found for: {query}")
                    return json.dumps({
                        "error": "No results found",
                        "url": "",
                        "snippet": ""
                    })
                
                best_result = organic_results[0]
                search_result = {
                    "url": best_result.get("link", ""),
                    "title": best_result.get("title", ""),
                    "snippet": best_result.get("snippet", "")
                }
                
                logger.info(f"Search successful - Found: {search_result['title']}")
                return json.dumps(search_result)
                
        except httpx.HTTPError as e:
            logger.error(f"Serper API error: {str(e)}")
            return json.dumps({
                "error": f"Search API error: {str(e)}",
                "url": "",
                "snippet": ""
            })
        except Exception as e:
            logger.error(f"Web search failed: {str(e)}")
            return json.dumps({
                "error": f"Search failed: {str(e)}",
                "url": "",
                "snippet": ""
            })
    
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
        Stage 1: Visual Identification using OpenAI GPT-4 Vision.

        Args:
            image_base64: Base64 encoded image string
            user_goal: User's stated goal

        Returns:
            String description of identified component

        Raises:
            ValueError: If response parsing fails
        """
        logger.info("Stage 1: Starting visual identification with OpenAI GPT-4 Vision")

        # Sanitize user_goal to remove any newlines or problematic characters
        user_goal = user_goal.replace('\n', ' ').replace('\r', ' ').strip()

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

            # CRITICAL: Strip any remaining newlines/whitespace that may have been added by proxy
            image_base64 = image_base64.replace('\n', '').replace('\r', '').replace(' ', '').replace('\t', '')

            # Test decode to validate format
            base64.b64decode(image_base64)
        except Exception as e:
            raise ValueError(f"Invalid base64 image data: {str(e)}")

        # Prepare the VLM request for OpenAI API
        # Build comprehensive prompt for hardware/component identification
        vlm_prompt = "".join([
            "You are analyzing an image of hardware, tools, or equipment for a technical assistance application. ",
            "This is NOT a person - it is electronic components, machinery, appliances, or similar objects. ",
            f"The user wants to: {user_goal}. ",
            "Describe what hardware/components you see in the image. ",
            "Focus on: type of device/component, current state (powered/unpowered/assembled/disassembled), ",
            "and any visible technical features (ports, connectors, labels, etc.). ",
            "Format your response as: [Component Type], [Current State], [Key Technical Features]. ",
            "Examples: 'Raspberry Pi 4 board, unpowered, 40-pin GPIO header visible'; ",
            "'Arduino Uno microcontroller, USB port visible, no power LED'; ",
            "'Breadboard with LED and resistor, no power connected'; ",
            "'PVC pipe fitting, P-trap disconnected, threaded connections visible'. ",
            "Be technical and specific about the hardware you observe."
        ])

        payload = {
            "model": self.settings.vision_model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": vlm_prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/{image_format};base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 300
        }

        async with httpx.AsyncClient(timeout=self.settings.api_timeout) as client:
            try:
                # Debug logging
                logger.info(f"OpenAI Vision URL: {self.chat_url}")
                logger.info(f"Model: {self.settings.vision_model}")
                logger.info(f"Prompt length: {len(vlm_prompt)}")
                logger.info(f"Base64 length: {len(image_base64)}")
                logger.info(f"API key present: {bool(self.settings.openai_api_key)}")

                response = await client.post(
                    self.chat_url,
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
                logger.error(f"Error type: {type(e).__name__}")
                logger.error(f"Error details: {repr(e)}")
                if hasattr(e, 'request'):
                    logger.error(f"Request URL: {e.request.url if e.request else 'N/A'}")
                if hasattr(e, 'response'):
                    logger.error(f"Response status: {e.response.status_code if e.response else 'N/A'}")
                    try:
                        logger.error(f"Response body: {e.response.text if e.response else 'N/A'}")
                    except:
                        pass
                raise

    async def generate_plan(
        self,
        component: str,
        component_state: str,
        user_goal: str
    ) -> Dict[str, Any]:
        """
        Stage 2: Chronological Planning using OpenAI GPT-4o-mini.

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
        logger.info("Stage 2: Generating chronological plan with OpenAI GPT-4o-mini")

        # Sanitize inputs
        component = component.replace('\n', ' ').replace('\r', ' ').strip()
        component_state = component_state.replace('\n', ' ').replace('\r', ' ').strip()
        user_goal = user_goal.replace('\n', ' ').replace('\r', ' ').strip()

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
            "model": self.settings.text_model,
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
                # Use retry mechanism
                result = await self._make_api_call_with_retry(
                    client=client,
                    url=self.chat_url,
                    payload=payload,
                    operation_name="Task Plan Generation"
                )

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

    async def generate_wiring_plan_combined(
        self,
        image_base64: str,
        user_goal: str
    ) -> List[Dict[str, Any]]:
        """
        Combined single-call approach: Analyze image and generate wiring plan using GPT-4o
        with autonomous web search capability via function calling.
        
        This combines vision analysis and planning into ONE fast API call for minimal latency.

        Args:
            image_base64: Base64 encoded image string
            user_goal: User's stated goal

        Returns:
            List of wiring steps with logical pin names and diagram URLs

        Raises:
            httpx.HTTPError: If API call fails
            ValueError: If response validation fails
        """
        logger.info("Starting combined vision + planning with GPT-4o (single call)")

        # Sanitize user_goal
        user_goal = user_goal.replace('\n', ' ').replace('\r', ' ').strip()

        # Validate and prepare image
        image_format = "jpeg"
        try:
            if image_base64.startswith('data:image'):
                if 'jpeg' in image_base64.lower():
                    image_format = "jpeg"
                elif 'png' in image_base64.lower():
                    image_format = "png"
                image_base64 = image_base64.split(',')[1]
            
            image_base64 = image_base64.replace('\n', '').replace('\r', '').replace(' ', '').replace('\t', '')
            base64.b64decode(image_base64)
        except Exception as e:
            raise ValueError(f"Invalid base64 image data: {str(e)}")

        system_prompt = """You are the TaskLens Cognitive Foreman and highly patient tutor. You specialize in guiding complete beginners through complex, unconventional manual tasks across ALL domains: electronics, plumbing, automotive, home repair, carpentry, and appliance maintenance.

CORE PERSONA:
- Patient, encouraging, and EXTREMELY descriptive
- Simple language (8th-grade reading level)
- NO assumptions about prior knowledge
- Treat user as if this is their first time holding tools
- Explain the purpose ('the why') BEFORE giving instructions ('the how')

CRITICAL STEP BREAKDOWN REQUIREMENTS:
1. You MUST generate EXACTLY 6 distinct, sequential steps (not 5, not 7 - exactly 6)
2. Break down complex actions into separate steps:
   - If connecting two components: Step 1 = prepare first component, Step 2 = prepare second component, Step 3 = connect them
   - If assembly has multiple parts: Dedicate one step per component placement
   - If verification needed: Include as a separate step
3. Each step must focus on ONE physical action or component

FIELD POPULATION REQUIREMENTS:
For EVERY step, you MUST populate:

- target_label: Physical label on the hardware (e.g., "GPIO Pin 17", "M8 Bolt", "Hot Water Valve")
- value_required: Specific value/tool needed (e.g., "220 ohm resistor", "8mm wrench", "Clockwise 2 turns")
- target_pin: Correct connection point (e.g., "Pin 17", "Terminal Block A", "Inlet Port")  
- unsafe_option: Common dangerous mistake (e.g., "5V Pin", "M6 Bolt", "Cold Water Inlet")
- requires_photo_verification: ALWAYS true (user must photograph completion before next step)
- verification_criteria: What to show in photo (e.g., "LED inserted with long leg in hole 7", "Wire firmly connected to Pin 17")

FEEDBACK_TEXT STRUCTURE (CRITICAL):
Write 2-3 short paragraphs:
- Paragraph 1: WHY this step matters (purpose, what it accomplishes)
- Paragraph 2: HOW to do it (detailed physical movements)
- Paragraph 3 (optional): What success looks like

Example: "This resistor limits the electrical current flowing to your LED, protecting it from burning out. Without it, too much power would destroy the LED instantly. To install the resistor, hold it gently by its colored bands (don't touch the metal legs). Bend each wire leg into a small L-shape using your fingernail or pliers. Insert one leg into hole 7 and the other into hole 9 on your breadboard. Press down firmly but gently until the resistor body sits flat against the board. You should feel it click into place."

ERROR_TEXT REQUIREMENTS:
- Explain EXACTLY what goes wrong and why
- Use beginner-friendly analogies
- Be specific about physical consequences

Example: "Connecting directly to the 5V pin would be like plugging a nightlight into an industrial power outlet - way too much power. The LED would flash bright for a split second, make a small popping sound, and burn out permanently with a tiny puff of smoke. Always use the resistor."

WEB SEARCH REQUIREMENT:
- Use web_search_tool to find "Raspberry Pi GPIO Pinout Diagram" (or equivalent for the hardware)
- Include the URL in diagram_url field for the FIRST step ONLY
- Other steps can have empty string for diagram_url

DOMAIN-SPECIFIC LABELING:
- Electronics: "GPIO Pin 17", "GND Rail", "220 ohm resistor", "Positive LED leg" 
- Plumbing: "Hot Water Inlet", "3/4 inch coupling", "Shutoff valve"
- Automotive: "Battery Positive Terminal", "10mm socket", "Oil drain plug"

Output EXACTLY 6 steps in valid JSON format conforming to the schema."""

        user_prompt = f"""Analyze this hardware image and generate a patient, beginner-friendly task plan with EXACTLY 6 detailed steps for: {user_goal}

Break complex actions into separate steps. Use physical labels. Provide detailed WHY and HOW explanations for each step. Search for a pinout/technical diagram URL for step 1."""

        # Define the function/tool for OpenAI
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "web_search_tool",
                    "description": "Search Google for technical diagrams, pinout guides, or component documentation. Use this when the plan mentions specific pins, connectors, or technical terms that need visual reference.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query for technical documentation (e.g., 'Raspberry Pi 4 GPIO pinout diagram', 'Arduino Uno pin layout')"
                            }
                        },
                        "required": ["query"],
                        "additionalProperties": False
                    }
                }
            }
        ]

        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/{image_format};base64,{image_base64}"
                        }
                    }
                ]
            }
        ]

        async with httpx.AsyncClient(timeout=self.settings.api_timeout) as client:
            try:
                # Initial call with tools enabled (no structured output yet - can't mix both)
                # Using GPT-4o (vision_model) for combined vision + planning
                max_iterations = 10  # Prevent infinite loops
                iteration = 0
                
                while iteration < max_iterations:
                    iteration += 1
                    logger.info(f"API call iteration {iteration}")
                    
                    payload = {
                        "model": self.settings.vision_model,  # Use GPT-4o for vision + reasoning
                        "messages": messages,
                        "temperature": 0.3,
                        "max_tokens": 2000,
                        "tools": tools,
                        "tool_choice": "auto"  # Let model decide when to use tools
                    }
                    
                    result = await self._make_api_call_with_retry(
                        client=client,
                        url=self.chat_url,
                        payload=payload,
                        operation_name=f"Wiring Plan Generation (Iteration {iteration})"
                    )
                    
                    assistant_message = result.get("choices", [{}])[0].get("message", {})
                    messages.append(assistant_message)
                    
                    # Check if the model wants to call a function
                    tool_calls = assistant_message.get("tool_calls", [])
                    
                    if not tool_calls:
                        # No more tool calls - model has finished, now request structured format
                        logger.info("Model finished using tools, requesting structured JSON output")
                        
                        # Add instruction to format the response
                        messages.append({
                            "role": "user",
                            "content": "Now format your complete plan as JSON conforming to the schema."
                        })
                        
                        # Final call with structured output using GPT-4o
                        final_payload = {
                            "model": self.settings.vision_model,  # Continue using GPT-4o
                            "messages": messages,
                            "temperature": 0.3,
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
                        
                        final_result = await self._make_api_call_with_retry(
                            client=client,
                            url=self.chat_url,
                            payload=final_payload,
                            operation_name="Wiring Plan Final Formatting"
                        )
                        
                        content = final_result.get("choices", [{}])[0].get("message", {}).get("content", "{}")
                        logger.info(f"Final LLM Response received: {len(content)} characters")
                        
                        # Parse JSON object and extract steps array
                        response_obj = json.loads(content)
                        wiring_steps = response_obj.get("steps", [])
                        
                        # Validate each step with Pydantic
                        validated_steps = [WiringStep(**step) for step in wiring_steps]
                        logger.info(f"Wiring plan generated with {len(validated_steps)} steps")
                        
                        return [step.model_dump() for step in validated_steps]
                    
                    # Execute the function calls
                    for tool_call in tool_calls:
                        function_name = tool_call.get("function", {}).get("name")
                        function_args = json.loads(tool_call.get("function", {}).get("arguments", "{}"))
                        tool_call_id = tool_call.get("id")
                        
                        logger.info(f"Model requested function: {function_name} with args: {function_args}")
                        
                        if function_name == "web_search_tool":
                            # Execute the search
                            search_result = await self.web_search_tool(function_args.get("query", ""))
                            
                            # Add function result to messages
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call_id,
                                "content": search_result
                            })
                        else:
                            logger.warning(f"Unknown function called: {function_name}")
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call_id,
                                "content": json.dumps({"error": "Unknown function"})
                            })
                
                # If we hit max iterations, return error
                raise ValueError("Maximum iterations reached in function calling loop")

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
        Orchestrate the complete pipeline - now using SINGLE combined call for speed.

        Args:
            image_base64: Base64 encoded image
            user_goal: User's stated goal

        Returns:
            List of wiring steps (JSON array)

        Raises:
            Exception: If any stage fails
        """
        logger.info("Starting TaskLens COMBINED vision + planning pipeline (single GPT-4o call)")

        # Combined approach: Vision analysis + planning in ONE call
        wiring_plan = await self.generate_wiring_plan_combined(image_base64, user_goal)

        logger.info("Pipeline orchestration completed successfully")
        return wiring_plan
