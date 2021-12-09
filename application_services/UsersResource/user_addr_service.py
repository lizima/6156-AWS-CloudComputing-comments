from database_services.RDBService import RDBService as RDBService


# data schema: UserInfo
# table_name: Address
class UserAddrResource(RDBService):

    def __init__(self):
        super().__init__()


    @classmethod
    def get_links(cls, resource_data):
        pass

    @classmethod
    def get_data_resource_info(cls):
        pass


    @classmethod
    def find_by_template(cls, template, limit, offset):
        res = RDBService.find_by_template("UserInfo", "Address", template, limit, offset)
        return res

    @classmethod
    def create(cls, create_data):
        res = RDBService.create("UserInfo", "Address", create_data)
        return res

    @classmethod
    def find_linked_data(cls, target, template, key):
        res = RDBService.find_linked_data("UserInfo", "Address", "User", target, template, key)
        return res

    # @classmethod
    # def get_user_and_address(cls, template):

    #     wc, args = RDBService.get_where_clause_args(template)
    #     sql = "select * from aaaaF21.users left join aaaaF21.addresses on " + \
    #             "aaaaF21.primary_address_id = aaaaF21.addresses.id"

    #     res = RDBService.run_sql(sql, args, fetch=True)
    #     return res

