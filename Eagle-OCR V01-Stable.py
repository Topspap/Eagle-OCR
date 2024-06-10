import io
from google.cloud import vision
import requests
from urllib.parse import unquote

# Eagle deafult API URL:
BASE_API_URL = "http://localhost:41595"

# Eagle Folder to Process OCR on: you have to create the folder in Eagle app and put the photos inside it
folderNameToProcess = "OCR_Process"

# Replace with the path to your credentials JSON file
credentials_path = r"Location\to\your\Google\API\Credentials\reflected-mark-235866-g4-0327c.json"

# -----------------------------------------------------------

def get_folderID(folderName):
    response = requests.get(f'{BASE_API_URL}/api/folder/list')
    data = response.json()

    folders = data['data']

    # Get the folder ID:
    for folder in folders:
        if folder['name'] == folderName:
            folderID = folder['id']
            print("Folder ID is:", folderID, "\n") # Print folder ID.
    return folderID

def get_items_with_no_annotation(max_iterations=None, folderID=None):
    offset = 0
    limit = 200
    items_with_no_annotation = []

    while True:
        print(f'Fetching items with offset {offset}...')

        response = requests.get(f'{BASE_API_URL}/api/item/list?limit={limit}&offset={offset}&folders={folderID}')
        data = response.json()

        if response.status_code != 200:
            print('Error fetching data:', response.status_code, response.text)
            break

        if 'data' not in data:
            print('Error: "data" key not found in response.')
            break

        items = data['data']

        if not items:
            print('No more items to fetch.')
            break

        if max_iterations is not None and offset >= max_iterations:
            print(f'Max iterations reached: {max_iterations}')
            break

        for item in items:  # you can add "and not item['annotation']" to exclude photo with note
            # Exclude photos that not in following extenstion 'jpg', 'jpeg', 'png', 'bmp', 'gif', 'webp', 'avif', 'pdf' &
            # already has note more than 3 charecters & has one of the follwoing tags: 'Auto_OCR', 'No_OCR', 'Broken_OCR'
            undesired_tags = {'Auto_OCR', 'No_OCR', 'Broken_OCR'}
            if item['ext'] in ['jpg', 'jpeg', 'png', 'bmp', 'gif', 'webp', 'avif', 'pdf'] and len(item['annotation']) < 3 and all(tag not in item['tags'] for tag in undesired_tags):
                items_with_no_annotation.append(item)

        offset += 1
        print(f'Iteration {offset} completed. Total items to process: {len(items_with_no_annotation)}')

    return items_with_no_annotation


def get_thumbnail_path(item_id):
    response = requests.get(f'{BASE_API_URL}/api/item/thumbnail?id={item_id}')
    data = response.json()
    if response.status_code == 200 and 'data' in data:
        return data['data']
    else:
        print('Error fetching thumbnail:', response.text)
        return None


def update_item_annotation(item_id, new_annotation=None, new_tags=None):
    response = requests.get(f'{BASE_API_URL}/api/item/info?id={item_id}')
    data = response.json()
    if response.status_code == 200 and 'data' in data and data['data']:
        existing_tags = data["data"]['tags']
        all_tags = list(set(existing_tags + new_tags))
        
        data = {
            'id': item_id,
            'tags': all_tags,
            'annotation': new_annotation
        }
        response = requests.post(f'{BASE_API_URL}/api/item/update', json=data)
        if response.status_code == 200:
            print('Tags updated successfully for item', item_id)
        else:
            print('Error updating annotation:', response.text)
    else:
        print('Error fetching item:', response.text)


def extract_text(imageToProcess):
    global credentials_path
    # Create a Vision client object
    client = vision.ImageAnnotatorClient.from_service_account_json(credentials_path)
    # Load the image
    with io.open(imageToProcess, "rb") as image_file:
        content = image_file.read()
    # Create an image object
    image = vision.Image(content=content)
    # Specify the desired feature (text detection)
    features = [vision.Feature(type_=vision.Feature.Type.TEXT_DETECTION)]
    # Send the request and handle the response
    request = vision.AnnotateImageRequest(image=image, features=features)
    response = client.annotate_image(request)
    # Process the response
    if response.error.message:
        raise Exception(response.error.message)
    # Access the full extracted text (without word-by-word breakdown)
    full_text = response.full_text_annotation.text
    # Print the full extracted text
    # print(full_text)
    return full_text


def main():
    folderID = get_folderID(folderNameToProcess)
    items_with_no_annotation = get_items_with_no_annotation(folderID=folderID)

    for item in items_with_no_annotation:
        thumbnail_path = get_thumbnail_path(item['id'])

        if thumbnail_path:
            thumbnail_path = unquote(thumbnail_path)
            try:
                annotation = extract_text(thumbnail_path)
                if annotation: # Run if Photo has Text
                    update_item_annotation(item['id'], new_annotation=annotation, new_tags=['Auto_OCR'])
                    print('Extracted text for item', item['id'])
                else:
                    update_item_annotation(item['id'], new_tags=['No_OCR']) # Add 'No_OCR' tag to photo that has no text
                    print('ID:',item['id'], 'Has no Text')

            except (FileNotFoundError, SyntaxError) as e:
                print(f'Error processing file: {thumbnail_path} ({e})')
                update_item_annotation(item['id'], new_tags=['Broken_OCR']) # Add 'Broken_OCR' tag for corrupted images
                print(f'Tagged item {item["id"]} as "Broken_OCR"')
                continue


if __name__ == '__main__':
    main()
