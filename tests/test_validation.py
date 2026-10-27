import unittest
from unittest.mock import patch
from subprocess import CompletedProcess
from netlab.validation import test_server_health, test_firewall_rules


class TestValidation(unittest.TestCase):

    @patch("netlab.validation.subprocess.run")
    def test_server_health_success(self, mock_run):
        mock_run.return_value = CompletedProcess(
            args=[],
            returncode=0,
            stdout="200",
            stderr=""
        )

        result = test_server_health()

        self.assertTrue(result.passed)
        self.assertEqual(result.actual, "HTTP 200")
        mock_run.assert_called_once()

    @patch("netlab.validation.subprocess.run")
    def test_server_health_timeout(self, mock_run):
        mock_run.return_value = CompletedProcess(
            args=[],
            returncode=28,
            stdout="000",
            stderr="Connection timed out"
        )

        result = test_server_health()

        self.assertFalse(result.passed)
        self.assertEqual(result.actual, "HTTP 000")

    @patch("netlab.validation.subprocess.run")
    def test_firewall_missing_rules(self, mock_run):
        mock_run.return_value = CompletedProcess(
            args=[],
            returncode=0,
            stdout="table inet filter { }",
            stderr=""
        )

        result = test_firewall_rules()

        self.assertFalse(result.passed)


if __name__ == "__main__":
    unittest.main()
