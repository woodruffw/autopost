import os
from collections.abc import Iterator
from typing import Annotated, Literal

from pydantic import BaseModel, Field, SecretStr, StrictStr

from autopost._backend.interface import Backend


class Embedded(BaseModel):
    type_: Literal["Embedded"] = Field(alias="type")
    value: SecretStr

    def get_secret_value(self) -> str:
        return self.value.get_secret_value()


class Environment(BaseModel):
    type_: Literal["Environment"] = Field(alias="type")
    variable: StrictStr

    def get_secret_value(self) -> str:
        return os.environ[self.variable]


Credential = Annotated[Embedded | Environment, Field(discriminator="type_")]


class RedditConfig(BaseModel):
    type_: Literal["Reddit"] = Field(alias="type")
    name: str
    subreddit: str
    client_id: Credential
    client_secret: Credential
    username: str
    password: Credential


class TwitterConfig(BaseModel):
    type_: Literal["Twitter"] = Field(alias="type")
    name: str
    api_key: Credential
    api_key_secret: Credential
    access_token: Credential
    access_token_secret: Credential


class MastodonConfig(BaseModel):
    type_: Literal["Mastodon"] = Field(alias="type")
    name: str
    server: str
    client_secret: Credential
    client_key: Credential
    access_token: Credential


class BlueskyConfig(BaseModel):
    type_: Literal["Bluesky"] = Field(alias="type")
    name: str
    username: str
    password: Credential


class DummyConfig(BaseModel):
    type_: Literal["Dummy"] = Field(alias="type")
    name: str


BackendConfig = Annotated[
    RedditConfig | TwitterConfig | MastodonConfig | BlueskyConfig | DummyConfig,
    Field(discriminator="type_"),
]


class Config(BaseModel):
    backend_configs: list[BackendConfig] = Field(..., alias="backend")

    @property
    def backends(self) -> Iterator[Backend]:
        import autopost._backend as backend

        for config in self.backend_configs:
            klass = getattr(backend, config.type_)
            yield klass(config)
