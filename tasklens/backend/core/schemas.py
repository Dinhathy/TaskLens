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
    """Individual wiring step with pin guidance."""
    step_id: int = Field(..., description="Sequential step number")
    component: str = Field(default="", description="Component being wired")
    safe_pin: str = Field(..., description="Correct pin name, e.g., GPIO 17")
    unsafe_pin_option: str = Field(..., description="Common mistake pin, e.g., 5V")
    x_coord: float = Field(..., description="Normalized X-coordinate (0.0 to 1.0) for visual overlay", ge=0.0, le=1.0)
    y_coord: float = Field(..., description="Normalized Y-coordinate (0.0 to 1.0) for visual overlay", ge=0.0, le=1.0)
    feedback_text: str = Field(..., description="Detailed instruction for the correct choice")
    error_text: str = Field(..., description="Expert reasoning on why the unsafe pin is wrong")


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
                    "safe_pin": {"type": "string", "description": "Correct pin name, e.g., GPIO 17"},
                    "unsafe_pin_option": {"type": "string", "description": "Common mistake pin, e.g., 5V"},
                    "x_coord": {"type": "number", "description": "Normalized X-coordinate (0.0 to 1.0) for visual overlay."},
                    "y_coord": {"type": "number", "description": "Normalized Y-coordinate (0.0 to 1.0) for visual overlay."},
                    "feedback_text": {"type": "string", "description": "Detailed instruction for the correct choice."},
                    "error_text": {"type": "string", "description": "Expert reasoning on why the unsafe pin is wrong."}
                },
                "required": ["step_id", "safe_pin", "unsafe_pin_option", "x_coord", "y_coord", "feedback_text", "error_text"],
                "additionalProperties": False
            },
            "minItems": 5,
            "maxItems": 5
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
