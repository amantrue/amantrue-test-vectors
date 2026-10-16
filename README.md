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

All private keys in `request-auth/vectors.json` and `proxy-profile/keys.json`
are fixed TEST keys. They were made for these vectors. They protect nothing.
Do not use them for anything other than tests.

All certificates come from test CAs named `Amantrue Demo` or `Profile Root`.
Host names, email addresses and IP addresses use the documentation values of
RFC 2606, RFC 5737 and RFC 3849.

The interop cases in `xmldsig/interop` are hand-written from the published
message layouts of WSS4J/CXF, WCF and Metro. They are not captured vendor
messages.

The binding vectors hold compiled element structures of HL7 FHIR (CC0), NIEM
(public domain) and the Apache Axis AddressBook sample (Apache-2.0).

The file `.gitleaks.toml` allows the two files with test keys. A secret scan
of this repository finds nothing else.

## proxy-profile

`proxy-profile/vectors.json` holds the shared test vectors of the proxy
signature profile: 9 valid and 11 invalid cases, each with the request, the
response headers and body, the `Signature-Input` and `Signature` headers, the
signature base of each label, and, for an invalid case, a part of the
expected error text. `proxy-profile/keys.json` holds the fixed TEST keys
(ES256 PKCS#8 PEM, ML-DSA-65 seed) and their JWKs. Do not use these keys for
anything other than tests.

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
