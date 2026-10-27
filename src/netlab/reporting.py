import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path


def save_json_report(results, output_path="reports/latest.json"):
    passed = sum(result.passed for result in results)
    total = len(results)

    report = {
        "project": "SecureNet Lab",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "success": passed == total
        },
        "tests": [asdict(result) for result in results]
    }

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=4)

    print(f"JSON report saved to {path}")

    return report
