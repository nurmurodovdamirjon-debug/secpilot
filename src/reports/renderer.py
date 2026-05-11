from dataclasses import dataclass


@dataclass(frozen=True)
class ReportDraft:
    title: str
    summary: str
    evidence: list[str]


def render_text_report(report: ReportDraft) -> str:
    evidence = "\n".join(f"- {item}" for item in report.evidence)
    return f"# {report.title}\n\n{report.summary}\n\nEvidence:\n{evidence}\n"
