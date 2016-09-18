import redis
from flask import Flask, request, jsonify, abort, render_template, redirect, session, url_for
import MySQLdb.cursors
import hashlib
import html
import json
import math
import os
import pathlib
import random
import re
import string
import urllib

_config = {
    "db_host":       'localhost',
    "db_port":       3306,
    "db_user":       "isucon",
    "db_password":   "isucon",
    "isutar_origin": "http://localhost:5001",
    "isupam_origin": "http://localhost:5050",
}

def config(key):
    if key in _config:
        return _config[key]
    else:
        raise "config value of %s undefined" % key

def dbh():
    if hasattr(request, 'db'):
        return request.db
    else:
        request.db = MySQLdb.connect(**{
            'host': "localhost",
            'port': 3306,
            'user': "isucon",
            'passwd': "isucon",
            'db': 'isuda',
            'charset': 'utf8mb4',
            'cursorclass': MySQLdb.cursors.DictCursor,
            'autocommit': True,
        })
        cur = request.db.cursor()
        cur.execute("SET SESSION sql_mode='TRADITIONAL,NO_AUTO_VALUE_ON_ZERO,ONLY_FULL_GROUP_BY'")
        cur.execute('SET NAMES utf8mb4')
        return request.db

def main():
    print("replicate")

    r = redis.Redis(unix_socket_path="/var/run/redis/redis.sock")
    cursor = dbh().cursor()

    cursor.execute("SELECT * FROM user")
    for u in cursor.fetchall():
        r.hset("users:" + u["id"], "name", u["name"])
        r.hset("users:" + u["id"], "password", u["password"])
        r.hset("users:" + u["id"], "salt", u["salt"])
        r.hset("users:" + u["id"], "created_at", u["created_at"])

    cursor.execute("SELECT * FROM entry")
    for e in cursor.fetchall():
        r.hset("entries:" + e["id"], "user_id", e["author_id"])
        r.hset("entries:" + e["id"], "keyword", e["keyword"])
        r.hset("entries:" + e["id"], "description", e["description"])
        r.hset("entries:" + e["id"], "created_at", e["created_at"])
        r.hset("entries:" + e["id"], "updated_at", e["updated_at"])

main()
