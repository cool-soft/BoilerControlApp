from .boiler_t_prediction_view import BoilerTPredictionView

API_RULES = [
    (
        "/api/v1/getPredictedBoilerT",
        {
            "view_func": BoilerTPredictionView.as_view("getPredictedBoilerT_v1")
        }
    )
]
