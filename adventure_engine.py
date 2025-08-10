# ==============================================================================
# Puch Adventure Engine - Final Hackathon Code
# ==============================================================================
# This MCP server creates a stateful, AI-powered interactive text adventure game
# designed to run within the Puch AI chat client.
#
# Key Technologies:
# - MCP Server: FastMCP
# - Text Generation: Google Gemini API
# - Image Generation: Placeholder service for demo reliability
# - Environment Management: python-dotenv
# ==============================================================================

# --- Core Python Libraries ---
import os
import json
import urllib.parse
from typing import Annotated

# --- Third-Party Libraries ---
from dotenv import load_dotenv
from fastmcp import FastMCP
from pydantic import Field
import google.generativeai as genai

# ==============================================================================
# SECTION 1: INITIAL SETUP & CONFIGURATION
# ==============================================================================

# 1.1: Load Environment Variables
# This must be the first step to ensure all secret keys and configurations
# are available to the script as it starts up.
load_dotenv()

# 1.2: Pre-flight Checks and Loading Variables into Constants
# This robust pattern, which you discovered, loads all necessary variables from
# the environment at startup. Using.strip() prevents errors from invisible
# whitespace in the.env file. The `assert` statements will cause the server
# to crash immediately if a key is missing, which is good for debugging.
TOKEN = os.environ.get("AUTH_TOKEN", "").strip()
MY_NUMBER = os.environ.get("MY_NUMBER", "").strip()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()

assert TOKEN, "CRITICAL ERROR: Please set AUTH_TOKEN in your.env file"
assert MY_NUMBER, "CRITICAL ERROR: Please set MY_NUMBER in your.env file"
assert GEMINI_API_KEY, "CRITICAL ERROR: Please set GEMINI_API_KEY in your.env file"

print("✅ All environment variables loaded successfully at startup.")

# 1.3: Configure AI Clients and Server Instance
# The Gemini library requires explicit configuration. This is the "main power switch".
genai.configure(api_key=GEMINI_API_KEY)

# This dictionary will act as our in-memory database to store game sessions.
# The key will be the user's unique `puch_user_id`.
ADVENTURE_SESSIONS = {}

# Create and configure the MCP server instance. Based on our logs, we know
# the Puch AI client sends requests to the root path ("/").
mcp = FastMCP(
    "PuchAdventureEngine",
    host="0.0.0.0",
    port=8086,
    streamable_http_path="/"
)


# ==============================================================================
# SECTION 2: HELPER FUNCTIONS FOR AI LOGIC
# ==============================================================================
# These functions handle the calls to external AI services. Keeping them
# separate from the main tool logic makes the code cleaner.

async def get_narrative_update(story_log: list, user_choice: str) -> dict:
    """Calls the Gemini API to get the next part of the story."""
    model = genai.GenerativeModel('gemini-1.5-flash')

    # This detailed prompt acts as our "Dungeon Master," instructing the AI
    # on its role and forcing it to return a structured JSON response.
    system_prompt = f"""
    You are an expert Dungeon Master for a text-based adventure game.
    Your role is to create a compelling, engaging, and coherent narrative.

    Here is the story so far:
    {story_log}

    The player's latest action is: "{user_choice}"

    Based on this, you must:
    1.  Generate the next part of the story as a single, descriptive paragraph.
    2.  Provide a list of 3 distinct, actionable choices for the player to make next.
    3.  Provide a short, descriptive prompt (5-10 words) for an image generator.
    4.  Update the player's inventory if they acquired or lost an item.
    5.  Return the response ONLY in a valid JSON format with the following keys:
        "narrative": "The next part of the story.",
        "choices": ["Choice 1", "Choice 2", "Choice 3"],
        "image_prompt": "A prompt for an image generator.",
        "new_inventory": ["item1", "item2",...]
    """

    response = await model.generate_content_async(system_prompt)

    # Clean up the response to remove markdown formatting that Gemini sometimes adds.
    cleaned_json = response.text.replace("```json", "").replace("```", "").strip()
    return json.loads(cleaned_json)


async def get_scene_image(prompt: str) -> str:
    """
    Creates a placeholder image URL for the scene.
    This is a robust hackathon strategy to ensure the demo works smoothly
    and a visible image URL is always present in the response, as some chat
    clients cannot display base64 data URLs.
    """
    print(f"🎨 Creating placeholder image for prompt: '{prompt}'")

    # We use a placeholder service that is fast and 100% reliable for demos.
    # It creates a gray box with the prompt text written on it.
    # We must URL-encode the prompt text to handle spaces and special characters.
    formatted_prompt = urllib.parse.quote_plus(prompt)
    image_placeholder_url = f"https://via.placeholder.com/1024x1024.png?text={formatted_prompt}"

    print("✅ Placeholder image URL created.")
    return image_placeholder_url


# ==============================================================================
# SECTION 3: MCP TOOL DEFINITIONS
# ==============================================================================
# These are the functions that the Puch AI client can call.

# --- Tool: validate (required by Puch) ---
@mcp.tool()
async def validate() -> str:
    return MY_NUMBER


@mcp.tool(
    description="Starts a new adventure for the user or resumes an existing one."
)
async def start_adventure(
        puch_user_id: Annotated[str, Field(description="...")]
) -> str:
    """Initializes a new game session for a user."""
    if puch_user_id in ADVENTURE_SESSIONS:
        last_log = ADVENTURE_SESSIONS[puch_user_id]["story_log"][-1]
        return f"You are already in an adventure! Your last update was: {last_log}"

    initial_prompt = "Start a new fantasy adventure for me in a mysterious, ancient forest."
    narrative_data = await get_narrative_update([], initial_prompt)
    image_url = await get_scene_image(narrative_data["image_prompt"])

    ADVENTURE_SESSIONS[puch_user_id] = {
        "story_log": [narrative_data["narrative"]],
        "inventory": narrative_data["new_inventory"],
    }

    response_str = (
        f"A new adventure begins!\n\n"
        f"{narrative_data['narrative']}\n\n"
        f"Image: {image_url}\n\n"
        f"What do you do?\n"
        f"1. {narrative_data['choices']}\n"
        f"2. {narrative_data['choices'][1]}\n"
        f"3. {narrative_data['choices'][2]}\n"
        f"4. Or, type your own action..."
    )
    return response_str


@mcp.tool(
    description="Makes a choice in the adventure and progresses the story."
)
async def make_choice(
        puch_user_id: Annotated[str, Field(description="...")],
        choice: Annotated[str, Field(description="...")]
) -> str:
    """The main game loop."""
    if puch_user_id not in ADVENTURE_SESSIONS:
        return "You haven't started an adventure yet! Use the 'start_adventure' tool first."

    current_session = ADVENTURE_SESSIONS[puch_user_id]
    narrative_data = await get_narrative_update(current_session["story_log"], choice)
    image_url = await get_scene_image(narrative_data["image_prompt"])

    current_session["story_log"].append(f"Player chose: {choice}")
    current_session["story_log"].append(narrative_data["narrative"])
    current_session["inventory"] = narrative_data["new_inventory"]

    response_str = (
        f"{narrative_data['narrative']}\n\n"
        f"Image: {image_url}\n\n"
        f"What do you do?\n"
        f"1. {narrative_data['choices']}\n"
        f"2. {narrative_data['choices'][1]}\n"
        f"3. {narrative_data['choices'][2]}\n"
        f"4. Or, type your own action..."
    )
    return response_str


@mcp.tool(
    description="Shows the user's current inventory and status."
)
async def show_status(
        puch_user_id: Annotated[str, Field(description="...")]
) -> str:
    """A utility tool to let the user check their status."""
    if puch_user_id not in ADVENTURE_SESSIONS:
        return "You haven't started an adventure yet! Use the 'start_adventure' tool first."

    inventory = ADVENTURE_SESSIONS[puch_user_id]["inventory"]
    if not inventory:
        return "Your inventory is empty."
    else:
        return f"Your inventory contains: {', '.join(inventory)}"


@mcp.tool(
    description="Resets the user's current adventure, deleting all progress."
)
async def reset_adventure(
        puch_user_id: Annotated[str, Field(description="...")]
) -> str:
    """Deletes the current game session for a user, allowing them to start over."""
    if puch_user_id in ADVENTURE_SESSIONS:
        del ADVENTURE_SESSIONS[puch_user_id]
        return "Your adventure has been reset. You can now start a new one by using the 'start_adventure' tool."
    else:
        return "You do not have an active adventure to reset."


# ==============================================================================
# SECTION 4: RUN THE SERVER
# ==============================================================================
# This block runs only when the script is executed directly. It's the most
# direct and reliable way to start our server.

if __name__ == "__main__":
    print("🚀 Starting MCP server...")
    mcp.run(transport="streamable-http")

