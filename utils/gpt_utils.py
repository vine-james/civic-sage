from openai import OpenAI
import utils.constants as constants

MODEL = "gpt-3.5-turbo" # Model: Use "gpt-4" for GPT-4o.

TEMPERATURE = 1.0 # Temperature: Controls the randomness of the output (e.g., 0.7 for more creative responses, 0 for deterministic).
MAX_TOKENS = 3000 # Max Tokens: Limits the length of the response.
TOP_P = 1.0 # Top-p: Controls diversity via nucleus sampling.


SYSTEM_PROMPT = f"""
Be nice and friendly!
"""

client = OpenAI(
    api_key=constants.TOKEN_OPENAI,
)

def prompt(message_prompt):
    # warnings.warn("This will send out a API call to generate a prompt for OpenAI GPT-4o. Are you sure?")
    # breakpoint()
    try:
        chat_completion = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message_prompt}
            ],
            temperature=TEMPERATURE,  # Controls randomness
            top_p=TOP_P,        # Controls diversity
            # max_tokens=MAX_TOKENS,    # Limits the response length
        )

        message = chat_completion.choices[0].message.content
    except:
        message = "I'm sorry. I timed out. Please ask again!"

    # breakpoint()
    return message