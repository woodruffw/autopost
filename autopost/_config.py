from typing import Annotated, Iterator, Literal

from pydantic import BaseModel, Field, SecretStr

from autopost._backend.interface import Backend


class RedditConfig(BaseModel):
    type_: Literal["Reddit"] = Field(alias="type")
    name: str | None
    subreddit: str
    client_id: SecretStr
    client_secret: SecretStr
    username: str
    password: SecretStr


class TwitterConfig(BaseModel):
    type_: Literal["Twitter"] = Field(alias="type")
    name: str | None


class MastodonConfig(BaseModel):
    type_: Literal["Mastodon"] = Field(alias="type")
    name: str | None
    server: str
    client_secret: SecretStr
    client_key: SecretStr
    access_token: SecretStr


BackendConfig = Annotated[
    RedditConfig | TwitterConfig | MastodonConfig, Field(discriminator="type_")
]


class Config(BaseModel):
    backend_configs: list[BackendConfig] = Field(..., alias="backends")

    @property
    def backends(self) -> Iterator[Backend]:
        import autopost._backend as backend

        for config in self.backend_configs:
            klass = getattr(backend, config.type_)
            yield klass(config)
