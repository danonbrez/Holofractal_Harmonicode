from fastapi import FastAPI
from fastapi.testclient import TestClient
from hhs_backend.api.pass135_audit_routes import router


def test_pass135_readonly_audit_routes_are_reachable():
    app=FastAPI()
    app.include_router(router)
    with TestClient(app) as client:
        status=client.get('/api/audit/ceuac/pass135/status')
        record=client.get('/api/audit/ceuac/pass135/record')
        scenarios=client.get('/api/audit/ceuac/pass135/scenarios')
        verification=client.get('/api/audit/ceuac/pass135/verification')
        errata=client.get('/api/audit/ceuac/pass135/errata')
    assert status.status_code == 200
    assert status.json()['status'] == 'CANONICAL_CEUAC_AUDIT_COMPLETED_WITH_BOUNDED_FINDINGS'
    assert record.status_code == 200
    assert record.json()['pass_id'] == 'PASS_135'
    assert scenarios.status_code == 200
    assert len(scenarios.json()['scenarios']) >= 10
    assert verification.status_code == 200
    assert verification.json()['ok'] is True
    assert errata.status_code == 200
    assert errata.json()['erratum_id'] == 'PASS_135_COMPLETION_ERRATUM_001'
    assert 'CONFORMANCE_API_NOT_EXPOSED_ON_RESPONSIVE_RUNTIME' in status.json()['bounded_findings']
