# amantrue-test-vectors

## What this repository is

This repository holds the test vectors that amantrue-zk-node, amantrue-node
and amantrue-attestation-proxy share. Each folder is one corpus. The sections
below tell what each corpus holds and which project writes it.

Each consumer pins one commit id of this repository. No branch or tag is
followed. In amantrue-zk-node the pin is the file `FIXTURES_VERSION`, and
amantrue-zk-node fetches the vectors into `core/tests/fixtures`.

## How to change a vector

1. Change the vectors here first. Make a commit.
2. Push the commit.
3. In each consumer, put the new full commit id in the pin. In
   amantrue-zk-node, change `FIXTURES_VERSION`.
4. Run the tests of each consumer.

## License

This repository is licensed under MIT OR Apache-2.0, as the amantrue-zk-node
crates. See `LICENSE-MIT` and `LICENSE-APACHE`.

## Test-only keys and synthetic data

All personal data in these vectors is synthetic. The patient Eboni Brekke (id
`bb7fb8e1-1a76-4328-92ea-3852f34846e6`) is a sample patient that Synthea
generated. It comes from the public SMART Health IT sandbox
(`https://r4.smarthealthit.org`). Other names (Eboni Ward, Mallory, Maria Ruiz,
`GivenNNNNN`, `Consultation N`) are placeholders.

All private keys in `proxy-profile/keys.json` are fixed TEST keys. They were
made for these vectors. They protect nothing.
Do not use them for anything other than tests.

All certificates come from test CAs named `Amantrue Demo` or `Profile Root`.
Host names, email addresses and IP addresses use the documentation values of
RFC 2606, RFC 5737 and RFC 3849.

The interop cases in `xmldsig/interop` are hand-written from the published
message layouts of WSS4J/CXF, WCF and Metro. They are not captured vendor
messages.

The binding vectors hold compiled element structures of HL7 FHIR (CC0), NIEM
(public domain) and the Apache Axis AddressBook sample (Apache-2.0).

The file `.gitleaks.toml` allows the file with test keys. A secret scan
of this repository finds nothing else.

## proxy-profile

`proxy-profile/vectors.json` holds the shared test vectors of the proxy
signature profile: 8 valid and 12 invalid cases, each with the request, the
response headers and body, the `Signature-Input` and `Signature` headers, the
signature base of each label, and, for an invalid case, a part of the
expected error text. The signature covers `@status`, `content-type`,
`content-digest`, `x-session-id`, `amantrue-request-digest`, `@method;req`
and `@target-uri;req`, and `amantrue-response-parts` for a multipart
response. The SOAP cases carry synthetic WS-Security headers in the request
body, as the node builds them. `proxy-profile/keys.json` holds the fixed TEST
keys (ES256 PKCS#8 PEM, ML-DSA-65 seed) and their JWKs. Do not use these keys
for anything other than tests.

In amantrue-zk-node, `core/tests/proxy_profile_vectors.rs`,
`core/tests/proxy_signed.rs` and `host/tests/guests_verify_signatures.rs`
read the vectors. amantrue-attestation-proxy keeps a copy. To make the vectors
again:

```
cargo test -p amantrue-prover-core --test proxy_profile_vectors -- --ignored regenerate_the_vectors
```

The output is deterministic (fixed `created` and `expires`, RFC 6979 ECDSA,
deterministic ML-DSA). A test regenerates into a temporary directory and
compares the bytes with the committed files.

## xml-reader

`xml-reader/` holds the shared corpus of the plain XML reader. The Rust reader
of amantrue-zk-node and the Go reader of amantrue-node must give the same
result for every case. Each case is one folder, `xml-reader/<case>/`, with two
files:

- `body.xml` holds the input bytes, without change.
- `expected.json` holds the result.

`expected.json` has one of two forms:

- `{"ok": true, "tree": E}` for an accepted document.
- `{"ok": false, "rule": "<id>"}` for a refused document.

`E` is `{"ns": str, "name": str, "attrs": [[ns, name, value], ...], "content": [str | E, ...]}`.
`ns` is the namespace URI and `name` is the local name. The attributes have no
`xmlns` declarations. They are sorted by namespace URI, then by local name.
Text runs are never empty.

A reader must give the same `ok` value for each case, and the same tree for
each accepted case. The rule id is for the report of an error. A reader must
give the rule id of the case where it can.

### Rule ids

| Id | Refused input |
| --- | --- |
| `size` | More than 1,048,576 bytes. |
| `encoding` | Bad UTF-8 or UTF-16, or a declared encoding that does not match the input. |
| `decl` | Bad XML declaration, or an XML declaration that is not at the start. |
| `doctype` | A DOCTYPE. |
| `pi` | A processing instruction other than the XML declaration. |
| `char` | A character or a character reference that is not in the XML 1.0 `Char` production. |
| `name` | A name that is not valid in XML 1.0 4th edition, or a bad QName. |
| `ns` | A namespace error. This includes a prefixed attribute with the local name `xmlns` and an element name with the prefix `xml`. |
| `dup-attr` | Two attributes with the same expanded name. |
| `structure` | No root, more than one root, or text outside the root. |
| `depth` | More than 64 nested elements. |
| `limits` | More than 1,024 attributes on one element, `xmlns` declarations included. Also more than 32 distinct namespace bindings in scope at one element. The default namespace counts when it has a non-empty URI, and `xmlns=""` removes it. The implicit `xml` binding does not count; an explicit `xmlns:xml` declaration counts as one binding. A redeclared prefix counts once. |
| `syntax` | Any other well-formedness error. |

### Output tree rules

- In an attribute value, a literal TAB, LF or CR becomes a space. A character
  from a character reference stays as it is.
- Line ends are normalized before parsing: CR LF and a lone CR become LF. A
  character reference `&#13;` stays CR.
- CDATA joins the text next to it into one text run. A comment does not split
  a text run.
- Only one BOM is removed. A second BOM is text outside the root, and the
  reader refuses it with `structure`.

### Cases

The file `scripts/xml-reader-cases.json` lists the cases. Each entry has
`case` (the folder name), `source`, `expect` (`accept` or `refuse:<id>`),
`body_file` and `body_b64`. Every entry has the two body keys. One of them
holds the body and the other is `null`.

| Source | Count | Description |
| --- | --- | --- |
| `edge` | 66 | Edge cases from the spike. |
| `w3c:<ID>` | 123 | W3C XML Conformance Suite tests (`valid`, `invalid` and `not-wf`) with no DOCTYPE and no processing instruction. |
| `name-table`, `limits` | 14 | Cases for the Go name tables, for the limit of 1,024 attributes and for the limit of 32 namespace bindings. |
| `rule-8-11` | 12 | Cases for line ends, character references, BOMs and reserved namespace names. |
| `walk-a/<dir>`, `walk-edge/<dir>` | 49 | The bodies of the `walk-a` and `walk-edge` corpora whose root is not a SOAP envelope. |

The corpus has 264 cases.

Where the W3C suite and the rules disagree, the rules win. The three
`x-rmt5-*` cases (names that only the 5th edition allows) are refused with
`name`.

### How to make the corpus again

Python 3 and the standard library are enough. The committed corpus was made
with Python 3.14.5 and expat 2.7.4. Run this command in the root of this
repository:

```
python3 -I scripts/gen-xml-reader.py
```

The script reads each body and computes the result with a reference reader. The
reader uses `xml.parsers.expat` with namespace processing, and the rules that
expat does not check. The script compares the result with `expect`. If one case
disagrees, the script prints the case, exits with code 1 and writes nothing.
Otherwise it writes the case folders and deletes the folders of removed cases.
The output is deterministic.

### Consumers

- amantrue-zk-node: `core/tests/xml_reader.rs`.
- amantrue-node: `internal/xmlread/corpus_test.go`.
