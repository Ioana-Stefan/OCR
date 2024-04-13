# Python OCR Microservices Application

This project contains multiple microservices designed to work together inside a Kubernetes cluster in order to convert text from images into text documents.

## Description

From a design point of view I tried to separate each big important task handler into a separate service and I adopted a loosely coupled architecture making use of a message broker service in order to implement an asynchronous connection between services.

In order to experiment and practice with microservices design and implementation features the project is making use of different technology stacks.

The actual cluster used for development is Minikube, a lightweight version of Kubernetes that can be easily deployed locally. I decided to use Docker for the container implementation and DockerHub as the container registry, these two being very straightforward and working seemingly together with Minikube

The project contains the following services:

**auth** -> Authentication and Authorization service. Used to authenticate, authorize and validate users with the help of JWT. </br>
**gateway** -> A gateway service designed to be the entry point of the application. </br>
**MySQL** -> MySQL database used for storing users credentials. </br>
**MongoDB** -> MongoDB database used for storing files. GridFS driver is used in order to store documents bigger than 16 MB. </br>
**rabbitmq** -> RabbitMQ is a message-broker which holds two separate queues (image, text) where the micro services will publish and consume messages. </br>
**ocr** -> Converter service. It's making use of Tesseract binary and PyTesseract library in order to extract text from images. </br>
**notification** -> Notification service. As soon as the conversion is done, will make use of an SMTP server in order to send the user an email letting him know that the conversion is completed and the file is ready for download. </br>

Every service will have a **manifests** folder where YAML files for the Kubernetes configuration can be found.

**auth**, **gateway**, **ocr** and **notification** service are stateless deployments. Because persistence is needed for the databases and the message broker these were deployed as StatefulSets, and they had PersistentVolumes and PersistentVolumeClaim attached to them. Every microservice has a network service attached to it with the exception of **ocr** and **notification**. These two are not http(s)servers and they communicate with the rest of the microservices through RabbitMQ queues, thus they don't need a network interface to be accessible to the cluster, they only need to be able to connect to the RabbitMQ server. **gateway** and **rabbitmq** have an ingress attached to them so we can access them externally. The gateway will be accessed by sending hhtp requests and the RabbitMQ server will be accessed from the web browser in order for us to interact with the manager console for configurating our queues.

Python was the programming language of choice. You will also find SQL and javascript init files that will be attached to docker entrypoints in order to preconfigure the databases(e.g. create a database user, create a table with users and insert a user, etc.)

Application flow:

1. Send request to gateway to authenticate
2. Request comes back with JWT. Every request you send must include the JWT.
3. Send request with an image that you want to extract the text from
4. Gateway validates you request, will take the file and it will upload it in the database. After upload complete will write a message to the **image** queue with the file id returned from the database.
5. OCR service reads the queue and gets the file from the database. After reading the text from the image it uploads the text to the database and puts a message to the **text** queue for the notification service.
6. The notification service reads the message and sends an email to the user with the fid of the text.

## Install, Configuration and Run

I developed and ran the project on Ubuntu 22.04 LTS but everything can be done as well on Windows or MacOS.

Installation:

1. Instal Python 3.10.
2. Install [Docker](https://docs.docker.com/engine/install/).
3. Install [Minikube](https://minikube.sigs.k8s.io/docs/start/).
4. Install [kubectl](https://kubernetes.io/docs/tasks/tools/).

Configuration:

1. Go to mysql/init.sql and change the databse user credentials and the credentials of the user that you would want to authenticate to in order to run the application. Don't forget to also make these changes in auth/manifests/configmap.yaml.
2. Start Minikube and enable ingress and ingress-dns addons. Also you need to run **minikube tunnel** in order to channel the ingress traffic to localhost.
3. If you are on Linux or MacOS you can go to /etc/hosts and add the output ip address from minikube tunnel and match it to the DNS name the ingress is set. (e.g. 192.168.49.2 imagetotext.com 192.168.49.2 rabbitmq-manager.com). If you are on Windows you go to C:\Windows\System32\drivers\etc\hosts.
4. Go to notification/send/email.py and uncomment the code. Please fill the credentials for the email address of the service inside notification/manifests/secret.yaml
5. Deploy the rabbitmq service using **kubectl apply -f manifests**
6. Connect to the manager console inside the web browser by connecting to rabbitmq-manager.com. Default username and password are bot 'guest'. Go to queues and create a text and image queue. Use the default settings, just type the queue name and create it. If you would like you can use a different exchange than the default one but you will have to change the code inside the dependent services. You can set up persistance, etc., but for a fast run, you should just create them without any additional configuration.
7. Deploy all the other resources inside the cluster.

Run:

1. curl -X POST http://imagetotext.com/login -u email:password -> First send a request with you credentials in order to be authenticated and to receive a JWT
2. curl -X POST -F 'file=@./image.jpg' -H 'Authorization: Bearer <JWT_TOKEN>' http://imagetotext.com/upload -> Send a request with a file and the received JWT
3. curl --output -X GET -H 'Authorization: Bearer <JWT_TOKEN>' http://imagetotext.com/download?fid={fid_received_in_the_email} -> After receiving the email send a request using the fid to download the file.
