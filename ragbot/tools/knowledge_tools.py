from langchain_core.tools import tool
from repository import retriever_ICT283, retriever_SOF


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
def Stack_overflow_questions(query: str) -> str:
    """ALWAYS use this tool when the user asks a question has Stack_overflow_questions keywords.
        Look for keywords:
        - Tree
        - Graph
        - DSA
        - Programming language
        - Interface, Abstract Classes
        - C, C++, Java, Python, C#, JavaScript, TypeScript
    """
    docs = retriever_SOF.invoke(query)
    return "\n\n".join(doc.page_content for doc in docs)