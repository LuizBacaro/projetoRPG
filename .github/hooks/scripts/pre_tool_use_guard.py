#!/usr/bin/env python3
import json
import sys


def _first_present(mapping, keys, default=None):
    for key in keys:
        if key in mapping:
            return mapping[key]
    return default


def _as_text(value):
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    try:
        return json.dumps(value, ensure_ascii=True)
    except Exception:
        return str(value)


def _emit_allow():
    print(json.dumps({"continue": True}))


def _emit_ask(reason, message):
    print(
        json.dumps(
            {
                "systemMessage": message,
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "ask",
                    "permissionDecisionReason": reason,
                },
            }
        )
    )


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        _emit_allow()
        return

    tool_name = _first_present(payload, ["tool_name", "toolName", "tool"])
    tool_input = _first_present(payload, ["tool_input", "toolInput", "input", "parameters"], {})
    text = _as_text(tool_input).lower()

    dangerous_terminal_patterns = [
        "git reset --hard",
        "git checkout --",
        "git clean -fd",
        "rm -rf",
        "drop database",
    ]
    dangerous_sql_patterns = [
        "drop table",
        "truncate table",
        "delete from",
        "alter table",
    ]

    if tool_name in {"run_in_terminal", "send_to_terminal"}:
        if any(pattern in text for pattern in dangerous_terminal_patterns):
            _emit_ask(
                "Comando de terminal potencialmente destrutivo.",
                "Hook de seguranca: revise se a operacao destrutiva foi solicitada explicitamente pelo usuario antes de prosseguir.",
            )
            return

    if tool_name == "mcp_postgresql_mc_pgsql_modify":
        if any(pattern in text for pattern in dangerous_sql_patterns):
            _emit_ask(
                "Modificacao SQL potencialmente destrutiva.",
                "Hook de seguranca: confirme que a mudanca em banco foi pedida explicitamente e que o estado atual do schema foi inspecionado antes da execucao.",
            )
            return

    _emit_allow()


if __name__ == "__main__":
    main()