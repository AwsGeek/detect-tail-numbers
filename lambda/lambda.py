from __future__ import print_function

import re
import boto3
import urllib2
from botocore.vendored import requests

print('Loading function')

rek = boto3.client('rekognition')

# There are many ways to do this , some harder than others. One way involves scouring the web for APIs or 
# databases of aircraft information (some countries provide them, many don't), then maintaining and updating. 
# Another way is to simply search for links that include tail numbers and extract the interesting info from 
# the found links. Many aircraft enthusiast sites around the world maintain large collections of aircraft 
# images and information, with links conveniently crawled and indexed by popular search engines. This is the 
# method used here

def tailNumberLookup(tailNumber):
  print("Looking up tail number: %s" % (tailNumber))

  response = requests.get(tailNumberLookup.search % (tailNumber))  
  if response.status_code == requests.codes.ok:
    
    matches = tailNumberLookup.regex.search(response.content)
    if matches:
      
      # Return manufacturer and model, like "Boeing 747"
      maker = matches.group(1).strip()
      model = matches.group(2).strip()
      return "%s %s" % (maker, model)

  return None

# The search URL to find the link with the aircraft tail number in it
tailNumberLookup.search = "https://www.google.com/search?num=1&q=%s+site:www.planespotters.net+inurl:airframe"

# A regex to extract aircraft manufacturer & model number from the URL
tailNumberLookup.regex = re.compile('https://www.planespotters.net/airframe/(.*?)/(.*?)/(.*?)/.*')

# Regular expressions to search for tail numbers in strings found by Rekognition. The source for these can
# be found here: https://en.wikipedia.org/wiki/List_of_aircraft_registration_prefixes
# Is there a better way of doing this? Other than maintaining a (changing) list of individual RegExs?
tailNumberRegexs = [
  # source: https://onehundredairports.com/2015/09/04/creating-a-regular-expression-for-us-tail-numbers/
  re.compile('(N[1-9]\d{0,4}|N[1-9]\d{0,3}[A-HJ-NP-Z]|N[1-9]\d{0,2}[A-HJ-NP-Z]{2})'),  # US
  re.compile('(C-G[A-Z]{3}|C-F[A-Z]{3})'),                                             # CA
  re.compile('(X[A-C]-[A-Z]{3})'),                                                     # MX
]

# The input event JSON contains a list of images to process. Each image should be identified by an S3 
# bucket and key, or by URL, like so: { images: [{ bucket: <bucket>, key: <key> }  OR { image: { url: <url> }] }

def handler(event, context):

    aircraft = {}
    
    if 'images' in event:
      return 

      for image in event['images']:
        try:
          if 'url' in event:
            uri = event['url']
            response = urllib2.urlopen(uri)
            image = {'Bytes': response.read()}
          elif 'bucket' in event and 'key' in event:
            bucket = event['bucket']
            key = urllib.unquote_plus(event['key'].encode('utf8'))
            uri = "s3://%s%s" % (bucket, key)
            image = { "S3Object": { "Bucket": bucket, "Name": key} }
          else:
            print ("Invalid image specification: %s" % (image))
            continue

          # Use AWS Rekognition to extract text from the image
          response = rek.detect_text( Image = image )
          textDetections = response['TextDetections']
          for textDetection in textDetections:
              detectedText = textDetection['DetectedText']
              if detectedText in aircraft:
                  continue

              for tailNumberRegex in tailNumberRegexs:
                  if tailNumberRegex.match(detectedText):
                    # If the text looks like a tail number, look it up
                    aircraftType = tailNumberLookup(detectedText)
                    if aircraftType:
                      aircraft[detectedText] = ({ 'tailNumber': detectedText, 
                                                  'aircraftType': aircraftType, 
                                                  'boundingBox': textDetection['Geometry']['BoundingBox']})

        except Exception as e:
            print(e)

    print(aircraft.values())
    return aircraft.values()

