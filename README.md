# detect-tail-numbers
This example demonstrates the use of the [AWS Rekognition DetectText API](https://docs.aws.amazon.com/rekognition/latest/dg/API_DetectText.html) to detect tail numbers on commercial US aircraft. The included Lambda function uses Rekognition to detect text in an image, then filters that text to include only strings that match the US aircraft tail number format. Finally, it queries the [FAA database](http://registry.faa.gov/aircraftinquiry/NNum_Inquiry.aspx) for information about the tail numbers detected and returns the results.

#### 1. Clone this repo

```
git clone https://github.com/awsgeek/detect-tail-numbers
```

#### 2. Package the Lambda functions and upload to S3.  
The ```cloudformation package``` command packages local artifacts used by your lambda function and uploads them to S3. The command replaces references to local artifacts in your template with references to the S3 location and returns the modified template. 

Packaging requires that you provide the ```<AWS Region>``` you’ll be operating in and the ```<Bucket Name>``` to upload the resulting Lambda function packages to. Once the package has been created, you can ```cloudformation deploy``` to deploy your function after providing a ```<Stack Name>```

```
aws —region <AWS Region> cloudformation package —template-file template.yaml —s3-bucket <Bucket Name> —output-template-file package.yaml 
aws —region <AWS Region> cloudformation deploy —stack-name <Stack Name> —template-file package.yaml —capabilities CAPABILITY_IAM
```

There's also a convienient script provided that you can run lik:

```build.sh <AWS Region> <Bucket Name> <Stack Name>```

#### 3. Test the Lambda function.
Upload an image to an S3 bucket you own. In the Lambda console, create a test event like the one below to verify everything is working correctly.

```
{
  "bucket": "<Image Bucket>",
  "key": "<Image Name>"
}
```
