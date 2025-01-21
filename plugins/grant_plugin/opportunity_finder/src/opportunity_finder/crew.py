import datetime
import os
from eda_config import ConfigLoader
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import ScrapeWebsiteTool, SerperDevTool

# Get config
config = ConfigLoader.get_config()

search_tool = SerperDevTool(api_key=config.api_keys.serper)
scrape_tool = ScrapeWebsiteTool()

llm = LLM(
    model=config.ai_models["premium"].model,
    api_key=config.api_keys.groq,
    temperature=config.ai_models["premium"].temperature,
)


@CrewBase
class OpportunityFinderCrew:
    """OpportunityFinder crew"""

    @agent
    def search_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config["search_specialist"],
            verbose=True,
            allow_delegation=True,
            tools=[search_tool, scrape_tool],
            llm=llm,
        )

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["researcher"],
            tools=[search_tool, scrape_tool],
            verbose=True,
            allow_delegation=True,
            llm=llm,
        )

    @agent
    def reporting_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["reporting_analyst"],
            tools=[search_tool, scrape_tool],
            verbose=True,
            llm=llm,
        )

    @task
    def search_terms_task(self) -> Task:
        return Task(
            config=self.tasks_config["search_terms_task"],
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config["research_task"],
        )

    @task
    def reporting_task(self) -> Task:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return Task(
            config=self.tasks_config["reporting_task"],
            output_file=f"report_{timestamp}.csv",
        )

    @crew
    def crew(self) -> Crew:
        """Creates the OpportunityFinder crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.hierarchical,
            manager_llm=llm,
            verbose=True,
            output_log_file=f'OpportunityFinderCrew_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
        )
