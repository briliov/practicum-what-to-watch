import json

import requests

from . import app

DROPBOX_TOKEN = app.config['DROPBOX_TOKEN']
AUTH_HEADER = f'Bearer {DROPBOX_TOKEN}'
UPLOAD_LINK = 'https://content.dropboxapi.com/2/files/upload'
SHARING_LINK = (
    'https://api.dropboxapi.com/2/' 'sharing/create_shared_link_with_settings'
)


def upload_files_to_dropbox(images: list) -> list[str]:
    urls = []
    if images is not None:
        for image in images:
            dropbox_args = json.dumps(
                {'autorename': True, 'path': f'/{image.filename}'},
            )
            response = requests.post(
                UPLOAD_LINK,
                headers={
                    'Authorization': AUTH_HEADER,
                    'Content-Type': 'application/octet-stream',
                    'Dropbox-API-arg': dropbox_args,
                },
                data=image.read(),
            )
            path = response.json()['path_lower']

            response = requests.post(
                SHARING_LINK,
                headers={
                    'Authorization': AUTH_HEADER,
                    'Content-Type': 'application/json',
                },
                json={'path': path},
            )
            data = response.json()

            if 'url' not in data:
                data = data['error']['shared_link_already_exists']['metadata']

            url = data['url']
            url = url.replace('&dl=0', '&raw=1')
            urls.append(url)
        return urls
