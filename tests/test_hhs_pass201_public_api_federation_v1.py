from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from hhs_backend.visual_server import app


class Pass201PublicAPIFederationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.federation = app.state.hhs_public_api_federation
        cls.client = TestClient(app)

    def test_all_api_modules_import_and_all_router_routes_are_exposed(self) -> None:
        report = app.state.hhs_public_api_registration
        self.assertTrue(report["registration_started"])
        self.assertEqual(report["import_failure_count"], 0, report["import_failures"])
        self.assertEqual(report["unexposed_route_count"], 0, report["unexposed_routes"])
        self.assertTrue(report["closed"])
        self.assertGreater(report["api_module_count"], 0)
        self.assertGreater(report["router_count"], 0)
        self.assertGreater(report["discovered_router_route_count"], 0)

    def test_catalog_contains_every_application_route_once(self) -> None:
        routes = self.federation.route_catalog(app)
        self.assertEqual(len(routes), len(app.router.routes))
        route_ids = [route["route_id"] for route in routes]
        self.assertEqual(len(route_ids), len(set(route_ids)))
        self.assertTrue(any(route["path"] == "/api/public/status" for route in routes))
        self.assertTrue(any(route["path"] == "/api/runtime/optimization-active/status" for route in routes))

    def test_every_openapi_visible_route_is_present_in_openapi(self) -> None:
        catalog = self.federation.catalog(app)
        self.assertEqual(catalog["openapi_missing_count"], 0, catalog["openapi_missing"])
        self.assertTrue(catalog["closed"])
        self.assertGreater(catalog["openapi_path_count"], 0)

    def test_services_and_pass_modules_are_publicly_cataloged(self) -> None:
        services = self.federation.service_catalog(app)
        passes = self.federation.pass_catalog(app)
        self.assertGreater(len(services), 0)
        self.assertGreater(len(passes), 0)
        self.assertTrue(all(service["public_api_available"] for service in services))
        self.assertTrue(all(pass_module["public_api_available"] for pass_module in passes))
        self.assertTrue(any(item["pass_id"] == "pass201" for item in passes))
        self.assertTrue(any(item["pass_id"] == "pass200c" for item in passes))

    def test_public_endpoints_and_tools_respond(self) -> None:
        for path in (
            "/api/public/status",
            "/api/public/catalog",
            "/api/public/routes",
            "/api/public/services",
            "/api/public/passes",
            "/api/public/openapi",
            "/api/public/tools",
        ):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200, (path, response.text))
        invoke = self.client.post(
            "/api/public/tools/invoke",
            json={"tool": "public.status", "arguments": {}},
        )
        self.assertEqual(invoke.status_code, 200, invoke.text)
        self.assertEqual(invoke.json()["tool"], "public.status")

    def test_route_service_and_pass_detail_endpoints(self) -> None:
        route = self.federation.route_catalog(app)[0]
        response = self.client.get(f"/api/public/routes/{route['route_id']}")
        self.assertEqual(response.status_code, 200, response.text)

        service = self.federation.service_catalog(app)[0]
        response = self.client.get(f"/api/public/services/{service['service_id']}")
        self.assertEqual(response.status_code, 200, response.text)

        pass_module = self.federation.pass_catalog(app)[0]
        response = self.client.get(f"/api/public/passes/{pass_module['module_name']}")
        self.assertEqual(response.status_code, 200, response.text)

    def test_catalog_identity_is_deterministic(self) -> None:
        first = self.federation.catalog(app)
        second = self.federation.catalog(app)
        self.assertEqual(first["catalog_sha256"], second["catalog_sha256"])
        self.assertEqual(first["routes"], second["routes"])
        self.assertEqual(first["services"], second["services"])
        self.assertEqual(first["passes"], second["passes"])

    def test_static_root_mount_is_last(self) -> None:
        self.assertEqual(getattr(app.router.routes[-1], "name", None), "hhs-visual-home")
        public_index = next(
            index for index, route in enumerate(app.router.routes)
            if getattr(route, "path", None) == "/api/public/status"
        )
        self.assertLess(public_index, len(app.router.routes) - 1)


if __name__ == "__main__":
    unittest.main()
