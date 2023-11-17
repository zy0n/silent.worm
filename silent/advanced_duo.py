import time
from worm.utilities import *
from worm.sanitize import *


autogen.oai.completion.Completion.retry_wait_time = 60
# autogen.oai.completion.Completion.cache_path = "./memory/.cache" # cant get this to work...? fix with docker copy

set_sub_dir("advanced_duo_dir/")


default_termination_message = (
    lambda x: x.get("content", "").rstrip().endswith("TERMINATE")
)

llm_config = {
    "seed": sandbox_cache_seed,  # seed for caching and reproducibility
    "config_list": config_list,  # a list of OpenAI API configurations
    "temperature": 0,  # temperature for sampling
}


# UTILITY FUNCTIONS
def generate_task_assistant(
    name: str,
    professional_description: str,
    llm_config=llm_config,
    code_execution_config=None,
    function_map=None,
):
    assistant_prompt = get_assistant_prompt(professional_description)
    # print(assistant_prompt)

    assistant = autogen.AssistantAgent(
        name=name,
        llm_config=llm_config,
        system_message=assistant_prompt,
        code_execution_config=code_execution_config,
        function_map=function_map,
    )
    return assistant


func_update_group = {
    "name": "update_group",
    "description": "After adding a new agent, the group must be updated.",
    "parameters": {
        "type": "object",
        "properties": {},
        "required": [],
    },
}

asst_func_list = [
    func_text_to_image,
    func_text_to_speech,
    func_examine_image,
    func_save_to_file,
    func_search,
    func_scrape,
    func_advanced_search,
    func_create_directory,
    func_sanitize_url,
    func_sanitize_arXiv,
    func_format_for_markdown,
    func_summary,
]

spawn_boss_llm_config = {
    **llm_config,
    "request_timeout": 1000,
    "functions": asst_func_list,
}

spawn_asst_llm_config = {
    **llm_config,
    "request_timeout": 1000,
    "functions": asst_func_list,
}

default_func_map = {
    "search": web_search,
    "advanced_search": search_arXiv,
    "scrape": scrape,
    "save_to_file": save_to_file,
    "text_to_speech": text_to_audio,
    "examine_image": examine_image,
    "text_to_image": text_to_image,
    "create_directory": create_directory,
    "sanitize_url": sanitize_url,
    "sanitize_arXiv": sanitize_arXiv,
    "format_for_markdown": format_for_markdown,
    "summary": summary,
}


def spawn_task_expert(task):
    # an agent calls this function and passes in a task
    # spawn_boss determines what type of expert to create
    # spawn_boss has function to spawn agent
    # spawn_user calls that function given the responses from the spawn_boss?
    chat_conversation = {}
    autogen.ChatCompletion.start_logging(history_dict=chat_conversation, compact=True)
    spawn_boss = generate_task_assistant(
        name="Zer0-Cool",
        professional_description=AGENT_DUO_PROMPT,
        llm_config=spawn_boss_llm_config,
    )

    user_func_map = {
        **default_func_map,
    }
    spawn_user = autogen.UserProxyAgent(
        name="Lilith",
        max_consecutive_auto_reply=1,  # terminate without auto-reply
        human_input_mode="TERMINATE",
        function_map=user_func_map,
        code_execution_config={
            "work_dir": f"memory/{base_directory}",
            "use_docker": False,
            "last_n_messages": 3,
        },
        default_auto_reply="You are going to figure all out by your own. "
        "Work by yourself, the user won't reply until you output `TERMINATE` to end the conversation.",
    )
    spawn_user.initiate_chat(spawn_boss, message=task)
    return


def ask_an_expert(message):
    pass


init_user_input(spawn_task_expert)
