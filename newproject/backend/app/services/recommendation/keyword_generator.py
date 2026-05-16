from app.data.condition_rules import CONDITION_RULES


class KeywordGenerator:

    def generate(self, conditions: list[str]) -> list[str]:

        include_set = set()
        exclude_set = set()

        for condition in conditions:

            rule = CONDITION_RULES.get(condition)

            if not rule:
                continue

            include_set.update(rule.get("include", []))
            exclude_set.update(rule.get("exclude", []))

        result = include_set - exclude_set

        return list(result)