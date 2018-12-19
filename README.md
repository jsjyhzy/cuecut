# CueCut

Cut a CD image file by its cue file.

## Usage

### Prerequisite

There should exists an executable `ffmpeg` in `PATH`,
and the minimal Python/FFmpeg version that has been tested is 3.6.6/4.1 .

### Folder Struct

```
.
├──xxx.cue
└──yyy.zzz
```

Where `yyy.zzz` is the name defined in `xxx.cue`

### Cut it

`python cuecut.py /path/to/xxx.cue`
