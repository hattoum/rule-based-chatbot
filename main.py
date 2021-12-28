from regexbot import Chatbot

chatbot = Chatbot("test_script.json")

conversation = ["Hello",
                "How much is the service going to cost me?",
                "Great! Can you help me subscribe?",
                "Okay thanks", 
                "Hey I forgot to say something",
                "How can I can unsubscribe later?",
                "Ah ok, thanks again"]

for message in conversation:
    chatbot.chat(message)
    

