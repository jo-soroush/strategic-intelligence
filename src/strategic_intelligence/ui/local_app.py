"""Minimal local-only WSGI presentation over the approved workflow facade."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import date
from html import escape
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

from strategic_intelligence.application.workflow_application import WorkflowApplication
from strategic_intelligence.domain.models import AnalysisItem, MeetingBrief, MeetingQuestion, MeetingTakeaway, Opportunity, QuickBrief, WorkflowError
from strategic_intelligence.harness.workflow_executor import WorkflowExecutionResult
from strategic_intelligence.observability.logging import configured_secret_values, redact_secrets


_HOST = "127.0.0.1"
_PORT = 8765
_MAX_FORM_BYTES = 16_384
_FORM_FIELDS = (
    "company_name", "executive_name", "meeting_goal", "company_website",
    "company_linkedin_url", "company_country", "company_business_unit",
    "executive_linkedin_url", "executive_current_title", "extra_context",
)


def _text(value: object) -> str:
    return escape(str(value), quote=True)


def _item(item: AnalysisItem) -> str:
    restriction = ""
    if item.is_restricted:
        reasons = ", ".join(reason.value for reason in item.restriction_reason_codes) or "qualification required"
        restriction = f" <strong>RESTRICTED:</strong> {_text(reasons)}"
    rationale = f" <em>{_text(item.rationale)}</em>" if item.rationale else ""
    return f"<li>{_text(item.text)}{restriction}{rationale}</li>"


def _items(title: str, values: Iterable[AnalysisItem]) -> str:
    rendered = "".join(_item(value) for value in values)
    return "" if not rendered else f"<section><h3>{_text(title)}</h3><ul>{rendered}</ul></section>"


def _takeaways(values: Iterable[MeetingTakeaway]) -> str:
    rendered: list[str] = []
    for value in values:
        restriction = ""
        if value.is_restricted:
            reasons = ", ".join(reason.value for reason in value.restriction_reason_codes) or "qualification required"
            restriction = f" <strong>RESTRICTED:</strong> {_text(reasons)}"
        rationale = f" <em>{_text(value.rationale)}</em>" if value.rationale else ""
        rendered.append(f"<li>{_text(value.text)}{restriction}{rationale}</li>")
    return "" if not rendered else f"<section><h3>Meeting takeaways</h3><ul>{''.join(rendered)}</ul></section>"


def _opportunities(values: Iterable[Opportunity]) -> str:
    rendered: list[str] = []
    for value in values:
        restriction = ""
        if value.is_restricted:
            reasons = ", ".join(reason.value for reason in value.restriction_reason_codes) or "qualification required"
            restriction = f" <strong>RESTRICTED:</strong> {_text(reasons)}"
        qualification = f" <em>{_text(value.qualification)}</em>" if value.qualification else ""
        rendered.append(f"<li><strong>{_text(value.title)}</strong>: {_text(value.description)}{restriction}{qualification}</li>")
    return "" if not rendered else f"<section><h3>Opportunities</h3><ul>{''.join(rendered)}</ul></section>"


def _questions(values: Iterable[MeetingQuestion]) -> str:
    rendered: list[str] = []
    for value in values:
        restriction = ""
        if value.is_restricted:
            reasons = ", ".join(reason.value for reason in value.restriction_reason_codes) or "qualification required"
            restriction = f" <strong>RESTRICTED:</strong> {_text(reasons)}"
        qualification = f" <em>{_text(value.qualification)}</em>" if value.qualification else ""
        rendered.append(f"<li>{_text(value.question)} — {_text(value.reason)}{restriction}{qualification}</li>")
    return "" if not rendered else f"<section><h3>Questions</h3><ul>{''.join(rendered)}</ul></section>"


def _omissions(brief: QuickBrief) -> str:
    values: list[str] = []
    if brief.omitted_restriction_count:
        values.append(f"{brief.omitted_restriction_count} governed restriction(s) were omitted from bounded analysis context.")
    if brief.omitted_knowledge_gap_count:
        values.append(f"{brief.omitted_knowledge_gap_count} knowledge gap(s) were omitted from the Quick Brief.")
    return "" if not values else f"<section><h3>Omission disclosures</h3><ul>{''.join(f'<li>{_text(value)}</li>' for value in values)}</ul></section>"


def _quick_brief(brief: QuickBrief) -> str:
    return (
        "<section><h2>Quick Brief</h2>"
        f"{_items('Key facts', brief.key_facts)}{_items('Key signals', brief.key_signals)}"
        f"{_opportunities(brief.top_opportunities)}{_questions(brief.top_questions)}"
        f"{_items('Major risks', brief.major_risks)}{_items('Knowledge gaps', brief.knowledge_gaps)}"
        f"{_omissions(brief)}</section>"
    )


def _full_brief(brief: MeetingBrief) -> str:
    sources = "".join(f"<li>{_text(source)}</li>" for source in brief.source_references)
    do_not_assume = "".join(f"<li>{_text(item)}</li>" for item in brief.do_not_assume)
    return (
        "<section><h2>Full Brief</h2>"
        f"<p>{_text(brief.executive_summary or '')}</p>"
        f"{_takeaways(brief.meeting_takeaways)}"
        f"{_items('Company situation', brief.company_situation)}{_items('Strategy direction', brief.strategy_direction)}"
        f"{_items('Projects and client cases', brief.projects_client_cases)}{_items('AI activity', brief.ai_activity)}"
        f"{_items('Executive intelligence', brief.executive_intelligence)}{_items('Strategic signals', brief.strategic_signals)}"
        f"{_opportunities(brief.opportunity_map)}{_items('User relevance', brief.user_relevance)}"
        f"{_items('Meeting strategy', brief.meeting_strategy)}{_questions(brief.questions)}"
        f"{_items('Knowledge gaps', brief.knowledge_gap_details)}"
        f"<section><h3>Do not assume</h3><ul>{do_not_assume}</ul></section>"
        f"<section><h3>Evidence and sources</h3><ul>{sources}</ul></section></section>"
    )


def _errors(errors: Iterable[WorkflowError]) -> str:
    rendered = "".join(
        f"<li><strong>{_text(error.error_code.value)}</strong> at {_text(error.stage.value if error.stage else 'unknown stage')}: {_text(redact_secrets(error.message, configured_secret_values()))}</li>"
        for error in errors
    )
    return "" if not rendered else f"<section><h3>Workflow errors</h3><ul>{rendered}</ul></section>"


def render_result(result: WorkflowExecutionResult) -> str:
    """Render existing typed workflow output without assigning trust meaning."""
    run = result.workflow_run
    stage = result.state.current_stage or run.current_stage
    brief = result.brief if result.brief and (result.brief.quick_brief or result.brief.full_brief) else None
    presentation = [
        "<section class=\"result\">",
        f"<h2>Status: {_text(result.status.value)}</h2>",
        f"<p>Run ID: <code>{_text(run.run_id)}</code></p>",
        f"<p>Stage: {_text(stage.value if stage else 'not available')}</p>",
    ]
    if brief and brief.quick_brief:
        presentation.append(_quick_brief(brief.quick_brief))
    if brief and brief.full_brief:
        presentation.append(_full_brief(brief.full_brief))
    presentation.append(_errors(result.errors))
    presentation.append("</section>")
    return "".join(presentation)


def _form(values: Mapping[str, str] | None = None) -> str:
    values = values or {}

    def value(name: str) -> str:
        return _text(values.get(name, ""))

    return f"""
    <section><h1>Strategic Intelligence</h1>
    <p>Provide company and executive identity support. C05 validates identity; this interface does not override it.</p>
    <form method=\"post\" action=\"/\">
      <label>Company name <input name=\"company_name\" required value=\"{value('company_name')}\"></label>
      <label>Executive name <input name=\"executive_name\" required value=\"{value('executive_name')}\"></label>
      <label>Meeting goal <textarea name=\"meeting_goal\" required>{value('meeting_goal')}</textarea></label>
      <h2>Company identity support</h2>
      <p>Provide a company website, company LinkedIn URL, or both country and business unit.</p>
      <label>Company website <input name=\"company_website\" value=\"{value('company_website')}\"></label>
      <label>Company LinkedIn URL <input name=\"company_linkedin_url\" value=\"{value('company_linkedin_url')}\"></label>
      <label>Company country <input name=\"company_country\" value=\"{value('company_country')}\"></label>
      <label>Company business unit <input name=\"company_business_unit\" value=\"{value('company_business_unit')}\"></label>
      <h2>Executive identity support</h2>
      <p>Provide an executive LinkedIn URL or current title.</p>
      <label>Executive LinkedIn URL <input name=\"executive_linkedin_url\" value=\"{value('executive_linkedin_url')}\"></label>
      <label>Current title <input name=\"executive_current_title\" value=\"{value('executive_current_title')}\"></label>
      <label>Extra context <textarea name=\"extra_context\">{value('extra_context')}</textarea></label>
      <button type=\"submit\">Prepare brief</button>
    </form></section>
    """


def _page(body: str) -> bytes:
    return ("<!doctype html><html><head><meta charset=\"utf-8\"><title>Strategic Intelligence</title>"
            "</head><body>" + body + "</body></html>").encode("utf-8")


class LocalUi:
    """A thin WSGI adapter over one owned WorkflowApplication instance."""

    def __init__(self, workflow: WorkflowApplication | None, *, startup_error: str | None = None) -> None:
        self._workflow = workflow
        self._startup_error = startup_error

    def __call__(self, environ: Mapping[str, object], start_response) -> list[bytes]:
        method = str(environ.get("REQUEST_METHOD", "GET")).upper()
        if method == "GET":
            return self._respond(start_response, "200 OK", _page(self._startup_message() + _form()))
        if method != "POST":
            return self._respond(start_response, "405 Method Not Allowed", _page("<p>Method not allowed.</p>"))
        if self._workflow is None:
            return self._respond(start_response, "503 Service Unavailable", _page(self._startup_message() + _form()))
        payload, values, error = self._payload(environ)
        if error:
            return self._respond(start_response, "400 Bad Request", _page(f"<p>{_text(error)}</p>" + _form(values)))
        try:
            result = self._workflow.execute(payload, as_of=date.today())
        except Exception:
            return self._respond(start_response, "503 Service Unavailable", _page("<p>Local workflow is unavailable. Check approved local configuration.</p>" + _form(values)))
        return self._respond(start_response, "200 OK", _page(_form(values) + render_result(result)))

    @staticmethod
    def _respond(start_response, status: str, body: bytes) -> list[bytes]:
        start_response(status, [("Content-Type", "text/html; charset=utf-8"), ("Content-Length", str(len(body)))])
        return [body]

    @staticmethod
    def _payload(environ: Mapping[str, object]) -> tuple[dict[str, str], dict[str, str], str | None]:
        raw_length = environ.get("CONTENT_LENGTH", "0")
        try:
            length = int(str(raw_length) or "0")
        except ValueError:
            return {}, {}, "Invalid form request."
        if length < 0 or length > _MAX_FORM_BYTES:
            return {}, {}, "Form request is too large."
        stream = environ.get("wsgi.input")
        if not hasattr(stream, "read"):
            return {}, {}, "Invalid form request."
        try:
            parsed = parse_qs(stream.read(length).decode("utf-8"), keep_blank_values=True, strict_parsing=True)
        except (UnicodeDecodeError, ValueError):
            return {}, {}, "Invalid form request."
        values = {name: parsed.get(name, [""])[0] for name in _FORM_FIELDS}
        payload = {name: value for name, value in values.items() if value or name in {"company_name", "executive_name", "meeting_goal"}}
        return payload, values, None

    def _startup_message(self) -> str:
        return "" if self._startup_error is None else f"<p>{_text(self._startup_error)}</p>"


def create_local_ui() -> tuple[LocalUi, WorkflowApplication | None]:
    """Create the production UI and keep startup configuration errors safe."""
    try:
        workflow = WorkflowApplication.from_environment()
    except Exception:
        return LocalUi(None, startup_error="Local workflow is unavailable. Check approved local configuration."), None
    return LocalUi(workflow), workflow


def run_local_ui() -> None:
    """Serve the minimal UI on the loopback-only V1 local endpoint."""
    ui, workflow = create_local_ui()
    server = make_server(_HOST, _PORT, ui)
    try:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
    finally:
        server.server_close()
        if workflow is not None:
            workflow.close()
