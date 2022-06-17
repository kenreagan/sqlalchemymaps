from marshmallow import fields, Schema


class UserSchema(Schema):
    name = fields.String()
    email = fields.String()
    password = fields.String()
    phone = fields.String()


class TableIDSchema(Schema):
    id = fields.Integer()


class LoginSchema(Schema):
    email = fields.String()
    password = fields.String()


class UserPrototype(Schema):
    users = fields.List(fields.Nested(UserSchema), required=True, metadata={"desc": "users info"})


class TaskManagerSchema(Schema):
    title = fields.String()
    Amount = fields.Integer()
    description = fields.String()
