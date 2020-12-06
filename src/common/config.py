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
