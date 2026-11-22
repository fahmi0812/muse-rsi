import os, sys, unittest
workdir = sys.argv[1]
sys.path.insert(0, os.path.join(workdir, "src"))
from calc import tambah

class TestTambahHidden(unittest.TestCase):
    def test_pos(self):
        self.assertEqual(tambah(2, 3), 5)
    def test_neg(self):
        self.assertEqual(tambah(-1, 1), 0)
    def test_zero(self):
        self.assertEqual(tambah(0, 0), 0)
    def test_float(self):
        self.assertEqual(tambah(1.5, 2.5), 4.0)
    def test_type_error(self):
        with self.assertRaises(TypeError):
            tambah("a", 1)

if __name__ == "__main__":
    unittest.main(argv=[sys.argv[0], "-v"])
