import re
import json

class Chatbot:
    def __init__(self,script,entities=None):
        self.script = script
        self.entities = entities
        self.states=self.get_states() # dict of all states
        self.state=self.states["STATE_START"] # Holds the current state
        self.entities=self.get_starting_entities() 
        self.intent_counts=self.get_counts() # Holds the count of each intent for cycling responses
        

    #returns a dict of all State objects
    def get_states(self):
        file = open(self.script)
        script = json.load(file)
        states = {}

        for state in script["states"]:
            states[state["name"]] = State(self,state)
            
        return states
    
    #returns a dict of entities from input file
    def get_starting_entities(self):
        if self.entities:
            file = open(self.entities)
            return json.load(file)

    #returns a dict of all intents as keys and their initial value as 0
    def get_counts(self):
        intents_nested = [obj.intents for obj in [self.states[state] for state in self.states]]
        
        #Flattening out the list of lists and creating a dict comprehension 
        all_intents = {el:0 for el in[intent for sublist in intents_nested for intent in sublist]}
        return dict(all_intents)
    
    #sets current state
    def set_state(self,state_name):
        self.state=self.states[state_name]
    
    #set entity to value
    def set_entity(self,entity_name,value):
        self.entities[entity_name]=value
    
    #Takes message from user and returns a string response
    #Communicates with the current State object
    def chat(self,message):
        message_formatted = message.lower()
        print("User: ", message)
        print("Regexbot: ", self.state.respond(message_formatted))
#         return self.state.respond(message)


#The base State object
class State:
    def __init__(self, parent, state_dict):
        #Changes all args and actions to list
        self.state_dict = state_dict
        
        #State name and name of default state formatted as "default_"+state name
        self.name = self.state_dict["name"]
        self.default = ("default_"+self.name.split("_")[1]).lower()
        
        #Parent Chatbot object
        self.parent = parent
        
        #houses a list of all (dict)intents in the State
        self.intents = self.get_intents()
          
    #Matches regex and returns the first matched intent
    def find_match(self,text):
        for intent_name in self.intents:
            for pattern in self.state_dict["intents"][intent_name]["patterns"]:
                p = re.compile(pattern)
                if(p.search(text)):
                    return intent_name
                
        return self.default
    
    #returns a list of all intent dicts in the state
    def get_intents(self):
        return [item for item in self.state_dict["intents"]]
    
    #sets state in parent to 
    def set_state(self,state_name):
        self.parent.set_state(state_name)
    
    #sets entity in parent
    def set_entity(self,entity_name,value):
        self.parent.set_entity(entity_name,value)
    
    #returns intent dict from intent name
    def get_intent(self,intent_name):
        return self.state_dict["intents"][intent_name]
    
    #Runs actions
    def respond(self,text=None,intent_name=None):
        if(text):
            intent_name = self.find_match(text)
        response = self.get_response(intent_name)
        
        intent = self.get_intent(intent_name)
        #Logic for handling the action and args
        actions = {
            "set_state": lambda x: self.set_state(x),
            "set_entity": lambda x: self.set_entity(x[0],x[1]),
            "say": lambda x: self.get_response(intent_name=x)
        }
        if "actions" in intent:
            for index in range(len(intent["actions"])):
                actions[intent["actions"][index]](intent["args"][index])
        
        return(response)
        
    #Returns string response and cycles through responses   
    def get_response(self,intent_name):
        intent = self.get_intent(intent_name)
        current_response = self.parent.intent_counts[intent_name]
        
        self.parent.intent_counts[intent_name] += 1
        if(current_response == len(intent["responses"])):
            current_response = 0
            self.parent.intent_counts[intent_name] = 0
    

        return intent["responses"][current_response]
        