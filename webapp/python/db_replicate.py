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

def main():
    print("replicate")

    db = MySQLdb.connect(**{
        "host": "localhost",
        "port": 3306,
        "user": "isucon",
        "passwd": "isucon",
        "db": 'isuda',
        "charset": 'utf8mb4',
        "cursorclass": MySQLdb.cursors.DictCursor,
        "autocommit": True,
    })

    cursor = db.cursor()
    cursor.execute("SET SESSION sql_mode='TRADITIONAL,NO_AUTO_VALUE_ON_ZERO,ONLY_FULL_GROUP_BY'")
    cursor.execute('SET NAMES utf8mb4')

    r = redis.Redis(unix_socket_path="/var/run/redis/redis.sock")

    cursor.execute("SELECT * FROM user")
    for u in cursor.fetchall():
        r.hset("users:" + str(u["id"]), "name", u["name"])
        r.hset("users:" + str(u["id"]), "password", u["password"])
        r.hset("users:" + str(u["id"]), "salt", u["salt"])
        r.hset("users:" + str(u["id"]), "created_at", u["created_at"])
    
    r.zremrangebyscore("sorted_entry_ids:keyword_size", "-inf", "+inf")
    r.zremrangebyscore("sorted_entry_ids:updated_at", "-inf", "+inf")
    cursor.execute("SELECT *, UNIX_TIMESTAMP(updated_at) AS updated_at2 FROM entry")
    for e in cursor.fetchall():
        r.hset("entries:" + str(e["id"]), "user_id", e["author_id"])
        r.hset("entries:" + str(e["id"]), "keyword", e["keyword"])
        r.hset("entries:" + str(e["id"]), "description", e["description"])
        r.hset("entries:" + str(e["id"]), "created_at", e["created_at"])
        r.hset("entries:" + str(e["id"]), "updated_at", e["updated_at"])
        r.hset("keywords:" + e["keyword"], "id", str(e["id"]))
        r.zadd("sorted_entry_ids:keyword_size", str(e["id"]), len(e["keyword"]))
        r.zadd("sorted_entry_ids:updated_at", str(e["id"]), e["updated_at2"])

main()
