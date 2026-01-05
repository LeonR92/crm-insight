from agent.agent import run_simple_360
from database import session

if __name__ == "__main__":

    final_data = run_simple_360(session, 3, 4)
    print(f"Executive Summary: {final_data.final_executive_summary}")

    if final_data.citations:
        print(f"Sample Citation URL: {final_data.citations[0].url}")
