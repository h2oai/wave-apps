from h2o_wave import Q
from typing import Optional, List


def add_card(q: Q, name, card) -> None:
    q.client.cards.add(name)
    q.page[name] = card


# Remove all the cards related to navigation.
def clear_cards(q: Q, ignore: Optional[List[str]] = []) -> None:
    print("Clearing cards")
    if not q.client.cards:
        print("No cards")
        return

    for name in q.client.cards.copy():
        if name not in ignore:
            del q.page[name]
            q.client.cards.remove(name)
