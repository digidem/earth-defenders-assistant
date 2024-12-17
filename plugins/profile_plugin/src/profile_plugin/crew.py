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
    
    def __init__(self, mock_profile: dict = None):
        self.mock_profile = mock_profile
        super().__init__()

    @agent
    def profile_analyzer(self) -> Agent:
        return Agent(config=self.agents_config["profile_analyzer"], verbose=True, llm=llm)
    
    @agent
    def conversation_flow(self) -> Agent:
        return Agent(config=self.agents_config["conversation_flow"], verbose=True, llm=llm)

    @agent
    def data_quality(self) -> Agent:
        return Agent(config=self.agents_config["data_quality"], verbose=True, llm=llm)

    @task
    def analyze_profile(self) -> Task:
        task_config = self.tasks_config["analyze_profile"]
        task_config["description"] = (
            f"Analyze this specific profile:\n{self.mock_profile}\n\n" 
            + task_config["description"]
        )
        return Task(
            config=task_config,
            input={"profile": self.mock_profile}
        )
    
    @task
    def start_conversation_flow(self) -> Task:
        task_config = self.tasks_config["start_conversation_flow"]

        return Task(
            config=task_config,
            human_input=True,
        )

    @task
    def validate_profile(self) -> Task:
        task_config = self.tasks_config["validate_profile"]
        return Task(
            config=task_config,
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            manager_llm=llm,
        )
