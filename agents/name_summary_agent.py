# Importing necessary libraries
from uagents import Agent, Context
from uagents.setup import fund_agent_if_low
from uagents import Model
from google.api_core import retry
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import json
import ast

class NameMessage(Model):
    message: str
    responseCode:int

class SummaryMessage(Model):
    summary: str
    responseCode:int

# Defining the user agent
Name_Summary_Agent = Agent(
    name="Name Summary Agent",
    port=8001,
    seed="Name Summary Agent secret phrase",
    endpoint=["http://localhost:8001/submit"],
)

# Funding the user agent if its wallet balance is low
fund_agent_if_low(Name_Summary_Agent.wallet.address())

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
    response = model.generate_content(f"""Generate a comprehensive summary of the movie {name}, ensuring to include all key aspects that contribute to the storyline's advancement and elements that viewers will appreciate. If you cannot recognize the movie send *MOVIE NOT FOUND* only and if multiple movies with the same name exist, provide a summary of the latest movie with that name. Format the output as a textual summary.""",stream=False,safety_settings={
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
        if(output.candidates[0].finish_reason==1):
            return (output.text,200)
        else:
            return (f"Cannot Summarise {message} because of our privacy policy issues. Thank You",400)
        
        
# Event handler for agent startup
@Name_Summary_Agent.on_event('startup')
async def address(ctx: Context):
    # Logging the agent's address
    ctx.logger.info(Name_Summary_Agent.address)

# Handler for query given by user
@Name_Summary_Agent.on_message(model=NameMessage)
async def handle_query_response(ctx: Context, sender: str, msg: NameMessage):
    # Handling the incoming message
    (summary,responseCode) = await handle_message(msg.message)

    # Logging the Request from the User Agent
    ctx.logger.info(summary)

    await ctx.send(sender, SummaryMessage(summary=summary,responseCode=responseCode))
    # Sending the response back to the sender
    