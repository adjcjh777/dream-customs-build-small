try:
    import spaces
except ImportError:
    spaces = None


def _gpu_decorator(func):
    if spaces is None:
        return func
    return spaces.GPU(func)


@_gpu_decorator
def zerogpu_startup_probe():
    """Registers a lightweight ZeroGPU function without moving Modal inference into HF."""
    return {"status": "ok", "purpose": "zerogpu-startup-detection"}

