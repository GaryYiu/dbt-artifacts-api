## parsing issue for materialized and checksum (deep level parse) week 2 problem
Problem: Node(**raw) blindly spreads a raw manifest dict as kwargs, assuming every field lives at the top level. Two fields didn't: materialized is nested under config, and checksum is a nested object ({"name": "sha256", "checksum": "<hash>"}) where the model expected a plain string.

Why it broke twice:
1. First pass: Node(**raw, materialized=..., checksum=...) — passing explicit kwargs alongside **raw fails when the key already exists at the top level of raw (checksum does; materialized doesn't) → TypeError: multiple values for keyword argument.
2. Fix: build the override as a dict literal first ({**raw, "checksum": ...}), where a repeated key just gets overwritten by the later one — no error, unlike a function call. Then spread that merged dict into Node(**merged).

Takeaway for NOTES.md: f(**d, key=val) (function call) rejects duplicate keys; {**d, "key": val} (dict literal) silently overwrites them. Use the dict-merge-then-spread pattern whenever you need to override a handful of keys from a larger dict you're otherwise passing through as-is.