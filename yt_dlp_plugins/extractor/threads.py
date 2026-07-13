"""Threads (threads.net / threads.com) extractor plugin for yt-dlp.

Threads is not supported by mainline yt-dlp. Post pages are now empty JS
shells with no server-rendered post data, so this extractor talks to the
same GraphQL endpoint the web app uses:

1. GET the post page - yields a csrftoken cookie and an LSD token
2. Derive the numeric post ID from the URL shortcode (base64url, the same
   scheme Instagram media IDs use)
3. POST /api/graphql (BarcelonaPostPageContentQuery) - returns the post
   JSON including video_versions CDN URLs

Works anonymously for public posts (verified 2026-07); login-walled posts
need browser cookies (Settings > Instagram/Threads login).

yt-dlp auto-discovers this file because it lives in a ``yt_dlp_plugins``
package on sys.path (in development that's the script directory; in the
packaged exe it's bundled via build.py).
"""

import json

from yt_dlp.extractor.common import InfoExtractor
from yt_dlp.utils import (
    ExtractorError,
    strftime_or_none,
    urlencode_postdata,
)
from yt_dlp.utils.traversal import traverse_obj

# Instagram/Threads shortcode alphabet: a shortcode is the media's numeric
# ID in base64url
_SHORTCODE_ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'


class ThreadsIE(InfoExtractor):
    IE_NAME = 'threads'
    _VALID_URL = r'https?://(?:www\.)?threads\.(?:net|com)/(?P<uploader>[^/?#]+)/post/(?P<id>[^/?#&]+)'

    # Relay doc_id of BarcelonaPostPageContentQuery; Meta rotates these but
    # old ones stay valid for a long time
    _GRAPHQL_DOC_ID = '25460088156920903'

    # Meta serves an empty response to yt-dlp's default User-Agent
    _UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
           '(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36')

    _TESTS = [{
        'url': 'https://www.threads.net/@tntsportsbr/post/C6cqebdCfBi',
        'info_dict': {
            'id': 'C6cqebdCfBi',
            'ext': 'mp4',
            'uploader_id': 'tntsportsbr',
        },
    }, {
        'url': 'https://www.threads.com/@felipebecari/post/C6cM_yNPHCF',
        'only_matching': True,
    }]

    @staticmethod
    def _shortcode_to_pk(shortcode):
        pk = 0
        for char in shortcode:
            index = _SHORTCODE_ALPHABET.find(char)
            if index < 0:
                raise ExtractorError(f'Invalid Threads shortcode {shortcode!r}')
            pk = pk * 64 + index
        return str(pk)

    def _real_extract(self, url):
        video_id = self._match_id(url)
        pk = self._shortcode_to_pk(video_id)

        # The page itself is an empty shell, but fetching it sets the
        # csrftoken cookie and embeds the LSD token the API requires
        webpage = self._download_webpage(
            url, video_id, headers={'User-Agent': self._UA})
        lsd = self._search_regex(
            r'"LSD",\[\],\{"token":"([^"]+)"', webpage, 'lsd token')

        response = self._download_json(
            'https://www.threads.com/api/graphql', video_id,
            note='Downloading post JSON',
            # Error responses carry an anti-JSON-hijacking prefix
            transform_source=lambda s: s.removeprefix('for (;;);'),
            data=urlencode_postdata({
                'av': '0',
                '__user': '0',
                '__a': '1',
                '__req': '1',
                'dpr': '1',
                'lsd': lsd,
                'fb_api_caller_class': 'RelayModern',
                'fb_api_req_friendly_name': 'BarcelonaPostPageContentQuery',
                'variables': json.dumps({'postID': pk}),
                'server_timestamps': 'true',
                'doc_id': self._GRAPHQL_DOC_ID,
            }),
            headers={
                'User-Agent': self._UA,
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-FB-LSD': lsd,
                'X-IG-App-ID': '238260118697367',
                'X-ASBD-ID': '129477',
                'X-FB-Friendly-Name': 'BarcelonaPostPageContentQuery',
                'Origin': 'https://www.threads.com',
                'Referer': url,
                'Accept': '*/*',
                # Meta rejects the request (error 1357055) without these
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Dest': 'empty',
            })

        if traverse_obj(response, 'error'):
            raise ExtractorError(
                'Threads API error: {}'.format(
                    traverse_obj(response, 'errorSummary') or response['error']),
                expected=True)

        formats = []
        thumbnails = []
        metadata = {'id': video_id}

        # The response carries the whole thread (post + replies); pick our post
        for node in traverse_obj(response, ('data', 'data', 'edges')) or []:
            for item in traverse_obj(node, ('node', 'thread_items')) or []:
                post = item.get('post')
                if not post or (str(post.get('pk')) != pk
                                and post.get('code') != video_id):
                    continue

                # Carousel posts carry several media items; plain posts are
                # their own single media item
                for media in post.get('carousel_media') or [post]:
                    for video in media.get('video_versions') or []:
                        if not video.get('url'):
                            continue
                        formats.append({
                            'format_id': '{}-{}'.format(
                                media.get('pk'), video.get('type')),
                            'url': video['url'],
                            'ext': 'mp4',
                            'width': media.get('original_width'),
                            'height': media.get('original_height'),
                        })

                for thumb in traverse_obj(
                        post, ('image_versions2', 'candidates')) or []:
                    if not thumb.get('url'):
                        continue
                    thumbnails.append({
                        'url': thumb['url'],
                        'width': thumb.get('width'),
                        'height': thumb.get('height'),
                    })

                username = traverse_obj(post, ('user', 'username'))
                caption = traverse_obj(post, ('caption', 'text'))
                metadata.setdefault('uploader_id', username)
                metadata.setdefault(
                    'channel_is_verified',
                    traverse_obj(post, ('user', 'is_verified')))
                if username:
                    metadata.setdefault(
                        'uploader_url', f'https://www.threads.com/@{username}')
                metadata.setdefault('timestamp', post.get('taken_at'))
                metadata.setdefault('like_count', post.get('like_count'))
                if caption:
                    metadata.setdefault('title', caption)
                    metadata.setdefault('description', caption)

        if not formats:
            self.raise_no_formats(
                'No video found in this Threads post. It may be image/text-only, '
                'deleted, or visible only when logged in - if you are logged in '
                'to Threads in your browser, configure that browser for cookies',
                expected=True)

        metadata.setdefault(
            'title', 'Threads post by {}'.format(
                metadata.get('uploader_id') or 'unknown'))
        metadata['channel'] = metadata.get('uploader_id')
        metadata['channel_url'] = metadata.get('uploader_url')
        metadata['uploader'] = metadata.get('uploader_id')
        metadata['upload_date'] = strftime_or_none(metadata.get('timestamp'))

        return {
            **metadata,
            'formats': formats,
            'thumbnails': thumbnails,
        }


class ThreadsIOSIE(InfoExtractor):
    IE_NAME = 'threads:ios'
    IE_DESC = "Threads' iOS barcelona:// URL"
    _VALID_URL = r'barcelona://media\?shortcode=(?P<id>[^/?#&]+)'
    _TESTS = [{
        'url': 'barcelona://media?shortcode=C6fDehepo5D',
        'only_matching': True,
    }]

    def _real_extract(self, url):
        video_id = self._match_id(url)
        # Threads ignores the username segment and redirects to the right
        # post, so a placeholder works
        return self.url_result(
            f'https://www.threads.com/@_/post/{video_id}', ThreadsIE, video_id)
