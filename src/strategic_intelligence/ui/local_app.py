"""Minimal local-only WSGI presentation over the approved workflow facade."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import date
from html import escape
from pathlib import Path
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

from strategic_intelligence.application.workflow_application import WorkflowApplication
from strategic_intelligence.domain.models import AnalysisItem, MeetingBrief, MeetingQuestion, MeetingTakeaway, Opportunity, QuickBrief, ResearchCategory, WorkflowError
from strategic_intelligence.harness.workflow_executor import WorkflowExecutionResult
from strategic_intelligence.observability.logging import configured_secret_values, redact_secrets


_HOST = "127.0.0.1"
_PORT = 8765
_MAX_FORM_BYTES = 16_384
_DISPLAY_TEXT_LIMIT = 280
_MEETING_ROOM_ASSET = "strategic-intelligence-meeting-room.webp"
_ASSET_ROOT = Path(__file__).with_name("assets")
_FORM_FIELDS = (
    "company_name", "executive_name", "meeting_goal", "company_website",
    "company_linkedin_url", "company_country", "company_business_unit",
    "executive_linkedin_url", "executive_current_title", "extra_context",
)


def _text(value: object) -> str:
    return escape(str(value), quote=True)


def _display_text(value: object, *, clamp: bool = True) -> str:
    value = str(value)
    if clamp and len(value) > _DISPLAY_TEXT_LIMIT:
        return _text(value[:_DISPLAY_TEXT_LIMIT].rstrip() + "…")
    return _text(value)


def _item(item: AnalysisItem, *, clamp: bool = True) -> str:
    restriction = ""
    if item.is_restricted:
        reasons = ", ".join(reason.value for reason in item.restriction_reason_codes) or "qualification required"
        restriction = f" <strong>RESTRICTED:</strong> {_text(reasons)}"
    rationale = f" <em>{_display_text(item.rationale, clamp=clamp)}</em>" if item.rationale else ""
    return f"<li class=\"brief-card\"><span>{_display_text(item.text, clamp=clamp)}</span>{restriction}{rationale}</li>"


def _items(title: str, values: Iterable[AnalysisItem], *, limit: int | None = None, clamp: bool = True) -> str:
    values = list(values)
    if limit is not None:
        values = values[:limit]
    rendered = "".join(_item(value, clamp=clamp) for value in values)
    return "" if not rendered else f"<section class=\"brief-section\"><h3>{_text(title)}</h3><ul>{rendered}</ul></section>"


def _takeaways(values: Iterable[MeetingTakeaway], *, limit: int | None = None, clamp: bool = True) -> str:
    rendered: list[str] = []
    for value in list(values)[:limit] if limit is not None else values:
        restriction = ""
        if value.is_restricted:
            reasons = ", ".join(reason.value for reason in value.restriction_reason_codes) or "qualification required"
            restriction = f" <strong>RESTRICTED:</strong> {_text(reasons)}"
        rationale = f" <em>{_display_text(value.rationale, clamp=clamp)}</em>" if value.rationale else ""
        rendered.append(f"<li class=\"brief-card\"><span>{_display_text(value.text, clamp=clamp)}</span>{restriction}{rationale}</li>")
    return "" if not rendered else f"<section class=\"brief-section\"><h3>What You Need to Know</h3><ul>{''.join(rendered)}</ul></section>"


def _opportunities(values: Iterable[Opportunity], *, limit: int | None = None, clamp: bool = True) -> str:
    rendered: list[str] = []
    for value in list(values)[:limit] if limit is not None else values:
        restriction = ""
        if value.is_restricted:
            reasons = ", ".join(reason.value for reason in value.restriction_reason_codes) or "qualification required"
            restriction = f" <strong>RESTRICTED:</strong> {_text(reasons)}"
        qualification = f" <em>{_display_text(value.qualification, clamp=clamp)}</em>" if value.qualification else ""
        rendered.append(f"<li class=\"brief-card\"><strong>{_display_text(value.title, clamp=clamp)}</strong>: {_display_text(value.description, clamp=clamp)}{restriction}{qualification}</li>")
    return "" if not rendered else f"<section class=\"brief-section\"><h3>Opportunities</h3><ul>{''.join(rendered)}</ul></section>"


def _questions(values: Iterable[MeetingQuestion], *, limit: int | None = None, clamp: bool = True) -> str:
    rendered: list[str] = []
    for value in list(values)[:limit] if limit is not None else values:
        restriction = ""
        if value.is_restricted:
            reasons = ", ".join(reason.value for reason in value.restriction_reason_codes) or "qualification required"
            restriction = f" <strong>RESTRICTED:</strong> {_text(reasons)}"
        qualification = f" <em>{_display_text(value.qualification, clamp=clamp)}</em>" if value.qualification else ""
        rendered.append(f"<li class=\"brief-card\"><span>{_display_text(value.question, clamp=clamp)}</span> <span class=\"supporting-text\">— {_display_text(value.reason, clamp=clamp)}</span>{restriction}{qualification}</li>")
    return "" if not rendered else f"<section class=\"brief-section\"><h3>Questions to Ask</h3><ul>{''.join(rendered)}</ul></section>"


def _detail_items(title: str, values: Iterable[AnalysisItem]) -> str:
    rendered = _items(title, values, clamp=False)
    return rendered or f'<section class="brief-section"><h3>{_text(title)}</h3><p class="empty">No governed items are available.</p></section>'


def _detail_takeaways(values: Iterable[MeetingTakeaway]) -> str:
    rendered = _takeaways(values, clamp=False)
    return rendered or '<section class="brief-section"><h3>What You Need to Know</h3><p class="empty">No governed takeaways are available.</p></section>'


def _detail_opportunities(values: Iterable[Opportunity]) -> str:
    rendered = _opportunities(values, clamp=False)
    return rendered or '<section class="brief-section"><h3>Opportunities</h3><p class="empty">No governed opportunities are available.</p></section>'


def _detail_questions(values: Iterable[MeetingQuestion]) -> str:
    rendered = _questions(values, clamp=False)
    return rendered or '<section class="brief-section"><h3>Questions to Ask</h3><p class="empty">No governed questions are available.</p></section>'


def _omissions(brief: QuickBrief) -> str:
    values: list[str] = []
    if brief.omitted_restriction_count:
        values.append(f"{brief.omitted_restriction_count} governed restriction(s) were omitted from bounded analysis context.")
    if brief.omitted_knowledge_gap_count:
        values.append(f"{brief.omitted_knowledge_gap_count} knowledge gap(s) were omitted from the Quick Brief.")
    return "" if not values else f"<section class=\"notice\"><h3>Omission disclosures</h3><ul>{''.join(f'<li>{_text(value)}</li>' for value in values)}</ul></section>"


def _executive_banner(items: Iterable[AnalysisItem]) -> str:
    items = list(items)
    if items and not all(item.is_restricted for item in items):
        return ""
    return (
        '<div class="notice executive-gap" role="status">'
        "<strong>Executive evidence is limited.</strong> Available public-professional "
        "sources do not support a confident executive profile. Validate this context in the meeting."
        "</div>"
    )


def _executive_items(brief: MeetingBrief, result: WorkflowExecutionResult) -> list[AnalysisItem]:
    """Keep the executive card presentation scoped to governed executive claims."""
    executive_topics = {
        ResearchCategory.EXECUTIVE_ROLE.value,
        ResearchCategory.EXECUTIVE_FOCUS.value,
        ResearchCategory.PUBLICATIONS.value,
        ResearchCategory.INTERVIEWS.value,
        ResearchCategory.PUBLIC_ACTIVITY.value,
    }
    claims = {claim.claim_id: claim for claim in result.state.claims}
    return [
        item for item in brief.executive_intelligence
        if item.related_claim_ids
        and all(claims.get(claim_id) is not None and claims[claim_id].topic in executive_topics for claim_id in item.related_claim_ids)
    ][:5]


def _evidence(brief: MeetingBrief, result: WorkflowExecutionResult) -> str:
    """Render only existing, safe provenance and source references."""
    sources = [source.strip() for source in brief.source_references if source.strip() and source.strip() != "-"]
    blocked_ids = {
        decision.target_id for decision in result.state.governance_decisions
        if decision.decision.value == "BLOCK"
    }
    items = [
        *brief.meeting_takeaways, *brief.executive_intelligence, *brief.company_situation,
        *brief.strategy_direction, *brief.projects_client_cases, *brief.ai_activity,
        *brief.strategic_signals, *brief.user_relevance, *brief.meeting_strategy,
        *brief.knowledge_gap_details,
    ]
    claim_ids = sorted({
        claim_id
        for item in items
        for claim_id in (item.supporting_claim_ids if isinstance(item, MeetingTakeaway) else item.related_claim_ids)
        if claim_id not in blocked_ids
    })
    source_markup = "".join(f'<li class="brief-card">{_text(source)}</li>' for source in sources)
    claim_markup = "".join(f'<li class="brief-card">Claim reference: {_text(claim_id)}</li>' for claim_id in claim_ids)
    governance_markup = "".join(
        f'<li class="brief-card">Governance: RESTRICTED — {_text(", ".join(reason.value for reason in item.restriction_reason_codes) or "qualification required")}</li>'
        for item in items
        if item.is_restricted
        and all(claim_id not in blocked_ids for claim_id in (item.supporting_claim_ids if isinstance(item, MeetingTakeaway) else item.related_claim_ids))
    )
    if not source_markup and not claim_markup and not governance_markup:
        return '<p class="empty">No safe source or provenance references are available.</p>'
    source_list = source_markup or '<li class="empty">No safe source references are available.</li>'
    claim_list = claim_markup or '<li class="empty">No provenance references are available.</li>'
    governance_list = governance_markup or '<li class="empty">No governance qualifications are recorded.</li>'
    return (
        f'<section class="brief-section"><h3>Sources</h3><ul>{source_list}</ul></section>'
        f'<section class="brief-section"><h3>Provenance</h3><ul>{claim_list}</ul></section>'
        f'<section class="brief-section"><h3>Governance</h3><ul>{governance_list}</ul></section>'
    )


def _meeting_snapshot(result: WorkflowExecutionResult) -> str:
    case = result.state.case_context
    if case is None:
        return "<section class=\"snapshot brief-section\"><h2>Meeting Snapshot</h2><p>Case context is not available.</p></section>"
    return (
        '<section class="snapshot brief-section"><h2>Meeting Snapshot</h2>'
        f"<p class=\"snapshot-company\">{_text(case.company_name)}</p>"
        f"<p><strong>Executive:</strong> {_text(case.executive_name)}</p>"
        f"<p><strong>Goal:</strong> {_display_text(case.meeting_goal)}</p></section>"
    )


def _quick_brief(brief: QuickBrief, full: MeetingBrief | None, result: WorkflowExecutionResult) -> str:
    executive_values = [] if full is None else _executive_items(full, result)
    executive_cards = "".join(_item(item) for item in executive_values)
    executive = (
        '<section class="brief-section"><h2>Executive Intelligence</h2>'
        f"{_executive_banner(executive_values)}"
        f"<ul>{executive_cards}</ul></section>"
    )
    signals = "".join(_item(item) for item in list(brief.key_signals)[:3])
    opportunities = _opportunities(brief.top_opportunities, limit=2)
    risks = "".join(_item(item) for item in list(brief.major_risks)[:2])
    gaps = "".join(_item(item) for item in list(brief.knowledge_gaps)[:3])
    takeaways = _takeaways([] if full is None else full.meeting_takeaways, limit=5)
    questions = _questions(brief.top_questions, limit=3)
    takeaways = takeaways or '<section class="brief-section"><h2>What You Need to Know</h2><p class="empty">No governed takeaways are available.</p></section>'
    questions = questions or '<section class="brief-section"><h2>Questions to Ask</h2><p class="empty">No governed questions are available.</p></section>'
    return (
        '<section class="default-brief" aria-label="Meeting brief"><div class="brief-grid">'
        f'<section class="result-card">{takeaways}</section>'
        f'<section class="result-card">{executive}</section>'
        '<section class="result-card"><section class="brief-section"><h2>Strategic View</h2><div class="section-grid">'
        f"<section><h3>Signals</h3><ul>{signals}</ul></section>"
        f"{_opportunities(brief.top_opportunities, limit=2)}"
        f"<section><h3>Risks</h3><ul>{risks}</ul></section></div></section></section>"
        f'<section class="result-card">{questions}</section>'
        f'<section class="result-card"><section class="brief-section"><h2>Knowledge Gaps</h2><ul>{gaps}</ul></section></section>'
        f"</div>{_omissions(brief)}</section>"
    )


def _full_brief(brief: MeetingBrief, result: WorkflowExecutionResult) -> str:
    do_not_assume = "".join(
        f'<li class="brief-card">{_display_text(item, clamp=False)}</li>' for item in brief.do_not_assume
    )
    return (
        '<details class="disclosure"><summary>Details</summary><section><h2>Full Brief</h2>'
        f"<p>{_display_text(brief.executive_summary or '', clamp=False)}</p>"
        f"{_detail_takeaways(brief.meeting_takeaways)}"
        f"{_detail_items('Executive intelligence', _executive_items(brief, result))}"
        f"{_detail_items('Company situation', brief.company_situation)}{_detail_items('Strategy direction', brief.strategy_direction)}"
        f"{_detail_items('Projects and client cases', brief.projects_client_cases)}{_detail_items('AI activity', brief.ai_activity)}"
        f"{_detail_items('Strategic signals', brief.strategic_signals)}"
        f"{_detail_opportunities(brief.opportunity_map)}{_detail_items('User relevance', brief.user_relevance)}"
        f"{_detail_items('Meeting strategy', brief.meeting_strategy)}{_detail_questions(brief.questions)}"
        f"{_detail_items('Knowledge gaps', brief.knowledge_gap_details)}"
        f"<section class=\"brief-section\"><h3>Do not assume</h3><ul>{do_not_assume}</ul></section>"
        '<details class="nested-disclosure"><summary>Evidence</summary>'
        f"{_evidence(brief, result)}</details></section></details>"
    )


def _brief_preview() -> str:
    """Static entry-screen preview; it does not imply another product feature."""
    cards = (
        ("Meeting Brief", "A focused view for the room."),
        ("What You Need to Know", "Bounded takeaways first."),
        ("Executive Intelligence", "Public, professional, relevant."),
        ("Strategic View", "Signals, opportunities, and risks."),
        ("Questions to Ask", "Prompts grounded in the goal."),
        ("Knowledge Gaps", "Uncertainty stays visible."),
    )
    return (
        '<section class="preview-section" aria-labelledby="preview-heading">'
        '<p class="eyebrow">Brief Preview</p><h2 id="preview-heading">From research to ready.</h2>'
        '<p class="preview-copy">A calm, concise brief that keeps evidence and uncertainty in view.</p>'
        '<div class="preview-grid">'
        + "".join(
            f'<article class="preview-card"><span class="preview-icon" aria-hidden="true">{index:02d}</span><h3>{_text(title)}</h3><p>{_text(copy)}</p></article>'
            for index, (title, copy) in enumerate(cards, start=1)
        )
        + "</div></section>"
    )


def _errors(errors: Iterable[WorkflowError]) -> str:
    rendered = "".join(
        f"<li><strong>{_text(error.error_code.value)}</strong> at {_text(error.stage.value if error.stage else 'unknown stage')}: {_text(redact_secrets(error.message, configured_secret_values()))}</li>"
        for error in errors
    )
    return "" if not rendered else f"<section class=\"notice error\"><h3>Workflow errors</h3><ul>{rendered}</ul></section>"


def render_result(result: WorkflowExecutionResult) -> str:
    """Render existing typed workflow output without assigning trust meaning."""
    run = result.workflow_run
    stage = result.state.current_stage or run.current_stage
    brief = result.brief if result.brief and (result.brief.quick_brief or result.brief.full_brief) else None
    status_class = result.status.value.lower()
    case = result.state.case_context
    snapshot = (
        '<p class="eyebrow">Meeting Brief · Meeting Snapshot</p>'
        f'<h2>{_text(case.company_name) if case else "Meeting Brief"}</h2>'
        f'<p class="result-context"><strong>Executive:</strong> {_text(case.executive_name) if case else "Not available"} '
        f'<span aria-hidden="true">·</span> <strong>Goal:</strong> {_display_text(case.meeting_goal) if case else "Not available"}</p>'
    )
    presentation = [
        f'<section class="result {status_class}" aria-live="polite">',
        f'<div class="result-header"><div>{snapshot}</div><div class="status-stack"><div class="status-pill" role="status">Status: {_text(result.status.value)}</div>'
        f'<p class="status-meta"><span>Stage: {_text(stage.value if stage else "not available")}</span><span>Run ID: <code>{_text(run.run_id)}</code></span></p></div></div>',
    ]
    if brief and brief.quick_brief:
        presentation.append(_quick_brief(brief.quick_brief, brief.full_brief, result))
    if brief and brief.full_brief:
        presentation.append(_full_brief(brief.full_brief, result))
    presentation.append(_errors(result.errors))
    presentation.append("</section>")
    return "".join(presentation)


def _form(values: Mapping[str, str] | None = None) -> str:
    values = values or {}

    def value(name: str) -> str:
        return _text(values.get(name, ""))

    return f"""
    <section class="entry-screen">
      <header class="brand-header"><div class="brand-lockup"><span class="brand-mark" aria-hidden="true">SI</span><div><p class="brand-name">Strategic Intelligence</p><p class="brand-tagline">Executive meeting intelligence</p></div></div><nav class="visual-nav" aria-hidden="true"><span>Home</span><span>Library</span><span>Insights</span><span>Settings</span></nav><div class="visual-tools" aria-hidden="true"><span class="visual-search">Search</span></div></header>
      <div class="entry-layout">
        <section class="case-form-card"><p class="eyebrow">Meeting intelligence</p><h1>Prepare for the conversation that matters.</h1>
        <p class="lede">Build a focused, evidence-led brief from bounded public research.</p>
        <form method="post" action="/" class="case-form" aria-describedby="form-note">
      <fieldset><legend>Meeting context</legend>
        <label for="company_name">Company name <span aria-hidden="true">*</span></label>
        <input id="company_name" name="company_name" required autocomplete="organization" value="{value('company_name')}">
        <label for="executive_name">Executive name <span aria-hidden="true">*</span></label>
        <input id="executive_name" name="executive_name" required autocomplete="name" value="{value('executive_name')}">
        <label for="meeting_goal">Meeting goal <span aria-hidden="true">*</span></label>
        <textarea id="meeting_goal" name="meeting_goal" required rows="3">{value('meeting_goal')}</textarea>
      </fieldset>
      <p id="form-note" class="form-note">Identity support helps C05 resolve the intended company and executive. Validation remains application-owned.</p>
      <details class="form-support"><summary>Identity support <span>Optional context for entity resolution</span></summary>
        <fieldset>
          <legend class="sr-only">Company identity support</legend>
          <label for="company_website">Company website</label><input id="company_website" name="company_website" inputmode="url" value="{value('company_website')}">
          <label for="company_linkedin_url">Company LinkedIn URL</label><input id="company_linkedin_url" name="company_linkedin_url" inputmode="url" value="{value('company_linkedin_url')}">
          <label for="company_country">Company country</label><input id="company_country" name="company_country" value="{value('company_country')}">
          <label for="company_business_unit">Company business unit</label><input id="company_business_unit" name="company_business_unit" value="{value('company_business_unit')}">
          <label for="executive_linkedin_url">Executive LinkedIn URL</label><input id="executive_linkedin_url" name="executive_linkedin_url" inputmode="url" value="{value('executive_linkedin_url')}">
          <label for="executive_current_title">Current title</label><input id="executive_current_title" name="executive_current_title" value="{value('executive_current_title')}">
          <label for="extra_context">Extra context</label><textarea id="extra_context" name="extra_context" rows="3">{value('extra_context')}</textarea>
        </fieldset>
      </details>
      <button type="submit"><span>Prepare brief</span><span class="button-loading" aria-hidden="true">Preparing…</span></button>
      <p class="loading-status" role="status" aria-live="polite" hidden>Preparing your brief. This may take a moment.</p>
        </form></section>
        <aside class="context-panel"><div class="panel-visual"><img class="meeting-room-image" src="/assets/strategic-intelligence-meeting-room.webp" alt="Modern executive meeting room with a city view"><div class="panel-overlay"><p class="eyebrow">Built for the room</p><h2>Know what matters before you walk in.</h2><p>Public research becomes governed evidence and meeting-ready insight, with gaps kept visible.</p><div class="chip-list" aria-label="Brief qualities"><span>Public-source research</span><span>Governed evidence</span><span>Meeting-ready insights</span></div></div></div></aside>
      </div>
    </section>
    {_brief_preview()}
    """


def _page(body: str) -> bytes:
    style = """
    :root { color-scheme: light; --ink:#17232d; --muted:#5e6d78; --line:#dbe3e8; --paper:#f6f8f9; --accent:#1d5960; --accent-soft:#e7f1f0; --danger:#8a2f2f; }
    * { box-sizing:border-box; } body { margin:0; background:var(--paper); color:var(--ink); font:16px/1.55 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }
    main { width:min(86vw, 1360px); margin:0 auto; padding:48px 0 80px; } h1,h2,h3 { line-height:1.2; letter-spacing:-.025em; } h1 { font-size:clamp(2.35rem,5.6vw,4.15rem); max-width:12ch; margin:.35rem 0 1.1rem; } h2 { font-size:1.55rem; } h3 { font-size:1rem; margin:0 0 .75rem; } p { margin:.35rem 0 1rem; } .eyebrow { color:var(--accent); font-size:.75rem; font-weight:800; letter-spacing:.14em; text-transform:uppercase; } .lede { color:var(--muted); font-size:1.12rem; max-width:52ch; }
    .entry-screen { min-height:calc(100vh - 112px); } .brand-header { align-items:center; display:flex; gap:24px; justify-content:space-between; margin-bottom:58px; } .brand-lockup { align-items:center; display:flex; gap:16px; } .brand-mark { align-items:center; background:linear-gradient(145deg,#246b70,#123e4a); border-radius:13px; box-shadow:0 8px 18px #1d596044; color:#fff; display:flex; font-size:.9rem; font-weight:900; height:52px; justify-content:center; letter-spacing:.1em; width:52px; } .brand-name { color:var(--ink); font-size:1.45rem; font-weight:900; letter-spacing:-.035em; margin:0; } .brand-tagline { color:var(--muted); font-size:.86rem; margin:3px 0 0; } .visual-nav { align-items:center; color:#536871; display:flex; font-size:.86rem; font-weight:650; gap:24px; margin-left:auto; } .visual-nav span { border-bottom:2px solid transparent; padding:7px 0; } .visual-nav span:first-child { border-color:#8bc4be; color:var(--accent); } .visual-tools { align-items:center; color:var(--muted); display:flex; gap:10px; } .visual-search { border:1px solid var(--line); border-radius:999px; font-size:.78rem; min-width:108px; padding:7px 13px; } .utility-mark { align-items:center; background:#e2efed; border:1px solid #bfdad7; border-radius:50%; color:var(--accent); display:flex; font-size:.63rem; font-weight:850; height:31px; justify-content:center; width:31px; } .entry-layout { align-items:stretch; display:grid; gap:40px; grid-template-columns:minmax(0,3fr) minmax(300px,2fr); } .case-form-card,.context-panel,.result { background:#fff; border:1px solid var(--line); border-radius:22px; box-shadow:0 16px 42px #18313d10; padding:clamp(30px,4vw,52px); } .context-panel { background:linear-gradient(145deg,#f8fcfb 0%,#e5f1ef 100%); border-color:#bfdad7; box-shadow:0 16px 38px #1d596018; color:var(--ink); display:flex; flex-direction:column; justify-content:center; min-height:480px; overflow:hidden; position:relative; } .context-panel .eyebrow { color:var(--accent); position:relative; } .context-panel p:not(.eyebrow) { color:#40555d; position:relative; } .context-panel h2 { max-width:15ch; position:relative; } .panel-visual { height:240px; margin:-8px -8px 24px; overflow:hidden; position:relative; border-radius:16px; box-shadow:0 12px 26px #18313d18; } .panel-visual::before { display:none; } .panel-visual::after { background:linear-gradient(135deg,#0d4f5755,#d8efeb22); content:""; inset:0; pointer-events:none; position:absolute; } .meeting-room-image { display:block; height:100%; object-fit:cover; object-position:center; width:100%; } .visual-orb,.visual-line,.visual-window { display:none; } .chip-list { display:flex; flex-wrap:wrap; gap:11px; margin-top:26px; position:relative; } .chip-list span { background:#fff; border:1px solid #a8cfca; border-radius:999px; box-shadow:0 4px 9px #1d596014; color:var(--accent); font-size:.8rem; font-weight:750; line-height:1.25; padding:9px 13px; transition:background .18s ease, border-color .18s ease, transform .18s ease; } .chip-list span:hover { background:#f0f8f7; border-color:#6ca9a4; transform:translateY(-1px); } fieldset { border:0; margin:0; padding:0; display:grid; gap:14px; } legend { font-size:1.25rem; font-weight:800; margin-bottom:18px; } label { font-weight:650; margin-top:13px; } input,textarea { width:100%; border:1px solid #a5b9c1; border-radius:11px; color:var(--ink); background:#fff; font:inherit; padding:14px 15px; transition:border-color .18s ease, box-shadow .18s ease; } input:hover,textarea:hover { border-color:#6e9ea5; } input:focus,textarea:focus,summary:focus-visible,button:focus-visible { outline:3px solid #9bd0cb; outline-offset:2px; } input:focus,textarea:focus { border-color:var(--accent); box-shadow:0 0 0 4px #9bd0cb33; } textarea { resize:vertical; } .form-note,.form-support summary span { color:var(--muted); font-size:.9rem; } .form-support { border-top:1px solid var(--line); margin-top:30px; padding-top:21px; } .form-support summary,.disclosure summary { cursor:pointer; font-weight:700; color:var(--accent); } .form-support summary span { font-weight:400; margin-left:8px; } button { display:block; margin-top:30px; border:0; border-radius:11px; background:linear-gradient(135deg,#246b70,#164950); box-shadow:0 10px 20px #1d596044; color:#fff; cursor:pointer; font:800 1.08rem inherit; padding:17px 24px; transition:box-shadow .18s ease, transform .18s ease, background .18s ease; width:100%; } button:hover { background:linear-gradient(135deg,#2c7b7d,#16474d); box-shadow:0 13px 24px #1d596055; transform:translateY(-1px); } button:active { transform:translateY(0); } button:disabled { cursor:wait; opacity:.75; } .button-loading { display:none; } button[aria-busy="true"] .button-loading { display:inline; } button[aria-busy="true"] > span:first-child { display:none; } .loading-status { color:var(--accent); margin-top:14px; }
    .preview-section { margin:78px 0 8px; } .preview-section h2 { font-size:clamp(1.8rem,3vw,2.55rem); margin:.35rem 0 .5rem; } .preview-copy { color:var(--muted); margin-bottom:24px; } .preview-grid { display:grid; gap:14px; grid-template-columns:repeat(3,minmax(0,1fr)); } .preview-card { background:#fff; border:1px solid var(--line); border-radius:14px; box-shadow:0 8px 22px #18313d08; min-height:130px; padding:18px; transition:border-color .18s ease, box-shadow .18s ease, transform .18s ease; } .preview-card:hover { border-color:#b7d4d1; box-shadow:0 12px 26px #18313d12; transform:translateY(-2px); } .preview-icon { color:var(--accent); display:inline-block; font-size:.7rem; font-weight:850; letter-spacing:.08em; margin-bottom:14px; } .preview-card h3 { margin-bottom:6px; } .preview-card p { color:var(--muted); font-size:.86rem; margin:0; } .result { margin-top:30px; } .result-header { align-items:flex-start; border-bottom:1px solid var(--line); display:flex; gap:20px; justify-content:space-between; margin-bottom:26px; padding-bottom:20px; } .result-header h2 { margin:.2rem 0 0; } .result-context { color:var(--muted); margin-bottom:0; } .status-stack { align-items:flex-end; display:flex; flex-direction:column; gap:8px; } .status-pill { background:var(--accent-soft); border:1px solid #c7dfdc; border-radius:999px; color:var(--accent); font-size:.78rem; font-weight:800; letter-spacing:.08em; padding:8px 13px; } .status-meta { color:var(--muted); display:grid; font-size:.75rem; gap:2px; margin:0; text-align:right; } code { overflow-wrap:anywhere; } .brief-grid { display:grid; gap:20px; grid-template-columns:repeat(2,minmax(0,1fr)); } .result-card { background:#fbfcfc; border:1px solid var(--line); border-radius:15px; padding:4px 18px 18px; transition:border-color .18s ease, box-shadow .18s ease, transform .18s ease; } .result-card:hover { border-color:#b7d4d1; box-shadow:0 8px 18px #18313d0b; transform:translateY(-1px); } .result-card:first-child { grid-column:span 2; } .brief-section { margin-top:24px; } .brief-section h2 { margin-bottom:14px; } .brief-section ul,.notice ul { list-style:none; margin:0; padding:0; } .section-grid { display:grid; gap:16px; grid-template-columns:repeat(3,minmax(0,1fr)); } .brief-card { background:#fff; border:1px solid var(--line); border-radius:10px; margin:8px 0; padding:12px 14px; } .supporting-text { color:var(--muted); } .empty { color:var(--muted); font-style:italic; } .snapshot { background:var(--accent-soft); border-color:#c7dfdc; } .snapshot-company { font-size:1.3rem; font-weight:750; margin-bottom:4px; } .notice { background:#fff8e7; border:1px solid #ead49a; border-radius:10px; margin-top:18px; padding:14px 16px; } .error { background:#fff4f4; border-color:#e4baba; color:var(--danger); } .disclosure { border-top:1px solid var(--line); margin-top:30px; padding-top:20px; } .disclosure > section { margin-top:18px; } .nested-disclosure { border-top:1px solid var(--line); margin-top:22px; padding-top:16px; } .nested-disclosure > section { margin-top:16px; } .sr-only { clip:rect(0 0 0 0); clip-path:inset(50%); height:1px; overflow:hidden; position:absolute; white-space:nowrap; width:1px; } .partial .status-pill { background:#fff8e7; border-color:#ead49a; color:#87611b; } .failed .status-pill { background:#fff4f4; border-color:#e4baba; color:var(--danger); }
    @media (max-width:960px) { main { width:calc(100% - 48px); } .entry-layout { gap:24px; grid-template-columns:minmax(0,1fr) minmax(260px,1fr); } .case-form-card,.result { padding:28px; } .context-panel { padding:0; } } @media (max-width:760px) { main { width:calc(100% - 32px); } .entry-layout,.brief-grid { grid-template-columns:1fr; } .result-card:first-child { grid-column:auto; } .section-grid { grid-template-columns:1fr; } .context-panel { min-height:0; } .preview-section { margin-top:54px; } .preview-grid { grid-template-columns:repeat(2,minmax(0,1fr)); } } @media (max-width:640px) { main { padding-top:28px; } .brand-header { margin-bottom:34px; } .brand-mark { height:46px; width:46px; } .brand-name { font-size:1.25rem; } .result-header { display:block; } .status-stack { align-items:flex-start; margin-top:14px; } .status-meta { text-align:left; } .form-support summary span { display:block; margin:3px 0 0; } .preview-grid { grid-template-columns:1fr; } }
    main { width:min(1440px,calc(100vw - 64px)); padding-top:32px; } .brand-header { min-height:64px; margin-bottom:34px; } .brand-mark { height:58px; width:58px; } .brand-name { font-size:clamp(1.65rem,2.4vw,2.15rem); } .visual-nav { align-items:center; display:flex; gap:26px; margin-left:auto; } .visual-nav span { color:#536871; padding:7px 0; } .visual-tools { display:flex; } .visual-search { background:#fff; min-width:118px; } .entry-layout { grid-template-columns:minmax(0,44fr) minmax(0,56fr); gap:24px; } .case-form-card { padding:clamp(26px,3vw,40px); } .case-form-card h1 { font-size:clamp(3.15rem,5vw,4.2rem); line-height:1.02; } .case-form-card .lede { margin-bottom:24px; } .context-panel { min-height:560px; padding:0; } .panel-visual { height:100%; min-height:560px; margin:0; border-radius:21px; box-shadow:none; } .meeting-room-image { inset:0; position:absolute; } .panel-visual::after { background:linear-gradient(90deg,#062f37a8 0%,#062f3755 46%,#06242d22 100%),linear-gradient(180deg,#082f3820 12%,#06242dcc 100%); } .panel-overlay { bottom:0; color:#fff; left:0; padding:clamp(28px,4vw,46px); position:absolute; right:0; z-index:1; } .panel-overlay .eyebrow { color:#b8e4dc; } .panel-overlay h2 { color:#fff; font-size:clamp(2rem,3.5vw,3.2rem); line-height:1.05; margin:.4rem 0 .8rem; max-width:13ch; } .panel-overlay p:not(.eyebrow) { color:#edf8f6; max-width:45ch; } .panel-overlay .chip-list { margin-top:22px; } .panel-overlay .chip-list span { background:#ffffffea; border-color:#d1eee8; color:#174f55; } .preview-section { margin-top:38px; } .preview-grid { grid-template-columns:repeat(6,minmax(0,1fr)); } .preview-card { min-height:142px; padding:16px; }
    @media (max-width:1100px) { .visual-nav { gap:16px; } .entry-layout { grid-template-columns:minmax(0,1fr) minmax(0,1.08fr); } .preview-grid { grid-template-columns:repeat(3,minmax(0,1fr)); } }
    @media (max-width:760px) { main { width:calc(100% - 32px); } .brand-header { align-items:flex-start; } .visual-nav,.visual-tools { display:none; } .entry-layout,.brief-grid { grid-template-columns:1fr; } .context-panel { min-height:500px; } .panel-visual { min-height:500px; } .case-form-card h1 { font-size:clamp(2.7rem,11vw,3.6rem); } .preview-section { margin-top:38px; } .preview-grid { grid-template-columns:repeat(2,minmax(0,1fr)); } }
    @media (max-width:480px) { .preview-grid { grid-template-columns:1fr; } .brand-name { font-size:1.55rem; } }
    main { width:min(1480px,92vw); padding-top:24px; } .brand-header { margin-bottom:26px; } .entry-layout { gap:22px; } .case-form-card { padding:clamp(24px,2.6vw,34px); } .case-form-card .lede { margin-bottom:18px; } fieldset { gap:10px; } label { margin-top:8px; } input,textarea { padding:11px 13px; } textarea { min-height:84px; } .form-support { margin-top:22px; padding-top:16px; } button { margin-top:22px; padding:14px 20px; } .context-panel,.panel-visual { min-height:500px; } .preview-section { margin-top:28px; }
    @media (max-width:760px) { main { width:calc(100% - 32px); padding-top:24px; } .context-panel,.panel-visual { min-height:460px; } }
    """
    script = """
    document.addEventListener('DOMContentLoaded', function () {
      const form = document.querySelector('.case-form');
      if (!form) return;
      form.addEventListener('submit', function () {
        const button = form.querySelector('button');
        const status = form.querySelector('.loading-status');
        button.disabled = true; button.setAttribute('aria-busy', 'true');
        status.hidden = false;
      });
    });
    """
    return ("<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"><title>Strategic Intelligence</title>"
            f"<style>{style}</style></head><body><main>{body}</main><script>{script}</script></body></html>").encode("utf-8")


class LocalUi:
    """A thin WSGI adapter over one owned WorkflowApplication instance."""

    def __init__(self, workflow: WorkflowApplication | None, *, startup_error: str | None = None) -> None:
        self._workflow = workflow
        self._startup_error = startup_error

    def __call__(self, environ: Mapping[str, object], start_response) -> list[bytes]:
        method = str(environ.get("REQUEST_METHOD", "GET")).upper()
        path = str(environ.get("PATH_INFO", "/"))
        if method == "GET" and path == f"/assets/{_MEETING_ROOM_ASSET}":
            return self._asset_response(start_response)
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
    def _asset_response(start_response) -> list[bytes]:
        try:
            body = (_ASSET_ROOT / _MEETING_ROOM_ASSET).read_bytes()
        except OSError:
            return LocalUi._respond(start_response, "404 Not Found", b"Asset not found.")
        start_response("200 OK", [("Content-Type", "image/png"), ("Content-Length", str(len(body)))])
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
