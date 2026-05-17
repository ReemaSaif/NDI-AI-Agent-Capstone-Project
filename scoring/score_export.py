# JSON EXPORT & UTILITIES

import json
from datetime import datetime, timezone
from scoring_engine import OEResult

def export_json(filepath: str, result: OEResult):
    data = {
        "entity_name": result.entity_name,
        "cycle_name": result.cycle_name,
        "final_score": result.final_score,
        "maturity_level": result.maturity_level,
        "maturity_label": result.maturity_label,
        "maturity_description": result.maturity_description,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "metrics": [
            {
                "metric_id": m.metric_id,
                "percentage": m.percentage,
                "scale": m.scale,
                "weight": m.weight,
                "weighted_score": m.weighted_score
            }
            for m in result.metrics
        ]
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def print_report(result: OEResult):
    print("\n" + "=" * 60)
    print("                    OE SCORING REPORT")
    print("=" * 60)
    print(f"Entity: {result.entity_name}")
    print(f"Cycle : {result.cycle_name}")
    print(f"Maturity Level : {result.maturity_level}")
    print(f"Maturity Label : {result.maturity_label}")
    print(f"Description    : {result.maturity_description}")
    print(f"Final Operational Excellence (OE) Score: {result.final_score:.4f}\n")

    for m in result.metrics:
        print(
            f"{m.metric_id:<12}  {m.percentage:>6.2f}%  "
            f"Scale={m.scale}  Weight={m.weight:.2f}  "
            f"Weighted={m.weighted_score:.4f}"
        )

    print("=" * 60 + "\n")


