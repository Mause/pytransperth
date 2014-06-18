import gzip
import json
from hashlib import md5
from concurrent import futures
from operator import itemgetter

import requests

from .utils import prepare_url

BASE = 'http://journeyplanner.silverrailtech.com/JourneyPlannerService/V2'


class InvalidReferenceData(Exception):
    pass


def _load_single_file(url):
    r = requests.get(url['url'])
    data = gzip.decompress(r.content)

    checksum = md5(data).hexdigest()
    if checksum != url['checksum']:
        raise InvalidReferenceData('{} != {}'.format(
            checksum,
            url['checksum']
        ))

    return json.loads(data.decode())


def load_reference_data(api_key, dataset='PerthRestricted'):
    params = {
        'dataset': dataset
    }

    url = BASE + '/rest/Datasets/:dataset/AvailableReferenceData'
    url = prepare_url(url, params)

    files = requests.get(
        url,
        params={
            'ApiKey': api_key,
            'format': 'json'
        }
    )

    urls = (
        {
            'checksum': ref_data['JsonChecksum'],
            'url': ref_data['JsonZippedUrl']
        }
        for ref_data in files.json()['AvailableReferenceDataList']
    )

    data = futures.ThreadPoolExecutor(5).map(_load_single_file, urls)

    reference_data = {}
    for json_data in data:
        reference_data.update(json_data)

    return reference_data


def get_stop_numbers(api_key):
    """
    Returns a rather large generator; be careful now :P
    """

    ref = load_reference_data(api_key)

    stopdata = ref['TransitStopReferenceData']
    codes = map(itemgetter('Code'), stopdata)
    codes = filter(bool, codes)

    return codes


if __name__ == '__main__':
    from os.path import dirname, join
    filename = join(dirname(__file__), '..', '..', 'auth.json')

    with open(filename) as fh:
        api_key = json.load(fh)['api_key']

    output = load_reference_data(api_key)

    import IPython
    IPython.embed()
