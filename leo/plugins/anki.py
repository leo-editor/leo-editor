#@+leo-ver=5-thin
#@+node:ekr.20210223152423.1: * @file ../plugins/anki.py
#@@language python
""" Push @anki nodes.

- Download instructions here: https://apps.ankiweb.net/#linux

- Once Anki installed, install the AnkiConnect extension:
  https://ankiweb.net/shared/info/2055492159

- This plugin pushes the @anki nodes to AnkiConnect for later usage as flash cards.

- Currently only supports the /Basic/ card type of Anki

Usage:
Create headline like this:
@anki <card title>

- Create three children called `@anki front`, `@anki back`, `@anki deck`

- `@anki front` contains the front of the flash card

- `@anki back` contains the back of the flash card

- `@anki deck` specifies the deck for this flash card

- [OPTIONAL] `@anki tag` contains the tags for the card, comma separated

Select any of these nodes (@anki, @anki front, @anki back), do `alt-x
act-on-node`. This pushes the card to AnkiConnect. If any errors happen, a child
to `@anki` called `@anki error` is populated with the relevant error details.
"""

# broad-exception-raised: Not valid in later pylints.

import leo.core.leoGlobals as g
from leo.core import leoPlugins

try:
    import json
    import urllib.request
    ok = True
    # TODO: check if AnkiConnect reachable here
except ImportError:
    ok = False

def init():
    """ Return True if plugin has loaded successfully."""
    if ok:
        g.plugin_signon(__name__)
        g.act_on_node.add(anki_act_on_node, 50)
    return ok

def _request(action, **params):
    return {'action': action, 'params': params, 'version': 6}

def _invoke(action, **params):
    requestJson = json.dumps(_request(action, **params)).encode('utf-8')
    response = json.load(urllib.request.urlopen(urllib.request.Request('http://localhost:8765', requestJson)))
    if len(response) != 2:
        raise Exception('response has an unexpected number of fields')
    if 'error' not in response:
        raise Exception('response is missing required error field')
    if 'result' not in response:
        raise Exception('response is missing required result field')
    if response['error'] is not None:
        raise Exception(response['error'])
    return response['result']


def anki_warn(deck, front, back):
    # AnkiConnect will anyway throw an error, warn user now?
    useful_msg = (
        'No %s specified for this card. '
        'Please create a child node to @anki called @anki %s '
        'and populate with a %s name'
    )
    if deck is None:
        g.es(useful_msg % ("deck", "deck", "deck"))
        return
    if front is None:
        g.es(useful_msg % ("front", "front", "front"))
        return
    if back is None:
        g.es(useful_msg % ("back", "back", "back"))
        return

def anki_deck_check(deck):
    result = _invoke('deckNames')
    if deck not in result:
        g.es('Specified deck is %s. But it is present in your list of desks. Creating now...' % (deck))
        result = _invoke('createDeck', deck=deck)
        g.es('Created %s with id %s' % (deck, str(result)))

def anki_act_on_node(c, p, event):
    h = p.h

    if not h.strip().startswith('@anki'):
        raise leoPlugins.TryNext

    # are we on root @anki
    if h.strip() != '@anki':
        # find the parent
        for parent in p.parents():
            if parent.h.strip().startswith('@anki'):
                # parent found
                p = parent

    # we are at root, ready to process inputs
    # now find the deck
    # is this card update or new card?
    # if @anki id not present, it's new
    card_id = None
    deck = None
    front = None
    back = None
    tag = None
    for child in p.children():
        if child.h.strip() == '@anki deck':
            deck = child.b

        elif child.h.strip() == '@anki front':
            front = child.b

        elif child.h.strip() == '@anki back':
            back = child.b

        elif child.h.strip() == '@anki id':
            card_id = int(child.b)

        elif child.h.strip() == '@anki tag':
            tag = child.b

    # new card to be added
    if card_id is None:
        anki_warn(deck, front, back)

        # front, back, deck all available
        # check if deck needs to be created
        anki_deck_check(deck)

        result = _invoke('addNote', note={
            'deckName': deck,
            'modelName': 'Basic',
            'fields': {
                'Front': front,
                'Back': back
            },
            'tags': tag.split(",")
        })
        # result id needs to be stored for future updates
        card_id_node = p.insertAsLastChild()
        card_id_node.h = '@anki id'
        card_id_node.b = str(result)

    # updating existing card
    else:
        anki_warn(deck, front, back)

        # front, back, deck all available
        # deck also will be present
        result = _invoke('updateNoteFields', note={
            'deckName': deck,
            'modelName': 'Basic',
            'id': int(card_id),
            'fields': {
                'Front': front,
                'Back': back
            },
            'tags': tag.split(",")
        })

#@-leo
