import testEnv
from testEnv import MockCommand, MockRegion
import unittest

class TestUtils(unittest.TestCase):
  
  def setUp(self):
    self.command = MockCommand()
  
  def tearDown(self):
    self.command = None

  def testWriteLink(self):
    self.command.view.text = "foo bar baz"
    self.command.region = MockRegion(4, 7)
    anchorman.Utils.writeLink(self.command, "(URL)", "(TITLE)")
    self.assertEquals("foo <a href=\"(URL)\">(TITLE)</a> baz", self.command.view.text)
    
if __name__ == "__main__":
  testEnv.init()
  import anchorman
  unittest.main()