import os
from graph.state import AgentState
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from langgraph.types import interrupt
from pydantic import BaseModel, Field
from prompts.assessment import assessment_prompt_template, evaluation_prompt_template
from typing import Literal
load_dotenv(override=True)

api_key = os.getenv("GOOGLE_API_KEY")
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

class Score(BaseModel):
    score: dict[str, Literal["beginner", "intermediate", "advanced"]] = Field(
        default_factory=dict,
        description="A mapping of subtopics to their respective proficiency levels."
    )

evaluation_llm = llm.with_structured_output(Score)

def question_generator(state: AgentState)-> dict:
    user_topic = state["topic"]
    current_question_count = state.get("question_count", 0)
    final_question_prompt = assessment_prompt_template.format(
        topic=user_topic
    )

    system_message = SystemMessage(content=final_question_prompt)
    history = state["messages"]
    payload = [system_message] + history
    result = llm.invoke(payload)
    generated_question = result.content
    return {
        "questions" : [generated_question],
        "question_count" : current_question_count + 1,
        "messages" : [AIMessage(content=generated_question)]
    }


def get_human_answer(state: AgentState) -> dict:
    last_question = state["questions"][-1]
    user_answer = interrupt(last_question)

    return{
        "answers" : [user_answer],
        "messages" : [HumanMessage(content = user_answer)]
    }


def evaluation(state : AgentState) -> dict:
    user_topic = state["topic"]
    final_eval_prompt = evaluation_prompt_template.format(topic=user_topic)
    eval_system_message = SystemMessage(content=final_eval_prompt)
    history = state["messages"]
    payload = [eval_system_message] + history
    result = evaluation_llm.invoke(payload)
    final_score = result.score
    
    return{
        "score": final_score,
        "assessment_complete": True
    }