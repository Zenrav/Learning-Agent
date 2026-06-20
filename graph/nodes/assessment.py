import os
from graph.state import AgentState
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, AIMessage
from prompts.assessment import assessment_prompt_template
load_dotenv(override=True)

api_key = os.getenv("GOOGLE_API_KEY")
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

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


