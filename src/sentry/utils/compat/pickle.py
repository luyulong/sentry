from __future__ import absolute_import, print_function

import kombu.serialization as kombu_serializer

from sentry.utils.compat import pickle

# TODO(python3): We use the pickles `2` protocol as this is the protocol that
# is supported in both 2 and 3.
#
#  - python3 defaults to a protocol > 2 (depending on the version, see [0]).
#  - python2 defaults to protocol 2.
#
# This is ONLY required for the transition of Python 2 -> 3. There will be a
# period where data may be pickled in python3, where if we did not declare the
# version, would be in format that python 2's pickle COULD NOT decode.
#
# Once the python3 transition is complete we can use a higher version
#
# NOTE: from the documentation:
#       > The protocol version of the pickle is detected automatically
#
# [0]: https://docs.python.org/3/library/pickle.html#pickle-protocols
pickle.DEFAULT_PROTOCOL = 2


# TODO(python3): Notes on pickle compatibility between 2 + 3:
#
# ## Encoding
#
#  In python, when pickling a data structure, the output is a byte stream. We
#  must tell pickle how to decode byte strings during unpickling that are from
#  python2 in python3.
#
#  Typically we could use the default ASCII decoding, since if correctly used,
#  byte strings should ONLY contain ASCII data. During the 2 -> 3 conversion,
#  we should make a great effort to ensure text values are unicode.
#
#  HOWEVER, we must decode as latin-1 due to quark in how datetime objects are
#  decoded [0]. Leaving it as ASCII will result in a decoding error.
#
#  ### Potentially problems
#
#  In cases where we encode truly binary data (which must be stored as a string
#  in python2, as there is no bytes type) we will improperly decode it as
#  latin1, resulting in a unicode string in python3 that will contain all kinds
#  of strange characters.
#
#  If we run into this issue when dealing with bytes / strings / unicode. The
#  solution will be to check if we're running py3, and check if the specific
#  field is not the bytes type, but a string, we will have to then encode as
#  `latin-1` to get the bytes back.
#
#
# ## Object Type
#
#  When unpickling python2 objects created as old-style classes, python3 will
#  not know what to do.
#
#  Typically we would have to have some compatibility checking / fixing here
#  (see [0]), but because we do not have any oldstyle objects, we don't need to
#  worry about this.
#
#
# ## What are we patching
#
#  - We patch ALL instances of `pickle_loads` to attempt normal depickling,
#    this will always work in python2, however in python3 if the object
#    contains a datetime object, or non-ASCII str data, it will fail with a
#    UnicodeDecodeError, in which case we will decode strings as latin-1.
#
#  - We patch kombus `pickle_load` function to do the same as above, however
#    because kombu passes in a byte buffer, we have to seek back to the start of
#    the byte buffer to attempt depickling again.
#
#  - At the moment we DO NOT patch `pickle.load`, since it may or may not be
#    the case that we can seek to the start of the passed file-like object. As
#    far as I can tell we DO NOT use pickle.load, so it may be the case that
#
#
# [0]: https://rebeccabilbro.github.io/convert-py2-pickles-to-py3/#python-2-objects-vs-python-3-objects

original_pickle_load = pickle.load
original_pickle_loads = pickle.loads
original_kombu_pickle_loads = kombu_serializer.pickle_loads


def __py3_compat_pickle_loads(*args, **kwargs):
    try:
        return original_pickle_loads(*args, **kwargs)
    except UnicodeDecodeError:
        kwargs["encoding"] = kwargs.get("encoding", "latin-1")
        return original_pickle_loads(*args, **kwargs)


def __py3_compat_kombu_pickle_load(*args, **kwargs):
    """
    This patched pickle.load is specifically used for kombu's `pickle_loads`
    function, with similar logic to above.
    """
    try:
        return original_pickle_load(*args, **kwargs)
    except UnicodeDecodeError:
        # We must seek back to the start of the BytesIO buffer to depickle
        # again after failing above, without this we'll get a
        args[0].seek(0)

        kwargs["encoding"] = kwargs.get("encoding", "latin-1")
        return original_pickle_load(*args, **kwargs)


def __py3_compat_kombu_pickle_loads(s, load=__py3_compat_kombu_pickle_load):
    return original_kombu_pickle_loads(s, load)


def monkeypatch_pickle_loaders():
    pickle.loads = __py3_compat_pickle_loads
    kombu_serializer.pickle_loads = __py3_compat_kombu_pickle_loads
