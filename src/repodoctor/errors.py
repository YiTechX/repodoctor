class RepoDoctorError(Exception):
    pass


class RegistryError(RepoDoctorError):
    pass


class ConfigError(RepoDoctorError):
    pass


class PluginError(RepoDoctorError):
    pass


class ScaffoldError(RepoDoctorError):
    pass
