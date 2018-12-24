# CueCut

Cut a CD image file by its cue file.

## Installation

```bash
pip install cuecut
```

## Usage

### 1. Prerequisite

There should exists an executable `ffmpeg` in `PATH`,
and the minimal Python/FFmpeg version that has been tested is 3.6.6/4.1 .

### 2. Folder Struct

```
.
├──xxx.cue
└──yyy.zzz
```

Where `yyy.zzz` is the name defined in `xxx.cue`

### 3. Cut it

```bash
cuecut /path/to/xxx.cue -c CodecYouLike
```