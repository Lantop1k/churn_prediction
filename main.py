from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS setup to allow cross-origin requests (for HTML page)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all domains
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (POST, GET, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Google Drive file ID
file_id = "17vCtATtPYv2PJzfL-ZRpj9BnmgS-QwNx"
url = f"https://drive.google.com/uc?id={file_id}"

# Loading data from Google Drive CSV link
data = pd.read_csv(url)
print("Dataset loaded successfully")
print(data.head())  # This will help you verify the data structure

# Input model that requires learner id and video title
class VideoQuery(BaseModel):
    learner_id: str  # Assuming learner_id is a string
    video_title: str

@app.post("/predict_churn")
def predict_churn(query: VideoQuery):
    # Logging to check incoming query
    print(f"Received request: learner_id={query.learner_id}, video_title={query.video_title}")

    # Find matching row based on learner_id and video_title
    row = data[
        (data['student_id'] == query.learner_id) &
        (data['video_title'].str.lower() == query.video_title.lower())
    ]

    if row.empty:
        print(f"No matching data found for learner_id: {query.learner_id}, video_title: {query.video_title}")
        raise HTTPException(status_code=404, detail="Learner/video not found")

    # Log the found row
    print(f"Found matching row: {row}")

    # Get completion rate and apply logic for churn prediction
    completion = row.iloc[0]['completion_rate_percent']
    churn = 1 if completion < 49 else 0

    # Return result
    return {
        "learner_id": query.learner_id,
        "video_title": query.video_title,
        "completion_rate_percent": completion,
        "churn": churn
    }
