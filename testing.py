from unittest import mock
from unittest import TestCase


#import files to test
import util
import planning

class TestUtil(TestCase):
    @mock.patch('util.getfile', create=True)
    def test_getfile(self, mocked_input):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_getfiles(self):
        pass

class DictCreateTests(TestCase):

    def testdictCreateSimple(self, mocked_input):
        mocked_input.side_effect = ['Albert Einstein', '42.81', 'done']
        result = dictCreate(1)
        self.assertEqual(result, {'Albert Einstein': [42.81]})



if __name__ == '__main__':
    unittest.main()