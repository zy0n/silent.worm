from worm.utilities import *

from worm.team_group import *

set_sub_dir("team_dir")

llm_config = {
    "seed": 42,  # seed for caching and reproducibility
    "config_list": config_list,  # a list of OpenAI API configurations
    "temperature": 0,  # temperature for sampling
    "timeout": 120,
    "use_cache": True,
}

# Initialization
# f"List of fruits: {', '.join(fruit for fruit in [])}"
# result_string = f"List of fruits: {', '.join(f'{fruit.name} (Color: {fruit.color})' for fruit in [])}"

all_team_leaders = ["A1", "B1", "C1"]
all_team_members = [["A2", "A3", "A4", "A5"], ["B2", "B3", "B4"], ["C2", "C3", "C4"]]


team_agents = generate_all_teams(all_team_leaders, all_team_members)

# Accessing the array of AssistantAgent instances for Team A
team_a_agents = team_agents[0]

# for team in team_agents:
#     for agent in team:
#         print(agent.system_message)
# exit(0)
agents_A = team_agents[0]

agents_B = team_agents[1]

agents_C = team_agents[2]


def run_turbo_group(message):
    # Terminates the conversation when TERMINATE is detected.
    user_proxy = autogen.UserProxyAgent(
        name="User_proxy",
        system_message="Terminator admin.",
        code_execution_config=False,
        is_termination_msg=is_termination_msg,
        human_input_mode="NEVER",
    )

    list_of_agents = agents_A + agents_B + agents_C
    list_of_agents.append(user_proxy)

    # Create CustomGroupChat
    group_chat = CustomGroupChat(
        agents=list_of_agents,  # Include all agents
        messages=[
            'Everyone cooperate and complete the task(s). Team A has A1, A2, A3. Team B has B1, B2. etc... Only members of the same team can talk to one another. Only team leaders (names ending with 1) can talk amongst themselves. Team leaders will delegate out who needs to do what, and who has what skills. You must use "NEXT: B1" to suggest talking to B1 for example; You can suggest only one person, you cannot suggest yourself or the previous speaker; You can also dont suggest anyone.'
        ],
        max_round=30,
    )

    # Create the manager
    turbo_llm_config = {
        "config_list": config_list,
        "cache_seed": None,
    }  # cache_seed is None because we want to observe if there is any communication pattern difference if we reran the group chat.
    turbo_manager = LimitedGroupChatManager(
        groupchat=group_chat, llm_config=turbo_llm_config
    )

    # Initiates the chat with B2
    agents_A[0].initiate_chat(
        turbo_manager,
        message=message,
    )


init_user_input(run_turbo_group)
# input_msg = input("Enter a Task: ")
# run_turbo_group(input_msg)
