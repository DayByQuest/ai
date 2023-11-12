# dependencies.py
from queue import Queue

queue_key_creation = Queue()
queue_key_judgment = Queue()
queue_file_creation = Queue()
queue_file_judgment = Queue()

def get_queue_key_creation():
    return queue_key_creation
def get_queue_key_judgment():
    return queue_key_judgment
def get_queue_file_creation():
    return queue_file_creation
def get_queue_file_judgment():
    return queue_file_judgment
