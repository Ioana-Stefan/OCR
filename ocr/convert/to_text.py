import pika, json, tempfile, os
from bson.objectid import ObjectId
from PIL import Image
import pytesseract

def start(message, fs_images, fs_text, channel):
    
    message = json.loads(message)
    tf = tempfile.NamedTemporaryFile()
    out = fs_images.get(ObjectId(message["image_fid"]))
    tf.write(out.read())

    pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'
    text = pytesseract.image_to_string(Image.open(tf.name))
    print(text)
    tf.close()

    # Create a temporary text file and write the string to it
    file_path = 'temporary_file.txt'
    with open(file_path, 'w') as file:
        file.write(text)

    # Open the newly created file in binary read mode to upload
    with open(file_path, 'rb') as file_to_upload:
        # Store the file in GridFS
        fid = fs_text.put(file_to_upload, filename='uploaded_text_file.txt')
        
    message["text_fid"] = str(fid)

    os.remove(file_path)
    

    try:
        channel.basic_publish(
        exchange="",
        routing_key=os.environ.get("TEXT_QUEUE"),
        body=json.dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
        )
    )
    except Exception as err:
        print(err)
        fs_text.delete(fid)
        return "failed to publish message"


