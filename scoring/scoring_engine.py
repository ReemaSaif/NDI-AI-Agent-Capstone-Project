# Operational Excellence (OE) Scoring Engine: (13 METRICS - THIRD CYCLE)

from dataclasses import dataclass
from typing import Dict, Any, List

# DATA STRUCTURES

@dataclass
class MetricResult:
    metric_id: str
    percentage: float
    scale: int
    weight: float
    weighted_score: float

@dataclass
class OEResult:
    entity_name: str
    cycle_name: str
    final_score: float
    maturity_level: int
    maturity_label: str
    maturity_description: str
    metrics: List[MetricResult]


# SCALE MAPPING (0–5)
def map_percentage_to_scale(score: float) -> int:
    """Maps a percentage (0–100) to SDAIA OE scale (0–5)"""
    if score < 40: return 0   # Unacceptable (0% - 39.99%)
    if score < 60: return 1   # Low (40% - 59.99%)
    if score < 75: return 2   # Fair (60% - 74.99%)
    if score < 90: return 3   # Good (75% - 89.99%)
    if score < 100: return 4  # Excellent (90% - 99.99%)
    return 5                  # Leader (Exactly 100%)


def get_maturity_level_from_score(score: float) -> dict:
    """Returns maturity level based on the Maturity Score Band (0–5)."""
    for level in MATURITY_LEVELS:
        if level["min_score"] <= score <= level["max_score"]:
            return level
    return MATURITY_LEVELS[0]


# OFFICIAL OE METRIC WEIGHTS (THIRD MEASUREMENT CYCLE)

OE_WEIGHTS = {
    "DSI.OE.02": 0.20,
    "DO.OE.03": 0.05,
    "DQ.OE.02": 0.05,
    "DO.OE.02": 0.10,
    "DSI.OE.01": 0.05,
    "RMD.OE.01": 0.10,
    "OD.OE.01": 0.15,
    "OD.OE.05": 0.05,
    "MCM.OE.01": 0.05,
    "MCM.OE.02": 0.05,
    "MCM.OE.03": 0.05,
    "DSI.OE.05": 0.05,
    "DQ.OE.03": 0.05,
}

# MATURITY LEVELS

MATURITY_LEVELS = [
    {
        "level": 0,
        "label": "غياب القدرات",
        "description": "نقص في القدرات الأساسية لإدارة البيانات، مع عدم وجود ممارسات معرفة.",
        "min_score": 0.00,
        "max_score": 0.24
    },
    {
        "level": 1,
        "label": "البناء",
        "description": "تم تعريف ممارسات أساسية لإدارة البيانات، ولكنها ليست وفقاً لمعايير محددة.",
        "min_score": 0.25,
        "max_score": 1.24
    },
    {
        "level": 2,
        "label": "التعريف",
        "description": "تم تطوير ممارسات البيانات بشكل رسمي، مما يضمن اتساقها ويمكن الاعتماد عليها.",
        "min_score": 1.25,
        "max_score": 2.49
    },
    {
        "level": 3,
        "label": "التفعيل",
        "description": "تم تنفيذ عمليات مؤسسية وأدوات قابلة للتوسع مع إدارة فعالة للأنظمة الداعمة لإدارة البيانات.",
        "min_score": 2.50,
        "max_score": 3.99
    },
    {
        "level": 4,
        "label": "التمكن",
        "description": "توجد حوكمة مركزية مع مقاييس ومؤشرات رئيسية (KPIs) شاملة.",
        "min_score": 4.00,
        "max_score": 4.74
    },
    {
        "level": 5,
        "label": "الريادة",
        "description": "تمكين التحسين المستمر مع التركيز القوي على الابتكار في البيانات كنموذج متميز في إدارة البيانات.",
        "min_score": 4.75,
        "max_score": 5.00
    }
]

# METRIC FORMULAS

def calc_dsi_oe_01(apis: List[Dict[str, Any]]) -> float:
    """Adherence to Data Sharing Policy (GSB)"""
    scores = []
    for api in apis:
        certified = api["certified"]
        total = api["total_attributes"]
        classified = 1 if api["classified"] else 0
        score = ((certified / total) * 0.8 + classified * 0.2) * 100
        scores.append(score)
    return sum(scores) / len(scores) if scores else 0


def calc_dsi_oe_02(systems: List[Dict[str, bool]]) -> float:
    """Systems Integrated with NDL (NDL)"""
    total = len(systems)
    if total == 0:
        return 0
    fully = sum(
        1 for s in systems
        if s["implemented"] and s["method_followed"] and s["updated"]
    )
    return (fully / total) * 100


def calc_od_oe_01(published: int, required: int) -> float:
    """Datasets Published in ODP (ODP)"""
    if required <= 0:
        return 0
    return (published / required) * 100


def calc_rmd_oe_01(published: int, required: int) -> float:
    """Publishing Reference Entities (RDP)"""
    if required <= 0:
        return 0
    return (published / required) * 100


def calc_mcm_generic(done: int, required: int) -> float:
    """Generic NDC metric formula"""
    if required <= 0:
        return 0
    return (done / required) * 100


SLA_MAP = {"New": 3, "Easy": 7, "Medium": 11, "Complex": 15}
def calc_od_oe_05(requests: List[Dict[str, Any]]) -> float:
    """Response Effectiveness to new open dataset requests (ODP)"""
    scores = []
    for r in requests:
        sla = SLA_MAP[r["category"]]
        duration = r["duration"]
        effectiveness = (1 - ((duration - sla) / sla)) * 100
        effectiveness = max(0, min(effectiveness, 100))
        scores.append(effectiveness)
    return sum(scores) / len(scores) if scores else 0


# MAIN EVALUATION ENGINE

def evaluate_oe(entity_name: str, cycle_name: str, data: Dict[str, Any]) -> OEResult:
    """Computes all 13 metrics, maps to scale, applies weights, and assigns maturity level."""

    metric_values = {
            "DSI.OE.01": calc_dsi_oe_01(data["DSI.OE.01"]["apis"]),
            "DSI.OE.02": calc_dsi_oe_02(data["DSI.OE.02"]["systems"]),
            "DO.OE.03": data["DO.OE.03"]["percentage"],
            "DQ.OE.02": data["DQ.OE.02"]["percentage"],
            "DO.OE.02": data["DO.OE.02"]["percentage"],
            "RMD.OE.01": calc_rmd_oe_01(data["RMD.OE.01"]["published"], data["RMD.OE.01"]["required"]),
            "OD.OE.01": calc_od_oe_01(data["OD.OE.01"]["published"], data["OD.OE.01"]["required"]),
            "OD.OE.05": calc_od_oe_05(data["OD.OE.05"]["requests"]),
            "MCM.OE.01": calc_mcm_generic(data["MCM.OE.01"]["done"], data["MCM.OE.01"]["required"]),
            "MCM.OE.02": calc_mcm_generic(data["MCM.OE.02"]["done"], data["MCM.OE.02"]["required"]),
            "MCM.OE.03": calc_mcm_generic(data["MCM.OE.03"]["done"], data["MCM.OE.03"]["required"]),
            "DSI.OE.05": calc_mcm_generic(data["DSI.OE.05"]["done"], data["DSI.OE.05"]["required"]),
            "DQ.OE.03": calc_mcm_generic(data["DQ.OE.03"]["done"], data["DQ.OE.03"]["required"]),
        }

    metric_results = []
    final_score = 0

    for metric_id, percentage in metric_values.items():
        scale = map_percentage_to_scale(percentage)
        weight = OE_WEIGHTS[metric_id]
        weighted = scale * weight
        final_score += weighted

        metric_results.append(
            MetricResult(
                metric_id=metric_id,
                percentage=round(percentage, 2),
                scale=scale,
                weight=weight,
                weighted_score=round(weighted, 4)
            )
        )

    maturity = get_maturity_level_from_score(final_score)

    return OEResult(
        entity_name=entity_name,
        cycle_name=cycle_name,
        final_score=round(final_score, 4),
        maturity_level=maturity["level"],
        maturity_label=maturity["label"],
        maturity_description=maturity["description"],
        metrics=metric_results
    )


