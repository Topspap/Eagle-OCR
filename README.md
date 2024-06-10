# Eagle-OCR
A Python code that upload photos from Eagle app to Google Cloud Vision API to perform OCR and then return the result to Eagle photo note.

The code is tested on Windows 10, Eagle-4.0-beta20, Python 3.12

Tested on .jpg .gif .png .webp .pdf

# How the Script work:

the script will access your Eagle opened library and look for a folder named "OCR_Process" Only (it will process only the photos inside this folder)

then upload the photos to google-cloud-vision to analysie and extrct text

then if the photo has text detected the result will be pasted into the photo note "annotation" && the photo will be tagged with "Auto_OCR"

or if the photo has no text detected it will be tagged with "No_OCR"

**Aslo note:** 
photos that already has note (annotation) more than 3 charecters it will be ignored and no tag will be added to it

photos that has any of the following tags will be ignore from the process: "Auto_OCR", "No_OCR", "Broken_OCR"

you can keep the photo in their original folder but also add them to "OCR_Process" folder to be processed, after process is done you can just remove them from "OCR_Process" folder.

# Installation:
1. Download the code "Eagle-OCR V01-Stable.py" with "requirements.txt"
2. Install the requirements from "requirements.txt"

   2.1 Run CMD
   
   2.2 Run the code: cd "Location\of\requirements.txt"
   
   2.3. Run the code: pip install -r requirements.txt
   
4. Setup your google-cloud-vision library and authentication, as you need the credentials.json file.
5. Create a Folder in Eagle named "OCR_Process" and put all the photos that you need to perform OCR in it.
6. Open "Eagle-OCR V01-Stable.py" and change the credentials_path to where your credentials.json is located.
7. Simply run the code

**Note:** 
The google-cloud-vision library requires additional setup and authentication steps to work with the Google Cloud Vision API. Make sure to follow the official Google Cloud documentation for setting up the required credentials and authentication.

you can use claude.ai or gemini.google.com to help you further...
