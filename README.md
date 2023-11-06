<!--
title: 'AWS Python Example'
description: 'This template demonstrates how to deploy a Python function running on AWS Lambda using the traditional Serverless Framework.'
layout: Doc
framework: v3
platform: AWS
language: python
priority: 2
authorLink: 'https://github.com/serverless'
authorName: 'Serverless, inc.'
authorAvatar: 'https://avatars1.githubusercontent.com/u/13742415?s=200&v=4'
-->


# Serverless Framework AWS Python Example

This template demonstrates how to deploy a Python function running on AWS Lambda using the traditional Serverless Framework. The deployed function does not include any event definitions as well as any kind of persistence (database). For more advanced configurations check out the [examples repo](https://github.com/serverless/examples/) which includes integrations with SQS, DynamoDB or examples of functions that are triggered in `cron`-like manner. For details about configuration of specific `events`, please refer to our [documentation](https://www.serverless.com/framework/docs/providers/aws/events/).

## Usage

### Deployment

In order to deploy the example, you need to run the following command:

```
$ serverless deploy
```

After running deploy, you should see output similar to:

```bash
Deploying aws-python-project to stage dev (us-east-1)

✔ Service deployed to stack aws-python-project-dev (112s)

functions:
  hello: aws-python-project-dev-hello (1.5 kB)
```

### Invocation

After successful deployment, you can invoke the deployed function by using the following command:

```bash
serverless invoke --function hello
```

Which should result in response similar to the following:

```json
{
    "statusCode": 200,
    "body": "{\"message\": \"Go Serverless v3.0! Your function executed successfully!\", \"input\": {}}"
}
```

### Local development

You can invoke your function locally by using the following command:

```bash
serverless invoke local --function hello
```

Which should result in response similar to the following:

```
{
    "statusCode": 200,
    "body": "{\"message\": \"Go Serverless v3.0! Your function executed successfully!\", \"input\": {}}"
}
```

### Bundling dependencies

In case you would like to include third-party dependencies, you will need to use a plugin called `serverless-python-requirements`. You can set it up by running the following command:

```bash
serverless plugin install -n serverless-python-requirements
```

Running the above will automatically add `serverless-python-requirements` to `plugins` section in your `serverless.yml` file and add it as a `devDependency` to `package.json` file. The `package.json` file will be automatically created if it doesn't exist beforehand. Now you will be able to add your dependencies to `requirements.txt` file (`Pipfile` and `pyproject.toml` is also supported but requires additional configuration) and they will be automatically injected to Lambda package during build process. For more details about the plugin's configuration, please refer to [official documentation](https://github.com/UnitedIncome/serverless-python-requirements).


### Other Importand commands and errors encountered during development

list default profile : 
```bash
aws configure list
```
list other profile :  
```bash
aws configure list --profile <profile_name>
```
list all profiles : 
```bash
aws configure list-profiles
```
to change the default profile : 
```bash
setx AWS_DEFAULT_PROFILE <profile_name>
```

[ERROR] ClientError: 
An error occurred (AccessDeniedException) when calling the SendTaskFailure operation: 
User: arn:aws:sts::752671163579:assumed-role/product-inventory-management-dev-us-east-2-lambdaRole/product-inventory-management-dev-sqsWorkerFn 
is not authorized to perform: states:SendTaskFailure on resource: arn:aws:states:us-east-2:752671163579:stateMachine:productCheckOutFlow 
because no identity-based policy allows the states:SendTaskFailure action

--- For this error we need to assign policy for the particular role mentioned in the error (sns,sqs,step functions)

Integration request template for calling step functions from AWS API gateway
```
 #set($input = $input.json('$'))
  {
     "input": "$util.escapeJavaScript($input).replaceAll("\\'", "'")",
    "stateMachineArn": "arn:aws:states:us-east-2:752671163579:stateMachine:productCheckOutFlow"
  }
```