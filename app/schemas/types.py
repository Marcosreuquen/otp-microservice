from typing import Annotated
from fastapi import Header

AuthHeader = Annotated[str, Header(alias="Authorization")]