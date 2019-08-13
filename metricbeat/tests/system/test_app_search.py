import metricbeat
import unittest

class Test(metricbeat.BaseTest):
    COMPOSE_SERVICES = ['elasticsearch', 'app_search']
    COMPOSE_TIMEOUT = 600

    @unittest.skipUnless(metricbeat.INTEGRATION_TESTS, "integration test")
    def test_status(self):
        self.render_config_template(modules=[{
            "name": "app_search",
            "metricsets": ["stats"],
            "hosts": ["localhost:3002"],
            "period": "5s"
        }])
        proc = self.start_beat()
        self.wait_until(lambda: self.output_lines() > 0)
        proc.check_kill_and_wait()
        self.assert_no_logged_warnings()

        output = self.read_output_json()
        self.assertEqual(len(output), 1)
        evt = output[0]
        self.assert_fields_are_documented(evt)

        self.assertIn("app_search", evt)
        self.assertIn("stats", evt["app_search"])

        app_search_stats = evt["app_search"]["stats"]
        self.assertIn("jvm", app_search_stats)
        self.assertIn("queues", app_search_stats)
