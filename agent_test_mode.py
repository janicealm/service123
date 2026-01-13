"""
Test mode agent that works without OpenAI API calls.
Uses mock responses to demonstrate the agent workflow.
"""
import json
from typing import TypedDict, Annotated, List
from enum import Enum
from langchain_core.messages import HumanMessage, AIMessage


class Intent(Enum):
    """User intent types."""
    GREETING = "greeting"
    PRODUCT_INQUIRY = "product_inquiry"
    HIGH_INTENT_LEAD = "high_intent_lead"


class AgentState(TypedDict):
    """State management for the agent."""
    messages: List
    intent: str
    lead_info: dict
    conversation_turn: int


class MockRAGPipeline:
    """Mock RAG pipeline that returns hardcoded knowledge."""
    
    def __init__(self):
        with open("knowledge_base.json", 'r', encoding='utf-8') as f:
            self.kb_data = json.load(f)
    
    def get_context(self, query: str) -> str:
        """Return formatted knowledge base context."""
        context_parts = []
        
        # Pricing
        if "pricing" in self.kb_data:
            context_parts.append("## Pricing Plans\n")
            for plan_key, plan_data in self.kb_data["pricing"].items():
                context_parts.append(f"\n{plan_data['name']}:")
                context_parts.append(f"  Price: {plan_data['price']}")
                context_parts.append(f"  Videos per month: {plan_data['videos_per_month']}")
                context_parts.append(f"  Resolution: {plan_data['resolution']}")
                if "features" in plan_data:
                    context_parts.append(f"  Features: {', '.join(plan_data['features'])}")
        
        # Policies
        if "policies" in self.kb_data:
            context_parts.append("\n## Company Policies\n")
            for policy_key, policy_value in self.kb_data["policies"].items():
                if policy_key == "refund_policy":
                    context_parts.append(f"Refund Policy: {policy_value}")
                elif policy_key == "support":
                    context_parts.append(f"Support: {policy_value}")
        
        return "\n".join(context_parts)


class MockIntentDetector:
    """Mock intent detector using simple keyword matching."""
    
    def detect(self, message: str, conversation_history: str = "") -> Intent:
        """Detect intent from user message."""
        message_lower = message.lower()
        
        # Check if we're already collecting lead info (from conversation history)
        if "lead_info" in conversation_history.lower() or "name" in message_lower or "@" in message_lower:
            # If user is providing name/email, continue lead collection
            return Intent.HIGH_INTENT_LEAD
        
        # High intent keywords
        high_intent_keywords = ["want", "try", "sign up", "buy", "purchase", "interested", "ready"]
        platform_keywords = ["youtube", "instagram", "tiktok", "channel", "platform"]
        
        if any(keyword in message_lower for keyword in high_intent_keywords) or \
           any(keyword in message_lower for keyword in platform_keywords):
            return Intent.HIGH_INTENT_LEAD
        
        # Greeting keywords
        greeting_keywords = ["hi", "hello", "hey", "greetings"]
        if any(keyword in message_lower for keyword in greeting_keywords) and len(message_lower.split()) < 5:
            return Intent.GREETING
        
        # Default to product inquiry
        return Intent.PRODUCT_INQUIRY


class TestModeAgent:
    """Test mode agent that works without API calls."""
    
    def __init__(self):
        self.rag = MockRAGPipeline()
        self.intent_detector = MockIntentDetector()
        print("[INFO] Test mode agent initialized (no API calls required)")
    
    def _format_conversation_history(self, messages: List) -> str:
        """Format conversation history for context."""
        history_parts = []
        for msg in messages[-6:]:
            if isinstance(msg, HumanMessage):
                history_parts.append(f"User: {msg.content}")
            elif isinstance(msg, AIMessage):
                history_parts.append(f"Agent: {msg.content}")
        return "\n".join(history_parts)
    
    def chat(self, user_message: str, state: AgentState = None) -> tuple[str, AgentState]:
        """Process a user message and return agent response."""
        if state is None:
            state = {
                "messages": [],
                "intent": "",
                "lead_info": {},
                "conversation_turn": 0
            }
        
        # Add user message
        state["messages"].append(HumanMessage(content=user_message))
        
        # Check if we're already collecting lead info
        lead_info = state.get("lead_info", {})
        is_collecting_lead = bool(lead_info) and not (
            "name" in lead_info and lead_info.get("name") and
            "email" in lead_info and lead_info.get("email") and
            "platform" in lead_info and lead_info.get("platform")
        )
        
        # Detect intent
        history = self._format_conversation_history(state["messages"][:-1])
        
        # If we're collecting lead info, route to lead handler
        if is_collecting_lead:
            intent = Intent.HIGH_INTENT_LEAD
        else:
            intent = self.intent_detector.detect(user_message, history)
        
        state["intent"] = intent.value
        state["conversation_turn"] = state.get("conversation_turn", 0) + 1
        
        # Handle based on intent
        if intent == Intent.GREETING:
            response = "Hello! Welcome to AutoStream. I'm here to help you learn about our automated video editing platform for content creators. How can I assist you today?"
        
        elif intent == Intent.PRODUCT_INQUIRY:
            # Use RAG to answer
            context = self.rag.get_context(user_message)
            
            # Simple response generation based on query
            query_lower = user_message.lower()
            if "pricing" in query_lower or "price" in query_lower or "cost" in query_lower:
                response = """We offer two pricing plans:

**Basic Plan:**
- Price: $29/month
- 10 videos per month
- 720p resolution
- Basic editing tools

**Pro Plan:**
- Price: $79/month
- Unlimited videos
- 4K resolution
- AI captions
- Advanced editing tools

Which plan interests you?"""
            
            elif "pro" in query_lower and ("feature" in query_lower or "include" in query_lower):
                response = """The Pro Plan includes:
- Unlimited videos per month
- 4K resolution output
- AI-powered captions
- Advanced editing tools
- 24/7 support

It's perfect for professional content creators who need high-quality output and unlimited capacity."""
            
            elif "refund" in query_lower or "policy" in query_lower:
                response = "Our refund policy: No refunds after 7 days. We also offer 24/7 support, but only on the Pro plan."
            
            else:
                response = f"""Based on our knowledge base:

{context}

Is there anything specific you'd like to know about AutoStream?"""
        
        elif intent == Intent.HIGH_INTENT_LEAD:
            # Initialize lead_info if not present
            if "lead_info" not in state:
                state["lead_info"] = {}
            
            lead_info = state["lead_info"]
            
            # Extract information from message
            from lead_capture import extract_info_from_message
            extracted = extract_info_from_message(user_message)
            
            # Also check if user provided info directly in the message
            user_lower = user_message.lower()
            
            # Extract name
            if "name" in extracted and extracted["name"]:
                lead_info["name"] = extracted["name"]
            elif "name" not in lead_info or not lead_info.get("name"):
                # Try to extract name from patterns
                import re
                name_patterns = [
                    r"(?:i'?m|my name is|i am|this is|call me)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
                    r"name[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)"
                ]
                for pattern in name_patterns:
                    name_match = re.search(pattern, user_message, re.IGNORECASE)
                    if name_match:
                        potential_name = name_match.group(1).strip()
                        # Basic validation: name shouldn't be too long or contain email-like patterns
                        if len(potential_name) < 50 and '@' not in potential_name:
                            lead_info["name"] = potential_name
                            break
            
            # Extract email
            if "email" in extracted and "email" not in lead_info:
                lead_info["email"] = extracted["email"]
            elif "email" not in lead_info:
                import re
                email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', user_message)
                if email_match:
                    lead_info["email"] = email_match.group()
            
            # Extract platform
            if "platform" in extracted and "platform" not in lead_info:
                lead_info["platform"] = extracted["platform"]
            elif "platform" not in lead_info:
                platforms = ['YouTube', 'Instagram', 'TikTok', 'Facebook', 'Twitter', 'LinkedIn', 'Twitch']
                for platform in platforms:
                    if platform.lower() in user_lower:
                        lead_info["platform"] = platform
                        break
            
            # Check what's missing
            missing = []
            if "name" not in lead_info or not lead_info["name"]:
                missing.append("name")
            if "email" not in lead_info or not lead_info["email"]:
                missing.append("email")
            if "platform" not in lead_info or not lead_info["platform"]:
                missing.append("platform")
            
            if missing:
                if len(missing) == 3:
                    response = "Great! I'd love to help you get started with AutoStream. To proceed, I'll need a few details:\n\n1. What's your name?\n2. What's your email address?\n3. Which platform do you create content on? (YouTube, Instagram, TikTok, etc.)"
                elif len(missing) == 2:
                    if "name" in missing and "email" in missing:
                        response = "I'd like to collect your name and email address to proceed."
                    elif "name" in missing and "platform" in missing:
                        response = "I'd like to know your name and which platform you create content on."
                    else:
                        response = "I'd like to collect your email and which platform you create content on."
                else:
                    if "name" in missing:
                        response = "What's your name?"
                    elif "email" in missing:
                        response = "What's your email address?"
                    else:
                        response = "Which platform do you create content on? (YouTube, Instagram, TikTok, etc.)"
            else:
                # All info collected - call mock_lead_capture
                from lead_capture import mock_lead_capture, validate_email
                
                name = lead_info.get("name", "")
                email = lead_info.get("email", "")
                platform = lead_info.get("platform", "")
                
                if validate_email(email):
                    result = mock_lead_capture(name, email, platform)
                    response = f"Perfect! I've captured your information:\n- Name: {name}\n- Email: {email}\n- Platform: {platform}\n\nOur team will reach out to you shortly to help you get started with AutoStream!"
                else:
                    response = "I need a valid email address. Could you please provide your email?"
        
        else:
            response = "I'm here to help! How can I assist you with AutoStream?"
        
        # Add AI response to state
        state["messages"].append(AIMessage(content=response))
        
        return response, state


# Alias for compatibility
ConversationalAgent = TestModeAgent
