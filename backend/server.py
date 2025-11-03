from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import io
import os
import json
import uvicorn
from pydantic import BaseModel


class Form(BaseModel):
    jobTitle: str
    fullTime: bool
    partTime: bool
    contract: bool
    internship: bool

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/data")
async def generate_smart_queries(form: Form):
    # form is automatically parsed and validated by FastAPI
    print(form)
    print(form.dict())  # converts the Pydantic model to a Python dict

    # You can now use form.jobTitle, form.fullTime, etc.
    return {
        "message": "Form received successfully!",
        "data": form.dict()
    }
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)