import os
from dotenv import load_dotenv
import openai
import autogen

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")


def is_running_in_docker():
    return os.environ["PWD"] == "/home/worm-playground"


def get_base_dir():
    if is_running_in_docker():
        return "memory/"
    return "./"


# api_model = "gpt-4"  # "gpt-4-1106-preview"
api_model = "gpt-4-1106-preview"
config_list = [{"api_key": api_key, "model": api_model}]

openai.api_key = api_key
OAI_IMAGE_GENERATION_URL = "https://api.openai.com/v1/images/generations"
