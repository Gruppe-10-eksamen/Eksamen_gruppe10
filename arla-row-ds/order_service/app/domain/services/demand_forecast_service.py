"""
Domain Service: DemandForecastService.
Forecaster fremtidig efterspørgsel per distributør og produkt via lineær regression (scikit-learn).
Dækker deskriptiv, diagnostisk og predictiv analyse på historiske ordredata.
"""
from collections import defaultdict
from dataclasses import dataclass, field

import numpy as np
from sklearn.linear_model import LinearRegression


@dataclass
class ProductForecast:
    product_code: str
    total_historical_quantity: int
    forecast_next_period: float


@dataclass
class ForecastResult:
    distributor_id: str
    historical_periods: int
    total_historical_quantity: int
    rejection_rate: float
    forecast_next_period: float
    products: list[ProductForecast] = field(default_factory=list)


class DemandForecastService:
    def forecast_for_distributor(self, orders: list) -> ForecastResult | None:
        """
        orders: liste af Order-objekter for én distributør, sorteret efter dato.
        Returnerer None hvis der er for lidt data til at forecaste.
        """
        if not orders:
            return None

        distributor_id = orders[0].distributor_id

        # --- Deskriptiv: aggregér mængde per periode ---
        quantities = [o.total_quantity for o in orders]
        total_qty = sum(quantities)

        # --- Diagnostisk: fejlrate ---
        rejected = sum(1 for o in orders if o.status.value == "REJECTED")
        rejection_rate = round(rejected / len(orders), 3)

        # --- Predictiv: forecast på totalmængde ---
        forecast = self._predict_next(quantities)

        # --- Per-produkt forecast ---
        product_quantities: dict[str, list[int]] = defaultdict(list)
        for order in orders:
            seen_in_order = defaultdict(int)
            for line in order.lines:
                seen_in_order[line.product_code] += line.quantity.value
            for product_code, qty in seen_in_order.items():
                product_quantities[product_code].append(qty)

        product_forecasts = [
            ProductForecast(
                product_code=product_code,
                total_historical_quantity=sum(qtys),
                forecast_next_period=self._predict_next(qtys),
            )
            for product_code, qtys in sorted(product_quantities.items())
        ]

        return ForecastResult(
            distributor_id=distributor_id,
            historical_periods=len(orders),
            total_historical_quantity=total_qty,
            rejection_rate=rejection_rate,
            forecast_next_period=forecast,
            products=product_forecasts,
        )

    def _predict_next(self, quantities: list[int]) -> float:
        """Lineær regression på mængde over tid. Kræver mindst 2 datapunkter."""
        if len(quantities) < 2:
            return float(quantities[-1]) if quantities else 0.0

        x = np.arange(len(quantities)).reshape(-1, 1)
        y = np.array(quantities)
        model = LinearRegression().fit(x, y)
        next_index = np.array([[len(quantities)]])
        prediction = model.predict(next_index)[0]
        return round(max(prediction, 0.0), 1)