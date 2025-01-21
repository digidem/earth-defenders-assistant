import datetime
import os
from typing import List
from eda_config import ConfigLoader
from crewai import LLM, Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

# Get config
config = ConfigLoader.get_config()

# Initialize LLM using config
llm = LLM(
    model=config.ai_models["premium"].model,
    api_key=config.api_keys.groq,
    temperature=config.ai_models["premium"].temperature,
)


@CrewBase
class ProposalWriterCrew:
    """ProposalWriter crew with managed workflow for grant proposal development"""

    def __init__(self, community_project: str, grant_call: str):
        super().__init__()
        self.community_project = community_project
        self.grant_call = grant_call

    @agent
    def manager(self) -> Agent:
        return Agent(
            config=self.agents_config["manager"],
            verbose=True,
            allow_delegation=True,
            llm=llm,
        )

    @agent
    def outliner(self) -> Agent:
        return Agent(
            config=self.agents_config["outliner"],
            verbose=True,
            allow_delegation=True,
            llm=llm,
        )

    @agent
    def writer(self) -> Agent:
        return Agent(
            config=self.agents_config["writer"],
            verbose=True,
            allow_delegation=True,
            human_input_mode="ALWAYS",
            llm=llm,
        )

    @agent
    def quality_assurance(self) -> Agent:
        return Agent(
            config=self.agents_config["quality_assurance"],
            verbose=True,
            allow_delegation=True,
            human_input_mode="ALWAYS",
            llm=llm,
        )

    @task
    def create_outline_task(self) -> Task:
        return Task(
            config=self.tasks_config["create_outline_task"],
            context={
                "community_project": self.community_project,
                "grant_call": self.grant_call,
            },
        )

    @task
    def writing_task(self) -> Task:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return Task(
            config=self.tasks_config["writing_task"],
            context={
                "community_project": self.community_project,
                "grant_call": self.grant_call,
            },
            output_file=f"proposal_{timestamp}.md",
        )

    @task
    def qa_review_task(self) -> Task:
        return Task(
            config=self.tasks_config["qa_review_task"],
            context={
                "community_project": self.community_project,
                "grant_call": self.grant_call,
            },
        )

    @crew
    def crew(self) -> Crew:
        """Creates the ProposalWriter crew with hierarchical process managed by the manager agent"""
        return Crew(
            agents=[self.manager, self.outliner, self.writer, self.quality_assurance],
            tasks=[
                self.create_outline_task(),
                self.writing_task(),
                self.qa_review_task(),
            ],
            manager=self.manager,
            process=Process.hierarchical,
            verbose=True,
            memory=True,
            manager_llm=llm,
        )
