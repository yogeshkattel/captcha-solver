import requests
from datetime import datetime
import os
import time
from PIL import Image
import io
from main.inferenceModel import predict
 
def download_image(image_url, save_as, session):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
  
    response = session.get(image_url, headers=headers, stream=True)
    if response.status_code == 200:
        # Convert image to PNG if it's not already in PNG format
        image = Image.open(io.BytesIO(response.content))
        image.save(save_as, 'PNG')
        predictImage  = predict(save_as)
        if len(predictImage) ==6:
          os.rename(save_as, f'captchas/{predictImage}.png')
        else:
            os.remove(save_as)
        print(f"Image downloaded and saved as '{save_as}'.")

    return True
 
def create_directory(directory_name):
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)
 
image_url = 'https://tms49.nepsetms.com.np/tmsapi/authApi/captcha/reload/d9b43138-73f8-4cf4-b61e-c7ca43718bbc'
save_directory = 'captchas'
create_directory(save_directory)
number_of_images = 100
delay_between_requests = 0.1  # seconds
 
with requests.Session() as session:
    for i in range(number_of_images):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")
        save_as = os.path.join(save_directory, f'captcha_image_{timestamp}.png')
        success = download_image(image_url, save_as, session)
        if not success:
            break
        time.sleep(delay_between_requests)
