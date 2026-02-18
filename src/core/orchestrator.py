#!/usr/bin/env python3
"""
Imperium Flow - Core Orchestration Engine
Multi-Agent Orchestration System with Board Oversight,
Imperium Protocol, Shared Memory, and Performance Metrics.
"""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

from .workflow_engine import WorkflowEngine
from .agent_manager import AgentManager
from .quality_gates import QualityGateManager
from .protocol import MessageBus, ImperiumMessage, AgentType, IntentType, Priority
from .memory import ImperiumMemory
from .metrics import ImperiumMetrics


class WorkflowStatus(Enum):
    PENDING = "pending"
    PLANNING = "planning"
    EXECUTING = "executing"
    QUALITY_CHECK = "quality_check"
    COMPLETED = "completed"
    FAILED = "failed"
    ABORTED = "aborted"


@dataclass
class WorkflowContext:
    """سياق سير العمل"""
    workflow_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    status: WorkflowStatus = WorkflowStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    agents_involved: List[str] = field(default_factory=list)
    results: Dict[str, Any] = field(default_factory=dict)
    quality_report: Optional[Dict] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class ZNOrchestrator:
    """
    Imperium Flow - Core Orchestration Engine.
    
    Manages:
    - Task distribution to agents
    - Parallel execution with DAG scheduling
    - Quality gates enforcement
    - Board of Directors oversight
    - Inter-agent communication (Imperium Protocol)
    - Shared knowledge (Imperium Memory)
    - Performance tracking (Imperium Metrics)
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.logger = logging.getLogger("ImperiumFlow")
        
        # Core Systems
        self.workflow_engine = WorkflowEngine()
        self.agent_manager = AgentManager()
        self.quality_manager = QualityGateManager()
        
        # Imperium Systems
        self.message_bus = MessageBus()
        self.memory = ImperiumMemory(
            persistence_path=self.config.get("memory_path", ".imperium/memory.json")
        )
        self.metrics = ImperiumMetrics()
        
        # Board of Directors
        from src.board.directors import BoardOfDirectors, WorkflowProposal
        self.board = BoardOfDirectors()
        
        self.active_workflows: Dict[str, WorkflowContext] = {}
        self.max_parallel_agents = 5
        
        self.logger.info("🚀 Imperium Flow Engine initialized")
    
    async def execute_workflow(
        self, 
        name: str, 
        goal: str,
        initial_plan: Optional[List[Dict]] = None,
        parallel: bool = True,
        quality_gates: Optional[List[str]] = None,
        require_board_approval: bool = False
    ) -> WorkflowContext:
        """
        تنفيذ سير عمل كامل مع Smart Loop (Plan -> Execute -> Fail -> Fix -> Retry)
        """
        # إنشاء السياق
        context = WorkflowContext(name=name)
        self.active_workflows[context.workflow_id] = context
        
        # Superpowers
        from src.superpowers.planning import SmartPlanner
        from src.superpowers.debugging import SystematicDebugger
        
        planner = SmartPlanner()
        debugger = SystematicDebugger()
        
        try:
            # Phase 1: Planning
            self.logger.info(f"🧠 Planning workflow for goal: {goal}")
            tasks = initial_plan or planner.create_plan(goal)
            await self._phase_planning(context, tasks)
            
            # Board Approval
            if require_board_approval:
                approved = await self._request_board_approval(context)
                if not approved:
                    context.status = WorkflowStatus.ABORTED
                    return context
            
            # Phase 2: Evaluation Loop execution (DAG)
            context.status = WorkflowStatus.EXECUTING
            completed_task_ids = set()
            max_retries = 3
            
            while not self.workflow_engine.is_workflow_complete(tasks, completed_task_ids):
                # Get ready tasks (DAG)
                ready_tasks = self.workflow_engine.get_ready_tasks(tasks, completed_task_ids)
                
                if not ready_tasks:
                    if not self.workflow_engine.is_workflow_complete(tasks, completed_task_ids):
                         self.logger.error("❌ Deadlock detected: unfinished tasks but no ready tasks.")
                         context.status = WorkflowStatus.FAILED
                         break
                
                self.logger.info(f"⚡ Executing batch: {[t['id'] for t in ready_tasks]}")
                
                # Execute in parallel
                results = await self._execute_batch(ready_tasks)
                
                for task, result in zip(ready_tasks, results):
                    task_id = task["id"]
                    
                    if isinstance(result, Exception) or (isinstance(result, dict) and result.get("status") == "failed"):
                        # Failure handling -> Debugging Loop
                        self.logger.warning(f"⚠️ Task {task_id} failed. Entering Debug Loop.")
                        
                        fix_attempt = 0
                        fixed = False
                        current_error = str(result)
                        
                        while fix_attempt < max_retries:
                            fix_attempt += 1
                            self.logger.info(f"🔧 Fix Attempt {fix_attempt}/{max_retries} for Task {task_id}")
                            
                            # 1. Analyze
                            analysis = debugger.analyze_failure(current_error, {"task": task})
                            
                            # 2. Fix (Simulated by re-running agent with 'fix' instruction)
                            # In real world, we would apply a patch here provided by the fixer agent
                            
                            # 3. Retry Execution
                            try:
                                # Retry the task (simplified for now)
                                new_result = await self._execute_single_task(task)
                                if not isinstance(new_result, Exception) and new_result.get("status") != "failed":
                                    fixed = True
                                    self.logger.info(f"✅ Fixed Task {task_id} on attempt {fix_attempt}")
                                    completed_task_ids.add(task_id)
                                    context.results[f"task_{task_id}"] = new_result
                                    break
                            except Exception as e:
                                current_error = str(e)
                        
                        if not fixed:
                            self.logger.error(f"❌ Task {task_id} failed after {max_retries} attempts.")
                            context.status = WorkflowStatus.FAILED
                            return context
                    else:
                        # Success
                        completed_task_ids.add(task_id)
                        context.results[f"task_{task_id}"] = result

            # Phase 3: Quality Gates
            if quality_gates:
                await self._phase_quality_check(context, quality_gates)
                if context.status == WorkflowStatus.FAILED:
                    context.results["Note"] = "Failed Quality Gates"
                    # Ideally we loop back to fix here too, but for now we stop
                    return context
            
            # Phase 4: Completion
            await self._phase_completion(context)
            
        except Exception as e:
            self.logger.error(f"Workflow {context.workflow_id} crashed: {e}")
            context.status = WorkflowStatus.FAILED
            context.results["error"] = str(e)
            
        return context

    async def _phase_planning(self, context: WorkflowContext, tasks: List[Dict]):
        """مرحلة التخطيط"""
        context.status = WorkflowStatus.PLANNING
        self.logger.info(f"📋 Planning workflow: {context.name}")
        
        # تحديد الوكلاء المطلوبين
        required_agents = set()
        for task in tasks:
            agent_type = task.get("agent_type", "generic")
            required_agents.add(agent_type)
        
        context.agents_involved = list(required_agents)
        context.metadata["planned_tasks"] = len(tasks)
        context.updated_at = datetime.now()

    async def _execute_batch(self, tasks: List[Dict]) -> List[Any]:
        """Execute a batch of tasks in parallel."""
        return await asyncio.gather(
            *[self._execute_single_task(task) for task in tasks],
            return_exceptions=True
        )

    async def _execute_single_task(self, task: Dict) -> Any:
        """Execute a single task with the appropriate agent, tracking metrics and memory."""
        import time
        agent_type = task.get("agent_type", "generic")
        agent = self.agent_manager.get_agent(agent_type)
        task_id = task.get("id", "unknown")

        # Track execution in metrics
        self.metrics.start_task(str(task_id), agent_type, task.get("description", "task"))
        start_time = time.time()

        try:
            result = await agent.execute(task)
            elapsed = time.time() - start_time
            self.metrics.complete_task(str(task_id), success=True)

            # Store result pattern in memory for learning
            task_status = result.get("status", "unknown") if isinstance(result, dict) else "completed"
            self.memory.store_memory(
                agent_name=agent_type,
                category="task_result",
                key=str(task_id),
                value={
                    "description": task.get("description", ""),
                    "status": task_status,
                    "elapsed": elapsed,
                },
                success_rate=1.0 if task_status == "completed" else 0.5
            )

            return result

        except Exception as e:
            elapsed = time.time() - start_time
            self.metrics.complete_task(str(task_id), success=False, error=str(e))
            raise

    async def _phase_quality_check(
        self, 
        context: WorkflowContext, 
        criteria: List[str]
    ):
        """مرحلة فحص الجودة"""
        context.status = WorkflowStatus.QUALITY_CHECK
        self.logger.info(f"🔍 Running quality gates: {criteria}")
        
        report = await self.quality_manager.check(
            context.results,
            criteria
        )
        
        context.quality_report = report
        
        if report["passed"]:
            self.logger.info("✅ Quality gates passed")
        else:
            self.logger.error(f"❌ Quality gates failed: {report['failures']}")
            context.status = WorkflowStatus.FAILED
    
    async def _phase_completion(self, context: WorkflowContext):
        """مرحلة الإكمال"""
        context.status = WorkflowStatus.COMPLETED
        context.updated_at = datetime.now()
        self.logger.info(f"✨ Workflow {context.workflow_id} completed")
    
    async def _request_board_approval(self, context: WorkflowContext) -> bool:
        """Request real Board of Directors review using BoardOfDirectors.review_workflow()."""
        self.logger.info("🏛️ Requesting Board of Directors review...")

        from src.board.directors import WorkflowProposal

        # Build a real proposal from the workflow context
        proposal = WorkflowProposal(
            workflow_type=context.name,
            complexity=context.metadata.get("complexity", 5),
            agents_required=context.agents_involved,
            estimated_duration_minutes=context.metadata.get("estimated_minutes", 60),
            touches_external_services=context.metadata.get("touches_external", False),
            touches_database=context.metadata.get("touches_database", False),
        )

        # Real board review with conditions (async)
        decision = await self.board.review_workflow(proposal)
        self.logger.info(
            f"Board decision: {'approved' if decision.approved else 'rejected'} "
            f"(director: {decision.director.value})"
        )

        if decision.approved:
            # Store conditions in context for enforcement
            context.metadata["board_conditions"] = decision.conditions
            context.metadata["board_director"] = decision.director.value
            return True
        else:
            self.logger.warning(f"❌ Board REJECTED workflow: {decision.reason}")
            context.metadata["board_rejection_reason"] = decision.reason
            return False
    
    def get_status(self, workflow_id: str) -> Optional[WorkflowContext]:
        """الحصول على حالة سير العمل"""
        return self.active_workflows.get(workflow_id)
    
    async def abort_workflow(self, workflow_id: str) -> bool:
        """إلغاء سير العمل"""
        if workflow_id in self.active_workflows:
            context = self.active_workflows[workflow_id]
            context.status = WorkflowStatus.ABORTED
            self.logger.warning(f"🛑 Workflow {workflow_id} aborted")
            return True
        return False
