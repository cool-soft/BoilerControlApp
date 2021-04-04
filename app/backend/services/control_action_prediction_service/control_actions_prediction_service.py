from backend.services.updater_service.updatable_service import UpdatableService


class ControlActionPredictionService(UpdatableService):

    async def update_async(self):
        raise NotImplementedError
