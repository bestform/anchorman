import sublime
import sublime_plugin
import json
from urllib2 import urlopen, quote, Request
import re

class AnchormanCommand(sublime_plugin.TextCommand):
  def run(self, edit, multiple):
    self.items = []
    self.originalQuery = ""

    s = sublime.load_settings("anchorman.sublime-settings")
    bingAppID = s.get('bing_api_key')
    if not bingAppID or bingAppID == "":
      sublime.error_message("Please provide a 'bing_api_key' in an anchorman.sublime-settings file in your user dir")
      return
    count = 1
    if multiple:
      count = s.get('multiple_count')
    
    baseurl = "http://api.bing.net/json.aspx?AppId="+bingAppID+"&Version=2.2&Sources=web&Web.Count="+str(count)+"&JsonType=raw&Query="

    # for now we only work with the first selected region. multiple region support might come later, if i feel like it
    self.region = self.view.sel()[0]
    if self.region.size() == 0:
      # nothing selected? get off my lawn!
      return
    
    self.originalQuery = self.view.substr(self.region)
    query = Utils.cleanQuery(self.originalQuery)
    url = baseurl + quote(query.encode("utf-8"))
    result = urlopen(url).read()
    # no error handling at this point. we trust microsoft. i for one welcome our new api overlords.
    jsonresult = json.loads(result)
    results = jsonresult["SearchResponse"]["Web"]["Results"]
    if len(results) == 0:
      return
    if not multiple:
      resulturl = results[0]["Url"]
      Utils.writeLink(self, resulturl, self.originalQuery)
      return
    for i in range(0, min(len(results), count)):
      self.items.append([results[i]["Title"], results[i]["Url"]])
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