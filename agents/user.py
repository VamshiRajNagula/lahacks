# Importing necessary libraries from uagents package
from uagents import Agent, Context
from uagents.setup import fund_agent_if_low
from pypdf import PdfReader
from uagents import Model

class FileMessage(Model):
    message: str
    responseCode:int

class NameMessage(Model):
    message: str
    responseCode:int

# Defining a model for messages
class ResponseMessage(Model):
    message: str
    summary: str
    responseCode:int

class SummaryMessage(Model):
    summary: str
    responseCode:int

class PromptMessage(Model):
    message: str
    summary: str
    responseCode:int


# Specifying the address of the gemini ai agent
summary_agent = "agent1qvs5c92j90p43w67kaja3szrpmm0vw7yjzrsvdksdyrr5rjvm5h7wlwu2ll" # replace your Gemini API key here
prompt_agent = "agent1qw7cfvt5g6dedssn8hsrgpkghkhesqssvzdya0faj2rzzmudu3g4v4p5vze" # replace your Gemini API key here
gemini_agent = "agent1qwg20ukwk97t989h6kc8a3sev0lvaltxakmvvn3sqz9jdjw4wsuxqa45e8l" # replace your Gemini API key here
name_summary_agent = "agent1qfyv2kz69n84sakcpz8tlqcc9awy653fs6qa56pgc5ph6hxce6rrwnw4yn3" # replace your Gemini API key here

# Defining the user agent with specific configuration details
user = Agent(
    name="user",
    port=8000,
    seed="user secret phrase",
    endpoint=["http://localhost:8000/submit"],
)
 
# Checking and funding the user agent's wallet if its balance is low
fund_agent_if_low(user.wallet.address())
 
def read_text_from_file(filename):
    reader = PdfReader(filename) 

    # getting a specific page from the pdf file 
    text = "" 
    for page in reader.pages: 
        text+=page.extract_text() 

    return(text) 


# Event handler for the user agent's startup event
@user.on_event('startup')
async def agent_address(ctx: Context):
    # Logging the user agent's address
    ctx.logger.info(user.address)
    # Prompting for user input and sending it as a message to the gemini agent
    print("Select an option\n1.To Enter Movie Name\n2.To Upload Your Script pdf\n Anything else to exit")
    message = int(input('Your Option : '))
    if message==1:
        value = str(input('Enter a movie name : '))
        await ctx.send(name_summary_agent, NameMessage(message=value,responseCode=101))
    elif message==2:
        value = str(input('Enter the file : '))
        message = read_text_from_file(f"{value}.pdf")
        ctx.logger.info(f"Size of the contents of the file - {len(message)}")
        await ctx.send(summary_agent, FileMessage(message=message,responseCode=101))
    else:
        exit()
    


# Handler for receiving messages from gemini agent and sending new request
@user.on_message(model=SummaryMessage)
async def handle_query_response(ctx: Context, sender: str, msg: SummaryMessage):
    # Prompting for the next user input upon receiving a message
    if(msg.responseCode==200):
        await ctx.send(prompt_agent, PromptMessage(message="",summary=msg.summary,responseCode=101))
    elif(msg.responseCode==404):
        ctx.logger.info("User cancelled the transaction!")
    elif(msg.responseCode==400):
        ctx.logger.info(msg.summary)
    # Sending the user's message back to the sender (restaurant agent)


@user.on_message(model=PromptMessage)
async def handle_query_response(ctx: Context, sender: str, msg: PromptMessage):
    # Prompting for the next user input upon receiving a message
    # Sending the user's message back to the sender (restaurant agent)
    if(msg.responseCode==404):
        ctx.logger.info("I do not have necesarry information yet")
        return
    await ctx.send(gemini_agent, ResponseMessage(message=msg.message,summary=msg.summary,responseCode=101))

@user.on_message(model=ResponseMessage)
async def handle_query_response(ctx: Context, sender: str, msg: ResponseMessage):
    if(msg.responseCode==404):
        ctx.logger.info("I do not have necesarry information yet")
    ctx.logger.info(msg.message)
    ctx.logger.info("Have a good day!")
    print("Select an option\n1.To Enter Movie Name\n2.To Upload Your Script pdf\n Anything else to exit")
    message = int(input('Your Option : '))
    if message==1:
        value = str(input('Enter a movie name : '))
        await ctx.send(name_summary_agent, NameMessage(message=value,responseCode=101))
    elif message==2:
        value = str(input('Enter the file : '))
        message = read_text_from_file(f"{value}.pdf")
        ctx.logger.info(f"Size of the contents of the file - {len(message)}")
        await ctx.send(summary_agent, FileMessage(message=message,responseCode=101))
    else:
        exit()