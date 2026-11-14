"""Libellés lisibles des données saisies à l'inscription USSD.

Les codes correspondent aux choix des menus USSD (airtel-quiz-ussd,
src/ussd/pages/register.js). Garder les deux synchronisés.
"""

LEVELS = {
    1: "Éducation de base",
    2: "Humanités",
}

# Options des humanités (non demandées en éducation de base).
OPTIONS = {
    1: "Littéraire",
    2: "Commercial",
    3: "Math-Physique",
    4: "Scientifique",
    5: "Électronique",
    6: "Électricité",
    7: "Mécanique",
}


def _int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def level_label(level):
    n = _int(level)
    return LEVELS.get(n, str(level) if level not in (None, "") else "")


def class_label(cls):
    n = _int(cls)
    if n is None:
        return "" if cls in (None, "") else str(cls)
    return "1ère année" if n == 1 else f"{n}ème année"


def option_label(level, option):
    # L'option n'a de sens qu'en humanités.
    if _int(level) != 2:
        return ""
    n = _int(option)
    return OPTIONS.get(n, "" if option in (None, "") else str(option))
