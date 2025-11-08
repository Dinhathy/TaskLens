"""
Sample request script to test the TaskLens API.
Demonstrates how to send a request with a base64-encoded image.
"""
import requests
import base64
import json
from pathlib import Path


def encode_image_to_base64(image_path: str) -> str:
    """Convert an image file to base64 string."""
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded


def send_plan_request(image_base64: str, user_goal: str, api_url: str = "http://localhost:8000"):
    """Send a plan generation request to the TaskLens API."""
    endpoint = f"{api_url}/api/v1/plan/generate"

    payload = {
        "image_data": image_base64,
        "user_goal": user_goal
    }

    print(f"Sending request to {endpoint}")
    print(f"Goal: {user_goal}")
    print(f"Image size: {len(image_base64)} characters\n")

    try:
        response = requests.post(
            endpoint,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )

        response.raise_for_status()
        plan = response.json()

        # Pretty print the response
        print("✓ Success! Generated Plan:")
        print("=" * 80)
        print(f"Component: {plan['identified_component']}")
        print(f"State: {plan['component_state']}")
        print(f"Goal: {plan['goal']}")
        print(f"Total Steps: {len(plan['plan_steps'])}")
        print(f"Estimated Time: {plan['total_estimated_time_seconds']} seconds")
        print("\nSteps:")
        for step in plan['plan_steps']:
            print(f"  {step['step_number']}. {step['action']}")
            print(f"     Component: {step['component']}")
            print(f"     Safety: {step['safety_level']} | Time: {step['estimated_time_seconds']}s")

        print("\nCommon Errors:")
        for error in plan['common_errors']:
            print(f"  • {error['error_name']}")
            print(f"    Symptoms: {', '.join(error['symptoms'])}")

        print("\n" + "=" * 80)

        return plan

    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the server.")
        print("   Make sure the server is running: uvicorn main:app --reload")
        return None

    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e.response.status_code}")
        print(f"   {e.response.json().get('detail', 'Unknown error')}")
        return None

    except requests.exceptions.Timeout:
        print("❌ Error: Request timed out")
        return None

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


def test_with_sample_image():
    """Test with a sample image if available."""
    # Check for common image files
    sample_images = [
        "raspberry_pi.jpg",
        "arduino.jpg",
        "hardware.jpg",
        "test.jpg",
        "sample.png"
    ]

    image_path = None
    for img in sample_images:
        if Path(img).exists():
            image_path = img
            break

    if image_path:
        print(f"Found sample image: {image_path}")
        image_base64 = encode_image_to_base64(image_path)
        send_plan_request(image_base64, "Blink an LED")
    else:
        print("No sample image found.")
        print("Place an image file in the current directory and update this script,")
        print("or use the example below with your own base64 image data.")


def test_with_dummy_data():
    """Test with minimal dummy data (will likely fail at NVIDIA API but tests the endpoint)."""
    print("Testing with dummy base64 data...")
    # This is a tiny 1x1 transparent PNG
    dummy_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

    send_plan_request(dummy_base64, "Test goal: Blink an LED")


def check_health():
    """Check if the API is healthy."""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        response.raise_for_status()
        health = response.json()

        print("API Health Check:")
        print(f"  Status: {health['status']}")
        print(f"  API Key Configured: {health['api_key_configured']}")
        print(f"  VLM URL: {health['nano2_vlm_url']}")
        print(f"  LLM URL: {health['nano3_llm_url']}")
        print()
        return True
    except Exception as e:
        print(f"❌ Health check failed: {str(e)}")
        print("   Make sure the server is running!")
        return False


def main():
    """Main test flow."""
    print("TaskLens API Test Script")
    print("=" * 80)

    # First check if server is running
    if not check_health():
        return

    # Try to test with a real image, otherwise use dummy data
    print("\nAttempting to test with sample image...")
    test_with_sample_image()

    # Uncomment to test with dummy data:
    # print("\nTesting with dummy data (will test endpoint but may fail at AI processing)...")
    # test_with_dummy_data()


if __name__ == "__main__":
    main()
