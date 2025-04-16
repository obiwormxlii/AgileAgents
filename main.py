from pprint import pprint
import json
from datetime import datetime
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Field, Session, SQLModel, create_engine, select
from agent import Agent
from prompts import prompts


class Project(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str


class ChatMessage(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id")
    author: str
    message: str
    created_at: datetime = Field(default_factory=datetime.now)


class AIMessage(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    message_id: int = Field(foreign_key="chatmessage.id")
    document_created: bool = False


class AIRequest(SQLModel):
    project_id: int
    agent_name: str


class Document(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id")
    name: str
    text: str
    created_at: datetime = Field(default_factory=datetime.now)


class DBAgent(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    agent_name: str = Field(unique=True)
    system_prompt: str


def seed_agents():
    agent1 = DBAgent(
        agent_name="Business Analyst", system_prompt=prompts["Business Analyst"]
    )
    agent2 = DBAgent(agent_name="Scrum Master", system_prompt=prompts["Scrum Master"])
    agent3 = DBAgent(
        agent_name="Project Manager", system_prompt=prompts["Project Manager"]
    )
    agent4 = DBAgent(
        agent_name="Software Architect", system_prompt=prompts["Software Architect"]
    )
    agent5 = DBAgent(agent_name="Product Owner", system_prompt=prompts["Product Owner"])

    with Session(engine) as session:
        for agent in [agent1, agent2, agent3, agent4, agent5]:
            exitsts = session.exec(
                select(DBAgent).where(DBAgent.agent_name == agent.agent_name)
            ).first()
            if not exitsts:
                session.add(agent)
                session.commit()


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)
SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

seed_agents()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/projects")
async def get_projects(session: Session = Depends(get_session)):
    projects = session.exec(select(Project)).all()
    return projects


@app.post("/projects")
async def create_project(project: Project, session: Session = Depends(get_session)):
    session.add(project)
    session.commit()
    session.refresh(project)
    return project


@app.get("/agents")
async def get_agents(session: Session = Depends(get_session)):
    agents = session.exec(select(DBAgent)).all()
    return agents


@app.get("/projects/{project_id}/documents")
async def get_project_documents(
    project_id: int, session: Session = Depends(get_session)
):
    documents = session.exec(
        select(Document).order_by(Document.created_at.desc())
    ).all()
    return documents


@app.delete("/documents/{document_id}")
async def delete_document(document_id: int, session: Session = Depends(get_session)):
    document = session.exec(select(Document).where(Document.id == document_id)).one()
    session.delete(document)
    session.commit()
    return {"message": "Document deleted"}


@app.get("/messages")
async def get_messages(session: Session = Depends(get_session)):
    messages = session.exec(select(ChatMessage)).all()
    return messages


@app.post("/messages")
async def create_message(message: ChatMessage, session: Session = Depends(get_session)):
    session.add(message)
    session.commit()
    session.refresh(message)
    return message


@app.delete("/messages/{message_id}")
async def delete_message(message_id: int, session: Session = Depends(get_session)):
    message = session.exec(
        select(ChatMessage).where(ChatMessage.id == message_id)
    ).one()
    session.delete(message)
    session.commit()
    return {"message": "Message deleted"}


@app.post("/ai")
async def create_ai_message(
    ai_request: AIRequest, session: Session = Depends(get_session)
):

    try:
        project_docs_obj = session.exec(
            select(Document).where(Document.project_id == ai_request.project_id)
        ).all()
        project_docs_text = "\n".join([doc.text for doc in project_docs_obj])
    except Exception as e:
        print("error getting project docs", e)
        project_docs_text = ""

    try:
        messages_obj = session.exec(
            select(ChatMessage).where(ChatMessage.project_id == ai_request.project_id)
        ).all()

        messages_text = "\n".join(
            [msg.author + ": " + msg.message for msg in messages_obj]
        )

    except Exception as e:
        print("error getting messages", e)
        messages_text = ""

    try:
        agent_obj = session.exec(
            select(DBAgent).where(DBAgent.agent_name == ai_request.agent_name)
        ).one()
    except Exception as e:
        print("error getting agent", e)
        return {"error": "Agent not found", "status_code": 404}

    agent = Agent(project_context=messages_text, project_docs=project_docs_text)

    agent.system_prompt = agent_obj.system_prompt

    ai_response = agent.get_response()
    message = ChatMessage(
        author=ai_request.agent_name,
        message=ai_response["text"],
        project_id=ai_request.project_id,
    )

    if ai_response["document_generated"]:
        document = Document(
            name=ai_response["document_name"],
            text=ai_response["document_text"],
            project_id=ai_request.project_id,
        )
        session.add(document)
        session.commit()
        session.refresh(document)

    session.add(message)
    session.commit()
    session.refresh(message)

    ai_message = AIMessage(
        message_id=message.id, document_created=ai_response["document_generated"]
    )

    session.add(ai_message)
    session.commit()
    session.refresh(ai_message)
    return message
