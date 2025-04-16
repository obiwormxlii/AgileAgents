from dotenv import load_dotenv
import os
from google import genai
from pydantic import BaseModel
import json
from enum import Enum
from pprint import pprint


class NextAction(Enum):
    ASK_QUESTION = "0"
    AGENT_RESPONSE = "1"
    END_CONVERSATION = "2"
    CONTINUE_SPEAKING = "3"


class DIRECT_QUESTION(Enum):
    NONE = "0"
    USER = "1"
    BUSINESS_ANALYST = "2"
    PROJECT_MANAGER = "3"
    SOFTWARE_ARCHITECT = "4"
    PRODUCT_OWNER = "5"
    SCRUM_MASTER = "6"


class Document(BaseModel):
    agent_name: str
    text: str
    document_text: str
    document_generated: bool
    document_name: str
    #    next_action: NextAction
    #    direct_question: DIRECT_QUESTION

    def __getitem__(self, item):
        return getattr(self, item)


def get_files_in_directory(directory):
    """
    Gets all files in a directory.

    Args:
      directory: The path to the directory.

    Returns:
      A list of file names in the directory.
    """
    files = [
        f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))
    ]
    return files


class Agent:
    output_file = ""

    def __init__(
        self,
        project_context="",
        project_docs="",
        api_key=None,
        model="gemini-2.0-flash",
    ):
        """
        Initialize the Agent

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
        self.project_docs = project_docs
        self.project_context = project_context

        self.context = {}
        self.system_prompt = ""

    def get_response(self, prompt="It's your turn to speak"):
        # self.project_context = self.read_context_doc()
        prompt = self.project_context + self.project_docs + prompt

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": Document,
                "system_instruction": self.system_prompt,
            },
        )

        result = json.loads(response.text)
        # self.update_context({"agent": result})
        # return self.process_reply(result)
        return result

    def question_user(self):
        user_response = input("user: ")
        self.update_context({"user": user_response})

    def process_reply(self, reply: Document):
        """Process a reply from the agent."""
        pprint(reply)
        if reply["document_generated"]:
            print("agent: " + reply["text"] + "\n")
            self.write_document(reply["document_name"], reply["document_text"])
        match reply["next_action"]:
            case NextAction.ASK_QUESTION.value:
                if reply["direct_question"] == DIRECT_QUESTION.USER.value:
                    print("agent: " + reply["text"] + "\n")
                    self.question_user()
                else:
                    print("agent: " + reply["text"] + "\n")
                    return reply
            case NextAction.AGENT_RESPONSE.value:
                print("agent: " + reply["text"] + "\n")
                return reply
            case NextAction.END_CONVERSATION.value:
                print("agent: " + reply["text"] + "\n")
                print(f"{reply['agent_name']} has ended their turn")
                return None

    def write_document(self, filename, content, relative_path="generated_documents"):
        """
        Creates a directory if it doesn't exist and writes content to a file.

            Args:
                relative_path (str): Relative directory path
                filename (str): Name of the file to write
                content (str): Content to write to the file

            Returns:
                str: Path to the created file
        """
        # Convert relative path to absolute path
        abs_path = os.path.abspath(relative_path)

        # Check if directory exists, create if it doesn't
        if not os.path.exists(abs_path):
            try:
                os.makedirs(abs_path)
                print(f"Directory created: {abs_path}")
            except OSError as e:
                raise OSError(f"Failed to create directory {abs_path}: {e}")

        # Create full file path
        file_path = os.path.join(abs_path, filename)

        # Write content to file
        try:
            with open(file_path, "w") as f:
                f.write(content)
            print(f"Content written to {file_path}")
        except IOError as e:
            raise IOError(f"Failed to write to file {file_path}: {e}")

    def get_project_context(self):
        """Get the full project context."""
        files = get_files_in_directory("./generated_documents")
        context = ""
        for file in files:
            with open(f"./generated_documents/{file}", "r") as f:
                context += f.read()
        return context

    def read_context_doc(self):
        """Read the context document."""
        if not os.path.exists("./generated_documents/" + "context.json"):
            with open("./generated_documents/" + "context.json", "w") as f:
                contents = json.dumps([])
                f.write(contents)
        with open("./generated_documents/" + "context.json", "r") as f:
            contents = f.read()
        return "<context>" + contents + "</context>"

    def update_context(self, new_context):
        """Update the context document."""
        with open("./generated_documents/" + "context.json", "r") as f:
            contents = f.read()
            if contents == "":
                contents = "[]"
            contents = json.loads(contents)

        contents.append(new_context)

        with open("./generated_documents/" + "context.json", "w") as f:
            f.write(json.dumps(contents))


def main():
    """Example usage of the Agent class."""
    agent = Agent()
    agent.get_response()


if __name__ == "__main__":
    #    main()
    print(NextAction.AGENT_RESPONSE.value)
