#-*- coding:utf-8 -*-

import json
from kafka import KafkaProducer
from config import *
import logging
#logging.basicConfig(level=logging.DEBUG)

class Kafkas(object):

	def __init__(self):
		pass

	def push_msg(self, msg='hello'):
		try:
			producer = KafkaProducer(bootstrap_servers="%s:%s" % (kafka_host, kafka_port), value_serializer=lambda v: json.dumps(v).encode('utf-8'))
			future = producer.send(kafka_topic, msg)
			result = future.get(timeout=5)
		except Exception,e:
			print("KafkaAdd.py msg_add Error: %s" % (str(e)))

if __name__ == '__main__':
	obj = Kafkas()
	obj.push_msg()