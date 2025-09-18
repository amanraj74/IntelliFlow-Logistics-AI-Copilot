import pathway as pw


def read_streaming_csv(path: str) -> pw.Table:
    return pw.io.csv.read(path, mode="streaming", infer_schema=True)


