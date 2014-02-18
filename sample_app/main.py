# standard library
import logging
import os
import sys

here = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(here, '..'))

# third party
import tornado.ioloop
import tornado.log
import tornado.web

# application specific
import transperth.fares
from location_proxy import determine_location
from utils import fares_to_table, BaseRequestHandler

logging.basicConfig(level=logging.DEBUG)
tornado.log.enable_pretty_logging()


class FaresRequestHandler(BaseRequestHandler):
    def get(self):
        self.render('fares.html')

    def post(self):
        from_loco = self.get_location('from')
        to_loco = self.get_location('to')

        locations = determine_location(from_loco, to_loco)

        from_loco = locations['from'][0]
        to_loco = locations['to'][0]

        fares = transperth.fares.determine_fare(
            from_loco,
            to_loco
        )

        table = fares_to_table(fares)
        self.write(table._repr_html_())


settings = {
    'debug': True,
    'template_path': os.path.join(here, 'templates')
}


application = tornado.web.Application([
    (r"/", FaresRequestHandler),
], **settings)

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
