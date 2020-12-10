import os
import shutil
import time

import visbeat as vb

# length music-video beats, duration of outout, 16 beats ~ 8 sec
DEFAULT_NBEATS = 40
DEFAULT_MAX_HEIGHT = 720
SYNCH_VIDEO_BEAT = 0
SYNCH_AUDIO_BEAT = 0


class SourceMedia:
    def __init__(self, path, name=None, **kwargs):
        self.path = path
        self._name = name
        self.__dict__.update(**kwargs)

    @property
    def name(self):
        if self._name is not None:
            return self._name
        else:
            return os.path.splitext(os.path.basename(self.path))[0]


def dancify(source_video_path, source_audio_path, user_id):
    vb.SetAssetsDir(os.environ.get('VISBEAT_DATA'))
    output_path = os.path.splitext(source_video_path)
    output_path = '{0}_music{1}'.format(output_path[0], output_path[1])
    visbit_video_name = 'video_to_warp_{0}_{1}'.format(user_id, int(time.time()))
    video_to_warp = SourceMedia(path=source_video_path, name=visbit_video_name)
    vb.LoadVideo(name=video_to_warp.name)
    video = vb.PullVideo(name=video_to_warp.name, source_location=video_to_warp.path, max_height=DEFAULT_MAX_HEIGHT)
    audio = vb.Audio(source_audio_path)
    vb.Dancify(source_video=video, target=audio, synch_video_beat=SYNCH_VIDEO_BEAT, synch_audio_beat=SYNCH_AUDIO_BEAT,
               force_recompute=True, warp_type='quad', nbeats=DEFAULT_NBEATS, output_path=output_path)
    shutil.rmtree(os.path.join(os.environ.get('VISBEAT_DATA'), 'VideoSources', visbit_video_name))
    return output_path


def update_logo(logo):
    dst = 'VisBeatWatermark.png'
    assets = '/usr/local/lib/python2.7/site-packages/visbeat/_assets/images/'
    src = logo + '.png'
    shutil.copyfile(assets + src, assets + dst)
