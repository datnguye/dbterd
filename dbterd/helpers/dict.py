class ObjectView:
    """Convert nested dict to dynamic object."""

    def __init__(self, d, nested=True):
        self.origin = d
        for a, b in d.items():
            if nested:
                if isinstance(b, (list, tuple)):
                    setattr(
                        self,
                        a,
                        [ObjectView(x) if isinstance(x, dict) else x for x in b],
                    )
                else:
                    setattr(self, a, ObjectView(b) if isinstance(b, dict) else b)
            else:
                setattr(self, a, b)

    def has_field(self, field):
        fields = field.split(".")
        # This is a safeguard but actually never triggered in practice
        # because split always returns at least one element (empty string for empty input)
        if len(fields) == 0:  # pragma: no cover
            return False

        obj = self.origin
        for f in fields:
            if f not in obj:
                return False
            obj = obj[f]

        return True
