import pathway as pw


def run_pipeline(incidents_path: str = "data/streams/incidents") -> None:
    incidents = pw.io.csv.read(incidents_path, mode="streaming", infer_schema=True)

    @pw.udf
    def severity_to_score(sev: str) -> float:
        return {"low": 0.1, "medium": 0.5, "high": 0.9}.get(str(sev).lower(), 0.3)

    incidents = incidents + incidents.select(risk_score=severity_to_score(pw.this.severity))

    alerts = incidents.filter(pw.this.risk_score >= 0.8).select(
        id=pw.this.id,
        type=pw.make_const("safety"),
        message=pw.this.description,
        priority=pw.make_const("high"),
    )

    pw.io.jsonlines.write(alerts, "data/output/alerts/alerts_stream.jsonl")

    pw.run()


if __name__ == "__main__":
    run_pipeline()


