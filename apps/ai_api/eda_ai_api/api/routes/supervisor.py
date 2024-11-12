from fastapi import APIRouter
from eda_ai_api.models.supervisor import SupervisorRequest, SupervisorResponse
from crewai import Agent, Crew, Task, Process
from crewai.project import CrewBase, agent, crew, task
from opportunity_finder.crew import OpportunityFinderCrew
from crewai import LLM
import os

router = APIRouter()


# Use the same Cerebras LLM configuration as in OpportunityFinderCrew
cerebras_llm = LLM(
    model="sambanova/Meta-Llama-3.1-70B-Instruct",
    api_key=os.environ.get("SAMBANOVA_API_KEY"),
    # base_url="https://api.cerebras.ai/v1",
    temperature=0.5,
)


@CrewBase
class SupervisorCrew:
    @agent
    def decision_maker(self) -> Agent:
        return Agent(
            role="Decision Maker",
            goal="Analyze user requests and route them to appropriate endpoints",
            backstory="I am an AI supervisor that determines which endpoint to call based on user messages",
            allow_delegation=False,
            llm=cerebras_llm,  # Add explicit LLM configuration
        )

    @task
    def route_decision_task(self, message: str) -> Task:
        return Task(
            description=f"""
            Analyze this message: "{message}"
            Choose between these endpoints:
            1. discovery - For finding grant opportunities
            2. heartbeat - For checking system health
            
            Return only: "discovery" or "heartbeat"
            """,
            agent=self.decision_maker,
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.decision_maker],
            tasks=[self.route_decision_task],
            process=Process.sequential,
            verbose=True,
        )


@router.post("/supervisor", response_model=SupervisorResponse)
async def supervisor_route(request: SupervisorRequest) -> SupervisorResponse:
    supervisor = SupervisorCrew()
    decision = supervisor.crew().kickoff(inputs={"message": request.message})

    if decision.lower() == "discovery":
        topics = ["AI", "Technology"]  # Extract topics from message
        crew = OpportunityFinderCrew()
        result = crew.crew().kickoff(inputs={"topics": ", ".join(topics)})
    else:
        result = {"is_alive": True}

    return SupervisorResponse(result=str(result))
