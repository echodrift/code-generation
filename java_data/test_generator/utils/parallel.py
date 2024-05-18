from multiprocessing import Pool, RLock
from tqdm.auto import tqdm
import logging
from typing import Iterable, List, T
import numpy as np
from . import tqdm as hf_tqdm
logger = logging.Logger("Logger", logging.INFO)

def map_with_multiprocessing_pool(
    function,
    iterable,
    num_proc,
    batched,
    batch_size,
    types,
    disable_tqdm,
    desc,
    # single_map_nested_func,
):
    num_proc = num_proc if num_proc <= len(iterable) else len(iterable)
    split_kwds = []  # We organize the splits ourselve (contiguous splits)
    for index in range(num_proc):
        div = len(iterable) // num_proc
        mod = len(iterable) % num_proc
        start = div * index + min(index, mod)
        end = start + div + (1 if index < mod else 0)
        split_kwds.append(
            (
                function,
                iterable[start:end],
                batched,
                batch_size,
                types,
                index,
                disable_tqdm,
                desc,
            )
        )

    if len(iterable) != sum(len(i[1]) for i in split_kwds):
        raise ValueError(
            f"Error dividing inputs iterable among processes. "
            f"Total number of objects {len(iterable)}, "
            f"length: {sum(len(i[1]) for i in split_kwds)}"
        )

    logger.info(
        f"Spawning {num_proc} processes for {len(iterable)} objects in slices of {[len(i[1]) for i in split_kwds]}"
    )
    initargs, initializer = None, None
    if not disable_tqdm:
        initargs, initializer = (RLock(),), tqdm.set_lock
    with Pool(num_proc, initargs=initargs, initializer=initializer) as pool:
        mapped = pool.map(_single_map_nested, split_kwds)
    logger.info(f"Finished {num_proc} processes")
    mapped = [obj for proc_res in mapped for obj in proc_res]
    logger.info(f"Unpacked {len(mapped)} objects")

    return mapped


def _single_map_nested(args):
    """Apply a function recursively to each element of a nested data struct."""
    function, data, batched, batch_size, types, rank, disable_tqdm, desc = args

    # Singleton first to spare some computation
    if not isinstance(data, dict) and not isinstance(data, types):
        if batched:
            return function([data])[0]
        else:
            return function(data)
    if (
        batched
        and not isinstance(data, dict)
        and isinstance(data, types)
        and all(not isinstance(v, (dict, types)) for v in data)
    ):
        return [mapped_item for batch in iter_batched(data, batch_size) for mapped_item in function(batch)]

    # Reduce logging to keep things readable in multiprocessing with tqdm
    if rank is not None and logging.get_verbosity() < logging.WARNING:
        logging.set_verbosity_warning()
    # Print at least one thing to fix tqdm in notebooks in multiprocessing
    # see https://github.com/tqdm/tqdm/issues/485#issuecomment-473338308
    if rank is not None and not disable_tqdm and any("notebook" in tqdm_cls.__name__ for tqdm_cls in tqdm.__mro__):
        print(" ", end="", flush=True)

    # Loop over single examples or batches and write to buffer/file if examples are to be updated
    pbar_iterable = data.items() if isinstance(data, dict) else data
    pbar_desc = (desc + " " if desc is not None else "") + "#" + str(rank) if rank is not None else desc
    with hf_tqdm(pbar_iterable, disable=disable_tqdm, position=rank, unit="obj", desc=pbar_desc) as pbar:
        if isinstance(data, dict):
            return {
                k: _single_map_nested((function, v, batched, batch_size, types, None, True, None)) for k, v in pbar
            }
        else:
            mapped = [_single_map_nested((function, v, batched, batch_size, types, None, True, None)) for v in pbar]
            if isinstance(data, list):
                return mapped
            elif isinstance(data, tuple):
                return tuple(mapped)
            else:
                return np.array(mapped)
            

def iter_batched(iterable: Iterable[T], n: int) -> Iterable[List[T]]:
    if n < 1:
        raise ValueError(f"Invalid batch size {n}")
    batch = []
    for item in iterable:
        batch.append(item)
        if len(batch) == n:
            yield batch
            batch = []
    if batch:
        yield batch