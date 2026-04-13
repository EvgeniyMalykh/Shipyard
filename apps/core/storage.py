class PublicMediaStorage(S3Boto3Storage):
    """Public-read bucket for avatars, team logos."""
    location       = "media/public"
    default_acl    = "public-read"
    file_overwrite = False


class PrivateMediaStorage(S3Boto3Storage):
    """Private bucket for sensitive documents — URL signing required."""
    location           = "media/private"
    default_acl        = "private"
    file_overwrite     = False
    custom_domain      = False

    def url(self, name):
        return self.connection.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket_name, "Key": self._normalize_name(name)},
            ExpiresIn=3600,
        )