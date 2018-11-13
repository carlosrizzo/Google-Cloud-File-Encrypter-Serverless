from google.cloud import datastore
from google.cloud import storage
from google.cloud.storage import Blob
from flask import Flask, Response

import google
import os
import uuid
import slugify
import hashlib
import json

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
    if not request.files or not 'file' in request.files:
        return ('Bad request: File is required', 400)
           
    # Get external ref
    external_ref = request.form.get('external_ref')
    # Get external key
    external_key = request.form.get('external_key')
    
    # External ref uuid name
    external_ref_uuid_name = 'extref=%s%s' % (slugify.slugify(external_ref), external_key)
    # Generate UUID external ref
    external_ref_uuid = uuid.uuid5(uuid.NAMESPACE_X500, external_ref_uuid_name)
    # Get external ref uuid str
    external_ref_uuid_str = str(uuid.uuid5(uuid.NAMESPACE_X500, external_ref_uuid_name))
    # Get unique key external ref
    external_ref_key = hashlib.md5(external_ref_uuid.bytes).hexdigest()

    try: # Get/Create bucket
        client_storage = storage.Client()
        bucket = client_storage.create_bucket(BUCKET_NAME)
    except google.api_core.exceptions.Conflict: # Bucket already exists
        bucket = client_storage.get_bucket(BUCKET_NAME)
    except Exception as e: # Any exception
        return (u'Error: %s' % e, 500) 
    
    # Bucket file uuid name
    encryption_key_name = 'extrefkey=%s' % external_ref_key
    # Generate UUID Bucket file
    encryption_key_uuid = uuid.uuid5(uuid.NAMESPACE_X500, encryption_key_name)
    # Generate encryption key Bucket file
    encryption_key = hashlib.md5(encryption_key_uuid.bytes).hexdigest()

    try: # Get file
        file = request.files.get('file')
        # Generate path file
        path_file = "%s/%s/%s" % (str(external_ref_uuid), str(encryption_key_uuid), file.filename)
        # Create encripty Blob
        blob = Blob(name=path_file, bucket=bucket, encryption_key=encryption_key)
    except Exception as e:
        return (u'Error: %s' % e, 500)
    
    try: # Read and upload file into bucket
        buff = file.read()
        blob.upload_from_string(buff, content_type=file.content_type)
    except Exception as e: # Any exception
        return (e, 500)

    # Generate File hash
    file_hash = hashlib.md5(buff).hexdigest()

    try: # Create entity
        client_datastore = datastore.Client()
        # Generate Datastore Key
        item_key = client_datastore.key(DS_KIND, "%s-%s" % (external_ref_key, file_hash))
        # Entity
        item = datastore.Entity(key=item_key,) # Insert user key
        item['external_ref_key'] = external_ref_key
        item['file_hash'] = file_hash
        item['file_path'] = path_file
        item['file_content_type'] = file.content_type
        client_datastore.put(item) 
    except Exception as e: # Any exception
        return (u'Error: %s' % e, 500)

    # Data return
    data = json.dumps({'filename': file.filename,'hash' : file_hash})
    # Response
    return Response(data, mimetype='application/json')