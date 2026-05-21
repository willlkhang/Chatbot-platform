from langchain_core.tools import tool
from repository import retriever_ICT283, retriever_ICT167, retriever_ICT159

@tool
def ICT283_questions(query: str) -> str:
    """ALWAYS use this tool when the user asks a question has ICT283_questions keywords.
        Look for keywords:
        - Assignment 1
        - Assignment 2
        - Lab, tutorials
        - SOLID
        - ICT283
        - No marks, zero marks
        - Demostrate, demo, demostration
    """
    docs = retriever_ICT283.invoke(query)
    return "\n\n".join(doc.page_content for doc in docs)

@tool
def ICT167_questions(query: str) -> str:
    """ALWAYS use this tool when the user asks a question has ICT167_questions keywords.
    Look for keywords:
    - ICT167
    """
    docs = retriever_ICT167.invoke(query)
    return "\n\n".join(doc.page_content for doc in docs)

@tool
def ICT159_questions(query: str) -> str:
    """ALWAYS use this tool when the user asks a question has ICT159_questions keywords.
    Look for keywords:
    - ICT159
    - Modularity
    """
    docs = retriever_ICT159.invoke(query)
    return "\n\n".join(doc.page_content for doc in docs)