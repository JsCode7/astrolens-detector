import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AstroLens Pipeline API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

class JobCreate(BaseModel):
    job_name: str

class Job(BaseModel):
    id: int
    job_name: str
    status: str
    created_at: datetime

class Candidate(BaseModel):
    id: Optional[int] = None
    job_id: int
    candidate_name: str
    confidence_score: float
    image_url: Optional[str] = None
    redshift: Optional[float] = None
    magnitude: Optional[float] = None
    object_type: Optional[str] = None
    attention_image_url: Optional[str] = None

@app.post("/api/jobs", response_model=Job)
async def create_job(job_in: JobCreate):
    response = supabase.table("processing_jobs").insert({"job_name": job_in.job_name, "status": "pending"}).execute()
    if len(response.data) == 0:
        raise HTTPException(status_code=400, detail="Failed to create job")
    return response.data[0]

@app.get("/api/jobs/pending", response_model=List[Job])
async def get_pending_jobs():
    response = supabase.table("processing_jobs").select("*").eq("status", "pending").execute()
    return response.data

@app.get("/api/jobs/active", response_model=List[Job])
async def get_active_jobs():
    response = supabase.table("processing_jobs").select("*").in_("status", ["pending", "processing"]).execute()
    return response.data

@app.put("/api/jobs/{job_id}/status", response_model=Job)
async def update_job_status(job_id: int, status: str):
    response = supabase.table("processing_jobs").update({"status": status}).eq("id", job_id).execute()
    if len(response.data) == 0:
        raise HTTPException(status_code=404, detail="Job not found")
    return response.data[0]

@app.post("/api/candidates", response_model=Candidate)
async def add_candidate(candidate: Candidate):
    data = candidate.dict(exclude={"id"})
    
    modified_name = candidate.candidate_name
    if "object_type" in data and data["object_type"]:
        modified_name = f"{candidate.candidate_name} [{data['object_type']}]"
        
    supabase.table("lens_candidates").delete().eq("candidate_name", modified_name).execute()
    
    if "redshift" in data:
        data["einstein_radius"] = data.pop("redshift")
    if "magnitude" in data:
        data["mass_estimate"] = data.pop("magnitude")
    
    data["candidate_name"] = modified_name
    if "object_type" in data:
        data.pop("object_type")
        
    response = supabase.table("lens_candidates").insert(data).execute()
    if len(response.data) == 0:
        raise HTTPException(status_code=400, detail="Failed to create candidate")
        
    ret_data = response.data[0]
    if "einstein_radius" in ret_data:
        ret_data["redshift"] = ret_data.pop("einstein_radius")
    if "mass_estimate" in ret_data:
        ret_data["magnitude"] = ret_data.pop("mass_estimate")
    return ret_data

@app.get("/api/candidates", response_model=List[Candidate])
async def get_candidates():
    response = supabase.table("lens_candidates").select("*").execute()
    data = response.data
    for item in data:
        if "einstein_radius" in item:
            item["redshift"] = item.pop("einstein_radius")
        if "mass_estimate" in item:
            item["magnitude"] = item.pop("mass_estimate")
    return data
