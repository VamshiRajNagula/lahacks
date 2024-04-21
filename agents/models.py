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