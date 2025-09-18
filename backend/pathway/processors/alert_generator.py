import pathway as pw


def generate_high_risk_alerts(incidents: pw.Table) -> pw.Table:
    @pw.udf
    def sev_to_score(sev: str) -> float:
        return {"low": 0.1, "medium": 0.5, "high": 0.9}.get(str(sev).lower(), 0.3)

    scored = incidents + incidents.select(risk_score=sev_to_score(pw.this.severity))
    return scored.filter(pw.this.risk_score >= 0.8).select(
        id=pw.this.id,
        type=pw.make_const("safety"),
        message=pw.this.description,
        priority=pw.make_const("high"),
    )


