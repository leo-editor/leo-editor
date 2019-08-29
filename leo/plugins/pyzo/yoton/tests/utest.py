""" _utest.py

Unit tests for yoton.

"""

import sys, os, time
import unittest

# Go up one directory and then import the yoton package
os.chdir('..')
os.chdir('..')
sys.path.insert(0,'.')

# Import yoton from there
import yoton
from yoton.misc import long
class Tester(unittest.TestCase):
    """ Perform a set of tests using three contexts and
    each of the six channels at each context.

    """

    def setUp(self):

        # Create contexts
        self._context1 = c1 = yoton.Context()
        self._context2 = c2 = yoton.Context()
        self._context3 = c3 = yoton.Context()

        # Create pub sub channels
        self._channel_pub1 = yoton.PubChannel(c1,'foo')
        self._channel_pub2 = yoton.PubChannel(c2,'foo')
        self._channel_pub3 = yoton.PubChannel(c3,'foo')
        #
        self._channel_sub1 = yoton.SubChannel(c1,'foo')
        self._channel_sub2 = yoton.SubChannel(c2,'foo')
        self._channel_sub3 = yoton.SubChannel(c3,'foo')

        # Create req rep channels
        self._channel_req1 = yoton.ReqChannel(c1,'bar')
        self._channel_req2 = yoton.ReqChannel(c2,'bar')
        self._channel_req3 = yoton.ReqChannel(c3,'bar')
        #
        self._channel_rep1 = yoton.RepChannel(c1,'bar')
        self._channel_rep2 = yoton.RepChannel(c2,'bar')
        self._channel_rep3 = yoton.RepChannel(c3,'bar')

        # Create state channels
        self._channel_state1 = yoton.StateChannel(c1, 'spam')
        self._channel_state2 = yoton.StateChannel(c2, 'spam')
        self._channel_state3 = yoton.StateChannel(c3, 'spam')
    def tearDown(self):
        self._context1.close()
        self._context2.close()
        self._context3.close()
    def test_connecting(self):

        # Connect
        self._context1.bind('localhost:test1')
        self._context2.connect('localhost:test1')
        time.sleep(0.1) # Give time for binding to finish

        # Test if connected
        self.assertEqual(self._context1.connection_count, 1)
        self.assertEqual(self._context2.connection_count, 1)
        self.assertEqual(self._context3.connection_count, 0)

        # Connect more
        self._context1.bind('localhost:test2')
        self._context3.connect('localhost:test2')
        time.sleep(0.1) # Give time for binding to finish

        # Test if connected
        self.assertEqual(self._context1.connection_count, 2)
        self.assertEqual(self._context2.connection_count, 1)
        self.assertEqual(self._context3.connection_count, 1)
    def test_closing_channel(self):

        # Connect
        self._context1.bind('localhost:test')
        self._context2.connect('localhost:test')

        # Send data
        self._channel_pub1.send('hello')

        # Receive data
        self.assertEqual(self._channel_sub2.recv(), 'hello')
        self.assertEqual(self._channel_sub2.recv(False), '')

        # Close channel
        self._channel_sub2.close()
        self.assertEqual(self._channel_sub2.recv(), '')
        self.assertTrue(self._channel_sub2.closed)
    def test_pub_sub(self):

        # also test hopping

        # Connect
        self._context1.bind('localhost:test1')
        self._context2.connect('localhost:test1')
        self._context2.bind('localhost:test2')
        self._context3.connect('localhost:test2')

        # Send messages
        self._channel_pub1.send('msg1')
        time.sleep(0.1)
        self._channel_pub2.send('msg2')
        time.sleep(0.1)

        # Receive msssages
        self.assertEqual(self._channel_sub2.recv(), 'msg1')
        self.assertEqual(self._channel_sub3.recv(), 'msg1')
        self.assertEqual(self._channel_sub3.recv(), 'msg2')
    def test_pub_sub_select_channel(self):

        # Connect
        self._context1.bind('localhost:test1')
        self._context2.connect('localhost:test1')

        # Create channels
        pub1 = yoton.PubChannel(self._context1, 'foo1')
        pub2 = yoton.PubChannel(self._context1, 'foo2')
        #
        sub1 = yoton.SubChannel(self._context2, 'foo1')
        sub2 = yoton.SubChannel(self._context2, 'foo2')

        # Send a bunch of messages
        I = [0,1,0,0,1,0,1,1,1,0,0,1,0,0,0,1,1,0,1]
        for i in range(len(I)):
            pub = [pub1, pub2][I[i]]
            pub.send(str(i))

        time.sleep(0.1)

        # Receive in right order
        count = 0
        while True:
            sub = yoton.select_sub_channel(sub1, sub2)
            if sub:
                i = int(sub.recv())
                self.assertEqual(i, count)
                count += 1
            else:
                break

        # Test count
        self.assertEqual(count, len(I))
    def test_pubstate_substate(self):

        # also test hopping

        # Set status before connecting
        self._channel_state1.send('status1')

        # Connect
        self._context1.bind('localhost:test1')
        self._context2.connect('localhost:test1')
        self._context2.bind('localhost:test2')
        self._context3.connect('localhost:test2')
        time.sleep(0.1)

        # Receive msssages
        self.assertEqual(self._channel_state2.recv(), 'status1')
        self.assertEqual(self._channel_state2.recv(), 'status1')
        self.assertEqual(self._channel_state3.recv(), 'status1')
        self.assertEqual(self._channel_state3.recv(), 'status1')

        # Update status
        self._channel_state1.send('status2')
        time.sleep(0.1)

        # Receive msssages (recv multiple times should return last status)
        self.assertEqual(self._channel_state2.recv(), 'status2')
        self.assertEqual(self._channel_state2.recv(), 'status2')
        self.assertEqual(self._channel_state3.recv(), 'status2')
        self.assertEqual(self._channel_state3.recv(), 'status2')
    def test_req_rep1(self):

        # Connect
        self._context1.bind('localhost:test1')
        self._context2.connect('localhost:test1')
        self._context2.bind('localhost:test2')
        self._context3.connect('localhost:test2')

        # Turn on one replier
        self._channel_rep3.set_mode('thread')

        # Do requests
        foo, id1 = self._channel_req1.echo('foo').result(1)
        bar, id2 = self._channel_req1.echo('bar').result(1)

        # Check reply
        self.assertEqual(foo, 'foo')
        self.assertEqual(bar, 'bar')
        self.assertEqual(id1, hex(self._context3.id))
        self.assertEqual(id2, hex(self._context3.id))
    def test_req_rep2(self):

        # Test multiple requesters and multiple repliers

        # Connect
        if True:
            self._context1.bind('localhost:test1')
            self._context3.connect('localhost:test1')
            #
            self._context1.bind('localhost:test2')
            self._context2.connect('localhost:test2')
        else:
            freeNode = yoton.Context()
            #
            self._context1.bind('localhost:test1')
            freeNode.connect('localhost:test1')
            freeNode.bind('localhost:test1f')
            self._context3.connect('localhost:test1f')
            #
            self._context1.bind('localhost:test2')
            self._context2.connect('localhost:test2')
        time.sleep(0.1)

        # Turn on 2 requesters and 3 repliers
        self._channel_rep1.set_mode('thread') # threaded because simulating
        self._channel_rep2.set_mode('thread') # different processes
        self._channel_rep3.set_mode('thread')

        # Define and register reply handler
        def reply_handler(future):
            reply = future.result()
            reqnr = future.reqnr

            echo, id = reply
            if echo.lower() == 'stop':
                yoton.stop_event_loop()
            else:
                self.assertEqual(echo[:3], 'msg')
                contextnr = {   self._context1.id:1,
                                self._context2.id:2,
                                self._context3.id:3}[long(id,16)]
                print('request %s from %i handled by context %i.' %
                                                (echo, reqnr, contextnr))

        # Get echo functions
        echoFun1 = self._channel_req1.echo
        echoFun2 = self._channel_req2.echo

        # Send requests on req 1
        sleepTimes = [1, 0.1, 1, 0.6, 0.6, 0.6, 0.6, 0.6]
        for i in range(len(sleepTimes)):
            f = echoFun1('msg%i'%i, sleepTimes[i])
            f.add_done_callback(reply_handler)
            f.reqnr = 1

        # Send requests on req 2
        sleepTimes = [0.4, 0.4, 0.4, 0.4, 0.4]
        for i in range(len(sleepTimes)):
            f = echoFun2('msg%i'%i, sleepTimes[i])
            f.add_done_callback(reply_handler)
            f.reqnr = 2

        # Stop
        f = echoFun1('stop')
        f.add_done_callback(reply_handler)
        f.reqnr = 1

        # Enter event loop
        yoton.start_event_loop()
if __name__ == '__main__':

    suite = unittest.TestLoader().loadTestsFromTestCase(Tester)
    unittest.TextTestRunner(verbosity=2).run(suite)
    print('')
