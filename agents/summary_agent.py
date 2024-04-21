# Importing necessary libraries
from uagents import Agent, Context
from uagents.setup import fund_agent_if_low
from uagents import Model
from google.api_core import retry
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import json
import ast

class FileMessage(Model):
    message: str
    responseCode:int

class SummaryMessage(Model):
    summary: str
    responseCode:int
    
# Defining the user agent
Summary_Agent = Agent(
    name="Summary Agent",
    port=8001,
    seed="Summary Agent secret phrase",
    endpoint=["http://localhost:8001/submit"],
)

# Funding the user agent if its wallet balance is low
fund_agent_if_low(Summary_Agent.wallet.address())

# Configuring the API key for Google's generative AI service
genai.configure(api_key='AIzaSyBHMyGQahgRV9IcexrWB3lNZJ0Sn1kZ0Hk') #replace your gemini API key here
    
# Initializing the generative model with a specific model name
model = genai.GenerativeModel('gemini-1.5-pro-latest')
    
# Starting a new chat session
chat = model.start_chat(history=[])

print("Chat session has started. Type 'quit' to exit.")


# async def generate_summary(model,name):
#     response = model.generate_content(["(Return NO SUMMARY AVAILABLE only if you don't know about the summary or response)Generate a brief summary of the movie", name],stream=False,safety_settings={
#         HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
#         HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
#     })
#     return response
async def generate_summary(model,name):
    response = model.generate_content(["""Generate a concise and accurate summary of the provided script. The summary should contain all crucial plot points necessary for making informed decisions and understanding the entire story.""", name],stream=False,safety_settings={
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    })
    return response

# Function to handle incoming messages
async def handle_message(message):
    # Get user input
    while True:
        # Check if the user wants to quit the conversation
        if message.lower() == 'quit'or message.lower=='exit':
            return(message,404)
            
        # Send the message to the chat session and receive a streamed response

        output = await generate_summary(model,message)
        print(output)
        try:
            if(output.candidates[0].finish_reason==1 or output.candidates[0].finish_reason=="STOP"):
                return (output.text,200)
            else:
                return ("Please Try Again with some other movie, because this restricts our policies",404)
        except ValueError:
            # If the response doesn't contain text, check if the prompt was blocked.
            print(output.prompt_feedback)
            # Also check the finish reason to see if the response was blocked.
            print(output.candidates[0].finish_reason)
            # If the finish reason was SAFETY, the safety ratings have more details.
            print(output.candidates[0].safety_ratings)
            return ("Please Try Again with some other movie, because this restricts our policies",404)
        
        
        # Initialize an empty string to accumulate the response text
        
# Event handler for agent startup
@Summary_Agent.on_event('startup')
async def address(ctx: Context):
    # Logging the agent's address
    ctx.logger.info(Summary_Agent.address)

# Handler for query given by user
@Summary_Agent.on_message(model=FileMessage)
async def handle_query_response(ctx: Context, sender: str, msg: FileMessage):
    # Handling the incoming message
    (message,responseCode) = await handle_message(msg.message)
    
    # Logging the response
    ctx.logger.info(message)
    await ctx.send(sender, SummaryMessage(summary=message,responseCode=responseCode))
    # Sending the response back to the sender
    