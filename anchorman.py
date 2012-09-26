import sublime
import sublime_plugin
import json
from urllib2 import urlopen, quote, Request
import re
from bs4 import BeautifulSoup

class AnchormanCommand(sublime_plugin.TextCommand):
  def run(self, edit, multiple):
    self.items = []
    self.originalQuery = ""
    
    baseurl = "http://duckduckgo.com/html/?q="

    # for now we only work with the first selected region. multiple region support might come later, if i feel like it
    self.region = self.view.sel()[0]
    if self.region.size() == 0:
      # nothing selected? get off my lawn!
      return
    
    self.originalQuery = self.view.substr(self.region)
    query = Utils.cleanQuery(self.originalQuery)
    url = baseurl + quote(query.encode("utf-8"))
    result = urlopen(url).read()    
    soup = BeautifulSoup(result)
    links = soup.find_all("a", "large")
    linkRegEx = re.compile("<a.*?href=\"(.*?)\"", re.I|re.M)
    parsed_links = [(link['href']," ".join([string for string in link.stripped_strings])) for link in links]

    if len(parsed_links) == 0:
      return
    if not multiple:
      resulturl = results[0][0]
      Utils.writeLink(self, resulturl, self.originalQuery)
      return
    for entry in parsed_links:
      self.items.append([entry[1], entry[0]])
    self.view.window().show_quick_panel(self.items, self.panelDone, sublime.MONOSPACE_FONT)

  def panelDone(self, index):
    if index == -1:
      return
    Utils.writeLink(self, self.items[index][1], self.originalQuery)

class AnchormanLinkCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    self.region = self.view.sel()[0]
    if self.region.size() == 0:
      # nothing selected? get off my lawn!
      return
    url = self.view.substr(self.region)
    if not url.startswith("http"):
      # no URL? oh c'mon
      return

    titleRegEx = re.compile("<title.*?>(.*?)</title>", re.I|re.M)
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.874.106 Safari/535.2"
    headers = {'User-Agent': user_agent}
    request = Request(url, None, headers)
    response = urlopen(request).read()
    match = titleRegEx.search(response)
    title = url
    if match.group(1):
      title = match.group(1)
    Utils.writeLink(self, url, title)

class Utils(object):
  @staticmethod
  def writeLink(source, resulturl, title):
    edit = source.view.begin_edit()
    start = source.region.begin()
    end = source.region.end()
    part1 = "<a href=\""+resulturl+"\">"
    part2 = title
    part3 = "</a>"
    anchor = part1+part2+part3
    markstart = start + len(part1)
    markend = markstart + len(part2)
    source.view.replace(edit, source.region, anchor)
    source.view.sel().clear()
    source.view.sel().add(sublime.Region(markstart, markend))
    source.view.end_edit(edit)
  
  @staticmethod
  def cleanQuery(query):
    query = query.replace(" ", "+")
    return query