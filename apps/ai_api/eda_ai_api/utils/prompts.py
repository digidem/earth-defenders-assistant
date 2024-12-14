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

RESPONSE_PROCESSOR_TEMPLATE = PromptTemplate(
    """IMPORTANT: You must respond in exactly the same language as the user's original message:
{original_message}

Process this response to:
1. MATCH THE EXACT LANGUAGE of the input message (this is crucial!)
2. Be clear and conversational in that language
3. Not exceed 2000 characters (summarize if longer)
4. Use WhatsApp formatting:
   - *bold* for important terms
   - _italic_ for emphasis
   - ```code``` for technical terms
   - ~strikethrough~ for corrections
   - Lists with emoji bullets
   - For URLs: Write "Link: " followed by the plain URL (no markdown)
     Example: "Link: https://example.com"
5. If response looks like JSON, convert to natural language in the user's language:
   - For heartbeat: "*Yes, I'm here! 🟢*\n_Ready to help you!_" (translate to match user's language)
   - For errors: "⚠️ *Error*: _[error message]_" (translate to match user's language)
   - For other JSON: Convert to organized message with formatting (in user's language)

Original response:
{response}

Respond in the SAME LANGUAGE as the original message with WhatsApp formatting:"""
)
