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
from gevent import monkey; monkey.patch_all()

static_folder = pathlib.Path(__file__).resolve().parent.parent / 'public'
app = Flask(__name__, static_folder = str(static_folder), static_url_path='')

app.secret_key = 'tonymoris'

_config = {
    'db_host':       'localhost',
    'db_port':       3306,
    'db_user':       "isucon",
    'db_password':   "isucon",
    'isutar_origin': "http://localhost:5001",
    'isupam_origin': "http://localhost:5050"),
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
    print(dbh())

main()
