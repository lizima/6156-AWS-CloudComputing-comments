from application_services.BaseApplicationResource import BaseRDBApplicationResource
from database_services.RDBService import RDBService as RDBService

# data schema: CommentInfo
# table_name: Comment
class CommentResource(BaseRDBApplicationResource):

    def __init__(self):
        super().__init__()

    @classmethod
    def get_links(cls, resource_data):
        pass

    @classmethod
    def find_by_template(cls, template, limit=None, offset=None, field_list=None):
        res = RDBService.find_by_template("CommentInfo", "Comment", template, limit, offset, field_list)
        return res

    @classmethod
    def create(cls, create_data):
        res = RDBService.create("CommentInfo", "Comment", create_data)
        return res

    @classmethod
    def update(cls, select_data, update_data):
        res = RDBService.update("CommentInfo", "Comment", select_data, update_data)
        return res

    @classmethod
    def delete(cls, template):
        res = RDBService.delete("CommentInfo", "Comment", template)
        return res

    @classmethod
    def find_linked_user(cls, template):
        res = RDBService.find_linked_user("UserInfo", "CommentInfo", "User", "Comment", template)
        return res
