"""
RAG Pipeline for knowledge retrieval from local knowledge base.
"""
import json
from typing import List, Dict
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


class RAGPipeline:
    """RAG pipeline for retrieving information from knowledge base."""
    
    def __init__(self, knowledge_base_path: str = "knowledge_base.json", api_key: str = None):
        """
        Initialize RAG pipeline.
        
        Args:
            knowledge_base_path: Path to JSON knowledge base
            api_key: OpenAI API key for embeddings (if None, uses environment variable)
        """
        self.knowledge_base_path = knowledge_base_path
        
        # Ensure API key is available - use environment variable if not provided
        if api_key is None:
            import os
            api_key = os.getenv("OPENAI_API_KEY")
        
        self.embeddings = OpenAIEmbeddings(api_key=api_key)
        self.vectorstore = None
        self._load_and_index_knowledge_base()
    
    def _load_knowledge_base(self) -> Dict:
        """Load knowledge base from JSON file."""
        try:
            with open(self.knowledge_base_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Knowledge base file not found: {self.knowledge_base_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in knowledge base: {e}")
    
    def _format_knowledge_base(self, kb_data: Dict) -> str:
        """Format knowledge base data into searchable text."""
        text_parts = []
        
        # Company info
        if "company_info" in kb_data:
            info = kb_data["company_info"]
            text_parts.append(f"Company: {info.get('name', 'AutoStream')}")
            text_parts.append(f"Description: {info.get('description', '')}")
        
        # Pricing plans
        if "pricing" in kb_data:
            text_parts.append("\n## Pricing Plans\n")
            for plan_key, plan_data in kb_data["pricing"].items():
                text_parts.append(f"\n{plan_data['name']}:")
                text_parts.append(f"  Price: {plan_data['price']}")
                text_parts.append(f"  Videos per month: {plan_data['videos_per_month']}")
                text_parts.append(f"  Resolution: {plan_data['resolution']}")
                if "features" in plan_data:
                    text_parts.append(f"  Features: {', '.join(plan_data['features'])}")
        
        # Policies
        if "policies" in kb_data:
            text_parts.append("\n## Company Policies\n")
            for policy_key, policy_value in kb_data["policies"].items():
                if policy_key == "refund_policy":
                    text_parts.append(f"Refund Policy: {policy_value}")
                elif policy_key == "support":
                    text_parts.append(f"Support: {policy_value}")
        
        return "\n".join(text_parts)
    
    def _load_and_index_knowledge_base(self):
        """Load knowledge base and create vector store."""
        kb_data = self._load_knowledge_base()
        formatted_text = self._format_knowledge_base(kb_data)
        
        # Create documents
        documents = [Document(page_content=formatted_text, metadata={"source": "knowledge_base"})]
        
        # Split documents
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        split_docs = text_splitter.split_documents(documents)
        
        # Create vector store
        self.vectorstore = FAISS.from_documents(split_docs, self.embeddings)
    
    def retrieve(self, query: str, k: int = 3) -> List[str]:
        """
        Retrieve relevant information from knowledge base.
        
        Args:
            query: User query
            k: Number of documents to retrieve
            
        Returns:
            List of relevant text chunks
        """
        if self.vectorstore is None:
            return ["Knowledge base not loaded."]
        
        docs = self.vectorstore.similarity_search(query, k=k)
        return [doc.page_content for doc in docs]
    
    def get_context(self, query: str) -> str:
        """
        Get formatted context for the query.
        
        Args:
            query: User query
            
        Returns:
            Formatted context string
        """
        retrieved_docs = self.retrieve(query)
        return "\n\n".join(retrieved_docs)
