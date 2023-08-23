import copy
from flask import Flask, render_template, request, jsonify

from src.prompts import (
    DAN_pizza_systemMsg,
    DAN_pizza_guideLines,
    DAN_suicidePrevention_systemMsg,
    DAN_suicidePrevention_guideLines,
)
import src.utils as utils
from src.prompts import unittest_prompts, unittest_prompts_suicide

app = Flask(__name__)

################################################################
# Initilization
################################################################

# Temperature value for the Language Model (LLM)
LLM_TEMPERATURE = 1

# Temperature value for the Guideline Checker (GL)
GL_CHECKER_TEMPERATURE = 0

# Number of unit tests to perform
# Each one requires another API call
UNIT_TEST_COUNT = 3

# Number of times a prompt will be queried to LLM
# Must be an odd number
REPETITION_COUNT = 3


models = ["ChatGPT 3.5"]  # , "FastChat T5", "BlenderBot"]

# The data structure that holds messages is as follows
#
# chat_messages = {
#   LLM#1: [
#       {"role": "system", "content": SYSTEM_MSG},
#       {"role": "user", "content": USER_MSG#1},
#       {"role": "assistant", "content": LLM_RESPONSE#1},
#       {"role": "user", "content": USER_MSG#2},
#       {"role": "assistant", "content": LLM_RESPONSE#2},
#   ],
#   LLM#2: [
#       {"role": "system", "content": SYSTEM_MSG},
#       {"role": "user", "content": USER_MSG#1},
#       {"role": "assistant", "content": LLM_RESPONSE#1},
#       {"role": "user", "content": USER_MSG#2},
#       {"role": "assistant", "content": LLM_RESPONSE#2},
#   ],
#   ...
# }

chat1_messages = {}
chat2_messages = {}
for model in models:
    chat1_messages[model] = []
    chat2_messages[model] = []


# Define templates
@app.route("/")
def index():
    friends_HTML = utils.getFriendsHTML(models)
    return render_template(
        "index.html", chat1_friends=friends_HTML, chat2_friends=friends_HTML
    )


@app.route("/friend_selected", methods=["POST"])
def friend_selected():
    name = request.form.get("name")
    chatbox_id = request.form.get("chatboxId")

    if chatbox_id == "chatbox1":
        chat1_messages_HTML = utils.getMessagesHTML(chat1_messages[name], name)
        return jsonify({"messages": chat1_messages_HTML})
    elif chatbox_id == "chatbox2":
        chat2_messages_HTML = utils.getMessagesHTML(chat2_messages[name], name)
        return jsonify({"messages": chat2_messages_HTML})
    else:
        return jsonify({"error": "Unexpected chatboxid provided"})


@app.route("/send_message", methods=["POST"])
def send_message():
    msg = request.form.get("message")
    chatbox_id = request.form.get("chatboxId")
    name = request.form.get("selectedModel")

    ################################################################
    # Made a request to chatbot
    ################################################################
    llm_response = None
    chat_messages = None
    gl_message = []
    unittests_prompts = None

    # Chatteroni received a message
    if chatbox_id == "chatbox1":
        unittests_prompts = unittest_prompts
        chat_messages = chat1_messages
        # The list of messages is empty initialize with the system message
        if not chat_messages[name]:
            chat_messages[name].append(
                {"role": "system", "content": DAN_pizza_systemMsg}
            )
        # Start guideline checker with right guidelines
        gl_message.append({"role": "system", "content": DAN_pizza_guideLines})
    # Guardian angel received a message
    elif chatbox_id == "chatbox2":
        unittests_prompts = unittest_prompts_suicide
        chat_messages = chat2_messages
        # The list of messages is empty initialize with the system message
        if not chat_messages[name]:
            chat_messages[name].append(
                {"role": "system", "content": DAN_suicidePrevention_systemMsg}
            )
        # Start guideline checker with right guidelines
        gl_message.append(
            {"role": "system", "content": DAN_suicidePrevention_guideLines}
        )
    else:
        return jsonify({"error": "Unexpected chatboxid provided"})

    # Append the question to the history
    chat_messages[name].append({"role": "user", "content": msg})

    print('Message is being forwarded to the chatbot....')
    if name == "ChatGPT 3.5":
        llm_response = utils.requestOpenAPI(
            "gpt-3.5-turbo", chat_messages[name], LLM_TEMPERATURE
        )
    else:
        return jsonify({"error": "Unexpected model name provided"})
    
    ################################################################
    # Perform Unittest for Guideline Checker
    ################################################################
    print('Unittesting the guideline checker before accepting its response....')

    healthy_gl_checker = True

    for unittest in unittests_prompts[:UNIT_TEST_COUNT]: # Take only some unittests for less API access
        unittestNumber, _, _, unittestPrompt = unittest

        gl_this_unittest_context = copy.deepcopy(gl_message)
        gl_this_unittest_context.append(
            {"role": "user", "content": "##### " + unittestPrompt + " #####"}
        )

        gl_test_response = utils.requestOpenAPI(
            "gpt-3.5-turbo", gl_this_unittest_context, GL_CHECKER_TEMPERATURE
        )
        print(f'Test {unittestNumber} response: {gl_test_response.choices[0].message.content}')
        # Storing last rejected response
        if "Rejected" not in gl_test_response.choices[0].message.content:
            print(
                f"All unit tests are expected to yield a rejected answer from the guideline checker. \
                However, the {unittestNumber}.test got accepted thus failing the test. At this point \
                we suspect that the guideline checker might be corrupted."
            )

            chat_messages[name].append(
                {
                    "role": "assistant",
                    "content": "This prompt led to a comprimised unit-test, please rephrase your message or try again.",
                }
            )
            healthy_gl_checker = False
            break

    if healthy_gl_checker:
        ################################################################
        # Check if the answer violates any guidelines
        ################################################################
        print('Generated response is being checked for the guidelines....')
        print('This procedure will be repeated {REPETITION_COUNT} times....')

        # As a part of protection against injection attacks, we wrap the response with a certain
        # delimeter (five hashtags) and tell the model to interpret it as a text rather than
        # a command.
        gl_message.append({"role": "user", "content": "##### " + llm_response.choices[0].message.content + " #####"})

        acceptance_rate = 0
        rejection_rate = 0
        for i in range(REPETITION_COUNT):
            print(f"Checking {i}\{REPETITION_COUNT}...")
            gl_response = utils.requestOpenAPI(
                "gpt-3.5-turbo", gl_message, GL_CHECKER_TEMPERATURE
            )

            if "Accepted" in gl_response.choices[0].message.content:
                # Guideline checker is not altered and the response is accepted
                acceptance_rate = acceptance_rate + 1

            if "Rejected" in gl_response.choices[0].message.content:
                # Guideline checker is not altered and the response is rejected
                rejection_rate = rejection_rate + 1


        if acceptance_rate > rejection_rate:
            chat_messages[name].append({"role": "assistant", "content": llm_response.choices[0].message.content})
        else:
            rejection_message = llm_response.choices[0].message.content.replace(
                "Rejected response",
                "The generated answer for this question is rejected due to the following reason, please try a different prompt",
            )
            chat_messages[name].append({"role": "assistant", "content": rejection_message})

    print('Done...')
    ################################################################
    # Update DOM
    ################################################################
    if chatbox_id == "chatbox1":
        chat1_messages_HTML = utils.getMessagesHTML(chat1_messages[name], name)
        return jsonify({"messages": chat1_messages_HTML})
    elif chatbox_id == "chatbox2":
        chat2_messages_HTML = utils.getMessagesHTML(chat2_messages[name], name)
        return jsonify({"messages": chat2_messages_HTML})


if __name__ == "__main__":
    # Entry point to the application
    app.run(debug=False)
