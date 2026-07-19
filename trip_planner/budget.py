
COST_TIERS = {
    "budget": {"lodging": 3000, "food": 2000, "transport": 800, "activities": 1200},
    "mid-range": {"lodging": 9000, "food": 4500, "transport": 2000, "activities": 3000},
    "luxury": {"lodging": 29000, "food": 10000, "transport": 5000, "activities": 7500},
}


def estimate_budget(days: int, travelers: int, tier: str) -> dict:
    tier = tier.lower()
    rates = COST_TIERS.get(tier, COST_TIERS["mid-range"])

    per_day = {k: v * travelers for k, v in rates.items()}
    totals = {k: v * days for k, v in per_day.items()}
    grand_total = sum(totals.values())

    return {
        "tier": tier,
        "days": days,
        "travelers": travelers,
        "per_day_per_group": per_day,
        "totals_by_category": totals,
        "grand_total": grand_total,
    }


def format_inr(amount: float) -> str:
    """Format a number using Indian digit grouping, e.g. 1,45,000."""
    n = int(round(amount))
    sign = "-" if n < 0 else ""
    n = abs(n)
    s = str(n)

    if len(s) <= 3:
        return f"{sign}₹{s}"

    last3 = s[-3:]
    rest = s[:-3]
    groups = []
    while len(rest) > 2:
        groups.insert(0, rest[-2:])
        rest = rest[:-2]
    if rest:
        groups.insert(0, rest)

    return f"{sign}₹{','.join(groups)},{last3}"


def format_budget_table(budget: dict) -> list[dict]:
    """Rows suitable for st.dataframe / st.table."""
    rows = []
    for category, total in budget["totals_by_category"].items():
        rows.append({
            "Category": category.capitalize(),
            "Per day (group)": format_inr(budget["per_day_per_group"][category]),
            "Total": format_inr(total),
        })
    rows.append({
        "Category": "TOTAL",
        "Per day (group)": format_inr(sum(budget["per_day_per_group"].values())),
        "Total": format_inr(budget["grand_total"]),
    })
    return rows
