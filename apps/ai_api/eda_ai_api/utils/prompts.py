from llama_index.core import PromptTemplate

ROUTER_TEMPLATE = PromptTemplate(
    """Given a user message, determine the appropriate service to handle the request.
    Choose between:
    - discovery: For finding grant opportunities
    - proposal: For writing grant proposals
    - onboarding: For getting help using the system
    - heartbeat: For checking system health

    User message: {message}

    Return only one word (discovery/proposal/onboarding/heartbeat):"""
)

TOPIC_TEMPLATE = PromptTemplate(
    """Previous conversation:
{context}

Extract up to 5 most relevant topics for grant opportunity research from the user message.
If there isn't enough context to determine specific topics, return "INSUFFICIENT_CONTEXT".
Otherwise, return only a comma-separated list of topics (maximum 5), no other text.

User message: {message}

Output:"""
)

PROPOSAL_TEMPLATE = PromptTemplate(
    """Previous conversation:
{context}

Extract the community project name and grant program name from the user message.
Return in format: project_name|grant_name
If either cannot be determined, use "unknown" as placeholder.

User message: {message}

Output:"""
)

INSUFFICIENT_TEMPLATES = {
    "proposal": PromptTemplate(
        """Previous conversation:
{context}

The user wants to write a proposal but hasn't provided enough information.
Generate a friendly response in the same language as the user's message asking for:
1. The project name and brief description
2. The specific grant program they're applying to (if any)
3. The main objectives of their project
4. The target community or region

User message: {message}

Response:"""
    ),
    "discovery": PromptTemplate(
        """Previous conversation:
{context}

The user wants to find grant opportunities but hasn't provided enough information.
Generate a friendly response in the same language as the user's message asking for:
1. The main topics or areas of their project
2. The target region or community
3. Any specific funding requirements or preferences

User message: {message}

Response:"""
    ),
}
