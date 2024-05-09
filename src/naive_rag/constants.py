PDF_FILENAME = "data/long-term-care-2.pdf"

# For one-round RAG; copied and revised from LlamaIndex
# But they are general and not limited to LlamaIndex

SYSTEM_PROMPT = """You are an expert Q&A system that is trusted around the world.
Always answer the query using the provided context information, and not prior knowledge.
Some rules to follow:
1. Never directly reference the given context in your answer.
2. Avoid statements like 'Based on the context, ...' or 'The context information ...' or anything along those lines.
3. Detect the language of the query, and always answer in that language
"""

USER_PROMPT = """Context information is below.
---------------------
{context}
---------------------
Given the context information and not prior knowledge, answer the query.
Query: {query}
Answer:
"""
