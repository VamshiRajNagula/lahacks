# Importing necessary libraries
from uagents import Agent, Context
from uagents.setup import fund_agent_if_low
from uagents import Model
from google.api_core import retry
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import json
import ast

class PromptMessage(Model):
    message: str
    summary: str
    responseCode:int
    
# Defining the user agent
Prompt_agent = Agent(
    name="Prompt Agent",
    port=8001,
    seed="Prompt Agent secret phrase",
    endpoint=["http://localhost:8001/submit"],
)
 
# Funding the user agent if its wallet balance is low
fund_agent_if_low(Prompt_agent.wallet.address())

# Configuring the API key for Google's generative AI service
genai.configure(api_key='AIzaSyBHMyGQahgRV9IcexrWB3lNZJ0Sn1kZ0Hk') #replace your gemini API key here
    
# Initializing the generative model with a specific model name
model = genai.GenerativeModel('gemini-1.5-pro-latest',generation_config={"response_mime_type": "application/json"})
    
# Starting a new chat session
chat = model.start_chat(history=[])

async def generate_prompts(model, summary):
    response = model.generate_content(["""Given the provided summary, generate a set of prompts to create interesting yet smoothly transitionable plot twists. Ensure that the genre, characters' personalities, and story context remain unchanged. Output an array of prompts, each not exceeding 25 words.""",summary],stream=False,safety_settings={
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    })
    return response



# Function to handle incoming messages
async def handle_message(summary):
    # Get user input
    # Send the message to the chat session and receive a streamed response
    prompts = await generate_prompts(model,summary)
    if(prompts.candidates[0].finish_reason==1 or prompts.candidates[0].finish_reason=="STOP"):
        out = json.loads(prompts.text)
        for i in range(0,len(out)):
            print(f'Enter {i} for {out[i]}')
        while(True):
            index = int(input())
            if(index<len(out)):
                return(out[index],summary,200)
            else:
                print(f'Enter number between {0} and {len(out)}')
                continue
    return("",summary,404)
        
# Event handler for agent startup
@Prompt_agent.on_event('startup')
async def address(ctx: Context):
    # Logging the agent's address
    ctx.logger.info(Prompt_agent.address)

# Handler for query given by user
@Prompt_agent.on_message(model=PromptMessage)
async def handle_query_response(ctx: Context, sender: str, msg: PromptMessage):
    # Handling the incoming message
    (message,summary,responseCode) = await handle_message(msg.summary)
    # Logging the response
    ctx.logger.info(message)
    # Sending the response back to the sender
    await ctx.send(sender, PromptMessage(message=message,summary=summary,responseCode=responseCode))