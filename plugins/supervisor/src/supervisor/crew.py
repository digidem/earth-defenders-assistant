import datetime
import os
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task

cerebras_llm = LLM(
    model="sambanova/Meta-Llama-3.1-70B-Instruct",
    api_key=os.environ.get("SAMBANOVA_API_KEY"),
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
    def create_crew(self) -> Crew:
        """Creates the Supervisor crew"""
        return Crew(
            agents=[self.decision_maker()],
            tasks=[self.route_decision_task()],
            process=Process.sequential,
            verbose=True,
            output_log_file=f'SupervisorCrew_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
        )


__all__ = ["SupervisorCrew"]
