from agents import Runner, AsyncOpenAI, OpenAIChatCompletionsModel, set_tracing_disabled, set_default_openai_client,function_tool, Agent,RunContextWrapper
import google.generativeai as genai
from dotenv import load_dotenv

import asyncio
import os


load_dotenv()  
gemini_api_key = os.getenv("GEMINI_API_KEY")
set_tracing_disabled(True)

external_client= AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/"
)

set_default_openai_client(external_client)

model=OpenAIChatCompletionsModel(
    model="models/gemini-2.0-flash",
    openai_client=external_client
)

from agents import (
    Runner,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    set_tracing_disabled,
    set_default_openai_client,
    function_tool,
    Agent,
    RunContextWrapper
)
import asyncio
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional, List

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

set_tracing_disabled(True)

external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/"
)
set_default_openai_client(external_client)

model = OpenAIChatCompletionsModel(
    model="models/gemini-2.0-flash",
    openai_client=external_client
)


inventory = [
    {"name": "lemon", "id": 1, "taste": "sour", "price": 5},
    {"name": "potato", "id": 2, "taste": "sweet", "price": 10},
    {"name": "tomato", "id": 3, "taste": "bitter", "price": 15}
]

@function_tool
async def deleter(item_name: str):
    """Delete an item from the inventory by its name."""
    global inventory
    inventory = [item for item in inventory if item["name"].lower() != item_name.lower()]
    return f'{item_name}: deleted \n remaining items: {inventory} '

@function_tool
async def updater(item_name: str, new_name: str = None, new_taste: str = None, new_price: float = None):
    """Update an item's details in the inventory."""
    for item in inventory:
        if item["name"].lower() == item_name.lower():
            if new_name:
                item["name"] = new_name
            if new_taste:
                item["taste"] = new_taste
            if new_price is not None:
                item["price"] = new_price
            return {"message": f"Item '{item_name}' updated.", "item": item}
    return {"error": f"Item '{item_name}' not found."}

@function_tool
async def view(item_name: str = None):
    """View the inventory or a specific item."""
    if item_name:
        for item in inventory:
            if item["name"].lower() == item_name.lower():
                return item
        return {"error": f"Item '{item_name}' not found."}
    return inventory

@function_tool
async def add_item(name: str, id: str, taste: str, price: str)-> str:
    "add new item in inventory"
    global inventory
    for item in inventory:
        if item["id"] == id or item["name"] == name.lower():
            return {"error": f"Item with name '{name}' or id '{id}' already exists."}           

    new_item = dict(name=name,id=id,taste=taste,price=price)
    inventory.append(new_item)

    return {
        "message": f"Item '{name}' added successfully.",
        "inventory": inventory
    }

@function_tool
async def view_all_items(items: str):
    global inventory
    for items in inventory:
        return inventory


agent = Agent(
    name="Inventory Agent",
    instructions="You help manage an inventory. You can delete, update, add or view items.if user wants help in terms of selecting taste price  you can choose ",
    model=model,
    tools=[view, updater, deleter, add_item, view_all_items]
)

async def main():
    while True:
        input_to_agent = input("ask your queries: ")  

        if input_to_agent.lower() == "exit":
            print("Thanks for asking, exiting agent...")
            break  

        result = await Runner.run(agent, input_to_agent)
        print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())