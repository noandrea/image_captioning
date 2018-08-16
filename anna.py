#!/usr/bin/env python3
# version 0.2.1-DEV

import os
import sys
import logging
import json
from collections import namedtuple
import sqlite3
from contextlib import contextmanager
import argparse
import threading
from queue import Queue
import time

# flask
from flask import Flask, jsonify, abort, flash, request, redirect, render_template
from flask_socketio import SocketIO
from werkzeug.utils import secure_filename

# hashing
import nacl
from nacl.hash import blake2b

# ai
import tensorflow as tf
from config import Config
from model import CaptionGenerator
from dataset import prepare_test_data


# also log to stdout because docker
root = logging.getLogger()
root.setLevel(logging.INFO)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

ch.setFormatter(formatter)
root.addHandler(ch)


def fdate(dt):
    """format a date"""
    return dt.strftime('%d/%m/%Y – %H:%M:%S')


def authorize(request_key):
    """validate a request key, raise an exception when authorization fails"""
    global settings
    return True
    if request_key == settings.access_key:
        return True
    err = UnauthorizedException(f"Unauthorized access for key '{request_key}'")
    logging.error(err.message)
    raise err


class UnauthorizedException(Exception):
    """Raised when a request is unauthorized
    Attributes:
        message -- what caused the error
    """

    def __init__(self, message):
        self.message = message


class UnsupportedStateException(Exception):
    """Raised when a state change is requested for a state that is not supported
    Attributes:
        message -- what caused the error
    """

    def __init__(self, state):
        self.message = f"Unsupported state {state}"

#   ______   ______
#  |_   _ `.|_   _ \
#    | | `. \ | |_) |
#    | |  | | |  __'.
#   _| |_.' /_| |__) |
#  |______.'|_______/
#


class DB(object):
    def __init__(self, db_path):
        logging.info(f"using database at {db_path}")
        do_init = False if os.path.exists(db_path) else True
        self.db_path = db_path
        self.init_db(do_init)

    def init_db(self, do_init):
        if not do_init:
            logging.info("db exists")
            return
        logging.info("initializing database")
        with open("initdb.d/init.sql") as fp:
            sql = fp.read()
            self.execute(sql)

    @contextmanager
    def getcursor(self):
        """retrieve a cursor from the database"""
        try:
            conn = sqlite3.connect(self.db_path)

            def dict_factory(cursor, row):
                d = {}
                for idx, col in enumerate(cursor.description):
                    d[col[0]] = row[idx]
                return d
            
            conn.row_factory = dict_factory
            yield conn.cursor()
        finally:
            conn.commit()
            conn.close()

    def execute(self, query, params=()):
        """run a database update
        :param query: the query string
        :param params: the query parameteres
        """
        with self.getcursor() as c:
            try:
                c.execute(query, params)
            except Exception as e:
                logging.error(e)

    def select(self, query, params=(), many=False):
        """
        run a database update
        :param query: the query string
        :param params: the query parameteres
        :param many: if True returns a list of rows, otherwise just on row
        """
        with self.getcursor() as c:
            try:
                # Insert a row of data
                c.execute(query, params)
                if many:
                    return c.fetchall()
                else:
                    return c.fetchone()
            except Exception as e:
                logging.error(e)


#        _       _____
#       / \     |_   _|
#      / _ \      | |
#     / ___ \     | |
#   _/ /   \ \_  _| |_
#  |____| |____||_____|
#

class AI(object):
    def __init__(self, model_path):
        """
        Initialize the AI
        :param model_path: path to the trained model file, (eg: models/289999.npy)
        """
        self.config = Config()
        self.config.phase = 'test'
        self.config.beam_size = 3
        self.model_path = model_path

    def load(self):
        self.sess = tf.Session()
        # testing phase
        self.model = CaptionGenerator(self.config)
        # TODO:load the right model
        self.model.load(self.sess, self.model_path)
        tf.get_default_graph().finalize()

    def image_caption(self, image_path):
        # this is what it should do
        data, vocabulary = prepare_test_data(self.config, image_path=image_path)
        caption, score = self.model.caption(self.sess, data, vocabulary)
        print(f"caption '{caption}' wiht score {score} for image {image_path} ")
        return caption, score


#    ______     ___      ______  ___  ____   ________  _________  _    ___
#  .' ____ \  .'   `.  .' ___  ||_  ||_  _| |_   __  ||  _   _  |(_) .'   `.
#  | (___ \_|/  .-.  \/ .'   \_|  | |_/ /     | |_ \_||_/ | | \_|__ /  .-.  \
#   _.____`. | |   | || |         |  __'.     |  _| _     | |   [  || |   | |
#  | \____) |\  `-'  /\ `.___.'\ _| |  \ \_  _| |__/ |   _| |_   | |\  `-'  /
#   \______.' `.___.'  `.____ .'|____||____||________|  |_____| [___]`.___.'
#


socketio = SocketIO()
app = Flask(__name__)
# root.addHandler(app.logger)


def rpl(tx_hash, success, msg):
    return {
        "tx_hash": tx_hash,
        "success": success,
        "msg": msg
    }


@socketio.on('say_hy')
def handle_was_beer_scanned():
    """check if the trasaction was scanned"""
    return {"msg": "hi beautiful"}


@socketio.on('describe')
def handle_describe(access_key, image_data):
    """
    refund an account from the bar account
    :param access_key: the shared secret to authenticate the pos
    :param image_data: the image to caption
    """
    # run the refund
    try:
        # check authorization
        authorize(access_key)

        # return rpl(None, True, state)
        pass

    except UnauthorizedException as e:
        pass
    except Exception as e:
        logging.error(f"refund error {e}")
        pass


#   _______     ________   ______   _________
#  |_   __ \   |_   __  |.' ____ \ |  _   _  |
#    | |__) |    | |_ \_|| (___ \_||_/ | | \_|
#    |  __ /     |  _| _  _.____`.     | |
#   _| |  \ \_  _| |__/ || \____) |   _| |_
#  |____| |___||________| \______.'  |_____|
#

@app.after_request
def after_request(response):
    """enable CORS"""
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    return response


@app.route('/rest/name/<public_key>')
def rest_get_name(public_key):
    """reverse mapping for the account name"""
    global cash_register
    name = cash_register.get_wallet_name(public_key)
    if name is None:
        abort(404)
    return jsonify({"name": name})


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ["jpeg", "jpg", "png"]


@app.route('/', methods=['GET'])
def home():
    rows = app.config['DB'].select("select * from captions order by created_at desc", many=True)
    lines = [(r['caption'], r['created_at']) for r in rows]
    # TODO: add dates to the lines
    return render_template('index.html', rows=lines)


@app.route('/upload', methods=['POST'])
def upload_file():
    # check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        # generate the caption
        app.config['UPLOAD_QUEUE'].put(filepath)
        return redirect("/")

    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''


#   ____      ____   ___   _______     ___  ____   ________  _______
#  |_  _|    |_  _|.'   `.|_   __ \   |_  ||_  _| |_   __  ||_   __ \
#    \ \  /\  / / /  .-.  \ | |__) |    | |_/ /     | |_ \_|  | |__) |
#     \ \/  \/ /  | |   | | |  __ /     |  __'.     |  _| _   |  __ /
#      \  /\  /   \  `-'  /_| |  \ \_  _| |  \ \_  _| |__/ | _| |  \ \_
#       \/  \/     `.___.'|____| |___||____||____||________||____| |___|
#


class ProcessWorker(object):
    """
    Poll the bar account to look for transactions
    """

    def __init__(self,  db, ai, orders_queue, interval=15):
        """ Constructor
        :type db: PG
        :param db: object for database connection
        :type epoch: EpochClient
        :param epoch: client to interatct with the chain
        :type bar_wallet: KeyPair
        :param bar_wallet: contains the bar wallet
        :type orders_queue: Queue
        :param orders_queue: orders chain queue
        :type interval: int
        :param interval: Check interval, in seconds
        """
        self.interval = interval
        self.db = db
        self.ai = ai
        self.orders_queue = orders_queue

    def start(self):
        """start the polling """
        # start the polling
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()

    def run(self):
        # sleep at the beginning
        time.sleep(self.interval)
        while True:
            imagpath = self.orders_queue.get()
            logging.info(f"process image {imagpath}")
            with open(imagpath, 'rb') as fp:
                # calculate the digest
                hexdigest = blake2b(data=fp.read(), digest_size=64, encoder=nacl.encoding.HexEncoder).decode("utf-8")
                row = self.db.select("select caption from captions where hexdigest = ?", (hexdigest,))
                if row is not None:
                    # image exists
                    caption = row.get('caption')
                    logging.info(f"image {imagpath}, caption {caption}, already processed ")
                else:
                    # generate caption
                    caption, p = self.ai.image_caption(imagpath)
                    # this will als
                    self.db.execute("insert into captions(hexdigest,file_name, caption,probability) values (?,?,?,?)",
                                    (hexdigest, os.path.basename(imagpath), caption, p))
                    logging.info(f"image {imagpath}, caption {caption}, {p}")
                # emit("describe", {"digest": hexdigest, "caption": caption})


#     ______  ____    ____  ______     ______
#   .' ___  ||_   \  /   _||_   _ `. .' ____ \
#  / .'   \_|  |   \/   |    | | `. \| (___ \_|
#  | |         | |\  /| |    | |  | | _.____`.
#  \ `.___.'\ _| |_\/_| |_  _| |_.' /| \____) |
#   `.____ .'|_____||_____||______.'  \______.'
#

def cmd_caption(args=None):
    with open(args.config, 'r') as fp:
        print(f"Load settigns from {args.config}")
        settings = json.load(fp, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
        print(f"Using model at {settings.captions_model_path}")
        image_ai = AI(settings.captions_model_path)
        print(f"Caption:")
        caption, _ = image_ai.xxx_imag(args.image_path)
        print(caption)


def cmd_start(args=None):
    global settings
    if args.config is not None:
        # load the parameters from json
        # and set them as env var
        with open(args.config, 'r') as fp:
            settings = json.load(fp, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))

    # uploaded images names will be set in this queue
    uploads_queue = Queue()

    app.config['UPLOAD_FOLDER'] = settings.upload_path
    app.config['SECRET_KEY'] = settings.flask_secret
    app.config['UPLOAD_QUEUE'] = uploads_queue
    app.config['DB'] = DB(settings.db_path)

    image_ai = AI(settings.captions_model_path)
    if not args.no_ai:
        image_ai.load()

    global process_worker
    process_worker = ProcessWorker(
        app.config['DB'],
        image_ai,
        uploads_queue,
        interval=args.polling_interval)

    # background worker
    process_worker.start()

    # start the app
    logging.info('start socket.io')
    socketio.init_app(app)
    socketio.run(app, host="0.0.0.0", max_size=10000, debug=False)


if __name__ == '__main__':
    cmds = [
        {
            'name': 'start',
            'help': 'start the beer aepp-pos-middelware',
            'opts': [
                {
                    'names': ['-c', '--config'],
                    'help':'use the configuration file instead of environment variables',
                    'default':None
                },
                {
                    'names': ['-n', '--no-ai'],
                    'help':'only start the socketio service not the chain polling worker',
                    'action': 'store_true',
                    'default': False
                },
                {
                    'names': ['-p', '--polling-interval'],
                    'help':'polling interval in seconds',
                    'default': 15
                }
            ]
        }, {
            'name': 'caption',
            'help': 'caption an image',
            'opts': [
                {
                    'names': ['-c', '--config'],
                    'help':'select the configuration file',
                    'required': True,
                },
                {
                    'names': ['-i', '--image-path'],
                    'help':'the path of the image to caption',
                    'required': True
                }
            ]
        }
    ]
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    subparsers.required = True
    subparsers.dest = 'command'
    # register all the commands
    for c in cmds:
        subp = subparsers.add_parser(c['name'], help=c['help'])
        # add the sub arguments
        for sa in c.get('opts', []):
            subp.add_argument(*sa['names'],
                              help=sa['help'],
                              action=sa.get('action'),
                              default=sa.get('default'))

    # parse the arguments
    args = parser.parse_args()
    # call the command with our args
    ret = getattr(sys.modules[__name__], 'cmd_{0}'.format(
        args.command.replace('-', '_')))(args)
