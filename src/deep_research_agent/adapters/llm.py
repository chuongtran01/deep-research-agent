import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import Runnable
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, ConfigDict, PrivateAttr


class LLMError(Exception):
    pass


class LLMValidationError(LLMError):
    pass


class LLMInvocationError(LLMError):
    pass


class LLM(BaseModel):
    """Gemini wrapper: init-bound structured output; ``structured_chat`` only."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    _client: Runnable = PrivateAttr()
    _system_prompt: str = PrivateAttr()
    _model_name: str = PrivateAttr()
    _schema: type[BaseModel] = PrivateAttr()

    def __init__(
        self,
        *,
        structured_output: type[BaseModel],
        system_prompt: str,
        model: str | None = None,
        api_key: str | None = None,
        temperature: float = 0.2,
    ) -> None:
        super().__init__()
        load_dotenv()

        key = (api_key or os.getenv("GOOGLE_API_KEY") or "").strip()
        if not key:
            raise ValueError("GOOGLE_API_KEY is not set")

        resolved = (
            (model or os.getenv("GOOGLE_GENAI_MODEL") or "gemini-2.5-flash").strip()
            or "gemini-2.5-flash"
        )

        self._schema = structured_output
        self._system_prompt = system_prompt.strip()
        self._model_name = resolved

        base_client = ChatGoogleGenerativeAI(
            model=self._model_name,
            google_api_key=key,
            temperature=temperature,
        )
        self._client = base_client.with_structured_output(
            self._schema,
            method="json_schema",
        )

    def structured_chat(self, prompt: str) -> BaseModel:
        try:
            raw = self._client.invoke(
                [
                    SystemMessage(content=self._system_prompt),
                    HumanMessage(content=prompt),
                ]
            )
        except Exception as e:
            raise LLMInvocationError(
                f"LLM invoke failed for model={self._model_name}"
            ) from e

        if isinstance(raw, self._schema):
            out: BaseModel = raw
        elif isinstance(raw, dict):
            try:
                out = self._schema.model_validate(raw)
            except Exception as e:
                raise LLMValidationError(
                    f"Structured validation failed for schema={self._schema.__name__}"
                ) from e
        else:
            raise LLMValidationError(
                f"Unexpected structured output type: {type(raw)!r}"
            )

        return out
