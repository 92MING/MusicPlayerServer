print('i am here')

if __name__ == '__main__':
    import time, multiprocessing


    def runNode(queue: multiprocessing.Queue):
        # region import
        try:
            import pythonp2p
        except ModuleNotFoundError:
            import sys, crypto
            sys.modules['Crypto'] = crypto
            import pythonp2p
        import threading, time
        # endregion
        class Node(pythonp2p.Node):

            def __init__(self, *args, queue: multiprocessing.Queue = None, **kwargs):
                super().__init__()
                self.queue = queue
                queue.put(self.port)
                self.stop_UDP_send_repeat = False

                def get_command_from_queue():
                    if self.queue is not None:
                        while True:
                            command = self.queue.get()
                            funcName, args, kwargs = command
                            print('received command:', funcName, 'args:', args, 'kwargs:', kwargs)
                            try:
                                getattr(self, funcName)(*args, **kwargs)
                            except Exception as e:
                                print('Error when executing command:', e)

                threading.Thread(target=get_command_from_queue, daemon=True).start()

            def udp_send(self, data: bytes, addr: tuple, port: int):
                self.sock.sendto(data, (addr, port))

            def udp_send_repeatly(self, data: bytes, addr: tuple, port: int, interval: float = 0.5,
                                  time_limit: float = 10):
                def _send():
                    timeCount = 0
                    while timeCount < time_limit and not self.stop_UDP_send_repeat:
                        # self.sock.sendto(data, (addr, port))
                        print('send', data, 'to', addr, port)
                        time.sleep(interval)
                        timeCount += interval
                    self.stop_UDP_send_repeat = False
                    print('stop sending')

                threading.Thread(target=_send, daemon=True).start()

            def stop_udp_send_repeatly(self):
                self.stop_UDP_send_repeat = True

        node = Node(queue=queue)
        node.start()

    queue = multiprocessing.Queue()
    p = multiprocessing.Process(target=runNode, args=(queue,))
    p.start()
    port = queue.get()
    def orderProcess(funcName, *args, **kwargs):
        queue.put((funcName, args, kwargs))
    orderProcess('udp_send_repeatly', data=b'hello',addr='0.0.0.0', port=9192)
    time.sleep(5)
    orderProcess('stop_udp_send_repeatly')
    p.join()
