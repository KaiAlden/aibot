from app.schemas import Constitution, SessionContext


def find_constitution_in_text(text: str) -> Constitution | None:
    for constitution in Constitution:
        if constitution.value in text or constitution.value.removesuffix("质") in text:
            return constitution
    return None


def precheck_constitution(query: str, context: SessionContext) -> Constitution | None:
    explicit = find_constitution_in_text(query)
    if explicit is not None:
        return explicit
    return context.constitution
