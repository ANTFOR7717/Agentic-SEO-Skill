import os
import sys
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))

from github.github_api import (
    get_token,
    gh_available,
    gh_auth_details,
    auth_context,
    normalize_repo_slug,
    parse_repo_slug,
    _build_url,
    _headers,
)


class TestGitHubAPI(unittest.TestCase):
    def test_get_token_from_env(self):
        with patch.dict(os.environ, {"GITHUB_TOKEN": "test-token-123"}):
            token = get_token()
            self.assertEqual(token, "test-token-123")

    def test_get_token_from_gh_env(self):
        with patch.dict(os.environ, {"GH_TOKEN": "gh-token-456"}, clear=True):
            token = get_token()
            self.assertEqual(token, "gh-token-456")

    def test_get_token_cli_override(self):
        with patch.dict(os.environ, {"GITHUB_TOKEN": "env-token"}):
            token = get_token(cli_token="cli-token")
            self.assertEqual(token, "cli-token")

    def test_get_token_empty(self):
        with patch.dict(os.environ, {}, clear=True):
            token = get_token()
            self.assertEqual(token, "")

    def test_gh_available_true(self):
        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result

            result = gh_available()
            self.assertTrue(result)

    def test_gh_available_false(self):
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError()

            result = gh_available()
            self.assertFalse(result)

    def test_gh_auth_details_not_available(self):
        with patch("github.github_api.gh_available", return_value=False):
            result = gh_auth_details(force_refresh=True)
            self.assertFalse(result["available"])
            self.assertFalse(result["authenticated"])

    def test_gh_auth_details_authenticated(self):
        with patch("github.github_api.gh_available", return_value=True):
            with patch("subprocess.run") as mock_run:
                mock_result = MagicMock()
                mock_result.stdout = "Logged in to github.com as user"
                mock_result.stderr = ""
                mock_run.return_value = mock_result

                result = gh_auth_details(force_refresh=True)
                self.assertTrue(result["available"])
                self.assertTrue(result["authenticated"])

    def test_gh_auth_details_not_authenticated(self):
        with patch("github.github_api.gh_available", return_value=True):
            with patch("subprocess.run") as mock_run:
                mock_result = MagicMock()
                mock_result.stdout = ""
                mock_result.stderr = "Not logged into github.com"
                mock_run.return_value = mock_result

                result = gh_auth_details(force_refresh=True)
                self.assertTrue(result["available"])
                self.assertFalse(result["authenticated"])

    def test_auth_context_with_token(self):
        with patch("github.github_api.gh_auth_details", return_value={"available": True, "authenticated": False}):
            result = auth_context(token="test-token")
            self.assertEqual(result["mode"], "token")
            self.assertTrue(result["token_present"])

    def test_auth_context_with_gh(self):
        with patch("github.github_api.gh_auth_details", return_value={"available": True, "authenticated": True}):
            result = auth_context(token="")
            self.assertEqual(result["mode"], "gh")

    def test_auth_context_unauthenticated(self):
        with patch("github.github_api.gh_auth_details", return_value={"available": False, "authenticated": False}):
            result = auth_context(token="")
            self.assertEqual(result["mode"], "unauthenticated")

    def test_normalize_repo_slug_https(self):
        result = normalize_repo_slug("https://github.com/owner/repo")
        self.assertEqual(result, "owner/repo")

    def test_normalize_repo_slug_ssh(self):
        result = normalize_repo_slug("git@github.com:owner/repo.git")
        self.assertEqual(result, "owner/repo")

    def test_normalize_repo_slug_short(self):
        result = normalize_repo_slug("owner/repo")
        self.assertEqual(result, "owner/repo")

    def test_normalize_repo_slug_with_git(self):
        result = normalize_repo_slug("owner/repo.git")
        self.assertEqual(result, "owner/repo")

    def test_normalize_repo_slug_empty(self):
        result = normalize_repo_slug("")
        self.assertEqual(result, "")

    def test_parse_repo_slug_valid(self):
        owner, repo = parse_repo_slug("owner/repo")
        self.assertEqual(owner, "owner")
        self.assertEqual(repo, "repo")

    def test_parse_repo_slug_invalid(self):
        from github.github_api import GitHubAPIError
        with self.assertRaises(GitHubAPIError):
            parse_repo_slug("invalid")

    def test_build_url(self):
        url = _build_url("/repos/owner/repo")
        self.assertEqual(url, "https://api.github.com/repos/owner/repo")

    def test_build_url_with_params(self):
        url = _build_url("/repos/owner/repo", {"page": 1, "per_page": 10})
        self.assertIn("page=1", url)
        self.assertIn("per_page=10", url)

    def test_build_url_full(self):
        url = _build_url("https://custom.api.com/endpoint")
        self.assertEqual(url, "https://custom.api.com/endpoint")

    def test_headers_basic(self):
        headers = _headers()
        self.assertEqual(headers["User-Agent"], "SEOSkill-GitHubAPI/1.0")
        self.assertEqual(headers["Accept"], "application/vnd.github+json")

    def test_headers_with_token(self):
        headers = _headers(token="test-token")
        self.assertEqual(headers["Authorization"], "Bearer test-token")


if __name__ == "__main__":
    unittest.main()
