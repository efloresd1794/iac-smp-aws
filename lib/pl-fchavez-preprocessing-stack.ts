import * as cdk from 'aws-cdk-lib';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as sagemaker from 'aws-cdk-lib/aws-sagemaker';
import { Construct } from 'constructs';
import * as fs from 'fs';

//props
interface PlFchavezPreprocessingStackProps extends cdk.StackProps {
  bucketName: string;
  clientName: string;
  productName: string;
  modelVersion: string;
}

export class PlFchavezPreprocessingStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: PlFchavezPreprocessingStackProps) {
    super(scope, id, props);

    const { clientName, productName, modelVersion } = props;
    
    const pipelineName = `pipeline-${clientName}-${productName}-${modelVersion}`;
    const definitionFile = `pd-${clientName}-${productName}-${modelVersion}.json`;

    const pipelineRole = new iam.Role(this, 'SageMakerPipelineRole', {
      assumedBy: new iam.ServicePrincipal('sagemaker.amazonaws.com'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonSageMakerFullAccess'),
        iam.ManagedPolicy.fromAwsManagedPolicyName('AWSLambda_FullAccess'),
        iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonS3FullAccess'),
      ],
    });

    // Load the pipeline definition JSON
    const pipelineDefinition = JSON.parse(
      // how define name based on stack props
      fs.readFileSync(definitionFile, 'utf8')
    );
    
    const pipeline = new sagemaker.CfnPipeline(this, 'FchavezPreprocessingPipeline', {
      pipelineName: pipelineName,
      pipelineDefinition: {
        "PipelineDefinitionBody" : JSON.stringify(pipelineDefinition),
      },
      roleArn: pipelineRole.roleArn,
    });
  }
}