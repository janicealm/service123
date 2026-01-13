"""
Intent detection system for classifying user messages.
"""
from enum import Enum
from typing import Dict
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate


class Intent(Enum):
    """User intent types."""
    GREETING = "greeting"
    PRODUCT_INQUIRY = "product_inquiry"
    HIGH_INTENT_LEAD = "high_intent_lead"


class IntentDetector:
    """Detects user intent from conversation messages."""
    
    def __init__(self, api_key: str = None, model: str = "gpt-4o-mini"):
        """
        Initialize intent detector.
        
        Args:
            api_key: OpenAI API key (if None, uses environment variable)
            model: LLM model to use
        """
        # Ensure API key is available - use environment variable if not provided
        if api_key is None:
            import os
            api_key = os.getenv("OPENAI_API_KEY")
        
        self.llm = ChatOpenAI(
            model=model,
            temperature=0,
            api_key=api_key
        )
        
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are an intent classification system for AutoStream, a SaaS video editing platform.

Classify the user's message into one of these intents:
1. "greeting" - Casual greetings, hello, hi, etc.
2. "product_inquiry" - Questions about pricing, features, plans, policies
3. "high_intent_lead" - User shows clear interest in signing up, wants to try/buy, mentions their platform/channel, ready to proceed

Consider the conversation history to understand context. A user asking about pricing is "product_inquiry", but if they say "I want to try/sign up/buy" or mention their platform, classify as "high_intent_lead".

Respond with ONLY the intent name: greeting, product_inquiry, or high_intent_lead"""),
            ("human", "Conversation history:\n{history}\n\nUser message: {message}\n\nIntent:")
        ])
    
    def detect(self, message: str, conversation_history: str = "") -> Intent:
        """
        Detect intent from user message.
        
        Args:
            message: Current user message
            conversation_history: Previous conversation context
            
        Returns:
            Detected Intent enum
        """
        prompt = self.prompt_template.format_messages(
            history=conversation_history or "No previous conversation.",
            message=message
        )
        
        response = self.llm.invoke(prompt)
        intent_str = response.content.strip().lower()
        
        # Map string to enum
        intent_map = {
            "greeting": Intent.GREETING,
            "product_inquiry": Intent.PRODUCT_INQUIRY,
            "high_intent_lead": Intent.HIGH_INTENT_LEAD
        }
        
        return intent_map.get(intent_str, Intent.PRODUCT_INQUIRY)
