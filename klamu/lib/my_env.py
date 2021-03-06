"""
This module consolidates all local configuration for the script, including modulename collection for logfile name
setup and initializing the config file.
Also other utilities find their home here.
"""

import configparser
# import datetime
import logging
import logging.handlers
import os
import platform
import time
from calendar import timegm
from datetime import datetime
from dotenv import load_dotenv


def init_env(projectname, filename):
    """
    This function will initialize the environment: Find and return handle to config file and set-up logging.

    :param projectname: Name that will be used to find ini file in properties subdirectory.
    :param filename: Filename (__file__) of the calling script (for logfile).
    :return: config handle
    """
    modulename = get_modulename(filename)
    config = get_inifile(projectname)
    my_log = init_loghandler(modulename)
    my_log.info('Start Application')
    return config


def get_inifile(projectname):
    """
    Read Project configuration ini file in subdirectory properties. Config ini filename is the projectname.
    The ini file is located in the properties module, which is sibling of the lib module.
    Environment settings defined in .env file are exported as well. The .env file needs to be in the project main
    directory.

    :param projectname: Name of the project.
    :return: Object reference to the inifile.
    """
    # Use Project Name as ini file.
    (filepath_lib, _) = os.path.split(__file__)
    (filepath, _) = os.path.split(filepath_lib)
    # configfile = filepath + "/properties/" + projectname + ".ini"
    configfile = os.path.join(filepath, 'properties', "{p}.ini".format(p=projectname))
    ini_config = configparser.ConfigParser()
    try:
        f = open(configfile)
        ini_config.read_file(f)
        f.close()
    except FileNotFoundError:
        # If no Config file defined, then return empty dictionary.
        ini_config = {}
    # envfile is 2 levels up from this script
    envpath = os.path.dirname(filepath)
    envfile = os.path.join(envpath, ".env")
    load_dotenv(dotenv_path=envfile)
    return ini_config


def get_modulename(scriptname):
    """
    Modulename is required for logfile and for properties file.

    :param scriptname: Name of the script for which modulename is required. Use __file__.
    :return: Module Filename from the calling script.
    """
    # Extract calling application name
    (filepath, filename) = os.path.split(scriptname)
    (module, fileext) = os.path.splitext(filename)
    return module


def init_loghandler(modulename):
    """
    This function initializes the loghandler. Logfilename consists of calling module name + computername.
    Format of the logmessage is specified in basicConfig function.

    :param modulename: The name of the module. Each module will create it's own logfile.
    :return: Log Handler
    """
    logdir = os.getenv("LOGDIR")
    loglevel = os.getenv("LOGLEVEL").upper()
    # Define logfileName
    logfn = "{module}_{host}.log".format(module=modulename, host=platform.node())
    logfile = os.path.join(logdir, logfn)
    # Configure the root logger
    logger = logging.getLogger()
    level = logging.getLevelName(loglevel)
    logger.setLevel(level)
    # Get logfiles of 1M
    maxbytes = 1024 * 1024
    rfh = logging.handlers.RotatingFileHandler(logfile, maxBytes=maxbytes, backupCount=5)
    # Create Formatter for file
    formatter_file = logging.Formatter(fmt='%(asctime)s|%(module)s|%(funcName)s|%(lineno)d|%(levelname)s|%(message)s',
                                       datefmt='%d/%m/%Y|%H:%M:%S')
    # Add Formatter to Rotating File Handler
    rfh.setFormatter(formatter_file)
    # Add Handler to the logger
    logger.addHandler(rfh)
    # Configure Console Handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter_console = logging.Formatter(fmt='%(asctime)s - %(module)s - %(funcName)s - %(lineno)d - %(levelname)s -'
                                              ' %(message)s',
                                          datefmt='%H:%M:%S')
    # Add Formatter to Console Handler
    ch.setFormatter(formatter_console)
    logger.addHandler(ch)
    logging.getLogger('neo4j.bolt').setLevel(logging.WARNING)
    logging.getLogger('httpstream').setLevel(logging.WARNING)
    return logger


def date2epoch(ds):
    """
    This function will convert a date time string to epoch for storage in SQLite table.

    :param ds: Date time string in format %Y-%m-%d %H:%M:%S
    :return: epoch - seconds since 1/01/1970
    """
    utc_time = time.strptime(ds, "%Y-%m-%d %H:%M:%S")
    return timegm(utc_time)


def children_sorted(children):
    return sorted(children, key=lambda child: child.content.title)


def nodes_sorted(nodes):
    return sorted(nodes, key=lambda node: node.created, reverse=True)[:10]


def terms_sorted(terms):
    return sorted(terms, key=lambda term: (term.vocabularies.name, term.name))


def datestamp(epoch):
    """
    This is a Jinja2 filter

    :param epoch: Unix timestamp - seconds since 1/01/1970 UTC
    :return: Date in format 'DD/MM/YY
    """
    return datetime.fromtimestamp(epoch).strftime('%Y-%m-%d')


def datetimestamp(epoch):
    """
    This is a Jinja2 filter

    :param epoch: Unix timestamp - seconds since 1/01/1970 UTC
    :return: Date and Time in format 'DD/MM/YY HH:MM:SS
    """
    return datetime.fromtimestamp(epoch).strftime('%d/%m/%y %H:%M:%S')


def monthdisp(ym):
    """
    This is a Jinja2 filter to convert %Y-%m into month Year.

    :param ym: Date in %Y-%m format
    :return: Date in month Year format.
    """
    month_arr = ["januari", "februari", "maart", "april", "mei", "juni",
                 "juli", "augustus", "september", "oktober", "november", "december"]
    (yr, mnth) = ym.split("-")
    return "{m} {y}".format(y=yr, m=month_arr[int(mnth)-1])


class LoopInfo:
    """
    This class handles a FOR loop information handling.
    """

    def __init__(self, attribname, triggercnt):
        """
        Initialization of FOR loop information handling. Start message is printed for attribname. Information progress
        message will be printed for every triggercnt iterations.

        :param attribname:
        :param triggercnt:
        :return:
        """
        self.rec_cnt = 0
        self.loop_cnt = 0
        self.attribname = attribname
        self.triggercnt = triggercnt
        curr_time = datetime.now().strftime("%H:%M:%S")
        print("{0} - Start working on {1}".format(curr_time, str(self.attribname)))
        return

    def info_loop(self):
        """
        Check number of iterations. Print message if number of iterations greater or equal than triggercnt.
        :return:
        """
        self.rec_cnt += 1
        self.loop_cnt += 1
        if self.loop_cnt >= self.triggercnt:
            curr_time = datetime.now().strftime("%H:%M:%S")
            print("{0} - {1} {2} handled".format(curr_time, str(self.rec_cnt), str(self.attribname)))
            self.loop_cnt = 0
        return

    def end_loop(self):
        curr_time = datetime.now().strftime("%H:%M:%S")
        print("{0} - {1} {2} handled - End.\n".format(curr_time, str(self.rec_cnt), str(self.attribname)))
        return
