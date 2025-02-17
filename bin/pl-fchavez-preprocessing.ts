#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { PlFchavezPreprocessingStack } from '../lib/pl-fchavez-preprocessing-stack';
import { PlScriptsStack } from '../lib/pl-scripts-stack';
import { Tags } from 'aws-cdk-lib';

const env = { 
  account: process.env.CDK_DEFAULT_ACCOUNT, 
  region: process.env.CDK_DEFAULT_REGION 
};

const commonTags = {
  Environment: 'Dev',
  Project: 'FarmaciasChavez',
  Owner: 'MLOps',                   
  CostCenter: 'IT',                  
  Application: 'Preprocessing',         
};

const pl_bucket = 'pricelab-mlops-prod';
const pl_client = 'c-farmaciaschavez';
const pl_product = 'preprocessing';
const pl_modelv = 'mv3';

const app = new cdk.App();

const plfchavezppstack = new PlFchavezPreprocessingStack(app, 'PlFchavezPreprocessingStack', {
  bucketName: pl_bucket,
  clientName: pl_client,
  productName: pl_product,
  modelVersion: pl_modelv,
  env
});

const plfchavezspstack = new PlScriptsStack(app, 'PlScriptsPreprocessingStack',{
  bucketName: pl_bucket,
  clientName: pl_client,
  productName: pl_product,
  modelVersion: pl_modelv,
  env
});

// Apply tags to all stacks
[plfchavezppstack, plfchavezspstack].forEach(stack => {
  Object.entries(commonTags).forEach(([key, value]) => {
    Tags.of(stack).add(key, value);
  });
});

app.synth();