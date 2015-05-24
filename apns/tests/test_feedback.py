from datetime import datetime

from twisted.trial.unittest import TestCase

from apns.feedback import Feedback


class FeedbackTestCase(TestCase):

    def test_str(self):
        feedback = Feedback()
        feedback.when = 'when'
        feedback.token = 'token'

        self.assertEqual(str(feedback), '<Feedback: token, when>')

    def test_from_binary_string(self):
        t1 = datetime(2015, 1, 1, 12, 0, 0, 123456)
        stream = Feedback(t1, '00').to_binary_string()
        t2 = datetime(2015, 2, 1, 12, 0, 0, 123456)
        stream += Feedback(t2, '11').to_binary_string()

        feedbacks = Feedback.from_binary_string(stream)

        self.assertEqual(len(feedbacks), 2)
        self.assertEqual(feedbacks[0].when, t1.replace(microsecond=0))
        self.assertEqual(feedbacks[0].token, '00')
        self.assertEqual(feedbacks[1].when, t2.replace(microsecond=0))
        self.assertEqual(feedbacks[1].token, '11')
