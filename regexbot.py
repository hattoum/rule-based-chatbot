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
        self.state.respond(message)

#The base state for actions
class Action:
    def __init__(self, parent, action, args):
        self.action = action
        self.args = args
        self.parent = parent

        self.actions = {
            "set_state": self.set_state,
            "set_entity": self.set_entity,
            "say": self.say,
            "goto_intent": self.goto_intent
        }
    
    #Performs the action with the args    
    def run(self):
        self.actions[self.action](self.args)
         
    def set_state(self,x):
        self.parent.set_state(x)
        
    def set_entity(self,x):
        self.parent.set_entity(x[0],x[1])
        
    def say(self,x):
        self.parent.say()
        
    def goto_intent(self,x):
        self.parent.goto_intent(x)

#The base State object
class State:
    def __init__(self, parent, state_dict):
        #Changes all args and actions to list
        self.state_dict = state_dict
        
        #Gets a list of tuples of all (pattern,intent)
        self.patterns = self.get_patterns()
        
        #State name and name of default state formatted as "default_"+state name
        self.name = self.state_dict["name"]
        self.default = ("default_"+self.name.split("_")[1]).lower()
        
        #Parent Chatbot object
        self.parent = parent
        
        #houses a list of all (dict)intents in the State
        self.intents = self.get_intents()
        
        #A list of Action objects to be run sequentially 
        self.action_queue = []
        
        #Holds current intent temporarily
        self.current_intent = None
          
    #Matches regex and returns the first matched intent
    def find_match(self,text):
        for pattern in self.patterns:
            p = re.compile(pattern[0])
            if(p.search(text)):
                    return pattern[1]
                
        return self.default
    
    #returns a list of all intent dicts in the state
    def get_intents(self):
        return [item for item in self.state_dict["intents"]]
    
    #returns a list of list
    def get_patterns(self):
        return  [pattern.split(":") for pattern in self.state_dict["patterns"] ]
    
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
    def respond(self,text=None, intent_name = None):
        if(text):
            intent_name = self.find_match(text)
            print("User: ", text)
        
        self.current_intent = intent_name    
        self.get_actions(self.current_intent)
        self.run_actions()
        self.current_intent = None
        
    def goto_intent(self, intent_name):
        self.action_queue.pop(0)
        self.respond(intent_name=intent_name)
    
    #Print current response    
    def say(self):
        print("Regexbot: ", self.get_response())
        
    #Returns string response and cycles through responses   
    def get_response(self):
        current_response = self.parent.intent_counts[self.current_intent]
        
        self.parent.intent_counts[self.current_intent] += 1
        if(current_response == len(self.get_intent(self.current_intent)["responses"])):
            current_response = 0
            self.parent.intent_counts[self.current_intent] = 0

        return self.get_intent(self.current_intent)["responses"][current_response]
    
    #Loads all the actions in an intent
    def get_actions(self,intent_name):
        intent = self.get_intent(intent_name)
        if "actions" in intent:
            for index in range(len(intent["actions"])):
                self.action_queue.append(Action(self,intent["actions"][index],intent["args"][index]))
    
    #Runs all actions in action_queue
    def run_actions(self):
        while bool(self.action_queue):
            self.action_queue[0].run()
            
            #The try block prevents an out of range error if goto_intent runs a second instance of run_actions and empties the queue before the first finishes
            try:
                self.action_queue.pop(0)
            except:
                pass