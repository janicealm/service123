"""
Main entry point for TEST MODE (no API calls required).
Run this script to start an interactive chat session without needing OpenAI credits.
"""
import os
import sys
from agent_test_mode import TestModeAgent, AgentState


def main():
    """Main function to run the conversational agent in test mode."""
    print("=" * 60)
    print("AutoStream Conversational AI Agent - TEST MODE")
    print("=" * 60)
    print("\n[INFO] Running in test mode - no API calls required!")
    print("Welcome! I'm here to help you learn about AutoStream.")
    print("Type 'quit' or 'exit' to end the conversation.\n")
    
    # Initialize agent (test mode)
    try:
        agent = TestModeAgent()
        print("[OK] Agent initialized successfully!\n")
    except Exception as e:
        print(f"[ERROR] Error initializing agent: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Initialize state
    state: AgentState = {
        "messages": [],
        "intent": "",
        "lead_info": {},
        "conversation_turn": 0
    }
    
    # Conversation loop
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\nThank you for chatting with AutoStream! Goodbye!")
                break
            
            if not user_input:
                continue
            
            # Process message
            response, state = agent.chat(user_input, state)
            
            print(f"\nAgent: {response}")
            
            # Show state info (for debugging)
            if os.getenv("DEBUG", "").lower() == "true":
                print(f"\n[DEBUG] Intent: {state.get('intent', 'N/A')}")
                print(f"[DEBUG] Lead Info: {state.get('lead_info', {})}")
                print(f"[DEBUG] Turn: {state.get('conversation_turn', 0)}")
        
        except KeyboardInterrupt:
            print("\n\nConversation interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n[ERROR] Error: {e}")
            if os.getenv("DEBUG", "").lower() == "true":
                import traceback
                traceback.print_exc()


if __name__ == "__main__":
    main()
