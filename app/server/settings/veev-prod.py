from .base import *

AWS_STACK_STORAGE_CDN = 'veev-prod-storage-cdn'
AWS_STACK_STORAGE_CDN_REGION = 'us-east-1'
AWS_STACK_STORAGE = 'veev-prod-storage'
AWS_STACK_UPLOAD = 'veev-prod-upload'
AWS_STACKS = [
    # the app should not reference its own stack
    # deployment with outputs finishes after the app is already started
    (AWS_STACK_STORAGE_CDN, AWS_STACK_STORAGE_CDN_REGION),
    (AWS_STACK_STORAGE, AWS_REGION),
    (AWS_STACK_UPLOAD, AWS_REGION),
]
