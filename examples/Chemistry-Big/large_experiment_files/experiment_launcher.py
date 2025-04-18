import pandas as pd
import random
import subprocess
from queue import Queue, Empty
from threading import Thread
import time


def worker(device_id, queue):
    while True:
        try:
            experiment = queue.get_nowait()
        except Empty:
            break

        try:
            # Construct the command to run the script
            command = (
                f"python3 experiment.py --device={device_id} --run_index={experiment}"
            )
            # Start the experiment
            subprocess.run(command, shell=True, check=True)
        except Exception as e:
            print(f"Error running experiment {experiment} on device {device_id} : {e}")
            print("Retrying")
            try:
                # Start the experiment
                subprocess.run(command, shell=True, check=True)
            except Exception as e:
                print(
                    f"Second error running experiment {experiment} on device {device_id} : {e}"
                )
                print("Skipping")

        finally:
            queue.task_done()


def main():
    df_batches = pd.read_csv("batches.csv")
    num_devices = 3
    max_scripts_per_device = 1
    num_experiments = len(df_batches)
    queue = Queue()

    # Fill the queues with experiments
    for i in range(num_experiments):
        queue.put(i)

    threads = []
    for device_id in range(0, num_devices):
        # Create up to max_scripts_per_device threads per device
        for _ in range(max_scripts_per_device):
            t = Thread(target=worker, args=(device_id, queue))
            t.start()
            threads.append(t)

    # Wait for all threads to finish
    for t in threads:
        t.join()


if __name__ == "__main__":
    main()
