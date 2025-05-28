# SageMaker Pipeline Infrastructure as Code

[![AWS CDK](https://img.shields.io/badge/AWS%20CDK-2.176.0-orange.svg)](https://aws.amazon.com/cdk/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6.3-blue.svg)](https://www.typescriptlang.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A production-ready Infrastructure as Code (IaC) solution for deploying and managing AWS SageMaker ML pipelines using AWS CDK with TypeScript. This project demonstrates enterprise-level cloud architecture patterns, automated ML pipeline deployment, and scalable infrastructure management.

## 🏗️ Architecture Overview

This solution implements a multi-stack architecture for ML pipeline management:

- **Pipeline Stack**: Provisions SageMaker pipelines with proper IAM roles and permissions
- **Scripts Stack**: Manages ML script deployment and S3 integration
- **Environment-agnostic**: Supports multiple deployment environments (dev/QA/prod)
- **Client-configurable**: Multi-tenant architecture supporting different client configurations

## 📁 Project Structure

```
├── bin/
│   └── ip-pipeline.ts          # CDK app entry point
├── lib/
│   ├── ip-pipeline-stack.ts    # SageMaker pipeline infrastructure
│   └── ip-scripts-stack.ts     # S3 script deployment
├── scripts/
│   └── ip-script.py            # Python ML processing script
├── sm-pipeline-client-n1.json  # Pipeline definition
├── cdk.json                    # CDK configuration
├── tsconfig.json              # TypeScript configuration
└── jest.config.js             # Testing configuration
```

## 🚀 Quick Start

### Prerequisites
- AWS CLI configured with appropriate permissions
- Node.js 18+ and npm
- Python 3.8+ (for ML scripts)
- AWS CDK CLI installed globally

### Installation & Deployment

```bash
# Clone and install dependencies
git clone <repository-url>
cd ip-pipeline
npm install

# Configure environment
export CDK_DEFAULT_ACCOUNT=<your-aws-account-id>
export CDK_DEFAULT_REGION=<your-preferred-region>

# Build and test
npm run build
npm test

# Deploy infrastructure
npm run cdk deploy --all

# Or deploy specific stacks
npm run cdk deploy IPPipelineStack
npm run cdk deploy IPScriptsStack
```

## 📋 Configuration

### Environment Variables
```bash
CDK_DEFAULT_ACCOUNT  # AWS Account ID
CDK_DEFAULT_REGION   # Deployment region
```

### Stack Configuration
```typescript
const commonTags = {
  Environment: 'dev || QA || prod',
  Project: 'CLIENT1',
  Owner: 'MLE',
  CostCenter: 'IT',
  Application: 'APP1'
};

const g_bucket = 'bucket-s3-prod';
const g_client = 'client-n1';
```

## 🏛️ Infrastructure Components

### SageMaker Pipeline Stack
- **Pipeline Creation**: Automated SageMaker pipeline provisioning
- **IAM Roles**: Service-linked roles with comprehensive permissions
- **Pipeline Definition**: JSON-based configuration management
- **Security**: Least-privilege access patterns

### Scripts Deployment Stack
- **S3 Integration**: Automated script upload and versioning
- **Path Management**: Client-specific script organization
- **Deployment Options**: Configurable retention policies
- **Asset Management**: CDK asset bundling and deployment

## 🧪 Testing

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test -- --watch

# Generate coverage report
npm run test -- --coverage
```

## 📈 DevOps Integration

### Build Commands
```bash
npm run build    # Compile TypeScript
npm run watch    # Watch mode for development
npm run test     # Run test suite
npm run cdk      # CDK CLI commands
```

### CI/CD Pipeline Support
- GitHub Actions compatible
- GitLab webhook that integrate with AWS
- Automated testing on PR
- Multi-environment deployment support
- Infrastructure drift detection
