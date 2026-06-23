# -*- coding: utf-8 -*-
import sys
import traceback
from contextlib import contextmanager
from .utils import logger

@contextmanager
def debug_exception():
    """
    Diagnostic helper context manager.
    Safeguards engine exceptions and writes trace records directly to the log.
    """
    try:
        yield
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        logger("--- UNHANDLED SCRAPER EXCEPTION TRACE ---", level="ERROR")
        logger(f"Fault Context: {exc_type.__name__} - {exc_value}", level="ERROR")
        
        # Format the traceback array cleanly for standard string outputs
        trace_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        for line in trace_lines:
            # Strip trailing newlines to keep formatting clear in logs
            logger(line.rstrip('\n'), level="ERROR")
            
        logger("---------------------------------------", level="ERROR")
        # Re-raise so the calling virtual file system registers the extraction state fault
        raise e
