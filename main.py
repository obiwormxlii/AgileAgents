from prompts import prompts
from agent import Agent


class BusinessAnalystAgent(Agent):
    def __init__(self, api_key=None, model="gemini-2.0-flash"):
        super().__init__(api_key, model)
        self.system_prompt = prompts["ba"]


class ProjectManagerAgent(Agent):
    def __init__(self, api_key=None, model="gemini-2.0-flash"):
        super().__init__(api_key, model)
        self.system_prompt = prompts["pm"]


class SoftwareArchitectAgent(Agent):
    def __init__(self, api_key=None, model="gemini-2.0-flash"):
        super().__init__(api_key, model)
        self.system_prompt = prompts["architect"]


class ProductOwner(Agent):
    def __init__(self, api_key=None, model="gemini-2.0-flash"):
        super().__init__(api_key, model)
        self.system_prompt = prompts["product_owner"]


class ScrumMaster(Agent):
    def __init__(self, api_key=None, model="gemini-2.0-flash"):
        super().__init__(api_key, model)
        self.system_prompt = prompts["scrum_master"]


agents = {
    "business_analyst_agent": BusinessAnalystAgent(),
    "project_manager_agent": ProjectManagerAgent(),
    "software_architect_agent": SoftwareArchitectAgent(),
    "product_owner_agent": ProductOwner(),
    "scrum_master_agent": ScrumMaster(),
}


def get_agent_response(agent, prompt=None):
    if prompt is not None:
        response = agent.get_response(prompt)
    else:
        response = agent.get_response()
    if response is None:
        return
    if response["next_action"] == 0:
        match response["direct_question"]:
            case 2:
                get_agent_response(agents["business_analyst_agent"])
            case 3:
                get_agent_response(agents["project_manager_agent"])
            case 4:
                get_agent_response(agents["software_architect_agent"])
            case 5:
                get_agent_response(agents["product_owner_agent"])
            case 6:
                get_agent_response(agents["scrum_master_agent"])
            case _:
                get_agent_response(agents["project_manager_agent"])


def main():

    while True:
        for agent in agents.values():
            agent.get_response()


if __name__ == "__main__":
    main()
