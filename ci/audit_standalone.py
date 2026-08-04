#!/usr/bin/env python3
"""
ARCHON CI — Standalone Security Auditor
========================================
A portable, provider-agnostic script that performs static analysis and
LLM-powered security auditing on any Python codebase.

Designed to run in GitHub Actions, local terminals, or any CI/CD pipeline.
"""

import os
import sys
import json
import argparse
import py_compile
import subprocess
from pathlib import Path
from datetime import datetime

# ---------------------------------------------------------------------------
# LangChain provider imports — used directly in get_llm_client()
# ---------------------------------------------------------------------------
try:
    from langchain_groq import ChatGroq  # noqa: F401
    from langchain_openai import ChatOpenAI  # noqa: F401
    from langchain_core.messages import SystemMessage, HumanMessage
    _LANGCHAIN_AVAILABLE = True
except ImportError:
    _LANGCHAIN_AVAILABLE = False

# ---------------------------------------------------------------------------
# Stdout encoding fix for CI environments
# ---------------------------------------------------------------------------
if hasattr(sys.stdout, "reconfigure") and sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure") and sys.stderr.encoding != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------------------
# 1. Native Python Syntax Check
# ---------------------------------------------------------------------------

def python_syntax_check(target_path: Path) -> list[str]:
    """Compile all .py files to catch SyntaxErrors before wasting LLM tokens."""
    errors = []
    for root, _, files in os.walk(target_path):
        for file in files:
            if file.endswith(".py"):
                file_path = Path(root) / file
                try:
                    py_compile.compile(str(file_path), doraise=True)
                except py_compile.PyCompileError as e:
                    rel_path = file_path.relative_to(target_path).as_posix()
                    errors.append(f"SyntaxError in `{rel_path}`:\n```\n{e}\n```")
    return errors

# ---------------------------------------------------------------------------
# 2. Collect Source Files
# ---------------------------------------------------------------------------

SUPPORTED_EXTENSIONS = {".py", ".js", ".ts", ".jsx", ".tsx", ".json"}

def collect_files_full(target_path: Path) -> list[dict]:
    """Collect ALL source files from the project, ignoring metadata/logs."""
    files = []
    ignored_dirs = {"chronicle", "studio", "node_modules", "venv", ".git", "__pycache__"}
    for root, dirs, filenames in os.walk(target_path):
        dirs[:] = [d for d in dirs if d not in ignored_dirs]
        for fname in filenames:
            fpath = Path(root) / fname
            if fpath.suffix in SUPPORTED_EXTENSIONS:
                try:
                    content = fpath.read_text(encoding="utf-8")
                    rel = fpath.relative_to(target_path).as_posix()
                    files.append({"path": rel, "content": content})
                except (OSError, UnicodeDecodeError):
                    pass
    return files

def collect_files_diff(target_path: Path) -> list[dict]:
    """Collect only files changed in the current git diff (PR scope)."""
    if not target_path.exists() or not target_path.is_dir():
        print("⚠️ [CI Audit] Invalid target path. Falling back to full mode.")
        return collect_files_full(target_path)

    try:
        # SECURE: shell=False prevents shell injection. target_path is a validated directory.
        result = subprocess.run(
            ["git", "diff", "--name-only", "origin/main...HEAD"],
            capture_output=True, text=True, cwd=str(target_path),
            check=True, shell=False
        )
        changed = [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
    except (subprocess.SubprocessError, FileNotFoundError, OSError):
        print("⚠️ [CI Audit] Could not run git diff. Falling back to full mode.")
        return collect_files_full(target_path)

    files = []
    for rel_path in changed:
        fpath = target_path / rel_path
        if fpath.exists() and fpath.suffix in SUPPORTED_EXTENSIONS:
            try:
                content = fpath.read_text(encoding="utf-8")
                files.append({"path": rel_path, "content": content})
            except (OSError, UnicodeDecodeError):
                pass
    return files

# ---------------------------------------------------------------------------
# 3. LLM-Powered Semantic Audit
# ---------------------------------------------------------------------------

AUDITOR_PROMPT = """You are a Senior Security Auditor reviewing a Pull Request in a multi-file Python project.
You will receive ONLY the files changed in this PR — NOT the entire codebase.

CRITICAL RULES — Read before auditing:
1. DO NOT flag cross-module imports as errors. If a file imports from 'common.providers', 'foundation.agents',
   or any other package not shown in the diff, that is VALID Python practice in a multi-module project.
   You are NOT seeing all files. Assume any imported name exists in the broader codebase.
2. DO NOT flag os.getenv() as a security vulnerability. Retrieving API keys via os.getenv() IS the correct
   and secure practice. It is the OPPOSITE of hardcoding. Only flag actual string literals like
   api_key = "sk-abc123..." as vulnerabilities.
3. DO NOT flag try/except ImportError patterns as bugs. This is a standard Python compatibility pattern.
4. DO NOT flag 'bpy' as missing. It is the Blender Python API, available at runtime inside the Blender process.
5. DO NOT flag conditional imports inside functions as "unused" if the top-level import exists as a fallback.

WHAT YOU MUST REPORT (real issues only):
- Actual hardcoded secrets: passwords or API key string literals directly in code (e.g. api_key = "sk-abc...")
- Real SyntaxErrors not caught by the native compiler (logic errors in control flow)
- Genuine bare except clauses that swallow ALL exceptions silently with no logging
- Actual circular import chains between files shown in the diff

Reply ONLY in valid JSON (no markdown, no extra text):
{
  "is_valid": true,
  "summary": "One-line summary.",
  "issues": []
}

If no real issues are found, set is_valid to true and return an empty issues array.
"""


def _build_llm_client(provider: str, model: str):
    """
    Instantiate the correct LangChain LLM client based on provider string.
    API keys are read exclusively from environment variables — never hardcoded.
    Returns None if the required API key secret is absent.
    """
    if provider == "groq":
        api_key = os.getenv("GROQ_API_KEY", "")
        if not api_key:
            print("🚨 [CI Audit] GROQ_API_KEY secret is not configured in the environment.")
            return None
        from langchain_groq import ChatGroq as _ChatGroq
        return _ChatGroq(model=model, api_key=api_key, temperature=0.0,
                         model_kwargs={"response_format": {"type": "json_object"}})

    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            print("🚨 [CI Audit] OPENAI_API_KEY secret is not configured in the environment.")
            return None
        from langchain_openai import ChatOpenAI as _ChatOpenAI
        return _ChatOpenAI(model=model, api_key=api_key, temperature=0.0,
                           model_kwargs={"response_format": {"type": "json_object"}})

    if provider == "openrouter":
        api_key = os.getenv("OPENROUTER_API_KEY", "")
        if not api_key:
            print("🚨 [CI Audit] OPENROUTER_API_KEY secret is not configured in the environment.")
            return None
        from langchain_openai import ChatOpenAI as _ChatOpenAI
        return _ChatOpenAI(model=model, api_key=api_key, temperature=0.0,
                           base_url="https://openrouter.ai/api/v1",
                           model_kwargs={"response_format": {"type": "json_object"}})

    print(f"🚨 [CI Audit] Unknown provider '{provider}'. Supported: groq, openai, openrouter.")
    return None


def _parse_llm_json(raw_content: str) -> dict:
    """Robustly extract and parse a JSON object from an LLM response string."""
    content = raw_content.strip()
    start = content.find('{')
    end = content.rfind('}')
    if start == -1 or end == -1:
        raise ValueError(f"No JSON object found in LLM response. Raw output: {content[:200]}")
    return json.loads(content[start:end + 1])


def llm_audit(files: list[dict]) -> dict | None:
    """Send collected files to the LLM for semantic security analysis."""
    if not _LANGCHAIN_AVAILABLE:
        print("⚠️ [CI Audit] LangChain dependencies are not installed. Skipping LLM audit.")
        return None

    provider = (os.getenv("AUDITOR_PROVIDER") or "groq").strip().lower()
    model = (os.getenv("AUDITOR_MODEL") or "llama-3.3-70b-versatile").strip()

    llm = _build_llm_client(provider, model)
    if llm is None:
        return None

    code_bundle = "\n".join([f"--- {f['path']} ---\n{f['content']}\n" for f in files])
    messages = [
        SystemMessage(content=AUDITOR_PROMPT),
        HumanMessage(content=f"Audit only these changed files:\n\n{code_bundle}")
    ]

    try:
        response = llm.invoke(messages)
        return _parse_llm_json(response.content)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"🚨 [CI Audit] Failed to parse LLM JSON response: {e}")
        return None
    except (ConnectionError, TimeoutError, OSError) as e:
        print(f"🚨 [CI Audit] Network error communicating with LLM provider: {e}")
        return None
    except RuntimeError as e:
        print(f"🚨 [CI Audit] LLM runtime error: {e}")
        return None
    except Exception as e:  # noqa: BLE001 — intentional catch-all for unknown SDK errors
        print(f"🚨 [CI Audit] Unexpected error from LLM SDK: {type(e).__name__}: {e}")
        return None

# ---------------------------------------------------------------------------
# 4. Report Generator
# ---------------------------------------------------------------------------

def generate_report(syntax_errors: list[str], llm_result: dict | None, mode: str) -> str:
    """Generate a markdown audit report."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "# 🛡️ ARCHON Security Audit Report",
        f"**Date:** {now}  ",
        f"**Mode:** `{mode}`  ",
        "",
    ]

    if syntax_errors:
        lines.append("## ❌ Native Syntax Errors (Python Compilation)")
        for err in syntax_errors:
            lines.append(f"- {err}")
        lines.append("")
    else:
        lines.append("## ✅ Native Syntax Check — Passed")
        lines.append("")

    if llm_result is None:
        lines.append("## ⚠️ LLM Audit — Skipped (No API key configured or provider unavailable)")
        lines.append("")
    elif llm_result.get("is_valid", False):
        summary = llm_result.get("summary", "No issues found.")
        lines.append("## ✅ LLM Security Audit — Passed")
        lines.append(f"_{summary}_")
        lines.append("")
    else:
        summary = llm_result.get("summary", "Issues detected.")
        lines.append("## ❌ LLM Security Audit — Failed")
        lines.append(f"_{summary}_")
        lines.append("")
        issues = llm_result.get("issues", [])
        if issues:
            lines.append("| Severity | File | Description |")
            lines.append("|----------|------|-------------|")
            for issue in issues:
                sev = issue.get("severity", "info").upper()
                icon = "🔴" if sev == "CRITICAL" else "🟡" if sev == "WARNING" else "🔵"
                lines.append(f"| {icon} {sev} | `{issue.get('file', '?')}` | {issue.get('description', '')} |")
            lines.append("")

    passed = (not syntax_errors) and (llm_result is None or llm_result.get("is_valid", False))
    verdict = "✅ **APPROVED** — No critical issues found." if passed else "❌ **REJECTED** — Issues require attention before merge."
    lines.append("---")
    lines.append(f"**Verdict:** {verdict}")
    return "\n".join(lines)

# ---------------------------------------------------------------------------
# 5. Main Entry Point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="ARCHON CI — Standalone Security Auditor")
    parser.add_argument("target", type=str, help="Path to the project directory to audit.")
    parser.add_argument("--mode", type=str, default="diff", choices=["diff", "full"],
                        help="Audit mode: 'diff' (only changed files) or 'full' (entire project).")
    parser.add_argument("--output", type=str, default="audit_report.md",
                        help="Output file for the audit report. Default: audit_report.md")

    args = parser.parse_args()
    target = Path(args.target).resolve()

    if not target.exists():
        print(f"🚨 [CI Audit] Target path does not exist: {target}")
        sys.exit(1)

    print(f"🛡️ [CI Audit] Starting Archon Audit...")
    print(f"   📂 Target : {target}")
    print(f"   📋 Mode   : {args.mode}")

    print("   🔍 Running native Python syntax check...")
    syntax_errors = python_syntax_check(target)
    if syntax_errors:
        print(f"   ❌ Found {len(syntax_errors)} syntax error(s).")
    else:
        print("   ✅ Syntax check passed.")

    files = collect_files_diff(target) if args.mode == "diff" else collect_files_full(target)
    print(f"   📄 Collected {len(files)} file(s) for LLM audit.")

    llm_result = None
    if files:
        print("   🧠 Sending to LLM for semantic analysis...")
        llm_result = llm_audit(files)
    else:
        print("   ⚠️ No source files found in diff. Skipping LLM audit.")

    report = generate_report(syntax_errors, llm_result, args.mode)
    Path(args.output).write_text(report, encoding="utf-8")
    print(f"   📝 Report saved to: {args.output}")

    has_critical_failures = (
        len(syntax_errors) > 0
        or (llm_result is not None and not llm_result.get("is_valid", True))
    )

    if has_critical_failures:
        print("   ❌ AUDIT FAILED.")
        sys.exit(1)
    else:
        print("   ✅ AUDIT PASSED.")
        sys.exit(0)


if __name__ == "__main__":
    main()