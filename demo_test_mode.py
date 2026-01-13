"""
Demo script using test mode (no API calls required).
This works without OpenAI credits!
"""
from agent_test_mode import TestModeAgent

def run_demo():
    """Run a demonstration of the agent in test mode."""
    print("=" * 70)
    print("AutoStream Conversational AI Agent - TEST MODE")
    print("=" * 70)
    print("[INFO] Running in test mode - no API calls required!")
    print()
    
    # Initialize agent (test mode)
    try:
        agent = TestModeAgent()
        print("[OK] Agent initialized successfully!\n")
    except Exception as e:
        print(f"[ERROR] Error initializing agent: {e}")
        import traceback
        traceback.print_exc()
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
        
        try:
            response, state = agent.chat(user_msg, state)
            print(f"Agent: {response}")
            
            # Show state info
            print(f"\n[State] Intent: {state.get('intent', 'N/A')}")
            if state.get('lead_info'):
                print(f"[State] Lead Info: {state.get('lead_info', {})}")
            print("-" * 70)
        except Exception as e:
            print(f"[ERROR] Error processing message: {e}")
            import traceback
            traceback.print_exc()
            break
    
    print("\n" + "=" * 70)
    print("Demo completed!")
    print("=" * 70)
    print("\n[INFO] This was test mode - no API calls were made.")
    print("[INFO] To use real OpenAI API, add credits and run: python demo.py")

if __name__ == "__main__":
    run_demo()
