import logging

from starlette.requests import Request

from app.core.security_audit import get_client_ip, log_security_event


def test_get_client_ip_prioriza_x_forwarded_for():
    request = Request(
        {
            "type": "http",
            "headers": [(b"x-forwarded-for", b"203.0.113.10, 198.51.100.1")],
        }
    )

    assert get_client_ip(request) == "203.0.113.10"


def test_log_security_event_emite_linha_estruturada(caplog):
    caplog.set_level(logging.INFO, logger="app.security")

    log_security_event(
        "login",
        "failure",
        user_email="user@example.com",
        actor_email="admin@example.com",
        target="usuario:7",
        reason="bad_password",
        details={"attempt": 2},
    )

    assert "event=login" in caplog.text
    assert "outcome=failure" in caplog.text
    assert "user=user@example.com" in caplog.text
    assert "actor=admin@example.com" in caplog.text
    assert "target=usuario:7" in caplog.text
    assert "reason=bad_password" in caplog.text
    assert "attempt=2" in caplog.text