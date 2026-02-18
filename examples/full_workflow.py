"""
Example: Full Workflow Execution

Demonstrates running a complete orchestrator workflow with
Board review, agent execution, quality gates, and metrics.
"""

import asyncio
from src.core.orchestrator import ZNOrchestrator
from src.core.metrics import ImperiumMetrics
from src.core.memory import ImperiumMemory


async def main():
    # Initialize the orchestrator
    orchestrator = ZNOrchestrator()
    metrics = ImperiumMetrics()
    memory = ImperiumMemory()

    print("🚀 Starting Imperium Flow Workflow")
    print("=" * 50)

    # Define the workflow plan
    plan = [
        {
            "id": "t1",
            "agent_type": "code_worker",
            "description": "Implement user authentication module",
        },
        {
            "id": "t2",
            "agent_type": "test_worker",
            "description": "Write integration tests for auth module",
        },
        {
            "id": "t3",
            "agent_type": "integration_worker",
            "description": "Connect to OAuth2 provider",
        },
    ]

    # Execute the workflow
    context = await orchestrator.execute_workflow(
        name="auth-feature",
        goal="Implement secure user authentication with OAuth2",
        initial_plan=plan,
        quality_gates=["complexity", "security"],
        parallel=True,
    )

    # Print results
    print(f"\n📊 Workflow Results")
    print(f"   Name: {context.name}")
    print(f"   Status: {context.status}")
    print(f"   Duration: {context.duration_seconds:.2f}s")

    # Show metrics dashboard
    dashboard = metrics.get_dashboard()
    print(f"\n📈 Dashboard Overview")
    print(f"   Total Tasks: {dashboard.get('overview', {}).get('total_tasks', 0)}")
    print(f"   Success Rate: {dashboard.get('overview', {}).get('success_rate', 0):.1%}")

    # Show memory stats
    stats = memory.get_stats()
    print(f"\n🧠 Memory Stats")
    print(f"   Total Entries: {stats.get('total_entries', 0)}")
    print(f"   Agents: {stats.get('agents', [])}")


if __name__ == "__main__":
    asyncio.run(main())
