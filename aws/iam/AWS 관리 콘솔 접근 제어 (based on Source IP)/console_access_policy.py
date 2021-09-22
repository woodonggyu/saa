#!/usr/bin/env python

import json
import boto3
from botocore.exceptions import ClientError


group = 'Admin'
allow_ip_addresses = ["1.1.1.1/32"]

iam = boto3.client('iam')

# create iam policy
with open(file='policy.json', mode='rb') as fp:
    policy = json.load(fp)

# setting a iam policy
policy['Statement']['Condition']['NotIpAddress']['aws:SourceIp'] = \
    allow_ip_addresses

try:
    # create iam policy
    response = iam.create_policy(PolicyName='TestPolicy2',
                                 PolicyDocument=json.dumps(policy))
    # get an Arn
    arn = response['Policy']['Arn']

    # attach iam group
    iam.attach_group_policy(GroupName=group, PolicyArn=arn)

except ClientError as error:
    # policy already exists
    if error.response['Error']['Code'] == 'EntityAlreadyExists':
        print(error.response['Error']['Message'])
