"""
Domain Service: DemandForecastService  (ANALYTICS som domain service)

Dette er opgavens krav om "data analytics implementeret som domain service".
Servicen forudsiger fremtidig efterspørgsel per marked/distributør baseret på
historiske ordredata.

Den demonstrerer de fire analyse-typer fra opgaven:
  - Deskriptiv:   historisk total mængde per distributør
  - Diagnostisk:  fejlrate (andel afviste ordrer)
  - Predictiv:    lineær regression der forecaster næste periodes mængde
  - (ML):         scikit-learn LinearRegression

Servicen ligger i domænelaget fordi den opererer på domænedata (ordrer) og
producerer domænerelevant indsigt. Den modtager historiske ordrer som input —
hvor de kommer fra (database) er infrastrukturens ansvar, ikke domænets.

Modellen er bevidst simpel. Pointen er at DEMONSTRERE konceptet med en ægte
ML-model, ikke at bygge en produktionsklar forecasting-motor.
"""
from collections import defaultdict
from dataclasses import dataclass

import numpy as np
from sklearn.linear_model import LinearRegression


@dataclass
class ForecastResult:
    distributor_id: str
    historical_periods: int
    total_historical_quantity: int
    rejection_rate: float
    forecast_next_period: float


class DemandForecastService:
    def forecast_for_distributor(self, orders: list) -> ForecastResult | None:
        """
        orders: liste af Order-objekter for én distributør, sorteret efter dato.
        Returnerer None hvis der er for lidt data til at forecaste.
        """
        if not orders:
            return None

        distributor_id = orders[0].distributor_id

        # --- Deskriptiv: aggregér mængde per periode (her: per ordre i rækkefølge) ---
        quantities = [o.total_quantity for o in orders]
        total_qty = sum(quantities)

        # --- Diagnostisk: fejlrate ---
        rejected = sum(1 for o in orders if o.status.value == "REJECTED")
        rejection_rate = round(rejected / len(orders), 3)

        # --- Predictiv (ML): lineær regression på mængde over tid ---
        forecast = self._predict_next(quantities)

        return ForecastResult(
            distributor_id=distributor_id,
            historical_periods=len(orders),
            total_historical_quantity=total_qty,
            rejection_rate=rejection_rate,
            forecast_next_period=forecast,
        )

    def _predict_next(self, quantities: list[int]) -> float:
        """
        Træn en simpel lineær regression: x = periodeindeks, y = mængde.
        Forudsig næste periode (x = n). Kræver mindst 2 datapunkter.
        """
        if len(quantities) < 2:
            # For lidt data — fald tilbage til seneste observation
            return float(quantities[-1]) if quantities else 0.0

        x = np.arange(len(quantities)).reshape(-1, 1)
        y = np.array(quantities)
        model = LinearRegression().fit(x, y)
        next_index = np.array([[len(quantities)]])
        prediction = model.predict(next_index)[0]
        return round(max(prediction, 0.0), 1)  # ingen negativ efterspørgsel
