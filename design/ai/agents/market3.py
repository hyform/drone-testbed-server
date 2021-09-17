from repo.models import Customer, Address
from exper.models import Market

class Market3():

    def __init__(self):


        print("code to create market 3, market 1 with 8 additional path waypoints")

#        all_markets = Market.objects.all()
#        for market in all_markets:
#            print("market query", market.id, market.name)

        # create market
#        market3 = Market()
#        market3.id = 3
#        market3.name = "Market 3"
#        market3.save()

        # add customers
#        market1 = Market.objects.filter(id=1).first()
#        market1_customers = Customer.objects.filter(market=market1)
#        for customer in market1_customers:
#            Customer.objects.create(
#                market = market3,
#                address = customer.address,
#                payload = customer.payload,
#                weight = customer.weight
#            )

#        restricted_airspace_waypoints = [[-2.99, 4.19], [-2.14, 3.84], [-1.81, 2.99], [-2.15, 2.15], [-3.01,  1.81], [-3.86, 2.15],  [-4.19, 3.01], [-3.84, 3.85]]
#        for waypoint in restricted_airspace_waypoints:
#            address = Address()
#            address.x = waypoint[0]
#            address.z = waypoint[1]
#            address.save()
#            Customer.objects.create(
#                market = market3,
#                address = address,
#                payload = "parcel",
#                weight = 0
#            )
