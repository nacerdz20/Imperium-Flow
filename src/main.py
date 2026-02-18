#!/usr/bin/env python3
"""
Zouaizia Nacer Orchestrator - Main Entry Point
starts the orchestrator and all workers.
"""

import logging
from conductor.client.automator.task_handler import TaskHandler
from conductor.client.configuration.configuration import Configuration

from src.core.orchestrator import ZNOrchestrator
from src.integrations.conductor_client import ConductorClient
from src.integrations.conductor_worker import ConductorWorker
from src.agents.worker import WorkerAgent
from src.config.worker_templates import CODE_WORKER, TEST_WORKER, UI_WORKER

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Main")

def main():
    logger.info("🚀 Starting Zouaizia Nacer Orchestrator...")
    
    # 0. Configuration
    base_url = "http://localhost:8080/api"
    config = Configuration(base_url=base_url)
    
    # 1. Initialize Agents
    logger.info("🤖 Initializing AI Agents...")
    code_agent = WorkerAgent("SeniorDev", CODE_WORKER)
    test_agent = WorkerAgent("QAEngineer", TEST_WORKER)
    ui_agent = WorkerAgent("FrontendDev", UI_WORKER)

    # 2. Initialize Conductor Workers (The Bridge)
    logger.info("👷 Registering Workers at Conductor...")
    
    workers = [
        ConductorWorker("code_task", code_agent, poll_interval=1.0),
        ConductorWorker("test_task", test_agent, poll_interval=1.0),
        ConductorWorker("ui_task", ui_agent, poll_interval=1.0)
    ]
    
    # 3. Start Polling Loop
    logger.info(f"🔌 Connecting to Conductor at {base_url}")
    logger.info("🌀 Starting Task Handler (Polling)...")
    
    try:
        with TaskHandler(workers, configuration=config) as task_handler:
            task_handler.start_processes()
            logger.info("✅ System Active. Press Ctrl+C to stop.")
            # Keep main thread alive
            import time
            while True:
                time.sleep(1)
                
    except Exception as e:
        logger.error(f"❌ System Error: {e}")
        # If connection fails, we might want to run in a localized fallback mode,
        # but for Phase 8, we expect Conductor to be running.
        logger.info("ℹ️ Is Conductor Server running? (docker-compose up)")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("🛑 System Stopping...")
