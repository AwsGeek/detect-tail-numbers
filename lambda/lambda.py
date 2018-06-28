from __future__ import print_function

import re
import boto3
import urllib2
from botocore.vendored import requests

print('Loading function')

rek = boto3.client('rekognition')

# A regex to extract aircraft model number from the returned HTML
def tailNumberLookup(tail):
  print("Looking up tail number: %s" % (tail))
  
  query = "https://www.google.com/search?num=1&q=%s+site:www.planespotters.net+inurl:airframe" % (tail)
  response = requests.get(query)
  if response.status_code == requests.codes.ok:
    matches = tailNumberLookup.regex.search(response.content)
    print(matches)
    if matches:
      return "%s %s" % (matches.group(1).strip(), matches.group(2).strip())

  return None
tailNumberLookup.regex = re.compile('https://www.planespotters.net/airframe/(.*?)/(.*?)/(.*?)/.*')


# regex to extract tail numbers from strings
# source: https://onehundredairports.com/2015/09/04/creating-a-regular-expression-for-us-tail-numbers/
# https://en.wikipedia.org/wiki/List_of_aircraft_registration_prefixes
tailNumberRegexs = [
  re.compile('(N[1-9]\d{0,4}|N[1-9]\d{0,3}[A-HJ-NP-Z]|N[1-9]\d{0,2}[A-HJ-NP-Z]{2})'),  # US
  re.compile('(C-G[A-Z]{3}|C-F[A-Z]{3})'),                                             # CA
  re.compile('(X[A-C]-[A-Z]{3})'),                                                     # MX
]

def handler(event, context):

    aircraft = {}
    
    try:
        if 'url' in event:
          url = event['url']
          response = urllib2.urlopen(url)
          image = {'Bytes': response.read()}
        elif 'bucket' in event and 'key' in event:
          bucket = event['bucket']
          key = urllib.unquote_plus(event['key'].encode('utf8'))
          image = { "S3Object": { "Bucket": bucket, "Name": key} }
        else:
          return []
          
        # Use AWS Rekognition to extract text from the image
        response = rek.detect_text( Image = image )
        textDetections = response['TextDetections']
        for textDetection in textDetections:
            detectedText = textDetection['DetectedText']
            if detectedText in aircraft:
                continue

            for tailNumberRegex in tailNumberRegexs:
                if tailNumberRegex.match(detectedText):
                  # If the text looks like a tail number, query the FAA
                  aircraftType = tailNumberLookup(detectedText)
                  if aircraftType:
                    aircraft[detectedText] = ({ 'tailNumber': detectedText, 
                                                'aircraftType': aircraftType, 
                                                'boundingBox': textDetection['Geometry']['BoundingBox']})

    except Exception as e:
        print(e)

    print(aircraft.values())
    return aircraft.values()

