import * as cdk from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as s3deploy from 'aws-cdk-lib/aws-s3-deployment';
import { Construct } from 'constructs';
import * as path from 'path';

//props
interface PlScriptsStackProps extends cdk.StackProps {
  bucketName: string;
  clientName: string;
  productName: string;
  modelVersion: string;
}

export class PlScriptsStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: PlScriptsStackProps) {
    super(scope, id, props);

    const { bucketName, clientName, productName, modelVersion } = props;
    
    const s3path = `${clientName}/${productName}/${modelVersion}/scripts`;
    
    // Define bucket
    const bucket = s3.Bucket.fromBucketName(
      this, 
      'ExistingBucket',
      bucketName
    );

    // Deploy scripts to S3
    new s3deploy.BucketDeployment(this, 'DeployScripts', {
      sources: [s3deploy.Source.asset(path.join(__dirname, '..', 'scripts'))],
      destinationBucket: bucket,
      destinationKeyPrefix: s3path,
      retainOnDelete: false,
    });
  }
}