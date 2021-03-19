from flask import Flask, abort, request
from peewee import IntegerField, CharField, TextField, Model, SqliteDatabase
from datetime import datetime


db = SqliteDatabase("pub_keys.db")


class BaseModel(Model):
    class Meta:
        database = db


class Pubkeys(BaseModel):
    telegram_id = IntegerField(primary_key=True)
    pub_key = TextField()
    last_date = CharField()


db.create_tables([Pubkeys])

app = Flask(__name__)


@app.route("/<int:telegram_id>/date", methods=["GET"])
def get_last_date(telegram_id):
    for entry in Pubkeys.select():
        if entry.telegram_id == telegram_id:
            return entry.last_date, 200
    abort(404)


@app.route("/<int:telegram_id>", methods=["GET"])
def check(telegram_id):
    for entry in Pubkeys.select():
        if entry.telegram_id == telegram_id:
            return entry.pub_key, 200
    abort(404)


@app.route("/update/<int:telegram_id>", methods=["POST"])
def update(telegram_id):

    for entry in Pubkeys.select():
        if entry.telegram_id == telegram_id:
            entry.pub_key = request.form["pub_key"]
            entry.last_date = str(datetime.utcnow().timestamp())
            return "updated", 200

    pubkey = Pubkeys(
        telegram_id=telegram_id,
        pub_key=request.form["pub_key"],
        last_date=datetime.utcnow().timestamp(),
    )
    pubkey.save(force_insert=True)

    return "updated", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
