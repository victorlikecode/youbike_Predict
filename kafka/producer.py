import sys
import os

from confluent_kafka import Producer

class producer(threading.Thread):
    topic = None
    p = None
    # Consumer configuration
    # See https://github.com/edenhill/librdkafka/blob/master/CONFIGURATION.md
    conf = {
        'bootstrap.servers': os.environ['CLOUDKARAFKA_BROKERS'],
        'session.timeout.ms': 6000,
        'default.topic.config': {'auto.offset.reset': 'smallest'},
        'security.protocol': 'SASL_SSL',
	'sasl.mechanisms': 'SCRAM-SHA-256',
        'sasl.username': os.environ['CLOUDKARAFKA_USERNAME'],
        'sasl.password': os.environ['CLOUDKARAFKA_PASSWORD']
    }
    def __init__(self,topic):
        self.topic = os.environ['CLOUDKARAFKA_TOPIC_PREFIX']+topic
        self.p = Producer(**conf)
    def delivery_callback(err, msg):
        if err:
            sys.stderr.write('%% Message failed delivery: %s\n' % err)
        else:
            sys.stderr.write('%% Message delivered to %s [%d]\n' %
                             (msg.topic(), msg.partition()))
    

    def run(self):
        for line in sys.stdin:
            try:
                self.p.produce(topic, line.rstrip(), callback=delivery_callback)
            except BufferError as e:
                sys.stderr.write('%% Local producer queue is full (%d messages awaiting delivery): try again\n' %
                             len(self.p))
            self.p.poll(0)
        sys.stderr.write('%% Waiting for %d deliveries\n' % len(self.p))
        self.p.flush()
