
# from fastapi import FastAPI, File, UploadFile, HTTPException
# from fastapi.responses import JSONResponse
# from fastapi.middleware.cors import CORSMiddleware
# from io import BytesIO
# from PIL import Image
# from infereenceModelApi import predict
# app = FastAPI()

# # Middleware for handling CORS issues
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )



# @app.post("/upload-image/")
# async def upload_image(file: UploadFile = File(...)):
#     try:
#         # Read image file
#         contents = await file.read()
#         image = BytesIO(contents)

#         # Call your predict function
#         result = await predict(image)

#              # Check the length of the result
#         if len(result) != 5:
#             # Save the image with a name based on the result
#             filename = f"failedimages/{result}.png"
#             with open(filename, "wb") as f:
#                 f.write(contents)
            
#         return JSONResponse(content={"prediction": result})
    
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"An error occurred: {e}")

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from io import BytesIO
from PIL import Image
from infereenceModelApi import predict
import json
import os
import asyncio
from datetime import datetime

app = FastAPI()

# Middleware for handling CORS issues
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
ADMIN_TOKEN= "Hacker@141423"
# File paths
TOKEN_FILE = 'tokens.json'
REQUEST_COUNT_FILE = 'request_count.json'
HISTORICAL_REQUEST_COUNT_FILE = 'historical_request_count.json'


# In-memory storage
tokens = {}
request_counts = {}
historical_request_counts = {}

# Lock for file operations
file_lock = asyncio.Lock()

async def load_json(file_path):
    async with file_lock:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        return {}

async def save_json(file_path, data):
    async with file_lock:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)

async def load_data():
    global tokens, request_counts
    tokens = await load_json(TOKEN_FILE)
    request_counts = await load_json(REQUEST_COUNT_FILE)

async def save_data():
    await save_json(TOKEN_FILE, tokens)
    await save_json(REQUEST_COUNT_FILE, request_counts)
    await save_json(HISTORICAL_REQUEST_COUNT_FILE, historical_request_counts)

def check_token(token: str):
    if token not in tokens:
        raise HTTPException(status_code=401, detail="Invalid token")

    token_limit = tokens[token]
    if token not in request_counts:
        request_counts[token] = 0
    
    if request_counts[token] >= token_limit:
        raise HTTPException(status_code=403, detail="Token limit exceeded")

    request_counts[token] += 1
    asyncio.create_task(save_data())

@app.on_event("startup")
async def startup_event():
    await load_data()

@app.post("/upload-image/")
async def upload_image(file: UploadFile , token: str):
    try:
        # Check token
        check_token(token)

        # Read image file
        contents = await file.read()
        image = BytesIO(contents)

        # Call your predict function
        result = await predict(image)

        # Check the length of the result
        if len(result) != 5:
            # Save the image with a name based on the result
            filename = f"failedimages/{result}.png"
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, "wb") as f:
                f.write(contents)
        
        return JSONResponse(content={"prediction": result})

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"An error occurred: {e}")

async def archive_request_counts(token: str):
    if token in request_counts:

        historical_request_counts[token] = historical_request_counts.get(token, [])
        historical_request_counts[token].append({
            "timestamp": datetime.utcnow().isoformat(),
            "request_count": request_counts[token]
        })
        request_counts.pop(token)
        
        await save_data()

@app.post("/update-token/")
async def update_token(token: str, limit: int, admin_token: str):
    if admin_token==ADMIN_TOKEN:
        if token in tokens:
            
        # Archive current request counts before updating
            await archive_request_counts(token)
        tokens[token] = limit
        request_counts[token] = 0  # Reset the request count for the new token
        await save_data()
        return JSONResponse(content={"message": "Token updated successfully"})
    return JSONResponse(content={"message": "Only Admin Can Update Token", "warning":"This action has been notified to to the admin."})
