import time
import random
import matplotlib.pyplot as plt
import numpy as np
from utils import generate_dataset, buscaComunes


def run_benchmark(passenger_sizes, poi_sizes, overlap_ratio=0.1, num_runs=3):
    """
    Run a comprehensive benchmark for different passenger and POI sizes.

    Args:
        passenger_sizes (list): List of passenger list sizes to test.
        poi_sizes (list): List of persons of interest list sizes to test.
        overlap_ratio (float): Ratio of overlap between the two sets.
        num_runs (int): Number of runs for each configuration.

    Returns:
        tuple: A tuple containing (results, naive_results) dictionaries.
    """
    results = {}
    naive_results = {}

    for passenger_size in passenger_sizes:
        for poi_size in poi_sizes:
            # Skip invalid configurations
            if poi_size > passenger_size:
                continue

            overlap_size = int(min(passenger_size, poi_size) * overlap_ratio)

            key = f"{passenger_size}_{poi_size}"
            results[key] = []
            naive_results[key] = []

            for _ in range(num_runs):
                # Generate datasets with expected overlap
                all_names = generate_dataset(passenger_size + poi_size)
                poi_names = set(random.sample(list(all_names), poi_size))
                passenger_names = set(
                    random.sample(
                        list(all_names - poi_names), passenger_size - overlap_size
                    )
                )

                # Add overlap
                overlap = set(random.sample(list(poi_names), overlap_size))
                passenger_names.update(overlap)

                # Time PSI approach
                start_time = time.time()
                psi_result = buscaComunes(poi_names, passenger_names)
                psi_time = time.time() - start_time

                # Time naive approach
                start_time = time.time()
                naive_result = poi_names.intersection(passenger_names)
                naive_time = time.time() - start_time

                # Verify results
                assert psi_result == naive_result

                # Store times
                results[key].append(psi_time)
                naive_results[key].append(naive_time)

    # Average results
    for key in results:
        results[key] = sum(results[key]) / len(results[key])
        naive_results[key] = sum(naive_results[key]) / len(naive_results[key])

    return results, naive_results


def plot_results(
    passenger_sizes,
    poi_sizes,
    results,
    naive_results,
    output_file="benchmark_results.png",
):
    """
    Plot benchmark results.

    Args:
        passenger_sizes (list): List of passenger list sizes tested.
        poi_sizes (list): List of persons of interest list sizes tested.
        results (dict): Dictionary of PSI benchmark results.
        naive_results (dict): Dictionary of naive benchmark results.
        output_file (str): Path to save the plot.
    """
    # Set up the figure
    fig, axs = plt.subplots(1, 2, figsize=(16, 8))

    # Prepare data for heatmap
    psi_data = np.zeros((len(passenger_sizes), len(poi_sizes)))
    naive_data = np.zeros((len(passenger_sizes), len(poi_sizes)))

    for i, p_size in enumerate(passenger_sizes):
        for j, poi_size in enumerate(poi_sizes):
            if poi_size > p_size:
                continue

            key = f"{p_size}_{poi_size}"

            if key in results:
                psi_data[i, j] = results[key]
                naive_data[i, j] = naive_results[key]

    # Plot PSI heatmap
    im1 = axs[0].imshow(psi_data, cmap="viridis")
    axs[0].set_title("PSI Protocol Execution Time (seconds)")
    axs[0].set_xlabel("POI List Size")
    axs[0].set_ylabel("Passenger List Size")
    axs[0].set_xticks(np.arange(len(poi_sizes)))
    axs[0].set_yticks(np.arange(len(passenger_sizes)))
    axs[0].set_xticklabels(poi_sizes)
    axs[0].set_yticklabels(passenger_sizes)
    fig.colorbar(im1, ax=axs[0])

    # Plot naive heatmap
    im2 = axs[1].imshow(naive_data, cmap="viridis")
    axs[1].set_title("Naive Set Intersection Time (seconds)")
    axs[1].set_xlabel("POI List Size")
    axs[1].set_ylabel("Passenger List Size")
    axs[1].set_xticks(np.arange(len(poi_sizes)))
    axs[1].set_yticks(np.arange(len(passenger_sizes)))
    axs[1].set_xticklabels(poi_sizes)
    axs[1].set_yticklabels(passenger_sizes)
    fig.colorbar(im2, ax=axs[1])

    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()


def main():
    """Run the benchmark and generate plots."""
    print("Running Privacy-Preserving Protocol Benchmark")

    # Define benchmark parameters
    passenger_sizes = [100, 1000, 5000, 10000]
    poi_sizes = [10, 100, 500, 1000]

    print(f"Testing with passenger sizes: {passenger_sizes}")
    print(f"Testing with POI sizes: {poi_sizes}")
    print("Running benchmarks (this may take a while)...")

    results, naive_results = run_benchmark(passenger_sizes, poi_sizes)

    print("Benchmark results:")
    for key in sorted(results.keys()):
        p_size, poi_size = map(int, key.split("_"))
        psi_time = results[key]
        naive_time = naive_results[key]
        ratio = psi_time / naive_time if naive_time > 0 else float("inf")

        print(f"Passengers: {p_size}, POI: {poi_size}")
        print(f"  PSI time: {psi_time:.6f} seconds")
        print(f"  Naive time: {naive_time:.6f} seconds")
        print(f"  Ratio (PSI/Naive): {ratio:.2f}x")

    print("Generating plot...")
    plot_results(passenger_sizes, poi_sizes, results, naive_results)
    print("Benchmark complete. Results saved to benchmark_results.png")


if __name__ == "__main__":
    main()
