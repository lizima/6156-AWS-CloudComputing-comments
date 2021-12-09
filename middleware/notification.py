import json
import boto3
import middleware.context as context
import os

SNSARN = "arn:aws:sns:us-east-1:213660796932:sprint2_6156_1"
REGION = "us-east-1"
notifydict = {"path": "/users", "method": "GET"}


class NotificationMiddlewareHandler:
    """
    Has a dict/JSON object in the file that defines:
       - Which paths trigger an SNS notification.
       - Which HTTP methods trigger the notification.
       - An example might be {“path”: “/api/users”, “method”: “POST”}
       - The after_request processing calls notification. If the path and method match an entry in the dict,
            the middleware sends an event to an SNS topic.
    """
    sns_client = None

    def __init__(self):
        pass

    @classmethod
    def get_sns_client(cls):
        if NotificationMiddlewareHandler.sns_client is None:
            key_id = os.getenv('AWS_ACCESS_KEY_ID')
            key = os.getenv('AWS_SECRET_ACCESS_KEY')
            NotificationMiddlewareHandler.sns_client = sns = boto3.client("sns",
                                                                          aws_access_key_id=key_id,
                                                                          aws_secret_access_key=key,
                                                                          region_name=REGION)
        return NotificationMiddlewareHandler.sns_client

    @classmethod
    def get_sns_topics(cls):
        s_client = NotificationMiddlewareHandler.get_sns_client()
        result = response = s_client.list_topics()
        topics = result["Topics"]
        return topics

    @classmethod
    def send_sns_message(cls, topic, message):
        s_client = NotificationMiddlewareHandler.get_sns_client()
        response = s_client.publish(
            TargetArn=topic,
            Message=json.dumps({"default": json.dumps(message)}),
            MessageStructure='json'
        )
        print("Publish response = ", json.dumps(response, indent=2))


    @staticmethod
    def notify(request, response):

        # if request.path in subscriptions:
        #     notification = {}
        #     try:
        #         request_data = request.get_json()
        #     except Exception as e:
        #         request_data = None

        path = request.path.split("?")[0]
        if not (path == notifydict["path"] and request.method == notifydict["method"]):
            # print(path, request.method)
            # print("No need to notify")
            return
        notification = {}

        try:
            request_data = request.get_json()
        except Exception as e:
            request_data = None
        if request.method == "GET":
            # t = response.get_data().decode("ascii")
            notification = json.loads((response.get_data()).decode('utf-8'))
        # elif request.method == "POST":
        #     notification["change"] = "CREATED"
        #     notification["new_state"] = request_data
        #     notification["params"] = path
        # elif request.method == "PUT":
        #     notification["change"] = "UPDATE"
        #     notification["new_state"] = request_data
        #     notification["params"] = path
        # elif request.method == "DELETE":
        #     notification["change"] = "DELETE"
        #     notification["params"] = path
        else:
            notification = None

        NotificationMiddlewareHandler.send_sns_message(
            SNSARN,
            notification
        )
