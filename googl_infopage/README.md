# googl-infopage

The [Google URL shortener](https://goo.gl) shows the information on the webpage

> All goo.gl URLs and click analytics are public and can be accessed by anyone

And we know the URL generate by Google URL shortener follows the format of `https://goo.gl/XXX`, and the click analytics information page follows the format of `https://goo.gl/info/XXX`.

Click analytics info page is a JavaScript-rendered page, so I build up the crawler by selenium with some simple usage.

## Usage

```
usage: main.py [-h] [--csv CSV] [--url URL [URL ...]]

interactive graph cut for moth image

optional arguments:
  -h, --help           show this help message and exit
  --csv CSV            given a csv file to process
  --url URL [URL ...]  given bunch of url to process
```

Input csv file should contain one `goo.gl/XXX` URL per line.
