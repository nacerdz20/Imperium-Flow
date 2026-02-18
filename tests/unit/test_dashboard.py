"""
اختبارات لـ dashboard/app.py — ConnectionManager + FastAPI endpoints.
تغطية: ConnectionManager (connect/disconnect/broadcast)، API endpoints، serve_dashboard.
الهدف: dashboard/app.py (0% → 90%+)
"""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from src.dashboard.app import ConnectionManager


# ═══════════════════════════════════════════════════════════
# ConnectionManager Tests
# ═══════════════════════════════════════════════════════════

class TestConnectionManager:
    def setup_method(self):
        self.mgr = ConnectionManager()

    def test_init_empty(self):
        assert self.mgr.active == []

    @pytest.mark.asyncio
    async def test_connect(self):
        ws = AsyncMock()
        await self.mgr.connect(ws)
        assert ws in self.mgr.active
        ws.accept.assert_called_once()

    def test_disconnect(self):
        ws = MagicMock()
        self.mgr.active.append(ws)
        self.mgr.disconnect(ws)
        assert ws not in self.mgr.active

    @pytest.mark.asyncio
    async def test_broadcast_single(self):
        ws = AsyncMock()
        self.mgr.active.append(ws)
        await self.mgr.broadcast({"status": "ok"})
        ws.send_text.assert_called_once()
        sent = json.loads(ws.send_text.call_args[0][0])
        assert sent["status"] == "ok"

    @pytest.mark.asyncio
    async def test_broadcast_multiple(self):
        ws1, ws2 = AsyncMock(), AsyncMock()
        self.mgr.active.extend([ws1, ws2])
        await self.mgr.broadcast({"msg": "hello"})
        ws1.send_text.assert_called_once()
        ws2.send_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_broadcast_exception_handled(self):
        """سطور 53-56: استثناء أثناء الإرسال لا يُؤثر على الآخرين."""
        ws_bad = AsyncMock()
        ws_bad.send_text.side_effect = Exception("broken")
        ws_good = AsyncMock()
        self.mgr.active.extend([ws_bad, ws_good])
        await self.mgr.broadcast({"data": 1})
        # ws_good يجب أن يحصل على الرسالة رغم فشل ws_bad
        ws_good.send_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_broadcast_empty_connections(self):
        await self.mgr.broadcast({"empty": True})
        # لا يحدث شيء — لا استثناء

    @pytest.mark.asyncio
    async def test_connect_multiple(self):
        ws1, ws2 = AsyncMock(), AsyncMock()
        await self.mgr.connect(ws1)
        await self.mgr.connect(ws2)
        assert len(self.mgr.active) == 2


# ═══════════════════════════════════════════════════════════
# FastAPI Endpoints (only if FastAPI available)
# ═══════════════════════════════════════════════════════════

try:
    from fastapi.testclient import TestClient
    from src.dashboard.app import app as dashboard_app, HAS_FASTAPI

    if HAS_FASTAPI and dashboard_app is not None:

        class TestDashboardEndpoints:

            def setup_method(self):
                self.client = TestClient(dashboard_app)

            def test_get_dashboard(self):
                resp = self.client.get("/api/dashboard")
                assert resp.status_code == 200
                data = resp.json()
                assert isinstance(data, dict)

            def test_get_agent_stats(self):
                resp = self.client.get("/api/agents/code_worker/stats")
                assert resp.status_code == 200

            def test_get_agent_trend(self):
                resp = self.client.get("/api/agents/code_worker/trend?limit=5")
                assert resp.status_code == 200

            def test_get_memory_stats(self):
                resp = self.client.get("/api/memory/stats")
                assert resp.status_code == 200

            def test_serve_dashboard_no_html(self):
                """سطور 103-106: الصفحة الرئيسية بدون ملف HTML."""
                resp = self.client.get("/")
                assert resp.status_code == 200
                assert "Imperium Flow" in resp.text

            def test_serve_dashboard_with_html(self):
                """سطور 104-105: الصفحة الرئيسية مع ملف HTML موجود."""
                from pathlib import Path
                html_path = Path(__file__).parent / "../../src/dashboard/index.html"
                if html_path.exists():
                    resp = self.client.get("/")
                    assert resp.status_code == 200

except ImportError:
    pass
