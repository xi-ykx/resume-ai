import os
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

os.environ.setdefault("DEEPSEEK_API_KEY", "test_api_key")

with patch("dotenv.load_dotenv", return_value=True):
    import day06


client = TestClient(day06.app)


class ResumeApiTestCase(unittest.TestCase):
    def test_empty_resume_text_returns_400(self):
        with patch("day06.ask_ai_json") as mock_ask_ai_json:
            response = client.post(
                "/polish-resume-json",
                json={
                    "job_target": "Python后端开发",
                    "resume_text": "   "
                }
            )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["detail"],
            "简历内容不能为空，请填写原始简历内容。"
        )
        mock_ask_ai_json.assert_not_called()

    def test_too_long_resume_text_returns_422(self):
        too_long_resume = "a" * (day06.MAX_RESUME_TEXT_LENGTH + 1)

        with patch("day06.ask_ai_json") as mock_ask_ai_json:
            response = client.post(
                "/polish-resume-json",
                json={
                    "job_target": "Python后端开发",
                    "resume_text": too_long_resume
                }
            )

        self.assertEqual(response.status_code, 422)
        self.assertIn("detail", response.json())
        mock_ask_ai_json.assert_not_called()

    def test_normal_resume_request_returns_expected_format(self):
        fake_ai_response = day06.ResumeJsonResponse(
            problem_analysis=["Python", "FastAPI"],
            optimized_resume="优化后的简历内容",
            reasons=["表达更具体", "更贴近目标岗位"]
        )

        with (
            patch("day06.ask_ai_json", return_value=fake_ai_response),
            patch("day06.save_history_record") as mock_save_history_record
        ):
            response = client.post(
                "/polish-resume-json",
                json={
                    "job_target": "Python后端开发",
                    "resume_text": "我做过 FastAPI 项目，负责接口开发。"
                }
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(
            set(data.keys()),
            {"problem_analysis", "optimized_resume", "reasons"}
        )
        self.assertIsInstance(data["problem_analysis"], list)
        self.assertIsInstance(data["optimized_resume"], str)
        self.assertIsInstance(data["reasons"], list)
        self.assertEqual(data["optimized_resume"], "优化后的简历内容")
        mock_save_history_record.assert_called_once()


if __name__ == "__main__":
    unittest.main()
