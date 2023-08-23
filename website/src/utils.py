import openai
import time
import os
import random

# Set OpenAI API key using the environment variable OPENAI_API_KEY
openai.api_key = os.getenv("OPENAI_API_KEY")


def getMessagesHTML(chat, modelName):
    """
    Turn each chat message into an 'Message' HTML component.

    This function takes the chat messages as input and converts them into 'Message' HTML components.
    It checks the role of each message (user, assistant) and generates the appropriate HTML code accordingly.

    Parameters:
        chat (list): A list of dictionaries representing chat messages.
        modelName (str): The name of the model (used for image src attribute).

    Returns:
        str: The HTML representation of the chat messages.
    """

    if not chat:  # Empty list
        return ""

    html = ""
    for message in chat:
        if message["role"] == "system":
            continue
        elif message["role"] == "assistant":
            html = html + (
                f"""<div class="message">
                        <img src="../static/resources/{modelName}.png">
                        <div class="bubble">
                            {message['content']}
                        </div>
                    </div>"""
            )
        elif message["role"] == "user":
            html = html + (
                f"""<div class="message right">
                        <img src="../static/resources/user_icon.png">
                        <div class="bubble">
                            {message['content']}
                        </div>
                    </div>"""
            )
    return html


def getFriendsHTML(models):
    """
    Turn each model name into a 'Friend' HTML component.

    This function takes a list of model names and converts each model name into a 'Friend' HTML component.
    It includes the model's name, image, and status (e.g., available) for display.

    Parameters:
        models (list): A list of model names.

    Returns:
        str: The HTML representation of the 'Friend' components.
    """

    if not models:  # Empty list
        return ""

    html = ""
    for model in models:
        html = html + (
            f"""<div class="friend">
                    <img src="../static/resources/{model}.png">
                    <p><strong>{model}</strong></p>
                    <div class="status available"></div>
                </div>"""
        )
    return html


def prepare_combined_prompt(chat_messages):
    """
    Prepare a combined prompt from the chat messages.

    This function combines the chat messages into a single prompt, including user and assistant responses,
    with appropriate role labels (User: and Assistant:). It is used to convert chat messages into a combined
    format that can be used by different chatbots/models.

    Parameters:
        chat_messages (list): A list of dictionaries representing chat messages.

    Returns:
        str: The combined prompt for the chat messages.
    """

    if not chat_messages:
        return ""

    combined_prompt = ""
    for message in chat_messages:
        role = message["role"]
        content = message["content"]
        if role == "system":
            combined_prompt = content
        elif role == "assistant":
            combined_prompt = combined_prompt + "\n" + "Assistant: " + content
        elif role == "user":
            combined_prompt = combined_prompt + "\n" + "User: " + content

    combined_prompt = combined_prompt + "\n" + "Assistant: "

    return combined_prompt


def requestOpenAPI(model, messages, temp):
    """
    Make a request to the OpenAI API and handle retries.

    This function sends a request to the OpenAI API with the given model, messages, and temperature.
    It handles any OpenAI errors and retries the request with exponential backoff if the service is busy.

    Parameters:
        model (str): The name of the OpenAI model.
        messages (list): A list of dictionaries representing chat messages.
        temp (float): The temperature value for response generation.

    Returns:
        dict: The API response from OpenAI.
    """

    for delay_secs in (2**x for x in range(0, 6)):
        try:
            response = openai.ChatCompletion.create(
                model=model, messages=messages, temperature=temp
            )
        except openai.OpenAIError as e:
            randomness_collision_avoidance = random.randint(0, 1000) / 1000.0
            sleep_dur = delay_secs + randomness_collision_avoidance
            print(
                f"Error: {e}. Retrying {model} response in {round(sleep_dur, 2)} seconds."
            )
            time.sleep(sleep_dur)
            continue

    return response
