from flask import Response
import json
from collections import OrderedDict

class AppHTTPStatus(Exception):
    """
    do not deal with 405 errors because this error won't cause messy report log.
    """

    other_code             =    200
    post_create            =    201
    delete                 =    204
    bad_data               =    400   # pymysql.err.DataError
    route_missing          =    404
    integrity_constraint   =    422   # pymysql.err.IntegrityError
    severe_server_err      =    500

    def __init__(self, code=None, message=None, ex=None):
        self.code = code
        self.message = message
        self.original_exception = ex

    def __str__(self):
        """
        TODO We should map MySQL and infrastructure exceptions to more meaningful exceptions.
        :return:
        """
        result = ""

        if self.code:
            self.code = str(self.code)
        else:
            self.code = "None"

        if self.message is None:
            self.messsage = "None"

        result += "AppHTTPStatus: code: {:<5}, message: {}".format(self.code, self.message)

        if self.original_exception is not None:
            result += "\nOriginal exception = " + repr(self.original_exception)

        return result

    def format_rsp(self, rsp_normal, rsp_exc, method, path=None):
        """

        :param rsp_normal: normal return response [modified number of lines in DB]
        :param rsp_exc: exception response
        :param path: current path of the url
        :return: Flask Response obj contains processed response header msg
        """
        if rsp_normal is not None and rsp_exc is not None:
            pass # not likely to happen
        elif rsp_normal is not None:
            if method == 'POST':
                rsp = Response(json.dumps({"location": path}, default=str, indent=4), status=self.post_create,
                               content_type="application/json")
            elif method == 'GET':
                # if type(rsp_normal) != dict:
                #     if len(rsp_normal) == 1:
                #         rsp_normal = rsp_normal[0]
                #     elif len(rsp_normal) > 1:
                #         rsp_normal = {'dataCollection': rsp_normal}
                #     else:
                #         rsp_normal = None
                # rsp = Response(json.dumps(rsp_normal, default=str, indent=4, separators=(',', ':')),
                #                status=self.other_code, content_type="application/json")
                rsp = Response(json.dumps(rsp_normal, default=str, indent=4),
                               status=self.other_code, content_type="application/json")
            elif method == 'DELETE':
                rsp = Response(json.dumps({"Number of rows affected": rsp_normal}, default=str, indent=4),
                               status=self.delete, content_type="application/json")
            else:
                rsp = Response(json.dumps({"Number of rows affected": rsp_normal}, default=str, indent=4),
                               status=self.other_code, content_type="application/json")
        elif rsp_exc is not None:
            if len(rsp_exc[1]) == 2:
                if rsp_exc[0].split(".")[-1] == "IntegrityError":
                    exc_status = self.integrity_constraint
                else:
                    exc_status = self.bad_data
                rsp = Response(json.dumps({"Number of rows affected": rsp_normal,
                                           "EXCEPTION/ERROR TYPE": rsp_exc[0],
                                           "EXCEPTION/ERROR CODE": rsp_exc[1][0],
                                           "EXCEPTION/ERROR DETAILS": rsp_exc[1][1]}, default=str, indent=4),
                               status=exc_status, content_type="application/json")
            else:
                exc_status = self.severe_server_err
                rsp = Response(json.dumps({"Number of rows affected": rsp_normal,
                                           "EXCEPTION/ERROR TYPE": rsp_exc[0],
                                           "EXCEPTION/ERROR DETAILS": rsp_exc[1][0]}, default=str, indent=4),
                               status=exc_status, content_type="application/json")
        else:
            pass # also not likely to happen
        return rsp
