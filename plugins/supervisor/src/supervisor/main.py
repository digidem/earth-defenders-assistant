#!/usr/bin/env python
import sys
from supervisor.crew import Supervisor


def run():
    """
    Run the crew for routing decision.
    """
    inputs = {"message": "I need to find grant opportunities for my research"}
    result = Supervisor().crew().kickoff(inputs=inputs)
    return result


def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {"message": "I need to find grant opportunities for my research"}
    try:
        Supervisor().crew().test(
            n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs
        )
    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")


if __name__ == "__main__":
    run()
