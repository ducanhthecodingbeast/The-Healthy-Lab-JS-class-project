import json
from dataclasses import dataclass
from typing import Any

from fastapi import HTTPException

from schemas import (
    FoodLabCustomPreviewRead,
    FoodLabCustomSelection,
    FoodLabOptionRead,
    FoodLabOptionsRead,
)


BASE_PRICE = 5.0

BASES = {
    "quinoa-bowl": {
        "label": "Quinoa Bowl",
        "price_delta": 1.5,
        "ingredients": {"Quinoa": 0.18, "Mixed Greens": 0.06},
    },
    "greens-salad": {
        "label": "Greens Salad",
        "price_delta": 0.8,
        "ingredients": {"Mixed Greens": 0.22},
    },
    "whole-wheat-wrap": {
        "label": "Whole Wheat Wrap",
        "price_delta": 0.5,
        "ingredients": {"Whole Wheat Wrap": 1, "Mixed Greens": 0.04},
    },
}

PROTEINS = {
    "none": {"label": "No Protein", "price_delta": 0, "ingredients": {}},
    "chicken": {"label": "Herbed Chicken", "price_delta": 2.6, "ingredients": {"Chicken": 0.16}},
    "salmon": {"label": "Grilled Salmon", "price_delta": 3.9, "ingredients": {"Salmon": 0.14}},
}

EXTRAS = {
    "avocado": {"label": "Avocado", "price_delta": 1.4, "ingredients": {"Avocado": 0.5}},
    "extra-greens": {"label": "Extra Greens", "price_delta": 0.8, "ingredients": {"Mixed Greens": 0.08}},
    "almond-milk-side": {"label": "Almond Milk Side", "price_delta": 1.8, "ingredients": {"Almond Milk": 0.2}},
}

DRESSINGS = {
    "lemon-herb": {"label": "Lemon Herb", "price_delta": 0, "ingredients": {}},
    "sesame-ginger": {"label": "Sesame Ginger", "price_delta": 0.3, "ingredients": {}},
    "no-dressing": {"label": "No Dressing", "price_delta": 0, "ingredients": {}},
}


@dataclass
class BuiltFoodLabItem:
    product_name: str
    custom_details: str
    unit_price: float
    total_price: float
    inventory_needs: dict[str, float]
    custom_data: dict[str, Any]
    custom_data_json: str


def food_lab_options() -> FoodLabOptionsRead:
    return FoodLabOptionsRead(
        bases=_options(BASES),
        proteins=_options(PROTEINS),
        extras=_options(EXTRAS),
        dressings=_options(DRESSINGS),
    )


def preview_food_lab(selection: FoodLabCustomSelection, quantity: int) -> FoodLabCustomPreviewRead:
    built = build_food_lab_item(selection, quantity)
    return FoodLabCustomPreviewRead(
        product_name=built.product_name,
        custom_details=built.custom_details,
        unit_price=built.unit_price,
        total_price=built.total_price,
        inventory_needs={name: _money(amount * quantity) for name, amount in built.inventory_needs.items()},
        custom_data=built.custom_data,
    )


def build_food_lab_item(selection: FoodLabCustomSelection, quantity: int) -> BuiltFoodLabItem:
    if quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be positive")

    base = _lookup(BASES, selection.base, "base")
    protein = _lookup(PROTEINS, selection.protein, "protein")
    dressing = _lookup(DRESSINGS, selection.dressing, "dressing")
    extras = _validate_extras(selection.extras)

    unit_price = BASE_PRICE + base["price_delta"] + protein["price_delta"] + dressing["price_delta"]
    inventory_needs: dict[str, float] = {}
    _merge_ingredients(inventory_needs, base["ingredients"])
    _merge_ingredients(inventory_needs, protein["ingredients"])
    _merge_ingredients(inventory_needs, dressing["ingredients"])

    for extra_id, extra in extras:
        unit_price += extra["price_delta"]
        _merge_ingredients(inventory_needs, extra["ingredients"])

    product_name = f"Food Lab {protein['label']} {base['label']}" if selection.protein != "none" else f"Food Lab {base['label']}"
    custom_details = "; ".join(
        [
            f"Base: {base['label']}",
            f"Protein: {protein['label']}",
            f"Extras: {', '.join(extra['label'] for _, extra in extras) if extras else 'None'}",
            f"Dressing: {dressing['label']}",
        ]
    )
    unit_price = _money(unit_price)
    custom_data = {
        "builder": "food_lab",
        "version": 1,
        "selection": {
            "base": selection.base,
            "protein": selection.protein,
            "extras": [extra_id for extra_id, _ in extras],
            "dressing": selection.dressing,
        },
        "inventory_needs": [{"ingredient": name, "quantity": amount} for name, amount in sorted(inventory_needs.items())],
    }
    return BuiltFoodLabItem(
        product_name=product_name,
        custom_details=custom_details,
        unit_price=unit_price,
        total_price=_money(unit_price * quantity),
        inventory_needs=inventory_needs,
        custom_data=custom_data,
        custom_data_json=json.dumps(custom_data, sort_keys=True),
    )


def parse_custom_data(raw: str | None) -> dict[str, Any] | None:
    if not raw:
        return None
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def _options(source: dict[str, dict[str, Any]]) -> list[FoodLabOptionRead]:
    return [
        FoodLabOptionRead(id=option_id, label=data["label"], price_delta=_money(data["price_delta"]))
        for option_id, data in source.items()
    ]


def _lookup(source: dict[str, dict[str, Any]], option_id: str, option_type: str) -> dict[str, Any]:
    option = source.get(option_id)
    if not option:
        raise HTTPException(status_code=400, detail=f"Invalid Food Lab {option_type} selection")
    return option


def _validate_extras(extra_ids: list[str]) -> list[tuple[str, dict[str, Any]]]:
    if len(set(extra_ids)) != len(extra_ids):
        raise HTTPException(status_code=400, detail="Food Lab extras must be unique")
    return [(extra_id, _lookup(EXTRAS, extra_id, "extra")) for extra_id in extra_ids]


def _merge_ingredients(target: dict[str, float], ingredients: dict[str, float]) -> None:
    for name, amount in ingredients.items():
        target[name] = round(target.get(name, 0) + float(amount), 4)


def _money(value: float) -> float:
    return round(float(value), 2)
