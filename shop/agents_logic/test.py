import tkinter as tk
from tkinter import filedialog
# from dataclasses import dataclass
import os
import asyncio
# from typing import Any
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, function_tool, set_tracing_disabled, AgentOutputSchema,RunContextWrapper,ModelSettings
# from django.shortcuts import render
# from pydantic import BaseModel
# from asgiref.sync import sync_to_async
from dotenv import load_dotenv
from pydantic import BaseModel
# from shop.models import Product

load_dotenv()  
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY not set.")

set_tracing_disabled(disabled=True)

# Global client and model (initialized once on import)
external_client: AsyncOpenAI = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

llm_model: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
    model="gemini-2.5-pro",
    openai_client=external_client
)

# Hide the main tkinter window
root = tk.Tk()
root.withdraw()

# Define allowed image types
IMAGE_TYPES = [("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif"), ("All Files", "*.*")]

# Variable to store the selected image path
selected_image_path = None
@function_tool
def select_image():
    """Open a file dialog to select an image and store its path."""
    global selected_image_path
    selected_image_path = filedialog.askopenfilename(
        title="Select an Image",
        filetypes=IMAGE_TYPES
    )
    if selected_image_path:
        print(f"✅ Image selected: {selected_image_path}")
        return selected_image_path

# Run the selection
class o_type(BaseModel):
    image_url:list[str]
    
agent = Agent(
    name="picture_selecter_agent",
    instructions="you are a picture selector agent just call your tool",
    tools=[select_image],
    # output_type=o_type,
    model=llm_model,
    model_settings=ModelSettings(tool_choice="select_image") 
)
agent1 = Agent(
    name="picture_selecter_agent",
    instructions="you are output management agent ,use your output_type tool for structure output , don't give user output by your self just use user_input and convert it in structure output",
    # tools=[select_image],
    output_type=o_type,
    model=llm_model,
    # model_settings=ModelSettings(tool_choice="select_image") 
)
async def main():
    print("🎙️ Ask the agent to help you pick an image.")
    result = await Runner.run(
        agent,
        input="Please help me choose an image from my computer."
    )
    result1 = await Runner.run(agent1,result.final_output)
    print("\n💬 Final Output:", result1.final_output)
    print(result1.final_output.image_url)

if __name__ == "__main__":
    asyncio.run(main())