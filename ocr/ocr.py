import pika, sys, os, time
from pymongo import MongoClient
import gridfs

from convert import to_text

def main():
    try:
        client = MongoClient("mongodb", 27017)
        db_images = client.images
        db_text = client.text

        fs_images = gridfs.GridFS(db_images)
        fs_text = gridfs.GridFS(db_text)

        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host="rabbitmq")
        )

        channel = connection.channel()

        def callback(ch, method, properties, body):
            err = to_text.start(body, fs_images, fs_text, channel)

            if err:
                ch.basic_nack(delivery_tag=method.delivery_tag)
            else:
                ch.basic_ack(delivery_tag=method.delivery_tag)

        channel.basic_consume(
            queue=os.environ.get("IMAGE_QUEUE"),
            on_message_callback=callback
        )

        print("Waiting for messages")

        channel.start_consuming()
    except Exception as err:
        print(repr(err))
        return repr(err)

if __name__ == "__main__" :
    try:
        main()
    except Exception:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)