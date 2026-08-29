import unittest

from ai_mvp.sql_guard import UnsafeQueryError, validate_read_only_sql


class SqlGuardTests(unittest.TestCase):
    def test_accepts_authorized_select(self):
        sql = "SELECT * FROM ADMIN.VW_INTERNACOES_MENSAIS"
        self.assertEqual(validate_read_only_sql(sql), sql)

    def test_accepts_authorized_join(self):
        sql = "SELECT * FROM ADMIN.VW_INTERNACOES_MENSAIS m JOIN ADMIN.VW_RANKING_MUNICIPIOS r ON 1=1"
        self.assertEqual(validate_read_only_sql(sql), sql)

    def test_accepts_extract_from_date_column(self):
        sql = (
            "SELECT SUM(INTERNACOES) "
            "FROM ADMIN.VW_INTERNACOES_DASHBOARD "
            "WHERE EXTRACT(YEAR FROM MES_REFERENCIA) = 2025"
        )
        self.assertEqual(validate_read_only_sql(sql), sql)

    def test_rejects_dml(self):
        with self.assertRaises(UnsafeQueryError):
            validate_read_only_sql("DELETE FROM ADMIN.VW_INTERNACOES_DASHBOARD")

    def test_rejects_unapproved_object(self):
        with self.assertRaises(UnsafeQueryError):
            validate_read_only_sql("SELECT * FROM ADMIN.INTERNACOES_SP")

    def test_rejects_multiple_statements(self):
        with self.assertRaises(UnsafeQueryError):
            validate_read_only_sql("SELECT * FROM ADMIN.VW_INTERNACOES_MENSAIS; DROP TABLE X")


if __name__ == "__main__":
    unittest.main()

