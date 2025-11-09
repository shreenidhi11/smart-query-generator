from datetime import timedelta

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import redis
from redis.commands.search.field import VectorField, TextField
# from redis.commands.search.index_definition import IndexDefinition, IndexType
from redis.exceptions import ResponseError
import io
import os
import json
import hashlib
import uvicorn
import google.generativeai as genai
from pydantic import BaseModel
from dotenv import load_dotenv

class Form(BaseModel):
    jobTitle: str
    # fullTime: bool = False
    # partTime: bool = False
    # contract: bool = False
    # internship: bool = False

load_dotenv()
genai.configure(api_key=os.getenv("GENAI_API_KEY"))
CACHE_TTL = timedelta(hours=24)
redis_client = redis.StrictRedis(host="localhost", port=6379, db=0, decode_responses=True)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# We keep these lists short (<= 4 items) to obey the <= 5 OR clause limit.
ACTION_PHRASES = [
    "hiring",
    "recruiting",
    "join our team",
    "looking for"
]

EXCLUSION_PHRASES = [
    "internship",
    "contract"
]

ROLE_SYNONYMS = {
  "software developer": [
    "software engineer",
    "backend engineer",
    "full stack developer",
    "application developer",
  ],
  "data scientist": [
    "machine learning engineer",
    "ai engineer",
    "data analyst",
    "research scientist",
  ],
  "systems engineer": [
    "devops engineer",
    "site reliability engineer",
    "infrastructure engineer",
  ]
}

# -----utilities------
#utility functions for redis access
def get_synonyms(jobTitle):
    '''
    returns the synonyms for the given jobTitle
    :param jobTitle: job title
    :return: list of synonyms
    '''
    global redis_client
    synonyms = []
    jobTitle = jobTitle.strip().lower()
#     first check in the redis server
    cached_synonyms = redis_client.get(jobTitle)
    if cached_synonyms:
        synonyms = cached_synonyms
        return json.loads(synonyms)
    else:
        synonyms = llm_call(jobTitle)
        redis_client.setex(jobTitle, CACHE_TTL, json.dumps(synonyms))
    return synonyms

def llm_call(title):
    '''
    Calls the LLM for returning alternate names of the given job titles
    :param title: title of the job
    :return: list of alternate names
    '''
    prompt = f"""
    Strictly list only 4 alternative professional job titles or synonyms that mean the same as '{title}'.
    Focus on realistic variations used in job postings.
    Output them as a comma-separated list.
    """
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(prompt)
    text = response.text.strip()

    results = [s.strip() for s in text.split(",") if s.strip()]
    return results

def build_boolean_queries(main_title):
    """
    Builds a *list* of short, safe queries that respect LinkedIn limits.
    """
    queries = []

    # --- Build reusable, safe query parts ---

    # Main title part (1 term)
    main_title_part = f'"{main_title.title()}"'

    # All titles part (max 4 terms, 3 ORs)
    all_titles_list = [main_title.title()]
    # all_titles_list = [main_title.title()] + synonyms
    titles_query_part = f"({' OR '.join([f'"{t}"' for t in all_titles_list])})"

    # All actions part (max 4 terms, 3 ORs)
    actions_query_part = f"({' OR '.join([f'"{p}"' for p in ACTION_PHRASES])})"

    # All exclusions part (max 4 terms, 3 ORs)
    exclusions_query_part = f"NOT ({' OR '.join([f'"{p}"' for p in EXCLUSION_PHRASES])})"

    # --- Generate the query list ---

    # Query 1: Main Title + All Actions (Simple & Effective)
    # Ops: 1 AND + 3 ORs = 4 (SAFE)
    queries.append(f"{main_title_part} AND {actions_query_part}")

    # Query 2: All Titles + "hiring" (Broadest "hiring" search)
    # Ops: 3 ORs + 1 AND = 4 (SAFE)
    queries.append(f'{titles_query_part} AND "hiring"')

    # Query 3: All Titles + "recruiting" (Broad "recruiting" search)
    # Ops: 3 ORs + 1 AND = 4 (SAFE)
    queries.append(f'{titles_query_part} AND "recruiting"')

    # Query 4: Main Title + All Actions + All Exclusions (Most Complex)
    # Ops: 1 AND + 3 ORs + 1 AND + 1 NOT + 3 ORs = 9 (SAFE)
    # This is the longest query we'll make, should be < 250 chars.
    queries.append(f"{main_title_part} AND {actions_query_part} AND {exclusions_query_part}")

    # Query 5: All Titles + All Actions (Riskier, but good to try)
    # Ops: 3 ORs + 1 AND + 3 ORs = 7 (SAFE)
    # This might get long, but operators are fine.
    # queries.append(f"{titles_query_part} AND {actions_query_part}")

    # Query 6: Just All Titles (For manual scanning)
    # Ops: 3 ORs (SAFE)
    # queries.append(f"{titles_query_part}")

    return queries

@app.post("/data")
async def generate_smart_queries(form: Form):
    jobTitle = form.jobTitle
    # fullTime = form.fullTime
    # partTime = form.partTime
    # contract = form.contract
    # internship = form.internship

    # Just a debug log
    # print(f"Received: {form.dict()}")

    # You can add logic later to modify queries based on the flags above.
    queries = build_boolean_queries(jobTitle.lower())

    #send synonyms to the user to try other searches
    alternate_job_titles = get_synonyms(jobTitle.lower())

    # alternate_job_titles =  ROLE_SYNONYMS[jobTitle.lower()] if jobTitle.lower() in ROLE_SYNONYMS else llm_call(jobTitle.lower())
    # if jobTitle.lower() not in ROLE_SYNONYMS:
    #     ROLE_SYNONYMS[jobTitle.lower()] = alternate_job_titles

    return {
        "message": "Form received successfully!",
        "data": queries,
        "additional_job_titles": alternate_job_titles
    }
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)