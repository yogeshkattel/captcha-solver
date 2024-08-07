import aiohttp
import asyncio
import time
from aiohttp import ClientTimeout
from PIL import Image
import io
import numpy as np
from rembg import remove 

async def compress_image(image_path, output_path, quality=50):
    """Compresses the image, removes the red color, saves it to a file, and returns a BytesIO object."""
    with Image.open(image_path) as img:
        # Convert image to RGBA if it's not already
        img = img.convert("RGBA")

        # Remove the red color and make background transparent
        data = np.array(img)
        red = data[:, :, 0]
        green = data[:, :, 1]
        blue = data[:, :, 2]
        alpha = np.ones(red.shape, dtype=np.uint8) * 255

        # Set alpha to 0 where red component is dominant
        mask = (red > green) & (red > blue)
        alpha[mask] = 0

        # Apply alpha to image
        data[:, :, 3] = alpha
        img = Image.fromarray(data, 'RGBA')

        # Convert to RGB and compress
        img_rgb = img.convert("RGB")
        
        # Save to a file
        img_rgb.save(output_path, format='JPEG', quality=quality, optimize=True)
        
        # Create a BytesIO buffer to return
        buffer = io.BytesIO()
        img_rgb.save(buffer, format='JPEG', quality=quality, optimize=True)
        buffer.seek(0)
        return buffer

async def solve_captcha_async(session, image_path):
    url = "http://38.242.213.32:8000/upload-image/?token=token123huzaifa"
    headers = {"accept": "application/json"}
    output_path = "processed_image.jpeg"

    try:
        compressed_image = await compress_image(image_path, output_path)
        data = {'file': compressed_image}
        
        async with session.post(url, headers=headers, data=data) as response:
            response.raise_for_status()  # Raise exception for HTTP errors
            response_json = await response.json()
            return response_json
    except Exception as e:
        print(f"Captcha Not Returned! Error: {e}")
        return None

async def fetch_with_timeout(session, image_path, timeout):
    try:
        return await asyncio.wait_for(solve_captcha_async(session, image_path), timeout)
    except asyncio.TimeoutError:
        print(f"Request timed out after {timeout} seconds")
        return None

async def main(image_path):
    start_time = time.time()

    # Adjust client timeout for faster response
    timeout = ClientTimeout(total=2.5, connect=1, sock_connect=1, sock_read=2.5)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        # Increase the number of parallel requests
        tasks = [asyncio.create_task(fetch_with_timeout(session, image_path, 2.5)) for _ in range(5)]
        
        # Wait for the first completed task
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        
        # Cancel remaining tasks
        for task in pending:
            task.cancel()
        
        result = None
        for task in done:
            result = await task
            if result:
                break
    
    end_time = time.time()
    print(f"Total time taken: {end_time - start_time:.3f} seconds")
    
    if result:
        print(result)
        return result.get('prediction')
    else:
        print("No result obtained.")
        return None

image_path = "f6c84745-50b4-4012-a3db-d50004b5a9a7-removebg-preview.png"
res = asyncio.run(main(image_path))
print(res)
