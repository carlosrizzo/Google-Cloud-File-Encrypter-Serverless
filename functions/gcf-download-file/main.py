from google.cloud import datastore
from google.cloud import storage
from google.cloud.storage import Blob
from datetime import datetime, timedelta
from flask import Flask, Response

import os
import uuid
import slugify
import hashlib

# Get env vars
BUCKET_NAME = os.environ.get('BUCKET_NAME', None)
DS_KIND = os.environ.get('DS_KIND', None)
# Check env vars
if not BUCKET_NAME or not DS_KIND:
    print('Export env vars: BUCKET_NAME and DS_KIND')
    raise # Circuit break

def execute(request):
     # Check Payload
    if not request.form or not 'external_ref' in request.form:
        return ('Bad request: External Ref is required', 400)
    if not request.form or not 'external_key' in request.form:
        return ('Bad request: External Key is required', 400)
    if not request.form or not 'file_hash' in request.form:
        return ('Bad request: Hash File required', 400)
           
    # Get external ref
    external_ref = request.form.get('external_ref')
    # Get external key
    external_key = request.form.get('external_key')
    # Get hash File
    file_hash = request.form.get('file_hash')

    # External ref uuid name
    external_ref_uuid_name = 'extref=%s%s' % (slugify.slugify(external_ref), external_key)
    # Generate UUID external ref
    external_ref_uuid = uuid.uuid5(uuid.NAMESPACE_X500, external_ref_uuid_name)
    # Get external ref uuid str
    external_ref_uuid_str = str(uuid.uuid5(uuid.NAMESPACE_X500, external_ref_uuid_name))
    # Get unique key external ref
    external_ref_key = hashlib.md5(external_ref_uuid.bytes).hexdigest()

    try: # Get bucket
        client_storage = storage.Client()
        bucket = client_storage.get_bucket(BUCKET_NAME)
    except Exception as e: # Any exception
        return (u'Error: %s' % e, 500)
    
    # Bucket file uuid name
    encryption_key_name = 'extrefkey=%s' % external_ref_key
    # Generate UUID Bucket file
    encryption_key_uuid = uuid.uuid5(uuid.NAMESPACE_X500, encryption_key_name)
    # Generate encryption key Bucket file
    encryption_key = hashlib.md5(encryption_key_uuid.bytes).hexdigest()

    try: # Get bucket
        client_datastore = datastore.Client()
        item_key = client_datastore.key(DS_KIND, "%s-%s" % (external_ref_key, file_hash))
        item = client_datastore.get(item_key)
    except Exception as e: # Any exception
        return (u'Error: %s' % e, 500)
    
    # Not found response
    response = 'Item not found'
    mimetype = 'text/plain'

    # Found item
    if item:
        # Get path file
        path_file = item['file_path']
        # Create encrypt Blob
        blob = Blob(name=path_file, bucket=bucket, encryption_key=encryption_key)
        response = blob.download_as_string()
        mimetype = item['file_content_type']

    # Response
    return Response(response, mimetype=mimetype)