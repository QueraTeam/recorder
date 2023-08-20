import os
import sys
import base64
import time
import requests


class ArvanVODConfigs:
    api_key = sys.argv[1]
    arvan_vod_url = sys.argv[2]
    channel_key = sys.argv[3]
    post_request_new_upload_file = f"{arvan_vod_url}/channels/{channel_key}/files"


class ArvanVODBackend:
    def __init__(self):
        self.offset = 0
        self.url = ""
        self.uuid = ""

    def get_tus_headers(self):
        api_key = ArvanVODConfigs.api_key
        headers = {
            "tus-resumable": "1.0.0",
            "Authorization": f"{api_key}",
            "Accept-Language": "en",
        }
        return headers

    def create_url(self, file_identifier, file_type, file_size):
        encoded_filename = base64.b64encode(file_identifier.encode()).decode()
        encoded_file_type = base64.b64encode(file_type.encode()).decode()

        headers = self.get_tus_headers()
        headers.update(
            {
                "upload-length": str(file_size),
                "upload-metadata": "filename {},filetype {}".format(
                    encoded_filename, encoded_file_type
                ),
            }
        )

        resp = requests.post(ArvanVODConfigs.post_request_new_upload_file, headers=headers)
        if resp.status_code not in [201]:
            raise Exception(resp.json())

        location_url = resp.headers.get("location")
        self.url = location_url
        return location_url

    def handle_upload(self, file_identifier, file_type, file_size, file):
        total_bytes_uploaded = 0
        offset = self.offset
        url = self.create_url(file_identifier, file_type, file_size)
        while True:
            data = file.read(1 * 1024 * 1024)
            if not data:
                break
            if total_bytes_uploaded + len(data) > int(offset):
                successful, should_retry = self.upload_chunk(url, data)
                if not successful:
                    if should_retry:
                        return "Chunk Failed! Upload this chunk again.", 204
                    else:
                        return "This file cannot be uploaded now!", 404
            total_bytes_uploaded += len(data)
            offset = self.offset
        return "Chunk Uploaded Successfully", 200

    def upload_chunk(self, url, data):
        if url is None:
            return False
        max_retry = 5
        retried = 0
        headers = self.get_tus_headers()
        headers.update({"upload-offset": str(self.offset)})
        should_retry = True
        while retried < max_retry:
            try:
                resp = requests.patch(url, data, headers=headers)
                upload_offset = resp.headers.get("upload-offset")
                if "upload-offset" not in resp.headers:
                    raise Exception("invalid upload-offset. Try again.")
                self.offset = upload_offset
                should_retry = False
                return True, should_retry
            except Exception as e:
                print(e)
                retried += 1
                time.sleep(1)
        return False, should_retry

    def get_file_uuid(self):
        url = self.url
        arvan_file_uuid = url.split("/")[-1]
        return arvan_file_uuid

    def after_upload(self, file_name):
        api_key = ArvanVODConfigs.api_key
        arvan_vod_url = ArvanVODConfigs.arvan_vod_url
        channel_key = ArvanVODConfigs.channel_key

        headers = {
            "Authorization": f"{api_key}",
            "Accept-Language": "en",
        }
        arvan_file_uuid = self.get_file_uuid()
        data = {
            "convert_info": [],
            "convert_mode": "auto",
            "title": file_name,
            "description": file_name,
            "file_id": arvan_file_uuid,
            "parallel_convert": False,
            "profile_id": None,
            "video_url": None,
        }
        resp = requests.post(f"{arvan_vod_url}/channels/{channel_key}/videos", json=data, headers=headers)
        result = resp.json()
        arvan_video_uuid = result["data"]["id"]
        self.uuid = arvan_video_uuid

    def send_video_uuid(self):
        try:
            callback_url = sys.argv[5]
            requests.put(callback_url, json={"video_uuid": self.uuid})
        except Exception as e:
            print(e)

    def check_file_is_ready(self, uuid):
        api_key = ArvanVODConfigs.api_key
        arvan_vod_url = ArvanVODConfigs.arvan_vod_url
        headers = {
            "Authorization": f"{api_key}",
            "Accept-Language": "en",
        }
        resp = requests.get(f"{arvan_vod_url}/videos/{uuid}", headers=headers)
        if resp.status_code == 200:
            result = resp.json()
            data = result.get("data", {})
            status = data.get("status")
            print(status)


def run():
    with open(sys.argv[4], "rb") as input_file:
        print("Starting upload...")
        file_size = os.fstat(input_file.fileno()).st_size
        file_name = os.path.basename(input_file.name)
        arvan = ArvanVODBackend()
        res, status = arvan.handle_upload(file_name, "video/mp4", file_size, input_file)
        if status == 200:
            arvan.after_upload(file_name)
            arvan.send_video_uuid()
        print(res, status)


run()
