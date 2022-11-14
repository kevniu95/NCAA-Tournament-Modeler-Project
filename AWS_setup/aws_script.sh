#! /bin/bash

aws ec2 run-instances --image-id ami-026b57f3c383c2eec --count 1 --instance-type t2.micro --key-name kniu --security-group-ids sg-0232c4467da0921d2 --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=kniu-ncaa}]' --iam-instance-profile Name=ec2_admin 

ssh -i ~/.ssh/kniu.pem ec2-user@3.85.143.204
ssh -i ~/.ssh/kniu.pem ec2-user@3.221.83.248