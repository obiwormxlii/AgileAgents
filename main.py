from datetime import datetime
from fastapi import FastAPI, Depends
from sqlmodel import Field, Session, SQLModel, create_engine, select


class Project(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str


class ChatMessage(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id")
    message: str
    created_at: datetime = Field(default_factory=datetime.now)


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)
SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


app = FastAPI()


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
