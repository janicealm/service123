"""
Main Conversational AI Agent using LangGraph with state management.
"""
from typing import TypedDict, Annotated, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

from rag_pipeline import RAGPipeline
from intent_detector import IntentDetector, Intent
from lead_capture import mock_lead_capture, validate_email, extract_info_from_message


class AgentState(TypedDict):
    """State management for the agent."""
    messages: Annotated[List, add_messages]
    intent: str
    lead_info: dict  # Stores name, email, platform as they're collected
    conversation_turn: int


class ConversationalAgent:
    """Main conversational agent with RAG, intent detection, and lead capture."""
    
    def __init__(self, api_key: str = None, model: str = "gpt-4o-mini"):
        """
        Initialize the conversational agent.
        
        Args:
            api_key: OpenAI API key (if None, uses environment variable)
            model: LLM model to use
        """
        # Ensure API key is available - use environment variable if not provided
        if api_key is None:
            import os
            api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            raise ValueError("OpenAI API key must be provided either as parameter or OPENAI_API_KEY environment variable")
        
        self.llm = ChatOpenAI(
            model=model,
            temperature=0.7,
            api_key=api_key
        )
        
        self.rag = RAGPipeline(api_key=api_key)
        self.intent_detector = IntentDetector(api_key=api_key, model=model)
        
        # Build the graph
        self.graph = self._build_graph()
        self.app = self.graph.compile()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state graph."""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("process_message", self._process_message)
        workflow.add_node("handle_greeting", self._handle_greeting)
        workflow.add_node("handle_inquiry", self._handle_inquiry)
        workflow.add_node("handle_lead", self._handle_lead)
        workflow.add_node("collect_lead_info", self._collect_lead_info)
        
        # Set entry point
        workflow.set_entry_point("process_message")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "process_message",
            self._route_intent,
            {
                "greeting": "handle_greeting",
                "product_inquiry": "handle_inquiry",
                "high_intent_lead": "handle_lead"
            }
        )
        
        workflow.add_conditional_edges(
            "handle_lead",
            self._check_lead_info_complete,
            {
                "complete": "collect_lead_info",
                "incomplete": END
            }
        )
        
        # All other nodes go to END
        workflow.add_edge("handle_greeting", END)
        workflow.add_edge("handle_inquiry", END)
        workflow.add_edge("collect_lead_info", END)
        
        return workflow
    
    def _process_message(self, state: AgentState) -> AgentState:
        """Process incoming message and detect intent."""
        messages = state["messages"]
        last_message = messages[-1]
        
        # Get conversation history for context
        history = self._format_conversation_history(messages[:-1])
        user_message = last_message.content if hasattr(last_message, 'content') else str(last_message)
        
        # Check if we're already collecting lead info
        lead_info = state.get("lead_info", {})
        is_collecting_lead = bool(lead_info) and not (
            "name" in lead_info and lead_info.get("name") and
            "email" in lead_info and lead_info.get("email") and validate_email(lead_info.get("email", "")) and
            "platform" in lead_info and lead_info.get("platform")
        )
        
        # If we're collecting lead info, route to lead handler regardless of detected intent
        if is_collecting_lead:
            state["intent"] = "high_intent_lead"
        else:
            # Detect intent
            intent = self.intent_detector.detect(user_message, history)
            state["intent"] = intent.value
        
        state["conversation_turn"] = state.get("conversation_turn", 0) + 1
        
        return state
    
    def _route_intent(self, state: AgentState) -> str:
        """Route to appropriate handler based on intent."""
        return state["intent"]
    
    def _handle_greeting(self, state: AgentState) -> AgentState:
        """Handle greeting messages."""
        system_prompt = """You are a friendly AI assistant for AutoStream, an automated video editing platform for content creators. 
Respond warmly to greetings and offer to help with information about AutoStream's pricing, features, or plans."""
        
        messages = state["messages"]
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages")
        ])
        
        formatted_prompt = prompt.format_messages(messages=messages)
        response = self.llm.invoke(formatted_prompt)
        
        state["messages"].append(AIMessage(content=response.content))
        return state
    
    def _handle_inquiry(self, state: AgentState) -> AgentState:
        """Handle product/pricing inquiries using RAG."""
        messages = state["messages"]
        last_message = messages[-1]
        user_query = last_message.content if hasattr(last_message, 'content') else str(last_message)
        
        # Retrieve relevant context from knowledge base
        context = self.rag.get_context(user_query)
        
        system_prompt = f"""You are a helpful AI assistant for AutoStream, an automated video editing platform for content creators.

Use the following knowledge base information to answer user questions accurately:

{context}

Answer questions clearly and concisely. If asked about pricing, provide specific details about both plans. If asked about features, be specific about what each plan includes."""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages")
        ])
        
        formatted_prompt = prompt.format_messages(messages=messages)
        response = self.llm.invoke(formatted_prompt)
        
        state["messages"].append(AIMessage(content=response.content))
        return state
    
    def _handle_lead(self, state: AgentState) -> AgentState:
        """Handle high-intent leads - collect information."""
        messages = state["messages"]
        last_message = messages[-1]
        user_message = last_message.content if hasattr(last_message, 'content') else str(last_message)
        
        # Initialize lead_info if not present
        if "lead_info" not in state:
            state["lead_info"] = {}
        
        lead_info = state["lead_info"]
        
        # Try to extract information from the message
        extracted = extract_info_from_message(user_message)
        if "name" in extracted and "name" not in lead_info:
            lead_info["name"] = extracted["name"]
        if "email" in extracted and "email" not in lead_info:
            lead_info["email"] = extracted["email"]
        if "platform" in extracted and "platform" not in lead_info:
            lead_info["platform"] = extracted["platform"]
        
        # Determine what's missing
        missing = []
        if "name" not in lead_info:
            missing.append("name")
        if "email" not in lead_info:
            missing.append("email")
        if "platform" not in lead_info:
            missing.append("platform (e.g., YouTube, Instagram)")
        
        if missing:
            # Ask for missing information
            if len(missing) == 3:
                response_text = "Great! I'd love to help you get started with AutoStream. To proceed, I'll need a few details:\n\n1. What's your name?\n2. What's your email address?\n3. Which platform do you create content on? (YouTube, Instagram, TikTok, etc.)"
            elif len(missing) == 2:
                if "name" in missing and "email" in missing:
                    response_text = "I'd like to collect your name and email address to proceed."
                elif "name" in missing and "platform" in missing:
                    response_text = "I'd like to know your name and which platform you create content on."
                else:
                    response_text = "I'd like to collect your email and which platform you create content on."
            else:
                if "name" in missing:
                    response_text = "What's your name?"
                elif "email" in missing:
                    response_text = "What's your email address?"
                else:
                    response_text = "Which platform do you create content on? (YouTube, Instagram, TikTok, etc.)"
        else:
            response_text = "Thank you! I have all the information I need."
        
        state["messages"].append(AIMessage(content=response_text))
        return state
    
    def _check_lead_info_complete(self, state: AgentState) -> str:
        """Check if all lead information has been collected."""
        lead_info = state.get("lead_info", {})
        
        has_name = "name" in lead_info and lead_info["name"]
        has_email = "email" in lead_info and lead_info["email"] and validate_email(lead_info["email"])
        has_platform = "platform" in lead_info and lead_info["platform"]
        
        if has_name and has_email and has_platform:
            return "complete"
        return "incomplete"
    
    def _collect_lead_info(self, state: AgentState) -> AgentState:
        """Collect and validate lead information, then call mock_lead_capture."""
        lead_info = state["lead_info"]
        
        name = lead_info.get("name", "")
        email = lead_info.get("email", "")
        platform = lead_info.get("platform", "")
        
        # Validate email
        if not validate_email(email):
            state["messages"].append(AIMessage(
                content="I need a valid email address. Could you please provide your email?"
            ))
            return state
        
        # Call mock lead capture
        result = mock_lead_capture(name, email, platform)
        
        # Add confirmation message
        confirmation = f"Perfect! I've captured your information:\n- Name: {name}\n- Email: {email}\n- Platform: {platform}\n\nOur team will reach out to you shortly to help you get started with AutoStream!"
        state["messages"].append(AIMessage(content=confirmation))
        
        return state
    
    def _format_conversation_history(self, messages: List) -> str:
        """Format conversation history for context."""
        history_parts = []
        for msg in messages[-6:]:  # Last 6 messages for context
            if isinstance(msg, HumanMessage):
                history_parts.append(f"User: {msg.content}")
            elif isinstance(msg, AIMessage):
                history_parts.append(f"Agent: {msg.content}")
        return "\n".join(history_parts)
    
    def chat(self, user_message: str, state: AgentState = None) -> tuple[str, AgentState]:
        """
        Process a user message and return agent response.
        
        Args:
            user_message: User's message
            state: Current agent state (None for new conversation)
            
        Returns:
            Tuple of (agent_response, new_state)
        """
        if state is None:
            state = {
                "messages": [],
                "intent": "",
                "lead_info": {},
                "conversation_turn": 0
            }
        
        # Add user message
        state["messages"].append(HumanMessage(content=user_message))
        
        # Run the graph
        final_state = self.app.invoke(state)
        
        # Get the last AI message
        messages = final_state["messages"]
        last_ai_message = None
        for msg in reversed(messages):
            if isinstance(msg, AIMessage):
                last_ai_message = msg.content
                break
        
        return last_ai_message or "I'm here to help!", final_state
