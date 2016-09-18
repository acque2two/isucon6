from flask import Flask, request, jsonify, abort
import MySQLdb.cursors
import os
import html
import urllib
from gevent import monkey; monkey.patch_all()

app = Flask(__name__)

def get_isutar_db():
    if hasattr(request, "isutar_db"):
        return request.isutar_db
    else:
        request.isutar_db = MySQLdb.connect(**{
            'host': 'localhost',
            'port': 3306,
            'user': 'isucon',
            'passwd': 'isucon',
            'db': 'isutar',
            'charset': 'utf8mb4',
            'cursorclass': MySQLdb.cursors.DictCursor,
            'autocommit': True,
        })
        cursor = request.isutar_db.cursor()
        cursor.execute("SET SESSION sql_mode='TRADITIONAL,NO_AUTO_VALUE_ON_ZERO,ONLY_FULL_GROUP_BY'")
        cursor.execute('SET NAMES utf8mb4')

        return request.isutar_db

@app.teardown_request
def close_db(exception=None):
    if hasattr(request, 'isutar_db'):
        request.isutar_db.close()

@app.route("/initialize")
def get_initialize():
    cursor = get_isutar_db().cursor()
    cursor.execute('TRUNCATE star')

    return jsonify(status = 'ok')

@app.route("/stars")
def get_stars():
    cursor = get_isutar_db().cursor()
    cursor.execute('SELECT * FROM star WHERE keyword = %s', (request.args['keyword'], ))

    return jsonify(stars = cursor.fetchall())

@app.route("/stars", methods=['POST'])
def post_stars():
    keyword = request.args.get('keyword', "")
    if keyword == None or keyword == "":
        keyword = request.form['keyword']

    origin = os.environ.get('ISUDA_ORIGIN', 'http://localhost:5000')
    url = "%s/keyword/%s" % (origin, urllib.parse.quote(keyword))
    try:
        urllib.request.urlopen(url)
    except urllib.error.HTTPError as e:
        if e.status == 404:
            abort(404)
        else:
            raise

    cursor = get_isutar_db().cursor()
    cursor.execute(
"""
INSERT INTO star (keyword, user_name, created_at)
VALUES (%s, %s, NOW())
"""
        ,
        (keyword, request.args.get('user', '', ))
    )

    user = request.args.get('user', "")
    if user == None or user == "":
        user = request.form['user']

    cursor.execute(
"""
INSERT INTO star (keyword, user_name, created_at)
VALUES (%s, %s, NOW())
"""
        ,
        (keyword, user)
    )

    return jsonify(result = 'ok')

if __name__ == "__main__":
    app.run()
