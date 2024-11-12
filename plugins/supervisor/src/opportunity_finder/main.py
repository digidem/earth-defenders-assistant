from supervisor.crew import SupervisorCrew


def run():
    """Run the supervisor crew"""
    crew = SupervisorCrew()
    result = crew.crew().kickoff(
        inputs={"message": "Find grant opportunities for AI projects"}
    )
    print(f"Decision: {result}")


if __name__ == "__main__":
    run()
