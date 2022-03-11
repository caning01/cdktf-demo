#!/usr/bin/env python
from constructs import Construct
from cdktf import App, TerraformStack
from imports.aws import AwsProvider
from imports.aws.s3 import S3Bucket
from imports.aws.vpc import Vpc

DEFAULTVPCCONFIG = {
    'PROD': {
        'CIB': {
            'cidr': '10.0.0.0/16',
            'azs': ['us-east-1a', 'us-east-1b'],
            'public_subnets': ['10.0.1.0/24', '10.0.2.0/24']
        },
        'GTI': {
            'cidr': '192.0.0.0/16',
            'azs': ['us-east-1a', 'us-east-1b'],
            'public_subnets': ['192.0.1.0/24', '192.0.2.0/24']
        }
    },
    'DEV': {
        'CIB': {
            'cidr': '172.0.0.0/16',
            'azs': ['us-east-1a', 'us-east-1b'],
            'public_subnets': ['172.0.1.0/24', '172.0.2.0/24']
        },
        'GTI': {
            'cidr': '173.0.0.0/16',
            'azs': ['us-east-1a', 'us-east-1b'],
            'public_subnets': ['173.0.1.0/24', '173.0.2.0/24']
        }
    }
}


class CustomS3Construct(Construct):
    def __init__(self,
                 scope: Construct,
                 ns: str,
                 stage: str,
                 lob: str):
        self.stage = stage
        self.lob = lob
        super().__init__(scope, ns)

        ## Creates a bucket ex: demo-gti-prod
        s3_bucket_1 = S3Bucket(self,
                               f's3-{lob}-{stage}'.upper(),
                               bucket=f'demo-{lob}-stage'.lower(),
                               tags={'lob': lob,
                                     'owner': lob}
                               )

        ## Creates a bucket ex: demo-gti1-prod
        s3_bucket_2 = S3Bucket(self,
                               f's3-{lob}1-{stage}'.upper(),
                               bucket=f'demo-{lob}1-stage'.lower(),
                               tags={'lob': lob,
                                     'owner': lob}
                               )
        ## Creates dependency to the resource creation
        s3_bucket_2.node.add_dependency(s3_bucket_1)


class CustomVPCConstruct(Construct):
    def __init__(self,
                 scope: Construct,
                 ns: str,
                 stage: str,
                 lob: str):
        self.stage = stage
        self.lob = lob
        super().__init__(scope, ns)
        vpc_configs = DEFAULTVPCCONFIG.get(stage.upper(), 'DEV').get('lob'.upper())

        Vpc(self,
            f'VPC-{lob}-{stage}'.upper(),
            name=f'VPC-{lob}-{stage}'.upper(),
            cidr_block=vpc_configs['cidr'],
            azs=vpc_configs['azs'],
            public_subnets=vpc_configs['public_subnets']
            )


class MyStack(TerraformStack):
    def __init__(self,
                 scope: Construct,
                 ns: str,
                 lob: str,
                 stage: str,
                 region: str):
        self.lob = lob
        self.stage = stage
        self.region = region
        super().__init__(scope,
                         ns)

        # define resources here
        AwsProvider(self, 'Aws', region='us-east-1')
        s3_bucket = CustomS3Construct(self,
                                      f'{lob}S3Bucket{stage}',
                                      lob=lob,
                                      stage=stage)
        # vpc1 = CustomS3Construct(self,
        #                          f'{lob}S3Bucket',
        #                          lob=lob,
        #                          stage=stage)
        # vpc1.node.add_dependency(s3_bucket)


app = App()
MyStack(app,
        'demo-tfcdk-cib-dev',
        lob='ds',
        stage='sd',
        region='us-east-1')
# MyStack(app, "demo-tfcdk-cib-dev", stage='dev', region='us-east-2', lob='CIB')
# MyStack(app, "demo-tfcdk--cib-prod", stage='prod', region='us-east-1', lob='CIB')
# MyStack(app, "demo-tfcdk-gti-dev", stage='dev', region='us-east-2', lob='GTI')
# MyStack(app, "demo-tfcdk-gti-prod", stage='prod', region='us-east-1', lob='GTI')

app.synth()

