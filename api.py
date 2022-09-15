from flask import Flask, redirect, request
from hashlib import md5
import re
import sqlite3

app = Flask("url_shortener")


@app.route("/shorten", methods=["POST"])
def shorten():
    connection = sqlite3.connect("short.db")
    cursor = connection.cursor()
    payload = request.json
    if "url" not in payload:
        return "Missing URL Parameter", 400

    regex_url = ("((http|https)://)(www.)?" +
                 "[a-zA-Z0-9@:%._\\+~#?&//=]" +
                 "{2,256}\\.[a-z]" +
                 "{2,6}\\b([-a-zA-Z0-9@:%" +
                 "._\\+~#?&//=]*)")
    regex_comp = re.compile(regex_url)
    if not (re.search(regex_comp, payload["url"])):
        return "Invalid URL", 400
    hash_ = md5()
    hash_.update(payload["url"].encode())
    # limiting to 6 chars. Less the limit more the chances of collission
    digest = hash_.hexdigest()[:6]
    cursor.execute(
        "SELECT COUNT(hash) FROM short WHERE hash = ?", (digest,))
    check_present = cursor.fetchall()[0][0]

    if int(check_present) == 0:
        cursor.execute("INSERT INTO short VALUES(?,?)",
                       (digest, payload["url"]))
        connection.commit()
        return f"Shortened: /{digest}\n"
    else:
        return f"Already exists: /{digest}\n"


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
    app.run(debug=True)
