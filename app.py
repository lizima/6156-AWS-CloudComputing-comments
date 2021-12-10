import time
from flask import Flask, Response, request, redirect, url_for, session
from flask_cors import CORS
import json
import logging
import os
from flask_dance.contrib.google import make_google_blueprint, google
from oauthlib.oauth2.rfc6749.errors import TokenExpiredError
import re

from application_services.CommentsResource.comment_service import CommentResource
from application_services.UsersResource.user_addr_service import UserAddrResource
from application_services.UsersResource.user_service import UserResource
from application_services.AppHTTPStatus import AppHTTPStatus
# from application_services.smarty_address_service import SmartyAddressService
from database_services.RDBService import RDBService as RDBService

# from flask_dance.contrib.google import make_google_blueprint, google
# import middleware.simple_security as simple_security
from middleware.notification import NotificationMiddlewareHandler as NotificationMiddlewareHandler
from middleware.steamsignin import SteamSignIn

import middleware.security as security

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# pagination data
OFFSET = 0
MAXLIMIT = 10 #20

app = Flask(__name__)
CORS(app)
app.secret_key = "supersekrit"
os.environ['steawmpowered_key'] = 'BBC837ECFD8415A58B7575D83BCDA639'
@app.errorhandler(404)
def not_found(e):
    rsp = Response(response=json.dumps({"ERROR": "404 NOT FOUND"}, default=str, indent=4), status=404,
                   content_type="application/json")
    return rsp


@app.errorhandler(500)
def messy_error(e):
    print(e)
    rsp = Response(json.dumps({"ERROR": "500 WEIRD SERVER ERROR"}, default=str, indent=4), status=500,
                   content_type="application/json")
    return rsp


# help function for pagination
def handle_links(url, offset, limit):
    if "?" not in url:
        url += "?offset=" + str(offset) + "&limit=" + str(limit)
    else:
        if "offset" not in url:
            url = url + "&offset=" + str(offset)
        if "limit" not in url:
            url = url + "&limit=" + str(limit)
    links = []
    nexturl = re.sub("offset=\d+", "offset=" + str(offset + limit), url)
    prevurl = re.sub("offset=\d+", "offset=" + str(max(0, offset - limit)), url)
    links.append({"rel": "self", "href": url})
    links.append({"rel": "next", "href": nexturl})
    links.append({"rel": "prev", "href": prevurl})
    return links


@app.route('/')
def hello_world():
    return '<u>Hello World!</u>'


@app.route('/comments', methods=['GET', 'POST'])
def get_comments():
    if request.method == 'GET':
        offset = int(request.args.get("offset", OFFSET))
        limit = int(request.args.get("limit", MAXLIMIT))
        if limit > MAXLIMIT:
            limit = MAXLIMIT
        query_parms = dict()
        arg_list = [i for i in request.args.keys()]
        for i in arg_list:
            if i.lower() != "offset" and i.lower() != "limit":
                query_parms[i] = request.args.get(i)
        data, exception_res = CommentResource.find_by_template(query_parms, limit, offset)
        links = handle_links(request.url, offset, limit)
        if data is not None:
            res = data
        else:
            res = data
        rsp = AppHTTPStatus().format_rsp(res, exception_res, method=request.method, path=request.path)
        return rsp
    elif request.method == 'POST':
        create_data = request.form
        if create_data:
            pass
        else:
            create_data = request.json
        res, exception_res = CommentResource.create(create_data)
        rsp = AppHTTPStatus().format_rsp(res, exception_res, method=request.method, path=request.path)
        return rsp
    else:
        res = Response()
        res.headers['Access-Control-Allow-Origin'] = '*'
        return res
    pass

@app.route('/comments/<comment_id>', methods=['GET', 'PUT', 'DELETE'])
def get_comment_by_comment_id(comment_id):
    if request.method == 'GET':
        template = {"comment_id": comment_id}
        res, exception_res = CommentResource.find_by_template(template, 1, 0)
        rsp = AppHTTPStatus().format_rsp(res, exception_res, method=request.method, path=request.path)
        return rsp
    elif request.method == 'PUT':
        content = request.form['content']
        select_data = {"comment_id": comment_id}
        update_data = {"content":content}
        res, exception_res = CommentResource.update(select_data, update_data)
        rsp = AppHTTPStatus().format_rsp(res, exception_res, method=request.method, path=request.path)
        return rsp
    elif request.method == 'DELETE':
        template = {"comment_id": comment_id}
        res, exception_res = CommentResource.delete(template)
        rsp = AppHTTPStatus().format_rsp(res, exception_res, method=request.method, path=request.path)
        return rsp

@app.route('/forums/<forum_id>/comments', methods=['GET'])
def get_comments_from_forum_id(forum_id):
    if request.method == 'GET':
        template = {"forum_id": forum_id}
        offset = int(request.args.get("offset", OFFSET))
        limit = int(request.args.get("limit", MAXLIMIT))
        if limit > MAXLIMIT:
            limit = MAXLIMIT
        res, exception_res = CommentResource.find_by_template(template, limit, offset)
        rsp = AppHTTPStatus().format_rsp(res, exception_res, method=request.method, path=request.path)
        return rsp

@app.route('/comments/<comment_id>/user', methods=['GET'])
def get_linked_user(comment_id):
    if request.method == 'GET':
        template = {"comment_id": comment_id}
        res = CommentResource.find_linked_user(template)
        rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
        return rsp


if __name__ == '__main__':
    app.run(port=8080, debug=False, host="0.0.0.0")
