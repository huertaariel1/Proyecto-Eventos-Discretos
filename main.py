from src.evolving_population import Evolving_Population

def main():
    print("<------------------- Evolving Population Simulation ------------------------>")
    print()
    H = int(input("Initial number of women: "))
    print("-----------------------------")
    M = int(input("Initial number of men: "))
    print("-----------------------------")
    print("-----------------------------")
    print()

    simulation = Evolving_Population(M, H)
    simulation.run()

__main__ = main()