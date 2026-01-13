# AutoStream Conversational AI Agent

A sophisticated Conversational AI Agent built for AutoStream, a SaaS video editing platform. This agent demonstrates real-world GenAI capabilities including intent detection, RAG-powered knowledge retrieval, and intelligent lead capture.

## Features

- **Intent Identification**: Classifies user messages into greetings, product inquiries, or high-intent leads
- **RAG-Powered Knowledge Retrieval**: Answers questions using a local knowledge base with pricing, features, and policies
- **Intelligent Lead Capture**: Collects user information (name, email, platform) and triggers lead capture only when all data is collected
- **State Management**: Maintains conversation context across multiple turns using LangGraph
- **Tool Execution**: Properly validates and executes lead capture with mock API function

## Project Structure

```
inflx/
├── agent.py              # Main LangGraph agent with state management
├── rag_pipeline.py       # RAG pipeline for knowledge retrieval
├── intent_detector.py    # Intent classification system
├── lead_capture.py       # Lead capture tool and validation
├── main.py               # Entry point for interactive chat
├── knowledge_base.json   # Local knowledge base (pricing, policies)
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

## Prerequisites

- Python 3.9 or higher
- OpenAI API key (for GPT-4o-mini or compatible model)

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd inflx
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your OpenAI API key:
```bash
# On Windows (PowerShell)
$env:OPENAI_API_KEY="your-api-key-here"

# On Linux/Mac
export OPENAI_API_KEY="your-api-key-here"
```

Alternatively, create a `.env` file:
```
OPENAI_API_KEY=your-api-key-here
```

## How to Run

### Interactive Chat Mode

Run the main script to start an interactive conversation:

```bash
python main.py
```

### Example Conversation Flow

1. **Greeting & Inquiry**:
   ```
   User: Hi, tell me about your pricing.
   Agent: [Retrieves pricing info from knowledge base and responds]
   ```

2. **High-Intent Detection**:
   ```
   User: That sounds good, I want to try the Pro plan for my YouTube channel.
   Agent: [Detects high intent, starts collecting information]
   ```

3. **Lead Collection**:
   ```
   Agent: Great! I'd love to help you get started. To proceed, I'll need:
   1. What's your name?
   2. What's your email address?
   3. Which platform do you create content on?
   
   User: My name is John Doe, email is john@example.com, and I create on YouTube.
   Agent: [Validates and captures lead using mock_lead_capture()]
   ```

## Architecture Explanation

### Why LangGraph?

I chose **LangGraph** over AutoGen for this project because:

1. **State Management**: LangGraph provides built-in state management through TypedDict, making it easy to maintain conversation context, intent history, and collected lead information across multiple turns. The state is explicitly defined and type-safe.

2. **Workflow Control**: LangGraph's graph-based architecture allows for clear, visualizable workflows. The conditional routing based on intent detection creates a natural flow: message → intent detection → routing → specialized handlers → tool execution.

3. **Simplicity**: For this use case, LangGraph's simpler API compared to AutoGen's multi-agent framework is more appropriate. We have a single agent with clear decision points, not multiple agents coordinating.

4. **Integration**: LangGraph integrates seamlessly with LangChain's RAG pipeline and tool system, making it straightforward to combine knowledge retrieval with conversational flow.

### State Management

State is managed through LangGraph's `AgentState` TypedDict, which includes:

- **messages**: Conversation history (maintained using `add_messages` reducer for automatic merging)
- **intent**: Current detected intent (greeting, product_inquiry, high_intent_lead)
- **lead_info**: Dictionary storing collected lead information (name, email, platform)
- **conversation_turn**: Counter tracking conversation turns

The state persists across graph invocations, allowing the agent to:
- Remember previous conversation context (last 6 messages)
- Track partially collected lead information
- Maintain intent history for better routing decisions

The graph workflow ensures state is properly passed between nodes, and the `add_messages` reducer automatically handles message list updates without manual state merging.

### Component Breakdown

1. **RAG Pipeline** (`rag_pipeline.py`): Loads knowledge base from JSON, creates embeddings using OpenAI, and uses FAISS for similarity search. Retrieves relevant context for user queries.

2. **Intent Detector** (`intent_detector.py`): Uses LLM-based classification to detect user intent. Considers conversation history for context-aware classification.

3. **Lead Capture** (`lead_capture.py`): Validates email format, extracts information from user messages using regex patterns, and provides the `mock_lead_capture()` function.

4. **Agent** (`agent.py`): Main orchestrator using LangGraph. Routes messages through intent detection, handles different intents with specialized nodes, and manages lead collection workflow.

## WhatsApp Integration via Webhooks

To integrate this agent with WhatsApp, you would need to:

### 1. **WhatsApp Business API Setup**
   - Register for WhatsApp Business API (via Meta or a provider like Twilio)
   - Obtain API credentials and webhook verification token

### 2. **Webhook Server**
   Create a Flask/FastAPI server that:
   - **Receives webhooks** from WhatsApp when users send messages
   - **Verifies webhook** during initial setup (WhatsApp sends a challenge)
   - **Processes incoming messages** by calling the agent
   - **Sends responses** back via WhatsApp API

### 3. **Implementation Example** (Flask):

```python
from flask import Flask, request, jsonify
from agent import ConversationalAgent
import os

app = Flask(__name__)
agent = ConversationalAgent(api_key=os.getenv("OPENAI_API_KEY"))

# Store conversation states per user (using phone number as key)
user_states = {}

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    """Verify webhook during setup."""
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if mode == 'subscribe' and token == os.getenv('WHATSAPP_VERIFY_TOKEN'):
        return challenge, 200
    return 'Forbidden', 403

@app.route('/webhook', methods=['POST'])
def handle_message():
    """Handle incoming WhatsApp messages."""
    data = request.json
    entry = data.get('entry', [])[0]
    changes = entry.get('changes', [])[0]
    value = changes.get('value', {})
    
    if 'messages' in value:
        message = value['messages'][0]
        phone_number = message['from']
        user_message = message['text']['body']
        
        # Get or create state for this user
        state = user_states.get(phone_number)
        
        # Process message with agent
        response, new_state = agent.chat(user_message, state)
        user_states[phone_number] = new_state
        
        # Send response via WhatsApp API
        send_whatsapp_message(phone_number, response)
    
    return jsonify({'status': 'success'}), 200

def send_whatsapp_message(to, message):
    """Send message via WhatsApp Business API."""
    import requests
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    data = {
        'messaging_product': 'whatsapp',
        'to': to,
        'type': 'text',
        'text': {'body': message}
    }
    requests.post(url, headers=headers, json=data)
```

### 4. **Key Considerations**:
   - **State Persistence**: Use a database (Redis, PostgreSQL) instead of in-memory dict for production
   - **Rate Limiting**: WhatsApp has rate limits; implement queuing/throttling
   - **Media Handling**: Extend agent to handle images/videos if needed
   - **Security**: Validate webhook signatures, use HTTPS
   - **Deployment**: Deploy webhook server on cloud (AWS, GCP, Heroku) with public URL
   - **Webhook URL**: Configure in WhatsApp Business API dashboard

### 5. **Testing**:
   - Use ngrok for local testing: `ngrok http 5000`
   - Set webhook URL in WhatsApp Business API to ngrok URL

This architecture allows the agent to handle WhatsApp conversations while maintaining the same state management and workflow logic.

## Knowledge Base

The knowledge base (`knowledge_base.json`) contains:
- **Pricing Plans**: Basic Plan ($29/month) and Pro Plan ($79/month) with features
- **Company Policies**: Refund policy and support information
- **Company Info**: Description and target audience

You can modify this file to update pricing or add new information.

## Testing

To test the agent, run `python main.py` and try these scenarios:

1. **Pricing Inquiry**: "Tell me about your pricing"
2. **Feature Question**: "What's included in the Pro plan?"
3. **Policy Question**: "What's your refund policy?"
4. **High-Intent Lead**: "I want to sign up for the Pro plan for my YouTube channel"
5. **Lead Collection**: Provide name, email, and platform when prompted

## Debug Mode

Set the `DEBUG` environment variable to see internal state:

```bash
# Windows
$env:DEBUG="true"
python main.py

# Linux/Mac
DEBUG=true python main.py
```

## License

This project is created for the ServiceHive Machine Learning Intern assignment.

## Author

Built for ServiceHive - Inflx Project
