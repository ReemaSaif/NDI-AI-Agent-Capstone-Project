
import json
from layouts import MetricItem, OESummary
from pdf_builder import OEReportBuilder
from font import register_fonts


if __name__ == "__main__":
    register_fonts()

    with open("../scoring/ARscoring_engine_OE_report.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    metrics = [
        MetricItem(
            metric_id=m["metric_id"],
            percentage=m["percentage"],
            scale=m["scale"],
            weight=m["weight"],
            weighted_score=m["weighted_score"],
        )
        for m in data.get("metrics", [])
    ]

    summary = OESummary(
        entity_name=data.get("entity_name", "غير محدد"),
        cycle_name=data.get("cycle_name", "غير محدد"),
        final_score=data.get("final_score", 0),
        maturity_level=data.get("maturity_level", 0),
        maturity_label=data.get("maturity_label", ""),
        maturity_description=data.get("maturity_description", ""),
        metrics=metrics,
    )


    engine = OEReportBuilder(output_file="OE_Arabic_Report.pdf")
    engine.build(summary)

