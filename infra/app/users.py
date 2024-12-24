from dataclasses import dataclass
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from ..retrieval import ColBERTv2Searcher
from typing import List, Optional
import asyncio
from openai import AsyncOpenAI
from pydantic_ai.models.openai import OpenAIModel 
import os
from dotenv import load_dotenv



# load the environment variables
load_dotenv()


@dataclass
class StudentDependencies:
    rag_retriever: ColBERTv2Searcher


class Course(BaseModel):
    course_number: str
    course_name: str
    course_url: str
    details: str
    course_level: Optional[str] = None
    general_course_objectives: str
    learning_objectives: str
    content: str
    search_rank: float
    remarks: str = Field(default="")



class SearchRequest(BaseModel):
    refined_query: str = Field(description="The refined search query based on user's input")
    search_focus: list[str] = Field(description="Key aspects to focus on in the search")


class SearchResult(BaseModel):
    recommendations: str = Field(description="Model's analysis and recommendations based on the courses and the search request")
    detailed_explanation: str = Field(description="A detailed explanation of the search request and the courses")
    gaps: str = Field(description="Potential gaps in the found courses relative to user's goals")
    


class CounslerResult(BaseModel):
    counsler_advice: str = Field(description="The advice given by the counsler, try and list more than one course.")
    retrieved_courses: List[Course]
    search_rank: int = Field(default=0)



        
study_plan_agent = Agent(
    "openai:gpt-4o-mini",
    deps_type = StudentDependencies,
    result_type = SearchResult,
    system_prompt = (
        'You are a study plan agent that helps the user plan their study'
        'You will be given a query based on the students learning goals, and based on that you will generate keywords or phrases that will be used to search for courses'
        'You will then return the most relevant courses, along side the explanation of why they are relevant, and what they would learn and what they might be missing on according to their original query'
        'When you return the courses, only return the courses you are sure are relevant to the query.'
        'Try and be very pedagogical and scientific in your explanation of how this course helps them reach their perspective'
        'Ask them questions to try and unwrap their goals and what they are looking for'
        'If you are unsure about whether some of the courses are relevant to the query, you should tell the user that you are unsure whether what they are looking for is available'
        'You dont have to choose the course with the highest search rank, you can choose the course that you think is the most relevant to the user'
        'The student may state their background and degree, the retrieved courses will have a course level, so do not add those to they keywords'
        )
)



@study_plan_agent.system_prompt
async def search_courses(ctx: RunContext[StudentDependencies]) -> str:
    # This function should return a string that will be added to the system prompt
    return (
        "You have access to a course search function that can find relevant courses"
        "Reword to cover broad aspects of the desired objective"
        "based on keywords. Use this to help students find courses that match their interests."
        "You don't need to use exact keywords, as this search function is based on semantic search and not lexical or exact wordsearch"
    )

@study_plan_agent.tool
async def search_course_catalog(ctx: RunContext[StudentDependencies], query: str) -> List[Course]:
    """Search for courses based on the given query."""
    print(f"key words used: {query}")
    retrieved_courses = ctx.deps.rag_retriever.search(query)
    return retrieved_courses



async def get_result_agent(query: str, deps: StudentDependencies):
    result = await study_plan_agent.run(query, deps=deps)
    return result

async def main():
    deps = StudentDependencies(rag_retriever=ColBERTv2Searcher())
    result = await study_plan_agent.run(
        "I want to learn more about FAISS, quantization and fast-retrievals and indexing. Mostly for indexing and quantization of vectors. I'am a MSc student in computer science and engineering.", 
        deps=deps
    )
    
    print(result.data)

if __name__ == "__main__":
    asyncio.run(main())