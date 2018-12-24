import argparse
from os import name as _platform
from os import stat, utime
from os.path import dirname, isfile, join
from subprocess import PIPE, CalledProcessError, run

from chardet import detect
from cueparser import CueSheet

RESERVED_NAME = {
    'AUX',
    'CON',
    *{'COM%s' % i
      for i in range(1, 10)},
    'NUL',
    *{'LPT%s' % i
      for i in range(1, 10)},
    'PRN',
} if _platform == 'nt' else {}


def bytes2str(bytesstring):
    codec = detect(bytesstring)['encoding']
    return str(bytesstring, encoding=codec)


class CueCut:
    def __init__(self,
                 cuepath,
                 filepath=None,
                 prefer_codec='flac',
                 ffmpeg_bin='ffmpeg'):
        self.prefer_codec = prefer_codec
        self.ffmpeg_bin = ffmpeg_bin

        with open(cuepath, 'rb') as fp:
            self.cuesheet = CueSheet()
            self.cuesheet.setData(bytes2str(fp.read()))
            self.cuesheet.setOutputFormat(
                '%performer% - %title%\n%file%\n%tracks%',
                '%performer% - %title%',
            )
            self.cuesheet.parse()
            self.n_tracks = len(self.cuesheet.tracks)
            print(self.cuesheet.output())

        if filepath and isfile(filepath):
            self.filepath = filepath
        else:
            if isfile(self.cuesheet.file):
                self.filepath = self.cuesheet.file
            else:
                filepath = join(dirname(cuepath), self.cuesheet.file)
                if isfile(filepath):
                    self.filepath = filepath
                else:
                    raise IOError("Can't not find file: %s" % self.filepath)

        self.amtime = (stat(self.filepath).st_atime,
                       stat(self.filepath).st_mtime)

    @staticmethod
    def vaildname(name):
        if name in RESERVED_NAME:
            print('Unable to resloving name issue: It`s a reserved name %s' %
                  name)

        vaild = "".join(i if i not in r"\/:*?<>|" else " " for i in name)
        if vaild != name:
            print(
                'Invaild name resloved.',
                '      "%s"' % name,
                '  --> "%s"' % vaild,
                sep='\n',
                end='\n\n')
        return vaild

    @staticmethod
    def offset(indextime):
        tick = [int(j) for j in indextime.split(':')]
        return tick[0] * 60 + tick[1] + tick[2] * 1e-2

    @staticmethod
    def time_plus_deltatime(start, delta):
        if delta is None:
            return CueCut.offset('99:59:99')
        return CueCut.offset(start) + delta.seconds + delta.microseconds * 1e-6

    def _output(self, trackidx):
        performer = self.cuesheet.tracks[trackidx].performer
        title = self.cuesheet.tracks[trackidx].title
        return join(
            dirname(self.filepath),
            '.'.join([
                self.vaildname(' - '.join(
                    filter(lambda x: x is not None, [performer, title]))),
                self.prefer_codec
            ]),
        )

    def cut(self):
        for idx in range(self.n_tracks):
            self._cut(idx)

    def _cut(self, trackidx):
        track = self.cuesheet.tracks[trackidx]
        output = self._output(trackidx)
        commandline = [
            self.ffmpeg_bin,
            '-hide_banner',  # I reckon you would not want to see the BANNER
            '-y',  # CAUTION: Overwrite by default
            '-i',  # def: Input Stream
            self.filepath,
            '-map_metadata',  # Drop metadata if exists
            '-1',
            '-c:a',  # def: Output Stream Codec
            self.prefer_codec,
            '-ss',  # From where
            '%.2f' % self.offset(track.offset),
            '-to',  # To where
            '%.2f' % self.time_plus_deltatime(track.offset, track.duration),
            '-loglevel',  # Disable massive log record
            'fatal',
            '-metadata',  # def: Metas
            'title=%s' % track.title,
            '-metadata',
            'artist=%s' % (track.songwriter or track.performer, ),
            '-metadata',
            'performer=%s' % track.performer,
            '-metadata',
            'album=%s' % self.cuesheet.title,
            '-metadata',
            'track=%s/%s' % (track.number, self.n_tracks),
            '-metadata',
            'album_artist=%s' % self.cuesheet.performer,
            '-metadata',
            'composer=%s' % self.cuesheet.performer,
            '-write_id3v1',  # Enable ID3V1
            '1',
            '-vn',
            # Disable video stream
            # For some audio file with album image bulit in,
            # may cause the issue
            # `No packets were sent for some of the attached pictures.`
            # which leads to loss of the duration of output
            output,  # def: Output Stream
        ]
        run(commandline, check=True, stderr=PIPE)
        utime(output, self.amtime)
        return 0


def entrypoint():
    parser = argparse.ArgumentParser(
        description='Cut your CD Image into slices.')
    parser.add_argument(
        'cuepath',
        metavar='CUEFILE',
        type=str,
        help='Cue file path',
    )
    parser.add_argument(
        '-c',
        dest='codec',
        action='store',
        default='flac',
        help='Preferred audio codec (Default: flac)',
    )
    parser.add_argument(
        '-f',
        dest='AUDIOFILE',
        action='store',
        default=None,
        help='Audio file overriding that defined in cue file (Default: None)',
    )

    args = parser.parse_args()
    try:
        CueCut(args.cuepath, prefer_codec=args.codec).cut()
    except FileNotFoundError:
        print('Can not find %s.' % args.cuepath)
    except KeyboardInterrupt:
        print('User interupted.')
    except CalledProcessError as err:
        print('FFmpeg reporting an error: ', bytes2str(err.stderr))


if __name__ == "__main__":
    entrypoint()
