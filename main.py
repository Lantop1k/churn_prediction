from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

file_id = "vCtATtPYv2PJzfL-ZRpj9BnmgS-QwNx"  # your file ID
url = f"https://drive.google.com/uc?id={file_id}"

data=pd.read_csv(url)

# Input model
# model requires learner id and video title
class VideoQuery(BaseModel):
    learner_id: str
    video_title: str

@app.post("/predict_churn")
def predict_churn(query: VideoQuery):
    # Find matching row
    print(query.learner_id)
    row = data[
        (data['student_id'] == query.learner_id) &
        (data['video_title'].str.lower() == query.video_title.lower())
    ]

    if row.empty:
        raise HTTPException(status_code=404, detail="Learner/video not found")

    # Get completion rate and apply logic
    completion = row.iloc[0]['completion_rate_percent']
    churn = 1 if completion < 49 else 0
    return {
        "learner_id": query.learner_id,
        "video_title": query.video_title,
        "completion_rate_percent": completion,
        "churn": churn
    }

