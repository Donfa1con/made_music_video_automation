from openvino.inference_engine import IECore


class OpenVinoModelWrapper:
    def _init__(self, path):
        ie = IECore()
        net = ie.read_network(model=path + '.xml', weights=path + '.bin')
        self.input_name = next(iter(net.inputs))
        self.output_name = next(iter(net.outputs))
        self.exec_net = ie.load_network(net, 'CPU', num_requests=1)

    def predict(self, batch):
        return self.exec_net.infer({self.input_name: batch})[self.output_name]
