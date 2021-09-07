import sys
import json
import logging
import requests
import configparser
import argparse
import platform
import uuid
import time
import datetime

logger = logging.getLogger()
LOG_FORMAT = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(name)s: %(funcName)s (%(lineno)s) - %(message)s')
console_handler = logging.StreamHandler()
console_handler.setFormatter(LOG_FORMAT)
logger.addHandler(console_handler)

SeverityStringToIntMapping = {
    "finest": 0,
    "finer": 1,
    "fine": 2,
    "info": 3,
    "warning": 4,
    "error": 5,
    "fatal": 6
}

SeverityIntToStringMapping = {
    0: "finest",
    1: "finer",
    2: "fine",
    3: "info",
    4: "warning",
    5: "error",
    6: "fatal"
}


class EventAttributes(dict):
    """EventAttributes for Events
        See the docs on addEvents / Events for details. https://app.scalyr.com/help/api#addEvents
        The attributes will be added to the attrs fields of an event or session

        dict (str, type): Attributes passed for event

    """
    pass


class ScalyrLogger:
    logger = logging.getLogger('ScalyrLogger')
    logger.setLevel('INFO')

    def __init__(self, apiToken=None, serverHost=None, sessionInfo: EventAttributes = {}, **kwargs):
        """Initialize ScalyrLogger

        Args:

        Kwargs:
            apiToken (str, optional): ScalyrAPI Token. Defaults to None.
            serverHost (str, optional): serverHost to use. Defaults to hostname of system.
            sessionInfo (EventAttributes, optional): Attributes passed to session. Defaults to {}.
        """
        self.__scalyrToken = apiToken
        # Generate unique UUID for each instance
        self.__sessionID = str(uuid.uuid4())
        # Store the lastEvent Timestamp (nanoseconds) must be unique per event
        self.__lastEventTimestamp = time.time_ns()
        self.ServerHost = serverHost if not serverHost is None else platform.node()
        self.FlushInterval = 5
        self.__sessionInfo = sessionInfo

        if not 'serverHost' in self.__sessionInfo:
            self.__sessionInfo['serverHost'] = self.ServerHost
            

        self.__scalyrSession = {
            'token': self.__scalyrToken,
            'session': self.__sessionID,
            'sessionInfo': self.__sessionInfo,
            'events': [],
            'threads': []
        }
        print(self.__scalyrSession)
    def __clearSessionEvents(self):
        """internal - Clear events for session
        """
        self.__scalyrSession['events'].clear()

    def Event(self, message: str = None, severity=None, eventAttributes: EventAttributes = {}, **kwargs):
        """Add event to session

        Kwargs:
            message (str, optional): Message of event. Defaults to None.
            severity (str || int, optional): Severity of event. Defaults to 3 (info) - For information see "severity" under https://app.scalyr.com/help/api#addEvents 
            eventAttributes (EventAttributes, optional): EventAttributes for event. Defaults to {}.
        """

        if (datetime.datetime.utcnow() - datetime.datetime.utcfromtimestamp(self.__lastEventTimestamp // 1000000000)).seconds >= self.FlushInterval:
            # Flush events if more than {FlushInterval} seconds have passed from lastEventTimestamp
            self.Flush()

        if (sys.getsizeof(self.__scalyrSession['events']) > 5000) or len(self.__scalyrSession['events']) > 500:
            # Flush if events size > 5K
            self.Flush()

        # ts must be unique for each event, so add 1 if not then set it as lastEventTimestamp
        ts = time.time_ns() if time.time_ns(
        ) > self.__lastEventTimestamp else (time.time_ns()+1)
        self.__lastEventTimestamp = ts

        if severity:
            if type(severity) == str or type(severity) == int:
                if type(severity) == str:
                    if severity.isdigit():
                        severity = int(severity)
                    else:
                        severity = SeverityStringToIntMapping.get(severity, 3)

                if type(severity) == int:
                    severity = severity if (severity <= 6) and (
                        severity >= 0) else 3
            else:
                severity = 3
        else:
            severity = 3

        scalyrEvent = {
            'ts': str(ts),
            'sev': severity,
            'attrs': eventAttributes
        }

        if scalyrEvent['attrs'].get("message", None) is None:
            scalyrEvent['attrs']['message'] = message

        self.__scalyrSession['events'].append(scalyrEvent)

        if (sys.getsizeof(self.__scalyrSession['events']) > 5000) or len(self.__scalyrSession['events']) > 500:
            # Flush if events size > 5K
            self.Flush()

    def Flush(self, **kwargs):
        """Flush events to Scalyr
        """
        if len(self.__scalyrSession['events']) > 0:
            try:
                scalyrResponse = requests.post(
                    'https://app.scalyr.com/api/addEvents', json=self.__scalyrSession)

                respJson = json.loads(scalyrResponse.text)

                if respJson.get('status', 'failure') == 'success':
                    successmsg = "" if respJson.get(
                        'message', None) is None else f' {respJson.get("message")}'
                    self.logger.info(f"Events Sent to Scalyr{successmsg}")
                    self.__clearSessionEvents()

                else:
                    self.logger.error(
                        f"Error Sending Events - ({scalyrResponse.status_code}) - {respJson.get('message', '')}")

            except Exception as ex:
                self.logger.error(f"Exception Sending Events - {ex}")
                pass


class LoggerManager:
    def __init__(self, **kwargs):
        """Initialize a Logger Manager
        """
        self.ScalyrLoggers = dict[str, ScalyrLogger]()
        self.logger = logging.getLogger('ScalyrLoggerManager')
        self.logger.setLevel('INFO')
        if kwargs.get("configfile", "config.ini"):
            config = configparser.ConfigParser()
            config.read(kwargs.get("configfile", "config.ini"))

            logLevel = config.get("Scalyr-Logging", "logLevel", fallback=None)
            if logLevel:
                self.logger.setLevel(logLevel)

    def AddLogger(self, LoggerName: str, ScalyrLogger: ScalyrLogger):
        """Add a logger to the manager

        Args:
            LoggerName (str): Name for logger
            ScalyrLogger (ScalyrLogger): ScalyrLogger instance
        """
        self.ScalyrLoggers[LoggerName] = ScalyrLogger
        self.logger.debug(f"Added Logger {LoggerName}")

    def RemoveLogger(self, LoggerName: str):
        """Remove a logger from the manager

        Args:
            LoggerName (str): Name of logger to remove
        """
        if LoggerName in self.ScalyrLoggers.keys():
            del self.ScalyrLoggers[LoggerName]
            self.logger.debug(f"Removed Logger {LoggerName}")

    def Event(self, LoggerName: str, message: str = None, severity=None, eventAttributes: EventAttributes = {}, **eventKwargs):
        """Add event to specific logger

        Args:
            LoggerName (str): Name of logger

        Kwargs:
            message (str, optional): message to add. Defaults to None.
            severity (str || int, optional): Severity of event. Defaults to 3 (info) - For information see "severity" under https://app.scalyr.com/help/api#addEvents 
            eventAttributes (EventAttributes, optional): EventAttributes to add. Defaults to {}.
        """
        ScalyrLogger = self.ScalyrLoggers.get(LoggerName, None)
        if ScalyrLogger:
            ScalyrLogger.Event(message, severity,
                               eventAttributes, **eventKwargs)
            self.logger.debug(f"Added event to logger {LoggerName}")
            return
        self.logger.error(
            f"Unable to add event - no logger with name: {LoggerName}")

    def FlushAll(self):
        """Flush all loggers under management
        """
        for Log in self.ScalyrLoggers.values():
            Log.Flush()
        self.logger.debug("Flushed Events For All Loggers")


def main():
    class kvdictAppendAction(argparse.Action):
        """
        argparse action to split an argument into KEY=VALUE form
        on the first = and append to a dictionary.
        """

        def __call__(self, parser, args, values, option_string=None):
            assert(len(values) == 1)
            try:
                (k, v) = values[0].split("=", 2)
            except ValueError as ex:
                raise argparse.ArgumentError(
                    self, f"could not parse argument \"{values[0]}\" as k=v format")
            d = getattr(args, self.dest) or {}
            d[k] = v
            setattr(args, self.dest, d)

    parser = argparse.ArgumentParser(description="Scalyr Logger")
    parser.add_argument('-c', '--config', default='config.ini',
                        help='Full path to config.ini')
    parser.add_argument('-t', '--token', help='Scalyr API Token')
    parser.add_argument(
        '-srv', '--server', help="serverHost name to use. Defaults to current hostname")
    parser.add_argument('-sev', '--severity',
                        help="Severity of message. Defaults to info / 3")
    parser.add_argument('-eattr', "--eventattribute",
                        nargs=1,
                        action=kvdictAppendAction,
                        metavar="attr=value",
                        help="Add to attrs of event. May appear multiple times.", default={})
    parser.add_argument("-sattr", "--sessionattribute",
                        nargs=1,
                        action=kvdictAppendAction,
                        metavar="attr=value",
                        help="Add to attrs of session. May appear multiple times.", default={})
    parser.add_argument("message", help="Message to send")

    args = parser.parse_args()
    Logger = ScalyrLogger(args.token, args.server,
                          args.sessionattribute, configfile=args.config)
    Logger.Event(args.message, args.severity, args.eventattribute)
    Logger.Flush()


if __name__ == "__main__":
    main()
