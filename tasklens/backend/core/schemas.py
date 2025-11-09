"""
Pydantic schemas for TaskLens API data validation and structured output.
"""
from pydantic import BaseModel, Field
from typing import List, Literal


class TaskRequest(BaseModel):
    """Input schema for task planning request from frontend."""
    image_data: str = Field(
        ...,
        description="Base64 encoded image string of the hardware component"
    )
    user_goal: str = Field(
        ...,
        description="User's goal description (e.g., 'Blink an LED')",
        min_length=1,
        max_length=500
    )


class Step(BaseModel):
    """Individual step in the hardware task plan."""
    step_number: int = Field(..., description="Sequential step number")
    action: str = Field(..., description="Clear, imperative action to perform")
    component: str = Field(..., description="Specific hardware component involved")
    safety_level: Literal["safe", "caution", "warning"] = Field(
        ...,
        description="Safety classification for this step"
    )
    estimated_time_seconds: int = Field(
        ...,
        description="Estimated time to complete this step in seconds",
        ge=1
    )


class ErrorState(BaseModel):
    """Common error condition and recovery steps."""
    error_name: str = Field(..., description="Name of the error condition")
    symptoms: List[str] = Field(
        ...,
        description="Observable symptoms of this error",
        min_length=1
    )
    recovery_steps: List[str] = Field(
        ...,
        description="Steps to recover from this error",
        min_length=1
    )


class TaskPlan(BaseModel):
    """Complete structured task plan output."""
    identified_component: str = Field(
        ...,
        description="Hardware component identified from image"
    )
    component_state: str = Field(
        ...,
        description="Current state of the component (e.g., 'Unpowered')"
    )
    goal: str = Field(..., description="User's stated goal")
    plan_steps: List[Step] = Field(
        ...,
        description="Chronologically ordered steps to achieve the goal",
        min_length=1
    )
    common_errors: List[ErrorState] = Field(
        ...,
        description="Common error states and recovery procedures",
        min_length=1,
        max_length=3
    )
    total_estimated_time_seconds: int = Field(
        ...,
        description="Total estimated time for all steps",
        ge=1
    )


class WiringStep(BaseModel):
    """Universal task step with physical labeling for any manual task."""
    step_id: int = Field(..., description="Sequential step number (1-6)")
    component: str = Field(..., description="Component or part being worked on")
    target_label: str = Field(..., description="Physical label of target (e.g., 'GPIO Pin 17', 'Bolt-M8', 'Water Inlet Valve')")
    value_required: str = Field(..., description="Value/setting needed (e.g., '220 ohms', '8mm wrench', 'Clockwise 2 turns', 'Off')")
    target_pin: str = Field(..., description="Correct connection/attachment point (e.g., 'Pin 17', 'Terminal Block 1', 'Hot Water Inlet')")
    unsafe_option: str = Field(..., description="Common mistake to avoid (e.g., '5V Pin', 'M6 Bolt', 'Cold Water Inlet')")
    feedback_text: str = Field(..., description="Patient, detailed explanation: WHY this action matters, then HOW to do it (8th-grade level)")
    error_text: str = Field(..., description="Clear warning explaining why the unsafe option is dangerous/wrong")
    diagram_url: str = Field(default="", description="URL to relevant diagram or guide (required for first step)")
    requires_photo_verification: bool = Field(default=True, description="Whether this step requires photo verification before proceeding")
    verification_criteria: str = Field(..., description="What the user should show in verification photo (e.g., 'LED inserted into breadboard', 'Wire connected to Pin 17')")


# JSON Schema for pin-focused wiring plan (NEW SCHEMA)
# OpenAI requires root to be an object, so we wrap the array
WIRING_PLAN_SCHEMA = {
    "type": "object",
    "properties": {
        "steps": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "step_id": {"type": "integer"},
                    "component": {"type": "string"},
                    "target_label": {"type": "string", "description": "Physical label of target (e.g., 'GPIO Pin 17', 'Bolt-M8', 'Water Inlet Valve')"},
                    "value_required": {"type": "string", "description": "Value/setting needed (e.g., '220 ohms', '8mm wrench', 'Clockwise 2 turns')"},
                    "target_pin": {"type": "string", "description": "Correct connection/attachment point"},
                    "unsafe_option": {"type": "string", "description": "Common mistake to avoid"},
                    "feedback_text": {"type": "string", "description": "Patient explanation of WHY and HOW (beginner-friendly)"},
                    "error_text": {"type": "string", "description": "Clear warning about the unsafe option"},
                    "diagram_url": {"type": "string", "description": "URL to relevant diagram. REQUIRED for first step."},
                    "requires_photo_verification": {"type": "boolean", "description": "Whether user must submit photo before next step"},
                    "verification_criteria": {"type": "string", "description": "What to show in verification photo"}
                },
                "required": ["step_id", "component", "target_label", "value_required", "target_pin", "unsafe_option", "feedback_text", "error_text", "diagram_url", "requires_photo_verification", "verification_criteria"],
                "additionalProperties": False
            },
            "minItems": 6,
            "maxItems": 6
        }
    },
    "required": ["steps"],
    "additionalProperties": False
}


# JSON Schema for guided generation with Nemotron Nano 3 (ORIGINAL SCHEMA)
PLAN_SCHEMA = {
    "type": "object",
    "properties": {
        "identified_component": {
            "type": "string",
            "description": "Hardware component identified from image analysis"
        },
        "component_state": {
            "type": "string",
            "description": "Current state of the component"
        },
        "goal": {
            "type": "string",
            "description": "User's stated goal"
        },
        "plan_steps": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "step_number": {"type": "integer", "minimum": 1},
                    "action": {"type": "string"},
                    "component": {"type": "string"},
                    "safety_level": {
                        "type": "string",
                        "enum": ["safe", "caution", "warning"]
                    },
                    "estimated_time_seconds": {"type": "integer", "minimum": 1}
                },
                "required": ["step_number", "action", "component", "safety_level", "estimated_time_seconds"],
                "additionalProperties": False
            },
            "minItems": 1
        },
        "common_errors": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "error_name": {"type": "string"},
                    "symptoms": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 1
                    },
                    "recovery_steps": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 1
                    }
                },
                "required": ["error_name", "symptoms", "recovery_steps"],
                "additionalProperties": False
            },
            "minItems": 1,
            "maxItems": 3
        },
        "total_estimated_time_seconds": {"type": "integer", "minimum": 1}
    },
    "required": [
        "identified_component",
        "component_state",
        "goal",
        "plan_steps",
        "common_errors",
        "total_estimated_time_seconds"
    ],
    "additionalProperties": False
}
