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


def generate_code_agent():
    return generate_task_assistant("EXPERT_Agent_Coder", CODE_PLANNER_AGENT)


# AGENT DEFINITIONS
code_agent = generate_code_agent()
code_manager = autogen.UserProxyAgent(
    name="Code_Manager",
    max_consecutive_auto_reply=10,  # terminate without auto-reply
    human_input_mode="NEVER",
    code_execution_config={"work_dir": "memory/agency", "use_docker": False},
)

func_ask_the_coder = {
    "name": "ask_code_manager",
    "description": "is used to implore the assistance of a professional developer for a task, Make sure to have all imports installed prior to attempting to run any code.",
    "parameters": {
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": "When formulating a question for the planner, provide comprehensive context. This should include the specific code that was used, the results or output from executing that code, and any relevant details from your interaction with the user that may impact the planner's understanding or response. The planner does not have access to previous exchanges between you and the user, so it is crucial to include all pertinent information in your query to ensure an informed and accurate assistance from the planner.",
            },
        },
        "required": ["message"],
    },
}
boss_llm_config = {
    **llm_config,
    "request_timeout": 1000,
    "functions": [func_ask_the_coder],
}


def ask_the_coder(message):
    code_manager.initiate_chat(code_agent, message=message)
    # return the last message received from the planner
    return code_manager.last_message()["content"]


func_spawn_agent = {
    "name": "spawn_agent",
    "description": "Generate agent specifications based on task requirements.",
    "parameters": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Specify agent name as KNOWLEDGE_Profession(e.g., EXPERT_Python_Developer) it must supply a match to this regex expression ^[a-zA-Z0-9_-]{1,64}",
            },
            "professional_description": {
                "type": "string",
                "description": """Describe a single task to accomplish based on the desired profession. 
                They will report back once the task is complete.
                Provide an input in the REQUIRED_FORMAT
                
                REQUIRED_FORMAT:
                Function: - Describe a single task to accomplish based on the desired profession. 
                Input Requirements: - Things they may need to accomplish their task. 
                Expected Output: - What the output result of them completing their task should be. If they are generating reports, it will be the reports. If it is images, it will be descriptions of expected images. etc...
                """,
            },
        },
        "required": ["name", "professional_description"],
    },
}

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
    func_spawn_agent,
    func_ask_the_coder,
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

assistant_swarm = []


def update_swarm():
    if groupchat is not None:
        print("Updating GroupChat")
        groupchat.agents = assistant_swarm
    return "GROUP UPDATED"


default_func_map = {
    "ask_code_manager": ask_the_coder,
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
}


groupchat = None


def spawn_task_expert(task):
    # an agent calls this function and passes in a task
    # spawn_boss determines what type of expert to create
    # spawn_boss has function to spawn agent
    # spawn_user calls that function given the responses from the spawn_boss?
    global groupchat
    chat_conversation = {}
    autogen.ChatCompletion.start_logging(history_dict=chat_conversation, compact=True)
    spawn_boss = generate_task_assistant(
        name="Agent_Architect",
        professional_description=CODE_PLANNER_AGENT,
        llm_config=spawn_boss_llm_config,
    )

    user_func_map = {
        **default_func_map,
    }
    print(user_func_map)
    spawn_user = autogen.UserProxyAgent(
        name="Lilith",
        max_consecutive_auto_reply=1,  # terminate without auto-reply
        human_input_mode="TERMINATE",
        function_map=user_func_map,
        code_execution_config={
            "work_dir": "memory/coding",
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
