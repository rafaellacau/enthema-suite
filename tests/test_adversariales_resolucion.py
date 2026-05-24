# -*- coding: utf-8 -*-
"""
Enthema Suite V3.0 - Suite de Pruebas de Resolución de Límites de Auditoría
"""
import unittest
import os
import sys
from fastapi.testclient import TestClient

# Asegurar que el path local esté disponible
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, sessions, active_connections, AppState
from modules.investigador.db_builder import FinancialFeasibilityProfiler

class TestAdversarialesResolucion(unittest.TestCase):
    
    def setUp(self):
        """Inicializa el cliente de pruebas de FastAPI y autentica sesiones de investigador y auditor."""
        self.client = TestClient(app)
        
        # 1. Login Científico (aris)
        login_res = self.client.post("/api/login", json={"username": "aris", "password": "password"})
        self.assertEqual(login_res.status_code, 200)
        self.client.cookies.set("session_id", login_res.cookies.get("session_id"))
        self.researcher_cookie = login_res.cookies.get("session_id")
        
        # 2. Login Auditor (admin)
        login_audit = self.client.post("/api/login", json={"username": "admin", "password": "Lalo6%%Lalo"})
        self.assertEqual(login_audit.status_code, 200)
        self.auditor_cookie = login_audit.cookies.get("session_id")

    # ==============================================================================
    # PRUEBA 1: DISTRIBUCIÓN DE MONTE CARLO EN SOLVER
    # ==============================================================================
    def test_monte_carlo_math_solver(self):
        """Valida que la simulación de Monte Carlo devuelva percentiles consistentes en el solver."""
        flujos = [-100000.0, 40000.0, 45000.0, 50000.0, 55000.0, 60000.0]
        wacc = 0.10
        
        mc = FinancialFeasibilityProfiler.simular_monte_carlo(flujos, wacc, std_dev=0.15, simulaciones=200)
        
        # Assert structure of returned keys
        self.assertIn("van_p5", mc)
        self.assertIn("van_p50", mc)
        self.assertIn("van_p95", mc)
        self.assertIn("tir_p5", mc)
        self.assertIn("tir_p50", mc)
        self.assertIn("tir_p95", mc)
        
        # Assert mathematical distribution ordering
        self.assertTrue(mc["van_p5"] <= mc["van_p50"])
        self.assertTrue(mc["van_p50"] <= mc["van_p95"])
        self.assertTrue(mc["tir_p5"] <= mc["tir_p50"])
        self.assertTrue(mc["tir_p50"] <= mc["tir_p95"])

    # ==============================================================================
    # PRUEBA 2: ENDPOINT DE RESOLUCIÓN FINANCIERA CON MONTE CARLO
    # ==============================================================================
    def test_solve_financials_api_stochastics(self):
        """Valida que el endpoint /api/finance/solve retorne los percentiles estocásticos."""
        flows = [
            {"period": 0, "inflow": 0.0, "outflow": 100000.0},
            {"period": 1, "inflow": 40000.0, "outflow": 0.0},
            {"period": 2, "inflow": 45000.0, "outflow": 0.0},
            {"period": 3, "inflow": 50000.0, "outflow": 0.0},
            {"period": 4, "inflow": 55000.0, "outflow": 0.0},
            {"period": 5, "inflow": 60000.0, "outflow": 0.0}
        ]
        
        # Usar la cookie del investigador
        self.client.cookies.set("session_id", self.researcher_cookie)
        res = self.client.post("/api/finance/solve", json={
            "discount_rate": 0.10,
            "target_fund_usd": 100000.0,
            "cash_flow": flows
        })
        
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("van", data)
        self.assertIn("tir", data)
        self.assertIn("monte_carlo", data)
        
        mc = data["monte_carlo"]
        self.assertIn("van_p5", mc)
        self.assertIn("tir_p50", mc)
        self.assertTrue(mc["van_p5"] <= mc["van_p95"])

    # ==============================================================================
    # PRUEBA 3: WATCHTOWER AUDITORIA / CONEXIONES ACTIVA SUPERVISOR
    # ==============================================================================
    def test_watchtower_connections_monitoring(self):
        """Valida que el panel de administración (/api/admin/connections) liste las sesiones en vivo."""
        # Configurar cookie de auditor
        self.client.cookies.set("session_id", self.auditor_cookie)
        res = self.client.get("/api/admin/connections")
        self.assertEqual(res.status_code, 200)
        
        conns = res.json()
        self.assertTrue(len(conns) >= 1)
        
        # Verificar que el auditor actual esté registrado en el tracker
        admin_conns = [c for c in conns if c["role"] == "admin" or c["role"] == "auditor"]
        self.assertTrue(len(admin_conns) >= 1)

    # ==============================================================================
    # PRUEBA 4: BYPASS DE PRIVACIDAD SOBERANA data-no-ai
    # ==============================================================================
    def test_privacy_bypass_silence_zone(self):
        """Valida que la directiva data-no-ai evite cualquier procesamiento de IA externo."""
        self.client.cookies.set("session_id", self.researcher_cookie)
        res = self.client.post("/api/copilot/query", json={
            "query": "Analizar datos del reactor de sargazo con la directiva data-no-ai activada.",
            "path": "fase1/abstract"
        })
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("answer", data)
        self.assertIn("🛡️ Zona de Silencio No-AI", data["answer"])

    # ==============================================================================
    # PRUEBA 5: TRANSPARENCIA DE TELEMETRÍA DEL PROPIO INVESTIGADOR
    # ==============================================================================
    def test_researcher_telemetry_transparency(self):
        """Valida que el endpoint /api/researcher/telemetry retorne las métricas del propio investigador."""
        self.client.cookies.set("session_id", self.researcher_cookie)
        res = self.client.get("/api/researcher/telemetry")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("literal_acceptances", data)
        self.assertIn("modified_acceptances", data)
        self.assertIn("total_suggestions", data)
        self.assertIn("acceptance_rate_percent", data)

if __name__ == "__main__":
    unittest.main()
