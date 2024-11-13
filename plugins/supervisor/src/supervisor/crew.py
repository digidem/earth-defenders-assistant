import datetime
import os
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task

cerebras_llm = LLM(
    model="cerebras/llama3.1-70b",
    api_key=os.environ.get("CEREBRAS_API_KEY"),
    base_url="https://api.cerebras.ai/v1",
    temperature=0.5,
)

@CrewBase
class SupervisorCrew:
    """Supervisor crew"""
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def decision_maker(self) -> Agent:
        return Agent(
            config=self.agents_config["decision_maker"],
            verbose=True,
            allow_delegation=False,
            llm=cerebras_llm,
        )

    @task 
    def route_decision_task(self) -> Task:
        return Task(config=self.tasks_config["route_decision_task"])

    @crew
    def crew(self) -> Crew:
        """Creates the Supervisor crew"""
        return Crew(
            agents=[self.decision_maker],
            tasks=[self.route_decision_task], 
            process=Process.sequential,
            verbose=True,
            output_log_file=f'SupervisorCrew_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        )

__all__ = ["SupervisorCrew"]