from pydantic import Field
from src.api.model.utils import OrmModel


class FavoriteRequest(OrmModel):
    training_id: int = Field(
        title="Training's ID", description="The training to fav's ID"
    )
