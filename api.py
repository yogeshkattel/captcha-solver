
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from io import BytesIO
from PIL import Image
from infereenceModelApi import predict 
app = FastAPI()

# Middleware for handling CORS issues
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.post("/upload-image/")
async def upload_image(file: UploadFile = File(...)):
    try:
        # Read image file
        contents = await file.read()
        image = BytesIO(contents)

        # Call your predict function
        result = await predict(image)

        return JSONResponse(content={"prediction": result})
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"An error occurred: {e}")
