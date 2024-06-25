import os
from dotenv import load_dotenv
import sys

load_dotenv()
WORKDIR=os.getenv("WORKDIR")
os.chdir(WORKDIR)
sys.path.append(WORKDIR)

from pydantic import BaseModel, Field
from typing import Literal


class QueryUserInput(BaseModel):
    """
    Validates if the input of the user about a question is formatted correctly
    """
    user_input: Literal[1,2] = Field(..., description = 'The desired of the user based on the initial question')
