from zeep.wsdl.bindings.soap import SoapBinding
from zeep.xsd import QName
from zeep.wsdl.definitions import Port, Binding, Operation
from zeep.proxy import ServiceProxy
from zeep.cache import SqliteCache
from urllib.parse import urlparse, urljoin
from zeep import CachingClient, Transport, Client


base = 'https://serviceinformation.transperth.info'


class InterceptingTransport(Transport):
    def load(self, url):
        parse_result = urlparse(url)
        return super().load(
            parse_result._replace(
                scheme='https', netloc='serviceinformation.transperth.info'
            ).geturl()
        )


class Text:
    def __init__(self, text):
        self.text = text


def create_binding(wsdl, transport):
    binding = SoapBinding(
        wsdl=wsdl,
        name=Text('FaresServiceSoapBinding'),
        port_name=Text('{http://tempuri.org/}IFaresService'),
        transport=transport,
        default_style='document',
    )
    for s in wsdl.port_types.values():
        for m in s.operations.values():
            binding._operation_add(Operation(m.name, binding))
    binding.resolve(list(wsdl._definitions.values())[0])
    return binding


def main():
    breakpoint()
    client = Client(
        wsdl=f'{base}?wsdl',
        transport=InterceptingTransport(
            cache=SqliteCache(),
        ),
    )
    service = client.wsdl.services['FaresService']
    port = Port('port', 'binding', None)
    port.binding = create_binding(client.wsdl, client.transport)
    service.add_port(port)
    client.service.GetOSVersion(a='1001', b='1001')
    # ServiceProxy(
    #     client,
    #     Binding(
    #         wsdl=client.wsdl,
    #         name='FaresServiceSoapBinding',
    #         port_name='FaresServiceSoapPort',
    #     ),
    #     #     Port(
    #     # base,
    #     #         )
    # ).GetStopInformation('1001')


if __name__ == '__main__':
    main()
