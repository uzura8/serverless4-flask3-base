# Flask3 on Serverless4 Project Template

Constructed by

- Serverside:
  - Python/Flask3 on Lambda + APIGateway
  - DynamoDB
  - Deploy by Terraform and Serverless Framework ver4

## Instration

#### Preparation

You need below

- common
  - aws-cli >= 1.32.X
  - Terraform >= 1.9.1
- serverless
  - nodeJS >= 22.3.X
  - Python >= 3.12.X

#### Install tools

Install serverless, python venv and terraform on mac

```bash
# At project root dir
cd (project_root/)serverless
npm install
python -m venv .venv

brew install tfenv
tfenv install 1.8.5
tfenv use 1.8.5
```

### Install Packages

Install npm packages

```bash
# At project root dir
cd (project_root/)serverless
npm install
```

Install python packages

```bash
. .venv/bin/activate
pip install -r requirements.txt
```

## Deploy AWS Resources by Terraform

#### Create AWS S3 Bucket for terraform state and frontend config

Create S3 Buckets like below in ap-northeast-1 region

- **your-serverless-deployment**
  - Store deployment state files by terraformand and serverless framework
  - Create directory "terraform/your-project-name"
- **your-serverless-configs**
  - Store config files for app
  - Create directory "your-project-name/frontend/prd" and "your-project-name/frontend/dev"

#### 1. Edit Terraform config file

Copy sample file and edit variables for your env

```bash
cd (project_root_dir)/terraform
cp terraform.tfvars.sample terraform.tfvars
vi terraform.tfvars
```

#### 2. Set AWS profile name to environment variable

```bash
export AWS_SDK_LOAD_CONFIG=1
export AWS_PROFILE=your-aws-profile-name
export AWS_REGION="ap-northeast-1"
```

#### 3. Execute terraform init

Command Example to init

```bash
terraform init -backend-config="bucket=your-deployment" -backend-config="key=terraform/your-project/terraform.tfstate" -backend-config="region=ap-northeast-1" -backend-config="profile=your-aws-profile-name"
```

#### 4. Execute terraform apply

```bash
terraform apply -auto-approve -var-file=./terraform.tfvars
```

#### 5. Set CORS of media file bucket

- Access to S3 console of media file bucket
- Select tab "Permission"
- Press "Edit" button of "Cross-origin resource sharing (CORS)"
- Set bellow

```
[
    {
        "AllowedHeaders": [
            "*"
        ],
        "AllowedMethods": [
            "PUT",
            "POST",
            "DELETE",
            "GET"
        ],
        "AllowedOrigins": [
            "https://your-domain.example.com"
        ],
        "ExposeHeaders": []
    }
]
```

## DynamoDB Backup Settings

If you want to backup DynamoDB items, set bellows

- Access to "AWS Backup" on AWS Console and set region
- Press "Create backup plan"
- Input as follows for "Plan"
  - Start options
    - Select "Build a new plan"
    - Backup plan name: your-project-dynamodb-backup
  - Backup rule configuration
    - Backup vault: Default
    - Backup rule name: your-project-dynamodb-backup-rule
    - Backup frequency: Daily
    - Backup window: Customize backup window
    - Backup window settings: as you like
  - Press "Create backup plan"
- Input as follows for "Assign resources"
  - General
    - Resource assignment name: your-project-dynamodb-backup-assignment
    - IAM role: Default role
  - Resource selection
    - 1. Define resource selection: Include specific resource types
    - 2. Select specific resource types: DynamoDB
      - Table names: All tables
    - 4. Refine selection using tags
      - Key: backup
      - Condition for value: Eauqls
      - Value: aws-backup
  - Press "Assign resources"

## Deploy Server Side Resources

### Setup configs

Setup config files per stage

```bash
cd (project_root/)serverless
cp -r config/stages-sample config/stages
vi config/stages/*
```

### Create Domains for API

Execute below command

```bash
cd (project_root/)serverless
export AWS_SDK_LOAD_CONFIG=1
export AWS_PROFILE="your-profile-name"
export AWS_REGION="ap-northeast-1"

npx sls create_domain # Deploy for dev
```

If deploy for prod

```bash
npx sls create_domain --stage prd # Deploy for prod
```

### Deploy to Lambda

Execute below command

```bash
cd (project_root/)serverless
export AWS_SDK_LOAD_CONFIG=1
export AWS_PROFILE="your-profile-name"
export AWS_REGION="ap-northeast-1"

npx sls deploy # Deploy for dev
```

If deploy for prod

```bash
npx sls deploy --stage prd # Deploy for prod
```

## Deploy Frontend Resources

### Set enviroment variables

- Access to https://github.com/{your-account}/{repository-name}/settings/secrets/actions
- Push "New repository secret"
- Add Below
  - Common
    - **AWS_ACCESS_KEY_ID** : your-aws-access_key
    - **AWS_SECRET_ACCESS_KEY** : your-aws-secret_key
  - For Production
    - **CLOUDFRONT_DISTRIBUTION** : your cloudfront distribution created by terraform for production
    - **S3_CONFIG_BUCKET**: "your-serverles-configs/your-project/frontend/prd" for production
    - **S3_RESOURCE_BUCKET**: "your-domain-static-site.example.com" for production
  - For Develop
    - **CLOUDFRONT_DISTRIBUTION_DEV** : your cloudfront distribution created by terraform for develop
    - **S3_CONFIG_BUCKET_DEV**: "your-serverles-configs/your-project/frontend/dev" for develop
    - **S3_RESOURCE_BUCKET_DEV**: "your-domain-static-site-dev.example.com" for develop

### Upload config file for frontend app

#### Edit config file

#### Basic config

```bash
cd (project_root_dir/)frontend
cp src/config/config.json.sample src/config/config.json
vi src/config/config.json
```

#### Upload S3 Bucket "your-serverless-configs/your-project-name/frontend/{stage}"

#### Deploy continually on pushed to git

## Development

### Local Development

Install packages for development

```bash
cd (project_root/)serverless
. .venv/bin/activate
pip install pylint
```

### Work on local

Set venv

```bash
cd (project_root/)serverless
. .venv/bin/activate
```

Create Docker container only for the first time

```bash
cd (project_root/)serverless
docker-compose build
```

Start DynamoDB Local on Docker

```bash
cd (project_root)/serverless/develop/
docker-compose up -d
```

DynamomDB setup

```bash
cd (project_root/)serverless
npx sls dynamodb start
```

Execute below command

```bash
cd (project_root/)serverless
npx sls wsgi serve
```

Request [http://127.0.0.1:5000](http://127.0.0.1:5000/hoge)

If you want to stop DynamoDB Local on Docker

```bash
cd (project_root)/serverless/develop/
docker-compose stop
```

#### Execute Script

```bash
cd (project_root/)serverless
npx sls invoke local --function funcName --data param
```

### Performance Test

#### Setup K6

Install for macOS

```bash
brew install k6
```

#### Execute

```bash
k6 run ./dev_tools/performance/vote.js --vus NN --duration MMs
```

## Destroy Resources

Destroy for serverless resources

```bash
cd (project_root/)serverless
npx sls remove --stage Target-stage
npx sls delete_domain --stage Target-stage
```

Removed files in S3 Buckets named "your-domain.example.com-cloudfront-logs" and "your-domain.example.com"

Destroy for static server resources by Terraform

```bash
cd (project_root/)terraform
terraform destroy -auto-approve -var-file=./terraform.tfvars
```
