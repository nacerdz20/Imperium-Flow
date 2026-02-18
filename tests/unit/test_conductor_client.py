"""
اختبارات لـ conductor_client.py — ConductorClient مع mock كامل لـ SDK.
تغطية: __init__، start_workflow، get_workflow_status (نجاح + فشل).
الهدف: conductor_client.py (0% → 90%+)
"""

import pytest
from unittest.mock import MagicMock, patch


class TestConductorClientInit:
    @patch("src.integrations.conductor_client.OrkesWorkflowClient")
    @patch("src.integrations.conductor_client.Configuration")
    def test_init_default_url(self, MockConfig, MockOrkes):
        from src.integrations.conductor_client import ConductorClient
        client = ConductorClient()
        MockConfig.assert_called_once_with(base_url="http://localhost:8080/api")
        MockOrkes.assert_called_once()

    @patch("src.integrations.conductor_client.OrkesWorkflowClient")
    @patch("src.integrations.conductor_client.Configuration")
    def test_init_custom_url(self, MockConfig, MockOrkes):
        from src.integrations.conductor_client import ConductorClient
        client = ConductorClient(base_url="http://custom:9090/api")
        MockConfig.assert_called_once_with(base_url="http://custom:9090/api")


class TestStartWorkflow:
    @patch("src.integrations.conductor_client.OrkesWorkflowClient")
    @patch("src.integrations.conductor_client.Configuration")
    def test_start_workflow_success(self, MockConfig, MockOrkes):
        from src.integrations.conductor_client import ConductorClient

        mock_wf_client = MagicMock()
        mock_wf_client.start_workflow.return_value = "wf-123"
        MockOrkes.return_value = mock_wf_client

        client = ConductorClient()
        wf_id = client.start_workflow("my_workflow", version=1, input_data={"key": "val"})
        assert wf_id == "wf-123"
        mock_wf_client.start_workflow.assert_called_once()

    @patch("src.integrations.conductor_client.OrkesWorkflowClient")
    @patch("src.integrations.conductor_client.Configuration")
    def test_start_workflow_failure(self, MockConfig, MockOrkes):
        from src.integrations.conductor_client import ConductorClient

        mock_wf_client = MagicMock()
        mock_wf_client.start_workflow.side_effect = Exception("Connection refused")
        MockOrkes.return_value = mock_wf_client

        client = ConductorClient()
        with pytest.raises(Exception, match="Connection refused"):
            client.start_workflow("failing_workflow")

    @patch("src.integrations.conductor_client.OrkesWorkflowClient")
    @patch("src.integrations.conductor_client.Configuration")
    def test_start_workflow_default_params(self, MockConfig, MockOrkes):
        from src.integrations.conductor_client import ConductorClient

        mock_wf_client = MagicMock()
        mock_wf_client.start_workflow.return_value = "wf-456"
        MockOrkes.return_value = mock_wf_client

        client = ConductorClient()
        wf_id = client.start_workflow("simple_wf")
        assert wf_id == "wf-456"


class TestGetWorkflowStatus:
    @patch("src.integrations.conductor_client.OrkesWorkflowClient")
    @patch("src.integrations.conductor_client.Configuration")
    def test_get_status_success(self, MockConfig, MockOrkes):
        from src.integrations.conductor_client import ConductorClient

        mock_workflow = MagicMock()
        mock_workflow.status = "COMPLETED"
        mock_workflow.input = {"data": "in"}
        mock_workflow.output = {"data": "out"}
        mock_workflow.tasks = []

        mock_wf_client = MagicMock()
        mock_wf_client.get_workflow.return_value = mock_workflow
        MockOrkes.return_value = mock_wf_client

        client = ConductorClient()
        status = client.get_workflow_status("wf-123")
        assert status["status"] == "COMPLETED"
        assert status["input"] == {"data": "in"}
        assert status["output"] == {"data": "out"}
        assert status["tasks"] == []

    @patch("src.integrations.conductor_client.OrkesWorkflowClient")
    @patch("src.integrations.conductor_client.Configuration")
    def test_get_status_with_tasks(self, MockConfig, MockOrkes):
        from src.integrations.conductor_client import ConductorClient

        mock_task = MagicMock()
        mock_task.to_ast.return_value = {"task_id": "t1", "status": "COMPLETED"}

        mock_workflow = MagicMock()
        mock_workflow.status = "RUNNING"
        mock_workflow.input = {}
        mock_workflow.output = {}
        mock_workflow.tasks = [mock_task]

        mock_wf_client = MagicMock()
        mock_wf_client.get_workflow.return_value = mock_workflow
        MockOrkes.return_value = mock_wf_client

        client = ConductorClient()
        status = client.get_workflow_status("wf-789")
        assert status["status"] == "RUNNING"
        assert len(status["tasks"]) == 1

    @patch("src.integrations.conductor_client.OrkesWorkflowClient")
    @patch("src.integrations.conductor_client.Configuration")
    def test_get_status_failure(self, MockConfig, MockOrkes):
        """سطور 50-52: فشل جلب الحالة يُرجع UNKNOWN."""
        from src.integrations.conductor_client import ConductorClient

        mock_wf_client = MagicMock()
        mock_wf_client.get_workflow.side_effect = Exception("Not found")
        MockOrkes.return_value = mock_wf_client

        client = ConductorClient()
        status = client.get_workflow_status("wf-missing")
        assert status["status"] == "UNKNOWN"
        assert "Not found" in status["error"]
