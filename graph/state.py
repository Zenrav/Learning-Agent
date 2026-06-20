from typing import TypedDict, Annotated
import operator
from langgraph.graph.message import add_messages
class AgentState(TypedDict):
    topic: str
    questions: Annotated[list[str],operator.add]
    answers: Annotated[list[str], operator.add]
    messages: Annotated[list, add_messages]
    question_count: int
    assessment_complete:bool
    score: dict

    