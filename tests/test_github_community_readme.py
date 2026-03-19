import unittest
import json
import sys
import os
import tempfile
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from github_community_health import local_artifacts, add_finding
from github_readme_lint import looks_like_placeholder, strip_code_fences


class TestGitHubCommunityHealth(unittest.TestCase):
    def test_local_artifacts(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            open(os.path.join(tmpdir, "README.md"), "w").close()
            open(os.path.join(tmpdir, "LICENSE"), "w").close()
            
            result = local_artifacts(tmpdir)
            
            self.assertTrue(result["README.md"])
            self.assertTrue(result["LICENSE"])
            self.assertFalse(result["CONTRIBUTING.md"])
            self.assertFalse(result["CODE_OF_CONDUCT.md"])

    def test_add_finding(self):
        findings = []
        add_finding(findings, "Warning", "Test finding", "evidence", "fix it")
        
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["severity"], "Warning")
        self.assertEqual(findings[0]["finding"], "Test finding")
        self.assertEqual(findings[0]["evidence"], "evidence")
        self.assertEqual(findings[0]["fix"], "fix it")


class TestGitHubReadmeLint(unittest.TestCase):
    def test_looks_like_placeholder_404(self):
        self.assertTrue(looks_like_placeholder("404"))
        self.assertTrue(looks_like_placeholder("404: not found"))
        self.assertTrue(looks_like_placeholder("Not Found"))
        self.assertTrue(looks_like_placeholder("404: page not found"))

    def test_looks_like_placeholder_html(self):
        self.assertTrue(looks_like_placeholder("<html>not found</html>"))

    def test_looks_like_placeholder_normal(self):
        self.assertFalse(looks_like_placeholder("This is a normal README"))
        self.assertFalse(looks_like_placeholder(""))

    def test_strip_code_fences(self):
        text = """# Title

Some text

```python
code here
```

More text

```
shell code
```

End"""
        result = strip_code_fences(text)
        self.assertNotIn("python", result)
        self.assertNotIn("code here", result)
        self.assertIn("Some text", result)
        self.assertIn("More text", result)

    def test_strip_code_fences_with_tildes(self):
        text = """# Title

~~~python
code
~~~

End"""
        result = strip_code_fences(text)
        self.assertNotIn("code", result)
        self.assertIn("Title", result)


if __name__ == "__main__":
    unittest.main()
