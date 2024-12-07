import os
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task

# Configure LLM
llm = LLM(
    model="groq/llama3-groq-70b-8192-tool-use-preview",
    api_key=os.environ.get("GROQ_API_KEY"),
    temperature=0.5,
)


@CrewBase
class ProfilePluginCrew:
    """Profile plugin crew"""

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
