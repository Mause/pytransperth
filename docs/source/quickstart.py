# create the Location object you wish to resolve;
from transperth.location import Location, ResolvedLocation, determine_location

from_location = Location.from_stop('12111')
to_location = Location.from_stop('20000')

# then we resolve it into something that the transperth api will accept
locations = determine_location(from_location, to_location)

# determine_location will return a dictionary like so;
{
    '<DIRECTION>': [
        ResolvedLocation('<NAME>', '<CODE>'),
        # etc
    ]
}

# it would be reasonable to assume the first result is correct,
# or to let the end user choose from a list
from_location = locations['from'][0]
to_location = locations['to'][0]

# once we have these, we can grab the routes
from transperth.routes import determine_routes

routes = determine_routes(from_location, to_location)

# take your pick of the routes
route = routes[0]

# and use 'em how you like
print(route['duration'])
