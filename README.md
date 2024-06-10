# Eagle-OCR
A Python code that upload photos from Eagle app to Google Cloud Vision API to perform OCR and then return the result to Eagle photo note.
The code is tested on Windows 10, Eagle-4.0-beta20, Python 3.12

**Installation:**

1. download the code "Eagle-OCR V01-Stable.py" with "requirements.txt"
2. Install the requirements from "requirements.txt"
  2.1. Rum CMD
  2.2. run the code: cd "Location\of\requirements.txt"
  2.3. run the code: pip install -r requirements.txt
3. Setup your google-cloud-vision library and authentication, You need the credentials.json file.
5. Create a Folder in Eagle named "OCR_Process" and put all the photos that you need to perform OCR on it.
6. Open "Eagle-OCR V01-Stable.py" and change the credentials_path to where your credentials.json is.
7. Simply run the code

**Note:** 
The google-cloud-vision library requires additional setup and authentication steps to work with the Google Cloud Vision API. Make sure to follow the official Google Cloud documentation for setting up the required credentials and authentication.
