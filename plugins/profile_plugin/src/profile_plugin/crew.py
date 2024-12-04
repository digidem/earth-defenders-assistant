import os
from typing import Dict, Any
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool, ScrapeWebsiteTool

# Initialize tools
search_tool = SerperDevTool()
scrape_tool = ScrapeWebsiteTool()

# Configure LLM
llm = LLM(
    model="groq/llama3-groq-70b-8192-tool-use-preview",
    api_key=os.environ.get("GROQ_API_KEY"),
    temperature=0.5,
)

@CrewBase
class ProfileCrew:
    """Profile management crew"""
    
    def __init__(self, profile_data: Dict[str, Any] = None):
        super().__init__()
        self.profile_data = profile_data or {}

    @agent
    def profile_analyzer(self) -> Agent:
        return Agent(
            config=self.agents_config["profile_analyzer"],
            verbose=True,
            allow_delegation=True,
            llm=llm,
        )

    @agent
    def conversation_manager(self) -> Agent:
        return Agent(
            config=self.agents_config["conversation_manager"],
            verbose=True,
            allow_delegation=True,
            llm=llm,
        )

    @agent
    def data_quality(self) -> Agent:
        return Agent(
            config=self.agents_config["data_quality"],
            verbose=True,
            allow_delegation=True,
            tools=[search_tool, scrape_tool],
            llm=llm,
        )

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["researcher"],
            verbose=True,
            allow_delegation=True,
            tools=[search_tool, scrape_tool],
            llm=llm,
        )

    @agent
    def profile_builder(self) -> Agent:
        return Agent(
            config=self.agents_config["profile_builder"],
            verbose=True,
            allow_delegation=True,
            llm=llm,
        )

    @task
    def analyze_profile_task(self) -> Task:
        return Task(
            config=self.tasks_config["analyze_profile"],
            context={"profile_data": self.profile_data},
        )

    @task
    def manage_conversation_task(self) -> Task:
        return Task(
            config=self.tasks_config["manage_conversation"],
            context={"context": self.profile_data},
        )

    @task
    def validate_data_task(self) -> Task:
        return Task(
            config=self.tasks_config["validate_data"],
            context={"user_data": self.profile_data},
        )

    @task
    def research_information_task(self) -> Task:
        return Task(
            config=self.tasks_config["research_information"],
            context={"research_query": self.profile_data},
        )

    @task
    def build_profile_task(self) -> Task:
        return Task(
            config=self.tasks_config["build_profile"],
            context={"validated_data": self.profile_data},
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Profile management crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.hierarchical,
            manager=self.profile_analyzer,
            verbose=True,
            manager_llm=llm,
        )
