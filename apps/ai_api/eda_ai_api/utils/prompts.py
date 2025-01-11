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
Generate a friendly response asking for:
1. Project name and brief description
2. Specific grant program (if any)
3. Main project objectives
4. Target community/region

User message: {message}

Response:"""
    ),
    "discovery": PromptTemplate(
        """Previous conversation:
{context}

The user wants to find grant opportunities but needs more information.
Generate a friendly response asking for:
1. Main project topics/areas
2. Target region/community
3. Funding requirements/preferences

User message: {message}

Response:"""
    ),
}

RESPONSE_PROCESSOR_TEMPLATE = PromptTemplate(
    """IMPORTANT: You must respond in exactly the same language as the user's
    original message. User is on {platform} platform.
{original_message}

Process this response to:
1. MATCH THE EXACT LANGUAGE of the input message (this is crucial!)
2. Be clear and conversational in that language
3. Not exceed 2000 characters (summarize if longer)
4. Use {platform} formatting:
   - *bold* for important terms
   - _italic_ for emphasis
   - ```code``` for technical terms
   - ~strikethrough~ for corrections
   - Lists with emoji bullets
   - For URLs:
     Write "Link: " followed by URL
     Example:
     Link: http://example.com
5. If response looks like JSON, convert to natural language in the user's language:
   - For heartbeat: "*Yes, I'm here! 🟢*\n_Ready to help you!_"
   - For errors: "⚠️ *Error*: _[error message]_"
   - For other JSON: Convert to organized message with formatting (in user's language)

Original response:
{response}

Respond in the SAME LANGUAGE as the original message with {platform} formatting:"""
)
