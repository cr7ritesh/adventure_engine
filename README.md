
# Puch Adventure Engine
## *Rewrite Your Favorite Stories*

---

> **Ever wished you could change the ending of your favorite movie?**  
> Or explore what would happen if a key character made a different choice?  
> **Puch Adventure Engine** is a stateful, AI-powered storytelling game that puts you in the director's chair.

Built as a **Model Context Protocol (MCP) server** for the Puch AI client, this engine lets you step into any fictional universe, become any character, and explore infinite "what if" scenarios. Lead the Starks to victory in Game of Thrones, see what happens if Walter White refuses to cook in Breaking Bad, or create entirely new adventures in worlds of your own making. Powered by Google's Gemini API, every choice you make creates a unique, branching narrative.

---

## 🚀 Key Features

- **Infinite Story Possibilities**  
	Powered by the Google Gemini API, the engine acts as a dynamic Dungeon Master, creating unique narratives, characters, and outcomes for every choice.

- **Explore "What Ifs"**  
	Dive into your favorite TV shows, movies, and books. Change character fates and see how the story unfolds based on your decisions.

- **True Player Agency**  
	Don't like the options provided? Type your own custom action to guide the story in any direction.

- **Stateful & Personal Sessions**  
	Persistent, unique game state for every user. Leave and return to your adventure anytime.

- **Visually Rich Experience**  
	Each narrative turn is accompanied by a scene image. (Demo uses placeholder images; engine supports AI-generated images.)

- **Seamless Puch AI Integration**  
	Built to work natively within the Puch AI chat client.

---

## 🛠️ Getting Started: 5-Minute Setup Guide

### Prerequisites

- Python **3.9+**
- [`uv`](https://github.com/astral-sh/uv) (fast Python package installer)
- Active [ngrok](https://ngrok.com/) account

---

### Step 1: Clone the Repository

```bash
git clone <your-repo-url>
cd puch-adventure-engine
```

---

### Step 2: Set Up the Environment

```bash
# Create the virtual environment
uv venv

# Activate the environment (macOS/Linux)
source .venv/bin/activate

# Install all required packages
uv pip install -r requirements.txt
```

---

### Step 3: Configure Your Secret Keys

Create a `.env` file in the root directory. You can copy `.env.example` if provided.

```env
# This is a password YOU invent. It will be used to connect to your server.
AUTH_TOKEN="a-secret-password-of-your-choice"

# Your phone number in the format required by Puch AI for validation.
MY_NUMBER="919876543210"

# Your free API key from Google AI Studio for the Gemini model.
GEMINI_API_KEY="your_google_gemini_api_key_here"
```

---

### Step 4: Run the Server

```bash
python adventure_engine.py
```
> You should see: `🚀 Starting MCP server...`

---

### Step 5: Expose Your Server with ngrok

Open a new terminal window:

```bash
ngrok http 8086
```
Copy the HTTPS "Forwarding" URL provided by ngrok (e.g., `https://<random-string>.ngrok-free.app`).

---

## 🎮 How to Play

- **Connect Your Server:**  
	Use the `/mcp connect` command with your ngrok URL and secret `AUTH_TOKEN`.  
	*Do not add `/mcp` to the end of the URL.*

	```text
	/mcp connect https://<your-ngrok-url>.ngrok-free.app your-secret-token
	```

- **Start Your Adventure:**  
	The most reliable way to begin is by explicitly calling the `start_adventure` tool.

	```text
	@PuchAdventureEngine start_adventure
	```

- **Make Your Choices:**  
	The AI Dungeon Master will present a scene, image, and choices. Type a suggested choice or your own custom action.

- **Manage Your Game:**
	- `@PuchAdventureEngine show_status` — Check your character's inventory.
	- `@PuchAdventureEngine reset_adventure` — End your current game and start fresh.

---

## 🧑‍💻 Technology Stack

- **Backend:** Python
- **MCP Framework:** FastMCP
- **Text Generation:** Google Gemini API (`gemini-1.5-flash`)
- **Image Generation:** Placeholder Service ([via.placeholder.com](https://via.placeholder.com))
- **Server:** Uvicorn

---

> **Ready to rewrite your favorite stories? Start your adventure now!**