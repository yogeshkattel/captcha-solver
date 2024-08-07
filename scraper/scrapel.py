import requests
from datetime import datetime
import os
import time
from PIL import Image
import io
# from main.inferenceModel import predict
from bs4 import BeautifulSoup
import re
import cv2
import numpy as np

import logging
import colorlog


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



def download_image(image_url, save_as, session):
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
        predictImageAi =  solve_captcha_ai(f'./{save_as}')
        print(predictImageAi)
        image_cv = np.array(image)
        cv2.imshow(f'{predictImageAi}', image_cv)
        cv2.waitKey(5000)
        cv2.destroyAllWindows()
        os.remove(save_as)


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




def run():
    with requests.Session() as session:
        for i in range(number_of_images):
            captcha_url = get_captcha_image_url(session)
            if captcha_url:
                full_captcha_url = f'{captcha_url}'
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")
                save_as = os.path.join(save_directory, f'captcha_image_{timestamp}.png')
                success = download_image(full_captcha_url, save_as, session)
                if not success:
                    logger.error('Failed to download image.')
                    break
                time.sleep(delay_between_requests)

def main():
    run()
        
if __name__ == '__main__':
    main()


