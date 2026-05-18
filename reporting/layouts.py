
import arabic_reshaper
from bidi.algorithm import get_display
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List

# Arabic Text Rendering Helper

def fix_arabic(text: str) -> str:
    if not text:
        return ""
    reshaped = arabic_reshaper.reshape(str(text))
    return get_display(reshaped)


# Data Models

@dataclass
class MetricItem:
    metric_id: str
    percentage: float
    scale: str
    weight: float
    weighted_score: float


@dataclass
class OESummary:
    entity_name: str
    cycle_name: str
    final_score: float
    maturity_level: int
    maturity_label: str
    maturity_description: str
    metrics: List[MetricItem]

# Chart Generator

def generate_metrics_chart(metrics, output_path="metrics_chart.png"):
    metric_ids = [m.metric_id for m in metrics]
    percentages = [m.percentage for m in metrics]

    plt.figure(figsize=(12, 5))
    plt.bar(metric_ids, percentages, color="#625D9C", width=0.8)

    plt.xticks(rotation=45, ha="right", fontsize=8)
    plt.yticks(fontsize=9)

    plt.title(fix_arabic("مخطط مؤشرات التميز التشغيلي"), fontsize=14)
    plt.ylabel(fix_arabic("النسبة المئوية"), fontsize=11)

    plt.grid(False)
    plt.ylim(0, 110)
    plt.tight_layout()

    plt.savefig(output_path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close()
