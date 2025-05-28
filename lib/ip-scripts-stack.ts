import * as cdk from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as s3deploy from 'aws-cdk-lib/aws-s3-deployment';
import { Construct } from 'constructs';
import * as path from 'path';

interface IPScriptsStackProps extends cdk.StackProps {
  bucketName: string;
  clientName: string;
}

export class IPScriptsStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: IPScriptsStackProps) {
    super(scope, id, props);

    const { bucketName, clientName } = props;

    const s3path = `${clientName}/scripts`;

    const bucket = s3.Bucket.fromBucketName(
      this, 
      'ExistingBucket',
      bucketName
    );

    new s3deploy.BucketDeployment(this, 'DeployScripts', {
      sources: [s3deploy.Source.asset(path.join(__dirname, '..', 'scripts'))],
      destinationBucket: bucket,
      destinationKeyPrefix: s3path,
      retainOnDelete: false,
    });
  }
}