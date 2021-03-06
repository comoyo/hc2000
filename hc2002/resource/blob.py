import boto.exception
import hc2002.aws.s3

def _setup_s3_connection():
    global s3
    s3 = hc2002.aws.s3.get_connection()

def _split_url(url):
    if not url.startswith('s3://'):
        raise Exception('Unsupported URL: %s' % url)

    bucket, _, key = url[5:].partition('/')
    return bucket, key

def _get_key(url):
    bucket, key = _split_url(url)
    return s3.get_bucket(bucket, validate=False).new_key(key)

def head(url):
    _setup_s3_connection()

    bucket, key = _split_url(url)
    s3_bucket = s3.get_bucket(bucket, validate=False)
    if s3_bucket and s3_bucket.get_key(key):
        return True
    return False

def put(url, blob, replace=True):
    _setup_s3_connection()

    key = _get_key(url)
    if isinstance(blob, basestring):
        return key.set_contents_from_string(blob, replace=replace)
    else:
        return key.set_contents_from_file(blob, replace=replace)

def get(url, blob=None):
    _setup_s3_connection()

    key = _get_key(url)
    try:
        if blob is None:
            return key.get_contents_as_string()
        else:
            return key.get_contents_to_file(blob)
    except boto.exception.BotoServerError as err:
        if err.status != 404:
            raise

    return None

def list(url):
    _setup_s3_connection()

    bucket, key = _split_url(url)
    if not bucket:
        return [ bucket.name.encode('utf-8')
                for bucket in s3.get_all_buckets() ]
    else:
        bucket = s3.get_bucket(bucket, validate=False)
        return [ ('s3://%s/%s' % (key.bucket.name, key.name)).encode('utf-8')
                for key in bucket.get_all_keys(prefix=key) ]
