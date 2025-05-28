import * as cdk from 'aws-cdk-lib';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as sagemaker from 'aws-cdk-lib/aws-sagemaker';
import { Construct } from 'constructs';
import * as fs from 'fs';

interface IPPipelineStackStackProps extends cdk.StackProps {
  bucketName: string;
  clientName: string;
}

export class IPPipelineStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: IPPipelineStackStackProps) {
    super(scope, id, props);

    const { bucketName, clientName } = props;
    
    const pipelineName = `pipeline-${clientName}`;
    const definitionFile = `sm-pipeline-${clientName}.json`;

    const pipelineRole = new iam.Role(this, 'SageMakerPipelineRole', {
      assumedBy: new iam.ServicePrincipal('sagemaker.amazonaws.com'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonSageMakerFullAccess'),
        iam.ManagedPolicy.fromAwsManagedPolicyName('AWSLambda_FullAccess'),
        iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonS3FullAccess'),
      ],
    });

    const pipelineDefinition = JSON.parse(
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