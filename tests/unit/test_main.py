"""
اختبارات لـ main.py — نقطة الدخول مع mock لجميع التبعيات الخارجية.
تغطية: main() function (agent init، worker creation، success/failure).
الهدف: main.py (0% → 90%+)
"""

import pytest
from unittest.mock import patch, MagicMock


class TestMainFunction:

    @patch("src.main.TaskHandler")
    @patch("src.main.Configuration")
    @patch("src.main.ConductorWorker")
    @patch("src.main.WorkerAgent")
    @patch("src.main.ConductorClient")
    def test_main_initializes_agents(self, MockClient, MockWorkerAgent, MockConductorWorker, MockConfig, MockTaskHandler):
        """سطور 32-35: تهيئة الوكلاء الثلاثة."""
        # Configure TaskHandler to raise after start to exit the loop
        mock_handler = MagicMock()
        mock_handler.__enter__ = MagicMock(return_value=mock_handler)
        mock_handler.__exit__ = MagicMock(return_value=False)
        mock_handler.start_processes.side_effect = KeyboardInterrupt()
        MockTaskHandler.return_value = mock_handler

        from src.main import main
        try:
            main()
        except (KeyboardInterrupt, SystemExit):
            pass

        # التحقق من إنشاء 3 وكلاء
        assert MockWorkerAgent.call_count == 3

    @patch("src.main.TaskHandler")
    @patch("src.main.Configuration")
    @patch("src.main.ConductorWorker")
    @patch("src.main.WorkerAgent")
    @patch("src.main.ConductorClient")
    def test_main_creates_workers(self, MockClient, MockWorkerAgent, MockConductorWorker, MockConfig, MockTaskHandler):
        """سطور 40-44: إنشاء عمال Conductor."""
        mock_handler = MagicMock()
        mock_handler.__enter__ = MagicMock(return_value=mock_handler)
        mock_handler.__exit__ = MagicMock(return_value=False)
        mock_handler.start_processes.side_effect = KeyboardInterrupt()
        MockTaskHandler.return_value = mock_handler

        from src.main import main
        try:
            main()
        except (KeyboardInterrupt, SystemExit):
            pass

        # التحقق من إنشاء 3 عمال conductor
        assert MockConductorWorker.call_count == 3

    @patch("src.main.TaskHandler")
    @patch("src.main.Configuration")
    @patch("src.main.ConductorWorker")
    @patch("src.main.WorkerAgent")
    @patch("src.main.ConductorClient")
    def test_main_configuration(self, MockClient, MockWorkerAgent, MockConductorWorker, MockConfig, MockTaskHandler):
        """سطر 29: تهيئة Configuration مع URL."""
        mock_handler = MagicMock()
        mock_handler.__enter__ = MagicMock(return_value=mock_handler)
        mock_handler.__exit__ = MagicMock(return_value=False)
        mock_handler.start_processes.side_effect = KeyboardInterrupt()
        MockTaskHandler.return_value = mock_handler

        from src.main import main
        try:
            main()
        except (KeyboardInterrupt, SystemExit):
            pass

        MockConfig.assert_called_once_with(base_url="http://localhost:8080/api")

    @patch("src.main.TaskHandler")
    @patch("src.main.Configuration")
    @patch("src.main.ConductorWorker")
    @patch("src.main.WorkerAgent")
    @patch("src.main.ConductorClient")
    def test_main_handles_connection_error(self, MockClient, MockWorkerAgent, MockConductorWorker, MockConfig, MockTaskHandler):
        """سطور 59-63: فشل الاتصال."""
        MockTaskHandler.side_effect = Exception("Connection refused")

        from src.main import main
        # يجب ألا يرفع استثناء — يتعامل معه داخلياً
        main()

    @patch("src.main.TaskHandler")
    @patch("src.main.Configuration")
    @patch("src.main.ConductorWorker")
    @patch("src.main.WorkerAgent")
    @patch("src.main.ConductorClient")
    def test_main_starts_task_handler(self, MockClient, MockWorkerAgent, MockConductorWorker, MockConfig, MockTaskHandler):
        """سطور 51-53: تشغيل TaskHandler."""
        mock_handler = MagicMock()
        mock_handler.__enter__ = MagicMock(return_value=mock_handler)
        mock_handler.__exit__ = MagicMock(return_value=False)
        mock_handler.start_processes.side_effect = KeyboardInterrupt()
        MockTaskHandler.return_value = mock_handler

        from src.main import main
        try:
            main()
        except (KeyboardInterrupt, SystemExit):
            pass

        mock_handler.start_processes.assert_called_once()
