import json
import time
import sys
from flask import Blueprint,request
from flask import Flask
import logging
from db_interface import insert_to_signals_database
app = Flask(__name__)
#@app.route('/dsky',methods=['GET','POST'])
@app.post('/')
def recv_data():
    try:
        para = request.values.get('data')
        insert_to_signals_database(para)
        data = json.loads(para)
        print(data['time'])
        #print(data)
    except:
        ExecInfo = sys.exc_info()
        logging.error(ExecInfo[1])
        #raise Exception(ExecInfo[1])
    return "Done"