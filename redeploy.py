import tutum
import websocket
import base64
import os
import sys
import json
import time

service_uuid = os.environ.get('TUTUM_SERVICE')
username = os.environ.get('TUTUM_USER')
apikey = os.environ.get('TUTUM_APIKEY')
tutum_auth = os.environ.get('TUTUM_AUTH')
grace_period = float(os.environ.get('TUTUM_GRACE_PERIOD') or 0)

if (not (username and apikey) and not tutum_auth):
    raise EnvironmentError('You should either give full access to this service, or provide TUTUM_USER and TUTUM_APIKEY as env variables')
if (not service_uuid):
    raise EnvironmentError('You must set the TUTUM_SERVICE env var.')

service_full = '/api/v1/service/'+service_uuid+'/'
nginx_config_dir = '/etc/nginx/conf.d/'

errors = []
containers = []

def redeploy_next():
    if (len(containers) == 0):
        if len(errors):
            sys.exit(str(len(errors)) + " errors have happened.")

        print "All is well."
        sys.exit()

    container = containers.pop()
    print "Redeploying " + container.name
    try:
        container.redeploy()
    except Exception as error:
        print "Unexpected error:" + str(error)
        print "Trying to continue"
        errors.append(error)
        redeploy_next()


def is_new_container(container):
    for c in containers:
        if c.resource_uri == container['resource_uri']:
            return False
    return True

def on_message(ws, message):
    message = json.loads(message)
    if message['type'] == 'container' and message['state'] == 'Running':
        if (is_new_container(message)):
            if (grace_period):
                print "Waiting " + str(grace_period) + " seconds (grace period)"
                time.sleep(grace_period)
            redeploy_next()

def on_error(ws, error):
    sys.exit(error)

def on_close(ws):
    print "Stream closed."

def on_open(ws):
    print "Stream opened."
    redeploy_next()

if (tutum_auth):
    header = "Authorization: " + tutum_auth
else:
    header = "Authorization: Basic %s" % base64.b64encode("%s:%s" % (username, apikey))


ws = websocket.WebSocketApp('wss://stream.tutum.co/v1/events',
                            header=[header],
                            on_message=on_message,
                            on_error=on_error,
                            on_close=on_close,
                            on_open=on_open
)

existing_containers = tutum.Container.list(service=service_full)
for container in existing_containers:
    if container.state in ['Running', 'Starting']:
        containers.append(container)

print "Found " + str(len(containers)) + " containers"


ws.run_forever()