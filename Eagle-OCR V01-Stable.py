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

        for item in items: # Exclude photos that already has note more than 3 charecters.
            if item['ext'] in ['jpg', 'jpeg', 'png', 'bmp', 'gif', 'webp', "avif"] and len(item['annotation']) < 3:
                items_with_no_annotation.append(item)

        offset += 1
        print(f'Iteration {offset} completed. Total items with few tags: {len(items_with_no_annotation)}')

    return items_with_no_annotation


def get_thumbnail_path(item_id):
    response = requests.get(f'{BASE_API_URL}/api/item/thumbnail?id={item_id}')
    data = response.json()
    if response.status_code == 200 and 'data' in data:
        return data['data']
    else:
        print('Error fetching thumbnail:', response.text)
        return None


def update_item_annotation(item_id, new_annotation):
    response = requests.get(f'{BASE_API_URL}/api/item/info?id={item_id}')
    data = response.json()
    if response.status_code == 200 and 'data' in data and data['data']:
        existing_tags = data["data"]['tags']
        all_tags = list(set(existing_tags + ['Auto_OCR'])) # Add 'Auto_OCR' tag to proccesed images that has text.
        
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
                    update_item_annotation(item['id'], annotation)
                    print('Extracted text for item', item['id'])
                else:
                    print('ID:',item['id'],'Name:',item['name'], 'Has no Text')

            except (FileNotFoundError, SyntaxError) as e:
                print(f'Error processing file: {thumbnail_path} ({e})')
                tags = ['Broken_OCR']  # Add 'Broken_OCR' tag for corrupted images
                update_item_annotation(item['id'], tags)
                print(f'Tagged item {item["id"]} as "Broken_OCR"')
                continue


if __name__ == '__main__':
    main()