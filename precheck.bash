#!/bin/bash
set -euxo pipefail

FULL=true
if [ 0 -ne $# ]; then
    if [ "--quick" = "$1" ]; then
        FULL=false
    else
        echo "Unknown argument: `$1`"
        exit 1
    fi
fi

cargo +nightly fmt --all
cargo clippy --all-targets --features python -- -D warnings
[ "$FULL" = true ] && cargo check --all-targets --no-default-features

INSTA_FORCE_PASS=1 INSTA_UPDATE=always TRYBUILD=overwrite cargo test --all-targets --no-fail-fast --features python
cargo test --doc
[ "$FULL" = true ] && RUSTDOCFLAGS="-Dwarnings" -cargo doc --no-deps

[ "$FULL" = true ] && CARGO_TARGET_WASM32_UNKNOWN_UNKNOWN_RUNNER=wasm-bindgen-test-runner cargo test -p hydroflow --target wasm32-unknown-unknown --tests --no-fail-fast
