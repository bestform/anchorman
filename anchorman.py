import sublime
import sublime_plugin
import json
from urllib import urlopen, quote

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
    query = self.cleanQuery(self.originalQuery)
    url = baseurl + quote(query.encode("utf-8"))
    result = urlopen(url).read()
    # no error handling at this point. we trust microsoft. i for one welcome our new api overlords.
    jsonresult = json.loads(result)
    results = jsonresult["SearchResponse"]["Web"]["Results"]
    if len(results) == 0:
      return
    if not multiple:
      resulturl = results[0]["Url"]
      self.writeLink(resulturl, self.originalQuery)
      return
    for i in range(0, min(len(results), count)):
      self.items.append([results[i]["Title"], results[i]["Url"]])
    self.view.window().show_quick_panel(self.items, self.panelDone, sublime.MONOSPACE_FONT)

  def panelDone(self, index):
    if index == -1:
      return
    self.writeLink(self.items[index][1], self.originalQuery)

  def writeLink(self, resulturl, originalquery):
    edit = self.view.begin_edit()
    start = self.region.begin()
    end = self.region.end()
    part1 = "<a href=\""+resulturl+"\">"
    part2 = originalquery
    part3 = "</a>"
    anchor = part1+part2+part3
    markstart = start + len(part1)
    markend = markstart + len(part2)

    self.view.replace(edit, self.region, anchor)
    self.view.sel().clear()
    self.view.sel().add(sublime.Region(markstart, markend))

    self.view.end_edit(edit)

  def cleanQuery(self, query):
    query = query.replace(" ", "+")
    return query
