"""
Command worker to make decisions based on Telemetry Data.
"""

import os
import pathlib

from pymavlink import mavutil

from utilities.workers import queue_proxy_wrapper
from utilities.workers import worker_controller
from . import command
from ..common.modules.logger import logger


# =================================================================================================
#                            ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
# =================================================================================================
def command_worker(
    connection: mavutil.mavfile,
    target: command.Position,
    input_queue: queue_proxy_wrapper.QueueProxyWrapper,
    output_queue: queue_proxy_wrapper.QueueProxyWrapper,
    controller: worker_controller.WorkerController,
) -> None:
    """
    Worker process.

    args... describe what the arguments are
    """
    # =============================================================================================
    #                          ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
    # =============================================================================================

    # Instantiate logger
    worker_name = pathlib.Path(__file__).stem
    process_id = os.getpid()
    result, local_logger = logger.Logger.create(f"{worker_name}_{process_id}", True)
    if not result:
        print("ERROR: Worker failed to create logger")
        return

    # Get Pylance to stop complaining
    assert local_logger is not None

    local_logger.info("Logger initialized for Command Worker", True)

    # =============================================================================================
    #                          ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
    # =============================================================================================
    # Instantiate class object (command.Command)

    result, command_instance = command.Command.create(connection, target, local_logger)

    if not result or command_instance is None:
        local_logger.error("Could not initialize Command object")
        return

    local_logger.info("Command object created successfully")

    # Main loop: do work
    while not controller.is_exit_requested():
        controller.check_pause()

        # Get telemetry data from input queue
        try:
            current_telemetry = input_queue.queue.get(timeout=0.5)

            if current_telemetry is None:
                local_logger.warning("Received None from telemetry queue")
                continue

            # Log the received telemetry
            local_logger.info(
                f"Received telemetry: pos=({current_telemetry.x:.2f}, {current_telemetry.y:.2f}, {current_telemetry.z:.2f}), yaw={current_telemetry.yaw:.2f}"
            )

            # Run command logic
            command_string = command_instance.run(current_telemetry)

            # Only send to output queue if a command was issued
            if command_string:
                output_queue.queue.put(command_string)
                local_logger.info(f"Command output: {command_string}")

        except Exception as e:
            # Timeout or other queue error - continue waiting
            local_logger.debug(f"Queue timeout or error: {e}")
            continue

    local_logger.info("Command worker stopped")


# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
