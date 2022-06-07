from marshmallow import fields, Schema


class UserSchema(Schema):
    name = fields.String()
    email = fields.String()
    password = fields.String()
    phone = fields.String()


class TableIDSchema(Schema):
    id = fields.Integer()


class UserPrototype(Schema):
    users = fields.List(fields.Nested(UserSchema), required=True, metadata={"desc": "users info"})


class TaskManagerSchema(Schema):
    amount = fields.Integer()
    description = fields.String()
    creator_id = fields.Integer()
