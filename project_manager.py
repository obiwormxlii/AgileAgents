from dotenv import load_dotenv
import os
from google import genai
from pydantic import BaseModel
import json
from prompts import prompts


class PMdocument(BaseModel):
    text: str
    document_text: str
    confidence: float
    document_generated: bool

    def __getitem__(self, item):
        return getattr(self, item)


class ProjectManagerAgent:
    def __init__(self, api_key=None, model="gemini-2.0-flash"):
        """
        Initialize the Project Manager Agent

        Args:
            api_key (str, optional): Google API key. If None, loads from environment.
            model (str, optional): The model to use for generation. Defaults to "gemini-2.0-flash".
        """
        if api_key is None:
            load_dotenv()
            api_key = os.getenv("GOOGLE_API_KEY")

        if not api_key:
            raise ValueError(
                "API key is required. Set GOOGLE_API_KEY in environment or pass to constructor."
            )

        self.client = genai.Client(api_key=api_key)
        self.model = model
        self.context = []
        self.system_prompt = prompts["system"][
            "pm"
        ]  # Assuming there's a PM prompt in the prompts dictionary

    def process_prompt(self, user_prompt: str) -> PMdocument:
        """
        Process a user prompt and return the response as a PMdocument

        Args:
            user_prompt (str): The user's prompt or question

        Returns:
            PMdocument: The response document with text, document_text, confidence, and document_generated
        """
        current_context = {"user": user_prompt}

        # Add context to prompt if needed
        if self.context:
            formatted_prompt = f"<context>{self.context}</context>\n{user_prompt}"
        else:
            formatted_prompt = user_prompt

        # Generate response
        response = self.client.models.generate_content(
            model=self.model,
            contents=formatted_prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": PMdocument,
                "system_instruction": self.system_prompt,
            },
        )

        # Parse response and update context
        result = json.loads(response.text)
        current_context["agent"] = result["text"]
        self.context.append(current_context)

        return PMdocument(**result)

    def clear_context(self):
        """Clear the conversation context."""
        self.context = []

    def add_project_context(self, project_details):
        """
        Add project-specific context to the agent

        Args:
            project_details (dict): Dictionary containing project details like name,
                                    timeline, resources, etc.
        """
        self.project_context = project_details
        context_entry = {
            "user": "Project context information",
            "agent": "I've recorded the project details",
        }
        self.context.append(context_entry)

    def generate_sprint_plan(self, sprint_number, duration, team_capacity):
        """
        Generate a sprint plan based on project context

        Args:
            sprint_number (int): The sprint number
            duration (int): Duration of sprint in days
            team_capacity (int): Team capacity in story points

        Returns:
            PMdocument: The response document with the sprint plan
        """
        prompt = f"Generate a sprint plan for sprint {sprint_number} with duration of {duration} days and team capacity of {team_capacity} story points."
        return self.process_prompt(prompt)

    def generate_project_timeline(self, start_date, milestones=None):
        """
        Generate a project timeline based on start date and milestones

        Args:
            start_date (str): Project start date in YYYY-MM-DD format
            milestones (list, optional): List of project milestones

        Returns:
            PMdocument: The response document with the project timeline
        """
        prompt = f"Generate a project timeline starting from {start_date}"
        if milestones:
            prompt += f" with the following milestones: {', '.join(milestones)}"
        return self.process_prompt(prompt)

    def run_interactive_session(self):
        """Run an interactive session with the project manager agent."""
        generating_document = True

        while generating_document:
            if not self.context:
                user_input = "I need help planning my software development project with agile methodology."
            else:
                user_input = input("user: ")

            reply = self.process_prompt(user_input)

            if reply.document_generated:
                generating_document = False
                print("document generated")
                print(reply.text)
                print("\n")
                print(reply.document_text)
            else:
                print("agent: " + reply.text + "\n")


def main():
    """Example usage of the ProjectManagerAgent class."""
    agent = ProjectManagerAgent()
    agent.run_interactive_session()


if __name__ == "__main__":
    main()
