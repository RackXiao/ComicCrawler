#! python3

"""this is exh module for comiccrawler, support exhentai.org, g.e-hentai.org

"""

import re

from html import unescape
from urllib.parse import urljoin
from configparser import ConfigParser

from ..core import Episode
from ..error import PauseDownloadError

cookie = {}
domain = ["exhentai.org", "g.e-hentai.org"]
name = "e紳士"
noepfolder = True
rest = 5
config = {
	"ipb_member_id": "請輸入Cookie中的ipb_member_id",
	"ipb_pass_hash": "請輸入Cookie中的ipb_pass_hash",
	"original": "false"
}

class BandwidthLimitError(Exception): pass

def get_boolean(s):
	return ConfigParser.BOOLEAN_STATES.get(s.lower())

def load_config():
	cookie["ipb_member_id"] = config["ipb_member_id"]
	cookie["ipb_pass_hash"] = config["ipb_pass_hash"]

def get_title(html, url):
	t = re.findall("<h1 id=\"g(j|n)\">(.+?)</h1>", html)
	t = t[-1][1]

	return unescape(t)

def get_episodes(html, url):
	url = re.search(r'href="([^\"]+?/s/\w+/\w+-1)"', html).group(1)
	e = Episode("image", url)
	return [e]

nl = ""
def get_images(html, url):
	global nl
	nl = re.search("nl\('([^)]+)'\)", html).group(1)
	
	image = re.search("<img id=\"img\" src=\"(.+?)\"", html)
	image = unescape(image.group(1))
	# bandwith limit
	if re.search("509s?\.gif", image) or re.search("403s?\.gif", image):
		# pause the download since retry doesn't help but increase view limit.
		raise PauseDownloadError("Bandwidth limit exceeded!")

	if get_boolean(config["original"]):
		match = re.search(r'href="(http://exhentai\.org/fullimg\.php[^"]+)', html)
		if match:
			return unescape(match.group(1))

	return image

def errorhandler(er, crawler):
	global nl
	url = urljoin(crawler.ep.current_url, "?nl=" + nl)
	if crawler.ep.current_url == url:
		crawler.ep.current_url = url.split("?")[0]
	else:
		crawler.ep.current_url = url
	crawler.html = None

def get_next_page(html, url):
	match = re.search('id="next"[^>]+?href="([^"]+)', html)
	if match:
		match = match.group(1)
		if match not in url:
			return match
