import os
import datetime
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import ScrapeWebsiteTool, SerperDevTool

search_tool = SerperDevTool()
scrape_tool = ScrapeWebsiteTool()
model_name = "groq/llama-3.3-70b-versatile"
print(f"Using LLM model: {model_name}")

high_resource_model = "groq/llama-3.3-70b-versatile"
medium_resource_model = "groq/mixtral-8x7b-32768"
low_resource_model = "groq/llama-3.1-8b-instant"
high_resource_llm = LLM(
    model=high_resource_model,
    api_key=os.environ.get("GROQ_API_KEY"),
    temperature=0.5,
)

medium_resource_llm = LLM(
    model=medium_resource_model,
    api_key=os.environ.get("GROQ_API_KEY"),
    temperature=0.5,
)

low_resource_llm = LLM(
    model=low_resource_model,
    api_key=os.environ.get("GROQ_API_KEY"),
    temperature=0.5,
)
@CrewBase
class OpportunityFinderCrew:
    """OpportunityFinder crew"""
    def manager_agent(self) -> Agent:
        return Agent(
            role="Crew Manager",
            goal="""
            Manage the team to complete the task in the best way possible.
            """,
            backstory="""
            You are a seasoned manager with a knack for getting the best out of your team.\nYou are also known for your ability to delegate work to the right people, and to ask the right questions to get the best out of your team.\nEven though you don't perform tasks by yourself, you have a lot of experience in the field, which allows you to properly evaluate the work of your team members.

            Additional rules for Tools:
            -----------------
            1. Regarding the Action Input (the input to the action, just a simple python dictionary, enclosed
            in curly braces, using \" to wrap keys and values.)

            For example for the following schema:
            ```
            class ExampleToolInput(BaseModel):
                task: str = Field(..., description="The task to delegate")
                context: str = Field(..., description="The context for the task")
                coworker: str = Field(..., description="The role/name of the coworker to delegate to")
            ```
            Then the input should be a JSON object with the user ID:
            - task: The task to delegate
            - context: The context for the task
            - coworker: The role/name of the coworker to delegate to
            """,
        )

    @agent
    def search_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config["search_specialist"],
            verbose=True,
            allow_delegation=True,
            tools=[search_tool, scrape_tool],
            llm=low_resource_llm,
        )

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["researcher"],
            tools=[search_tool, scrape_tool],
            verbose=True,
            allow_delegation=True,
            llm=medium_resource_llm,
        )

    @agent
    def reporting_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["reporting_analyst"],
            tools=[search_tool, scrape_tool],
            verbose=True,
            llm=low_resource_llm,
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
            # manager_llm=llm,
            manager_agent=self.manager_agent(),
            max_rpm=30,
            verbose=True,
            output_log_file=f'OpportunityFinderCrew_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
        )
