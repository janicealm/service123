# Quick Start Guide

## Setup (5 minutes)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set your OpenAI API key:**
   ```bash
   # Windows (PowerShell)
   $env:OPENAI_API_KEY="your-api-key-here"
   
   # Linux/Mac
   export OPENAI_API_KEY="your-api-key-here"
   ```

3. **Validate setup:**
   ```bash
   python validate_setup.py
   ```

4. **Run the agent:**
   ```bash
   python main.py
   ```

## Quick Test

Run the demo script to see the agent in action:
```bash
python demo.py
```

## Example Conversation

```
You: Hi, tell me about your pricing.
Agent: [Provides pricing information from knowledge base]

You: I want to try the Pro plan for my YouTube channel.
Agent: [Detects high intent, starts collecting information]

Agent: Great! I'd love to help you get started. To proceed, I'll need:
1. What's your name?
2. What's your email address?
3. Which platform do you create content on?

You: My name is John Doe, email is john@example.com, and I create on YouTube.
Agent: [Validates and captures lead]
```

## Troubleshooting

- **Import errors**: Make sure all dependencies are installed: `pip install -r requirements.txt`
- **API key errors**: Verify your OPENAI_API_KEY is set correctly
- **Knowledge base errors**: Ensure `knowledge_base.json` exists and is valid JSON

## Files Overview

- `main.py` - Interactive chat interface
- `demo.py` - Automated demo script
- `agent.py` - Core agent logic with LangGraph
- `rag_pipeline.py` - Knowledge retrieval system
- `intent_detector.py` - Intent classification
- `lead_capture.py` - Lead collection and validation
- `knowledge_base.json` - Product information and policies
