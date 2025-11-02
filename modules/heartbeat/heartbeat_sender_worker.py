"""
Heartbeat worker that sends heartbeats periodically.
"""

import os
import pathlib
import time

from pymavlink import mavutil

from utilities.workers import worker_controller
from . import heartbeat_sender
from ..common.modules.logger import logger


# =================================================================================================
#                            ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
# =================================================================================================
def heartbeat_sender_worker(
    connection: mavutil.mavfile,
    local_logger: logger.Logger,
    controller: worker_controller,
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

    local_logger.info("Logger initialized", True)

    # =============================================================================================
    #                          ↓ BOOTCAMPERS MODIFY BELOW THIS COMMENT ↓
    # =============================================================================================
    # Instantiate class object (heartbeat_sender.HeartbeatSender)

    result, heartbeat_sender_instance = heartbeat_sender.HeartbeatSender.create(connection)
    # Main loop: do work.

    if not result:
        local_logger.error("Failed to create HeartbeatSender")
        return

    # period = 1.0
    # next_time = time.time() + period

    while not controller.is_exit_requested():

        # controller.request_resume()

        # while next_time > time.time():
        controller.check_pause()
        # controller.request_resume()

        if heartbeat_sender_instance.run():
            local_logger.info("Heartbeat Sent")
        time.sleep(0.989999)

        # controller.request_pause()

        # sleep_time = max(0, next_time - time.time())
        # time.sleep(sleep_time)
        # next_time = time.time() + period

        # controller.request_resume()

    return


# =================================================================================================
#                            ↑ BOOTCAMPERS MODIFY ABOVE THIS COMMENT ↑
# =================================================================================================
