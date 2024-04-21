# Importing necessary libraries
from uagents import Agent, Context
from uagents.setup import fund_agent_if_low
from uagents import Model
from google.api_core import retry
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import json
import ast

class ResponseMessage(Model):
    message: str
    summary: str
    responseCode:int


# Defining the user agent
Gemini_agent = Agent(
    name="Gemini Agent",
    port=8001,
    seed="Gemini Agent secret phrase",
    endpoint=["http://localhost:8001/submit"],
)
 
# Funding the user agent if its wallet balance is low
fund_agent_if_low(Gemini_agent.wallet.address())

# Configuring the API key for Google's generative AI service
genai.configure(api_key='AIzaSyBHMyGQahgRV9IcexrWB3lNZJ0Sn1kZ0Hk') #replace your gemini API key here
    
# Initializing the generative model with a specific model name
model = genai.GenerativeModel('gemini-1.5-pro-latest')
    
# Starting a new chat session
chat = model.start_chat(history=[])

async def generate_with_retry(model, prompt,summary):
    response = model.generate_content(f"{summary} {prompt}", request_options={'retry':retry.Retry()},stream=False,safety_settings={
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    })
    return response
    



# Function to handle incoming messages
async def handle_message(message,summary):
    # Send the message to the chat session and receive a streamed response
    # response = chat.send_message(user_message, stream=True)
    answer = "Please Try Again with some other movie, because this restricts our policies"

    newPrompt = f"{message}, Rewrite the original story based on the provided summary and the 'what if' situation. Maintain the same characters, their personalities, the genre, and the story's context. Add suspense to create an entirely new plot without altering these key elements."
    s = await generate_with_retry(model,newPrompt,summary)
    if(s.candidates[0].finish_reason==1 or s.candidates[0].finish_reason=="STOP"):
        answer = "Gemini: " + s.text
        return (answer,200)
    else:
        return (answer,404)
        
# Event handler for agent startup
@Gemini_agent.on_event('startup')
async def address(ctx: Context):
    # Logging the agent's address
    ctx.logger.info(Gemini_agent.address)

# Handler for query given by user
@Gemini_agent.on_message(model=ResponseMessage)
async def handle_query_response(ctx: Context, sender: str, msg: ResponseMessage):
    # Handling the incoming message

    (message,responseCode) = await handle_message(msg.message,msg.summary)
    
    # Logging the response
    ctx.logger.info(message)
    
    # Sending the response back to the sender
    await ctx.send(sender, ResponseMessage(message=message,summary=msg.summary,responseCode=responseCode))