from pprint import pprint


class Validatable:
    def validate(
        self,
    ) -> list[str]:
        errors = []
        for test, reason in self.assertions():
            if not test:
                errors.append(reason)
        return errors

    def assertions(self) -> list[tuple[bool, str]]:
        return []

    def __post_init__(self):
        errors = self.validate()
        if errors:
            print("Failed Tests:")
            pprint(errors)
