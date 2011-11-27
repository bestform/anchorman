class MockSel(object):
  
  def clear(self):
    pass

  def add(self, region):
    pass

class MockCommand(object):
  
  def __init__(self):
    self.view = MockView()
    self.region = MockRegion(0,0)
    
class MockView(object):
  
  def __init__(self):
    self.editing = False
    self.selection = MockSel()
    self.text = "foo bar baz"

  def begin_edit(self):
    self.editing = True

  def end_edit(self, edit):
    self.editing = False

  def sel(self):
    return self.selection
  
  def sel_clear(self):
    pass

  def sel_add(self, region):
    pass

  def replace(self, edit, region, text):
    before = self.text[:region.begin()]
    after = self.text[region.end():]
    self.text = before+text+after

class MockRegion(object):

  def __init__(self, start, end):
    self.start = start
    self.endpoint = end
  
  def begin(self):
    return self.start
  
  def end(self):
    return self.endpoint

def init():
  import types
  import sys
  sys.modules["sublime"] = types.ModuleType("sublime")
  sys.modules["sublime_plugin"] = types.ModuleType("sublime_plugin")
  import sublime, sublime_plugin
  sublime_plugin.TextCommand = MockCommand
  sublime.Region = MockRegion