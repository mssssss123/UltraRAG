RANKCOT_PROMPTS = dict()

RANKCOT_PROMPTS["cot"] = """
Conversation History:{history}

Passage:{content}

Based on the conversation history and the passages, answer the question below.

Question:{query}

Let's think step by step:
"""

RANKCOT_PROMPTS["answer"] = """
Task Description:
1. Read the given question and related chain of thought to gather relevant information.
2. The content of the chain of thought is the thinking process that may be used to answer the question.
3. If the chain of thought don't work, please answer the question based on your own knowledge.
4. Give a short answer to a given question.

Question:{query}

Chain of Thought:{cot_response}
"""