from __future__ import print_function

import re
import boto3
import urllib
from botocore.vendored import requests

#nnum = re.compile('N[1-9]((\d{0,4})|(\d{0,3}[A-HJ-NP-Z])|(\d{0,2}[A-HJ-NP-Z]{2}))')

print('Loading function')

rek = boto3.client('rekognition')

# A regex to extract aircraft model number from the returned HTML
modelre = re.compile('<span id=\"content_Label7\" class=\"Results_DataText\">(.*)<\/span>')

def get_aircraft_from_tail_number(tail):

  # Could also DL the CSV database from FAA nightly and query directly
  response = requests.get("http://registry.faa.gov/aircraftinquiry/NNum_Results.aspx?NNumbertxt=%s" % (tail))
  if response.status_code == requests.codes.ok:
    matches = modelre.findall(response.content)
    if matches:
      return matches[0].strip()

  return None


# regex to extract US tail numbers from strings. 
# source: https://onehundredairports.com/2015/09/04/creating-a-regular-expression-for-us-tail-numbers/
tailre = re.compile('(N[1-9]\d{0,4}|N[1-9]\d{0,3}[A-HJ-NP-Z]|N[1-9]\d{0,2}[A-HJ-NP-Z]{2})')

def handler(event, context):

    bucket = event['bucket']
    key = urllib.unquote_plus(event['key'].encode('utf8'))
 
    try:
        tail_numbers = []
        # Use AWS Rekognition to extract text from the image
        response = rek.detect_text( Image = { "S3Object":
          { "Bucket": bucket, "Name": key}
        })
        detections = response['TextDetections']
        for detection in detections:
            string = detection['DetectedText']
            
            if tailre.match(string):
              # If the text looks like a tail number, query the FAA
              aircraft = get_aircraft_from_tail_number(string)
              if aircraft:
                tail_numbers.append({ 'tail_number': string, 
                                      'aircraft_type': aircraft, 
                                      'bounding_box': detection['Geometry']['BoundingBox']})

        print(tail_numbers)
        return tail_numbers

    except Exception as e:
        print(e)
        print("Error processing {} from bucket {}. ".format(key, bucket)) 
        raise e
