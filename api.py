from flask import Flask, redirect, jsonify, request
from hashlib import md5
import re
import sqlite3
from waitress import serve

app = Flask("url_shortener")

DOMAIN_NAME = "http://femto.me:5000/"

@app.route("/shorten", methods=["POST"])
def shorten():
    connection = sqlite3.connect("short.db")
    cursor = connection.cursor()
    payload = request.json
    if "url" not in payload:
        data = { "Message": "Missing URL Parameter", "shortened_url":"" }
        return jsonify(data), 400

    regex_url = ("((http|https)://)(www.)?" +
                 "[a-zA-Z0-9@:%._\\+~#?&//=]" +
                 "{2,256}\\.[a-z]" +
                 "{2,6}\\b([-a-zA-Z0-9@:%" +
                 "._\\+~#?&//=]*)")
    regex_comp = re.compile(regex_url)
    if not (re.search(regex_comp, payload["url"])):
        data = { "Message": "Invalid URL", "shortened_url":"" }
        return jsonify(data), 400
        
    hash_ = md5()
    hash_.update(payload["url"].encode())
    # limiting to 6 chars. Less the limit more the chances of collission
    digest = hash_.hexdigest()[:6]
    cursor.execute(
        "SELECT COUNT(hash) FROM short WHERE hash = ?", (digest,))
    check_present = cursor.fetchall()[0][0]
    url = DOMAIN_NAME + digest
    if int(check_present) == 0:
        cursor.execute("INSERT INTO short VALUES(?,?)",
                       (digest, payload["url"]))
        connection.commit()
        data = { "Message": "Success", "shortened_url":url }
        return jsonify(data)
    else:
        data = { "Message": "Already exists", "shortened_url":url }
        return jsonify(data)


@app.route("/<hash_>")
def redirect_(hash_):
    connection = sqlite3.connect("short.db")
    cursor = connection.cursor()
    cursor.execute(
        "SELECT COUNT(hash) FROM short WHERE hash = ?", (hash_,))
    check_present = cursor.fetchall()[0][0]
    if int(check_present) == 0:
        return "URL Not Found", 404
    cursor.execute("SELECT full_url FROM short WHERE hash = ?", (hash_,))
    return redirect(cursor.fetchall()[0][0])


if __name__ == "__main__":
    connection = sqlite3.connect("short.db")
    cursor = connection.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS short(hash TEXT, full_url TEXT)")
    connection.commit()
    #app.run(debug=True)
    serve(app, host='0.0.0.0',port=5000,url_scheme='http')
