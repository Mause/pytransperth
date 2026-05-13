from datetime import timedelta
from typing import cast
from urllib.parse import urljoin, urlparse

from zeep import CachingClient, Client, Transport
from zeep.cache import SqliteCache
from zeep.proxy import ServiceProxy
from zeep.wsdl.bindings import Soap12Binding
from zeep.wsdl.bindings.soap import SoapOperation
from zeep.wsdl.definitions import (
    AbstractOperation,
    Binding,
    MessagePart,
    Port,
    AbstractMessage,
)
from zeep.wsdl.messages import DocumentMessage
from zeep.xsd import QName

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


nsmap = dict(
    wsdl="http://schemas.xmlsoap.org/wsdl/",
    xsd="http://www.w3.org/2001/XMLSchema",
    wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd",
    soap="http://schemas.xmlsoap.org/wsdl/soap/",
    soap12="http://schemas.xmlsoap.org/wsdl/soap12/",
    tns="http://tempuri.org/",
    wsa="http://schemas.xmlsoap.org/ws/2004/08/addressing",
    wsx="http://schemas.xmlsoap.org/ws/2004/09/mex",
    wsap="http://schemas.xmlsoap.org/ws/2004/08/addressing/policy",
    wsaw="http://www.w3.org/2006/05/addressing/wsdl",
    msc="http://schemas.microsoft.com/ws/2005/12/wsdl/contract",
    wsp="http://schemas.xmlsoap.org/ws/2004/09/policy",
    wsa10="http://www.w3.org/2005/08/addressing",
    wsam="http://www.w3.org/2007/05/addressing/metadata",
    **{
        'soap-enc': "http://schemas.xmlsoap.org/soap/encoding/",
        'soap-env': "http://schemas.xmlsoap.org/soap/encoding/",
    },
)


def create_binding(wsdl, transport: Transport):
    binding = Soap12Binding(
        wsdl=wsdl,
        name=Text('FaresServiceSoapBinding'),
        port_name=Text('{http://tempuri.org/}IFaresService'),
        transport=transport,
        default_style='document',
    )
    for port_type in wsdl.port_types.values():
        for abstract_op in port_type.operations.values():
            abstract_op = cast(AbstractOperation, abstract_op)
            operation = SoapOperation(
                abstract_op.name,
                binding,
                nsmap=nsmap,
                soapaction=abstract_op.wsa_action,
                style='',
            )
            operation.input = resolve_message(
                abstract_op.input_message, wsdl, operation
            )
            operation.output = resolve_message(
                abstract_op.output_message, wsdl, operation
            )
            binding._operation_add(operation)
    binding.resolve(list(wsdl._definitions.values())[0])
    return binding


def resolve_message(message, wsdl, operation):
    message = cast(AbstractMessage, message)
    message.resolve(list(wsdl._definitions.values())[0])
    doc_message = DocumentMessage(wsdl, message.name, operation, type='', nsmap=nsmap)
    for part in message.parts.values():
        pass
    doc_message._resolve_info = {
        'header': [],
        'body': {'part': None},
    }
    return doc_message


def main():
    import pudb

    pudb.set_trace()
    client = Client(
        wsdl=f'{base}?wsdl',
        transport=InterceptingTransport(
            cache=SqliteCache(timeout=timedelta(days=60).total_seconds()),
        ),
    )
    service = client.wsdl.services['FaresService']
    port = Port(
        'port',
        'binding',
        None,
    )
    port.binding = create_binding(client.wsdl, client.transport)
    port.binding_options = {'address': base}
    service.add_port(port)
    client.service.GetOSVersion(LocationName='1001', ZoneNumber='1001')
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
