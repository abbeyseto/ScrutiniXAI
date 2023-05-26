import os
from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import spacy
import docx2txt
import PyPDF2
import openai
import re
from dotenv import load_dotenv
load_dotenv()

# import torch

# Set up OpenAI API credentials from .env file
openai.api_key = os.getenv("OPENAI_API_KEY")

# ChatGPT davinci model
model = "text-davinci-002"

app = FastAPI()

nlp = spacy.load("en_core_web_sm")


origins = [
    "http://localhost",
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["OPTIONS", "POST"],
    allow_headers=["*"],
)


class CVInput(BaseModel):
    job_description: str

# ===============
# CV MATCHING API
# ===============


@app.post("/match")
async def match_cv_to_job(cv_file: UploadFile = File(...), job_description: str = Form(...)):
    cv_text = ""
    file_extension = cv_file.filename.split(".")[-1].lower()

    if file_extension == "pdf":
        pdf_reader = PyPDF2.PdfReader(cv_file.file)
        cv_text = ""
        for page in range(len(pdf_reader.pages)):
            cv_text += pdf_reader.pages[page].extract_text()
    elif file_extension == "docx":
        cv_text = docx2txt.process(cv_file.file)
    else:
        # Unsupported file format
        return {"error": "Unsupported file format"}

    # Process CV text
    cv_keywords = extract_keywords(cv_text)
    # Process job description
    job_keywords = extract_keywords(job_description)

    # Find similar keywords
    similar_keywords = find_similar_keywords(cv_keywords, job_keywords)

    # Perform matching algorithm
    is_match = perform_matching(cv_keywords, job_keywords)

    return JSONResponse(
        content={
            "similar_keywords": similar_keywords,
            "is_match": is_match
        }
    )


def extract_keywords(text):
    doc = nlp(text)
    years_of_experience = []
    for ent in doc.ents:
        # like 6 years of experience or six years of experience
        if ent.label_ == "DATE" and "year" in ent.text:
            years_of_experience.append(ent.text)

    core_technology_skills = ["python", "java",
                              "javascript", "sql", "html", "css"]
    technology_skills = []
    for token in doc:
        if token.text.lower() in core_technology_skills:
            technology_skills.append(token.text.lower())

    soft_skills = ["communication", "leadership",
                   "teamwork", "problem-solving", "creativity"]
    extracted_soft_skills = []
    for token in doc:
        if token.text.lower() in soft_skills:
            extracted_soft_skills.append(token.text.lower())

    other_keywords = [token.text for token in doc if token.pos_ ==
                      "NOUN" or token.pos_ == "PROPN"]

    keywords = years_of_experience + technology_skills + \
        extracted_soft_skills + other_keywords
    return keywords


def find_similar_keywords(cv_keywords, job_keywords):
    cv_keyword_set = set(cv_keywords)
    job_keyword_set = set(job_keywords)
    similar_keywords = cv_keyword_set.intersection(job_keyword_set)
    return list(similar_keywords)


def perform_matching(cv_keywords, job_keywords):
    similar_keywords_count = len(
        find_similar_keywords(cv_keywords, job_keywords))
    # convert to percentage match score out of 100 % and round to 2 decimal places
    match_score = round((similar_keywords_count / len(job_keywords)) * 100, 2)

    # Define a threshold for match acceptance
    match_threshold = 0.5 * 100

    if match_score >= match_threshold:
        return {
            "match_score":  f"{match_score}%",
            "is_match": True
        }
    else:
        return {
            "match_score": f"{match_score}%",
            "is_match": False
        }


# ===============
# TRANSCRIPT ANALYSIS API
# ===============


@app.post("/extract-context")
async def extract_context(transcript: dict):
    # Get the text transcript from the request body
    transcript_text = transcript.get("transcript")

    # Apply NLP techniques to extract context
    doc = nlp(transcript_text)
    extracted_context = extract_information(doc)

    return {"context": extracted_context}


def extract_information(doc):
    # Example logic to extract relevant information from the transcript
    entities = extract_entities(doc)
    keywords = extract_keywords(doc)
    phrases = extract_phrases(doc)

    extracted_context = {
        "entities": entities,
        "keywords": keywords,
        "phrases": phrases
    }

    return extracted_context


def extract_entities(doc):
    entities = [ent.text for ent in doc.ents]
    return entities


def extract_phrases(doc):
    phrases = [chunk.text for chunk in doc.noun_chunks]
    return phrases


@app.post("/generate-questions")
async def generate_questions(request: Request):
    # get data from request body
    data = await request.json()
    if request.method == 'OPTIONS':
        return JSONResponse(status_code=200)

    # Get the extracted context and job description from the request body
    context = data.get("context")
    job_description = data.get("job_description")

    # Generate question recommendations based on the context and job description
    questions = generate_recommendations(context, job_description)
    return {"questions": questions}


def generate_recommendations(context, job_description):
    # Preprocess the raw text transcript
    context = re.sub(r"\n", " ", context)
    job_description = re.sub(r"\n", " ", job_description)
    # ChatGPT davinci model
    prompt = f"Based on this Conversation context:{context},\n Give me multiple questions can i ask this candidate to assertain if they are the best match for this \nJob Desscription: {job_description}\nQuestion:"
    response = openai.Completion.create(
        engine=model,
        prompt=prompt,
        temperature=0.5,
        max_tokens=100,
        n=1,
        frequency_penalty=0,
        presence_penalty=0.3,
        stop=None
    )

    # Extract the generated questions from the response
    questions = response.choices[0].text.strip().split("\n")
    print(questions)
    return questions

# endpont that gets job description from file and return its texts


@app.post("/get-job-description")
async def get_job_description(job_description_file: UploadFile = File(...)):
    job_description_text = ""
    file_extension = job_description_file.filename.split(".")[-1].lower()

    if file_extension == "pdf":
        pdf_reader = PyPDF2.PdfReader(job_description_file.file)
        job_description_text = ""
        for page in range(len(pdf_reader.pages)):
            job_description_text += pdf_reader.pages[page].extract_text()
    elif file_extension == "docx":
        job_description_text = docx2txt.process(job_description_file.file)
    else:
        # Unsupported file format
        return {"error": "Unsupported file format"}

    return {"job_description": job_description_text}

# endpont that gets text from local file job_description.txt


@app.get("/get-job-description-local")
async def get_job_description_local():
    job_description_text = ""
    with open("job_description.txt", "r") as f:
        job_description_text = f.read()

    return {"job_description": job_description_text}


# ===============
# GPT 3 API FOR CANDIDATE MATCHING
# ===============

# Endpoint to get the job description from a file and also get the candidate's resume from a file
# then it extracts the following from both file:
# Years of experience
# Core technology skills
# Programming languages
# Soft skills
# Other keywords
#  in json format using chatgpt davinci model

@app.post("/get-job-description-and-cv")
async def get_job_description_and_cv(job_description_file: UploadFile = File(...), cv_file: UploadFile = File(...)):

    job_description_text = extract_text_from_file(job_description_file)
    cv_text = extract_text_from_file(cv_file)

    #  write job description to job_description.txt
    with open("job_description.txt", "w") as f:
        f.write(job_description_text)

    #  write cv to cv.txt
    with open("cv.txt", "w") as f:
        f.write(cv_text)

    # Preprocess the raw text transcript
    cv_text = re.sub(r"\n", " ", cv_text)
    job_description_text = re.sub(r"\n", " ", job_description_text)

    job_description_text_prompt = f"Based on the provided \nJob Description: {job_description_text} \nWhat are the years of experience, programming languages, technology tools and skills mentioned in this Job description"
    cv_text_prompt = f"Based on the provided \nCV: {cv_text} \nWhat are the years of experience, programming languages, technology tools and skills mentioned in this Job description"

    job_description_response = openai.Completion.create(
        engine=model,
        prompt=job_description_text_prompt,
        temperature=0.5,
        max_tokens=100,
        n=1,
        frequency_penalty=0,
        presence_penalty=0.3,
        stop=None
    )

    cv_response = openai.Completion.create(
        engine=model,
        prompt=cv_text_prompt,
        temperature=0.5,
        max_tokens=100,
        n=1,
        frequency_penalty=0,
        presence_penalty=0.3,
        stop=None
    )

    job_description_response = job_description_response.choices[0].text.strip().split("\n")
    cv_response = cv_response.choices[0].text.strip().split("\n")

    # Comapre the responses and return the result
    compare_prompt = f'Based on this Job requirement:\n{job_description_response} and the candidate CV:\n{cv_response}, Write a detailed highlight report of how the required years of experience, programming languages, technology tools and skills mentioned in this Job description matched the candidate\'s experience as shown in his CV, also show match accuracy in percentage'
    compare_response = openai.Completion.create(
        engine=model,
        prompt=compare_prompt,
        temperature=0.5,
        max_tokens=200,
        n=1,
        frequency_penalty=0,
        presence_penalty=0.3,
        stop=None
    )
    compare_response = compare_response.choices[0].text.strip().split("\n")
    return {
        "jobDescriptionSummary": job_description_response,
        "cvSummary": cv_response,
        "analysis": compare_response
    }


# function to extract text from a file
def extract_text_from_file(file):
    text = ""
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension == "pdf":
        pdf_reader = PyPDF2.PdfReader(file.file)
        text = ""
        for page in range(len(pdf_reader.pages)):
            text += pdf_reader.pages[page].extract_text()
    elif file_extension == "docx":
        text = docx2txt.process(file.file)
    else:
        return {"error": "Unsupported file format"}

    return text
