# [START functions_helloworld_storage]
from google.cloud import storage
def hello_gcs(event, context):
    
    """Background Cloud Function to be triggered by Cloud Storage.
       This generic function logs relevant data when a file is changed.

    Args:
        event (dict):  The dictionary with data specific to this type of event.
                       The `data` field contains a description of the event in
                       the Cloud Storage `object` format described here:
                       https://cloud.google.com/storage/docs/json_api/v1/objects#resource
        context (google.cloud.functions.Context): Metadata of triggering event.
    Returns:
        None; the output is written to Stackdriver Logging
    """
    print('Event ID: {}'.format(context.event_id))
    print('Event type: {}'.format(context.event_type))
    print('Bucket: {}'.format(event['bucket']))
    print('File: {}'.format(event['name']))
    print('Metageneration: {}'.format(event['metageneration']))
    print('Created: {}'.format(event['timeCreated']))
    print('Updated: {}'.format(event['updated']))
    print(event)
    print(context)
    
# [END functions_helloworld_storage]

# Must export GOOGLE_APPLICATION_CREDENTIALS
gcs_client = storage.Client()
result = gcs_client.list_buckets()
for b in result:
    print(b)
    print(type(b))

from utils import unzip

unzip.unzip("20211230.zip")
