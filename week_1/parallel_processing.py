from random import randint
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool, Process, Queue
from time import perf_counter
from functools import wraps
from pprint import pp

def generate_data(n):
    for _ in range(n):
        yield randint(1, 1000)

def is_prime(n):
    if n == 2 or n == 3: return True
    if n < 2 or n%2 == 0: return False
    if n < 9: return True
    if n%3 == 0: return False
    r = int(n**0.5)
    f = 5
    while f <= r:
        if n % f == 0: return False
        if n % (f+2) == 0: return False
        f += 6
    return True

queue = []

def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        t1 = perf_counter()
        result = func(*args, **kwargs)
        elapsed = perf_counter() - t1
        queue.append((func.__name__, args[0], elapsed))
        return result
    return wrapper

@timer
def thread_pool_executor_solution(n, data_set):
    with ThreadPoolExecutor() as pool:
        results = pool.map(is_prime, data_set)
    # Force evaluation of generator
    list(results)

@timer
def multiprocessing_pool_solution(n, data_set):
    with Pool(8) as pool:
        results = pool.map(is_prime, data_set)

def is_prime_batched(in_queue, out_queue):
    while True:
        try:
            numbers = in_queue.get(timeout=1)
            if numbers is None:  # Sentinel value to terminate
                break
            result = []
            for n in numbers:
                result.append((n, is_prime(n)))
            out_queue.put(result)
        except Exception as e:
            break

@timer
def multiprocessing_process_solution(n, data_set):
    DOP = 8
    in_queue = Queue()
    out_queue = Queue()
    
    batch_size = (len(data_set) + DOP - 1) // DOP
    batches = []
    for i in range(0, len(data_set), batch_size):
        batch = data_set[i:i + batch_size]
        batches.append(batch)
        in_queue.put(batch)
    
    for _ in range(DOP):
        in_queue.put(None)
    
    processes = [Process(target=is_prime_batched, args=(in_queue, out_queue)) 
                 for _ in range(DOP)]
    
    [proc.start() for proc in processes]
    
    results = []
    for _ in range(len(batches)):
        results.extend(out_queue.get())
    
    [proc.join() for proc in processes]

@timer
def singlethreaded_solution(n, data_set):
    results = []
    for n in data_set:
        results.append((n, is_prime(n)))

        

def main(n):
    print(f"\n{'='*50}")
    print(f"Testing with n = {n}")
    print('='*50)
    
    data_set = list(generate_data(n))
    
    print("Running thread_pool_executor_solution...")
    thread_pool_executor_solution(n, data_set)
    
    print("Running multiprocessing_pool_solution...")
    multiprocessing_pool_solution(n, data_set)
    
    print("Running multiprocessing_process_solution...")
    multiprocessing_process_solution(n, data_set)

    print("Running singlethreaded_solution...")
    singlethreaded_solution(n, data_set)
    
    print(f"Completed n = {n}")

if __name__ == '__main__':
    main(1000)
    main(10000)
    main(100000)
    main(1000000)
    main(10000000)
    # main(100000000)
    
    print("\n" + "="*50)
    print("Timing Results:")
    print("="*50)
    # pp(queue)


    import matplotlib.pyplot as plt
    import numpy as np

    data = queue

    # Extract unique categories
    methods = list(set(item[0] for item in data))
    methods.sort()  # Sort for consistent ordering

    # Group data by method
    grouped_data = {}
    for method, size, time in data:
        if method not in grouped_data:
            grouped_data[method] = {'sizes': [], 'times': []}
        grouped_data[method]['sizes'].append(size)
        grouped_data[method]['times'].append(time)

    # Sort each group by size
    for method in grouped_data:
        sizes = grouped_data[method]['sizes']
        times = grouped_data[method]['times']
        # Sort by size
        sorted_pairs = sorted(zip(sizes, times))
        grouped_data[method]['sizes'] = [x[0] for x in sorted_pairs]
        grouped_data[method]['times'] = [x[1] for x in sorted_pairs]

    # Create the plot
    plt.figure(figsize=(12, 8))

    # Color scheme
    colors = {
        'thread_pool_executor_solution': 'blue',
        'multiprocessing_pool_solution': 'green',
        'multiprocessing_process_solution': 'red',
        'singlethreaded_solution': 'yellow',
    }

    # Line styles and markers
    line_styles = ['-', '--', '-.', ':']
    markers = ['o', 's', '^', '*']

    # Plot each method
    for idx, method in enumerate(methods):
        sizes = grouped_data[method]['sizes']
        times = grouped_data[method]['times']
        
        plt.plot(sizes, times, 
                 label=method.replace('_', ' ').title(),
                 color=colors[method],
                 linestyle=line_styles[idx % len(line_styles)],
                 marker=markers[idx % len(markers)],
                 linewidth=2,
                 markersize=8)

    # Set log scale for x-axis (since sizes are powers of 10)
    plt.xscale('log')
    plt.yscale('log')  # Also log scale for y-axis to better show differences

    # Set labels and title
    plt.xlabel('Input Size', fontsize=14)
    plt.ylabel('Execution Time (seconds)', fontsize=14)
    plt.title('Performance Comparison of Parallelization Methods', fontsize=16, fontweight='bold')

    # Add grid
    plt.grid(True, which="both", ls="--", alpha=0.3)

    # Add legend
    plt.legend(fontsize=12)

    # Adjust layout
    plt.tight_layout()

    # Show plot
    plt.show()

    # Alternatively, you can create a grouped bar chart for better comparison
    plt.figure(figsize=(14, 8))

    # Prepare data for grouped bars
    unique_sizes = sorted(list(set(item[1] for item in data)))
    x = np.arange(len(unique_sizes))
    width = 0.25

    # Create bars for each method
    for idx, method in enumerate(methods):
        times = []
        for size in unique_sizes:
            # Find the time for this method and size
            time = next((item[2] for item in data if item[0] == method and item[1] == size), 0)
            times.append(time)
        
        # Calculate bar positions
        positions = x + (idx - 1) * width
        
        plt.bar(positions, times, width, 
                label=method.replace('_', ' ').title(),
                color=colors[method],
                alpha=0.8)

    # Set x-axis labels
    plt.xlabel('Input Size', fontsize=14)
    plt.ylabel('Execution Time (seconds)', fontsize=14)
    plt.title('Performance Comparison - Grouped Bar Chart', fontsize=16, fontweight='bold')
    plt.xticks(x, [str(size) for size in unique_sizes])
    plt.yscale('log')  # Use log scale for better visualization

    # Add legend
    plt.legend(fontsize=12)

    # Add grid
    plt.grid(True, axis='y', alpha=0.3, linestyle='--')

    # Add value labels on bars (only for significant values)
    for idx, method in enumerate(methods):
        times = []
        for size in unique_sizes:
            time = next((item[2] for item in data if item[0] == method and item[1] == size), 0)
            times.append(time)
        
        positions = x + (idx - 1) * width
        for pos, time in zip(positions, times):
            if time > 0.01:  # Only label if time is significant
                plt.text(pos, time * 1.1, f'{time:.3f}', 
                        ha='center', va='bottom', fontsize=9, rotation=45)

    plt.tight_layout()
    plt.show()

    # Create a table summary
    print("\n" + "="*80)
    print("PERFORMANCE SUMMARY TABLE")
    print("="*80)
    print(f"{'Method':<35} {'Size':<15} {'Time (s)':<15}")
    print("-"*80)

    for method, size, time in sorted(data, key=lambda x: (x[0], x[1])):
        print(f"{method:<35} {size:<15} {time:<15.6f}")

    print("="*80)