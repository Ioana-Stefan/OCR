import os, gridfs, pika , json
from flask import Flask, request, send_file
from auth import validate
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from auth_svc import access
from storage import util


server = Flask(__name__)

mongo_image = PyMongo(server, uri="mongodb://mongodb:27017/images")
mongo_text  = PyMongo(server, uri="mongodb://mongodb:27017/text")
fs_image = gridfs.GridFS(mongo_image.db)
fs_text  = gridfs.GridFS(mongo_text.db)

connection  = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq", heartbeat=600))
channel     = connection.channel()

@server.route("/login", methods=["POST"])
def login():
    token, err = access.login(request)

    if not err:
        return token
    else:
        return err
    
@server.route("/upload", methods=["POST"])
def upload():
    access, err = validate.token(request)
    if err:
        return err
    
    access = json.loads(access)

    if access["admin"]:
        if len(request.files) > 1 or len(request.files) < 1:
            return "only one file permitted", 400
        
        for _, f in request.files.items():
            err = util.upload(f, fs_image, channel, access)

            if err:
                return err;

        return "success", 200
    
    else:
        return "not authorized", 401
    
@server.route("/download", methods=["GET"])
def download():
    access, err = validate.token(request)
    if err:
        return err
    
    access = json.loads(access)

    if access["admin"]:
        fid_string = request.args.get("fid")

        if not fid_string:
            return "fid is required", 400

        try:
            out = fs_text.get(ObjectId(fid_string))
            return send_file(out, download_name=f"{fid_string}.txt")
        except Exception as err:
            print(err)
            return "error downloading the file", 500

    return "not authorized", 401


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8080)