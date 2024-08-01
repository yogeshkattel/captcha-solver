


import requests
from datetime import datetime
import os
import time
from PIL import Image
import io
from main.inferenceModel import predict
from bs4 import BeautifulSoup
import re
import time
import google.generativeai as genai

def solveCaptcha(imagePath) :
    genai.configure(api_key="AIzaSyA6fi3rnqSmUdWkEiH2e63J78-UBfnS9bI")
    sample_file = genai.upload_file(path=imagePath, display_name='image')
    model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")

    response =model.generate_content( [sample_file, 'can you extract the text from the image and put the text inside ""'])
    pattern = r'"(.*?)"'
    matches = re.findall(pattern, response.text)
    print(response.text)
    return matches[0]

def download_image(image_url, save_as, session):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    
    response = session.get(image_url, headers=headers, stream=True)
    
    if response.status_code == 200:
        # Convert image to PNG if it's not already in PNG format
        image = Image.open(io.BytesIO(response.content))
        image.save(save_as, 'PNG')
        print(save_as)
        time.sleep(2)
        # try :
        predictImage = predict(f'./{save_as}'  )
        print(predictImage)
            # if len(predictImage) == 5:
            #     os.rename(save_as, f'captchas/{predictImage}.png')
            # else:
            #     os.remove(save_as)
            # print(f"Image downloaded and saved as '{save_as}'.")
        # except:
        os.remove(save_as)

            # return True


    return True

def create_directory(directory_name):
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)

def get_captcha_image_url(session):
    url = 'https://blsitalypakistan.com/account/login'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    response = session.get(url, headers=headers)
    

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        img_tag = soup.find('img', id='Imageid')
        if img_tag and 'src' in img_tag.attrs:
        
            return img_tag['src']
    return None

save_directory = 'captchas'
create_directory(save_directory)
number_of_images = 100
delay_between_requests = 0.1  # seconds


def solve_captcha_with_gemini(image_path):
    api_url = "https://gemini.google.com/solve_captcha"
    api_key = "AIzaSyA6fi3rnqSmUdWkEiH2e63J78-UBfnS9bI"  # Replace with your actual API key

    with open(image_path, 'rb') as image_file:
        files = {'file': image_file}
        headers = {'Authorization': f'Bearer {api_key}'}
        response = requests.post(api_url, files=files, headers=headers)

    if response.status_code == 200:
        solved_token = response.json().get('solved_token')
        return solved_token
    else:
        print(f"Failed to solve CAPTCHA. Status code: {response.status_code}")
        return None

def process_and_save_solved_captcha(image_path, solved_token, new_directory):
    if solved_token:
        file_extension = os.path.splitext(image_path)[1]
        new_file_name = f"{solved_token}{file_extension}"
        new_file_path = os.path.join(new_directory, new_file_name)
        os.rename(image_path, new_file_path)
        print(f"File renamed and moved to '{new_file_path}'.")

with requests.Session() as session:
    for i in range(number_of_images):
        captcha_url = get_captcha_image_url(session)
        if captcha_url:
            full_captcha_url = f'{captcha_url}'
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")
            save_as = os.path.join(save_directory, f'captcha_image_{timestamp}.png')
            success = download_image(full_captcha_url, save_as, session)
            if not success:
                break
            time.sleep(delay_between_requests)




 

