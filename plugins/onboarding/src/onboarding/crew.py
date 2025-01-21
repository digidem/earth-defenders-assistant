import os
from eda_config import ConfigLoader
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task

# Get config
config = ConfigLoader.get_config()

# Configure LLM using config settings
llm = LLM(
    model=config.ai_models["premium"].model,
    api_key=config.api_keys.groq,
    temperature=config.ai_models["premium"].temperature,
)


@CrewBase
class OnboardingCrew:
    """Onboarding crew"""

    @agent
    def guide(self) -> Agent:
        return Agent(config=self.agents_config["guide"], verbose=True, llm=llm)

    @agent
    def translator(self) -> Agent:
        return Agent(config=self.agents_config["translator"], verbose=True, llm=llm)

    @task
    def explain_bot_features(self) -> Task:
        return Task(config=self.tasks_config["explain_bot_features"])

    @task
    def translate_guide(self) -> Task:
        return Task(config=self.tasks_config["translate_guide"])

    @crew
    def crew(self) -> Crew:
        """Creates the Onboarding crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,  # Ensures translation happens after guide creation
            verbose=True,
            manager_llm=llm,
        )
