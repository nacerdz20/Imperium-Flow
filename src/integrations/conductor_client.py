#!/usr/bin/env python3
"""
Conductor Client Integration
يتعامل مع Conductor Server باستخدام conductor-python SDK
"""

import logging
from typing import Dict, Any, Optional
from conductor.client.configuration.configuration import Configuration
from conductor.client.http.models.start_workflow_request import StartWorkflowRequest
from conductor.client.configuration.configuration import Configuration
from conductor.client.http.models.start_workflow_request import StartWorkflowRequest
from conductor.client.orkes.orkes_workflow_client import OrkesWorkflowClient
# from conductor.client.worker.worker_task import WorkerTask # Not used yet

class ConductorClient:
    """واجهة التعامل مع Conductor Server"""
    
    def __init__(self, base_url: str = "http://localhost:8080/api"):
        self.logger = logging.getLogger("ConductorClient")
        self.config = Configuration(base_url=base_url)
        self.workflow_client = OrkesWorkflowClient(self.config)
        self.logger.info(f"🔌 Connected to Conductor at {base_url}")

    def start_workflow(self, name: str, version: int = 1, input_data: Dict = {}) -> str:
        """بدء سير عمل جديد في Conductor"""
        try:
            request = StartWorkflowRequest(
                name=name,
                version=version,
                input=input_data
            )
            workflow_id = self.workflow_client.start_workflow(request)
            self.logger.info(f"🚀 Started Conductor Workflow: {name} (ID: {workflow_id})")
            return workflow_id
        except Exception as e:
            self.logger.error(f"❌ Failed to start workflow {name}: {e}")
            raise

    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """جلب حالة سير العمل"""
        try:
            workflow = self.workflow_client.get_workflow(workflow_id, include_tasks=True)
            return {
                "status": workflow.status,
                "input": workflow.input,
                "output": workflow.output,
                "tasks": [t.to_ast() for t in workflow.tasks] if workflow.tasks else []
            }
        except Exception as e:
            self.logger.error(f"❌ Failed to get status for {workflow_id}: {e}")
            return {"status": "UNKNOWN", "error": str(e)}

    # يمكن إضافة وظائف أخرى مثل:
    # - تسجيل Workers
    # - إيقاف سير العمل
    # - إعادة تشغيل المهام الفاشلة
