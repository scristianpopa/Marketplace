"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""
from threading import Lock

class Marketplace:
    """
    Class that represents the Marketplace. It's the central part of the implementation.
    The producers and consumers use its methods concurrently.
    """
    def __init__(self, queue_size_per_producer):
        """
        Constructor

        :type queue_size_per_producer: Int
        :param queue_size_per_producer: the maximum size of a queue associated with each producer
        """
        self.q_size = queue_size_per_producer
        self.producers = {}
        self.producer_locks = {}
        self.carts = []
        self.producer_registration_lock = Lock()
        self.cart_registration_lock = Lock()

    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """
        self.producer_registration_lock.acquire()
        producer_id = 'prod' + str(len(self.producers))
        self.producers[producer_id] = []
        self.producer_locks[producer_id] = Lock()
        self.producer_registration_lock.release()
        return producer_id

    def publish(self, producer_id, product):
        """
        Adds the product provided by the producer to the marketplace

        :type producer_id: String
        :param producer_id: producer id

        :type product: Product
        :param product: the Product that will be published in the Marketplace

        :returns True or False. If the caller receives False, it should wait and then try again.
        """
        self.producer_locks[producer_id].acquire()
        if len(self.producers[producer_id]) >= self.q_size:
            self.producer_locks[producer_id].release()
            return False
        self.producers[producer_id].append(product)
        self.producer_locks[producer_id].release()
        return True

    def new_cart(self):
        """
        Creates a new cart for the consumer

        :returns an int representing the cart_id
        """
        self.cart_registration_lock.acquire()
        cart_id = len(self.carts)
        self.carts.append({})
        self.cart_registration_lock.release()
        return cart_id

    def add_to_cart(self, cart_id, product):
        """
        Adds a product to the given cart. The method returns

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to add to cart

        :returns True or False. If the caller receives False, it should wait and then try again
        """
        if product not in self.carts[cart_id]:
            self.carts[cart_id][product] = []
        for producer_id, products in self.producers.items():
            self.producer_locks[producer_id].acquire()
            for prod in products:
                if prod == product:
                    self.carts[cart_id][product].append(producer_id)
                    products.remove(prod)
                    self.producer_locks[producer_id].release()
                    return True
            self.producer_locks[producer_id].release()
        return False

    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to remove from cart
        """
        producer_id = self.carts[cart_id][product].pop(0)
        self.producer_locks[producer_id].acquire()
        self.producers[producer_id].append(product)
        self.producer_locks[producer_id].release()

    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """
        return [(product, len(producers)) for product, producers in self.carts[cart_id].items()]
