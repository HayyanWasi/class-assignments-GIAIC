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

rental_cars = [
    {"Model": 2022, "brand": "Nissan", "Color": "Grey", "Price": 36, "Available": True},
    {"Model": 2023, "brand": "Toyota", "Color": "Red", "Price": 40, "Available": True},
    {"Model": 2022, "brand": "Honda", "Color": "Black", "Price": 35, "Available": True},
    {"Model": 2021, "brand": "Ford", "Color": "White", "Price": 38, "Available": True},
    {"Model": 2020, "brand": "Toyota", "Color": "Blue", "Price": 30, "Available": True},
    {"Model": 2023, "brand": "BMW", "Color": "Silver", "Price": 60, "Available": True},
    {"Model": 2021, "brand": "Hyundai", "Color": "Green", "Price": 33, "Available": False},
    {"Model": 2023, "brand": "Kia", "Color": "Red", "Price": 34, "Available": True},
    {"Model": 2020, "brand": "Mazda", "Color": "Blue", "Price": 32, "Available": False},
    {"Model": 2021, "brand": "Chevrolet", "Color": "Black", "Price": 37, "Available": True}
]
@function_tool(description_override="car data Returns all available cars with details like model, brand, color, and price.")
async def car_data(task: str):
    cars = rental_cars
    "help user give cars"
    available_cars = [cars for cars in rental_cars if cars["Available"] ]
    return available_cars

@function_tool(description_override="cars data return all available cars with in required price range")
async def price_range(min_price, max_price):
    "calculate the price range of cars and suggest the required price"
    avail=[]
    for cars in rental_cars:
        if cars["Price"] >= min_price and cars["Price"] <= max_price:
            avail.append(cars)
    return avail

@function_tool(description_override="cars data return all the available cars with required brands")
async def get_brand(brand: str):
    "find the car with brands"
    avail = [cars for cars in rental_cars if cars["brand"] == brand.capitalize()]
    return avail

@function_tool(description_override="cars data return all available cars with in required color")
async def get_color(color: str):
    "find the car of specified color"
    avail = [cars for cars in rental_cars if cars["Color"] == color.capitalize()]
    return avail

@function_tool(description_override="cars data return all the available cars")
async def avail_cars():
    "return all the available cars"
    available = [cars for cars in rental_cars if cars["Available"]]
    return available


rental_agent = Agent(
    name = "car agent",
    instructions=
    """
    your are an rental car agent
    what you do is 
    you check the rental_cars and according to user you bring available cars or not available cars to user
    if user ask for certain price range or certain brand you full fill their requirements
    you are user friendly model 
    """,
    model=model,
    tools=[car_data, price_range, get_brand, get_color, avail_cars]

)

agent = Agent(
    name = "customer support",
    instructions="""
    you are an customer support agent who deals with customer politely
    what you job is ?
   -If the user asks anything about cars, renting, car list, brands, prices, or availability, hand off the conversation to the rental agent immediately.
    -if customer want any other service you will apologizize that we donot have this service available 
     """,
    model=model,
    handoffs=[rental_agent]

)

async def main():
    result = await Runner.run(agent, "I want to see a list of available rental cars.")
    print(result.final_output)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())