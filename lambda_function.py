import re
import json
import logging
from urllib.parse import parse_qs

# Legacy Endpoint Hosts
ORIGIN_ENDPOINT_1 = ''
ORIGIN_ENDPOINT_2 = ''
ORIGIN_ENDPOINT_3 = ''

# Load Balancer Endpoint for Istio Ingress Gateway
MSA_ENDPOINT = 'http://alb-xxx-xxx-xxx-xxx-0000000000.ap-northeast-2.elb.amazonaws.com/'

# Uri Patterns
URI_PATTERN_1 = '/xxx/'
URI_PATTERN_2 = '/xxxx/'

def lambda_handler(event, context):
    logger = logging.getLogger(context.aws_request_id)
    logger.setLevel(logging.DEBUG)

    request = event.get('Records')[0].get('cf').get('request')
    params = {k: v[0] for k, v in parse_qs(request.get('querystring')).items()}
    logger.info('Input Request: {}'.format(request))

    # Overwrite to Host Header From Seperate each service
    if re.compile(URI_PATTERN_1).match(request.get('uri')):
        request['headers']['host'] = [{'key': 'Host', 'value': ORIGIN_ENDPOINT_1}]
        request['origin']['custom']['domainName'] = ORIGIN_ENDPOINT_1
        
    elif re.compile(URI_PATTERN_2).match(request.get('uri')):
        request['headers']['host'] = [{'key': 'Host', 'value': ORIGIN_ENDPOINT_2}]
        request['origin']['custom']['domainName'] = ORIGIN_ENDPOINT_2
        
    else:
        request['headers']['host'] = [{'key': 'Host', 'value': ORIGIN_ENDPOINT_3}]
        request['origin']['custom']['domainName'] = ORIGIN_ENDPOINT_3

    with open('./api_info.json', 'r') as json_file:
        api_info = json.load(json_file)

    # Check the API from service_1 APIs
    if api_info.get(params.get('xxx')) and api_info.get(params.get('xxx')).get('endpoint') == 'msa':
        request['headers']['host'] = [{'key': 'Host', 'value': api_info.get(params.get('xxx')).get('header') + '.xxx.com'}]
        request['origin']['custom']['domainName'] = MSA_ENDPOINT
        request['origin']['custom']['port'] = 80
        request['origin']['custom']['protocol'] = 'http'

    # Check the API from service_2 APIs
    elif api_info.get(request.get('uri')) and api_info.get(request.get('uri')).get('endpoint') == 'msa':
        request['headers']['host'] = [{'key': 'Host', 'value': api_info.get(request.get('uri')).get('header') + '.xxx.com'}]
        request['origin']['custom']['domainName'] = MSA_ENDPOINT
        request['origin']['custom']['port'] = 80
        request['origin']['custom']['protocol'] = 'http'

    logger.info('Output Request: {}'.format(request))
    
    return request