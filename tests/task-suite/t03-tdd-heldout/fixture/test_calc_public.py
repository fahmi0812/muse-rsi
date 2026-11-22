import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from calc import tambah

class TestTambahPublic(unittest.TestCase):
    def test_pos(self):
        self.assertEqual(tambah(2, 3), 5)
    def test_neg(self):
        self.assertEqual(tambah(-1, 1), 0)

if __name__ == "__main__":
    unittest.main(argv=[sys.argv[0], "-v"])
