import os
import datetime
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import ScrapeWebsiteTool, SerperDevTool
from langchain_openai import ChatOpenAI
search_tool = SerperDevTool()
scrape_tool = ScrapeWebsiteTool()
cerebras_llm = LLM(
    model="sambanova/Meta-Llama-3.1-70B-Instruct", # Replace with your chosen Cerebras model name, e.g., "cerebras/llama3.1-8b"
    api_key=os.environ.get("SAMBANOVA_API_KEY"), # Your Cerebras API key
    temperature=0.5,
    # Optional parameters:
    # top_p=1,
    # max_completion_tokens=8192, # Max tokens for the response
    # response_format={"type": "json_object"} # Ensures the response is in JSON format
)

# Uncomment the following line to use an example of a custom tool
# from opportunity_finder.tools.custom_tool import MyCustomTool

# Check our tools documentations for more information on how to use them
# from crewai_tools import SerperDevTool

# manager_llm = ChatOpenAI(model_name="gpt-4o-mini")
manager_llm = cerebras_llm
@CrewBase
class OpportunityFinderCrew():
	"""OpportunityFinder crew"""
	@agent
	def search_specialist(self) -> Agent:
		return Agent(
			config=self.agents_config['search_specialist'],
			verbose=True,
			allow_delegation=True,
			tools=[search_tool, scrape_tool],
			# llm=cerebras_llm
		)

	@agent
	def researcher(self) -> Agent:
		return Agent(
			config=self.agents_config['researcher'],
			tools=[search_tool, scrape_tool],
			verbose=True,
			allow_delegation=True,
   			# llm=cerebras_llm
		)

	@agent
	def reporting_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['reporting_analyst'],
   			tools=[search_tool, scrape_tool],
			verbose=True,
   			# llm=cerebras_llm
		)

	@task
	def search_terms_task(self) -> Task:
		return Task(
			config=self.tasks_config['search_terms_task'],
		)

	@task
	def research_task(self) -> Task:
		return Task(
			config=self.tasks_config['research_task'],
		)

	@task
	def reporting_task(self) -> Task:
		timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
		return Task(
			config=self.tasks_config['reporting_task'],
			output_file=f'report_{timestamp}.csv'
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the OpportunityFinder crew"""
		return Crew(
			agents=self.agents,
			tasks=self.tasks,
			process=Process.hierarchical,
			manager_llm=manager_llm,
			verbose=True,
			output_log_file=f'OpportunityFinderCrew_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
		)