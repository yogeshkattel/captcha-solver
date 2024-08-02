import requests
from datetime import datetime
import os
import time
from PIL import Image
import io
# from main.inferenceModel import predict
from bs4 import BeautifulSoup
import re
import google.generativeai as genai
import logging
import colorlog
import argparse

# Configure logging with colorlog
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s%(asctime)s - %(levelname)s - %(message)s',
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    }
))

logger = colorlog.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
def solve_captcha_ai(image_path):
    url = "https://captcha.nepdevtech.com/upload-image/"
    headers = {
        "accept": "application/json",
        "accept-language": "en-US,en;q=0.8",
        "sec-ch-ua": "\"Not)A;Brand\";v=\"99\", \"Brave\";v=\"127\", \"Chromium\";v=\"127\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "sec-gpc": "1"
    }
    files = {'file': (image_path, open(image_path, 'rb'), 'image/jpeg')}
    response = requests.post(url, headers=headers, files=files)
    return response.json()

def solveCaptcha(imagePath, token):
    genai.configure(api_key=token)
    sample_file = genai.upload_file(path=imagePath, display_name='image')
    model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")

    response = model.generate_content([sample_file, 'can you extract the text from the image and put the text inside ""'])
    resData = response.candidates[0].content.parts[0].text
    
    pattern = r'"(.*?)"'
    matches = re.findall(pattern, resData)
    logger.info(f'Gemini response: {resData}')
    return matches[0]

def download_image(image_url, save_as, session, token):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    response = session.get(image_url, headers=headers, stream=True)

    if response.status_code == 200:
        # Convert image to PNG if it's not already in PNG format
        image = Image.open(io.BytesIO(response.content))
        image.save(save_as, 'PNG')
        logger.info(f'Image saved as {save_as}')
        time.sleep(2)
        try:
           
            predictImage = solveCaptcha(f'./{save_as}', token)
            predictImageAi =  solve_captcha_ai(f'./{save_as}'
                                               )
            print(predictImage, predictImageAi['prediction'])
            print((predictImage != predictImageAi['prediction']))
            if predictImage != predictImageAi['prediction']:
                os.rename(save_as, f'captchas/{predictImage}.png')
                logger.info(f'Image renamed to {predictImage}.png')
            else:
                os.remove(save_as)
                logger.warning(f'Image {save_as} removed due to invalid prediction length.')
        except Exception as e:
            
            os.remove(save_as)
            logger.error(f'Error in solving captcha for {save_as}: {e}')
            time.sleep(5)
            return True

    return True

def create_directory(directory_name):
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)
        logger.info(f'Directory {directory_name} created.')

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
            logger.info(f'Captcha image URL found: {img_tag["src"]}')
            return img_tag['src']
    logger.warning('Captcha image URL not found.')
    return None

save_directory = 'captchas'
create_directory(save_directory)
number_of_images = 100
delay_between_requests = 0.1  # seconds




def run(token):
    with requests.Session() as session:
        for i in range(number_of_images):
            captcha_url = get_captcha_image_url(session)
            if captcha_url:
                full_captcha_url = f'{captcha_url}'
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")
                save_as = os.path.join(save_directory, f'captcha_image_{timestamp}.png')
                success = download_image(full_captcha_url, save_as, session, token)
                if not success:
                    logger.error('Failed to download image.')
                    break
                time.sleep(delay_between_requests)

def main():
    # Setup argument parser
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('number', type=int, help='An integer number for case selection')
    args = parser.parse_args()
    
    # Simulate switch-case with if-else
    if args.number == 1:
        run("AIzaSyD7ap4WEUn49CKwCWFkRSP-Eqn-5pybkn4")
        
    elif args.number == 2:
        run("AIzaSyA6fi3rnqSmUdWkEiH2e63J78-UBfnS9bI")
        
    elif args.number == 3:
        run("AIzaSyAR92xg7diVXos2J3p5HRTPq9zhNNAlJjI")
        
    elif args.number ==4:
        run("AIzaSyD8Wgq3NkhT13JkhvzfqWcQN08aCkBK1A4")
    elif args.number==5:
        run("AIzaSyCQDiUbUI8Os01YVFLu4VfZloS7C3Fi0tU")
    else:
        print("Invalid case")
        
if __name__ == '__main__':
    main()


