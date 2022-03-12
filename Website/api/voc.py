from flask import templating, session, escape, request, jsonify
from apiflask import APIBlueprint
from db import userdb, requestdb, taskdb

voc = APIBlueprint("voc", __name__)


@voc.get("/get_voc/<string:name>/<string:lang>")
def get_voc(name, lang):
    trans = taskdb.GetTranslation(name, lang)
    if trans is None:
        return "Error: Voc does not exist", 404
    return jsonify(trans)
