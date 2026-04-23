"""Constants for ha-french-holidays."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "ha-french-holidays"
ATTRIBUTION = "Data provided by https: // data.education.gouv.fr/"

CONF_ZONE = "zone"
FRIENDLY_NAME = "Vacances Scolaires"
FRIENDLY_PREFIX = "Vacances"
