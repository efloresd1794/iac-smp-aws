#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { IPPipelineStack } from '../lib/ip-pipeline-stack';
import { IPScriptsStack } from '../lib/ip-scripts-stack';
import { Tags } from 'aws-cdk-lib';

const env = { 
  account: process.env.CDK_DEFAULT_ACCOUNT, 
  region: process.env.CDK_DEFAULT_REGION 
};

const commonTags = {
  Environment: 'dev || QA || prod',
  Project: 'CLIENT1',
  Owner: 'MLE',                   
  CostCenter: 'IT',                  
  Application: 'APP1',         
};

const g_bucket = 'bucket-s3-prod';
const g_client = 'client-n1';

const app = new cdk.App();

const plfchavezppstack = new IPPipelineStack(app, 'IPPipelineStack', {
  bucketName: g_bucket,
  clientName: g_client,
  env
});

const plfchavezspstack = new IPScriptsStack(app, 'IPScriptsStack',{
  bucketName: g_bucket,
  clientName: g_client,
  env
});

[plfchavezppstack, plfchavezspstack].forEach(stack => {
  Object.entries(commonTags).forEach(([key, value]) => {
    Tags.of(stack).add(key, value);
  });
});

app.synth();