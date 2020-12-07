from openvino.inference_engine import IECore


class OpenVinoModelWrapper:
    def __init__(self, path):
        ie = IECore()
        net = ie.read_network(model=path + '.xml', weights=path + '.bin')
        self.input_name = next(iter(net.inputs))
        self.output_names = [name for name in net.outputs]
        self.exec_net = ie.load_network(net, 'CPU', num_requests=1)

    def predict(self, batch):
        res = self.exec_net.infer({self.input_name: batch})
        return [res[name] for name in self.output_names]
