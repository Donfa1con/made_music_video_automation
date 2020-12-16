# -*- coding: utf-8 -*-

RABBIT_CONFIG = {
    'host': 'rabbitmq',
    'tgbot': {
        'to_queue': 'quality'
    },
    'quality': {
        'from_queue': 'quality',
        'to_queue': 'highlights'
    },
    'highlights': {
        'from_queue': 'highlights',
        'to_queue': 'music_recommendation'
    },
    'music_recommendation': {
        'from_queue': 'music_recommendation',
        'to_queue': 'video_audio_compose'
    },
    'video_audio_compose': {
        'from_queue': 'video_audio_compose'
    },
    'heartbeat': 0,
}

RESULT_VIDEO_PARAMS = {
    'size': (1280, 720),  # w, h
    'fps': 30.0,
    'format': {
        'fourcc': 'mp4v',
        'ext': 'mp4'
    }
}

# https://en.wikipedia.org/wiki/Video_file_format
VIDEO_FORMATS = {'.webm', '.mkv', '.flv', '.vob', '.ogv', '.ogg', '.drc', '.gif', '.gifv', '.mng', '.avi', '.mts',
                 '.m2ts', '.ts', '.mov', '.qt', '.wmv', '.yuv', '.rm', '.rmvb', '.viv', '.asf', '.amv', '.mp4', '.m4p',
                 '.m4v', '.mpg', '.mp2', '.mpeg', '.mpe', '.mpv', '.m2v', '.m4v', '.svi', '.3gp', '.3g2', '.mxf',
                 '.roq', '.nsv', '.f4v', '.f4p', '.f4a', '.f4b'}

IMAGE_FORMATS = {'.jpeg', 'jpg', '.png', '.webp'}

# https://en.wikipedia.org/wiki/Audio_file_format
AUDIO_FORMATS = {'.aa', '.aac', '.aax', '.act', '.aiff', '.alac', '.amr', '.ape', '.au', '.awb', '.dct', '.dss', '.dvf',
                 '.flac', '.gsm', '.iklax', '.ivs', '.m4a', '.m4b', '.m4p', '.mmf', '.mp3', '.mpc', '.msv', '.nmf',
                 '.ogg', '.oga', '.mogg', '.opus', '.org', '.ra', '.rm', '.raw', '.rf64', '.sln', '.tta', '.voc',
                 '.vox', '.wav', '.wma', '.wv', '.webm', '.8svx', '.cda'}

USER_CONFIG_NAME = 'settings.json'

DEFAULT_SETTINGS = {
    'stages': {
        'quality': "✅",
        'highlights': "✅",
        'music_recommendation': "✅",
        'visbeat': "✅",
    },
}
