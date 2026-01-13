"""
Demo script showcasing the agent's capabilities.
This script runs through a complete conversation flow.
"""
import os
from agent import ConversationalAgent

def run_demo():
    """Run a demonstration of the agent."""
    print("=" * 70)
    print("AutoStream Conversational AI Agent - Demo")
    print("=" * 70)
    print()
    
    # Initialize agent
    api_key = os.getenv("OPENAI_API_KEY")
    
    # Hardcoded API key as fallback
    if not api_key:
        api_key = "@apikey"
        # Set it in environment for this session
        os.environ["OPENAI_API_KEY"] = api_key
    
    if not api_key:
        print("[ERROR] OPENAI_API_KEY not set. Cannot proceed.")
        return
    
    try:
        agent = ConversationalAgent(api_key=api_key)
        print("[OK] Agent initialized successfully!\n")
    except Exception as e:
        error_msg = str(e)
        print(f"[ERROR] Error initializing agent: {e}")
        
        # Provide helpful error messages
        if "quota" in error_msg.lower() or "insufficient_quota" in error_msg.lower():
            print("\n[INFO] Your OpenAI account has exceeded its quota or has no credits.")
            print("Please check your billing and usage at: https://platform.openai.com/usage")
            print("You may need to add credits to your account.")
        elif "invalid_api_key" in error_msg.lower() or "401" in error_msg:
            print("\n[INFO] Invalid API key. Please verify your OPENAI_API_KEY is correct.")
            print("Get your API key from: https://platform.openai.com/api-keys")
        
        return
    
    # Initialize state
    state = {
        "messages": [],
        "intent": "",
        "lead_info": {},
        "conversation_turn": 0
    }
    
    # Demo conversation flow
    demo_messages = [
        "Hi, tell me about your pricing.",
        "What's included in the Pro plan?",
        "That sounds good, I want to try the Pro plan for my YouTube channel.",
        "My name is John Doe",
        "john.doe@example.com"
    ]
    
    print("Running demo conversation...\n")
    print("-" * 70)
    
    for i, user_msg in enumerate(demo_messages, 1):
        print(f"\n[Turn {i}] User: {user_msg}")
        print("-" * 70)
        
        response, state = agent.chat(user_msg, state)
        print(f"Agent: {response}")
        
        # Show state info
        print(f"\n[State] Intent: {state.get('intent', 'N/A')}")
        if state.get('lead_info'):
            print(f"[State] Lead Info: {state.get('lead_info', {})}")
        print("-" * 70)
    
    print("\n" + "=" * 70)
    print("Demo completed!")
    print("=" * 70)

if __name__ == "__main__":
    run_demo()
