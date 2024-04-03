import cv2
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Form, HTTPException
from insightface.app import FaceAnalysis
from insightface.model_zoo import get_model
from typing import Any


app = FastAPI()
app.add_middleware(CORSMiddleware,
                   allow_origins=["*"],  # Allows all origins
                   allow_credentials=True,
                   allow_methods=["*"],  # Allows all methods
                   allow_headers=["*"],)  # Allows all headers


def get_swapp() -> FaceAnalysis:
    """
    Initializes, prepares size and returns a FaceAnalysis object for face detection and analysis.

    :return: A FaceAnalysis object configured for use.
    """
    swapp = FaceAnalysis(name='buffalo_l')
    swapp.prepare(ctx_id=0, det_size=(640, 640))
    return swapp


def get_swapper() -> Any:
    """
    Loads and returns a face swapping model.

    :return: A model object for face swapping.
    """
    return get_model('inswapper_128.onnx', download=False)


@app.post('/analyze_faces')
async def analyze_faces(file_path: str = Form(...)) -> dict:
    """
    Analyzes faces in the provided image file, returning age, gender, and bounding box information.

    :param file_path: Path to the image file to analyze.
    :return: Dictionary containing detected face information.
    """
    read_img = cv2.imread(file_path)
    if read_img is None:
        raise HTTPException(status_code=400, detail="Invalid file path or unsupported image format")
    faces = SWAPP.get(read_img)
    if not faces:
        return {"message": "No faces detected"}
    results = []
    for face in faces:
        gender = 1 if face.gender > 0 else 0
        bbox = face.bbox.astype(int).tolist()
        results.append({"age": face.age, "gender": gender, "bbox": bbox})
    return {"faces": results}


# Create instances of detectors and swappers
SWAPP = get_swapp()
SWAPPER = get_swapper()
