import pika, json

def upload(f, fs, channel, access):
    try:
        fid = fs.put(f)
    except Exception as err:
        print(repr(err))
        return repr(err), 500
    
    message = {
        "image_fid": str(fid),
        "text_fid": None,
        "username": access["username"],
    }

    try:
        channel.basic_publish(
            exchange = "",
            routing_key = "image", 
            body = json.dumps(message),
            properties = pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )
    except Exception as err:
        print(repr(err))
        fs.delete(fid)
        return repr(err), 500