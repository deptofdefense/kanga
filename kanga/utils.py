# =================================================================
#
# Work of the U.S. Department of Defense, Defense Digital Service.
# Released as open source under the MIT License.  See LICENSE file.
#
# =================================================================

import boto3
import botocore
import csv
import re
from kanga import settings
import pandas as pd
from io import StringIO


def flatten(s):
    if s == []:
        return s
    if isinstance(s[0], list):
        return flatten(s[0]) + flatten(s[1:])
    return s[:1] + flatten(s[1:])


def format_string(obj):
    if isinstance(obj, str):
        return obj
    if isinstance(obj, float):
        return "{}".format(int(obj))
    return "{}".format(obj)


def split_string(s):
    if "," in s:
        return [x.strip() for x in s.split(",")]
    elif ";" in s:
        return [x.strip() for x in s.split(";")]
    elif "&" in s:
        return [x.strip() for x in s.split("&")]
    elif "|" in s:
        return [x.strip() for x in s.split("|")]
    elif "//" in s:
        return [x.strip() for x in s.split("//")]
    elif "/" in s:
        return [x.strip() for x in s.split("/")]
    elif "#" in s:
        return [x.strip() for x in s.split("#")]
    elif "_" in s:
        return [x.strip() for x in s.split("_")]
    else:
        slc = s.lower()
        if "and" in slc:
            return [x.strip() for x in slc.split("and")]
        elif "or" in slc:
            return [x.strip() for x in slc.split("or")]
        elif " " in slc and len(slc) > 18:
            # only split if length is greater than 9
            return [x.strip() for x in slc.split(" ")]
    return [s]


def clean_phone_number(s):
    # Only return digits and a "+"
    return re.sub("[^0-9+]", "", s)


def normalize_phone_number(s):
    slc = s.lower()

    if "usanumber" in slc:
        # replace "usanumber" with +1
        slc = slc.replace("usanumber", "+1")
    elif "secondnum" in slc:
        # drop secondnum
        slc = slc.replace("secondnum", "")
    else:
        slc = clean_phone_number(slc)

    if len(slc) == 14:
        if slc.startswith("00920") or slc.startswith("oo92o"):
            # PAK Number
            return "+92{}".format(slc[5:])
        elif slc.startswith("00930") or slc.startswith("oo93o"):
            # AFG Number
            return "+93{}".format(slc[5:])
        elif slc.startswith("011"):
            # clip the international dialing prefix and noramalize remainder
            return normalize_phone_number(s[:3])
    if len(slc) == 13:
        if slc.startswith("0093") or slc.startswith("o093") or slc.startswith("oo93") or slc.startswith("0o93"):
            return "+{}".format(slc[2:])
        elif slc.startswith("+920") or slc.startswith("+92o"):
            # PAK
            return "+92{}".format(slc[4:])
        elif slc.startswith("+930") or slc.startswith("+93o"):
            # AFG
            return "+93{}".format(slc[4:])
        elif slc.startswith("001"):
            # Likely USA (clip international dialing prefix "00" and leave "1")
            return normalize_phone_number(s[2:])
        else:
            raise Exception("cannot format phone number {}".format(s))
    elif len(slc) == 12:
        if slc.startswith("+1"):
            # American Number
            return slc
        elif slc.startswith("+92") or slc.startswith("+93"):
            # PAK or AFG
            return slc
        elif slc.startswith("092") or slc.startswith("093"):
            # PAK or AFG
            return "+{}".format(slc[1:])
        elif slc.startswith("920") or slc.startswith("930"):
            # PAK or AFG
            return "+{}{}".format(slc[0:2], slc[3:])
        else:
            raise Exception("cannot format phone number {}".format(s))
    elif len(slc) == 11:
        if slc[0] == "1":
            # USA Number
            return "+{}".format(slc)
        elif slc.startswith("92") or slc.startswith("93"):
            # PAK or AFG Number
            return "+{}".format(slc)
        else:
            raise Exception("cannot format phone number {}".format(s))
    elif len(slc) == 10:
        if slc[0] == "+":
            # Assume AFG number
            return "+93{}".format(slc[1:])
        elif slc[0] == "0" or slc[0] == "o":
            # Assume AFG number
            return "+93{}".format(slc[1:])
        else:
            # USA Number
            return "+1{}".format(slc)
    elif len(slc) == 9:
        # Assume AFG, could be PAK
        return "+{}{}".format("93", slc)
    else:
        raise Exception("cannot format phone number {}".format(s))
    return slc


def decode_data(data=None, file_format=None, sheet_name=None):
    if file_format == "excel":
        return pd.read_excel(data, sheet_name=sheet_name, parse_dates=False, dtype=str).to_dict('records')
    elif file_format == "csv":
        return csv.DictReader(StringIO(data.decode("utf-8")), delimiter=",")
    return None


class S3Mixin(object):

    def get_bucket(self):
        if not hasattr(self, 'bucket'):
            s3 = boto3.resource(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_DEFAULT_REGION
                )

            self.bucket = s3.Bucket(settings.REMOTE_FIXTURES_BUCKET_NAME)
            exists = True
            try:
                s3.meta.client.head_bucket(Bucket=settings.REMOTE_FIXTURES_BUCKET_NAME)
            except botocore.exceptions.ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == '404':
                    exists = False

        return self.bucket, exists

    def get_object(self, key, filename):

        if not hasattr(self, 's3_client'):

            if settings.AWS_SECRET_ACCESS_KEY and (len(settings.AWS_SECRET_ACCESS_KEY) > 0):
                print(f"settings.REMOTE_FIXTURES_BUCKET_NAME: {settings.REMOTE_FIXTURES_BUCKET_NAME}")
                print(f"settings.AWS_DEFAULT_REGION: {settings.AWS_DEFAULT_REGION}")
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    aws_session_token=settings.AWS_SESSION_TOKEN,
                    )

            else:
                # ec2 instance boto3 doesn't need creds passed in
                self.s3_client = boto3.client('s3')

        self.s3_client.download_file(
            Bucket=settings.REMOTE_FIXTURES_BUCKET_NAME,
            Key=key,
            Filename=filename)
