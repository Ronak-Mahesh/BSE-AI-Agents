class Trader_GA(Trader):
    def __init__(self, ttype, tid, balance, params, time):
        super().__init__(ttype, tid, balance, params, time)
        self.population_size = 10
        self.mutation_rate = 0.1
        self.crossover_rate = 0.7
        self.generation_time = 10  # Time after which we evolve a new generation
        self.last_generation_time = time
        self.population = self.initialize_population()
        self.best_strategy = None

    def initialize_population(self):
        population = []
        for _ in range(self.population_size):
            # Create random strategies and initialize with default fitness
            strategy = {
                'price_adjustment_factor': random.uniform(0.95, 1.05), # Random price adjustment factor
                'threshold': random.uniform(0.01, 0.1), # Random threshold for price adjustment
                'fitness': 0  # Initialize fitness to zero for each strategy
            }
            population.append(strategy)
        return population

    def mutation(self, strategy):
        if random.random() < self.mutation_rate:
            key = random.choice(list(strategy.keys()))
            if key == 'price_adjustment_factor':
                strategy[key] = random.uniform(0.95, 1.05)
            elif key == 'threshold':
                strategy[key] = random.uniform(0.01, 0.1)
        return strategy

    def crossover(self, parent1, parent2):
        child = {}
        for key in parent1:
            if random.random() < self.crossover_rate:
                child[key] = parent1[key]
            else:
                child[key] = parent2[key]
        return child

    def select_parents(self):
        # Simple random selection of parents
        return random.choice(self.population), random.choice(self.population)

    def getorder(self, time, countdown, lob):
        if (time - self.last_generation_time) >= self.generation_time:
            self.evolve_population()
            self.last_generation_time = time

        if len(self.orders) < 1:
            return None

        self.best_strategy = max(self.population, key=lambda x: x['fitness'])
        limit = self.orders[0].price
        otype = self.orders[0].otype
        qty = self.orders[0].qty
        qid = self.orders[0].qid

        proposed_price = limit * self.best_strategy['price_adjustment_factor']
        if otype == 'Bid':
            price = min(proposed_price, limit)
        elif otype == 'Ask':
            price = max(proposed_price, limit)

        order = Order(self.tid, otype, price, qty, time, qid)
        return order

    def respond(self, time, lob, trade, verbose):
        # Ensure there is at least one order and a trade to respond to
        if trade is not None and len(self.orders) > 0:
            # Calculate the profit or loss from the trade
            profit = trade['price'] - self.orders[0].price if self.orders[0].otype == 'Bid' else self.orders[0].price - trade['price']

            # Update fitness of the strategy used in the last trade
            if self.best_strategy in self.population:
                current_strategy_index = self.population.index(self.best_strategy)
                # Ensure the fitness key exists, if not, initialize it
                self.population[current_strategy_index].setdefault('fitness', 0)
                self.population[current_strategy_index]['fitness'] += profit

            # Evolve population if needed
            if time - self.last_generation_time >= self.generation_time:
                self.evolve_population()
                self.last_generation_time = time
        else:
            if verbose:
                print("No orders or trade to respond to.")

    def evolve_population(self):
        # Rank strategies by their fitness
        self.population.sort(key=lambda x: x.get('fitness', 0), reverse=True)
        new_population = []
        while len(new_population) < self.population_size:
            parent1, parent2 = self.select_parents()
            child = self.crossover(parent1, parent2)
            child = self.mutation(child)
            # Reset fitness of new child
            child['fitness'] = 0
            new_population.append(child)
        self.population = new_population