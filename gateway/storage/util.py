import pika, json

def upload(f, fs, channel, access):
    try:
        fid = fs.put(f)
    except Exception as err:
        return "internal server error", 500
    
    message = {
        "image_fid": str(fid),
        "text_fid": None,
        "username": access["username"],
    }

    try:
        channel.basic_publish(
            exchange = "",
            routing_key = "image", 
            ody = json.dump(message),
            properties = pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            )
        )
    except Exception as err:
        fs.delete(fid)
        return "internal server error", 500