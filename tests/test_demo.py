import unittest

from ai_mvp.demo import answer_demo, load_demo_data


class DemoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = load_demo_data()

    def test_total(self):
        _, result, _, chart = answer_demo("Qual foi o total?", self.df)
        self.assertEqual(int(result.iloc[0, 0]), 2_896_345)
        self.assertEqual(chart, "metric")

    def test_monthly(self):
        _, result, _, chart = answer_demo("Mostre a evolução mensal", self.df)
        self.assertEqual(len(result), 12)
        self.assertEqual(chart, "line")

    def test_ranking(self):
        _, result, _, chart = answer_demo("Quais os 5 municípios com mais internações?", self.df)
        self.assertEqual(len(result), 5)
        self.assertEqual(chart, "bar")


if __name__ == "__main__":
    unittest.main()
