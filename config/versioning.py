from rest_framework import versioning


class MobileAppVersioning(versioning.BaseVersioning):
    """
    Custom versioning scheme that expects the client to send the mobile app version
    in a header.
    """

    default_version = "1.0"
    allowed_versions = ["1.0", "2.0"]
    version_param = "mobile-app-version"

    def determine_version(self, request, *args, **kwargs):
        version = request.headers.get(self.version_param, self.default_version)
        return self.validate_version(version)

    def validate_version(self, version):
        if version not in self.allowed_versions:
            return self.default_version
        return version
