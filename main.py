"""
Main entry point for the Conversational AI Agent.
Run this script to start an interactive chat session.
"""
import os
import sys
from agent import ConversationalAgent, AgentState


def main():
    """Main function to run the conversational agent."""
    print("=" * 60)
    print("AutoStream Conversational AI Agent")
    print("=" * 60)
    print("\nWelcome! I'm here to help you learn about AutoStream.")
    print("Type 'quit' or 'exit' to end the conversation.\n")
    
    # Get API key from environment or use hardcoded fallback
    api_key = os.getenv("OPENAI_API_KEY")
    
    # Hardcoded API key as fallback
    if not api_key:
        api_key = "@apikey"
        # Set it in environment for this session
        os.environ["OPENAI_API_KEY"] = api_key
        print("[INFO] Using configured API key.")
    
    if not api_key:
        print("[ERROR] OPENAI_API_KEY not set. Cannot proceed.")
        print("Please set OPENAI_API_KEY environment variable or update the code.")
        sys.exit(1)
    
    # Initialize agent
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
        else:
            print("\nMake sure you have:")
            print("1. Set OPENAI_API_KEY environment variable")
            print("2. Installed all requirements (pip install -r requirements.txt)")
            print("3. Your OpenAI account has available credits")
        
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
