import re
import os.path
import fnmatch
import os

cdir = r'D:\files00\The Big Bang\Season 2'

files = os.listdir(cdir)

srtpattern = r'.*?\dx?(\d+).*?'

subtitles = dict()
movies = dict()

for fname in files:
    m = re.match(srtpattern, fname)
    if m:
        episode = m.group(1)
        if fnmatch.fnmatch(fname, '*.srt'):
            subtitles[episode] = fname 
        else:
            movies[episode] = fname 

for episode in movies:
    movie = movies[episode]
    title = os.path.splitext(movie)[0]
    print(subtitles[episode], '->>', title+'.srt')
    os.rename(os.path.join(cdir, subtitles[episode]), os.path.join(cdir, title+'.srt'))
