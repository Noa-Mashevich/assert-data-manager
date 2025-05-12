import boto3

from botocore.config import Config
from django.db import models
from django.core.cache import cache
from django.conf import settings

from server.utils import is_migration

# TODO refactor how Stack outputs are accessed in the project


class StackManager(models.Manager):
    STACKS_KEY = 'stacks'

    def __init__(self, *args, **kwargs):
        super(StackManager, self).__init__(*args, **kwargs)
        self._load_config()

    def _load_config(self):
        stack_list = settings.AWS_STACKS
        for stack_name, stack_region in stack_list:
            self._store_stack_outputs(stack_region, stack_name)

    def list(self):
        return cache.get(self.STACKS_KEY)

    def _store_stacks(self, stack_list):
        cache.set(self.STACKS_KEY, stack_list)

    def _get_key(self, stack_region, stack_name, output_key):
        return f'{stack_region}.{stack_name}.{output_key}'

    def _get_output(self, stack_region, stack_name, cache_key):
        value = cache.get(cache_key)
        # this code below is making a reasonable effort to resolve the stack outputs
        if not value:
            self._store_stack_outputs(stack_region, stack_name)
            value = cache.get(cache_key)
        return value

    def output(self, stack_region, stack_name, output_key):
        cache_key = self._get_key(stack_region, stack_name, output_key)
        value = self._get_output(stack_region, stack_name, cache_key)
        if not value:
            raise ValueError(f'Missing Stack output value for key {cache_key}')
        return value

    def _store_output(self, stack_region, stack_name, output_key, output_value):
        cache_key = self._get_key(stack_region, stack_name, output_key)
        cache.set(cache_key, output_value)

    def _store_stack_outputs(self, stack_region, stack_name):
        # do not fetch stack outputs in migrations
        if is_migration():
            return

        # optimization
        # use client for the default region or instantiate
        cfn_client = settings.AWS_CLIENT_CFN
        if stack_region != settings.AWS_REGION:
            config = Config(retries={'max_attempts': 3, 'mode': 'adaptive'})
            cfn_client = boto3.client(
                'cloudformation', region_name=stack_region, config=config
            )

        response = cfn_client.describe_stacks(StackName=stack_name)

        outputs = response['Stacks'][0]['Outputs']
        for output in outputs:
            self._store_output(
                stack_region, stack_name, output['OutputKey'], output['OutputValue']
            )

    def get_queryset(self):
        raise NotImplementedError


class Stack(models.Model):
    objects = StackManager()

    class Meta:
        managed = False
