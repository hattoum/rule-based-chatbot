# Regexbot

Regexbot is a simple regex-based Python chatbot with state management. It takes a conversational flow in the form of a .json file and creates a chatbot with it.

## Conversational flow

The conversation flow includes the states of the chatbot and the intents. Each intent includes the regex patterns that match to the intent as well as the responses to use. The intents are matched in the order they are in in the json file.

```json
"name": "STATE_START",
"intents": {
    "hello_start": {
        "responses": [
            "Hello, can I help you with the subscriptions?",
            "Hi, do you have more questions?"
        ],
        "actions": [
            "set_state"
        ],
        "args": [
            "STATE_QUESTION"
        ]
},
"patterns": [
    "[A-z]",
    "[0-9]"
    ]
```

### Note
This is a practice project and still in progress
